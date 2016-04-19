from .computed_function import ComputedFunction
import smache


class DSL:
    def __init__(self, data_source_repo, cache_manager, function_proxy,
                 computed_repo):
        self._data_source_repo = data_source_repo
        self._cache_manager = cache_manager
        self._computed_repo = computed_repo
        self._function_proxy = function_proxy
        self.cache_function = self._function_proxy.cache_function

    def computed(self, *deps, **kwargs):
        def _computed(fun):
            def wrapper(*args, **kwargs):
                proxy = smache._instance._cached_function_proxy
                return proxy.cache_function(fun, *args, **kwargs)
            self._add_computed(fun, deps, kwargs)
            wrapper.__name__ = fun.__name__
            wrapper.__module__ = fun.__module__
            return wrapper
        return _computed

    def relations(self, *relation_deps):
        def _relations(fun):
            self._add_relations(fun, *relation_deps)
            return fun
        return _relations

    def sources(self, *sources):
        def _sources(fun):
            self._add_sources(fun, *sources)
            return fun
        return _sources

    def _add_relations(self, fun, *relation_deps):
        computed_fun = self._get_computed(fun)
        relation_data_source_deps = self._relation_data_sources(relation_deps)
        self._cache_manager.add_relation_deps(
            computed_fun,
            relation_data_source_deps
        )

    def _add_sources(self, fun, *sources):
        entity_class_deps = self._parse_deps(sources)
        data_source_deps = [self._find_or_register_data_source(entity_class)
                            for entity_class in entity_class_deps]
        computed_fun = self._get_computed(fun)
        computed_fun.set_data_source_deps(data_source_deps)

    def _add_computed(self, fun, arg_entity_class_deps, kwargs):
        computed_deps = self._parse_deps(kwargs.get('computed_deps', ()))
        computed_dep_funs = [self._get_computed(computed_dep)
                             for computed_dep in computed_deps]
        arg_deps = [self._find_or_register_data_source(entity_class)
                    for entity_class in arg_entity_class_deps]
        computed_fun = ComputedFunction(fun, arg_deps, computed_dep_funs)
        self._cache_manager.add_computed(computed_fun)

    def _relation_data_sources(self, relation_deps):
        return [(self._find_or_register_data_source(entity_class), rel_fun)
                for (entity_class, rel_fun) in self._parse_deps(relation_deps)]

    def _find_or_register_data_source(self, entity_class):
        return self._data_source_repo.find_or_register_data_source(
            entity_class,
            self._cache_manager.on_data_source_update
        )

    def _get_computed(self, fun):
        return self._computed_repo.get(fun)

    def _parse_deps(self, value):
        if isinstance(value, tuple):
            return value
        else:
            return (value,)
