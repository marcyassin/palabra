import redis
from rq import Queue
from worker.config.settings import REDIS_URL

redis_conn = redis.from_url(REDIS_URL)

queue = Queue("books", connection=redis_conn)
