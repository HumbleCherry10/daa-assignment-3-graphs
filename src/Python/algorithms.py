"""Implement the six graph methods and your route helper. See the README at the repository root."""

import heapq


def dsu(request):
    """DSU with path compression and union by size/rank; return states."""
    n = request["n"]
    operations = request["operations"]

    if n == 0:
        return {"states": []}

    parent = list(range(n))
    size = [1] * n
    components = n
    largest = 1

    def find(i):
        root = i
        while root != parent[root]:
            root = parent[root]
        curr = i
        while curr != root:
            nxt = parent[curr]
            parent[curr] = root
            curr = nxt
        return root

    states = []
    for u, v in operations:
        root_u = find(u)
        root_v = find(v)
        if root_u != root_v:
            if size[root_u] < size[root_v]:
                root_u, root_v = root_v, root_u
            parent[root_v] = root_u
            size[root_u] += size[root_v]
            if size[root_u] > largest:
                largest = size[root_u]
            components -= 1
        states.append([components, largest])

    return {"states": states}


def kruskal(request):
    """Separate Kruskal implementation; return cost, edge_ids, components."""
    n = request["n"]
    edges = request["edges"]

    if n == 0:
        return {"cost": 0, "edge_ids": [], "components": 0}

    parent = list(range(n))
    size = [1] * n
    components = n
    cost = 0
    edge_ids = []

    def find(i):
        root = i
        while root != parent[root]:
            root = parent[root]
        curr = i
        while curr != root:
            nxt = parent[curr]
            parent[curr] = root
            curr = nxt
        return root

    indexed_edges = [(edges[i][2], i, edges[i][0], edges[i][1]) for i in range(len(edges))]
    indexed_edges.sort(key=lambda e: e[0])

    for w, edge_id, u, v in indexed_edges:
        if u == v:
            continue
        ru = find(u)
        rv = find(v)
        if ru != rv:
            if size[ru] < size[rv]:
                ru, rv = rv, ru
            parent[rv] = ru
            size[ru] += size[rv]
            cost += w
            edge_ids.append(edge_id)
            components -= 1

    return {"cost": cost, "edge_ids": edge_ids, "components": components}


def prim(request):
    """Separate Prim implementation; restart for every unvisited component."""
    n = request["n"]
    edges = request["edges"]

    if n == 0:
        return {"cost": 0, "edge_ids": [], "components": 0}

    adj = [[] for _ in range(n)]
    for i in range(len(edges)):
        u, v, w = edges[i]
        if u == v:
            continue
        adj[u].append((w, i, v))
        adj[v].append((w, i, u))

    visited = [False] * n
    cost = 0
    edge_ids = []
    components = 0

    for start in range(n):
        if visited[start]:
            continue
        components += 1
        visited[start] = True
        pq = []
        for w, edge_id, neighbor in adj[start]:
            heapq.heappush(pq, (w, edge_id, neighbor))

        while pq:
            w, edge_id, v = heapq.heappop(pq)
            if visited[v]:
                continue
            visited[v] = True
            cost += w
            edge_ids.append(edge_id)
            for next_w, next_edge_id, neighbor in adj[v]:
                if not visited[neighbor]:
                    heapq.heappush(pq, (next_w, next_edge_id, neighbor))

    return {"cost": cost, "edge_ids": edge_ids, "components": components}


def scc(request):
    """Kosaraju with two DFS passes; return component and condensation."""
    n = request["n"]
    edges = request["edges"]

    if n == 0:
        return {"component": [], "condensation": []}

    adj = [[] for _ in range(n)]
    adj_rev = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj_rev[v].append(u)

    # Pass 1: compute finish order on original graph
    visited = [False] * n
    order = []

    for start in range(n):
        if visited[start]:
            continue
        stack = [start]
        edge_idx = [0]
        visited[start] = True
        while stack:
            u = stack[-1]
            i = edge_idx[-1]
            if i < len(adj[u]):
                v = adj[u][i]
                edge_idx[-1] = i + 1
                if not visited[v]:
                    visited[v] = True
                    stack.append(v)
                    edge_idx.append(0)
            else:
                stack.pop()
                edge_idx.pop()
                order.append(u)

    # Pass 2: assign components on transposed graph in decreasing finish order
    component = [-1] * n
    label = 0
    for start in reversed(order):
        if component[start] != -1:
            continue
        component[start] = label
        stack = [start]
        edge_idx = [0]
        while stack:
            u = stack[-1]
            i = edge_idx[-1]
            if i < len(adj_rev[u]):
                v = adj_rev[u][i]
                edge_idx[-1] = i + 1
                if component[v] == -1:
                    component[v] = label
                    stack.append(v)
                    edge_idx.append(0)
            else:
                stack.pop()
                edge_idx.pop()
        label += 1

    # Condensation graph: distinct cross-component directed pairs
    condensation_set = set()
    for u, v in edges:
        cu, cv = component[u], component[v]
        if cu != cv:
            condensation_set.add((cu, cv))

    condensation = [list(pair) for pair in condensation_set]
    return {"component": component, "condensation": condensation}


def topo(request):
    """Three-state DFS and reverse finish order; return acyclic and order."""
    n = request["n"]
    edges = request["edges"]

    if n == 0:
        return {"acyclic": True, "order": []}

    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)

    # 0 = unvisited, 1 = active, 2 = finished
    state = [0] * n
    finish_order = []

    for start in range(n):
        if state[start] != 0:
            continue
        stack = [start]
        edge_idx = [0]
        state[start] = 1

        while stack:
            u = stack[-1]
            i = edge_idx[-1]
            if i < len(adj[u]):
                v = adj[u][i]
                edge_idx[-1] = i + 1
                if state[v] == 1:
                    # Directed cycle detected
                    return {"acyclic": False, "order": []}
                elif state[v] == 0:
                    state[v] = 1
                    stack.append(v)
                    edge_idx.append(0)
            else:
                stack.pop()
                edge_idx.pop()
                state[u] = 2
                finish_order.append(u)

    finish_order.reverse()
    return {"acyclic": True, "order": finish_order}


def dag(request):
    """Whole-graph cycle check and DAG relaxation; add your own route helper."""
    n = request["n"]
    source = request["source"]
    edges = request["edges"]

    adj = [[] for _ in range(n)]
    for edge_id in range(len(edges)):
        u, v, w = edges[edge_id]
        adj[u].append((v, w, edge_id))

    # Whole graph cycle check and topological sort using three-state DFS
    state = [0] * n
    finish_order = []

    for start in range(n):
        if state[start] != 0:
            continue
        stack = [start]
        edge_idx = [0]
        state[start] = 1

        while stack:
            u = stack[-1]
            i = edge_idx[-1]
            if i < len(adj[u]):
                v, _, _ = adj[u][i]
                edge_idx[-1] = i + 1
                if state[v] == 1:
                    return {"acyclic": False, "distance": [], "parent_edge": []}
                elif state[v] == 0:
                    state[v] = 1
                    stack.append(v)
                    edge_idx.append(0)
            else:
                stack.pop()
                edge_idx.pop()
                state[u] = 2
                finish_order.append(u)

    finish_order.reverse()

    distance = [None] * n
    parent_edge = [-1] * n
    distance[source] = 0

    for u in finish_order:
        if distance[u] is None:
            continue
        dist_u = distance[u]
        for v, w, edge_id in adj[u]:
            cand = dist_u + w
            if distance[v] is None or cand < distance[v]:
                distance[v] = cand
                parent_edge[v] = edge_id

    return {
        "acyclic": True,
        "distance": distance,
        "parent_edge": parent_edge,
    }


def reconstruct_route(edges, source, target, parent_edge):
    """
    Reconstructs the vertex sequence from source to target using parent_edge IDs.
    Returns:
        A list of vertices [source, ..., target] if target is reachable from source.
        Returns None if target is unreachable from source.
    """
    if target == source:
        return [source]
    if parent_edge[target] == -1:
        return None

    path = []
    curr = target
    while curr != source:
        p_edge = parent_edge[curr]
        if p_edge == -1:
            return None
        u, v, _ = edges[p_edge]
        path.append(curr)
        curr = u
    path.append(source)
    path.reverse()
    return path
