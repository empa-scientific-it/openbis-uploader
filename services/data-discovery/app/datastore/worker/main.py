import logging
from sqlite3 import connect
import settings
import utils
import argparse
from typing import Callable, List, Any
from logging import getLogger
from rq import Connection, Worker
import redis

from datastore import *

def create_app(connection: redis.Redis, queue: List[str]) -> Worker:
    
    worker = Worker(queue, connection=redis_conn)
    return worker




    
parser = argparse.ArgumentParser(description="Simple RQ worker")
parser.add_argument("queue", type=str, nargs='+')
args = parser.parse_args()
redis_conn = utils.get_connection()
worker = create_app(redis_conn, args.queue)
worker.work()