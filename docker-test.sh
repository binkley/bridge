#!/usr/bin/env bash
# Exit immediately if any command fails

set -euo pipefail

# Assumes Python 3.13 because of C++ depencencies

python3 -m coverage erase
python3 -m coverage run -a --source=. generate-hands.py --test
python3 -m coverage run -a --source=. evaluate-hands.py --test

echo
echo ">>> Coverage Report"
echo "--------------------------------------"
python3 -m coverage report --show-missing --fail-under=100
