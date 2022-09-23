import redis
from datastore.utils import settings
import redis.asyncio as redis_async

def get_redis(sync=True) -> redis.Redis | redis_async.Redis:
    config = settings.get_settings()
    params = dict(host=config.redis_host, port=config.redis_port, db=config.redis_db, password=config.redis_password)
    if sync:
        return redis.Redis(**params)
    else:
        pool = redis_async.ConnectionPool(**params)
        return redis_async.Redis(connection_pool=pool)

