"""
Tutor Domain Service - Async RAG implementation.
This replaces the old NLPController with proper async handling.
"""
from typing import List, Dict, Any
from domains.tutor.interfaces import IRAGService, TutoringMode
from infrastructure.llm.async_openai_provider import AsyncOpenAIProvider
from stores.llm.LLMEnums import DocumentTypeEnum
import structlog

logger = structlog.get_logger(__name__)

class TutorService(IRAGService):
    """Production RAG service with async LLM calls."""
    
    def __init__(
        self,
        llm_provider: AsyncOpenAIProvider,
        vectordb_client,
        embedding_client,
        template_parser
    ):
        self.llm_provider = llm_provider
        self.vectordb_client = vectordb_client
        self.embedding_client = embedding_client
        self.template_parser = template_parser
    
    def create_collection_name(self, project_id: int) -> str:
        """Generate collection name for project."""
        return f"collection_{self.vectordb_client.default_vector_size}_{project_id}".strip()
    
    async def index_chunks(
        self,
        project_id: int,
        texts: List[str],
        metadata: List[Dict[str, Any]],
        record_ids: List[int],
        do_reset: bool = False
    ) -> bool:
        """Index document chunks into vector database."""
        try:
            collection_name = self.create_collection_name(project_id)
            
            # Generate embeddings ASYNC
            vectors = await self.embedding_client.embed_text(
                text=texts,
                document_type=DocumentTypeEnum.DOCUMENT.value
            )
            
            # Create collection if needed
            await self.vectordb_client.create_collection(
                collection_name=collection_name,
                embedding_size=self.embedding_client.embedding_size,
                do_reset=do_reset,
            )
            
            # Insert into vector db
            await self.vectordb_client.insert_many(
                collection_name=collection_name,
                texts=texts,
                metadata=metadata,
                vectors=vectors,
                record_ids=record_ids,
            )
            return True
        except Exception as e:
            logger.error(f"Error indexing chunks: {e}")
            return False

    async def get_collection_info(self, project_id: int) -> Dict[str, Any]:
        """Get information about a project's vector collection."""
        collection_name = self.create_collection_name(project_id)
        return await self.vectordb_client.get_collection_info(collection_name=collection_name)

    async def reset_collection(self, project_id: int) -> bool:
        """Delete and recreate a project's vector collection."""
        collection_name = self.create_collection_name(project_id)
        return await self.vectordb_client.delete_collection(collection_name=collection_name)
    
    async def retrieve_context(
        self,
        query: str,
        project_id: int,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context from vector database.
        """
        try:
            collection_name = self.create_collection_name(project_id)
            
            # Generate query embedding
            query_vector = await self.embedding_client.embed_text(
                text=query,
                document_type=DocumentTypeEnum.QUERY.value
            )
            
            if not query_vector or len(query_vector) == 0:
                logger.error("Failed to generate query embedding")
                return []
            
            # Handle both single vector and list of vectors
            if isinstance(query_vector, list) and len(query_vector) > 0:
                query_vector = query_vector[0]
            
            # Search vector database
            results = await self.vectordb_client.search_by_vector(
                collection_name=collection_name,
                vector=query_vector,
                limit=limit
            )
            
            if not results:
                return []
            
            # Convert to dict format
            return [
                {
                    "text": result.text,
                    "score": result.score if hasattr(result, 'score') else None,
                    "metadata": result.metadata if hasattr(result, 'metadata') else {}
                }
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []
    
    async def tutor_response(
        self,
        query: str,
        context: List[str],
        level: str,
        mode: TutoringMode = TutoringMode.SOCRATIC
    ) -> str:
        """
        Generate pedagogical response using async LLM.
        """
        try:
            # Select appropriate system prompt based on mode
            if mode == TutoringMode.SOCRATIC:
                system_prompt = self.template_parser.get("rag", "system_prompt")
            elif mode == TutoringMode.GRAMMAR:
                system_prompt = f"You are a German grammar tutor. Explain grammar concepts at {level} level."
            elif mode == TutoringMode.TRANSLATE:
                system_prompt = f"You are a translator. Provide {level}-appropriate translations."
            else:
                system_prompt = self.template_parser.get("rag", "system_prompt")
            
            # Handling for Graceful Degradation: If context retrieval failed or returned empty
            if not context:
                logger.warning(f"Graceful Degradation: No context for user query: {query}")
                documents_prompts = "SYSTEM NOTE: No specific relevant documents were found in the learning materials for this question. Please answer based on your general knowledge but mention you didn't find specific documentation."
            else:
                # Build document context
                documents_prompts = "\n".join([
                    self.template_parser.get("rag", "document_prompt", {
                        "doc_num": idx + 1,
                        "chunk_text": self.llm_provider.process_text(doc),
                    })
                    for idx, doc in enumerate(context)
                ])
            
            # Build footer with query
            footer_prompt = self.template_parser.get("rag", "footer_prompt", {
                "query": query
            })
            
            # Construct chat history
            chat_history = [
                self.llm_provider.construct_prompt(
                    prompt=system_prompt,
                    role=self.llm_provider.enums.SYSTEM.value,
                )
            ]
            
            # Full prompt
            full_prompt = "\n\n".join([documents_prompts, footer_prompt])
            
            # Generate response using ASYNC provider
            answer = await self.llm_provider.generate_text(
                prompt=full_prompt,
                chat_history=chat_history
            )
            
            return answer if answer else "Entschuldigung, ich konnte keine Antwort generieren."
            
        except Exception as e:
            logger.error(f"Error generating tutor response: {e}")
            return "Es gab einen Fehler. Bitte versuchen Sie es erneut."
