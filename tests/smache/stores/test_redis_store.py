import redis
import json
import pytest

from smache.stores.redis_store import RedisStore
from smache.timestamp_registry import TimestampRegistry

redis_con = redis.StrictRedis(host='localhost', port=6379, db=0)


@pytest.yield_fixture(autouse=True)
def flush_before_each_test_case():
    redis_con.flushall()
    yield


@pytest.yield_fixture
def redis_store():
    yield RedisStore(redis_con, TimestampRegistry(redis_con))


def test_stored_elements_can_be_looked_up(redis_store):
    redis_store.store("hello", "world", 0)

    stored_element = redis_store.lookup("hello")

    assert stored_element.value == "world"


def test_newly_stored_elements_are_fresh(redis_store):
    redis_store.store("hello", "world", 0)

    assert redis_store.is_fresh("hello") == True


def test_key_marked_as_stale_is_not_fresh(redis_store):
    redis_store.store("hello", "world", 0)

    assert redis_store.is_fresh("hello") == True

    redis_store.mark_as_stale("hello")

    assert redis_store.is_fresh("hello") == False


def test_value_is_only_written_when_newer_then_current(redis_store):
    registry = TimestampRegistry(redis_con)
    redis_store = RedisStore(redis_con, registry)

    redis_store.store("hello", "world", 0)

    assert redis_store.lookup("hello").value == "world"

    registry.increment_state_timestamp("hello")

    redis_store.store("hello", "new_world", 0)

    assert redis_store.lookup("hello").value == "world"

    redis_store.store("hello", "new_world", 1)

    assert redis_store.lookup("hello").value == "new_world"


# This test is really NOT a good practice. It tests "private methods"
# But it tests that we retry transactions and
def test_retry_method_works_with_cache_overwrite(monkeypatch):
    redis_store = RedisStore(
        redis_con,
        TimestampRegistry(redis_con),
        retry_backoff=lambda: 0
    )
    global retries
    retries = 0

    def test_cache_update(cache_entry, pipe):
        global retries
        retries += 1
        redis_con.hset(cache_entry.key, "random_key", "random_value")

        pipe.multi()
        pipe.hset(cache_entry.key, "value", json.dumps(cache_entry.value))
        pipe.execute()

    monkeypatch.setattr(redis_store, '_update_cache_entry', test_cache_update)
    redis_store.store("hello", "world", 0)

    assert redis_store.lookup("hello").value is None
    assert retries == 5


def test_retry_method_works_with_timestamp_overwrite(monkeypatch):
    ts_registry = TimestampRegistry(redis_con)
    redis_store = RedisStore(redis_con, ts_registry, retry_backoff=lambda: 0)
    global retries
    retries = 0

    def test_cache_update(cache_entry, pipe):
        global retries
        retries += 1
        ts_key = ts_registry.value_ts_key(cache_entry.key)
        redis_con.set(ts_key, -500)

        pipe.multi()
        pipe.set(ts_key, 5)
        pipe.execute()

    monkeypatch.setattr(redis_store, '_update_cache_entry', test_cache_update)
    redis_store.store("hello", "world", 0)

    assert redis_store.lookup("hello").value is None
    assert retries == 5
