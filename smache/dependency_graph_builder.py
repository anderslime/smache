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
    nodes = {source.data_source_id: Node(source.data_source_id) for source in data_sources}

    for computed_fun in computed_functions.values():
        nodes[computed_fun.fun_name] = Node(computed_fun.fun_name)

    for computed_fun in computed_functions.values():
        computed_node = nodes[computed_fun.fun_name]
        for data_source_dep in list(computed_fun.entity_deps) + list(computed_fun.data_source_deps):
            nodes[data_source_dep.data_source_id].add_parent(computed_node)
        for computed_dep in computed_fun.computed_deps:
            nodes[computed_dep.fun_name].add_parent(computed_node)

    return nodes
