from smache import Smache
from smache.data_sources.dummy_data_source import DummyEntity, DummyDataSource
from tests.helper import execute_all_jobs

import pytest

import redis
from rq import Queue

# Definitions
redis_con = redis.StrictRedis(host='localhost', port=6379, db=0)
worker_queue = Queue('test_queue', connection=redis_con)
smache = Smache(worker_queue=worker_queue, write_through=True)

class DummyX(DummyEntity):
    data = {'1': {'value': 'hello'}, '2': {'value': 'hihi'}}

class DummyZ(DummyEntity):
    data = {'1': {'value': 'world'}}

smache.add_sources(DummyX, DummyZ)


@smache.computed(DummyX, DummyZ)
def hyphen(a, b):
    return ' - '.join([a.value, b.value])


@smache.computed(sources=(DummyX))
def slash():
    return '/'.join([DummyX.find('1').value, DummyX.find('2').value])


@pytest.yield_fixture(autouse=True)
def flush_before_each_test_case():
    smache._set_globals()
    # DummyX.reset()
    # DummyZ.reset()
    redis_con.flushall()
    yield


def test_write_through():
    ax = DummyX(1, 'hello')
    bx = DummyZ(1, 'world')

    assert hyphen(ax, bx) == 'hello - world'
    assert slash() == 'hello/hihi'

    assert smache.is_fun_fresh(hyphen, ax, bx) == True

    DummyX.update(1, {'value': 'wtf'})

    execute_all_jobs(worker_queue, redis_con)

    assert smache.is_fun_fresh(hyphen, ax, bx) == True

    assert smache._cache_manager.function_cache_value(
        hyphen, ax, bx
    ) == 'wtf - world'


def test_write_through_with_collection_wide_subscription():
    assert slash() == 'hello/hihi'

    DummyX.update(2, {'value': 'lol'})

    execute_all_jobs(worker_queue, redis_con)

    assert smache._cache_manager.function_cache_value(slash) == 'hello/lol'
