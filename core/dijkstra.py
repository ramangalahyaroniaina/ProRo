import heapq 
import math 

def dijkstra(graph, start, end=None):

    nodes = graph.get_nodes()

    dist = {node: math.inf for node in nodes}
    parent = {node: None for node in nodes}
    visited = set()

    steps = []
    tables = []

    dist[start] = 0
    pq = [(0, start)]

    steps.append(f"Initialisation: start={start}")
    tables.append({
        "dist": dist.copy(),
        "parent": parent.copy()
    })

    while pq:
        current_dist, u = heapq.heappop(pq)

        if u in visited:
            continue

        visited.add(u)

        steps.append(f"Choix du sommet {u} (distance={current_dist})")

        # Sauvegarder l'état avant relaxation
        tables.append({
            "dist": dist.copy(),
            "parent": parent.copy()
        })

        # Relaxation des voisins
        relaxation_occurred = False
        for v, weight in graph.get_neighbors(u).items():
            if v not in visited:  # Ne relaxer que les nœuds non visités
                new_dist = current_dist + weight

                if new_dist < dist[v]:
                    old = dist[v]
                    old_str = "∞" if old == math.inf else str(old)
                    dist[v] = new_dist
                    parent[v] = u
                    relaxation_occurred = True

                    steps.append(f"Relaxation: {u}->{v} | {old_str} → {new_dist}")

                    heapq.heappush(pq, (new_dist, v))

        # Sauvegarder l'état après relaxation (même si pas de changement)
        tables.append({
            "dist": dist.copy(),
            "parent": parent.copy()
        })

        # Vérifier si on a atteint la fin
        if end is not None and u == end:
            steps.append(f"Arrivée atteinte: {end}")
            tables.append({
                "dist": dist.copy(),
                "parent": parent.copy()
            })
            break

    # Reconstruire le chemin
    path = []
    if end is not None and dist[end] != math.inf:
        path = _reconstruct(parent, start, end)

    return {
        "distance": dist,
        "parent": parent,
        "path": path,
        "steps": steps,
        "tables": tables,
        "visited": visited
    }


def _reconstruct(parent, start, end):
    """Reconstruit le chemin du start à end"""
    if end is None:
        return []

    path = []
    cur = end

    while cur is not None:
        path.append(cur)
        cur = parent[cur]

    path.reverse()

    # Vérifier que le chemin commence bien par start
    if path and path[0] == start:
        return path
    return []