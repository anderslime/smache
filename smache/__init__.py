import redis

from stores import RedisStore
from dependency_graph import RedisDependencyGraph
from cache_manager import CacheManager


class Smache:
    def __init__(self, **kwargs):
        self._options = Options(**kwargs)

        redis_con = redis.StrictRedis(host='localhost', port=6379, db=0)

        store     = RedisStore(redis_con)
        dep_graph = RedisDependencyGraph(redis_con)

        self._cache_manager = CacheManager(store, dep_graph, self._options)

        # Delegates
        self.cache_function = self._cache_manager.cache_function
        self.computed = self._cache_manager.computed
        self.add_sources = self._cache_manager.add_sources

        self.is_fun_fresh = self._cache_manager.is_fun_fresh

class Options:
    defaults = {
        'write_through': False
    }

    def __init__(self, **options):
        self.options = self.defaults.update(options)

        self.write_through = self._value_equal(options, 'write_through', True)

    def _value_equal(self, options, prop, test_value):
        return prop in options and options[prop] == test_value

