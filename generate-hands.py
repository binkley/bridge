#!/usr/bin/env python3
"""
Bridge Deal Generator
Outputs PBN 2.1 compliant deals to STDOUT using endplay v0.5.12.

Examples:
    >>> import random
    >>> random.seed(42)
    >>> pbn = generate_pbn_string()
    >>> pbn.startswith("N:")
    True
    >>> boards = list(generate_boards(2))
    >>> len(boards)
    2
    >>> boards[0].board_num
    1
    >>> boards[1].info["Event"]
    'Simulation'
"""

import random
import sys
import argparse
import doctest
from datetime import date
from endplay.types import Board, Deal, Denom, Player
import endplay.parsers.pbn as pbn_io

RANKS = "23456789TJQKA"

def generate_pbn_string():
    """Manual shuffle to ensure card data is populated."""
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

def generate_boards(count):
    """
    Generator that yields Board objects with mandatory PBN 2.1 metadata.

    Examples:
        >>> import random
        >>> random.seed(42)
        >>> boards = generate_boards(2)
        >>> b1 = next(boards)
        >>> b1.board_num
        1
        >>> b1.info["Event"]
        'Simulation'
        >>> b1.info["Dealer"]
        'N'
        >>> # Verify the second board increments correctly
        >>> b2 = next(boards)
        >>> b2.board_num
        2
        >>> # Ensure cards were actually generated (not empty)
        >>> str(b2.deal).startswith("N:")
        True
    """
    today = date.today().strftime("%Y.%m.%d")
    for i in range(count):
        deal = Deal(generate_pbn_string())
        board = Board(deal)
        board.board_num = i + 1

        # Mandatory PBN 2.1 Tags
        board.info.update({
            "Event": "Simulation",
            "Site": "Local Machine",
            "Date": today,
            "West": "Robot", "North": "Robot",
            "East": "Robot", "South": "Robot",
            "Dealer": "N", "Vulnerable": "None", "Scoring": "Rubber"
        })
        yield board

def main():
    parser = argparse.ArgumentParser(
        description="Generate Bridge Deals in PBN format",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-n", "--count",
        help="Generate N deals",
        default=10,
        metavar="N",
        type=int,
    )
    parser.add_argument(
        "--test",
        help="Run internal tests",
        action="store_true",
    )
    args = parser.parse_args()

    if args.test:
        # Capture the named tuple (failed, attempted)
        results = doctest.testmod(verbose=True, extraglobs={
            'Deal': Deal,
            'Board': Board,
            'Denom': Denom,
            'Player': Player
        })
        sys.exit(bool(results.failed))

    # Convert generator to list for the pbn_io.dump function
    boards = list(generate_boards(args.count))
    pbn_io.dump(boards, sys.stdout)

if __name__ == "__main__":
    main()
