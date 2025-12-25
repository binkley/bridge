#!/usr/bin/env python3
"""
Bridge Deal Evaluator
Analyzes PBN deals from STDIN and calculates Double Dummy results.

Examples:
    >>> from endplay.types import Deal
    >>> # Example of a thin 4S game
    >>> d = Deal("N:KQ9864.J52.J9.A7 T52.AK73.KQ6.986 A.QT986.AT75.JT5 J73.4.8432.KQ432")
    >>> stats = get_stats(d)
    >>> stats['tricks']
    10
    >>> stats['fit']
    7
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
    # table.to_list() returns [NT, S, H, D, C] for [N, S, E, W]
    # Spades is index 1, North is index 0
    tricks = table.to_list()[1][0]
    
    fit_len = len(deal.north.spades) + len(deal.south.spades)
    hcp_total = hcp(deal.north) + hcp(deal.south)
    
    return {
        'fit': fit_len,
        'hcp': hcp_total,
        'tricks': tricks
    }

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
    parser.add_argument(
        "-l", "--limit", 
        type=int, 
        help="Limit evaluation to the first L boards"
    )
    parser.add_argument(
        "--quiet", 
        action="store_true", 
        help="Suppress header and formatting"
    )
    args = parser.parse_args()

    if args.test:
        from endplay.types import Deal
        doctest.testmod(verbose=True, extraglobs={'Deal': Deal})
        sys.exit(0)

    if not args.quiet:
        print(f"{'Fit':<6} {'HCP':<8} {'Tricks':<8} {'Result'}")
        print("-" * 35)

    try:
        # Load the PBN stream from STDIN
        boards = pbn_io.load(sys.stdin)
        
        for i, board in enumerate(boards):
            if args.limit and i >= args.limit:
                break
                
            stats = get_stats(board.deal)
            
            res = "GAME" if stats['tricks'] >= 10 else ""
            if not res and stats['hcp'] >= 25:
                res = "FAIL (High HCP)"

            print(f"{stats['fit']:<6} {stats['hcp']:<8.1f} {stats['tricks']:<8} {res}")

    except Exception as e:
        print(f"Error processing PBN stream: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()