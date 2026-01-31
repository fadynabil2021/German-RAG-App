from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from domains.shared.repository import BaseRepository
from models.db_schemes.minirag.schemes.user import User

class UserRepository(BaseRepository[User]):
    """SQLAlchemy implementation of the User repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def get_by_id(self, id: int) -> Optional[User]:
        result = await self.session.execute(select(User).filter(User.user_id == id))
        return result.scalars().first()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(select(User).filter(User.email == email))
        return result.scalars().first()
        
    async def save(self, user: User) -> User:
        self.session.add(user)
        # Session commit should be handled by the caller (Unit of Work pattern)
        # but we can do a flush here to get the ID back if it's new
        await self.session.flush()
        return user
    
    async def delete(self, id: int) -> bool:
        result = await self.session.execute(delete(User).where(User.user_id == id))
        return result.rowcount > 0
    
    async def list(self, skip: int = 0, limit: int = 100) -> List[User]:
        result = await self.session.execute(select(User).offset(skip).limit(limit))
        return list(result.scalars().all())
