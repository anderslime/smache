from smache import Smache, RedisStore, RedisDependencyGraph
from smache.data_sources.dummy_data_source import DummyEntity, DummyDataSource

import pytest

import redis

# Definitions
smache = Smache(write_through=True)

a = DummyDataSource('A', {'1': {'value': 'hello'}, '2': {'value': 'hihi'}})
b = DummyDataSource('B', {'1': {'value': 'world'}})

smache.add_sources(a, b)

@smache.computed(a, b)
def hyphen(a, b):
    return ' - '.join([a.value, b.value])

@smache.computed(sources=(a), computed_deps=(hyphen))
def slash():
    return '/'.join([a.find('1').value, a.find('2').value])

# Tests
redis_con = redis.StrictRedis(host='localhost', port=6379, db=0)

@pytest.yield_fixture(autouse=True)
def flush_before_each_test_case():
    a.reset()
    b.reset()
    redis_con.flushall()
    yield

def test_write_through():
    ax = DummyEntity(1, 'hello')
    bx = DummyEntity(1, 'world')

    assert hyphen(ax, bx) == 'hello - world'
    assert slash() == 'hello/hihi'

    assert smache.is_fun_fresh(hyphen, ax, bx) == True

    a.update(1, {'value': 'wtf'})

    assert smache.is_fun_fresh(hyphen, ax, bx) == True
    assert smache._cache_manager.function_cache_value(hyphen, ax, bx) == 'wtf - world'

def test_write_through_with_collection_wide_subscription():
    assert slash() == 'hello/hihi'

    a.update(2, {'value': 'lol'})

    assert smache._cache_manager.function_cache_value(slash) == 'hello/lol'
