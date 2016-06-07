from redis import StrictRedis
from rq import Queue
from mock import Mock

from smache.options import Options
from smache.schedulers import AsyncScheduler


def test_defaults():
    options = Options()

    assert options.write_through == True
    assert options.debug == False
    assert isinstance(options.redis_con, StrictRedis)
    assert isinstance(options.worker_queue, Queue)
    assert isinstance(options.scheduler, AsyncScheduler)


def test_write_through_is_set():
    assert Options(write_through=False).write_through == False


def test_debug_is_set():
    assert Options(debug=True).debug == True


def test_redis_con_is_set():
    redis_con = StrictRedis()
    assert Options(redis_con=redis_con).redis_con == redis_con


def test_worker_queue_is_set():
    worker_queue = Mock()
    assert Options(worker_queue=worker_queue).worker_queue == worker_queue


def test_scheduler_is_set():
    scheduler = Mock()
    assert Options(scheduler=scheduler).scheduler == scheduler
