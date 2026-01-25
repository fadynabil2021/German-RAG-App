from celery_app import celery_app
from core.container import container
from helpers.config import get_settings
import asyncio
from utils.idempotency_manager import IdempotencyManager

import logging
logger = logging.getLogger(__name__)

@celery_app.task(
                 bind=True, name="tasks.maintenance.clean_celery_executions_table",
                 autoretry_for=(Exception,),
                 retry_kwargs={'max_retries': 3, 'countdown': 60}
                )
def clean_celery_executions_table(self):

    return asyncio.run(
        _clean_celery_executions_table(self)
    )

async def _clean_celery_executions_table(task_instance):

    db_engine = None
    
    try:
        db_engine = container.db_engine
        db_client = container.db_session_factory
        
        # Create idempotency manager
        idempotency_manager = IdempotencyManager(db_client, db_engine)

        logger.warning(f"cleaning !!!")
        _ = await idempotency_manager.cleanup_old_tasks(5)

        return True

    except Exception as e:
        logger.error(f"Task failed: {str(e)}")
        raise