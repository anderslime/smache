from .schedulers import execute, execute_in_app
import smache
from contextlib import contextmanager
from .smache_logging import debug


class CachedFunctionProxy:

    def __init__(self, cache_manager, computed_repo, store, **proxy_options):
        self._cache_manager = cache_manager
        self._computed_repo = computed_repo
        self._store = store
        self._tolerate_stale = proxy_options.get('stale', True)

    def cache_function(self, fun, *args, **kwargs):
        key = self._computed_key(fun, *args, **kwargs)
        with self._fetch_cached_value(key, fun, args) as cached_value:
            if cached_value is not None:
                return cached_value
            else:
                return execute(self._store, key, fun, *args, **kwargs)

    def cache_function_in_app(self, fun, *args, **kwargs):
        key = self._computed_key(fun, *args, **kwargs)
        with self._fetch_cached_value(key, fun, args) as cached_value:
            if cached_value is not None:
                return cached_value
            else:
                return execute_in_app(
                    smache._instance.flask_app(),
                    self._store,
                    key,
                    fun,
                    *args,
                    **kwargs
                )

    @contextmanager
    def _fetch_cached_value(self, key, fun, args):
        self._cache_manager.add_computed_instance(fun, args, key)
        cache_result = self._store.lookup(key)
        is_fresh = self._store.is_fresh(key)
        if is_fresh or self._tolerate_stale and cache_result.value is not None:
            debug("HIT {}".format(fun.__name__))
            self._schedule_update_if_needed(cache_result, key, fun, is_fresh)
            yield cache_result.value
        else:
            debug("MISS {}".format(fun.__name__))
            yield None

    def _schedule_update_if_needed(self, cache_result, key, fun, is_fresh):
        computed_fun = self._computed_repo.get(fun)
        if not is_fresh:
            debug("{} is STALE - scheduling update".format(fun.__name__))
            smache._instance._scheduler.schedule_write_through([key])
        elif cache_result.needs_refresh(computed_fun.ttl):
            debug("{} has EXPIRED - scheduling update".format(fun.__name__))
            self._store.mark_as_stale(key)
            smache._instance._scheduler.schedule_write_through([key])

    def _return_cached_value(self, cache_result, key):
        return self._tolerate_stale and cache_result.value \
            or self._store.is_fresh(key)

    def _computed_key(self, fun, *args, **kwargs):
        return self._computed_repo.computed_key(fun, *args, **kwargs)
