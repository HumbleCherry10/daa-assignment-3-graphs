"""
Comprehensive test suite verifying correctness, edge cases, deep chains,
scale limits, route reconstruction, and non-unique answer checking
(including alternative valid answers and invalid witnesses).
"""

import sys
from pathlib import Path

# Add src/Python and tools to path
root_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root_dir / "src" / "Python"))
sys.path.insert(0, str(root_dir / "tools"))

import algorithms
import public_validate


def test_route_reconstruction_helper():
    print("Testing Route-Reconstruction Helper...")

    # Graph with diamond and parallel edges:
    # 0 -> 1 (w=3, edge 0)
    # 0 -> 2 (w=8, edge 1)
    # 1 -> 2 (w=-7, edge 2)
    # 2 -> 3 (w=4, edge 3)
    # 0 -> 1 (w=3, edge 4, parallel)
    # 4 is isolated (unreachable)
    edges = [
        [0, 1, 3],   # 0
        [0, 2, 8],   # 1
        [1, 2, -7],  # 2
        [2, 3, 4],   # 3
        [0, 1, 3],   # 4 (parallel to 0)
    ]
    n = 5
    source = 0
    dag_res = algorithms.dag({"task": "dag", "n": n, "source": source, "edges": edges})
    assert dag_res["acyclic"] is True
    parent_edge = dag_res["parent_edge"]
    distance = dag_res["distance"]

    # 1. Reachable target: target = 3
    route_3 = algorithms.reconstruct_route(edges, source, 3, parent_edge)
    assert route_3 == [0, 1, 2, 3], f"Expected [0, 1, 2, 3], got {route_3}"
    # Verify weight
    path_weight = 0
    for i in range(len(route_3) - 1):
        u, v = route_3[i], route_3[i + 1]
        # find weight of parent edge used
        p_edge = parent_edge[v]
        assert edges[p_edge][0] == u and edges[p_edge][1] == v
        path_weight += edges[p_edge][2]
    assert path_weight == distance[3] == 0, f"Path weight mismatch: {path_weight} != {distance[3]}"
    print("  [PASS] Reachable target (target=3): route =", route_3, "cost =", path_weight)

    # 2. Source target: target = source
    route_source = algorithms.reconstruct_route(edges, source, source, parent_edge)
    assert route_source == [source], f"Expected [{source}], got {route_source}"
    print("  [PASS] Source target (target=0): route =", route_source)

    # 3. Unreachable target: target = 4
    route_unreachable = algorithms.reconstruct_route(edges, source, 4, parent_edge)
    assert route_unreachable is None, f"Expected None for unreachable target, got {route_unreachable}"
    print("  [PASS] Unreachable target (target=4): route = None")

    # 4. Tied / parallel edges:
    # Graph where 0 -> 1 has two tied parallel edges (IDs 0 and 1)
    # and two paths to 2 of equal weight: 0->1->2 (cost 1+1=2) and 0->2 (cost 2)
    tied_edges = [
        [0, 1, 1],  # 0
        [0, 1, 1],  # 1 (parallel tied)
        [1, 2, 1],  # 2
        [0, 2, 2],  # 3 (tied route)
    ]
    tied_dag = algorithms.dag({"task": "dag", "n": 3, "source": 0, "edges": tied_edges})
    tied_route = algorithms.reconstruct_route(tied_edges, 0, 2, tied_dag["parent_edge"])
    # Either [0, 1, 2] or [0, 2] is optimal with cost 2
    assert tied_route in ([0, 1, 2], [0, 2]), f"Unexpected route: {tied_route}"
    # Verify cost equals distance[2]
    calc_cost = 0
    for i in range(len(tied_route) - 1):
        u, v = tied_route[i], tied_route[i + 1]
        p_edge = tied_dag["parent_edge"][v]
        assert tied_edges[p_edge][0] == u and tied_edges[p_edge][1] == v
        calc_cost += tied_edges[p_edge][2]
    assert calc_cost == tied_dag["distance"][2] == 2
    print("  [PASS] Tied/parallel edges (target=2): route =", tied_route, "cost =", calc_cost)


def test_non_unique_answers_and_witness_validation():
    print("\nTesting Semantic Validity and Invalid Witness Rejection...")

    # --- MSF (Kruskal & Prim): Triangle with tied weights of 1 ---
    # Triangle: 0-1 (w=1, id 0), 1-2 (w=1, id 1), 0-2 (w=1, id 2)
    # Three valid spanning trees: [0, 1], [1, 2], [0, 2], all cost 2.
    req_msf = {"task": "kruskal", "n": 3, "edges": [[0, 1, 1], [1, 2, 1], [0, 2, 1]]}
    expected_msf = {"cost": 2, "edge_ids": [0, 1], "components": 1}

    # Our algorithm output
    actual_k = algorithms.kruskal(req_msf)
    assert public_validate.check(req_msf, actual_k, expected_msf)
    print("  [PASS] MSF algorithm output validated")

    # Alternative valid answer: edge_ids = [1, 2]
    alt_valid_msf = {"cost": 2, "edge_ids": [1, 2], "components": 1}
    assert public_validate.check(req_msf, alt_valid_msf, expected_msf)
    print("  [PASS] MSF alternative valid answer [1, 2] accepted")

    # Invalid witness 1: contains cycle [0, 1, 2]
    inv_cycle_msf = {"cost": 3, "edge_ids": [0, 1, 2], "components": 1}
    assert not public_validate.check(req_msf, inv_cycle_msf, expected_msf)
    print("  [PASS] MSF invalid witness (contains cycle) correctly rejected")

    # Invalid witness 2: disconnected / missing edge [0]
    inv_disc_msf = {"cost": 1, "edge_ids": [0], "components": 1}
    assert not public_validate.check(req_msf, inv_disc_msf, expected_msf)
    print("  [PASS] MSF invalid witness (missing edge) correctly rejected")

    # --- SCC (Kosaraju): Two SCCs {0, 1} and {2} ---
    req_scc = {"task": "scc", "n": 3, "edges": [[0, 1], [1, 0], [1, 2]]}
    expected_scc = {"component": [0, 0, 1], "condensation": [[0, 1]]}

    actual_scc = algorithms.scc(req_scc)
    assert public_validate.check(req_scc, actual_scc, expected_scc)
    print("  [PASS] SCC algorithm output validated")

    # Alternative valid answer: labels [10, 10, 20], condensation [[10, 20]]
    alt_valid_scc = {"component": [10, 10, 20], "condensation": [[10, 20]]}
    assert public_validate.check(req_scc, alt_valid_scc, expected_scc)
    print("  [PASS] SCC alternative valid labels [10, 10, 20] accepted")

    # Invalid witness 1: wrongly merges vertex 2 into SCC 0
    inv_merged_scc = {"component": [0, 0, 0], "condensation": []}
    assert not public_validate.check(req_scc, inv_merged_scc, expected_scc)
    print("  [PASS] SCC invalid witness (falsely merged component) correctly rejected")

    # Invalid witness 2: falsely splits vertices 0 and 1
    inv_split_scc = {"component": [0, 1, 2], "condensation": [[0, 1], [1, 0], [1, 2]]}
    assert not public_validate.check(req_scc, inv_split_scc, expected_scc)
    print("  [PASS] SCC invalid witness (falsely split component) correctly rejected")

    # --- Topo: Diamond DAG (0->1, 0->2, 1->3, 2->3) ---
    req_topo = {"task": "topo", "n": 4, "edges": [[0, 1], [0, 2], [1, 3], [2, 3]]}
    expected_topo = {"acyclic": True, "order": [0, 1, 2, 3]}

    actual_topo = algorithms.topo(req_topo)
    assert public_validate.check(req_topo, actual_topo, expected_topo)
    print("  [PASS] Topo algorithm output validated")

    # Alternative valid answer: [0, 2, 1, 3]
    alt_valid_topo = {"acyclic": True, "order": [0, 2, 1, 3]}
    assert public_validate.check(req_topo, alt_valid_topo, expected_topo)
    print("  [PASS] Topo alternative valid order [0, 2, 1, 3] accepted")

    # Invalid witness: back-edge violation [3, 0, 1, 2]
    inv_topo = {"acyclic": True, "order": [3, 0, 1, 2]}
    assert not public_validate.check(req_topo, inv_topo, expected_topo)
    print("  [PASS] Topo invalid witness (back-edge violation) correctly rejected")

    # --- DAG: Tied routes ---
    # 0 -> 1 (w=2, id 0)
    # 0 -> 2 (w=1, id 1)
    # 2 -> 1 (w=1, id 2)  (cost 0->2->1 is 1+1=2, tied with 0->1)
    req_dag = {"task": "dag", "n": 3, "source": 0, "edges": [[0, 1, 2], [0, 2, 1], [2, 1, 1]]}
    expected_dag = {"acyclic": True, "distance": [0, 2, 1], "parent_edge": [-1, 2, 1]}

    actual_dag = algorithms.dag(req_dag)
    assert public_validate.check(req_dag, actual_dag, expected_dag)
    print("  [PASS] DAG algorithm output validated")

    # Alternative valid parent: parent_edge for vertex 1 is 0 (direct edge [0, 1, 2])
    alt_dag = {"acyclic": True, "distance": [0, 2, 1], "parent_edge": [-1, 0, 1]}
    assert public_validate.check(req_dag, alt_dag, expected_dag)
    print("  [PASS] DAG alternative valid parent edge accepted")

    # Invalid witness: parent_edge on vertex 1 pointing to non-optimal edge or cycle
    inv_dag = {"acyclic": True, "distance": [0, 2, 1], "parent_edge": [-1, -1, 1]}
    assert not public_validate.check(req_dag, inv_dag, expected_dag)
    print("  [PASS] DAG invalid parent_edge witness correctly rejected")


def test_deep_chains_and_scale():
    print("\nTesting Deep Chains (n=100,000) and Scale Limits...")
    n_deep = 100_000
    chain_edges = [[i, i + 1] for i in range(n_deep - 1)]

    # DSU deep chain operations
    dsu_req = {"task": "dsu", "n": n_deep, "operations": chain_edges}
    dsu_res = algorithms.dsu(dsu_req)
    assert len(dsu_res["states"]) == n_deep - 1
    assert dsu_res["states"][-1] == [1, n_deep]
    print(f"  [PASS] DSU on chain of {n_deep:,} vertices: components=1, largest={n_deep:,}")

    # Topo deep chain
    topo_req = {"task": "topo", "n": n_deep, "edges": chain_edges}
    topo_res = algorithms.topo(topo_req)
    assert topo_res["acyclic"] is True
    assert len(topo_res["order"]) == n_deep
    assert topo_res["order"][0] == 0 and topo_res["order"][-1] == n_deep - 1
    print(f"  [PASS] Topo on deep chain of {n_deep:,} vertices: acyclic=True")

    # Kosaraju SCC deep chain
    scc_req = {"task": "scc", "n": n_deep, "edges": chain_edges}
    scc_res = algorithms.scc(scc_req)
    assert len(scc_res["component"]) == n_deep
    assert len(scc_res["condensation"]) == n_deep - 1
    print(f"  [PASS] Kosaraju SCC on deep chain of {n_deep:,} vertices: {len(scc_res['condensation']):,} condensation edges")

    # DAG deep chain with weights
    dag_edges = [[i, i + 1, 1] for i in range(n_deep - 1)]
    dag_req = {"task": "dag", "n": n_deep, "source": 0, "edges": dag_edges}
    dag_res = algorithms.dag(dag_req)
    assert dag_res["acyclic"] is True
    assert dag_res["distance"][-1] == n_deep - 1
    print(f"  [PASS] DAG shortest paths on deep chain of {n_deep:,} vertices: distance={n_deep - 1:,}")


def main():
    test_route_reconstruction_helper()
    test_non_unique_answers_and_witness_validation()
    test_deep_chains_and_scale()
    print("\n" + "=" * 50)
    print("ALL TESTS PASSED SUCCESSFULLY!")
    print("=" * 50)


if __name__ == "__main__":
    main()
