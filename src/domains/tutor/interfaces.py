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
    async def tutor_response(
        self, 
        query: str, 
        context: List[str], 
        level: str,
        mode: TutoringMode = TutoringMode.SOCRATIC
    ) -> str:
        """
        Generates a pedagogical response based on user level and mode.
        
        Args:
            query: User's question
            context: Retrieved document chunks
            level: German proficiency level (A1-C2)
            mode: Tutoring interaction mode
            
        Returns:
            AI-generated tutoring response
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
        
        Args:
            query: Search query
            project_id: Project to search within
            limit: Maximum number of results
            
        Returns:
            List of retrieved document chunks with metadata
        """
        pass
