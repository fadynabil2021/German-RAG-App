from fastapi import FastAPI, APIRouter, status, Request, Depends
from fastapi.responses import JSONResponse
from routes.schemes.nlp import PushRequest, SearchRequest
from security.authentication import get_current_user
from domains.learning.repository import ProjectRepository
from domains.shared.dependencies import get_project_repo
from domains.tutor import TutorService, TutoringMode
from core.container import container
from models import ResponseSignal
from tasks.data_indexing import index_data_content
from models.db_schemes import User
from security.quotas import check_message_quota

from uuid import UUID
import structlog

logger = structlog.get_logger(__name__)

nlp_router = APIRouter(
    prefix="/api/v1/nlp",
    tags=["api_v1", "nlp"],
)

@nlp_router.post("/index/push/{project_id}")
async def index_project(request: Request, project_id: UUID, push_request: PushRequest,
                        current_user: User = Depends(get_current_user),
                        project_repo: ProjectRepository = Depends(get_project_repo)):

    project = await project_repo.get_or_create(
        project_uuid=project_id,
        owner_id=current_user.user_id
    )

    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.PROJECT_NOT_FOUND_ERROR.value
            }
        )

    task = index_data_content.delay(
        project_id=project_id,
        do_reset=push_request.do_reset
    )

    return JSONResponse(
        content={
            "signal": ResponseSignal.DATA_PUSH_TASK_READY.value,
            "task_id": task.id
        }
    )
    

@nlp_router.get("/index/info/{project_id}")
async def get_project_index_info(request: Request, project_id: UUID,
                                 current_user: User = Depends(get_current_user),
                                 project_repo: ProjectRepository = Depends(get_project_repo)):
    
    project = await project_repo.get_or_create(
        project_uuid=project_id,
        owner_id=current_user.user_id
    )

    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.PROJECT_NOT_FOUND_ERROR.value
            }
        )

    # Use injected async tutor service
    tutor_service = request.app.tutor_service

    collection_name = tutor_service.create_collection_name(project.project_id)
    collection_info = await request.app.vectordb_client.get_collection_info(
        collection_name=collection_name
    )

    return JSONResponse(
        content={
            "signal": ResponseSignal.VECTORDB_COLLECTION_RETRIEVED.value,
            "collection_info": collection_info
        }
    )

@nlp_router.post("/index/search/{project_id}")
async def search_index(request: Request, project_id: UUID, search_request: SearchRequest,
                       current_user: User = Depends(get_current_user),
                       project_repo: ProjectRepository = Depends(get_project_repo)):
    
    project = await project_repo.get_or_create(
        project_uuid=project_id,
        owner_id=current_user.user_id
    )

    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.PROJECT_NOT_FOUND_ERROR.value
            }
        )

    # Use injected async tutor service
    tutor_service = request.app.tutor_service

    results = await tutor_service.retrieve_context(
        query=search_request.text,
        project_id=project.project_id,
        limit=search_request.limit
    )

    if not results:
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.VECTORDB_SEARCH_ERROR.value
                }
            )
    
    return JSONResponse(
        content={
            "signal": ResponseSignal.VECTORDB_SEARCH_SUCCESS.value,
            "results": results
        }
    )

@nlp_router.post("/index/answer/{project_id}")
async def answer_rag(request: Request, project_id: UUID, search_request: SearchRequest,
                     current_user: User = Depends(get_current_user),
                     project_repo: ProjectRepository = Depends(get_project_repo),
                     quota_check: bool = Depends(check_message_quota)):
    
    # Parse and validate mode from request
    mode_str = search_request.mode or 'SOCRATIC'
    try:
        mode = TutoringMode[mode_str]
    except KeyError:
        mode = TutoringMode.SOCRATIC
    
    # Log request details
    logger.info(f"[G-RAG] user_id={current_user.user_id} project_id={project_id} mode={mode_str}")
    
    project = await project_repo.get_or_create(
        project_uuid=project_id,
        owner_id=current_user.user_id
    )

    if not project:
         return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.PROJECT_NOT_FOUND_ERROR.value,
                "error_type": "PROJECT_NOT_FOUND",
                "message": "Project does not exist or you don't have access"
            }
        )

    # Use injected async tutor service
    tutor_service = request.app.tutor_service

    # Sanitize user input
    from security.sanitizer import PromptSanitizer
    sanitized_query = PromptSanitizer.sanitize(search_request.text)

    # Retrieve context
    context_results = await tutor_service.retrieve_context(
        query=sanitized_query,
        project_id=project.project_id,
        limit=search_request.limit
    )

    if not context_results:
        logger.warning(f"[G-RAG] No context found for project_id={project_id}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.RAG_ANSWER_ERROR.value,
                "error_type": "NO_INDEXED_DOCUMENTS",
                "message": "Das Projekt hat noch keine indizierten Dokumente. Bitte laden Sie zuerst Dateien hoch."
            }
        )

    # Log embedding count
    logger.info(f"[G-RAG] Retrieved {len(context_results)} context chunks")

    # Extract text from context
    context_texts = [result["text"] for result in context_results]

    # Generate answer using async LLM - USE MODE FROM REQUEST
    answer = await tutor_service.tutor_response(
        query=search_request.text,
        context=context_texts,
        level=current_user.proficiency_level,
        mode=mode  # Now using the mode from request!
    )

    if not answer:
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.RAG_ANSWER_ERROR.value,
                    "error_type": "LLM_GENERATION_FAILED",
                    "message": "Der KI-Tutor konnte keine Antwort generieren. Bitte versuchen Sie es erneut."
                }
        )
    
    return JSONResponse(
        content={
            "signal": ResponseSignal.RAG_ANSWER_SUCCESS.value,
            "answer": answer,
            "context_count": len(context_results),
            "mode": mode_str
        }
    )
