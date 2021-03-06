from rq import SimpleWorker
from smache.data_sources.in_memory_data_source import InMemoryEntity
from smache.testing import relation_detector, RelationMissingError  # NOQA
from mongoengine import Document  # NOQA
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
