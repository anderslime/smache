from smache import Smache, Raw
from smache.data_sources import DummyDataSource, RawDataSource
from smache.schedulers import InProcessScheduler
from tests.dummy_data_source_helper import DummyA, DummyB
import pytest
import redis

# Definitions
smache = Smache(scheduler=InProcessScheduler())

smache.add_sources(DummyA, DummyB, Raw)


@smache.computed(
    DummyA,
    Raw,
    Raw,
    relations=[(DummyB, lambda b: DummyA.find('1'))]
)
def f(a, c, d):
    b = DummyB.find('2')
    return a.value * b.value


@smache.computed(
    DummyA,
    Raw,
    Raw,
    relations=[(DummyB, lambda b: [DummyA.find('1'), DummyA.find('2')])]
)
def h(a, c, d):
    b = DummyB.find('2')
    return a.value * b.value

# Tests
redis_con = redis.StrictRedis(host='localhost', port=6379, db=0)


@pytest.yield_fixture(autouse=True)
def flush_before_each_test_case():
    redis_con.flushall()
    yield


def test_computed_function_are_updated_when_relations_are():
    ax = DummyA('1', 10)
    ax2 = DummyB('2', 500)

    assert f(ax, 5, 10) == 200
    assert f(ax2, 5, 10) == 10000

    DummyB.update('1', {'value': 30})

    assert smache.is_fun_fresh(f, ax, 5, 10) == False
    assert smache.is_fun_fresh(f, ax2, 5, 10) == True


def test_relations_with_list():
    ax = DummyA('1', 10)
    ax2 = DummyB('2', 500)

    assert h(ax, 5, 10) == 200
    assert h(ax2, 5, 10) == 10000

    DummyB.update('2', {'value': 30})

    assert smache.is_fun_fresh(h, ax, 5, 10) == False
    assert smache.is_fun_fresh(h, ax2, 5, 10) == False
