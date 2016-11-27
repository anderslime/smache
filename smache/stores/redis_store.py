import time
import random
from .cache_result import CacheResult
from redis import WatchError
import pickle
from collections import namedtuple

CacheEntry = namedtuple('CacheEntry', ['key', 'value', 'state_timestamp'])


class RedisStore:

    def __init__(self, redis_con, timestamp_registry, **options):
        self.redis_con = redis_con
        self._timestamp_registry = timestamp_registry
        self._store_retries = 5
        self._retry_backoff = options.get(
            'retry_backoff',
            lambda: time.sleep(random.random())
        )

    def store(self, key, value, state_timestamp):
        pipe = self.redis_con.pipeline()
        cache_entry = CacheEntry(key, value, state_timestamp)
        self._store_entry(cache_entry, pipe, self._store_retries)

    def lookup(self, key):
        raw_cache_result = self._get_all(key) or {}
        return CacheResult(
            self._deserialize_value(raw_cache_result.get('value')),
            self._deserialize_value(raw_cache_result.get('updated_at'))
        )

    def is_fresh(self, key):
        return self._timestamp_registry.is_timestamps_syncronized(key)

    def mark_as_stale(self, key):
        self._timestamp_registry.increment_state_timestamp(key)

    def mark_all_as_stale(self, namespace):
        pipe = self.redis_con.pipeline()
        pipe.multi()
        keys = self.redis_con.keys("{}*".format(namespace))
        for key in keys:
            self._timestamp_registry.increment_state_timestamp(key, pipe)
        pipe.execute()

    def _deserialize_value(self, value):
        if value is None:
            return None
        return pickle.loads(value)

    def _store_entry(self, cache_entry, pipe, retries):
        try:
            if retries > 0:
                ts_key = self._timestamp_registry.value_ts_key(cache_entry.key)
                pipe.watch(cache_entry.key, ts_key)
                if self._is_newest_value(cache_entry):
                    self._update_cache_entry(cache_entry, pipe)
        except WatchError:
            self._retry_backoff()
            self._store_entry(cache_entry, pipe, retries - 1)

    def _is_newest_value(self, cache_entry):
        return self._timestamp_registry.is_newer_value_timestamp(
            cache_entry.key,
            cache_entry.state_timestamp
        )

    def _update_cache_entry(self, cache_entry, pipe):
        pipe.multi()
        pipe.hset(cache_entry.key, 'value', pickle.dumps(cache_entry.value))
        pipe.hset(cache_entry.key, 'updated_at', pickle.dumps(time.time()))
        self._timestamp_registry.set_value_timestamp(
            pipe,
            cache_entry.key,
            cache_entry.state_timestamp
        )
        pipe.execute()

    def _get_all(self, key):
        return self.redis_con.hgetall(key)
