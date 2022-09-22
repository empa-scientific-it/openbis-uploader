import redis
import settings
def make_redis_url(base_url: str, port:int, password: str) -> str:
    return f"redis://:{password}@{base_url}:{port}"

def get_connection() -> redis.Redis:
    config = settings.get_settings()
    return redis.Redis(config.redis_url, config.redis_port, config.redis_db, config.redis_password)