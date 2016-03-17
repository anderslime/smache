import redis
from rq import Queue
from smache.graph_drawer import draw_graph

from stores import RedisStore
from dependency_graphs import RedisDependencyGraph
from cache_manager import CacheManager
from computed_function_repository import ComputedFunctionRepository
from relation_dependency_repository import RelationDependencyRepository
from function_serializer import FunctionSerializer
from data_sources import MongoDataSource

from schedulers import AsyncScheduler, InProcessScheduler

from smache_logging import logger
import logging, sys

global _computed_repo, _relation_deps_repo, _dependency_graph, _options, _scheduler, _data_sources

class Smache:
    def __init__(self, **kwargs):
        self._options = Options(**kwargs)

        redis_con = self._options.redis_con
        worker_queue = self._options.worker_queue

        self._computed_repo      = ComputedFunctionRepository()
        self._relation_deps_repo = RelationDependencyRepository()
        self._dependency_graph   = RedisDependencyGraph(redis_con)
        self._scheduler          = self._options.scheduler
        self.data_sources        = []
        store                    = RedisStore(redis_con)
        function_serializer      = FunctionSerializer()

        self._cache_manager = CacheManager(store,
                                           self._dependency_graph,
                                           self._computed_repo,
                                           self.data_sources,
                                           self._scheduler,
                                           function_serializer,
                                           self._relation_deps_repo,
                                           self._options)

        # Delegates
        self.cache_function = self._cache_manager.cache_function
        self.computed = self._cache_manager.computed
        self.add_sources = self._cache_manager.add_sources

        self.is_fun_fresh = self._cache_manager.is_fun_fresh

        self.set_globals()

        if self._options.debug:
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(logging.DEBUG)

            logger.addHandler(handler)
            logger.setLevel(logging.DEBUG)

    def set_globals(self):
        global _computed_repo, _relation_deps_repo, _dependency_graph, _options, _scheduler, _data_sources
        _computed_repo      = self._computed_repo
        _relation_deps_repo = self._relation_deps_repo
        _dependency_graph   = self._dependency_graph
        _options            = self._options
        _scheduler          = self._scheduler
        _data_sources       = self.data_sources

    def log(self, something):
        logger.debug("LOGGING FROM SMACHE: {}".format(something))

    def draw(self, filename='graph'):
        draw_graph(self._build_dependency_graph().values(), filename)

    def _build_dependency_graph(self):
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
        'write_through': False,
        'debug': False
    }

    def __init__(self, **options):
        self.options = self.defaults.update(options)

        self.write_through = self._value_equal(options, 'write_through', True)
        self.debug         = self._value_equal(options, 'debug', True)
        self.redis_con     = self._redis_con(options)
        self.worker_queue  = self._worker_queue(options, self.redis_con)
        self.scheduler     = self._scheduler(options, self.worker_queue)

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

    def _scheduler(self, options, worker_queue):
        return self._use_or_default(
            options.get('scheduler'),
            lambda: AsyncScheduler(worker_queue)
        )


    def _use_or_default(self, value, default_lambda):
        if value != None:
            return value
        else:
            return default_lambda()

    def _value_equal(self, options, prop, test_value):
        return prop in options and options[prop] == test_value

def reset_globals():
    global _computed_repo, _relation_deps_repo, data_sources
    _computed_repo      = ComputedFunctionRepository()
    _relation_deps_repo = RelationDependencyRepository()
