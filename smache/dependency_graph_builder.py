class Node:

    def __init__(self, node_id):
        self.id = node_id
        self.parents = []

    def add_parent(self, parent):
        self.parents.append(parent)

    def __repr__(self):
        parent_ids = [str(parent.id) for parent in self.parents]
        return "<{} -> ({})>".format(self.id, parent_ids)


def build_dependency_graph(data_sources, computed_functions):
    nodes = {source.data_source_id: Node(
        source.data_source_id) for source in data_sources}

    for computed_fun in computed_functions.values():
        nodes[computed_fun.id] = Node(computed_fun.id)

    for computed_fun in computed_functions.values():
        computed_node = nodes[computed_fun.id]
        sources = list(computed_fun.arg_deps) + \
            list(computed_fun.data_source_deps)
        for data_source_dep in sources:
            nodes[data_source_dep.data_source_id].add_parent(computed_node)

    return nodes
