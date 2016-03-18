from smache import Smache
from smache.data_sources.dummy_data_source import DummyEntity
from smache.data_sources import DummyDataSource, RawDataSource
from smache.schedulers import InProcessScheduler

from collections import namedtuple
import pytest

import redis

# Definitions
smache = Smache(scheduler=InProcessScheduler())

A = DummyDataSource('A', {'1': { 'value': 10 }, '2': { 'value': 500 } })
B = DummyDataSource('B', {'2': { 'value': 20 } })
raw = RawDataSource()

smache.add_sources(A, B)

@smache.computed(A, raw, raw, relations=[(B, lambda b: A.find('1'))])
def f(a, c, d):
    b = B.find('2')
    return a.value * b.value

@smache.computed(A, raw, raw, relations=[(B, lambda b: [A.find('1'), A.find('2')])])
def h(a, c, d):
    b = B.find('2')
    return a.value * b.value

# Tests
redis_con = redis.StrictRedis(host='localhost', port=6379, db=0)

@pytest.yield_fixture(autouse=True)
def flush_before_each_test_case():
    smache._set_globals()
    A.reset()
    B.reset()
    redis_con.flushall()
    yield

def test_computed_function_are_updated_when_relations_are():
    ax = DummyEntity(A.data_source_id, '1', 10)
    ax2 = DummyEntity(A.data_source_id, '2', 500)

    assert f(ax, 5, 10) == 200
    assert f(ax2, 5, 10) == 10000

    B.update('1', {'value': 30 })

    assert smache.is_fun_fresh(f, ax, 5, 10) == False
    assert smache.is_fun_fresh(f, ax2, 5, 10) == True

def test_relations_with_list():
    ax = DummyEntity(A.data_source_id, '1', 10)
    ax2 = DummyEntity(A.data_source_id, '2', 500)

    assert h(ax, 5, 10) == 200
    assert h(ax2, 5, 10) == 10000

    B.update('2', {'value': 30 })

    assert smache.is_fun_fresh(h, ax, 5, 10) == False
    assert smache.is_fun_fresh(h, ax2, 5, 10) == False
