from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from domains.shared.repository import BaseRepository
from models.db_schemes.minirag.schemes.learning import Progress, LearningPath

class ProgressRepository(BaseRepository[Progress]):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: int) -> Optional[Progress]:
        result = await self.session.execute(select(Progress).filter(Progress.progress_id == id))
        return result.scalars().first()

    async def get_by_user(self, user_id: int) -> List[Progress]:
        result = await self.session.execute(select(Progress).filter(Progress.user_id == user_id))
        return list(result.scalars().all())

    async def save(self, progress: Progress) -> Progress:
        self.session.add(progress)
        await self.session.flush()
        return progress

    async def delete(self, id: int) -> bool:
        progress = await self.get_by_id(id)
        if progress:
            await self.session.delete(progress)
            return True
        return False

    async def list(self, skip: int = 0, limit: int = 100) -> List[Progress]:
        result = await self.session.execute(select(Progress).offset(skip).limit(limit))
        return list(result.scalars().all())

class LearningPathRepository(BaseRepository[LearningPath]):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: int) -> Optional[LearningPath]:
        result = await self.session.execute(select(LearningPath).filter(LearningPath.path_id == id))
        return result.scalars().first()

    async def get_active_by_user(self, user_id: int) -> Optional[LearningPath]:
        result = await self.session.execute(
            select(LearningPath)
            .filter(LearningPath.user_id == user_id, LearningPath.status == "active")
        )
        return result.scalars().first()

    async def save(self, path: LearningPath) -> LearningPath:
        self.session.add(path)
        await self.session.flush()
        return path

    async def delete(self, id: int) -> bool:
        path = await self.get_by_id(id)
        if path:
            await self.session.delete(path)
            return True
        return False

    async def list(self, skip: int = 0, limit: int = 100) -> List[LearningPath]:
        result = await self.session.execute(select(LearningPath).offset(skip).limit(limit))
        return list(result.scalars().all())
