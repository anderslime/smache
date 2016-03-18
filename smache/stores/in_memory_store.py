from .cache_result import CacheResult

class InMemoryStore:
    def __init__(self):
        self._data = {}

    def store(self, key, value):
        self._data[key] = {'is_fresh': True, 'value': value}

    def lookup(self, key):
        raw_cache_result = self._data.get(key, {})
        return CacheResult(
            raw_cache_result.get('value', None),
            raw_cache_result.get('is_fresh', False)
        )

    def is_fresh(self, key):
        return self._data.get(key, {}).get('is_fresh', None)

    def mark_as_stale(self, key):
        old_value = self._data.get(key, None)
        if old_value is not None:
            old_value['is_fresh'] = False
            self._data[key] = old_value

