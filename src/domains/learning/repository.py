from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from domains.shared.repository import BaseRepository
from models.db_schemes.minirag.schemes.project import Project

class ProjectRepository(BaseRepository[Project]):
    """SQLAlchemy implementation of the Project repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def get_by_id(self, id: int) -> Optional[Project]:
        result = await self.session.execute(select(Project).filter(Project.project_id == id))
        return result.scalars().first()
    
    async def get_by_uuid(self, uuid_str: str) -> Optional[Project]:
        result = await self.session.execute(select(Project).filter(Project.project_uuid == uuid_str))
        return result.scalars().first()
        
    async def get_by_owner(self, owner_id: int) -> List[Project]:
        result = await self.session.execute(select(Project).filter(Project.owner_id == owner_id))
        return list(result.scalars().all())

    async def save(self, project: Project) -> Project:
        self.session.add(project)
        await self.session.flush()
        return project
    
    async def delete(self, id: int) -> bool:
        result = await self.session.execute(delete(Project).where(Project.project_id == id))
        return result.rowcount > 0
    
    async def list(self, skip: int = 0, limit: int = 100) -> List[Project]:
        result = await self.session.execute(select(Project).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def get_or_create(self, project_id: int, owner_id: int = None) -> Optional[Project]:
        project = await self.get_by_id(project_id)
        if project:
            if owner_id is not None and project.owner_id != owner_id:
                return None # Ownership mismatch
            return project
        
        if owner_id is not None:
            new_project = Project(project_id=project_id, owner_id=owner_id)
            return await self.save(new_project)
        
        return None
