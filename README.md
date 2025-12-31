<a href="./LICENSE.md">
<img src="./images/cc0.svg" alt="Creative Commons Public Domain Dedication"
align="right" width="10%" height="auto"/>
</a>

# Bridge with AI

[![build](https://github.com/binkley/bridge/actions/workflows/ci.yml/badge.svg)](https://github.com/binkley/bridge/actions)
[![pull requests](https://img.shields.io/github/issues-pr/binkley/bridge.svg)](https://github.com/binkley/bridge/pulls)
[![issues](https://img.shields.io/github/issues/binkley/bridge.svg)](https://github.com/binkley/bridge/issues)
[![vulnerabilities](https://snyk.io/test/github/binkley/bridge/badge.svg)](https://snyk.io/test/github/binkley/bridge)
[![license](https://img.shields.io/badge/License-CC0_1.0-lightgrey.svg)](http://creativecommons.org/publicdomain/zero/1.0/)

I am not a data scientist, an expert in LLM model training, nor an expert in
Python libraries. This repo is an exploration of applying LLMs to a complex
domain model from scratch.

I use the game of [_bridge_](https://en.wikipedia.org/wiki/Contract_bridge) as
the domain model.

## Setup

This project requires **Python 3.11** to match the CI environment and ensure
compatibility with the `endplay` (DDS) library.

```bash
# Install Python 3.11 (Mac example)
$ brew install python@3.11

# Set up the local virtual environment
$python3.11 -m venv .venv$ source .venv/bin/activate

# Install dependencies
$ pip install -r requirements.txt
```

## Python Version Note

Because of specific C++ library dependencies for the Double Dummy Solver
(DDS), this project is currently pinned to Python 3.11. Newer versions (3.12+)
may cause instability or build failures.

## Usage

The primary entry point is the [./bridge.sh](./bridge.sh) orchestrator. Try
`./bridge.sh --help` for a list of commands.

### 1. Dealing Hands

Use the generate subcommand (or the underlying script) to create PBN hands.
This requires a mandatory count argument.

```bash
# Generate 10 hands to STDOUT
$ ./bridge.sh generate 10

# Or invoke the script directly
$ ./generate-hands.py 10
```

### 2. Judging Hands (Pipeline)

Use the evaluate-hands.py script to analyze deals. It reads PBN data from
input and prints out a table.

```bash
# Generate 3 hands and evaluate them immediately
$ ./generate-hands.py 3 | ./evaluate-hands.py
```

## Development

The project uses a containerized workflow to ensure that local development and
GitHub actions work the same.

- Run Tests: `./bridge.sh test`
  Runs inside a Docker container (Python 3.11 / Debian Bookworm).
- Records coverage.
- Fails if coverage drops below 90%.

## References

- [PBN 2.1 Specification](https://www.tistis.nl/pbn/pbn_v21.txt)
- [Blue Chip Bridge Table Manager Protocol](https://web.archive.org/web/20210514012054/https://www.bluechipbridge.co.uk/protocol.htm) &mdash; this is
  challenging to track down; the link is to the Wayback Machine, the original
  having turned into squatter spam.
  [bcb-table-manager-protocol.md](./bcb-table-manager-protocol.md) is a
  porting of this link contents to Markdown.
