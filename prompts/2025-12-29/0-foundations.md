# Milestone: The "Foundation" Architecture

**Date:** December 2025 <br>
**Status:** Stable (Green CI) <br>
**Coverage:** 93% Total (96% Gen / 90% Eval) <br>
**Architecture Pattern:** Compiler Pipeline (STDIN/STDOUT) <br>

## 1. Core Philosophy: The "Virtue of Laziness"

The project adheres to a strict "Trunk-Based Development" (TBD) workflow
powered by a high-coverage ratchet. We invest heavily in automated safety nets
(tests/CI) so we can be "lazy" about manual verification and branching
strategies.

* **No Feature Branches:** Commits go directly to `main`.
* **The Ratchet:** `docker-test.sh` enforces a strict 90%+ coverage threshold.
  If a change drops coverage, the build fails.
* **The "Rule of Three":** We deliberately defer abstracting shared logic
  (like CLI parsing) until a third consumer exists to prove the pattern.

## 2. Technical Implementation Details

### A. The "Clever" Two-Phase Argument Parsing

In `generate-hands.py`, we solved the conflict between `argparse` requirements and `doctest` execution using a partial parsing strategy. This allows the script to be tested without triggering the "required argument" error.

```python
# Phase 1: Pre-check for testing flags using sys.argv directly
if "--test" in sys.argv:
    import doctest
    # Run tests and exit immediately, bypassing the main parser
    sys.exit(doctest.testmod(...).failed)

# Phase 2: Full parsing (only runs if we aren't testing)
parser = argparse.ArgumentParser(...)
parser.add_argument("count", type=int, help="Number of hands")
args = parser.parse_args()
```

### B. The "Compiler Stage" Pattern

The pipeline is modeled after a compiler, where each stage consumes a stream
from STDIN and emits a stream to STDOUT.

- Stage 1 (generate-hands.py): Source of Truth. Emits PBN 2.1 stream with rich
  metadata ([Deal], [Vulnerable], [Dealer]).
- Stage 2 (evaluate-hands.py): Analysis. Consumes PBN, calculates Double Dummy
  results using endplay, and emits human-readable tables (currently) or
  augmented PBN (future).

### C. Defensive Batching for M3 Max

To prevent C++ segfaults in the dds library during large simulations on ARM64
architecture, evaluate-hands.py implements chunked processing:

```python
def process_boards(boards, batch_size=40):
    """
    Process deals in safe increments to maintain stability
    in the underlying C++ Double Dummy Solver.
    """
    for i in range(0, len(boards), batch_size):
        chunk = boards[i : i + batch_size]
        # Calculate tables for this chunk only
        # ...
```

## 3. Future Roadmap: Stage 3 (Bidding)

Moving from "Perfect Information" (DDS) to "Imperfect Information" (Bidding)
requires a new architectural stage.

### The Decision Matrix

- Legacy (Wbridge5): High-quality logic but technically brittle (Windows
  executable, requires Wine/VM). Status: Rejected for pipeline simplicity.
- Modern (BEN): Python-native, Tensorflow-based, M3 Max compatible. Status:
  Preferred Candidate.

### Data Contract Evolution

To support a 3-stage pipeline, the data format between stages must evolve from
"Text Table" to structured data.
