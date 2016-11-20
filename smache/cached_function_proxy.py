from .schedulers import execute, execute_in_app


class CachedFunctionProxy:
    def __init__(self, cache_manager, computed_repo, store, **proxy_options):
        self._cache_manager = cache_manager
        self._computed_repo = computed_repo
        self._store = store
        self._tolerate_stale = proxy_options.get('stale', True)

    def cache_function(self, fun, *args, **kwargs):
        key = self._computed_key(fun, *args, **kwargs)
        self._cache_manager.add_computed_instance(fun, args, key)
        cache_result = self._store.lookup(key)
        if self._return_cached_value(cache_result, key):
            return cache_result.value
        else:
            return execute(self._store, key, fun, *args, **kwargs)

    def cache_function_in_app(self, app, fun, *args, **kwargs):
        key = self._computed_key(fun, *args, **kwargs)
        self._cache_manager.add_computed_instance(fun, args, key)
        cache_result = self._store.lookup(key)
        if self._return_cached_value(cache_result, key):
            return cache_result.value
        else:
            return execute_in_app(app, self._store, key, fun, *args, **kwargs)

    def _return_cached_value(self, cache_result, key):
        return self._tolerate_stale and cache_result.value \
            or self._store.is_fresh(key)

    def _computed_key(self, fun, *args, **kwargs):
        return self._computed_repo.computed_key(fun, *args, **kwargs)
