from core.dijkstra import dijkstra
from core.bellman_max import bellman_max

def run_dijkstra(graph, start, end):
    return dijkstra(graph, start, end)

def run_bellman(graph, start, end):
    return bellman_max(graph, start, end)