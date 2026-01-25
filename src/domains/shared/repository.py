"""
Shared domain abstractions and base classes.
"""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional

T = TypeVar("T")

class BaseRepository(Generic[T], ABC):
    """Base repository pattern for domain entities."""
    
    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[T]:
        """Retrieve entity by ID."""
        pass
    
    @abstractmethod
    async def save(self, entity: T) -> T:
        """Save or update entity."""
        pass
    
    @abstractmethod
    async def delete(self, id: str) -> bool:
        """Delete entity by ID."""
        pass
    
    @abstractmethod
    async def list(self, skip: int = 0, limit: int = 100) -> List[T]:
        """List entities with pagination."""
        pass
