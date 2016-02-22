import redis
from stores import RedisStore
from function_serializer import FunctionSerializer

global computed_repo
computed_repo = 'NO_REPO_SET'

class AsyncScheduler:
    def __init__(self, worker_queue, comp_repo):
        self.worker_queue = worker_queue

        global computed_repo
        computed_repo = comp_repo

    def schedule_write_through(self, keys):
        for key in keys:
            self.worker_queue.enqueue_call(func=_execute, args=(key,))


class InProcessScheduler:
    def schedule_write_through(self, keys):
        for key in keys:
            _execute(key)


def _execute(key):
    if computed_repo == 'NO_REPO_SET':
        raise Exception("computed_repo is not set for the scheduler module")

    redis_con      = redis.StrictRedis(host='localhost', port=6379, db=0)
    store          = RedisStore(redis_con)

    fun_name, args = FunctionSerializer().deserialized_fun(key)
    computed_fun   = computed_repo.get_from_id(fun_name)
    computed_value = computed_fun(*args)
    return store.store(key, computed_value)
