from .schedulers import execute


class CachedFunctionProxy:
    def __init__(self, cache_manager, computed_repo, store, **proxy_options):
        self._cache_manager = cache_manager
        self._computed_repo = computed_repo
        self._store = store
        self._tolerate_stale = proxy_options.get('stale', True)

    def cache_function(self, fun, *args, **kwargs):
        key = self._computed_key(fun, *args, **kwargs)
        self._cache_manager.add_entity_dependencies(fun, args, key)
        self._cache_manager.add_data_source_dependencies(fun, key)
        cache_result = self._store.lookup(key)
        if self._tolerate_stale and cache_result.value:
            return cache_result.value
        else:
            return execute(self._store, key, fun, *args, **kwargs)

    def _computed_key(self, fun, *args, **kwargs):
        return self._computed_repo.computed_key(fun, *args, **kwargs)
