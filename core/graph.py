class Graph:
    def __init__(self, directed=True):
        self.directed = directed
        self._nodes = set()
        self._edges = {}  # {u: {v: weight}}

    # ---------------- NODES ----------------
    def add_node(self, node):
        self._nodes.add(node)
        if node not in self._edges:
            self._edges[node] = {}

    def remove_node(self, node):
        self._nodes.discard(node)
        self._edges.pop(node, None)

        for u in self._edges:
            self._edges[u].pop(node, None)

    # ---------------- EDGES ----------------
    def add_edge(self, u, v, weight=1):
        self.add_node(u)
        self.add_node(v)

        self._edges[u][v] = weight

        if not self.directed:
            self._edges[v][u] = weight

    def remove_edge(self, u, v):
        self._edges.get(u, {}).pop(v, None)

        if not self.directed:
            self._edges.get(v, {}).pop(u, None)

    # ---------------- COMPAT UI ----------------
    def get_nodes(self):
        return list(self._nodes)

    def get_edges(self):
        result = []
        for u, neigh in self._edges.items():
            for v, w in neigh.items():
                result.append((u, v, w))
        return result

    def get_neighbors(self, node):
        return self._edges.get(node, {})

    def number_of_nodes(self):
        return len(self._nodes)

    def number_of_edges(self):
        return sum(len(v) for v in self._edges.values())