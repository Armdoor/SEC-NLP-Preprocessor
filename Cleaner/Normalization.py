
import re
import nltk
from nltk.corpus import stopwords as sp
from nltk.tokenize import word_tokenize as wt 
from nltk.stem import WordNetLemmatizer as wnl
from transformers import BertTokenizer
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')


class Normalizer:

    def __init__(self, text):
        self.text = text


    def clean_text(self, text):
        text = re.sub(r'™', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'[^a-zA-Z0-9\s.,]', '', text)
        return text
    
    def remove_unnecessary_data(self, text):
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'^\w\s.,;:%&@#', '', text)
        text = text.lower()
        return text

    def remove_stopwords(self, text):
        stop_words = set(sp.words('english'))
        w_tokens = wt(text)
        filtered_text = [w for w in w_tokens if w not in stop_words]

        lemmatizer = wnl()
        lemmatized_text = [lemmatizer.lemmatize(word) for word in filtered_text]

        return ' '.join(lemmatized_text)
    
    def run_norm(self, text) :
        text = self.clean_text(text)
        text = self.remove_unnecessary_data(text)
        text = self.remove_stopwords(text)
        return text