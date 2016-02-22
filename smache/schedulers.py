import redis
from stores import RedisStore
from function_serializer import FunctionSerializer

import smache

from smache.smache_logging import logger

class AsyncScheduler:
    def __init__(self, worker_queue):
        self.worker_queue = worker_queue

    def schedule_write_through(self, keys):
        logger.debug("Schedule write through update on: {}".format(keys))
        for key in keys:
            self.worker_queue.enqueue_call(func=_execute, args=(key,))


class InProcessScheduler:
    def schedule_write_through(self, keys):
        for key in keys:
            _execute(key)


def _execute(key):
    logger.debug("EXECUTE on {}".format(key))
    redis_con      = redis.StrictRedis(host='localhost', port=6379, db=0)
    store          = RedisStore(redis_con)

    fun_name, args = FunctionSerializer().deserialized_fun(key)
    computed_fun   = smache.computed_repo.get_from_id(fun_name)
    computed_value = computed_fun(*args)
    return store.store(key, computed_value)
