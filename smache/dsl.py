from .computed_function import ComputedFunction


class DSL:
    def __init__(self, data_source_repo, cache_manager):
        self._data_source_repo = data_source_repo
        self._cache_manager = cache_manager
        self.cache_function = self._cache_manager.cache_function

    def computed(self, *deps, **kwargs):
        def _computed(fun):
            def wrapper(*args, **kwargs):
                return self.cache_function(fun, *args, **kwargs)
            self.add_computed(fun, deps, kwargs)
            wrapper.__name__ = fun.__name__
            wrapper.__module__ = fun.__module__
            return wrapper
        return _computed

    def add_computed(self, fun, arg_entity_class_deps, kwargs):
        entity_class_deps = self._parse_deps(kwargs.get('sources', ()))
        computed_deps = self._parse_deps(kwargs.get('computed_deps', ()))
        relation_deps = kwargs.get('relations', ())
        computed_dep_funs = [self._cache_manager._get_computed(computed_dep)
                             for computed_dep in computed_deps]
        arg_deps = [self._find_or_register_data_source(entity_class)
                    for entity_class in arg_entity_class_deps]
        data_source_deps = [self._find_or_register_data_source(entity_class)
                            for entity_class in entity_class_deps]
        relation_data_source_deps = self._relation_data_sources(relation_deps)
        computed_fun = ComputedFunction(fun,
                                        arg_deps,
                                        data_source_deps,
                                        computed_dep_funs)
        self._cache_manager.add_relation_deps(
            computed_fun,
            relation_data_source_deps
        )
        self._cache_manager.add_computed(computed_fun,)

    def _relation_data_sources(self, relation_deps):
        return [(self._find_or_register_data_source(entity_class), rel_fun)
                for (entity_class, rel_fun) in relation_deps]

    def _find_or_register_data_source(self, entity_class):
        return self._data_source_repo.find_or_register_data_source(
            entity_class,
            self._cache_manager._on_data_source_update
        )

    def _parse_deps(self, value):
        if isinstance(value, tuple):
            return value
        else:
            return (value,)