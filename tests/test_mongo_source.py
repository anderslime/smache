from smache import Smache, RedisStore, RedisDependencyGraph
from smache.data_sources import MongoDataSource
from mongoengine import Document, StringField, IntField, connect

from collections import namedtuple
import pytest

import redis

# Definitions
smache = Smache()
db = connect('testdb', host='localhost', port=27017,)

class User(Document):
    name = StringField()
    age = IntField()

a = MongoDataSource(User)

smache.add_sources(a)

@smache.computed(a)
def name(a):
    return a.name

# Tests
Entity = namedtuple('Entity', ['id', 'value'])
redis_con = redis.StrictRedis(host='localhost', port=6379, db=0)

@pytest.yield_fixture(autouse=True)
def flush_before_each_test_case():
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
