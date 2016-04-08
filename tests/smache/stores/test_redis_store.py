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
    redis_store.store("hello", "world", 0)

    stored_element = redis_store.lookup("hello")

    assert stored_element.value == "world"


def test_newly_stored_elements_are_fresh():
    redis_store = RedisStore(redis_con)
    redis_store.store("hello", "world", 0)

    assert redis_store.is_fresh("hello") == True


def test_key_marked_as_stale_is_not_fresh():
    redis_store = RedisStore(redis_con)
    redis_store.store("hello", "world", 0)

    redis_store.mark_as_stale("hello")

    assert redis_store.is_fresh("hello") == False


def test_timestamp_is_set():
    redis_store = RedisStore(redis_con)
    redis_store.store("hello", "world", 60)

    assert redis_store.lookup("hello").timestamp == 60


def test_value_is_only_written_when_newer_then_current():
    redis_store = RedisStore(redis_con)
    redis_store.store("hello", "world", 5)

    redis_store.store("hello", "old_world", 3)
    redis_store.store("hello", "old_world", 0)
    redis_store.store("hello", "old_world", 4)

    assert redis_store.lookup("hello").value == "world"

    redis_store.store("hello", "new_world", 6)

    assert redis_store.lookup("hello").value == "new_world"


# This test is really NOT a bad practice. It tests "private methods"
# But it tests that we retry transactions and
def test_retry_method_works(monkeypatch):
    import json
    redis_store = RedisStore(redis_con, retry_backoff=lambda: 0)
    global retries
    retries = 0

    def test_cache_update(key, value, timestamp, pipe):
        global retries
        retries += 1
        redis_con.hset(key, "random_key", "random_value")

        pipe.multi()
        pipe.hset(key, "value", json.dumps(value))
        pipe.execute()

    monkeypatch.setattr(redis_store, '_update_cache_entry', test_cache_update)
    redis_store.store("hello", "world", 0)

    assert redis_store.lookup("hello").value is None
    assert retries == 5
