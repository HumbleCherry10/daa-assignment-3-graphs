# Test Suite Documentation

**Student Name:** Dias Tursynbay  
**Student ID:** 230107000  
**Language:** Python 3.12+ (Python 3.14.3 tested; Java 17 also supported)  
**Test File:** `tests/my_cases.jsonl`  
**Automated Runner:** `tests/test_solution.py`  
**Benchmark Script:** `tests/benchmark.py`  

---

## 1. Test Execution Commands

```bash
# 1. Transport check
python tools/run.py --setup

# 2. Public test cases (36 tests + repeated batch state reset)
python tools/run.py --check

# 3. Custom test cases (JSON Lines output)
python tools/run.py --input tests/my_cases.jsonl

# 4. Comprehensive test suite (boundaries, witnesses, route helper, scale)
python tests/test_solution.py

# 5. Kruskal vs. Prim benchmark (3 sizes, 5 runs each, medians)
python tests/benchmark.py
```

---

## 2. Test Cases in `tests/my_cases.jsonl`

### DSU (Disjoint Set Union)
1. **Case 1: Empty graph boundary**
   - **Input:** `{"task":"dsu","n":0,"operations":[]}`
   - **Justification:** $n=0$ has no vertices; operations list is empty. By specification, returns empty states array.
   - **Expected:** `{"states":[]}`
   - **Actual:** `{"states":[]}`

2. **Case 2: Singleton with self-union**
   - **Input:** `{"task":"dsu","n":1,"operations":[[0,0]]}`
   - **Justification:** $n=1$ starts with 1 component of size 1. Self-union `[0,0]` finds both roots equal; partition does not change.
   - **Expected:** `{"states":[[1,1]]}`
   - **Actual:** `{"states":[[1,1]]}`

3. **Case 3: Redundant, self, and cross unions**
   - **Input:** `{"task":"dsu","n":4,"operations":[[0,1],[1,0],[0,1],[2,3],[0,2],[1,3]]}`
   - **Justification:**
     - `[0,1]`: joins {0} and {1} $\to$ 3 components, largest 2.
     - `[1,0]`: already united $\to$ 3 components, largest 2.
     - `[0,1]`: duplicate operation $\to$ 3 components, largest 2.
     - `[2,3]`: joins {2} and {3} $\to$ 2 components, largest 2.
     - `[0,2]`: joins {0,1} and {2,3} $\to$ 1 component, largest 4.
     - `[1,3]`: already connected in {0,1,2,3} $\to$ 1 component, largest 4.
   - **Expected:** `{"states":[[3,2],[3,2],[3,2],[2,2],[1,4],[1,4]]}`
   - **Actual:** `{"states":[[3,2],[3,2],[3,2],[2,2],[1,4],[1,4]]}`

4. **Case 4: Multi-cluster progressive merge**
   - **Input:** `{"task":"dsu","n":6,"operations":[[0,1],[2,3],[4,5],[1,3],[3,5],[0,4]]}`
   - **Justification:** Merges pairs into 3 components of size 2, then into size 4 and 2, then single component of size 6.
   - **Expected:** `{"states":[[5,2],[4,2],[3,2],[2,4],[1,6],[1,6]]}`
   - **Actual:** `{"states":[[5,2],[4,2],[3,2],[2,4],[1,6],[1,6]]}`

---

### Kruskal & Prim (Minimum Spanning Forest)
5. **Case 5: Kruskal empty graph**
   - **Input:** `{"task":"kruskal","n":0,"edges":[]}`
   - **Justification:** $n=0$ contains 0 components and 0 edges. Cost is 0.
   - **Expected:** `{"cost":0,"edge_ids":[],"components":0}`
   - **Actual:** `{"cost":0,"edge_ids":[],"components":0}`

6. **Case 6: Kruskal singleton with self-loop**
   - **Input:** `{"task":"kruskal","n":1,"edges":[[0,0,100]]}`
   - **Justification:** Self-loop cannot be selected; isolated vertex forms 1 component.
   - **Expected:** `{"cost":0,"edge_ids":[],"components":1}`
   - **Actual:** `{"cost":0,"edge_ids":[],"components":1}`

7. **Case 7: Kruskal negative weights, self-loops, and parallel edges**
   - **Input:** `{"task":"kruskal","n":4,"edges":[[0,0,-50],[0,1,10],[0,1,-5],[1,2,3],[2,3,-10],[3,3,20]]}`
   - **Justification:**
     - Discard self-loops: edge 0 `[0,0,-50]` and edge 5 `[3,3,20]`.
     - Between 0 and 1, select lighter parallel edge 2 (weight -5).
     - Select edge 4 `[2,3,-10]` (weight -10).
     - Select edge 3 `[1,2,3]` (weight 3).
     - Spans all 4 vertices into 1 component. Total cost: $-5 + 3 + (-10) = -12$.
   - **Expected:** `{"cost":-12,"edge_ids":[4,2,3],"components":1}` (edge order may vary)
   - **Actual:** `{"cost":-12,"edge_ids":[4,2,3],"components":1}`

8. **Case 8: Kruskal tied optima**
   - **Input:** `{"task":"kruskal","n":3,"edges":[[0,1,5],[1,2,5],[0,2,5]]}`
   - **Justification:** Triangle with equal edge weights 5. Any 2 edges form a spanning tree of cost 10.
   - **Expected:** `{"cost":10,"edge_ids":[0,1],"components":1}` (or any 2 edges)
   - **Actual:** `{"cost":10,"edge_ids":[0,1],"components":1}`

9. **Case 9: Kruskal 64-bit sum**
   - **Input:** `{"task":"kruskal","n":4,"edges":[[0,1,1500000000],[1,2,1500000000],[2,3,1500000000]]}`
   - **Justification:** Total cost $3 \times 1.5 \times 10^9 = 4,500,000,000 > 2^{31}-1$. Validates 64-bit integer handling.
   - **Expected:** `{"cost":4500000000,"edge_ids":[0,1,2],"components":1}`
   - **Actual:** `{"cost":4500000000,"edge_ids":[0,1,2],"components":1}`

10. **Case 10: Prim empty graph**
    - **Input:** `{"task":"prim","n":0,"edges":[]}`
    - **Expected:** `{"cost":0,"edge_ids":[],"components":0}`
    - **Actual:** `{"cost":0,"edge_ids":[],"components":0}`

11. **Case 11: Prim singleton with self-loop**
    - **Input:** `{"task":"prim","n":1,"edges":[[0,0,100]]}`
    - **Expected:** `{"cost":0,"edge_ids":[],"components":1}`
    - **Actual:** `{"cost":0,"edge_ids":[],"components":1}`

12. **Case 12: Prim negative weights and parallel edges**
    - **Input:** `{"task":"prim","n":4,"edges":[[0,0,-50],[0,1,10],[0,1,-5],[1,2,3],[2,3,-10],[3,3,20]]}`
    - **Expected:** `{"cost":-12,"edge_ids":[2,3,4],"components":1}`
    - **Actual:** `{"cost":-12,"edge_ids":[2,3,4],"components":1}`

13. **Case 13: Prim tied optima**
    - **Input:** `{"task":"prim","n":3,"edges":[[0,1,5],[1,2,5],[0,2,5]]}`
    - **Expected:** `{"cost":10,"edge_ids":[0,1],"components":1}`
    - **Actual:** `{"cost":10,"edge_ids":[0,1],"components":1}`

14. **Case 14: Prim disconnected forest with isolates**
    - **Input:** `{"task":"prim","n":5,"edges":[[0,1,-2],[2,3,4]]}`
    - **Justification:** Components are {0,1}, {2,3}, and isolate {4}. 3 components, 2 edges, cost 2.
    - **Expected:** `{"cost":2,"edge_ids":[0,1],"components":3}`
    - **Actual:** `{"cost":2,"edge_ids":[0,1],"components":3}`

15. **Case 15: Prim 64-bit sum**
    - **Input:** `{"task":"prim","n":4,"edges":[[0,1,1500000000],[1,2,1500000000],[2,3,1500000000]]}`
    - **Expected:** `{"cost":4500000000,"edge_ids":[0,1,2],"components":1}`
    - **Actual:** `{"cost":4500000000,"edge_ids":[0,1,2],"components":1}`

---

### Kosaraju SCC
16. **Case 16: SCC empty graph**
    - **Input:** `{"task":"scc","n":0,"edges":[]}`
    - **Expected:** `{"component":[],"condensation":[]}`
    - **Actual:** `{"component":[],"condensation":[]}`

17. **Case 17: SCC isolated vertices**
    - **Input:** `{"task":"scc","n":3,"edges":[]}`
    - **Justification:** Every isolated vertex is in its own SCC. Condensation has no cross-component edges.
    - **Expected:** 3 distinct component labels, `condensation=[]`.
    - **Actual:** `{"component":[2,1,0],"condensation":[]}`

18. **Case 18: SCC self-loops and parallel edges**
    - **Input:** `{"task":"scc","n":3,"edges":[[0,0],[0,1],[0,1],[1,0],[1,2]]}`
    - **Justification:** {0, 1} form an SCC; {2} is another SCC. Edge $1 \to 2$ connects the two SCCs.
    - **Expected:** `labels[0] == labels[1] != labels[2]`, condensation has 1 edge.
    - **Actual:** `{"component":[0,0,1],"condensation":[[0,1]]}`

19. **Case 19: SCC two 3-cycles connected by bridge**
    - **Input:** `{"task":"scc","n":6,"edges":[[0,1],[1,2],[2,0],[2,3],[3,4],[4,5],[5,3]]}`
    - **Justification:** SCC A is {0,1,2}, SCC B is {3,4,5}. Cross-component edge $2 \to 3$ yields 1 condensation edge.
    - **Expected:** `labels[0]==labels[1]==labels[2]`, `labels[3]==labels[4]==labels[5]`, condensation `[[cA, cB]]`.
    - **Actual:** `{"component":[0,0,0,1,1,1],"condensation":[[0,1]]}`

---

### DFS Topological Ordering
20. **Case 20: Topo empty graph**
    - **Input:** `{"task":"topo","n":0,"edges":[]}`
    - **Expected:** `{"acyclic":true,"order":[]}`
    - **Actual:** `{"acyclic":true,"order":[]}`

21. **Case 21: Topo singleton**
    - **Input:** `{"task":"topo","n":1,"edges":[]}`
    - **Expected:** `{"acyclic":true,"order":[0]}`
    - **Actual:** `{"acyclic":true,"order":[0]}`

22. **Case 22: Topo self-loop cycle**
    - **Input:** `{"task":"topo","n":2,"edges":[[0,1],[1,1]]}`
    - **Justification:** Vertex 1 has self-loop $[1,1]$, forming a cycle. Must return `acyclic=false, order=[]`.
    - **Expected:** `{"acyclic":false,"order":[]}`
    - **Actual:** `{"acyclic":false,"order":[]}`

23. **Case 23: Topo diamond DAG**
    - **Input:** `{"task":"topo","n":4,"edges":[[0,1],[0,2],[1,3],[2,3]]}`
    - **Justification:** Vertex 0 must precede 1 and 2; both must precede 3. Valid orders: `[0, 1, 2, 3]` or `[0, 2, 1, 3]`.
    - **Expected:** `acyclic=true`, valid order.
    - **Actual:** `{"acyclic":true,"order":[0,2,1,3]}`

24. **Case 24: Topo disconnected cycle**
    - **Input:** `{"task":"topo","n":5,"edges":[[0,1],[1,2],[3,4],[4,3]]}`
    - **Justification:** Component {3,4} contains cycle $3 \leftrightarrow 4$. Whole graph is cyclic.
    - **Expected:** `{"acyclic":false,"order":[]}`
    - **Actual:** `{"acyclic":false,"order":[]}`

---

### DAG Shortest Paths
25. **Case 25: DAG singleton**
    - **Input:** `{"task":"dag","n":1,"source":0,"edges":[]}`
    - **Expected:** `{"acyclic":true,"distance":[0],"parent_edge":[-1]}`
    - **Actual:** `{"acyclic":true,"distance":[0],"parent_edge":[-1]}`

26. **Case 26: DAG unreachable vertices**
    - **Input:** `{"task":"dag","n":4,"source":0,"edges":[[0,1,5],[2,3,4]]}`
    - **Justification:** Vertices 2 and 3 are unreachable from source 0. Distance must be `null`, parent `-1`.
    - **Expected:** `{"acyclic":true,"distance":[0,5,null,null],"parent_edge":[-1,0,-1,-1]}`
    - **Actual:** `{"acyclic":true,"distance":[0,5,null,null],"parent_edge":[-1,0,-1,-1]}`

27. **Case 27: DAG negative weights and path relaxation**
    - **Input:** `{"task":"dag","n":4,"source":0,"edges":[[0,1,10],[0,2,5],[2,1,-3],[1,3,2],[2,3,4]]}`
    - **Justification:**
      - Path $0 \to 1$ cost 10; path $0 \to 2 \to 1$ cost $5 + (-3) = 2$. Optimal to 1 is 2 (parent edge 2).
      - Path to 3: via 1 is $2 + 2 = 4$; via 2 is $5 + 4 = 9$. Optimal to 3 is 4 (parent edge 3).
    - **Expected:** `{"acyclic":true,"distance":[0,2,5,4],"parent_edge":[-1,2,1,3]}`
    - **Actual:** `{"acyclic":true,"distance":[0,2,5,4],"parent_edge":[-1,2,1,3]}`

28. **Case 28: DAG cycle unreachable from source**
    - **Input:** `{"task":"dag","n":5,"source":0,"edges":[[0,1,10],[2,3,1],[3,4,1],[4,2,1]]}`
    - **Justification:** Disconnected component {2,3,4} forms directed cycle $2 \to 3 \to 4 \to 2$. By specification, graph is cyclic: return `acyclic=false, distance=[], parent_edge=[]`.
    - **Expected:** `{"acyclic":false,"distance":[],"parent_edge":[]}`
    - **Actual:** `{"acyclic":false,"distance":[],"parent_edge":[]}`

29. **Case 29: DAG parallel edges with different and tied weights**
    - **Input:** `{"task":"dag","n":4,"source":0,"edges":[[0,1,5],[0,1,2],[1,2,3],[1,2,1],[2,3,4],[2,3,4]]}`
    - **Justification:** Selects lighter parallel edges: edge 1 (cost 2) over edge 0 (cost 5), edge 3 (cost 1) over edge 2 (cost 3).
    - **Expected:** `{"acyclic":true,"distance":[0,2,3,7],"parent_edge":[-1,1,3,4]}`
    - **Actual:** `{"acyclic":true,"distance":[0,2,3,7],"parent_edge":[-1,1,3,4]}`

30. **Case 30: DAG 64-bit distances**
    - **Input:** `{"task":"dag","n":4,"source":0,"edges":[[0,1,1500000000],[1,2,1500000000],[2,3,1500000000]]}`
    - **Justification:** Distance to vertex 3 is $4,500,000,000 > 2^{31}-1$.
    - **Expected:** `{"acyclic":true,"distance":[0,1500000000,3000000000,4500000000],"parent_edge":[-1,0,1,2]}`
    - **Actual:** `{"acyclic":true,"distance":[0,1500000000,3000000000,4500000000],"parent_edge":[-1,0,1,2]}`
