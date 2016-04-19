import json
import time
import random
from .cache_result import CacheResult
from redis import WatchError


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
        self._store_entry(
            key,
            value,
            state_timestamp,
            pipe,
            self._store_retries
        )

    def lookup(self, key):
        raw_cache_result = self._get_all(key) or {}
        return CacheResult(
            self._deserialize_json(raw_cache_result.get('value')),
            self._deserialize_bool(raw_cache_result.get('is_fresh')),
            self._deserialize_int(raw_cache_result.get('timestamp'))
        )

    def is_fresh(self, key):
        return self._timestamp_registry.is_timestamps_syncronized(key)

    def mark_as_stale(self, key):
        self._timestamp_registry.increment_state_timestamp(key)

    def _deserialize_bool(self, boolean):
        return boolean == 'True'

    def _deserialize_int(self, integer):
        if integer is None:
            return None
        return int(integer)

    def _deserialize_json(self, value):
        if value is None:
            return None
        return json.loads(value)

    def _store_entry(self, key, value, state_timestamp, pipe, retries):
        try:
            if retries > 0:
                ts_key = self._timestamp_registry.value_ts_key(key)
                pipe.watch(key, ts_key)
                if self._is_newest_value(key, state_timestamp):
                    self._update_cache_entry(key, value, state_timestamp, pipe)
        except WatchError:
            self._retry_backoff()
            self._store_entry(key, value, state_timestamp, pipe, retries - 1)

    def _is_newest_value(self, key, state_timestamp):
        return self._timestamp_registry.is_newer_value_timestamp(
            key,
            state_timestamp
        )

    def _update_cache_entry(self, key, value, state_timestamp, pipe):
        pipe.multi()
        pipe.hset(key, 'value', json.dumps(value))
        self._timestamp_registry.set_value_timestamp(pipe, key, state_timestamp)
        pipe.execute()

    def _get_all(self, key):
        return self.redis_con.hgetall(key)

    def _get_field(self, key, field):
        return self.redis_con.hget(key, field)
