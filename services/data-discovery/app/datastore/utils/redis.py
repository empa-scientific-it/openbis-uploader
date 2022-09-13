import redis
from datastore.utils import settings

def get_redis() -> redis.Redis:
    config = settings.get_settings()
    return redis.Redis(config.redis_host, config.redis_port, config.redis_db, config.redis_password)