from .computed_function import ComputedFunction
from .dependency_graph_builder import build_dependency_graph
from .schedulers import execute


class CacheManager:

    def __init__(self, store, dep_graph, computed_repo, data_sources,
                 scheduler, function_serializer, relation_deps_repo,
                 data_source_repo, options):
        self._store = store
        self._dep_graph = dep_graph
        self._options = options
        self._function_serializer = function_serializer
        self._scheduler = scheduler
        self._computed_repo = computed_repo
        self._data_sources = data_sources
        self._relation_deps_repo = relation_deps_repo
        self._data_source_repo = {}
        self._data_source_repo = data_source_repo

    def cache_function(self, fun, *args, **kwargs):
        key = self._computed_key(fun, *args, **kwargs)
        self._add_entity_dependencies(fun, args, key)
        self._add_data_source_dependencies(fun, key)
        cache_result = self._store.lookup(key)
        if cache_result.is_fresh:
            return cache_result.value
        else:
            return execute(self._store, key, fun, *args, **kwargs)

    def add_computed(self, computed_fun):
        self._set_computed(computed_fun)

    def add_relation_deps(self, computed_fun, relation_data_source_deps):
        self._relation_deps_repo.add_all(
            relation_data_source_deps,
            computed_fun
        )

    def is_fun_fresh(self, fun, *args, **kwargs):
        key = self._computed_key(fun, *args, **kwargs)
        return self._store.is_fresh(key)

    def function_cache_value(self, fun, *args, **kwargs):
        key = self._computed_key(fun, *args, **kwargs)
        return self._store.lookup(key).value

    def dependency_graph(self):
        return build_dependency_graph(
            self._data_sources,
            self._computed_repo.computed_funs
        )

    def _computed_key(self, fun, *args, **kwargs):
        computed_fun = self._computed_repo.get(fun)
        return self._function_serializer.serialized_fun(
            computed_fun.arg_deps,
            computed_fun.fun,
            *args,
            **kwargs
        )

    def _get_computed(self, fun):
        return self._computed_repo.get(fun)

    def _set_computed(self, computed_fun):
        self._computed_repo.add(computed_fun)

    def _add_data_source_dependencies(self, fun, key):
        data_source_deps = self._computed_repo.get(fun).data_source_deps
        for data_source_dep in data_source_deps:
            self._dep_graph.add_data_source_dependency(
                data_source_dep.data_source_id,
                key
            )

    def _add_entity_dependencies(self, fun, args, key):
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

    def _on_data_source_update(self, data_source, entity):
        self._scheduler.schedule_update_handle(
            data_source.data_source_id,
            entity.id
        )
