# Tests and Verification

All test cases, inputs, justified expected outputs, actual outputs, and command guidelines are detailed in [TESTS.md](TESTS.md).

### Quick Commands

```bash
# 1. Transport check
python tools/run.py --setup

# 2. 36 public cases and repeated batch state reset
python tools/run.py --check

# 3. Custom test cases (JSON Lines)
python tools/run.py --input tests/my_cases.jsonl

# 4. Comprehensive test suite (boundaries, route helper, scale limits, witness rejection)
python tests/test_solution.py

# 5. Kruskal vs. Prim empirical benchmark on identical graphs
python tests/benchmark.py
```
