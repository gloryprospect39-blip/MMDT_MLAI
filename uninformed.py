from collections import deque
from typing import Dict, List, Tuple


def reconstruct_path(parents: Dict[str, str | None], goal: str) -> List[str]:
    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = parents.get(current)
    return list(reversed(path))


def bfs(graph: Dict[str, Dict[str, float]], start: str, goal: str):
    if start == goal:
        return {"path": [start], "cost": 0.0, "visited": [start]}

    queue = deque([start])
    visited = {start}
    parents = {start: None}

    while queue:
        current = queue.popleft()
        for neighbor, weight in graph.get(current, {}).items():
            if neighbor in visited:
                continue
            visited.add(neighbor)
            parents[neighbor] = current
            if neighbor == goal:
                path = reconstruct_path(parents, goal)
                cost = sum(graph[path[i]][path[i + 1]] for i in range(len(path) - 1))
                return {"path": path, "cost": round(cost, 2), "visited": list(visited)}
            queue.append(neighbor)

    return {"path": [], "cost": float("inf"), "visited": list(visited)}


def dfs(graph: Dict[str, Dict[str, float]], start: str, goal: str):
    if start == goal:
        return {"path": [start], "cost": 0.0, "visited": [start]}

    stack = [(start, [start])]
    visited = set()
    seen = {start}

    while stack:
        current, path = stack.pop()
        visited.add(current)
        for neighbor, weight in graph.get(current, {}).items():
            if neighbor in seen:
                continue
            seen.add(neighbor)
            new_path = path + [neighbor]
            if neighbor == goal:
                cost = sum(graph[new_path[i]][new_path[i + 1]] for i in range(len(new_path) - 1))
                return {"path": new_path, "cost": round(cost, 2), "visited": list(visited)}
            stack.append((neighbor, new_path))

    return {"path": [], "cost": float("inf"), "visited": list(visited)}


def ucs(graph: Dict[str, Dict[str, float]], start: str, goal: str):
    import heapq

    if start == goal:
        return {"path": [start], "cost": 0.0, "visited": [start]}

    heap = [(0.0, start)]
    cost_so_far = {start: 0.0}
    parents = {start: None}
    visited = set()

    while heap:
        current_cost, current = heapq.heappop(heap)
        if current in visited:
            continue
        visited.add(current)

        if current == goal:
            path = reconstruct_path(parents, goal)
            return {"path": path, "cost": round(current_cost, 2), "visited": list(visited)}

        for neighbor, edge_cost in graph.get(current, {}).items():
            new_cost = current_cost + edge_cost
            if new_cost < cost_so_far.get(neighbor, float("inf")):
                cost_so_far[neighbor] = new_cost
                parents[neighbor] = current
                heapq.heappush(heap, (new_cost, neighbor))

    return {"path": [], "cost": float("inf"), "visited": list(visited)}


def ids(graph: Dict[str, Dict[str, float]], start: str, goal: str):
    def depth_limited_search(current, goal, limit, visited):
        if current == goal:
            return [current], 0.0
        if limit == 0:
            return None, float("inf")
        best_path = None
        best_cost = float("inf")
        for neighbor, weight in graph.get(current, {}).items():
            if neighbor in visited:
                continue
            visited.add(neighbor)
            path, cost = depth_limited_search(neighbor, goal, limit - 1, visited)
            if path is not None:
                route = [current] + path
                total_cost = cost + weight
                if total_cost < best_cost:
                    best_cost = total_cost
                    best_path = route
            visited.remove(neighbor)
        return best_path, best_cost

    limit = 0
    visited_order = []
    while True:
        visited = {start}
        path, cost = depth_limited_search(start, goal, limit, visited)
        if path is not None:
            return {"path": path, "cost": round(cost, 2), "visited": visited_order or [start]}
        if limit > len(graph) * 2:
            return {"path": [], "cost": float("inf"), "visited": visited_order}
        limit += 1
