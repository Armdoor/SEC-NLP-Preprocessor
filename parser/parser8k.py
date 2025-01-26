from parser import read_doc, document_data, normalize_filing_docs, parse_html,construct_master_dict, header_data_parser
import os
import json
from bs4 import BeautifulSoup, Tag
'''
An 8-K is required to announce significant events relevant to shareholders. 
Companies usually have four business days to file an 8-K for most items.

Sections of Form 8-K
Form 8-K is organized into nine main sections. Each section covers specific types of events or changes that trigger 
a reporting obligation. Here's a breakdown:

1. Registrant's business and operations: Including material agreements, bankruptcy filings, and mine safety violations.
2. Financial Information: Covers acquisition or disposition of assets, material impairments, and changes in shell 
company status.
3. Securities and trading markets: These include delistings, failures to meet listing standards, and unregistered sales 
of equity securities.
4. Matters related to accountants and financial statements: These include changes in auditors and non-reliance on 
previously issued financial statements.
5. Corporate governance and management: Covers changes in control, director departures, executive officer appointments, 
and amendments to governing documents.
6. Asset-backed securities: Specific to issuers of asset-backed securities.
7. Regulation FD Disclosure: For disclosures made under Regulation Fair Disclosure.
8. Other events: A catchall for voluntary disclosure of events not explicitly required but that the company deems 
important.
9. Financial statements and exhibits: For including financial statements, pro forma financial information, and other 
exhibits as required.
'''
######################################### Filing Data #########################################

styles = [
    {'style': lambda value: value and 'width: 100%' in value},  # Style condition using lambda
    {'width': '100%'},  # Checking for an exact width attribute
    {'style': 'page-break-after:always'}  # Checking for a specific page break style
]
all_headers ={}
def main_8k(path, file_name, preprocessed_path, cmp_name):
    output_file_path = os.path.join(preprocessed_path, f"{file_name}_data.txt")
    if os.path.exists(output_file_path):
        print(f"File '{output_file_path}' already exists. Skipping processing.")
        return  # Skip processing this file
    soup = read_doc(path)
    header, accession_number = header_data_parser(soup)
    if cmp_name not in all_headers:
        all_headers[cmp_name] = {}  # Initialize list for the company
    if file_name not in all_headers[cmp_name]:
        all_headers[cmp_name][file_name] = [] 
    all_headers[cmp_name][file_name].append(header['sec_header'])
    # style = [{'style': lambda value: value and 'width: 100%' in value}, {'style':'page-break-after:always'}]

    master_document_dict = document_data(soup, styles) 
    filing_dict = construct_master_dict(master_document_dict, header, accession_number)
    filing_docs = filing_dict[accession_number]['filing_documents']
    
    print(type(filing_docs))

    normm_data = normalize_filing_docs(filing_docs)
    # print(type(normm_data))
    os.makedirs(preprocessed_path, exist_ok=True)
    output_file_path = os.path.join(preprocessed_path, f"{file_name}_data.txt")

    file_acumulated_data = header['sec_header'] + "\n" +parse_html(normm_data)
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(file_acumulated_data)


def parse8Kfile(path, styles):
    soup = read_doc(path)
    # header = header_data(soup)
    header , accession_number = header_data_parser(soup)
    print(header['sec_header'])
    master_document_dict = document_data(soup, styles)  
    filing_dict = construct_master_dict(master_document_dict, header, accession_number)
    print(filing_dict.keys())
    filing_docs = filing_dict[accession_number]['filing_documents']
    print(type(filing_docs))
    normm_data = normalize_filing_docs(filing_docs)
    #  # print(type(normm_data))
    filedata = parse_html(normm_data)
    file_acumulated_data = header['sec_header'] + "\n" + filedata
    with open(f'extracted_data15.txt', 'w', encoding='utf-8') as file:
        file.write(file_acumulated_data)
# main()
# parse8Kfile("/Users/akshitsanoria/Desktop/PythonP/data1/AAPL/raw/8-K/filing_204.txt", styles)

import json
##############################################--FILING DATA LOADER--##################################################

def convert_tags_to_strings(data):
    """
    Recursively convert BeautifulSoup Tag objects to strings in a dictionary.
    """
    if isinstance(data, dict):
        return {key: convert_tags_to_strings(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_tags_to_strings(item) for item in data]
    elif isinstance(data, Tag):
        return str(data)
    else:
        return data

# header = convert_tags_to_strings(header)
# with open('headers.json', 'w', encoding='utf-8') as f:
#     f.write(convert_tags_to_strings(header))
def print_headers():
    with open("headers.txt", 'w', encoding='utf-8') as file:
        json.dump(all_headers, file, indent=4)
    # print("All headers: ", all_headers)
def search_filing_purpose(path):  
    with open(path, 'r', encoding='utf-8') as file:
        response_content = file.read()
    if not response_content:
        print("No content found in the file")
        return None
    # for section in filing_sections:
    #     for item in filing_sections[section]:
    #         if item in response_content:

