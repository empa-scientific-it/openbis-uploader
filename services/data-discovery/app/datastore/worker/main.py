from http import server
import logging
from sqlite3 import connect

import utils
import argparse
from typing import Callable, List, Any
from logging import getLogger
from rq import Connection, Worker
from redis import Redis

from datastore.utils import rq, redis




def create_app(connection: Redis, queue: List[str]) -> Worker:
    worker = Worker(queue, connection=redis_conn)
    return worker




    
parser = argparse.ArgumentParser(description="Simple RQ worker")
parser.add_argument("queue", type=str, nargs='+')
parser.add_argument("--n-workers", type=int)
args = parser.parse_args()
settings = rq.get_rq_settings()
redis_conn = Redis(settings.redis_host, settings.redis_port, settings.redis_db, settings.redis_password)
worker = create_app(redis_conn, args.queue)
worker.work()