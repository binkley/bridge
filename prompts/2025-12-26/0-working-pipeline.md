# Milestone: Bridge Simulation Pipeline (V1.0)

Date: 2025.12.26 Status: Functional / End-to-End Verified Architecture:
Unix-style Pipeline (`generate` | `evaluate`)

## 1. Overview

This project implements a bridge hand analysis pipeline using the endplay
library. It focuses on high-performance simulation and verifiable logic
through strict 90%+ code coverage.

## 2. Component: generate-hands.py

Generates random deals and outputs them in PBN 2.1 compliant format.

- Verification: Explicitly sets the "Big Seven" mandatory PBN tags to avoid
  parser ambiguity.
- Key Fix: Uses `board_num` integer assignment to prevent ValueError: invalid
  literal for int() with base 10: 'None' in downstream consumers.
- Coverage: 90% via doctest.

## 3. Component: evaluate-hands.py

Consumes PBN deals from STDIN and calculates Double Dummy Solver (DDS)
statistics.

- Logic: Calculates North-South Spade fit, combined HCP, and max tricks for
  Spades played by North.
- Key Fix: Uses semantic indexing (table[Denom.spades, Player.north]) to
  ensure library-agnostic results.
- Coverage Strategy: Includes doctests for both DDS calculation and game-logic
  branching (GAME vs FAIL).

## 4. Engineering Standards: The "Ratchet"

We maintain a strict "Green Build" policy via a centralized test runner.

`test.sh` <br>
A fail-fast bash script that orchestrates the audit trail.

```bash
set -e
python3 -m coverage run ... generate-hands.py --test
python3 -m coverage run ... evaluate-hands.py --test
python3 -m coverage report --fail-under=90
```

- Fail-Fast: Scripts explicitly sys.exit(1) on doctest failure to ensure set
  -e halts the pipeline immediately.
- Validation: Uses coverage to ensure that no "plausible AI code" enters the
  repo without execution verification.

## 5. Current Performance & Logic Baseline

- HCP Calculation: Verified at 23.0 for the test hand.
- DDS Result: Verified at 9 tricks for the test hand in the current environment.
- Throughput: Single-threaded processing (M3 Max performance optimization pending).

---

## Audit Trail Note

The conversation history has moved from implementation (shuffling logic/PBN
formatting) to architecture (pipeline flow/test-driven refactoring). Future
sessions should use this markdown to re-establish the "Green Build" baseline
before attempting performance scaling.
