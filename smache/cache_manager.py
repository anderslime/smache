from data_sources import DummyDataSource
from computed_function import ComputedFunction
from dependency_graph_builder import build_dependency_graph
from topological_sort import topological_sort
from computed_function_repository import ComputedFunctionRepository
from relation_dependency_repository import RelationDependencyRepository

from collections import namedtuple as struct
from smache.smache_logging import logger

class CacheManager:
    def __init__(self, store, dep_graph, computed_repo, scheduler, function_serializer, options):
        self.store                = store
        self.dep_graph            = dep_graph
        self._options             = options
        self._scheduler           = scheduler
        self._function_serializer = function_serializer
        self.computed_repo        = computed_repo
        self.data_sources         = []
        self._relation_deps_repo  = RelationDependencyRepository()

    def cache_function(self, fun, *args, **kwargs):
        key = self._computed_key(fun, *args, **kwargs)
        self._add_entity_dependencies(fun, args, key)
        self._add_data_source_dependencies(fun, key)
        cache_result = self.store.lookup(key)
        if cache_result.is_fresh:
            return cache_result.value
        else:
            computed_value = fun(*args)
            self.store.store(key, computed_value)
            return computed_value

    def computed(self, *deps, **kwargs):
        def _computed(fun):
            def wrapper(*args, **kwargs):
                return self.cache_function(fun, *args, **kwargs)
            self.add_computed(fun, deps, kwargs)
            wrapper.__name__ = fun.__name__
            wrapper.__module__ = fun.__module__
            return wrapper
        return _computed

    def add_sources(self, *data_sources):
        for data_source in data_sources:
            self.data_sources.append(data_source)
            data_source.subscribe(self._on_data_source_update)

    def add_computed(self, fun, arg_deps, kwargs):
        data_source_deps = self._parse_deps(kwargs.get('sources', ()))
        computed_deps    = self._parse_deps(kwargs.get('computed_deps', ()))
        relation_deps    = kwargs.get('relations', ())
        computed_dep_funs = [self._get_computed(computed_dep) for computed_dep in computed_deps]
        computed_fun = ComputedFunction(fun,
                                        arg_deps,
                                        data_source_deps,
                                        computed_dep_funs)
        self._relation_deps_repo.add_all(relation_deps, computed_fun)
        self._set_computed(computed_fun)

    def is_fresh(self, key):
        return self.store.is_fresh(key)

    def is_fun_fresh(self, fun, *args, **kwargs):
        key = self._computed_key(fun, *args, **kwargs)
        return self.store.is_fresh(key)

    def function_cache_value(self, fun, *args, **kwargs):
        key = self._computed_key(fun, *args, **kwargs)
        return self.store.lookup(key).value

    def dependency_graph(self):
        return build_dependency_graph(
            self.data_sources,
            self.computed_repo.computed_funs
        )

    def _computed_key(self, fun, *args, **kwargs):
        computed_fun = self.computed_repo.get(fun)
        return self._fun_key(
            computed_fun.arg_deps,
            computed_fun.fun,
            *args,
            **kwargs
        )

    def _node_ids_in_topological_order(self):
        topologically_sorted_nodes = topological_sort(self.dependency_graph())
        return [node.id for node in topologically_sorted_nodes]

    def _get_computed(self, fun):
        return self.computed_repo.get(fun)

    def _set_computed(self, computed_fun):
        self.computed_repo.add(computed_fun)

    def _add_data_source_dependencies(self, fun, key):
        data_source_deps = self.computed_repo.get(fun).data_source_deps
        for data_source_dep in data_source_deps:
            self.dep_graph.add_data_source_dependency(
                data_source_dep.data_source_id,
                key
            )

    def _add_entity_dependencies(self, fun, args, key):
        arg_deps = self._get_computed(fun).arg_deps
        for data_source, data_source_entity in zip(arg_deps, args):
            self.dep_graph.add_dependency(
                data_source.data_source_id,
                data_source.serialize(data_source_entity),
                key
            )
            self.dep_graph.add_fun_dependency(
                data_source.data_source_id,
                data_source.serialize(data_source_entity),
                ComputedFunction.id_from_fun(fun),
                key
            )

    def _parse_deps(self, value):
        if isinstance(value, tuple):
            return value
        else:
            return (value,)

    def _on_data_source_update(self, data_source, entity):
        depending_keys = self.dep_graph.values_depending_on(data_source.data_source_id, entity.id)
        depending_relation_keys = self._depending_relation_keys(data_source, entity)
        self._invalidate_keys(depending_keys | depending_relation_keys)

    def _depending_relation_keys(self, data_source, entity):
        depending_relations = self._relation_deps_repo.get(data_source.data_source_id)
        depending_relation_keys = [self._rel_keys(relation_fun, entity, computed_fun) for relation_fun, computed_fun in depending_relations]
        return self._flattened_sets(depending_relation_keys)

    def _rel_keys(self, relation_fun, entity, computed_fun):
        computed_sources = relation_fun(entity)
        rel_keys = [self._fun_values_depending_on(computed_source, computed_fun)
                    for computed_source in self._list(computed_sources)]
        return self._flattened_sets(rel_keys)

    def _flattened_sets(self, depending_relation_keys):
        return reduce(lambda x, y: x | y, depending_relation_keys, set())

    def _fun_values_depending_on(self, computed_source, computed_fun):
        data_source = next(source for source in self.data_sources if source.for_entity(computed_source))
        return self.dep_graph.fun_values_depending_on(
            data_source.data_source_id,
            computed_source.id,
            computed_fun.id
        )

    def _list(self, value):
        if isinstance(value, list):
            return value
        else:
            return [value]

    def _invalidate_keys(self, keys):
        self._mark_invalidation(keys)
        if self._options.write_through:
            self._write_through_invalidation(keys)

    def _mark_invalidation(self, keys):
        for key in keys:
            self.store.mark_as_stale(key)

    def _write_through_invalidation(self, keys):
        sorted_nodes = self._node_ids_in_topological_order()
        fun_names = [self._fun_name_from_key(key) for key in keys]
        indexes = [sorted_nodes.index(fun_name) for fun_name in fun_names]
        sorted_keys = [key for key, _ in sorted(zip(keys, indexes), key=lambda x: x[1])]
        self._scheduler.schedule_write_through(sorted_keys)

    def _fun_key(self, fun, *args, **kwargs):
        return self._function_serializer.serialized_fun(fun, *args, **kwargs)

    def _fun_name_from_key(self, fun_key):
        return self._function_serializer.fun_name(fun_key)
