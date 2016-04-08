from smache import Smache
from smache.data_sources import MongoDataSource
from smache.schedulers import InProcessScheduler
from tests.mongo_helper import User, test_connect

import pytest
import redis

# Definitions
test_connect()

smache = Smache(scheduler=InProcessScheduler())


@smache.computed(User)
def name(a):
    return a.name


@smache.computed(sources=(User))
def score():
    return 50


def teardown_module(module):
    for data_source in smache._data_sources:
        if isinstance(data_source, MongoDataSource):
            data_source.disconnect()

# Tests
redis_con = redis.StrictRedis(host='localhost', port=6379, db=0)


@pytest.yield_fixture(autouse=True)
def flush_before_each_test_case():
    smache._set_globals()
    redis_con.flushall()
    yield


def test_depending_computed_are_invalidated_on_save():
    user = User(name='Anders', age=12)
    user.save()

    assert name(user) == 'Anders'
    assert smache.is_fun_fresh(name, user) == True

    user.name = 'Emil'

    user.save()

    assert smache.is_fun_fresh(name, user) == False


def test_collection_whide_invalidation():
    user = User(name='Anders', age=12)
    user.save()

    assert score() == 50

    assert smache.is_fun_fresh(score) == True

    user.name = 'Emil'
    user.save()

    assert smache.is_fun_fresh(score) == False
