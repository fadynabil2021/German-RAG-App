from celery_app import celery_app
from core.container import container
import asyncio
from uuid import UUID
import structlog
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models import ResponseSignal

logger = structlog.get_logger(__name__)

@celery_app.task(
    bind=True, name="tasks.data_indexing.index_data_content",
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3, 'countdown': 60}
)
def index_data_content(self, project_id: int, do_reset: int):
    return asyncio.run(
        _index_data_content(self, project_id, do_reset)
    )

async def _index_data_content(task_instance, project_id: int, do_reset: int):
    try:
        db_client = container.db_session_factory
        tutor_service = container.tutor_service
        
        project_model = await ProjectModel.create_instance(db_client=db_client)
        chunk_model = await ChunkModel.create_instance(db_client=db_client)

        project = await project_model.get_project_or_create_one(project_id=project_id)

        if not project:
            task_instance.update_state(
                state="FAILURE",
                meta={"signal": ResponseSignal.PROJECT_NOT_FOUND_ERROR.value}
            )
            raise Exception(f"No project found for project_id: {project_id}")
    
        has_records = True
        page_no = 1
        inserted_items_count = 0

        # Create collection if not exists
        collection_name = tutor_service.create_collection_name(project_id=project.project_id)
        await tutor_service.vectordb_client.create_collection(
            collection_name=collection_name,
            embedding_size=tutor_service.embedding_client.embedding_size,
            do_reset=bool(do_reset),
        )

        while has_records:
            page_chunks = await chunk_model.get_poject_chunks(project_id=project.project_id, page_no=page_no)
            if not page_chunks:
                has_records = False
                break
            
            page_no += 1
            chunks_ids = [c.chunk_id for c in page_chunks]
            
            is_inserted = await tutor_service.index_chunks(
                project_id=project.project_id,
                texts=[c.chunk_text for c in page_chunks],
                metadata=[c.chunk_metadata for c in page_chunks],
                record_ids=chunks_ids,
                do_reset=False
            )

            if not is_inserted:
                task_instance.update_state(
                    state="FAILURE",
                    meta={"signal": ResponseSignal.INSERT_INTO_VECTORDB_ERROR.value}
                )
                raise Exception(f"Cannot insert into vectorDB | project_id: {project_id}")

            inserted_items_count += len(page_chunks)
        
        task_instance.update_state(
            state="SUCCESS",
            meta={"signal": ResponseSignal.INSERT_INTO_VECTORDB_SUCCESS.value}
        )

        return {
            "signal": ResponseSignal.INSERT_INTO_VECTORDB_SUCCESS.value,
            "inserted_items_count": inserted_items_count
        }

    except Exception as e:
        logger.error("Task failed", error=str(e))
        raise