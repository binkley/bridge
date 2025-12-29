#!/usr/bin/env python3
"""
Bridge Deal Evaluator
Analyzes PBN deals from STDIN and calculates Double Dummy results in parallel.
Uses defensive batching (~40 deals) for DDS C++ stability on ARM64/M3.
"""

import sys
import argparse
import doctest
import os
import endplay.dds as dds
from endplay.evaluate import hcp
from endplay.types import Denom, Player
import endplay.parsers.pbn as pbn_io

def get_game_result(tricks, strain):
    """
    Determines game or slam success based on strain-specific thresholds.

    Examples:
        >>> get_game_result(9, 'NT')
        'GAME'
        >>> get_game_result(11, 'C')
        'GAME'
    """
    if tricks == 13: return "GRAND"
    if tricks == 12: return "SMALL"
    game_thresholds = {'NT': 9, 'S': 10, 'H': 10, 'D': 11, 'C': 11}
    threshold = game_thresholds.get(strain, 10)
    return "GAME" if tricks >= threshold else "PART"

def print_header():
    """Prints the output table header."""
    header = f"{'HCP':<6} | {'NT':<12} | {'S':<12} | {'H':<12} | {'D':<12} | {'C':<12}"
    print(header)
    print("-" * len(header))

def process_boards(boards, batch_size=40):
    """Batch solves deals in library-safe increments."""
    if not boards:
        return

    strains = [('NT', Denom.nt), ('S', Denom.spades), ('H', Denom.hearts),
               ('D', Denom.diamonds), ('C', Denom.clubs)]

    for i in range(0, len(boards), batch_size):
        chunk = boards[i : i + batch_size]
        deals = [b.deal for b in chunk]
        tables = dds.calc_all_tables(deals)

        for board, table in zip(chunk, tables):
            hcp_total = float(hcp(board.deal.north) + hcp(board.deal.south))
            results = [f"{hcp_total:<6.1f}"]
            for label, denom in strains:
                tricks = table[denom, Player.north]
                marker = get_game_result(tricks, label)
                results.append(f"{marker:<5} ({tricks:>2})")
            print(" | ".join(results))

def main(args=None):
    """
    Main entry point for hand evaluation.

    Examples:
        >>> import os, sys
        >>> from io import StringIO
        >>> old_argv, old_stdin = sys.argv, sys.stdin
        >>> # 1. Test Help
        >>> sys.argv = [os.path.basename(__file__), "--help"]
        >>> try:
        ...     main()
        ... except SystemExit:
        ...     pass
        usage: evaluate-hands.py [-h] [-b N] [--test]
        ...
        >>> # 2. Integration Test with PBN 2.1 stream
        >>> pbn_input = (
        ...     '[Event "Simulation"]\\n'
        ...     '[Board "1"]\\n'
        ...     '[Deal "N:974.AJ3.63.AK963 K83.K9752.7.8752 AQJ5.T864.KJ94.4 T62.Q.AQT852.QJT"]\\n\\n'
        ... )
        >>> sys.stdin = StringIO(pbn_input)
        >>> sys.argv = [os.path.basename(__file__), "--batch-size", "1"]
        >>> main() # doctest: +NORMALIZE_WHITESPACE
        HCP    | NT           | S            | H            | D            | C
        ---------------------------------------------------------------------------------
        23.0   | GAME  ( 9) | PART  ( 9) | PART  ( 8) | PART  ( 8) | PART  ( 8)
        >>> sys.stdin, sys.argv = old_stdin, old_argv
    """
    parser = argparse.ArgumentParser(
        description="Evaluate Bridge hands using DDS",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("-b", "--batch-size", default=40, metavar='N', type=int,
                        help="Process deals N at a time to avoid internal errors")
    parser.add_argument("--test", action="store_true", help="Run internal tests")

    parsed_args = parser.parse_args(args)

    if parsed_args.test:
        # Restore verbose=True to see the "Test passed" output
        res = doctest.testmod(verbose=True, optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
        sys.exit(bool(res.failed))

    # Only print headers and process if we aren't in test mode
    print_header()

    try:
        boards = pbn_io.load(sys.stdin)
        process_boards(boards, batch_size=parsed_args.batch_size)
    except Exception as e:
        # Avoid crashing on empty stdin during simple runs
        if "empty" not in str(e).lower():
            print(f"Error processing PBN: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()
