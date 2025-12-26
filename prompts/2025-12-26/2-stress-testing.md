# Milestone: Stress Testing & Batch Stability

- Date: 2025-12-26
- Status: ✅ Green (90% Coverage)
- Hardware: Mac M3 Max

## 1. The 5,000-Hand Challenge

We transitioned from unit testing individual hands to a large-scale
statistical simulation.

- Command: `./generate-hands.py -n 5000 | ./evaluate-hands.py | grep "GAME" | wc -l`
- Result: 658 Games found (~13.2% frequency).

## 2. Engineering Sidebar: The "Invalid Index" Wall

During the stress test, we encountered a critical failure in the underlying
C++ Double Dummy Solver (DDS) library.

- The Symptom: Bus error: 10 or Error: invalid index when processing large PBN
  streams.
- The Root Cause: The DDS C++ backend has internal buffer limits (likely a
  fixed-size table array). Even with the M3 Max's high RAM, the library cannot
  "swallow the whale" of 5,000 hands in a single batch.
- The Fix: Implemented Defensive Batching. We discovered through empirical
  "binary search" testing that a batch size of 40 is the stability sweet spot
  for this environment.
- Implementation: Logic now fences the C++ calls into safe 40-unit increments
   ```python
   for i in range(0, len(boards), batch_size):
       chunk = boards[i : i + batch_size]
       tables = calc_all_tables([b.deal for b in chunk])
   ```

## 3. Findings: The "Power of the Fit"

The simulation revealed several "statistical anomalies" that challenge basic
High Card Point (HCP) theory:

- Minimum Point Game: Successfully made 4 Spades (10 tricks) with only 13.0
  HCP.
- Observation: These sub-20 HCP games were almost exclusively driven by 10+
  card Spade fits.
- The Audit:
   ```
   | Fit | HCP | Tricks | Result | |-----|-----|--------|--------| | 10 | 13.0| 10 | GAME | | 11 | 17.0| 10 | GAME | | 7 | 17.0| 10 | GAME* |
   ```

*The 7-card fit game suggests a highly distributional side-suit or a Double Dummy "perfect play" line.

## 4. Final Pipeline Features

- Parallelization: Utilizes M3 Max performance cores via `calc_all_tables`.
- CLI Flexibility: Added `--batch-size` (default 40) to allow
  hardware-specific tuning.
- Validation: Doctests remain at 90% coverage, verifying the batching and
  logic.
