def run(data):
    points = data.get("points", [])
    if not points:
        return {"error": "No points provided"}

    n = len(points)
    visited = [False] * n
    path = [0]
    visited[0] = True
    total = 0.0
    current = 0

    def dist(a, b):
        dx = a["x"] - b["x"]
        dy = a["y"] - b["y"]
        return (dx * dx + dy * dy) ** 0.5

    for _ in range(n - 1):
        next_i = None
        min_d = float("inf")
        for i, p in enumerate(points):
            if not visited[i]:
                d = dist(points[current], p)
                if d < min_d:
                    min_d = d
                    next_i = i
        path.append(next_i)
        visited[next_i] = True
        total += min_d
        current = next_i

    total += dist(points[current], points[0])
    path.append(0)
    edges = [{"source": path[i], "target": path[i+1]} for i in range(len(path) - 1)]
    return {"path": path, "edges": edges, "cost": total, "points": points}
