#!/usr/bin/env python3
"""
Bridge Deal Evaluator
Analyzes PBN deals from STDIN and calculates Double Dummy results in parallel.
Discovered stability limit for DDS C++ backend is ~40 deals per batch.
"""

import sys
import argparse
import doctest
from endplay.dds import calc_all_tables
from endplay.evaluate import hcp
from endplay.types import Denom, Player
import endplay.parsers.pbn as pbn_io

def get_stats(deal, table):
    """
    Calculates stats for a deal using a pre-computed DD table.

    Examples:
        >>> from endplay.types import Deal
        >>> from endplay.dds import calc_dd_table
        >>> d = Deal("N:974.AJ3.63.AK963 K83.K9752.7.8752 AQJ5.T864.KJ94.4 T62.Q.AQT852.QJT")
        >>> t = calc_dd_table(d)
        >>> s = get_stats(d, t)
        >>> s['tricks']
        9
    """
    tricks = table[Denom.spades, Player.north]
    fit_len = len(deal.north.spades) + len(deal.south.spades)
    hcp_total = float(hcp(deal.north) + hcp(deal.south))
    return {'fit': fit_len, 'hcp': hcp_total, 'tricks': tricks}

def get_game_result(stats):
    """
    Determines game success or failure.

    Examples:
        >>> get_game_result({'tricks': 10, 'hcp': 20})
        'GAME'
        >>> get_game_result({'tricks': 8, 'hcp': 25})
        'FAIL (High HCP)'
    """
    if stats['tricks'] >= 10:
        return "GAME"
    if stats['hcp'] >= 25:
        return "FAIL (High HCP)"
    return ""

def print_header():
    """
    Prints the table header.

    >>> print_header()
    Fit    HCP      Tricks   Result
    -------------------------------
    """
    header = f"{'Fit':<6} {'HCP':<8} {'Tricks':<8} {'Result'}"
    print(header)
    print("-" * len(header))

def process_boards(boards, batch_size=40):
    """
    Batch solves deals in library-safe increments.
    Prevents 'Invalid Index' or 'Too many tables' errors in DDS.

    Examples:
        >>> process_boards([])
        >>> from endplay.parsers import pbn
        >>> p_str = '[Deal "N:974.AJ3.63.AK963 K83.K9752.7.8752 AQJ5.T864.KJ94.4 T62.Q.AQT852.QJT"]'
        >>> process_boards(pbn.loads(p_str), batch_size=1)
        7      23.0     9...
    """
    if not boards:
        return

    # Process in safe chunks to respect C++ library limits
    for i in range(0, len(boards), batch_size):
        chunk = boards[i : i + batch_size]
        deals = [b.deal for b in chunk]

        # Parallel solve the safe batch
        tables = calc_all_tables(deals)

        for board, table in zip(chunk, tables):
            stats = get_stats(board.deal, table)
            result_tag = get_game_result(stats)
            print(f"{stats['fit']:<6} {stats['hcp']:<8.1f} {stats['tricks']:<8} {result_tag}")

def main():
    parser = argparse.ArgumentParser(
        description="Evaluate Bridge Deals from STDIN (Parallel)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--batch-size",
        help="Process deals N at a time to avoid internal errors",
        default=40,
        metavar='N',
        type=int,
    )
    parser.add_argument(
        "--test",
        help="Run internal tests",
        action="store_true",
    )
    args = parser.parse_args()

    if args.test:
        from endplay.types import Deal, Board
        # Use ELLIPSIS to ignore the trailing whitespace in column-formatted output
        res = doctest.testmod(
            verbose=True,
            optionflags=doctest.ELLIPSIS,
            extraglobs={'Deal': Deal, 'Board': Board, 'Denom': Denom, 'Player': Player}
        )
        sys.exit(bool(res.failed))

    print_header()

    try:
        # Load all boards from stdin PBN stream
        boards = pbn_io.load(sys.stdin)
        process_boards(boards, batch_size=args.batch_size)
    except Exception as e:
        print(f"Error processing PBN stream: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
