class RedisDependencyGraph:
    all_key = 'all'

    def __init__(self, redis_con):
        self.redis_con = redis_con

    def add_dependency(self, data_source_id, entity_id, dep_key):
        key = self._entity_key(data_source_id, entity_id)
        self.redis_con.sadd(key, dep_key)

    def add_fun_dependency(self, data_source_id, entity_id, fun_id, dep_key):
        key = self._entity_fun_key(data_source_id, entity_id, fun_id)
        self.redis_con.sadd(key, dep_key)

    def add_data_source_dependency(self, data_source_id, dep_key):
        self.add_dependency(data_source_id, self.all_key, dep_key)

    def values_depending_on(self, data_source_id, entity_id):
        entity_key = self._entity_key(data_source_id, entity_id)
        all_key = self._entity_key(data_source_id, self.all_key)
        return self.redis_con.sunion(entity_key, all_key)

    def fun_values_depending_on(self, data_source_id, entity_id, fun_id):
        key = self._entity_fun_key(data_source_id, entity_id, fun_id)
        return self.redis_con.smembers(key)

    def _entity_key(self, data_source_id, entity_id):
        return '/'.join([data_source_id, str(entity_id)])

    def _entity_fun_key(self, data_source_id, entity_id, fun_id):
        return '/'.join([self._entity_key(data_source_id, entity_id), fun_id])
