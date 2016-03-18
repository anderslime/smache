class RelationDependencyRepository:

    def __init__(self):
        self._relation_deps = {}

    def add_all(self, relations, computed_fun):
        for relation_data_source, related_fun in relations:
            self.add(
                relation_data_source.data_source_id,
                related_fun,
                computed_fun
            )

    def add(self, relation_data_source_id, relation_fun, computed_fun):
        if not self._relation_deps.get(relation_data_source_id):
            self._relation_deps[relation_data_source_id] = set()
        relation_dep = (relation_fun, computed_fun)
        self._relation_deps[relation_data_source_id].add(relation_dep)

    def get(self, data_source_id):
        return self._relation_deps.get(data_source_id, set())
