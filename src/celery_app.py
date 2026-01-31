from celery import Celery
from celery.signals import worker_process_init
from core.container import container

# Create Celery application instance
celery_app = Celery(
    "minirag",
    broker=container.settings.CELERY_BROKER_URL,
    backend=container.settings.CELERY_RESULT_BACKEND,
    include=[
        "tasks.file_processing",
        "tasks.data_indexing",
        "tasks.process_workflow",
        "tasks.maintenance",
    ]
)

@worker_process_init.connect
def init_worker(**kwargs):
    # This runs in each worker process after the fork.
    # We touch the db_engine to initialize the connection pool for this process.
    _ = container.db_engine
    print("Worker process initialized DB engine.")

# Configure Celery with essential settings
celery_app.conf.update(
    task_serializer=container.settings.CELERY_TASK_SERIALIZER,
    result_serializer=container.settings.CELERY_TASK_SERIALIZER,
    accept_content=[
        container.settings.CELERY_TASK_SERIALIZER
    ],

    # Task safety - Late acknowledgment prevents task loss on worker crash
    task_acks_late=True, # Hardcoded or add to config if critical

    # Time limits - Prevent hanging tasks
    task_time_limit=container.settings.CELERY_TASK_TIME_LIMIT,

    # Result backend - Store results for status tracking
    task_ignore_result=False,
    result_expires=3600,

    # Worker settings
    worker_concurrency=container.settings.CELERY_WORKER_CONCURRENCY,

    # Connection settings for better reliability
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=10,
    worker_cancel_long_running_tasks_on_connection_loss=True,

    task_routes={
        "tasks.file_processing.process_project_files": {"queue": "file_processing"},
        "tasks.data_indexing.index_data_content": {"queue": "data_indexing"},
        "tasks.process_workflow.process_and_push_workflow": {"queue": "file_processing"},
        "tasks.maintenance.clean_celery_executions_table": {"queue": "default"},
    },

    beat_schedule={
        'cleanup-old-task-records': {
            'task': "tasks.maintenance.clean_celery_executions_table",
            'schedule': 10,
            'args': ()
        }
    },

    timezone='UTC',

)

celery_app.conf.task_default_queue = "default"