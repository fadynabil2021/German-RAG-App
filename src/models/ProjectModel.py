from .BaseDataModel import BaseDataModel
from .db_schemes import Project
from .enums.DataBaseEnum import DataBaseEnum
from sqlalchemy.future import select
from sqlalchemy import func

class ProjectModel(BaseDataModel):

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.db_client = db_client

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        return instance

    async def create_project(self, project: Project):
        async with self.db_client() as session:
            async with session.begin():
                session.add(project)
            await session.commit()
            await session.refresh(project)
        
        return project

    async def get_project_or_create_one(self, project_id: int, owner_id: int = None):
        async with self.db_client() as session:
            async with session.begin():
                query = select(Project).where(Project.project_id == project_id)
                result = await session.execute(query)
                project = result.scalar_one_or_none()
                
                if project is None:
                    # Provide default behavior or create if owner_id provided
                    if owner_id is None:
                         # Needed for Tasks which might rely on existing project
                         return None
                    
                    project_rec = Project(
                        project_id = project_id,
                        owner_id = owner_id
                    )

                    project = await self.create_project(project=project_rec)
                    return project
                else:
                    return project

    async def get_all_projects(self, page: int=1, page_size: int=10, owner_id: int = None):

        async with self.db_client() as session:
            async with session.begin():
                
                query_filter = True
                if owner_id:
                    query_filter = (Project.owner_id == owner_id)

                total_documents = await session.execute(select(
                    func.count( Project.project_id )
                ).where(query_filter))

                total_documents = total_documents.scalar_one()

                total_pages = total_documents // page_size
                if total_documents % page_size > 0:
                    total_pages += 1

                query = select(Project).where(query_filter).offset((page - 1) * page_size ).limit(page_size)
                projects = await session.execute(query).scalars().all()

                return projects, total_pages
