import redis
from rq import Queue
from smache.graph_drawer import draw_graph

from stores import RedisStore
from dependency_graphs import RedisDependencyGraph
from cache_manager import CacheManager
from computed_function_repository import ComputedFunctionRepository
from function_serializer import FunctionSerializer
from data_sources import MongoDataSource

from schedulers import AsyncScheduler, InProcessScheduler

global computed_repo
computed_repo = ComputedFunctionRepository()

class Smache:
    def __init__(self, **kwargs):
        self._options = Options(**kwargs)

        redis_con = self._options.redis_con
        worker_queue = self._options.worker_queue

        global computed_repo
        computed_repo       = ComputedFunctionRepository()
        store               = RedisStore(redis_con)
        dep_graph           = RedisDependencyGraph(redis_con)
        function_serializer = FunctionSerializer()
        scheduler           = AsyncScheduler(worker_queue)

        self._cache_manager = CacheManager(store,
                                           dep_graph,
                                           computed_repo,
                                           scheduler,
                                           function_serializer,
                                           self._options)

        # Delegates
        self.cache_function = self._cache_manager.cache_function
        self.computed = self._cache_manager.computed
        self.add_sources = self._cache_manager.add_sources

        self.is_fun_fresh = self._cache_manager.is_fun_fresh

    def draw(self, filename='graph'):
        draw_graph(self._dependency_graph().values(), filename)

    def _dependency_graph(self):
        return self._cache_manager.dependency_graph()

    def _use_or_default(self, value, default_lambda):
        if value != None:
            return value
        else:
            return default_lambda()

    def __repr__(self):
        return "<Smache deps={}>".format(str(self._dependency_graph().values()))


class Options:
    defaults = {
        'write_through': False
    }

    def __init__(self, **options):
        self.options = self.defaults.update(options)

        self.write_through = self._value_equal(options, 'write_through', True)
        self.redis_con     = self._redis_con(options)
        self.worker_queue  = self._worker_queue(options, self.redis_con)

    def _worker_queue(self, options, redis_con):
        return self._use_or_default(
            options.get('worker_queue'),
            lambda: Queue('smache', connection=redis_con)
        )

    def _redis_con(self, options):
        return self._use_or_default(
            options.get('redis_con'),
            lambda: redis.StrictRedis(host='localhost', port=6379, db=0)
        )

    def _use_or_default(self, value, default_lambda):
        if value != None:
            return value
        else:
            return default_lambda()

    def _value_equal(self, options, prop, test_value):
        return prop in options and options[prop] == test_value

