#!/usr/bin/env python3
"""
Bridge Simulation Pipeline
--------------------------
Generates random deals and solves for tricks.
Designed for Unix piping: Data -> STDOUT, Logs -> STDERR.

Requirements:
    pip install endplay tqdm
"""

import multiprocessing
import random
import time
import csv
import sys
import argparse
import doctest
from tqdm import tqdm

# Imports (Fail fast if missing)
from endplay.types import Deal, Player
from endplay.dds import calc_dd_table
from endplay.evaluate import hcp

# CONSTANTS
RANKS = "23456789TJQKA"

def log(msg):
    """
    Writes metadata/logs to STDERR so it doesn't pollute the data pipe.
    
    Args:
        msg (str): The message to log.
    """
    sys.stderr.write(f"{msg}\n")
    sys.stderr.flush()

def generate_random_deal():
    """
    Creates a Deal object with a random distribution of cards via PBN string.
    
    Returns:
        endplay.types.Deal: A randomized bridge deal.
    
    Examples:
        >>> random.seed(42)
        >>> deal = generate_random_deal()
        >>> isinstance(deal, Deal)
        True
        >>> str(deal).startswith("N:")
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
        
    full_pbn = f"N:{' '.join(hands_pbn)}"
    deal = Deal(full_pbn)
    deal.first = Player.south
    return deal

def worker_task(batch_size):
    """
    Worker process: Generates 'batch_size' hands and solves them.
    Returns list of result dicts.
    """
    results = []
    random.seed()
    
    error_count = 0
    
    for _ in range(batch_size):
        try:
            deal = generate_random_deal()
            
            ns_spades = len(deal.north.spades) + len(deal.south.spades)

            # SOLVE: Double Dummy Analysis
            table = calc_dd_table(deal)
            
            # API FIX 1: Use to_list() to get a standard 5x4 matrix
            # Avoids API ambiguities with Enums
            # [Strain][Player]: 3=Spades, 0=North
            table_data = table.to_list()
            tricks = table_data[3][0] 
            
            # API FIX 2: Use evaluate.hcp() function
            points_north = hcp(deal.north)
            points_south = hcp(deal.south)
            
            results.append({
                "pbn": str(deal),
                "fit_len": ns_spades,
                "hcp_north": points_north,
                "hcp_south": points_south,
                "tricks_made": tricks
            })

        except Exception as e:
            # FORCE PRINT to STDERR to bypass tqdm
            if error_count == 0:
                print(f"CRITICAL WORKER FAILURE: {e}", file=sys.stderr)
                # Debug aid: What did we get?
                try:
                    print(f"DEBUG Table Type: {type(table)}", file=sys.stderr)
                except:
                    pass
            error_count += 1
            continue    
            
    return results

# --- DEFAULTS ---
DEFAULT_DEALS = 1_000_000
DEFAULT_BATCH_SIZE = 5_000
# NB: Even with smart OS scheduling, do not request more cores than
# needed by the UI and by Python itself.
DEFAULT_WORKERS = max(1, multiprocessing.cpu_count() - 2)

def parse_arguments():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Bridge Deal Simulation Pipeline",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument("-n", "--deals", type=int, 
                        default=DEFAULT_DEALS,
                        help="Total deals to generate")
    
    parser.add_argument("--batch-size", type=int, 
                        default=DEFAULT_BATCH_SIZE, 
                        help="(internal) Deals per batch")
    
    parser.add_argument("--workers", type=int, 
                        default=DEFAULT_WORKERS, 
                        help="(internal) Worker processes")
    
    parser.add_argument("--test", action="store_true", 
                        help="Run internal doctests and exit")
    
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    # --- TEST MODE ---
    if args.test:
        print("Running internal tests (doctest)...")
        result = doctest.testmod(verbose=True)
        if result.failed == 0:
            print("✅ All tests passed!")
            sys.exit(0)
        else:
            print("❌ Tests failed.")
            sys.exit(1)

    # --- SIMULATION MODE ---
    log(f"--- BRIDGE SIMULATION PIPE ---")
    log(f"Workers: {args.workers}")
    log(f"Target: {args.deals:,} deals")
    log(f"Batch Size: {args.batch_size:,}")
    log("-" * 30)

    if args.deals < args.batch_size:
        tasks = [args.deals]
        num_tasks = 1
    else:
        num_tasks = args.deals // args.batch_size
        tasks = [args.batch_size] * num_tasks
        remainder = args.deals % args.batch_size
        if remainder > 0:
            tasks.append(remainder)
            num_tasks += 1
    
    start_time = time.time()
    total_matches = 0
    
    # Header now includes 'pbn'
    header = ["pbn", "fit_len", "hcp_north", "hcp_south", "tricks_made"]
    writer = csv.DictWriter(sys.stdout, fieldnames=header)
    writer.writeheader()
    
    with multiprocessing.Pool(processes=args.workers) as pool:
        iterator = pool.imap_unordered(worker_task, tasks)
        for batch_results in tqdm(iterator, total=num_tasks, unit="batch", file=sys.stderr):
            for row in batch_results:
                writer.writerow(row)
                total_matches += 1
            sys.stdout.flush()
    
    duration = time.time() - start_time
    
    log("-" * 30)
    log(f"✅ DONE in {duration:.2f} seconds.")
    log(f"Hands Output: {total_matches:,}")
    
    if total_matches == 0 and args.deals > 0:
        sys.stderr.write("❌ FAILURE: No deals processed successfully.\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
