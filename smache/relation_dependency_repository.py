class RelationDependencyRepository:
    def __init__(self):
        self._relation_deps = {}

    def add_all(self, relations):
        for relation_data_source, related_fun in relations:
            self.add(relation_data_source.data_source_id, related_fun)

    def add(self, relation_data_source_id, relation_fun):
        if not self._relation_deps.get(relation_data_source_id):
            self._relation_deps[relation_data_source_id] = set()
        self._relation_deps[relation_data_source_id].add(relation_fun)

    def get(self, data_source_id):
        return self._relation_deps.get(data_source_id, set())
