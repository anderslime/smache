from smache import Smache, RedisStore
from smache.data_sources.dummy_data_source import DummyEntity
from smache.data_sources import DummyDataSource, RawDataSource

from collections import namedtuple
import pytest

import redis

# Definitions
smache = Smache()
a = DummyDataSource('A')
b = DummyDataSource('B')
c = DummyDataSource('C')
raw = RawDataSource()

smache.add_sources(a, b, c, raw)

@smache.computed(a, sources=(b, c))
def score(a):
    return a.value + 5 + 10

@smache.computed(b, c)
def h(b, c):
    return b.value + c.value

@smache.computed(a, b, c)
def f(a, b, c):
    return a.value * h(b, c)

@smache.computed(a, b, raw)
def with_raw(a, b, static_value):
    return (a.value + b.value) * static_value

# Tests
redis_con = redis.StrictRedis(host='localhost', port=6379, db=0)

@pytest.yield_fixture(autouse=True)
def flush_before_each_test_case():
    redis_con.flushall()
    yield

def test_cache():

    ax = DummyEntity(a.data_source_id, 1, 10)
    bx = DummyEntity(b.data_source_id, 2, 2)
    cx = DummyEntity(c.data_source_id, 3, 3)

    assert f(ax, bx, cx) == 50
    assert h(bx, cx) == 5
    assert score(ax)

    assert smache.is_fun_fresh(score, ax) == True
    assert smache.is_fun_fresh(f, ax, bx, cx) == True
    assert smache.is_fun_fresh(h, bx, cx) == True

    b.did_update(0)

    assert smache.is_fun_fresh(score, ax) == False
    assert smache.is_fun_fresh(f, ax, bx, cx) == True
    assert smache.is_fun_fresh(h, bx, cx) == True

    a.did_update(1)

    assert smache.is_fun_fresh(score, ax) == False
    assert smache.is_fun_fresh(f, ax, bx, cx) == False
    assert smache.is_fun_fresh(h, bx, cx) == True

    b.did_update(2)

    assert smache.is_fun_fresh(score, ax) == False
    assert smache.is_fun_fresh(f, ax, bx, cx) == False
    assert smache.is_fun_fresh(h, bx, cx) == False

def test_with_raw_value():
    ax = DummyEntity(a.data_source_id, 1, 10)
    bx = DummyEntity(b.data_source_id, 2, 2)

    assert with_raw(ax, bx, 1000) == 12000


def test_redis():
    key = 'hello_world'
    value = {'key': 'muthafucka'}

    store = RedisStore(redis_con)
    store.store(key, value)

    assert store.lookup(key).value == value
    assert store.is_fresh(key) == True

    store.mark_as_stale(key)

    assert store.is_fresh(key) == False
