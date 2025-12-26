<a href="./LICENSE.md">
<img src="./images/public-domain.svg" alt="Public Domain"
align="right" width="20%" height="auto"/>
</a>

# Bridge with AI

I am not a data scientist nor an expert in LLM model training nor an expert in
Python libraries.
This repo is me applying LLMs to what user experience might be like when
starting from scratch.
I use the game of [_bridge_](https://en.wikipedia.org/wiki/Contract_bridge) as
an interesting complex domain model.

## Setup

This project uses Python.  You **must** start with setting up your local
session to work with helper libraries for Bridge:

```
# The next step is installing Python 3.13 on a Mac. This does not interfere
# with your your other projets.
$ brew install python3.13  # The libraries do not work (yet) with newer Python
$ python3.13 -m venv .venv  # Lets keep code local and not update your install
$ .venv/bin/activate  # Turn on your setup specific to the current session
$ pip install -r requirements.txt  # Add "endplay" and others here only
```

### Python version

Because of library dependencies, this project is limited to Python 3.13 and
cannot use version 3.14 or later (for now).

## Dealing hands

Use the `[generate-hands.py](./generate-hands.py)` executable script to create
random hands.

## Judging hands

Use `[evaluate-hands.py](./evaluate-hands.py)` in a pipeline from PBN input
such as:
```sh
./generate-hands.py -n 3 | ./evaluate-hands.py  # Just 3-hand demonstration
```

## Development

- Run the `test.sh` script. It:
  - Ensures the venv is used.
  - Builds consolidated coverage across scripts.
  - Shows a summary report.
  - Fails if coverage is too low.
- The `coverage` library is for building and checking test code coverage. It
  is not needed to run the script.

## References

- [PBN 2.1](https://www.tistis.nl/pbn/pbn_v21.txt)
