from data_sources import DummyDataSource
from smache.dependency_graph_builder import build_dependency_graph
from smache.topological_sort import topological_sort

from collections import namedtuple as struct

class ComputedFunction:
    def __init__(self, fun, entity_deps, data_source_deps, computed_deps):
        self.fun              = fun
        self.fun_name         = fun.__name__
        self.entity_deps      = entity_deps
        self.data_source_deps = data_source_deps
        self.computed_deps    = computed_deps

    def call(self, *entity_dep_ids):
        deps_with_ids = zip(self.entity_deps, entity_dep_ids)
        args = [entity_dep.find(entity_id) for entity_dep, entity_id in deps_with_ids]
        return self.fun(*args)

class CacheManager:
    def __init__(self, store, dep_graph, options):
        self.store            = store
        self.dep_graph        = dep_graph
        self._options         = options
        self.computed_funs   = {}
        self.data_sources    = []

    def cache_function(self, fun, *args, **kwargs):
        key = self._fun_key(fun, *args, **kwargs)
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
            return wrapper
        return _computed

    def add_sources(self, *data_sources):
        for data_source in data_sources:
            self.data_sources.append(data_source)
            data_source.subscribe(self._on_data_source_update)

    def add_computed(self, fun, entity_deps, kwargs):
        data_source_deps = self._parse_deps(kwargs.get('sources', ()))
        computed_deps    = self._parse_deps(kwargs.get('computed_deps', ()))
        computed_dep_funs = [self._get_computed(computed_dep.__name__) for computed_dep in computed_deps]
        computed_fun = ComputedFunction(fun,
                                        entity_deps,
                                        data_source_deps,
                                        computed_dep_funs)
        self._set_computed(computed_fun)

    def is_fresh(self, key):
        return self.store.is_fresh(key)

    def is_fun_fresh(self, fun, *args, **kwargs):
        key = self._fun_key(fun, *args, **kwargs)
        return self.store.is_fresh(key)

    def function_cache_value(self, fun, *args, **kwargs):
        key = self._fun_key(fun, *args, **kwargs)
        return self.store.lookup(key).value

    def dependency_graph(self):
        return build_dependency_graph(self.data_sources, self.computed_funs)

    def _node_ids_in_topological_order(self):
        topologically_sorted_nodes = topological_sort(self.dependency_graph())
        return [node.id for node in topologically_sorted_nodes]

    def _get_computed(self, fun_name):
        return self.computed_funs[fun_name]

    def _set_computed(self, computed_fun):
        self.computed_funs[computed_fun.fun_name] = computed_fun


    def _add_data_source_dependencies(self, fun, key):
        data_source_deps = self.computed_funs[fun.__name__].data_source_deps
        for data_source_dep in data_source_deps:
            self.dep_graph.add_data_source_dependency(
                data_source_dep.data_source_id,
                key
            )

    def _add_entity_dependencies(self, fun, args, key):
        entity_deps = self._get_computed(fun.__name__).entity_deps
        for data_source, data_source_entity in zip(entity_deps, args):
            self.dep_graph.add_dependency(
                data_source.data_source_id,
                data_source_entity.id,
                key
            )


    def _parse_deps(self, value):
        if isinstance(value, tuple):
            return value
        else:
            return (value,)

    def _fun_key(self, fun, *args, **kwargs):
        fun_name_key = fun.__name__
        args_key = '/'.join(str(arg.id) for arg in args)
        return '/'.join([fun_name_key, args_key])

    def _decompose_fun_key(self, fun_key):
        elements = fun_key.split('/')
        fun_name = elements[0]
        arg_ids  = elements[1:]
        return fun_name, arg_ids

    def _on_data_source_update(self, data_source, entity_id):
        depending_keys = self.dep_graph.values_depending_on(data_source.data_source_id, entity_id)
        self._invalidate_keys(depending_keys)

    def _invalidate_keys(self, keys):
        if self._options.write_through:
            self._write_through_invalidation(keys)
        else:
            self._mark_invalidation(keys)

    def _mark_invalidation(self, keys):
        for key in keys:
            self.store.mark_as_stale(key)

    def _write_through_invalidation(self, keys):
        sorted_nodes = self._node_ids_in_topological_order()
        decomp_keys = [self._decompose_fun_key(key) for key in keys]
        fun_names = [fun_name for (fun_name, _) in decomp_keys]
        indexes = [sorted_nodes.index(fun_name) for fun_name in fun_names]
        sorted_keys = [key for key, _ in sorted(zip(keys, indexes), key=lambda x: x[1])]
        for key in sorted_keys:
            self._write_through_update(key)

    def _write_through_update(self, key):
        fun_name, arg_ids = self._decompose_fun_key(key)
        computed_fun = self.computed_funs[fun_name]
        computed_value = computed_fun.call(*arg_ids)
        return self.store.store(key, computed_value)
