#!/usr/bin/env python3
"""
Bridge Deal Generator
Outputs PBN 2.1 compliant deals to STDOUT using endplay v0.5.12.
Requires an explicit count of deals to generate.
"""

import argparse
import doctest
import random
import sys
import os
from datetime import date
from endplay.types import Board, Deal, Denom, Player
import endplay.parsers.pbn as pbn_io

# Rank constants for manual PBN string generation
RANKS = "23456789TJQKA"

def generate_pbn_string():
    """
    Manual shuffle to ensure card data is populated and correctly formatted.

    Examples:
        >>> import random
        >>> random.seed(42)
        >>> pbn = generate_pbn_string()
        >>> pbn.startswith("N:")
        True
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

def generate_boards(count):
    """
    Generator that yields Board objects with mandatory PBN 2.1 metadata.

    Examples:
        >>> import random
        >>> random.seed(42)
        >>> boards = list(generate_boards(2))
        >>> len(boards)
        2
        >>> boards[0].board_num
        1
        >>> boards[1].info["Event"]
        'Simulation'
    """
    today = date.today().strftime("%Y.%m.%d")
    for i in range(count):
        deal = Deal(generate_pbn_string())
        board = Board(deal)
        board.board_num = i + 1

        # Mandatory PBN 2.1 Tags restored
        board.info.update({
            "Event": "Simulation",
            "Site": "Local Machine",
            "Date": today,
            "West": "Robot", "North": "Robot",
            "East": "Robot", "South": "Robot",
            "Dealer": "N", "Vulnerable": "None", "Scoring": "Rubber"
        })
        yield board

def main(args=None):
    """
    Main entry point for deal generation. [cite: 3]

    Examples:
        >>> import os, sys
        >>> from io import StringIO
        >>> old_argv = sys.argv

        >>> # 1. Test missing argument (Should exit with error)
        >>> sys.argv = [os.path.basename(__file__)]
        >>> try:
        ...     main()
        ... except SystemExit as e:
        ...     exit_code = e.code
        >>> exit_code > 0
        True

        >>> # 2. Test Help Text
        >>> sys.argv = [os.path.basename(__file__), "--help"]
        >>> try:
        ...     main()
        ... except SystemExit:
        ...     pass
        usage: generate-hands.py [-h] [--test] count
        ...
        positional arguments:
          count       Number of deals to generate
        ...

        >>> # 3. Happy path
        >>> sys.argv = [os.path.basename(__file__), "1"]
        >>> main()
        % PBN 2.1
        ...

        >>> sys.argv = old_argv
    """
    test_parser = argparse.ArgumentParser(add_help=False)
    test_parser.add_argument("--test", action="store_true")
    test_args, remaining = test_parser.parse_known_args(args)

    if test_args.test:
        # Extraglobs restored to ensure doctests have access to types
        res = doctest.testmod(verbose=True, optionflags=doctest.ELLIPSIS, extraglobs={
            'Deal': Deal, 'Board': Board, 'Denom': Denom, 'Player': Player
        })
        sys.exit(bool(res.failed))

    parser = argparse.ArgumentParser(
        description="Generate Bridge Deals in PBN format",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    # Mandatary positional argument [cite: 3]
    parser.add_argument(
        "count",
        type=int,
        help="Number of deals to generate"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run internal tests"
    )

    parsed_args = parser.parse_args(remaining)

    # Convert generator to list for pbn_io.dump to ensure valid PBN file structure
    boards = list(generate_boards(parsed_args.count))
    pbn_io.dump(boards, sys.stdout)

if __name__ == "__main__":
    main()
