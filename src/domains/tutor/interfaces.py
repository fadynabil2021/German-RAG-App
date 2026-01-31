"""
RAG Service Interface for the Tutor Domain.
Allows mocking the entire AI pipeline for unit testing.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from enum import Enum

class TutoringMode(str, Enum):
    """Different tutoring interaction modes."""
    SOCRATIC = "socratic"  # Ask guiding questions
    EXPLAIN = "explain"    # Direct explanation
    TRANSLATE = "translate"  # Simple translation
    GRAMMAR = "grammar"    # Grammar breakdown

class IRAGService(ABC):
    """Interface for RAG-based tutoring service."""
    
    @abstractmethod
    async def index_chunks(
        self,
        project_id: int,
        texts: List[str],
        metadata: List[Dict[str, Any]],
        record_ids: List[int],
        do_reset: bool = False
    ) -> bool:
        """Index document chunks into vector database."""
        pass
        
    @abstractmethod
    async def get_collection_info(self, project_id: int) -> Dict[str, Any]:
        """Get information about a project's vector collection."""
        pass

    @abstractmethod
    async def reset_collection(self, project_id: int) -> bool:
        """Delete and recreate a project's vector collection."""
        pass

    @abstractmethod
    async def tutor_response(
        self, 
        query: str, 
        context: List[str], 
        level: str,
        mode: TutoringMode = TutoringMode.SOCRATIC
    ) -> str:
        """
        Generates a pedagogical response based on user level and mode.
        """
        pass
    
    @abstractmethod
    async def retrieve_context(
        self,
        query: str,
        project_id: int,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context from the vector database.
        """
        pass
