"""
Benchmark comparing Kruskal's and Prim's minimum spanning forest algorithms
on identical graphs at three sizes (Small, Medium, Large).
"""

import sys
import time
import random
import statistics
from pathlib import Path

# Add src/Python to path
root_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root_dir / "src" / "Python"))
import algorithms


def generate_graph(n, m, seed=42, min_w=-1000, max_w=1000):
    """
    Generate an undirected graph with n vertices and m edges.
    Guarantees connectivity across random spans and adds random cross edges.
    """
    rng = random.Random(seed)
    edges = []

    # First build a backbone spanning tree if n > 1 to ensure connectivity
    for v in range(1, n):
        u = rng.randint(0, v - 1)
        w = rng.randint(min_w, max_w)
        edges.append([u, v, w])

    # Fill the remaining edges
    remaining = m - len(edges)
    for _ in range(remaining):
        u = rng.randint(0, n - 1)
        v = rng.randint(0, n - 1)
        w = rng.randint(min_w, max_w)
        edges.append([u, v, w])

    return edges


def run_benchmark():
    print("=" * 70)
    print("Kruskal vs. Prim Benchmark on Identical Graphs")
    print("=" * 70)
    print(f"Python: {sys.version.split()[0]} on {sys.platform}")
    print(f"Timer: time.perf_counter (nanosecond resolution)")
    print(f"Timing boundary: Algorithm execution only (excludes graph generation)")
    print("=" * 70)

    sizes = [
        ("Small", 1_000, 3_000, 42),
        ("Medium", 10_000, 30_000, 1337),
        ("Large", 100_000, 250_000, 2026),
    ]

    results = []

    for name, n, m, seed in sizes:
        print(f"\nGenerating graph: {name} (n={n:,}, m={m:,}, seed={seed})...")
        edges = generate_graph(n, m, seed)

        kruskal_req = {"task": "kruskal", "n": n, "edges": edges}
        prim_req = {"task": "prim", "n": n, "edges": edges}

        # Warm-up run for both
        print("  Running warm-up...")
        k_warm = algorithms.kruskal(kruskal_req)
        p_warm = algorithms.prim(prim_req)

        # Verify equivalence and validity
        assert k_warm["cost"] == p_warm["cost"], f"Cost mismatch: {k_warm['cost']} != {p_warm['cost']}"
        assert k_warm["components"] == p_warm["components"], "Component count mismatch"
        assert len(k_warm["edge_ids"]) == n - k_warm["components"], "Kruskal edge count invalid"
        assert len(p_warm["edge_ids"]) == n - p_warm["components"], "Prim edge count invalid"
        print(f"  Warm-up verified: Optimal cost = {k_warm['cost']:,}, Components = {k_warm['components']}")

        # Kruskal timings (at least 3 timings)
        k_times = []
        for trial in range(5):
            t0 = time.perf_counter()
            res = algorithms.kruskal(kruskal_req)
            t1 = time.perf_counter()
            k_times.append(t1 - t0)

        # Prim timings (at least 3 timings)
        p_times = []
        for trial in range(5):
            t0 = time.perf_counter()
            res = algorithms.prim(prim_req)
            t1 = time.perf_counter()
            p_times.append(t1 - t0)

        k_med = statistics.median(k_times)
        p_med = statistics.median(p_times)

        results.append({
            "name": name,
            "n": n,
            "m": m,
            "seed": seed,
            "cost": k_warm["cost"],
            "components": k_warm["components"],
            "k_times": k_times,
            "k_med": k_med,
            "p_times": p_times,
            "p_med": p_med,
        })

        print(f"  Kruskal timings (s): {[round(t, 5) for t in k_times]} -> Median: {k_med:.5f}s")
        print(f"  Prim timings    (s): {[round(t, 5) for t in p_times]} -> Median: {p_med:.5f}s")

    print("\n" + "=" * 70)
    print("SUMMARY TABLE (Markdown format for ANALYSIS.md)")
    print("=" * 70)
    print("| Size | Vertices ($n$) | Edges ($m$) | Method | Timings (s) | Median (s) | Optimal Cost |")
    print("|---|---:|---:|---|---|---:|---:|")
    for r in results:
        k_str = ", ".join(f"{t:.4f}" for t in r["k_times"])
        p_str = ", ".join(f"{t:.4f}" for t in r["p_times"])
        print(f"| {r['name']} | {r['n']:,} | {r['m']:,} | Kruskal | [{k_str}] | **{r['k_med']:.4f}** | {r['cost']:,} |")
        print(f"| {r['name']} | {r['n']:,} | {r['m']:,} | Prim | [{p_str}] | **{r['p_med']:.4f}** | {r['cost']:,} |")

    return results


if __name__ == "__main__":
    run_benchmark()
