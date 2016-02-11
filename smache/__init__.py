from collections import namedtuple as struct
import redis
import json

CacheResult = struct("CacheResult", ["value", "is_fresh"])

class RedisStore:
    def __init__(self, redis_con):
        self.redis_con = redis_con

    def store(self, key, value):
        self._store_entry(key, value, 'True')

    def lookup(self, key):
        raw_cache_result = self._get_all(key) or {}
        return CacheResult(
            self._deserialize_json(raw_cache_result.get('value')),
            self._deserialize_bool(raw_cache_result.get('is_fresh'))
        )

    def is_fresh(self, key):
        return self._get_field(key, 'is_fresh') == 'True'

    def mark_as_stale(self, key):
        self.redis_con.hset(key, 'is_fresh', 'False')

    def _deserialize_bool(self, boolean):
        return boolean == 'True'

    def _deserialize_json(self, value):
        if value is None:
            return None
        return json.loads(value)

    def _store_entry(self, key, value, is_fresh):
        pipe = self.redis_con.pipeline()
        pipe.hset(key, 'value', json.dumps(value))
        pipe.hset(key, 'is_fresh', is_fresh)
        pipe.execute()

    def _get_all(self, key):
        return self.redis_con.hgetall(key)

    def _get_field(self, key, field):
        return self.redis_con.hget(key, field)

class InMemoryStore:
    def __init__(self):
        self._data = {}

    def store(self, key, value):
        self._data[key] = {'is_fresh': True, 'value': value}

    def lookup(self, key):
        raw_cache_result = self._data.get(key, {})
        return CacheResult(
            raw_cache_result.get('value', None),
            raw_cache_result.get('is_fresh', False)
        )

    def is_fresh(self, key):
        return self._data.get(key, {}).get('is_fresh', None)

    def mark_as_stale(self, key):
        old_value = self._data.get(key, None)
        if old_value is not None:
            old_value['is_fresh'] = False
            self._data[key] = old_value


class FunctionStore:
    def fun_key(self, fun, *args, **kwargs):
        fun_name_key = fun.__name__
        args_key = '/'.join(str(arg.id) for arg in args)
        return '/'.join([fun_name_key, args_key])


class DataSource:
    def __init__(self, data_source_id):
        self.data_source_id = data_source_id
        self.subscriber = lambda x: x

    def subscribe(self, fun):
        self.subscriber = fun

    def did_update(self, entity_id):
        self.subscriber(self, entity_id)


class Node:
    def __init__(self, node_id, parents = []):
        self.node_id = node_id
        self.parents = parents

    def add_parent(self, parent_node):
        self.parents.append(parent_node)

class RedisDependencyGraph:
    def __init__(self, redis_con):
        self.redis_con = redis_con

    def add_dependency(self, data_source_id, entity_id, dep_key):
        key = self._entity_key(data_source_id, entity_id)
        self.redis_con.sadd(key, dep_key)

    def add_data_source_dependency(self, data_source_id, dep_key):
        self.add_dependency(data_source_id, 'all', dep_key)

    def values_depending_on(self, data_source_id, entity_id):
        entity_key = self._entity_key(data_source_id, entity_id)
        all_key = self._entity_key(data_source_id, 'all')
        return self.redis_con.sunion(entity_key, all_key)

    def _entity_key(self, data_source_id, entity_id):
        return '/'.join([data_source_id, str(entity_id)])


class InMemoryDependencyGraph:
    def __init__(self):
        self._dependencies = {}

    def add_dependency(self, data_source_id, entity_id, dep_key):
        data_source_deps = self._dependencies.get(data_source_id, {})
        entity_deps = data_source_deps.get(entity_id, set())
        entity_deps.add(dep_key)
        data_source_deps[entity_id] = entity_deps
        self._dependencies[data_source_id] = data_source_deps

    def add_data_source_dependency(self, data_source_id, dep_key):
        self.add_dependency(data_source_id, 'all', dep_key)

    def values_depending_on(self, data_source_id, entity_id):
        data_source_deps = self._dependencies[data_source_id]
        return data_source_deps.get('all', set()) | data_source_deps.get(entity_id, set())

    def _entity_key(self, data_source_id, entity_id):
        return '/'.join([data_source_id, str(entity_id)])


class CacheManager:
    def __init__(self, fun_store, store, dep_graph):
        self.fun_store        = fun_store
        self.store            = store
        self.dep_graph        = dep_graph
        self._computed_funs   = {}

    def cache_function(self, fun, *args, **kwargs):
        key = self.fun_store.fun_key(fun, *args, **kwargs)
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

    def data_source(self, data_source_id):
        data_source = DataSource(data_source_id)
        self.add_sources(data_source)
        return data_source

    def add_sources(self, *data_sources):
        for data_source in data_sources:
            data_source.subscribe(self._on_data_source_update)

    def add_computed(self, fun, entity_deps, kwargs):
        data_source_deps = kwargs.get('sources', ())
        self._computed_funs[fun.__name__] = (fun.__name__, entity_deps, data_source_deps)

    def is_fresh(self, key):
        return self.store.is_fresh(key)

    def is_fun_fresh(self, fun, *args, **kwargs):
        key = self.fun_store.fun_key(fun, *args, **kwargs)
        return self.store.is_fresh(key)

    def _add_data_source_dependencies(self, fun, key):
        data_source_deps = self._computed_funs[fun.__name__][2]
        for data_source_dep in data_source_deps:
            self.dep_graph.add_data_source_dependency(
                data_source_dep.data_source_id,
                key
            )

    def _add_entity_dependencies(self, fun, args, key):
        entity_deps = self._computed_funs[fun.__name__][1]
        for data_source, data_source_entity in zip(entity_deps, args):
            self.dep_graph.add_dependency(
                data_source.data_source_id,
                data_source_entity.id,
                key
            )

    def parse_deps(self, value):
        if isinstance(value, tuple):
            return value
        else:
            return (value,)

    def _on_data_source_update(self, data_source, entity_id):
        depending_keys = self.dep_graph.values_depending_on(data_source.data_source_id, entity_id)
        for key in depending_keys:
            self.store.mark_as_stale(key)

redis_con = redis.StrictRedis(host='localhost', port=6379, db=0)

dep_graph = RedisDependencyGraph(redis_con)
store     = RedisStore(redis_con)
fun_store = FunctionStore()
smache    = CacheManager(fun_store, store, dep_graph)
