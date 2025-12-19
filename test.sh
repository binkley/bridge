#!/usr/bin/env bash

source .venv/bin/activate

python3 -m coverage erase
echo "Running random-hands.py tests..."
python3 -m coverage run -a --source=. \
    --omit=evaluate-hands.py \
    random-hands.py --test
# TODO: After working on the new script
if false; then
    echo "Running evaluate-hands.py tests..."
    python3 -m coverage run -a --source=. evaluate-hands.py
fi
echo "--------------------------------------"
python3 -m coverage report --fail-under=90
