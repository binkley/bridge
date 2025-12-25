#!/usr/bin/env python3
"""
Bridge Deal Generator
Outputs fully valid, populated PBN deals to STDOUT using endplay v0.5.12.
"""
import random
import sys
import argparse
import doctest

try:
    from endplay.types import Deal, Board
    import endplay.parsers.pbn as pbn_io
except ImportError as e:
    print(f"Error: Required library missing ({e}).", file=sys.stderr)
    sys.exit(1)

RANKS = "23456789TJQKA"

def generate_pbn_string():
    """
    Generates a random PBN string using manual shuffling logic.
    This ensures the Deal object is populated regardless of library version.
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

def generate_board():
    """
    1. Generates a populated PBN string.
    2. Creates a Deal object from that string.
    3. Wraps the Deal in a Board to satisfy the 'info' requirement.
    """
    pbn_str = generate_pbn_string()
    deal = Deal(pbn_str)
    return Board(deal)

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
        help="run tests"
    )
    args = parser.parse_args()

    if args.test:
        doctest.testmod(verbose=True)
        sys.exit(0)

    # Use a generator to create populated boards
    boards = (generate_board() for _ in range(args.count))
    
    # Dump to STDOUT
    pbn_io.dump(boards, sys.stdout)

if __name__ == "__main__":
    main()