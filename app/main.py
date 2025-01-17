from model import load_model
from dataset import prepare_dataset
from training import fine_tune_model

def main():
    # Load the model
    model, tokenizer = load_model()

    # Prepare the dataset
    train_dataset, val_dataset = prepare_dataset(tokenizer)

    # Fine-tune the model
    fine_tune_model(model, tokenizer, train_dataset, val_dataset)

if __name__ == "__main__":
    main()
