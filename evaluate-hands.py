#!/usr/bin/env python3
"""
Bridge Deal Analyzer
--------------------
Reads CSV data (with PBN) from STDIN and performs analysis.
Designed to be piped from bridge_pipe.py.

Usage:
    python3 bridge_pipe.py -n 1000 | python3 analyze_deals.py
"""

import sys
import csv
import argparse

def analyze_stream(input_stream):
    """
    Reads CSV rows from the input stream and analyzes them.
    """
    reader = csv.DictReader(input_stream)
    
    total_hands = 0
    game_makes = 0
    slam_makes = 0
    
    print(f"{'Fit':<5} {'HCP N':<8} {'HCP S':<8} {'Tricks':<8} {'Result'}")
    print("-" * 45)

    for row in reader:
        try:
            fit_len = int(row['fit_len'])
            hcp_n = float(row['hcp_north'])
            hcp_s = float(row['hcp_south'])
            tricks = int(row['tricks_made'])
            
            total_hands += 1
            
            # Example Analysis Logic:
            # Check for Game (10+ tricks in Spades/Hearts usually, simplified here to 10)
            result_str = ""
            if tricks >= 13:
                slam_makes += 1
                result_str = "GRAND SLAM"
            elif tricks >= 12:
                slam_makes += 1
                result_str = "SLAM"
            elif tricks >= 10:
                game_makes += 1
                result_str = "GAME"
            elif tricks < 10 and (hcp_n + hcp_s) > 25:
                 result_str = "GAME FAIL (High HCP)"

            # Print interesting hands only? Or all? 
            # Let's print games/slams to keep output manageable
            if result_str:
                 print(f"{fit_len:<5} {hcp_n:<8} {hcp_s:<8} {tricks:<8} {result_str}")

        except ValueError:
            continue # Skip malformed rows

    print("-" * 45)
    print(f"Total Analyzed: {total_hands}")
    print(f"Games Found:    {game_makes} ({game_makes/total_hands:.1%})")
    print(f"Slams Found:    {slam_makes} ({slam_makes/total_hands:.1%})")

def main():
    parser = argparse.ArgumentParser(description="Analyze Bridge Deals from STDIN")
    # Add arguments here if needed (e.g. --filter-slam)
    args = parser.parse_args()
    
    # Check if data is being piped
    if sys.stdin.isatty():
        print("⚠️  Warning: No input pipe detected. Waiting for CSV input...")
        print("   Usage: python3 bridge_pipe.py | python3 analyze_deals.py")
    
    analyze_stream(sys.stdin)

if __name__ == "__main__":
    main()