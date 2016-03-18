from collections import deque

GRAY, BLACK = 0, 1


def topological_sort(graph):
    order, state = deque(), {}
    enter = set(graph)

    def dfs(node_id):
        state[node_id] = GRAY
        node = graph.get(node_id)
        for k in node.parents:
            sk = state.get(k.id, None)
            if sk == GRAY:
                raise ValueError("cycle")
            if sk == BLACK:
                continue
            enter.discard(k.id)
            dfs(k.id)
        order.appendleft(node)
        state[node_id] = BLACK

    while enter:
        dfs(enter.pop())
    return order
