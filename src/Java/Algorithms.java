import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.PriorityQueue;
import java.util.Set;

/**
 * Implementation of graph algorithms: DSU, Kruskal, Prim, Kosaraju SCC,
 * DFS topological ordering, DAG shortest paths, and route reconstruction helper.
 */
public final class Algorithms {

    private Algorithms() {
    }

    /** DSU with path compression and union by size; returns states. */
    static Map<String, Object> dsu(Map<String, Object> input) {
        int n = Input.vertexCount(input);
        int[][] operations = Input.operations(input);

        if (n == 0) {
            return Map.of("states", List.of());
        }

        int[] parent = new int[n];
        int[] size = new int[n];
        for (int i = 0; i < n; i++) {
            parent[i] = i;
            size[i] = 1;
        }

        int components = n;
        int largest = 1;

        int[][] states = new int[operations.length][2];
        for (int i = 0; i < operations.length; i++) {
            int u = operations[i][0];
            int v = operations[i][1];

            int rootU = find(parent, u);
            int rootV = find(parent, v);

            if (rootU != rootV) {
                if (size[rootU] < size[rootV]) {
                    int tmp = rootU;
                    rootU = rootV;
                    rootV = tmp;
                }
                parent[rootV] = rootU;
                size[rootU] += size[rootV];
                if (size[rootU] > largest) {
                    largest = size[rootU];
                }
                components--;
            }
            states[i][0] = components;
            states[i][1] = largest;
        }

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("states", states);
        return result;
    }

    private static int find(int[] parent, int i) {
        int root = i;
        while (root != parent[root]) {
            root = parent[root];
        }
        int curr = i;
        while (curr != root) {
            int nxt = parent[curr];
            parent[curr] = root;
            curr = nxt;
        }
        return root;
    }

    /** Separate Kruskal implementation; return cost, edge_ids, components. */
    static Map<String, Object> kruskal(Map<String, Object> input) {
        int n = Input.vertexCount(input);
        int[][] edges = Input.edges(input);

        if (n == 0) {
            return Map.of("cost", 0L, "edge_ids", List.of(), "components", 0);
        }

        int[] parent = new int[n];
        int[] size = new int[n];
        for (int i = 0; i < n; i++) {
            parent[i] = i;
            size[i] = 1;
        }

        Integer[] order = new Integer[edges.length];
        for (int i = 0; i < edges.length; i++) {
            order[i] = i;
        }
        Arrays.sort(order, Comparator.comparingLong(i -> edges[i][2]));

        long cost = 0;
        int components = n;
        List<Integer> edgeIds = new ArrayList<>();

        for (int idx : order) {
            int u = edges[idx][0];
            int v = edges[idx][1];
            int w = edges[idx][2];

            if (u == v) {
                continue;
            }

            int rootU = find(parent, u);
            int rootV = find(parent, v);

            if (rootU != rootV) {
                if (size[rootU] < size[rootV]) {
                    int tmp = rootU;
                    rootU = rootV;
                    rootV = tmp;
                }
                parent[rootV] = rootU;
                size[rootU] += size[rootV];
                cost += w;
                edgeIds.add(idx);
                components--;
            }
        }

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("cost", cost);
        result.put("edge_ids", edgeIds);
        result.put("components", components);
        return result;
    }

    /** Separate Prim implementation; restart for every unvisited component. */
    static Map<String, Object> prim(Map<String, Object> input) {
        int n = Input.vertexCount(input);
        int[][] edges = Input.edges(input);

        if (n == 0) {
            return Map.of("cost", 0L, "edge_ids", List.of(), "components", 0);
        }

        List<List<int[]>> adj = new ArrayList<>(n);
        for (int i = 0; i < n; i++) {
            adj.add(new ArrayList<>());
        }

        for (int i = 0; i < edges.length; i++) {
            int u = edges[i][0];
            int v = edges[i][1];
            int w = edges[i][2];
            if (u == v) {
                continue;
            }
            adj.get(u).add(new int[]{w, i, v});
            adj.get(v).add(new int[]{w, i, u});
        }

        boolean[] visited = new boolean[n];
        long cost = 0;
        int components = 0;
        List<Integer> edgeIds = new ArrayList<>();

        PriorityQueue<long[]> pq = new PriorityQueue<>(Comparator.comparingLong(a -> a[0]));

        for (int start = 0; start < n; start++) {
            if (visited[start]) {
                continue;
            }
            components++;
            visited[start] = true;
            pq.clear();

            for (int[] e : adj.get(start)) {
                pq.offer(new long[]{e[0], e[1], e[2]});
            }

            while (!pq.isEmpty()) {
                long[] top = pq.poll();
                long w = top[0];
                int edgeId = (int) top[1];
                int to = (int) top[2];

                if (visited[to]) {
                    continue;
                }
                visited[to] = true;
                cost += w;
                edgeIds.add(edgeId);

                for (int[] nextE : adj.get(to)) {
                    int neighbor = nextE[2];
                    if (!visited[neighbor]) {
                        pq.offer(new long[]{nextE[0], nextE[1], neighbor});
                    }
                }
            }
        }

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("cost", cost);
        result.put("edge_ids", edgeIds);
        result.put("components", components);
        return result;
    }

    /** Kosaraju's two DFS passes; return component and exact condensation. */
    static Map<String, Object> scc(Map<String, Object> input) {
        int n = Input.vertexCount(input);
        int[][] edges = Input.edges(input);

        if (n == 0) {
            return Map.of("component", List.of(), "condensation", List.of());
        }

        List<List<Integer>> adj = new ArrayList<>(n);
        List<List<Integer>> adjRev = new ArrayList<>(n);
        for (int i = 0; i < n; i++) {
            adj.add(new ArrayList<>());
            adjRev.add(new ArrayList<>());
        }

        for (int[] edge : edges) {
            int u = edge[0];
            int v = edge[1];
            adj.get(u).add(v);
            adjRev.get(v).add(u);
        }

        // Pass 1: compute finish order on original graph using explicit stack
        boolean[] visited = new boolean[n];
        int[] finishOrder = new int[n];
        int finishCount = 0;

        int[] stack = new int[n];
        int[] edgeIdx = new int[n];

        for (int start = 0; start < n; start++) {
            if (visited[start]) {
                continue;
            }
            int top = 0;
            stack[top] = start;
            edgeIdx[top] = 0;
            visited[start] = true;

            while (top >= 0) {
                int u = stack[top];
                int idx = edgeIdx[top];
                List<Integer> neighbors = adj.get(u);
                if (idx < neighbors.size()) {
                    int v = neighbors.get(idx);
                    edgeIdx[top] = idx + 1;
                    if (!visited[v]) {
                        visited[v] = true;
                        top++;
                        stack[top] = v;
                        edgeIdx[top] = 0;
                    }
                } else {
                    finishOrder[finishCount++] = u;
                    top--;
                }
            }
        }

        // Pass 2: assign components on reversed graph in decreasing finish order
        int[] component = new int[n];
        Arrays.fill(component, -1);
        int label = 0;

        for (int i = n - 1; i >= 0; i--) {
            int start = finishOrder[i];
            if (component[start] != -1) {
                continue;
            }
            int top = 0;
            stack[top] = start;
            edgeIdx[top] = 0;
            component[start] = label;

            while (top >= 0) {
                int u = stack[top];
                int idx = edgeIdx[top];
                List<Integer> neighbors = adjRev.get(u);
                if (idx < neighbors.size()) {
                    int v = neighbors.get(idx);
                    edgeIdx[top] = idx + 1;
                    if (component[v] == -1) {
                        component[v] = label;
                        top++;
                        stack[top] = v;
                        edgeIdx[top] = 0;
                    }
                } else {
                    top--;
                }
            }
            label++;
        }

        // Condensation: distinct cross-component pairs
        Set<Long> edgeSet = new HashSet<>();
        List<int[]> condensation = new ArrayList<>();
        for (int[] edge : edges) {
            int cu = component[edge[0]];
            int cv = component[edge[1]];
            if (cu != cv) {
                long key = (((long) cu) << 32) | (cv & 0xFFFFFFFFL);
                if (edgeSet.add(key)) {
                    condensation.add(new int[]{cu, cv});
                }
            }
        }

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("component", component);
        result.put("condensation", condensation);
        return result;
    }

    /** Three-state DFS and reverse finish order; return acyclic and order. */
    static Map<String, Object> topo(Map<String, Object> input) {
        int n = Input.vertexCount(input);
        int[][] edges = Input.edges(input);

        if (n == 0) {
            return Map.of("acyclic", true, "order", List.of());
        }

        List<List<Integer>> adj = new ArrayList<>(n);
        for (int i = 0; i < n; i++) {
            adj.add(new ArrayList<>());
        }
        for (int[] edge : edges) {
            adj.get(edge[0]).add(edge[1]);
        }

        // 0 = unvisited, 1 = active, 2 = finished
        int[] state = new int[n];
        int[] order = new int[n];
        int orderCount = 0;

        int[] stack = new int[n];
        int[] edgeIdx = new int[n];

        for (int start = 0; start < n; start++) {
            if (state[start] != 0) {
                continue;
            }
            int top = 0;
            stack[top] = start;
            edgeIdx[top] = 0;
            state[start] = 1;

            while (top >= 0) {
                int u = stack[top];
                int idx = edgeIdx[top];
                List<Integer> neighbors = adj.get(u);
                if (idx < neighbors.size()) {
                    int v = neighbors.get(idx);
                    edgeIdx[top] = idx + 1;
                    if (state[v] == 1) {
                        return Map.of("acyclic", false, "order", List.of());
                    } else if (state[v] == 0) {
                        state[v] = 1;
                        top++;
                        stack[top] = v;
                        edgeIdx[top] = 0;
                    }
                } else {
                    state[u] = 2;
                    order[orderCount++] = u;
                    top--;
                }
            }
        }

        // Reverse finish order to get topological ordering
        int[] reversedOrder = new int[n];
        for (int i = 0; i < n; i++) {
            reversedOrder[i] = order[n - 1 - i];
        }

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("acyclic", true);
        result.put("order", reversedOrder);
        return result;
    }

    /** Whole-graph cycle check and DAG relaxation; return acyclic, distance, parent_edge. */
    static Map<String, Object> dag(Map<String, Object> input) {
        int n = Input.vertexCount(input);
        int source = Input.source(input);
        int[][] edges = Input.edges(input);

        List<List<int[]>> adj = new ArrayList<>(n);
        for (int i = 0; i < n; i++) {
            adj.add(new ArrayList<>());
        }
        for (int i = 0; i < edges.length; i++) {
            adj.get(edges[i][0]).add(new int[]{edges[i][1], edges[i][2], i});
        }

        // Whole graph cycle check and topological sort using three-state DFS
        int[] state = new int[n];
        int[] topo = new int[n];
        int topoCount = 0;

        int[] stack = new int[n];
        int[] edgeIdx = new int[n];

        for (int start = 0; start < n; start++) {
            if (state[start] != 0) {
                continue;
            }
            int top = 0;
            stack[top] = start;
            edgeIdx[top] = 0;
            state[start] = 1;

            while (top >= 0) {
                int u = stack[top];
                int idx = edgeIdx[top];
                List<int[]> neighbors = adj.get(u);
                if (idx < neighbors.size()) {
                    int v = neighbors.get(idx)[0];
                    edgeIdx[top] = idx + 1;
                    if (state[v] == 1) {
                        return Map.of("acyclic", false, "distance", List.of(), "parent_edge", List.of());
                    } else if (state[v] == 0) {
                        state[v] = 1;
                        top++;
                        stack[top] = v;
                        edgeIdx[top] = 0;
                    }
                } else {
                    state[u] = 2;
                    topo[topoCount++] = u;
                    top--;
                }
            }
        }

        // Reverse to get topological order
        int[] topoOrder = new int[n];
        for (int i = 0; i < n; i++) {
            topoOrder[i] = topo[n - 1 - i];
        }

        Long[] distance = new Long[n];
        int[] parentEdge = new int[n];
        Arrays.fill(parentEdge, -1);
        distance[source] = 0L;

        for (int u : topoOrder) {
            if (distance[u] == null) {
                continue;
            }
            long distU = distance[u];
            for (int[] out : adj.get(u)) {
                int v = out[0];
                int w = out[1];
                int edgeId = out[2];
                long cand = distU + w;
                if (distance[v] == null || cand < distance[v]) {
                    distance[v] = cand;
                    parentEdge[v] = edgeId;
                }
            }
        }

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("acyclic", true);
        result.put("distance", distance);
        result.put("parent_edge", parentEdge);
        return result;
    }

    /**
     * Reconstructs the vertex sequence from source to target using parent_edge IDs.
     *
     * @param edges      the original edges array where each row is [u, v, weight]
     * @param source     the source vertex
     * @param target     the target vertex
     * @param parentEdge array of incoming edge IDs on shortest path (-1 if unreachable or source)
     * @return vertex list [source, ..., target] if target is reachable, or null if unreachable
     */
    public static List<Integer> reconstructRoute(int[][] edges, int source, int target, int[] parentEdge) {
        if (target == source) {
            return List.of(source);
        }
        if (parentEdge[target] == -1) {
            return null;
        }

        List<Integer> revPath = new ArrayList<>();
        int curr = target;
        while (curr != source) {
            int pEdge = parentEdge[curr];
            if (pEdge == -1) {
                return null;
            }
            int u = edges[pEdge][0];
            revPath.add(curr);
            curr = u;
        }
        revPath.add(source);

        List<Integer> path = new ArrayList<>(revPath.size());
        for (int i = revPath.size() - 1; i >= 0; i--) {
            path.add(revPath.get(i));
        }
        return path;
    }
}
