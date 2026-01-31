from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from domains.shared.repository import BaseRepository
from models.db_schemes.minirag.schemes.asset import Asset

class AssetRepository(BaseRepository[Asset]):
    """SQLAlchemy implementation of the Asset repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def get_by_id(self, id: int) -> Optional[Asset]:
        result = await self.session.execute(select(Asset).filter(Asset.asset_id == id))
        return result.scalars().first()
    
    async def get_by_uuid(self, uuid_str: str) -> Optional[Asset]:
        result = await self.session.execute(select(Asset).filter(Asset.asset_uuid == uuid_str))
        return result.scalars().first()
        
    async def get_by_project(self, project_id: int) -> List[Asset]:
        result = await self.session.execute(select(Asset).filter(Asset.asset_project_id == project_id))
        return list(result.scalars().all())

    async def save(self, asset: Asset) -> Asset:
        self.session.add(asset)
        await self.session.flush()
        return asset
    
    async def delete(self, id: int) -> bool:
        result = await self.session.execute(delete(Asset).where(Asset.asset_id == id))
        return result.rowcount > 0
    
    async def list(self, skip: int = 0, limit: int = 100) -> List[Asset]:
        result = await self.session.execute(select(Asset).offset(skip).limit(limit))
        return list(result.scalars().all())
