#!/usr/bin/env python

import torch
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from trl import SFTTrainer

def train(path):
    """Return the trained dataset.

    >>> train('data/tatsu-lab/alpacka')
    """
    from datasets import load_dataset
    return load_dataset(path, split='train')

if __name__ == '__main__':
    import doctest
    doctest.testmod()
