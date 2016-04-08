from rq import SimpleWorker
from smache.data_sources.dummy_data_source import DummyEntity
import redis

redis_con = redis.StrictRedis(host='localhost', port=6379, db=0)


class DummyA(DummyEntity):
    pass


class DummyB(DummyEntity):
    pass


class DummyC(DummyEntity):
    pass


def execute_all_jobs(worker_queue, redis_con):
    worker = SimpleWorker([worker_queue], connection=redis_con)
    worker.work(burst=True)
