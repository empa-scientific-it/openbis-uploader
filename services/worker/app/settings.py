from pydantic import BaseSettings
from typing import List


class CelerySettings(BaseSettings):
    app_name: str = 'OpenbisUploader'
    redis_url:str = 'localhost'
    redis_port:int = 6379
    redis_password:str = ''
    task_serialiser:str = 'pickle'
    accept_content:List[str] = ['pickle']
    class Config:
        env_file = ".env"


def get_settings() -> CelerySettings:
    breakpoint()
    return CelerySettings()