from .computed_function import ComputedFunction
from .schedulers import execute
from .cached_function_proxy import CachedFunctionProxy


class CacheManager:

    def __init__(self, store, dep_graph, computed_repo, scheduler,
                 relation_deps_repo):
        self._store = store
        self._dep_graph = dep_graph
        self._scheduler = scheduler
        self._computed_repo = computed_repo
        self._relation_deps_repo = relation_deps_repo

    def cache_function(self, fun, *args, **kwargs):
        return CachedFunctionProxy(
            self,
            self._computed_repo,
            self._store
        ).cache_function(fun, *args, **kwargs)

    def add_computed(self, computed_fun):
        self._set_computed(computed_fun)

    def add_relation_deps(self, computed_fun, relation_data_source_deps):
        self._relation_deps_repo.add_all(
            relation_data_source_deps,
            computed_fun
        )

    def add_data_source_dependencies(self, fun, key):
        data_source_deps = self._computed_repo.get(fun).data_source_deps
        for data_source_dep in data_source_deps:
            self._dep_graph.add_data_source_dependency(
                data_source_dep.data_source_id,
                key
            )

    def add_entity_dependencies(self, fun, args, key):
        arg_deps = self._get_computed(fun).arg_deps
        for data_source, data_source_entity in zip(arg_deps, args):
            self._dep_graph.add_dependency(
                data_source.data_source_id,
                data_source.serialize(data_source_entity),
                key
            )
            self._dep_graph.add_fun_dependency(
                data_source.data_source_id,
                data_source.serialize(data_source_entity),
                ComputedFunction.id_from_fun(fun),
                key
            )

    def on_data_source_update(self, data_source, entity):
        self._scheduler.schedule_update_handle(
            data_source.data_source_id,
            entity.id
        )

    def _computed_key(self, fun, *args, **kwargs):
        return self._computed_repo.computed_key(fun, *args, **kwargs)

    def _get_computed(self, fun):
        return self._computed_repo.get(fun)

    def _set_computed(self, computed_fun):
        self._computed_repo.add(computed_fun)
