from smache.graph_drawer import draw_graph

from stores import RedisStore
from dependency_graphs import RedisDependencyGraph
from cache_manager import CacheManager
from computed_function_repository import ComputedFunctionRepository
from relation_dependency_repository import RelationDependencyRepository
from function_serializer import FunctionSerializer

from options import Options

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



def reset_globals():
    global _computed_repo, _relation_deps_repo, data_sources
    _computed_repo      = ComputedFunctionRepository()
    _relation_deps_repo = RelationDependencyRepository()
