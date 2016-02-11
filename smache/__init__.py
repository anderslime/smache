import redis

from stores import RedisStore
from dependency_graph import RedisDependencyGraph
from cache_manager import CacheManager


class Smache:
    def __init__(self):
        redis_con = redis.StrictRedis(host='localhost', port=6379, db=0)

        store     = RedisStore(redis_con)
        dep_graph = RedisDependencyGraph(redis_con)

        self._cache_manager = CacheManager(store, dep_graph)

        # Delegates
        self.cache_function = self._cache_manager.cache_function
        self.computed = self._cache_manager.computed
        self.data_source = self._cache_manager.data_source
        self.add_sources = self._cache_manager.add_sources

        self.is_fun_fresh = self._cache_manager.is_fun_fresh
