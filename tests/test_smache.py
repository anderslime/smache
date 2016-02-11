from smache import smache, RedisStore, RedisDependencyGraph
from smache.graph_drawer import draw

from collections import namedtuple
import pytest

import redis

# Definitions
a = smache.data_source('A')
b = smache.data_source('B')
c = smache.data_source('C')

@smache.computed(a, sources=(b, c))
def score(a):
    return a.value + 5 + 10

@smache.computed(b, c)
def h(b, c):
    return b.value + c.value

@smache.computed(a, b, c)
def f(a, b, c):
    return a.value * h(b, c)

# Tests
Entity = namedtuple('Entity', ['id', 'value'])
redis_con = redis.StrictRedis(host='localhost', port=6379, db=0)

@pytest.yield_fixture(autouse=True)
def flush_before_each_test_case():
    redis_con.flushall()
    yield


def test_cache():
    ax = Entity(1, 10)
    bx = Entity(2, 2)
    cx = Entity(3, 3)

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

def test_redis():
    key = 'hello_world'
    value = {'key': 'muthafucka'}

    store = RedisStore(redis_con)
    store.store(key, value)

    assert store.lookup(key).value == value
    assert store.is_fresh(key) == True

    store.mark_as_stale(key)

    assert store.is_fresh(key) == False


def test_source_deps():
    deps = RedisDependencyGraph(redis_con)
    deps.add_dependency('A', '1', 'hello/world')
    deps.add_dependency('A', '1', 'foo/bar')
    deps.add_dependency('A', '2', 'soo/tar')
    deps.add_dependency('B', '1', 'lalala')
    deps.add_data_source_dependency('A', 'full')

    assert deps.values_depending_on('A', '1') == set(['hello/world', 'foo/bar', 'full'])
    assert deps.values_depending_on('A', '2') == set(['soo/tar', 'full'])
    assert deps.values_depending_on('B', '1') == set(['lalala'])
