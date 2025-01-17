# import our libraries
import re
import requests
import unicodedata
from bs4 import BeautifulSoup

# link = "https://www.sec.gov/Archives/edgar/data/1166036/000110465904027382/0001104659-04-027382.txt"
# response = requests.get(link)

# # pass it through the parser, in this case let's just use lxml because the tags seem to follow xml.
# soup = BeautifulSoup(response.content, 'xml')
doc = "/Users/akshitsanoria/Desktop/PythonP/data/Apple Inc./raw/10-K/0000320193-24-000123.txt"
with open(doc, 'r', encoding='utf-8') as file:
    response_content = file.read()

# Use the XML parser
soup = BeautifulSoup(response_content, 'xml') 


# print(soup)
master_document_dict = {}
# print(soup.find_all('DOCUMENT'))
# find all the documents in the filing.
for filing_document in soup.find_all('DOCUMENT'):
    print("hello")
    # Use 'string' instead of 'text'
    document_id = filing_document.TYPE.find(string=True, recursive=False).strip()
    print(document_id)
    
    document_sequence = filing_document.SEQUENCE.find(string=True, recursive=False).strip()
    document_filename = filing_document.FILENAME.find(string=True, recursive=False).strip()
    document_description = filing_document.DESCRIPTION.find(string=True, recursive=False).strip()
    print(document_sequence, document_filename, document_description)
    
    # Initialize our document dictionary
    master_document_dict[document_id] = {}
    
    # Add the different parts, we parsed up above.
    master_document_dict[document_id]['document_sequence'] = document_sequence
    master_document_dict[document_id]['document_filename'] = document_filename
    master_document_dict[document_id]['document_description'] = document_description
    
    # Store the document itself
    master_document_dict[document_id]['document_code'] = filing_document.extract()
    
    # Check for the 'text' tag before extracting
    filing_doc_text = filing_document.find('TEXT')
    if filing_doc_text is not None:
        filing_doc_text = filing_doc_text.extract()
        # Find all the thematic breaks
        all_thematic_breaks = filing_doc_text.find_all('hr', {'width': '100%'})
    else:
        print(f"No 'text' tag found for document ID: {document_id}")