import redis
import smache

from .stores import RedisStore
from .function_serializer import FunctionSerializer
from .data_update_propagator import DataUpdatePropagator
from .smache_logging import logger
from functools import reduce

class AsyncScheduler:

    def __init__(self, worker_queue):
        self.worker_queue = worker_queue

    def schedule_write_through(self, keys):
        logger.debug("Schedule write through update on: {}".format(keys))
        reduce(self._enqueue_execute, keys, None)

    def schedule_update_handle(self, data_source_id, entity_id):
        self.worker_queue.enqueue_call(
            func=_handle_data_source_update,
            args=(data_source_id, entity_id),
            at_front=True # TODO: Use queue prioritization instead of this
        )

    def _enqueue_execute(self, last_job, key):
        return self.worker_queue.enqueue_call(
            func=_execute_from_key,
            args=(key,),
            depends_on=last_job
        )


class InProcessScheduler:

    def schedule_write_through(self, keys):
        for key in keys:
            _execute_from_key(key)

    def schedule_update_handle(self, data_source_id, entity_id):
        _handle_data_source_update(data_source_id, entity_id)


def _handle_data_source_update(data_source_id, entity_id):
    DataUpdatePropagator().handle_update(data_source_id, entity_id)


def _execute_from_key(key):
    logger.debug("EXECUTE on {}".format(key))
    redis_con = redis.StrictRedis(host='localhost', port=6379, db=0)
    store = RedisStore(redis_con)

    fun_name, args = FunctionSerializer().deserialized_fun(key)
    computed_fun = smache._instance._computed_repo.get_from_id(fun_name)
    return execute(store, key, computed_fun, *args)

def execute(store, key, computed_fun, *args, **kwargs):
    computed_value = computed_fun(*args)
    store.store(key, computed_value)
    return computed_value
