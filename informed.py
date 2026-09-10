import math
from heapq import heappush, heappop
from typing import Dict, List


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    return 2 * radius * math.asin(math.sqrt(a))


def reconstruct_path(parents: Dict[str, str | None], goal: str) -> List[str]:
    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = parents.get(current)
    return list(reversed(path))


def heuristic_distance(graph: Dict[str, Dict[str, float]], node: str, goal: str) -> float:
    if not graph.get(node):
        return 0.0
    node_data = graph.get("_meta", {}).get(node)
    if node_data is not None:
        lat1, lon1 = node_data["lat"], node_data["lon"]
        lat2, lon2 = graph["_meta"][goal]["lat"], graph["_meta"][goal]["lon"]
        return haversine_km(lat1, lon1, lat2, lon2)
    return 0.0


def greedy_best_first(graph: Dict[str, Dict[str, float]], start: str, goal: str):
    if start == goal:
        return {"path": [start], "cost": 0.0, "visited": [start]}

    frontier = []
    heappush(frontier, (0.0, start))
    visited = set()
    parents = {start: None}

    while frontier:
        _, current = heappop(frontier)
        if current in visited:
            continue
        visited.add(current)

        if current == goal:
            path = reconstruct_path(parents, goal)
            cost = sum(graph[path[i]][path[i + 1]] for i in range(len(path) - 1))
            return {"path": path, "cost": round(cost, 2), "visited": list(visited)}

        for neighbor, edge_cost in graph.get(current, {}).items():
            if neighbor in visited:
                continue
            parents[neighbor] = current
            h = heuristic_distance(graph, neighbor, goal)
            heappush(frontier, (h, neighbor))

    return {"path": [], "cost": float("inf"), "visited": list(visited)}


def a_star(graph: Dict[str, Dict[str, float]], start: str, goal: str):
    if start == goal:
        return {"path": [start], "cost": 0.0, "visited": [start]}

    frontier = []
    g_score = {start: 0.0}
    parents = {start: None}
    visited = set()
    heappush(frontier, (0.0, start))

    while frontier:
        _, current = heappop(frontier)
        if current in visited:
            continue
        visited.add(current)

        if current == goal:
            path = reconstruct_path(parents, goal)
            return {"path": path, "cost": round(g_score[current], 2), "visited": list(visited)}

        for neighbor, edge_cost in graph.get(current, {}).items():
            tentative = g_score[current] + edge_cost
            if tentative < g_score.get(neighbor, float("inf")):
                g_score[neighbor] = tentative
                parents[neighbor] = current
                h = heuristic_distance(graph, neighbor, goal)
                heappush(frontier, (tentative + h, neighbor))

    return {"path": [], "cost": float("inf"), "visited": list(visited)}
