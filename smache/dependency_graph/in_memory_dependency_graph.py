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
