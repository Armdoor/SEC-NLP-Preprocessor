from tokenizer import preprocess_text
from model import AIModel
from sentiment_analysis import analyze_sentiment

# Input text for testing
input_text = "Once upon a time in a faraway land, there was a brave knight."

# Preprocess text
processed_text = preprocess_text(input_text)
print(f"Processed Text: {' '.join(processed_text)}")

# Initialize the AI model
model = AIModel()

# Generate text using the model
generated_text = model.generate_text(" ".join(processed_text))
print(f"Generated Text: {generated_text}")

# Optionally, analyze sentiment of the generated text
sentiment = analyze_sentiment(generated_text)
print(f"Sentiment: {sentiment}")
