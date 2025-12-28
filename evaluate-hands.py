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
from endplay.types import Denom, Player, Deal
import endplay.parsers.pbn as pbn_io

def get_game_result(tricks, strain):
    """
    Determines game or slam success based on strain-specific thresholds.

    Examples:
        >>> get_game_result(13, 'S')
        'GRAND'
        >>> get_game_result(9, 'NT')
        'GAME'
        >>> get_game_result(11, 'C')
        'GAME'
    """
    if tricks == 13: return "GRAND"
    if tricks == 12: return "SMALL"
    
    # NT needs 9, Majors 10, Minors 11
    game_thresholds = {'NT': 9, 'S': 10, 'H': 10, 'D': 11, 'C': 11}
    threshold = game_thresholds.get(strain, 10)
    
    return "GAME" if tricks >= threshold else "PART"

def print_header():
    """Prints the output table header."""
    header = f"{'HCP':<6} | {'NT':<12} | {'S':<12} | {'H':<12} | {'D':<12} | {'C':<12}"
    print(header)
    print("-" * len(header))

def process_boards(boards, batch_size=40):
    """
    Batch solves deals to prevent C++ backend errors.
    Iterates through all 5 strains for each hand.
    """
    if not boards:
        return

    strains = [('NT', Denom.nt), ('S', Denom.spades), ('H', Denom.hearts), 
               ('D', Denom.diamonds), ('C', Denom.clubs)]

    for i in range(0, len(boards), batch_size):
        chunk = boards[i : i + batch_size]
        deals = [b.deal for b in chunk]

        # Parallel solve the safe batch using dds module
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
    """
    parser = argparse.ArgumentParser(description="Evaluate Bridge hands using DDS")
    parser.add_argument("-b", "--batch-size", type=int, default=40,
                        help="Number of hands to process per DDS call")
    parser.add_argument("--test", action="store_true", help="Run internal tests")
    
    parsed_args = parser.parse_args(args)

    if parsed_args.test:
        # Verify internal logic via doctest
        res = doctest.testmod(optionflags=doctest.ELLIPSIS)
        sys.exit(bool(res.failed))

    print_header()

    try:
        # Load and process PBN from STDIN
        boards = pbn_io.load(sys.stdin)
        process_boards(boards, batch_size=parsed_args.batch_size)
    except Exception as e:
        print(f"Error processing PBN: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()