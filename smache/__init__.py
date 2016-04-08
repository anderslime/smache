from .graph_drawer import draw_graph
from .stores import RedisStore
from .dependency_graphs import RedisDependencyGraph
from .cache_manager import CacheManager
from .computed_function_repository import ComputedFunctionRepository
from .relation_dependency_repository import RelationDependencyRepository
from .function_serializer import FunctionSerializer
from .options import Options
from .smache_logging import setup_logger
from .timestamp_registry import TimestampRegistry
from .data_update_propagator import DataUpdatePropagator
from .data_sources.raw_data_source import Raw  # NOQA

global _instance


class Smache:

    def __init__(self, **kwargs):
        self._options = Options(**kwargs)

        redis_con = self._options.redis_con

        self._computed_repo = ComputedFunctionRepository()
        self._relation_deps_repo = RelationDependencyRepository()
        self._dependency_graph = RedisDependencyGraph(redis_con)
        self._scheduler = self._options.scheduler
        self._timestamp_registry = TimestampRegistry(redis_con)
        self._data_sources = []
        store = RedisStore(redis_con)
        function_serializer = FunctionSerializer()
        self._data_update_propagator = \
            DataUpdatePropagator(function_serializer, store)

        self._cache_manager = CacheManager(store,
                                           self._dependency_graph,
                                           self._computed_repo,
                                           self._data_sources,
                                           self._scheduler,
                                           function_serializer,
                                           self._relation_deps_repo,
                                           self._options)

        # Delegates
        self.cache_function = self._cache_manager.cache_function
        self.computed = self._cache_manager.computed

        self.is_fun_fresh = self._cache_manager.is_fun_fresh

        setup_logger(self._options)

        self._set_globals()

    def draw(self, filename='graph'):
        draw_graph(self._build_dependency_graph().values(), filename)

    def _set_globals(self):
        global _instance
        _instance = self

    def _build_dependency_graph(self):
        return self._cache_manager.dependency_graph()

    def _use_or_default(self, value, default_lambda):
        if value is not None:
            return value
        else:
            return default_lambda()

    def __repr__(self):
        return "<Smache deps={}>".format(
            str(self._cache_manager.dependency_graph().values()))
