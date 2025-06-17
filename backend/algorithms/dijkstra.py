import heapq

def run(data):
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    start = data.get("start", 0)
    goal = data.get("goal", len(nodes) - 1)

    adj = {i: [] for i in range(len(nodes))}
    for e in edges:
        adj[e["source"]].append((e["target"], e.get("weight", 1)))
        adj[e["target"]].append((e["source"], e.get("weight", 1)))

    dist = [float("inf")] * len(nodes)
    prev = [None] * len(nodes)
    dist[start] = 0
    pq = [(0, start)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        if u == goal:
            break
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))

    path = []
    u = goal
    if prev[u] is not None or u == start:
        while u is not None:
            path.append(u)
            u = prev[u]
        path.reverse()

    path_edges = [{"source": path[i], "target": path[i+1]} for i in range(len(path)-1)] if len(path) > 1 else []
    return {
        "path": path,
        "edges": path_edges,
        "cost": dist[goal],
        "nodes": nodes,
        "all_edges": edges,
    }
