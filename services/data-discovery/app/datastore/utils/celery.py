
import celery
from datastore.utils import settings

def get_celery() -> celery.Celery:
    config = settings.get_settings()
    backend_url = f"redis://:{config.redis_password}@{config.redis_host}:{config.redis_port}/{config.redis_db}"
    app = celery.Celery('tasks', broker=backend_url, backend=backend_url, task_serializer=config.task_serialiser)
    return app