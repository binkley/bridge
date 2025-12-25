#!/usr/bin/env python3
"""
Bridge Deal Generator
Outputs fully valid PBN deals to STDOUT using endplay v0.5.12.

Examples:
    >>> import random
    >>> random.seed(42)
    >>> pbn = generate_pbn_string()
    >>> pbn.startswith("N:")
    True
"""
import random
import sys
import argparse
import doctest
from endplay.types import Deal, Board
import endplay.parsers.pbn as pbn_io

RANKS = "23456789TJQKA"

def generate_pbn_string():
    """Manual shuffle for card data (v0.5.12 compatible)."""
    deck = list(range(52))
    random.shuffle(deck)
    hands_pbn = []
    for i in range(4):
        h = deck[i*13 : (i+1)*13]
        s_held = [sorted([c%13 for c in h if c//13 == s], reverse=True) for s in [3,2,1,0]]
        hands_pbn.append(".".join("".join(RANKS[r] for r in suit) for suit in s_held))
    return f"N:{' '.join(hands_pbn)}"

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-n", "--count", type=int, default=1000, metavar="N")
    parser.add_argument("--test", action="store_true", help="run doctests")
    args = parser.parse_args()

    if args.test:
        doctest.testmod(verbose=True)
        sys.exit(0)

    # Wrap deals in Boards with valid numeric metadata
    boards = []
    for i in range(args.count):
        b = Board(Deal(generate_pbn_string()))
        b.info["Board"] = str(i + 1)
        boards.append(b)
    
    pbn_io.dump(boards, sys.stdout)

if __name__ == "__main__":
    main()
