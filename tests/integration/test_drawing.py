from smache import Smache
from smache.data_sources.in_memory_data_source import InMemoryEntity
import pytest
import redis
import os


class DummyA(InMemoryEntity):
    pass

smache = Smache()


@smache.computed(DummyA)
def score(a):
    return a.value

# Tests
redis_con = redis.StrictRedis(host='localhost', port=6379, db=0)


@pytest.yield_fixture(autouse=True)
def flush_before_each_test_case():
    redis_con.flushall()
    yield


def test_draw():
    execution_path = os.getcwd()
    dot_file_path = '{}/tests/hello.dot'.format(execution_path)
    png_file_path = '{}/tests/hello.png'.format(execution_path)

    smache.draw('tests/hello')

    assert os.path.exists(dot_file_path)
    assert os.path.exists(png_file_path)

    try:
        os.remove(dot_file_path)
        os.remove(png_file_path)
    except:
        pass
