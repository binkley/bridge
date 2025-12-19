#!/usr/bin/env python3
"""
Bridge Deal Generator
Outputs PBN hands to STDOUT for piping.

Examples:
    >>> random.seed(42)
    >>> pbn = generate_pbn()
    >>> pbn.startswith("N:")
    True
    >>> len(pbn.split()) == 4
    True
"""
import random
import sys
import csv
import argparse
import doctest

RANKS = "23456789TJQKA"

def generate_pbn():
    """
    Generates a random PBN string.
    """
    deck = list(range(52))
    random.shuffle(deck)
    hands_pbn = []
    for i in range(4):
        hand_indices = deck[i*13 : (i+1)*13]
        suits_held = [[], [], [], []] 
        for card_idx in hand_indices:
            suit = card_idx // 13
            rank = card_idx % 13
            suits_held[suit].append(rank)
        pbn_hand_parts = []
        for s in [3, 2, 1, 0]: # S, H, D, C
            ranks_held = sorted(suits_held[s], reverse=True)
            rank_str = "".join([RANKS[r] for r in ranks_held])
            pbn_hand_parts.append(rank_str)
        hands_pbn.append(".".join(pbn_hand_parts))
    return f"N:{' '.join(hands_pbn)}"

def main():
    parser = argparse.ArgumentParser(
        description="Bridge Deal Generator",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-n", "--count",
        type=int,
        help="generate N random deals in PBN format",
        metavar="N",
        default=1000
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="run tests for developers"
    )
    args = parser.parse_args()

    if args.test:
        import doctest
        doctest.testmod(verbose=True)
        sys.exit(0)

    writer = csv.DictWriter(sys.stdout, fieldnames=["pbn"], quoting=csv.QUOTE_NONNUMERIC)
    writer.writeheader()
    for _ in range(args.count):
        writer.writerow({"pbn": generate_pbn()})

if __name__ == "__main__":
    main()
