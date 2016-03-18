import json
from .cache_result import CacheResult

class RedisStore:
    def __init__(self, redis_con):
        self.redis_con = redis_con

    def store(self, key, value):
        self._store_entry(key, value, 'True')

    def lookup(self, key):
        raw_cache_result = self._get_all(key) or {}
        return CacheResult(
            self._deserialize_json(raw_cache_result.get('value')),
            self._deserialize_bool(raw_cache_result.get('is_fresh'))
        )

    def is_fresh(self, key):
        return self._get_field(key, 'is_fresh') == 'True'

    def mark_as_stale(self, key):
        self.redis_con.hset(key, 'is_fresh', 'False')

    def _deserialize_bool(self, boolean):
        return boolean == 'True'

    def _deserialize_json(self, value):
        if value is None:
            return None
        return json.loads(value)

    def _store_entry(self, key, value, is_fresh):
        pipe = self.redis_con.pipeline()
        pipe.hset(key, 'value', json.dumps(value))
        pipe.hset(key, 'is_fresh', is_fresh)
        pipe.execute()

    def _get_all(self, key):
        return self.redis_con.hgetall(key)

    def _get_field(self, key, field):
        return self.redis_con.hget(key, field)
