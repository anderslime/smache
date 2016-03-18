import redis
import pytest

from smache.stores import RedisStore

redis_con = redis.StrictRedis(host='localhost', port=6379, db=0)


@pytest.yield_fixture(autouse=True)
def flush_before_each_test_case():
    redis_con.flushall()
    yield


def test_stored_elements_can_be_lookued_up():
    redis_store = RedisStore(redis_con)
    redis_store.store("hello", "world")

    stored_element = redis_store.lookup("hello")

    assert stored_element.value == "world"


def test_newly_stored_elements_are_fresh():
    redis_store = RedisStore(redis_con)
    redis_store.store("hello", "world")

    assert redis_store.is_fresh("hello") == True


def test_key_marked_as_stale_is_not_fresh():
    redis_store = RedisStore(redis_con)
    redis_store.store("hello", "world")

    redis_store.mark_as_stale("hello")

    assert redis_store.is_fresh("hello") == False
