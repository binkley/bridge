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

This project uses Python.
This is a common choice by experts in AI/LLM/ML work.
Assuming Python, Conda is a common choice for managing libraries.

### Use Conda

[Install
Conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html)
for setting up your Python environment.

From your command line:
```bash
conda env create --file environment.yml
conda activate bridge
```

When you edit [`environment.yml`](./environment.yml), update with:
```bash
conda env update
```

## Training

Follow along with [How to Train an LLM with
PyTorch](https://www.datacamp.com/tutorial/how-to-train-a-llm-with-pytorch).
