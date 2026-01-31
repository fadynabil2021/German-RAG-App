from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.container import container
from domains.identity.repository import UserRepository
from domains.learning.repository import ProjectRepository
from domains.learning.asset_repository import AssetRepository
from domains.learning.chunk_repository import ChunkRepository

async def get_db():
    async with container.db_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

def get_user_repo(session: AsyncSession = Depends(get_db)):
    return UserRepository(session)

def get_project_repo(session: AsyncSession = Depends(get_db)):
    return ProjectRepository(session)

def get_asset_repo(session: AsyncSession = Depends(get_db)):
    return AssetRepository(session)

def get_chunk_repo(session: AsyncSession = Depends(get_db)):
    return ChunkRepository(session)
