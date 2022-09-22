from datastore.utils  import redis as redis_utils
from rq import Connection, Queue
from datastore.utils import settings

def get_queue() -> Queue:
    redis = redis_utils.get_redis()
    q = Queue(connection=redis)
    return q