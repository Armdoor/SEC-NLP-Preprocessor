from parser import read_doc, header_data, document_data, normalize_filing_docs, parse_html,construct_master_dict,header_data_parser
import os
import json
styles = [
    {'style': lambda value: value and 'width: 100%' in value},  # Style condition using lambda
    {'width': '100%'},  # Checking for an exact width attribute
    {'style': 'page-break-after:always'}  # Checking for a specific page break style
]
def main():
    path = "/Users/akshitsanoria/Desktop/PythonP/data1/AAPL/raw/10-K/filing_14.txt"

    soup = read_doc(path)
    header = header_data(soup)
    master_document_dict = document_data(soup) 
    filing_dict, accession_number = construct_master_dict(master_document_dict, header)
    filing_docs = filing_dict[accession_number]['filing_documents']
    print(type(filing_docs))

    normm_data = normalize_filing_docs(filing_docs)
    print(type(normm_data))
    file_acumulated_data = parse_html(normm_data)
    with open("extracted_data.txt", 'w', encoding='utf-8') as file:
        file.write(file_acumulated_data)
all_headers ={}

def main_10k(path, file_name, preprocessed_path, cmp_name):
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

# main()
# {'style':'page-break-after:always'}
def parse10Kfile(path, styles):
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
# parse10Kfile("/Users/akshitsanoria/Desktop/PythonP/data1/AAPL/raw/10-K/filing_14.txt", styles)



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