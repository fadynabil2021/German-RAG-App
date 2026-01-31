from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, func
from domains.shared.repository import BaseRepository
from models.db_schemes.minirag.schemes.datachunk import DataChunk

class ChunkRepository(BaseRepository[DataChunk]):
    """SQLAlchemy implementation of the DataChunk repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def get_by_id(self, id: int) -> Optional[DataChunk]:
        result = await self.session.execute(select(DataChunk).filter(DataChunk.chunk_id == id))
        return result.scalars().first()
        
    async def get_by_project(self, project_id: int, skip: int = 0, limit: int = 100) -> List[DataChunk]:
        result = await self.session.execute(
            select(DataChunk)
            .filter(DataChunk.chunk_project_id == project_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_project(self, project_id: int) -> int:
        result = await self.session.execute(
            select(func.count(DataChunk.chunk_id))
            .filter(DataChunk.chunk_project_id == project_id)
        )
        return result.scalar() or 0

    async def save(self, chunk: DataChunk) -> DataChunk:
        self.session.add(chunk)
        await self.session.flush()
        return chunk
    
    async def delete(self, id: int) -> bool:
        result = await self.session.execute(delete(DataChunk).where(DataChunk.chunk_id == id))
        return result.rowcount > 0
    
    async def delete_by_project(self, project_id: int) -> int:
        result = await self.session.execute(delete(DataChunk).where(DataChunk.chunk_project_id == project_id))
        return result.rowcount

    async def list(self, skip: int = 0, limit: int = 100) -> List[DataChunk]:
        result = await self.session.execute(select(DataChunk).offset(skip).limit(limit))
        return list(result.scalars().all())
