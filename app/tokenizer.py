"""
Text Preprocessing and Tokenization
Purpose:
This file contains the functions for preprocessing and tokenizing the input text. 
In Natural Language Processing (NLP), tokenization is the process of splitting text into individual units (tokens), 
like words or subwords. It helps the model understand and work with the text efficiently.

Concept:

Tokenization is the first step before passing the text to a model for any NLP task.
This file would typically use libraries like SpaCy to clean and break down text into manageable pieces, 
removing stopwords (commonly used words like “the”, “a”, “is”) to help the model focus on important words.
"""

import spacy

# Load spaCy's small English model
nlp = spacy.load("en_core_web_sm")

def preprocess_text(text):
    """Tokenize and remove stopwords from input text."""
    doc = nlp(text)
    return [token.text for token in doc if not token.is_stop]