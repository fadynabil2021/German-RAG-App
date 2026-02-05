from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from domains.shared.dependencies import get_db
from security.authentication import get_current_user
from models.db_schemes import User, Project, Asset
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

projects_router = APIRouter(
    prefix="/api/v1/projects",
    tags=["projects"],
)

class ProjectCreate(BaseModel):
    project_name: str
    project_description: Optional[str] = ""

class ProjectResponse(BaseModel):
    project_id: int
    project_name: str
    project_description: Optional[str]
    asset_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True

@projects_router.get("", response_model=List[ProjectResponse])
async def list_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all projects for the authenticated user.
    User-scoped via JWT. Sorted by most recent first.
    """
    result = await db.execute(
        select(
            Project.project_id,
            Project.project_name,
            Project.project_description,
            Project.created_at,
            func.count(Asset.asset_id).label("asset_count")
        )
        .outerjoin(Asset, Asset.asset_project_id == Project.project_id)
        .where(Project.project_owner == current_user.user_id)
        .group_by(Project.project_id)
        .order_by(Project.created_at.desc())
    )
    
    rows = result.fetchall()
    
    return [
        {
            "project_id": row.project_id,
            "project_name": row.project_name or f"Projekt {row.project_id}",
            "project_description": row.project_description or "",
            "asset_count": row.asset_count,
            "created_at": row.created_at or datetime.now(),
        }
        for row in rows
    ]

@projects_router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_in: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new project for the authenticated user.
    """
    new_project = Project(
        project_name=project_in.project_name,
        project_description=project_in.project_description,
        project_owner=current_user.user_id
    )
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)
    
    logger.info(f"[Projects] Created project_id={new_project.project_id} for user_id={current_user.user_id}")
    
    return {
        "project_id": new_project.project_id,
        "project_name": new_project.project_name,
        "project_description": new_project.project_description,
        "asset_count": 0,
        "created_at": new_project.created_at or datetime.now(),
    }

@projects_router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific project by ID. User-scoped.
    """
    result = await db.execute(
        select(
            Project.project_id,
            Project.project_name,
            Project.project_description,
            Project.created_at,
            func.count(Asset.asset_id).label("asset_count")
        )
        .outerjoin(Asset, Asset.asset_project_id == Project.project_id)
        .where(Project.project_id == project_id)
        .where(Project.project_owner == current_user.user_id)
        .group_by(Project.project_id)
    )
    
    row = result.fetchone()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projekt nicht gefunden"
        )
    
    return {
        "project_id": row.project_id,
        "project_name": row.project_name or f"Projekt {row.project_id}",
        "project_description": row.project_description or "",
        "asset_count": row.asset_count,
        "created_at": row.created_at or datetime.now(),
    }

@projects_router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a project. User-scoped.
    """
    result = await db.execute(
        select(Project)
        .where(Project.project_id == project_id)
        .where(Project.project_owner == current_user.user_id)
    )
    project = result.scalars().first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projekt nicht gefunden"
        )
    
    await db.delete(project)
    await db.commit()
    
    logger.info(f"[Projects] Deleted project_id={project_id} for user_id={current_user.user_id}")
