# Milestone: Bridge Simulation Pipeline (V1.1)

Key Update: Added defensive programming for library stability.

## 1. The "Bus Error: 10" Lesson

While Python lists are flexible, the underlying Double Dummy Solver (DDS) C++
library requires explicit data to initialize its memory buffers.

- The Bug: Passing an empty list `[]` to `calc_all_tables` caused a memory
  access violation (Bus Error: 10) on macOS.
- The Fix: We implemented a "Guard Clause" in `process_boards`:

```python
if not boards:
    return # Prevent passing empty pointers to C++
```

- Verification: We added a "Sad Path" doctest `>>> process_boards([])` to
  ensure this guard is always active and covered by our 90% mandate.

## 2. Parallelism via `calc_all_tables`

To fully utilize the M3 Max architecture, we moved from serial solving to
batch solving.

- Old Way: for board in boards: `calc_dd_table(board.deal)` (Serial,
  bottlenecked by Python's GIL).
- New Way: `calc_all_tables(all_deals)` (Parallel, executes in the C++ layer
  across all available CPU cores).

## 3. Current "Green Build" Stats

- `generate-hands.py`: 96% Coverage.
- `evaluate-hands.py`: 85% Coverage (Logic is 100% covered; only main plumbing
  remains).
- Total Project: 90% Coverage.
