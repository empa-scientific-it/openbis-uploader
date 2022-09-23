from distutils.command.config import config

from datastore.services.ldap.ldap import LdapUser
from datastore.utils  import redis as redis_utils
from rq import Connection, Queue
from rq.job import Job
from datastore.utils import settings
from pydantic import BaseSettings
from typing import Any, List,  Callable, Dict

import redis

class RqSettings(BaseSettings):
    app_name: str = 'OpenbisUploader'
    redis_host:str = 'localhost'
    redis_port:int = 6379
    redis_db:int = 0
    redis_password:str = ''
    class Config:
        env_file = ".env"


def get_rq_settings() -> RqSettings:
    return RqSettings()

def get_queue() -> Queue:
    redis = redis_utils.get_redis()
    q = Queue(connection=redis, is_async=True)
    return q

def create_job(connection: redis.Redis, user: LdapUser, func: Callable, args: List[Any], kwargs: Dict[str, Any] | None = None,  timeout:int=360):
    return Job.create(func, args=args, connection=connection, timeout=timeout,  meta={'user': user.username}, kwargs=kwargs)