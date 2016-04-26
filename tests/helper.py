from rq import SimpleWorker
from smache.data_sources.in_memory_data_source import InMemoryEntity
import redis

redis_con = redis.StrictRedis(host='localhost', port=6379, db=5)


class DummyA(InMemoryEntity):
    pass


class DummyB(InMemoryEntity):
    pass


class DummyC(InMemoryEntity):
    pass


def execute_all_jobs(worker_queue, redis_con):
    worker = SimpleWorker([worker_queue], connection=redis_con)
    worker.work(burst=True)
