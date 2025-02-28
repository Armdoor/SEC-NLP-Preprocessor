'''
Sentences that contained any of the following non-GAAP measures were then extracted, using a Python script: 
 - Revised Net Income 
 - Earnings Before Interest and Taxes (EBIT) 
 - Earnings Before Interest, Taxes, and Depreciation (EBITDA) 
 - Earnings Before Interest, Taxes, Depreciation, Amortization, and Rent/Restructuring (EBITDAR) 
 - Adjusted Earnings Per Share 
 - Free Cash Flow (FCF) 
 - Core Earnings 
 - Funds From Operations (FFO) 
 - Unbilled Revenue
 - Return on Capital Employed (ROCE) 
 - Non-GAAP 
 - Reconciliation

'''
import re
import nltk
from nltk.corpus import stopwords as sp
from nltk.tokenize import word_tokenize as wt 
from nltk.stem import WordNetLemmatizer as wnl
from transformers import BertTokenizer
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
# nltk.download('')



class TokenizeData():

    def __init__(self, path):
        self.path = path 
        with open(self.path, 'r') as file:
            self.text = file.read()
        
    def remove_unnecessary_data(self, text):
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s.,;:%&$@#]', '', text)
        text = text.lower()
        return text

    def remove_stopwords(self, text):
        stop_words = set(sp.words('english'))
        w_tokens = wt(text)
        filtered_text = [w for w in w_tokens if w not in stop_words]

        lemmatizer = wnl()
        lemmatized_text = [lemmatizer.lemmatize(word) for word in filtered_text]

        return ' '.join(lemmatized_text)
    
path ='/Users/akshitsanoria/Desktop/PythonP/printing_files/item1.txt'
data = TokenizeData(path)
c_text = data.remove_unnecessary_data(data.text)
cleaned_text = data.remove_stopwords(c_text)

# with open('/Users/akshitsanoria/Desktop/PythonP/printing_files/cleaned_item1.txt', 'w') as file:
#     file.write(cleaned_text)    

# tokenize the text 
tokenizer = BertTokenizer.from_pretrained('yiyanghkust/finbert-pretrain')
tokens = tokenizer(cleaned_text, padding=True, truncation=True, return_tensors="pt")

input_ids = tokens['input_ids']
attention_mask = tokens['attention_mask']

print(input_ids)
print(attention_mask)
