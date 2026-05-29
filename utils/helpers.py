import math


def distance(p1, p2):
    """Distance entre 2 points (utile pour UI graph)"""
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)


def midpoint(p1, p2):
    """Milieu entre 2 points"""
    return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)


def clamp(value, min_val, max_val):
    """Limiter une valeur"""
    return max(min_val, min(value, max_val))


def reconstruct_path(parent, end):
    """Reconstruit un chemin depuis un dictionnaire parent"""
    path = []
    current = end

    while current is not None:
        path.append(current)
        current = parent.get(current)

    return list(reversed(path))


def format_infinity(value):
    """Affichage propre des infinis"""
    if value == float("inf"):
        return "∞"
    if value == float("-inf"):
        return "-∞"
    return str(value)