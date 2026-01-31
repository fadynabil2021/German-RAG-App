"""
Async-first OpenAI Provider with proper event loop handling.
This resolves the P0 blocking I/O issue identified in the audit.
"""
from typing import Union
from openai import AsyncOpenAI
from stores.llm.LLMEnums import OpenAIEnums, DocumentTypeEnum
from helpers.config import Settings
import logging

logger = logging.getLogger(__name__)

class AsyncOpenAIProvider:
    """Async OpenAI provider for non-blocking LLM calls."""
    
    def __init__(self, config: Settings):
        self.config = config
        self.client = AsyncOpenAI(
            api_key=config.OPENAI_API_KEY.get_secret_value() if config.OPENAI_API_KEY else None,
            base_url=config.OPENAI_API_URL or None
        )
        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None
        self.enums = OpenAIEnums
        
    def set_generation_model(self, model_id: str):
        """Set the generation model ID."""
        self.generation_model_id = model_id
        
    def set_embedding_model(self, model_id: str, embedding_size: int):
        """Set the embedding model configuration."""
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size
    
    def construct_prompt(self, prompt: str, role: str):
        """Construct a message dict for chat completion."""
        return {"role": role, "content": prompt}
    
    def process_text(self, text: str, max_length: int = None) -> str:
        """Process and optionally truncate text."""
        if max_length and len(text) > max_length:
            return text[:max_length]
        return text
    
    async def generate_text(
        self,
        prompt: str,
        chat_history: list = None,
        max_output_tokens: int = 200,
        temperature: float = 0.1
    ) -> str:
        """
        Generate text using async OpenAI API.
        Non-blocking implementation to prevent event loop saturation.
        """
        if not self.generation_model_id:
            logger.error("Generation model not set")
            return None
            
        if chat_history is None:
            chat_history = []
        
        # Add user prompt to history
        chat_history.append(
            self.construct_prompt(prompt=prompt, role=self.enums.USER.value)
        )
        
        try:
            response = await self.client.chat.completions.create(
                model=self.generation_model_id,
                messages=chat_history,
                max_tokens=max_output_tokens,
                temperature=temperature
            )
            
            if not response or not response.choices or len(response.choices) == 0:
                logger.error("Empty response from OpenAI")
                return None
                
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            return None
    
    async def embed_text(self, text: Union[str, list], document_type: str = None) -> list:
        """
        Generate embeddings using async OpenAI API.
        Supports both single text and batch processing.
        """
        if not self.embedding_model_id:
            logger.error("Embedding model not set")
            return []
        
        try:
            # Handle both single string and list of strings
            texts = [text] if isinstance(text, str) else text
            
            response = await self.client.embeddings.create(
                model=self.embedding_model_id,
                input=texts
            )
            
            if not response or not response.data:
                logger.error("Empty embedding response from OpenAI")
                return []
            
            # Extract embeddings
            embeddings = [item.embedding for item in response.data]
            
            # Return single embedding if input was single string
            return embeddings[0] if isinstance(text, str) else embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return []
