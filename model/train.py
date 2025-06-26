# train.py
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from data_loader import load_8k_dataset
from config import PRETRAINED_MODEL, OUTPUT_DIR, NUM_EPOCHS, BATCH_SIZE, MAX_LEN

def tokenize(batch):
    return tokenizer(
        batch["text"],
        truncation=True,
        padding="max_length",
        max_length=MAX_LEN
    )

if __name__ == "__main__":
    # 1) load model + tokenizer
    tokenizer = AutoTokenizer.from_pretrained(PRETRAINED_MODEL)
    model     = AutoModelForSequenceClassification.from_pretrained(
                    PRETRAINED_MODEL,
                    num_labels=3
                )

    # 2) load & tokenize
    ds = load_8k_dataset()
    ds = ds.map(tokenize, batched=True)
    ds.set_format("torch", ["input_ids","attention_mask","label"])

    # 3) setup Trainer
    args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=NUM_EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE*2,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        logging_steps=50,
    )
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=ds["train"],
        eval_dataset= ds["eval"],
        tokenizer=tokenizer,
        compute_metrics=lambda p: {
            "accuracy": (p.predictions.argmax(-1) == p.label_ids).mean()
        }
    )

    # 4) train & save
    trainer.train()
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
