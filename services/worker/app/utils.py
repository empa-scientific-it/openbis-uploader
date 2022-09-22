def make_redis_url(base_url: str, port:int, password: str) -> str:
    return f"redis://:{password}@{base_url}:{port}"