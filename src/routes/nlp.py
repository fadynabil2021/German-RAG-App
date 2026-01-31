from fastapi import FastAPI, APIRouter, status, Request, Depends
from fastapi.responses import JSONResponse
from routes.schemes.nlp import PushRequest, SearchRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models import ResponseSignal
from tasks.data_indexing import index_data_content
from models.db_schemes import User
from domains.identity import get_current_user
from domains.tutor import TutorService, TutoringMode
from core.container import container

import logging

logger = logging.getLogger('uvicorn.error')

nlp_router = APIRouter(
    prefix="/api/v1/nlp",
    tags=["api_v1", "nlp"],
)

@nlp_router.post("/index/push/{project_id}")
async def index_project(request: Request, project_id: int, push_request: PushRequest,
                        current_user: User = Depends(get_current_user)):

    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    project = await project_model.get_project_or_create_one(
        project_id=project_id,
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
async def get_project_index_info(request: Request, project_id: int,
                                 current_user: User = Depends(get_current_user)):
    
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    project = await project_model.get_project_or_create_one(
        project_id=project_id,
        owner_id=current_user.user_id
    )

    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.PROJECT_NOT_FOUND_ERROR.value
            }
        )

    # Use new async tutor service
    tutor_service = TutorService(
        llm_provider=container.async_llm_provider,
        vectordb_client=request.app.vectordb_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser,
    )

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
async def search_index(request: Request, project_id: int, search_request: SearchRequest,
                       current_user: User = Depends(get_current_user)):
    
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    project = await project_model.get_project_or_create_one(
        project_id=project_id,
        owner_id=current_user.user_id
    )

    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.PROJECT_NOT_FOUND_ERROR.value
            }
        )

    # Use new async tutor service
    tutor_service = TutorService(
        llm_provider=container.async_llm_provider,
        vectordb_client=request.app.vectordb_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser,
    )

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
async def answer_rag(request: Request, project_id: int, search_request: SearchRequest,
                     current_user: User = Depends(get_current_user)):
    
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    project = await project_model.get_project_or_create_one(
        project_id=project_id,
        owner_id=current_user.user_id
    )

    if not project:
         return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.PROJECT_NOT_FOUND_ERROR.value
            }
        )

    # Use new async tutor service
    tutor_service = TutorService(
        llm_provider=container.async_llm_provider,
        vectordb_client=request.app.vectordb_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser,
    )

    # Retrieve context
    context_results = await tutor_service.retrieve_context(
        query=search_request.text,
        project_id=project.project_id,
        limit=search_request.limit
    )

    if not context_results:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.RAG_ANSWER_ERROR.value,
                "message": "No relevant context found"
            }
        )

    # Extract text from context
    context_texts = [result["text"] for result in context_results]

    # Generate answer using async LLM
    answer = await tutor_service.tutor_response(
        query=search_request.text,
        context=context_texts,
        level="B1",  # TODO: Get from user profile
        mode=TutoringMode.SOCRATIC
    )

    if not answer:
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.RAG_ANSWER_ERROR.value
                }
        )
    
    return JSONResponse(
        content={
            "signal": ResponseSignal.RAG_ANSWER_SUCCESS.value,
            "answer": answer,
            "context_count": len(context_results)
        }
    )
