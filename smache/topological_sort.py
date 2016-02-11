from collections import deque

GRAY, BLACK = 0, 1

def topological_sort(nodes):
    graph = _graph_from_nodes(nodes)
    order, state = deque(), {}
    enter = set(graph)

    def dfs(node_id):
        state[node_id] = GRAY
        (node, parents) = graph.get(node_id)
        for k in parents:
            sk = state.get(k.node_id, None)
            if sk == GRAY: raise ValueError("cycle")
            if sk == BLACK: continue
            enter.discard(k.node_id)
            dfs(k.node_id)
        order.appendleft(node)
        state[node_id] = BLACK

    while enter: dfs(enter.pop())
    return order


def _graph_from_nodes(nodes):
    graph = dict()
    for node in nodes:
        graph[node.node_id] = (node, node.parents)
    return graph
