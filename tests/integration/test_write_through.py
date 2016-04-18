from smache import Smache
from tests.helper import execute_all_jobs, redis_con, DummyA, DummyB
import pytest
from rq import Queue


def setup_module(module):
    global smache, hyphen, slash, worker_queue
    worker_queue = Queue('test_queue', connection=redis_con)
    smache = Smache(worker_queue=worker_queue, write_through=True)

    @smache.computed(DummyA, DummyB)
    def hyphen(a, b):
        return ' - '.join([a.value, b.value])

    @smache.sources(DummyA)
    @smache.computed()
    def slash():
        return '/'.join([DummyA.find('1').value, DummyA.find('2').value])


@pytest.yield_fixture(autouse=True)
def flush_before_each_test_case():
    smache._set_globals()
    DummyA.set_data({'1': {'value': 'hello'}, '2': {'value': 'hihi'}})
    DummyB.set_data({'1': {'value': 'world'}})
    redis_con.flushall()
    yield


def test_write_through():
    ax = DummyA(1, 'hello')
    bx = DummyB(1, 'world')

    assert hyphen(ax, bx) == 'hello - world'
    assert slash() == 'hello/hihi'

    assert smache.is_fun_fresh(hyphen, ax, bx) == True

    DummyA.update(1, {'value': 'wtf'})

    execute_all_jobs(worker_queue, redis_con)

    assert smache.is_fun_fresh(hyphen, ax, bx) == True

    assert smache.function_cache_value(
        hyphen, ax, bx
    ) == 'wtf - world'


def test_write_through_with_collection_wide_subscription():
    assert slash() == 'hello/hihi'

    DummyA.update(2, {'value': 'lol'})

    execute_all_jobs(worker_queue, redis_con)

    assert smache.function_cache_value(slash) == 'hello/lol'
