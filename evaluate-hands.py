#!/usr/bin/env python3
"""
Bridge Deal Evaluator
Analyzes PBN deals from STDIN and calculates Double Dummy results.

Examples:
    >>> from endplay.types import Deal
    >>> # Example hand from endplay tutorial
    >>> d = Deal("N:974.AJ3.63.AK963 K83.K9752.7.8752 AQJ5.T864.KJ94.4 T62.Q.AQT852.QJT")
    >>> s = get_stats(d)
    >>> s['hcp']
    22
    >>> s['tricks']
    6
"""

import sys
import argparse
import doctest
from endplay.dds import calc_dd_table
from endplay.evaluate import hcp
import endplay.parsers.pbn as pbn_io

def get_stats(deal):
    """
    Calculates double dummy tricks for Spades (North),
    combined North-South HCP, and Spade fit length.
    """
    table = calc_dd_table(deal)
    # endplay table.to_list() order: [Clubs, Diamonds, Hearts, Spades, NoTrump]
    # Spades is index 3, North is index 0
    tricks = table.to_list()[3][0]

    fit_len = len(deal.north.spades) + len(deal.south.spades)
    hcp_total = hcp(deal.north) + hcp(deal.south)

    return {
        'fit': fit_len,
        'hcp': hcp_total,
        'tricks': tricks
    }

def format_result(stats):
    """
    Returns a formatted string row with results and game analysis.

    Examples:
        >>> format_result({'fit': 8, 'hcp': 26, 'tricks': 11})
        '8      26.0     11       GAME'
        >>> format_result({'fit': 7, 'hcp': 25, 'tricks': 8})
        '7      25.0     8        FAIL (High HCP)'
    """
    res = "GAME" if stats['tricks'] >= 10 else ""
    if not res and stats['hcp'] >= 25:
        res = "FAIL (High HCP)"

    return f"{stats['fit']:<6} {stats['hcp']:<8.1f} {stats['tricks']:<8} {res}".strip()

def main():
    parser = argparse.ArgumentParser(
        description="Evaluate Bridge Deals from STDIN",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run doctests and exit"
    )
    args = parser.parse_args()

    if args.test:
        from endplay.types import Deal
        doctest.testmod(verbose=True, extraglobs={'Deal': Deal})
        sys.exit(0)

    print(f"{'Fit':<6} {'HCP':<8} {'Tricks':<8} {'Result'}")
    print("-" * 35)

    try:
        # pbn_io.load consumes the entire STDIN stream
        boards = pbn_io.load(sys.stdin)
        for board in boards:
            stats = get_stats(board.deal)
            print(format_result(stats))

    except Exception as e:
        print(f"Error processing PBN stream: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
