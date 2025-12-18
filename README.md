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

The initial data for setup comes from
[_alpaca_](https://huggingface.co/datasets/tatsu-lab/alpaca/tree/main/data).

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

## Dealing hands

Use the `[random-hands.py](./random-hands.py)` executable script to create
random hands.

## Training

Follow along with [How to Train an LLM with
PyTorch](https://www.datacamp.com/tutorial/how-to-train-a-llm-with-pytorch).
