# data_loader.py
import pandas as pd
from datasets import Dataset, DatasetDict
from transformers import pipeline
from config import PRETRAINED_MODEL, PSEUDO_LABEL_THRESHOLD
from Cleaner.insert_data import Importer

LABEL2ID = {"positive": 0, "neutral": 1, "negative": 2}

def load_8k_dataset():
    # 1) fetch raw descriptions
    imp = Importer()
    texts = imp.get_all_item_descriptions()
    df = pd.DataFrame({"text": texts})

    # 2) pseudo‑label with FinBERT
    classifier = pipeline(
        "sentiment-analysis",
        model=PRETRAINED_MODEL,
        tokenizer=PRETRAINED_MODEL,
        return_all_scores=False,
        device=0  # or -1 if no GPU
    )
    results = classifier(df["text"].tolist(), batch_size=16)

    # 3) unpack label + score, filter
    df["label"] = [LABEL2ID[r["label"].lower()] for r in results]
    df["score"] = [r["score"] for r in results]
    df = df[df["score"] >= PSEUDO_LABEL_THRESHOLD].reset_index(drop=True)

    # 4) train/test split
    ds = Dataset.from_pandas(df[["text","label"]])
    split = ds.train_test_split(test_size=0.1, seed=42)

    return DatasetDict({
        "train": split["train"],
        "eval":  split["test"]
    })
