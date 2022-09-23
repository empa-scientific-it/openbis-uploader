from io import StringIO
from redis import Redis

class RedisHandler(StringIO):

    def __init__(self, key, redis_client: Redis):
        """
        Create a new StringIO interface for the given key and redis_client.
        """

        StringIO.__init__(self)
        self.key = key
        self.redis_client = redis_client

    def write(self, record):
        """
        Publish record to redis logging list
        """
        self.redis_client.publish(self.key, record)