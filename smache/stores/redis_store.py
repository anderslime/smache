import json
import time
import random
from .cache_result import CacheResult
from redis import WatchError


class RedisStore:

    def __init__(self, redis_con, **options):
        self.redis_con = redis_con
        self._store_retries = 5
        self._retry_backoff = options.get(
            'retry_backoff',
            lambda: time.sleep(random.random())
        )

    def store(self, key, value, timestamp):
        pipe = self.redis_con.pipeline()
        self._store_entry(key, value, timestamp, pipe, self._store_retries)

    def lookup(self, key):
        raw_cache_result = self._get_all(key) or {}
        return CacheResult(
            self._deserialize_json(raw_cache_result.get('value')),
            self._deserialize_bool(raw_cache_result.get('is_fresh')),
            self._deserialize_int(raw_cache_result.get('timestamp'))
        )

    def is_fresh(self, key):
        return self._get_field(key, 'is_fresh') == 'True'

    def mark_as_stale(self, key):
        self.redis_con.hset(key, 'is_fresh', 'False')

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

    def _store_entry(self, key, value, timestamp, pipe, retries):
        try:
            if retries > 0:
                pipe.watch(key)
                if self._is_old_timestamp(key, timestamp):
                    self._update_cache_entry(key, value, timestamp, pipe)
        except WatchError:
            self._retry_backoff(self._store_retries, retries - 1)
            self._store_entry(key, value, timestamp, pipe, retries - 1)

    def _is_old_timestamp(self, key, timestamp):
        current_timestamp = self._get_field(key, 'timestamp')
        return current_timestamp is None or \
            int(timestamp) > int(current_timestamp)

    def _update_cache_entry(self, key, value, timestamp, pipe):
        pipe.multi()
        pipe.hset(key, 'value', json.dumps(value))
        pipe.hset(key, 'is_fresh', True)
        pipe.hset(key, 'timestamp', timestamp)
        pipe.execute()

    def _get_all(self, key):
        return self.redis_con.hgetall(key)

    def _get_field(self, key, field):
        return self.redis_con.hget(key, field)
