import redis
import smache

from .topological_sort import topological_sort
from .stores import RedisStore
from .function_serializer import FunctionSerializer
from .dependency_graph_builder import build_dependency_graph
from .smache_logging import logger
from functools import reduce


class DataUpdatePropagator:

    def __init__(self):
        self._function_serializer = FunctionSerializer()
        self.store = RedisStore(smache._options.redis_con)

    def handle_update(self, data_source_id, entity_id):
        data_source = self._find_data_source(data_source_id)
        entity = data_source.find(entity_id)
        depending_keys = smache._dependency_graph.values_depending_on(
            data_source_id,
            entity_id
        )
        depending_relation_keys = self._depending_relation_keys(
            data_source,
            entity
        )
        self._invalidate_keys(depending_keys | depending_relation_keys)

    def _depending_relation_keys(self, data_source, entity):
        data_source_id = data_source.data_source_id
        depending_relations = smache._relation_deps_repo.get(data_source_id)
        depending_relation_keys = self._map_relation_keys(
            entity,
            depending_relations
        )
        return self._flattened_sets(depending_relation_keys)

    def _flattened_sets(self, depending_relation_keys):
        return reduce(lambda x, y: x | y, depending_relation_keys, set())

    def _fun_values_depending_on(self, computed_source, computed_fun):
        data_source = self._find_data_source_for_entity(computed_source)
        return smache._dependency_graph.fun_values_depending_on(
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
        if smache._options.write_through:
            self._write_through_invalidation(keys)

    def _mark_invalidation(self, keys):
        for key in keys:
            self.store.mark_as_stale(key)

    def _write_through_invalidation(self, keys):
        sorted_nodes = self._node_ids_in_topological_order()
        fun_names = [self._fun_name_from_key(key) for key in keys]
        indices = [sorted_nodes.index(fun_name) for fun_name in fun_names]
        sorted_keys = self._keys_sorted_by_index(keys, indices)
        smache._scheduler.schedule_write_through(sorted_keys)

    def _keys_sorted_by_index(self, keys, indices):
        keys_with_indices = sorted(zip(keys, indices), key=lambda x: x[1])
        return [key for key, _ in keys_with_indices]

    def _fun_key(self, fun, *args, **kwargs):
        return self._function_serializer.serialized_fun(fun, *args, **kwargs)

    def _fun_name_from_key(self, fun_key):
        return self._function_serializer.fun_name(fun_key)

    def _node_ids_in_topological_order(self):
        topologically_sorted_nodes = topological_sort(self._dependency_graph())
        return [node.id for node in topologically_sorted_nodes]

    def _dependency_graph(self):
        return build_dependency_graph(
            smache._data_sources,
            smache._computed_repo.computed_funs
        )

    def _find_data_source(self, data_source_id):
        return [source for source in smache._data_sources
                if source.data_source_id == data_source_id][0]

    def _find_data_source_for_entity(self, computed_source):
        return next(source for source in smache._data_sources
                    if source.for_entity(computed_source))

    def _map_relation_keys(self, entity, depending_relations):
        return [self._rel_keys(relation_fun, entity, computed_fun)
                for relation_fun, computed_fun in depending_relations]

    def _rel_keys(self, relation_fun, entity, computed_fun):
        computed_sources = relation_fun(entity)
        rel_keys = [self._fun_values_depending_on(computed_source, computed_fun)
                    for computed_source in self._list(computed_sources)]
        return self._flattened_sets(rel_keys)


class AsyncScheduler:

    def __init__(self, worker_queue):
        self.worker_queue = worker_queue

    def schedule_write_through(self, keys):
        logger.debug("Schedule write through update on: {}".format(keys))
        reduce(self._enqueue_execute, keys, None)

    def schedule_update_handle(self, data_source_id, entity_id):
        self.worker_queue.enqueue_call(
            func=_handle_data_source_update,
            args=(data_source_id, entity_id)
        )

    def _enqueue_execute(self, last_job, key):
        return self.worker_queue.enqueue_call(
            func=_execute,
            args=(key,),
            depends_on=last_job
        )


class InProcessScheduler:

    def schedule_write_through(self, keys):
        for key in keys:
            _execute(key)

    def schedule_update_handle(self, data_source_id, entity_id):
        _handle_data_source_update(data_source_id, entity_id)


def _handle_data_source_update(data_source_id, entity_id):
    DataUpdatePropagator().handle_update(data_source_id, entity_id)


def _execute(key):
    logger.debug("EXECUTE on {}".format(key))
    redis_con = redis.StrictRedis(host='localhost', port=6379, db=0)
    store = RedisStore(redis_con)

    fun_name, args = FunctionSerializer().deserialized_fun(key)
    computed_fun = smache._computed_repo.get_from_id(fun_name)
    computed_value = computed_fun(*args)
    return store.store(key, computed_value)
