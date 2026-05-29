def bellman_max(graph, start, end=None):

    nodes = graph.get_nodes()

    dist = {n: float("-inf") for n in nodes}
    parent = {n: None for n in nodes}

    dist[start] = 0

    edges = graph.get_edges()

    for _ in range(len(nodes) - 1):
        updated = False

        for u, v, w in edges:
            if dist[u] != float("-inf") and dist[u] + w > dist[v]:
                dist[v] = dist[u] + w
                parent[v] = u
                updated = True

        if not updated:
            break

    path = _reconstruct(parent, start, end)

    return {
        "distance": dist,
        "parent": parent,
        "path": path
    }


def _reconstruct(parent, start, end):
    if end is None:
        return []

    path = []
    cur = end

    while cur is not None:
        path.append(cur)
        cur = parent[cur]

    path.reverse()
    return path if path and path[0] == start else []