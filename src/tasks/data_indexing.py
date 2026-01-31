from celery_app import celery_app
from core.container import container
from helpers.config import get_settings
import asyncio
from fastapi.responses import JSONResponse
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from controllers import NLPController
from models import ResponseSignal
from tqdm.auto import tqdm

import logging
logger = logging.getLogger(__name__)

@celery_app.task(
                 bind=True, name="tasks.data_indexing.index_data_content",
                 autoretry_for=(Exception,),
                 retry_kwargs={'max_retries': 3, 'countdown': 60}
                )
def index_data_content(self, project_id: int, do_reset: int):

    logger.warning("index_data_content started")
    return asyncio.run(
        _index_data_content(self, project_id, do_reset)
    )

async def _index_data_content(task_instance, project_id: int, do_reset: int):

    db_engine, vectordb_client = None, None

    try:
        # Use container
        db_engine = container.db_engine
        db_client = container.db_session_factory
        llm_provider_factory = container.llm_provider_factory
        vectordb_provider_factory = container.vectordb_provider_factory
        settings = container.settings

        logger.warning("Setup utils were loaded!")

        project_model = await ProjectModel.create_instance(
            db_client=db_client
        )

        chunk_model = await ChunkModel.create_instance(
            db_client=db_client
        )

        project = await project_model.get_project_or_create_one(
            project_id=project_id
        )

        if not project:

            task_instance.update_state(
                state="FAILURE",
                meta={
                    "signal": ResponseSignal.PROJECT_NOT_FOUND_ERROR.value
                }
            )

            raise Exception(f"No project found for project_id: {project_id}")
    
        # Use pre-wired TutorService from container
        tutor_service = container.tutor_service

        has_records = True
        page_no = 1
        inserted_items_count = 0
        idx = 0

        # create collection if not exists
        collection_name = tutor_service.create_collection_name(project_id=project.project_id)

        _ = await vectordb_client.create_collection(
            collection_name=collection_name,
            embedding_size=tutor_service.embedding_client.embedding_size,
            do_reset=do_reset,
        )

        # setup batching
        total_chunks_count = await chunk_model.get_total_chunks_count(project_id=project.project_id)
        pbar = tqdm(total=total_chunks_count, desc="Vector Indexing", position=0)

        while has_records:
            page_chunks = await chunk_model.get_poject_chunks(project_id=project.project_id, page_no=page_no)
            if len(page_chunks):
                page_no += 1
            
            if not page_chunks or len(page_chunks) == 0:
                has_records = False
                break

            chunks_ids =  [ c.chunk_id for c in page_chunks ]
            idx += len(page_chunks)
            
            # Use tutor_service for indexing
            is_inserted = await tutor_service.index_chunks(
                project_id=project.project_id,
                texts=[c.chunk_text for c in page_chunks],
                metadata=[c.chunk_metadata for c in page_chunks],
                record_ids=chunks_ids,
                do_reset=False # Only reset on the first call (already handled above)
            )

            if not is_inserted:
                

                task_instance.update_state(
                    state="FAILURE",
                    meta={
                        "signal": ResponseSignal.INSERT_INTO_VECTORDB_ERROR.value
                    }
                )

                raise Exception(f"can not insert into vectorDB | project_id: {project_id}")

            pbar.update(len(page_chunks))
            inserted_items_count += len(page_chunks)
        

        task_instance.update_state(
            state="SUCCESS",
            meta={
                "signal": ResponseSignal.INSERT_INTO_VECTORDB_SUCCESS.value,
            }
        )

        return {
                "signal": ResponseSignal.INSERT_INTO_VECTORDB_SUCCESS.value,
                "inserted_items_count": inserted_items_count
        }

    except Exception as e:
        logger.error(f"Task failed: {str(e)}")
        raise