import smache

from .dependency_graph_builder import build_dependency_graph
from .smache_logging import debug
from functools import reduce
from .data_sources.mongo_data_source import MongoDataSource


class DataUpdatePropagator:

    def __init__(self, function_serializer, store):
        self._function_serializer = function_serializer
        self._store = store

    def handle_update(self, data_source_id, entity_id):
        data_source = self._find_data_source(data_source_id)
        entity = data_source.find(entity_id)
        depending_keys = self._smache_dependency_graph.values_depending_on(
            data_source_id,
            entity_id
        )
        debug("depending keys={}".format(depending_keys))
        depending_relation_keys = self._depending_relation_keys(
            data_source,
            entity
        )
        debug("depending relation keys={}".format(depending_relation_keys))
        self._invalidate_keys(depending_keys | depending_relation_keys)

    def _depending_relation_keys(self, data_source, entity):
        data_source_id = data_source.data_source_id
        depending_relations = self._relation_deps_repo.get(data_source_id)
        depending_relation_keys = self._map_relation_keys(
            entity,
            depending_relations
        )
        return self._flattened_sets(depending_relation_keys)

    @property
    def _smache_dependency_graph(self):
        return smache._instance._dependency_graph

    @property
    def _relation_deps_repo(self):
        return smache._instance._relation_deps_repo

    def _flattened_sets(self, depending_relation_keys):
        return reduce(lambda x, y: x | y, depending_relation_keys, set())

    def _invalidate_keys(self, keys):
        self._mark_invalidation(keys)
        if smache._instance._options.write_through:
            debug("Writing through for {}".format(keys))
            self._write_through_invalidation(keys)
        else:
            debug("Write through skipped")

    def _mark_invalidation(self, keys):
        for key in keys:
            self._store.mark_as_stale(key)

    def _write_through_invalidation(self, keys):
        smache._instance._scheduler.schedule_write_through(keys)

    def _keys_sorted_by_index(self, keys, indices):
        keys_with_indices = sorted(zip(keys, indices), key=lambda x: x[1])
        return [key for key, _ in keys_with_indices]

    def _fun_name_from_key(self, fun_key):
        return self._function_serializer.fun_name(fun_key)

    def _dependency_graph(self):
        return build_dependency_graph(
            smache._instance._data_sources,
            smache._instance._computed_repo.computed_funs
        )

    def _find_data_source(self, data_source_id):
        return smache._instance._data_source_repository.find_by_data_source_id(
            data_source_id
        )

    def _map_relation_keys(self, entity, depending_relations):
        return [self._rel_keys(relation_fun, entity, computed_fun)
                for relation_fun, computed_fun in depending_relations]

    def _rel_keys(self, relation_fun, entity, computed_fun):
        computed_sources = relation_fun(entity)
        rel_keys = [self._fun_values_depending_on(source, computed_fun)
                    for source in self._list(computed_sources)]
        return self._flattened_sets(rel_keys)

    def _fun_values_depending_on(self, computed_source, computed_fun):
        data_source = self._find_data_source_for_entity(computed_source)
        return smache._instance._dependency_graph.fun_values_depending_on(
            data_source.data_source_id,
            computed_source.id,
            computed_fun.id
        )

    def _find_data_source_for_entity(self, computed_source):
        return smache._instance._data_source_repository.find_by_entity(
            computed_source
        )

    def _list(self, value):
        if self._is_iterable(value):
            return value
        else:
            return [value]

    def _is_iterable(self, value):
        return isinstance(value, list) or \
            hasattr(value, '__iter__') and \
            not MongoDataSource.is_instance(value.__class__)
