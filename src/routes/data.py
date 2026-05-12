from fastapi import FastAPI, APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
import os
from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController, ProcessController
import aiofiles
from models import ResponseSignal
import logging
from .schemes.data import ProcessRequest
from security.authentication import get_current_user
from domains.learning.repository import ProjectRepository
from domains.learning.asset_repository import AssetRepository
from domains.shared.dependencies import get_project_repo, get_asset_repo
from models.db_schemes import Asset, User
from models.enums.AssetTypeEnum import AssetTypeEnum
from tasks.file_processing import process_project_files
from tasks.process_workflow import process_and_push_workflow
from security.quotas import check_message_quota, check_asset_quota

# Logger setup

logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"],
)

@data_router.post("/upload/{project_id}")
async def upload_data(request: Request, project_id: int, file: UploadFile,
                      app_settings: Settings = Depends(get_settings),
                      current_user: User = Depends(get_current_user),
                      project_repo: ProjectRepository = Depends(get_project_repo),
                      asset_repo: AssetRepository = Depends(get_asset_repo),
                      quota_check: bool = Depends(check_asset_quota)):
        
    project = await project_repo.get_or_create(
        project_id=project_id,
        owner_id=current_user.user_id
    )

    if not project:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "signal": "PROJECT_NOT_FOUND_OR_ACCESS_DENIED"
            }
        )

    # validate the file properties
    data_controller = DataController()

    is_valid, result_signal = data_controller.validate_uploaded_file(file=file)

    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": result_signal
            }
        )

    project_dir_path = ProjectController().get_project_path(project_id=project_id)
    file_path, file_id = data_controller.generate_unique_filepath(
        orig_file_name=file.filename,
        project_id=project_id
    )

    try:
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:

        logger.error(f"Error while uploading file: {e}")

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.FILE_UPLOAD_FAILED.value
            }
        )

    # store the assets into the database via repository
    asset_resource = Asset(
        asset_project_id=project.project_id,
        asset_type=AssetTypeEnum.FILE.value,
        asset_name=file_id,
        asset_size=os.path.getsize(file_path)
    )

    asset_record = await asset_repo.save(asset=asset_resource)

    logger.info(f"[G-RAG] Document uploaded: user={current_user.user_id}, project={project.project_id}, filename={file.filename}")

    # Automatically trigger processing and indexing workflow
    process_and_push_workflow.delay(
        project_id=project.project_id,
        file_id=file_id,
        chunk_size=1000, # Default chunk size for German RAG
        overlap_size=100,
        do_reset=0
    )

    return JSONResponse(
            content={
                "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
                "file_id": str(asset_record.asset_id),
                "project_id": project.project_id
            }
        )

@data_router.post("/process/{project_id}")
async def process_endpoint(request: Request, project_id: int, process_request: ProcessRequest,
                           current_user: User = Depends(get_current_user),
                           project_repo: ProjectRepository = Depends(get_project_repo)):

    project = await project_repo.get_or_create(project_id=project_id, owner_id=current_user.user_id)
    
    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": "PROJECT_NOT_FOUND"
            }
        )

    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    task = process_project_files.delay(
        project_id=project_id,
        file_id=process_request.file_id,
        chunk_size=chunk_size,
        overlap_size=overlap_size,
        do_reset=do_reset,
    )

    return JSONResponse(
        content={
            "signal": ResponseSignal.PROCESSING_SUCCESS.value,
            "task_id": task.id
        }
    )

@data_router.post("/process-and-push/{project_id}")
async def process_and_push_endpoint(request: Request, project_id: int, process_request: ProcessRequest,
                                    current_user: User = Depends(get_current_user),
                                    project_repo: ProjectRepository = Depends(get_project_repo)):

    project = await project_repo.get_or_create(project_id=project_id, owner_id=current_user.user_id)
    
    if not project:
         return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": "PROJECT_NOT_FOUND"
            }
        )

    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    workflow_task = process_and_push_workflow.delay(
        project_id=project_id,
        file_id=process_request.file_id,
        chunk_size=chunk_size,
        overlap_size=overlap_size,
        do_reset=do_reset,
    )

    return JSONResponse(
        content={
            "signal": ResponseSignal.PROCESS_AND_PUSH_WORKFLOW_READY.value,
            "workflow_task_id": workflow_task.id
        }
    )
