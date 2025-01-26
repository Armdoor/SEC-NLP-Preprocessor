'''
This code is called by the paser_main.py used to parse the filings for each company. It uses the functions from 
parser.py to process and store the extracted data into a preprocessed folder under each filing type of the company.
'''


from parser import read_doc, document_data, normalize_filing_docs, parse_html,construct_master_dict, header_data_parser
import os
import json



##############################################--VARIABLE DECLARATION--#################################################
styles = [
    {'style': lambda value: value and 'width: 100%' in value},  # Style condition using lambda
    {'width': '100%'},  # Checking for an exact width attribute
    {'style': 'page-break-after:always'}  # Checking for a specific page break style
]

all_headers ={}

##############################################--VARIABLE DECLARATION ENDS--#############################################

##############################################--MAIN--##################################################################

# called by the parser_main.py to parse the filing type for each company. 
def companies_main(raw_path, preprocessed_path,file_name, cmp_name):

    #  create the path to where we will be storing the preprocessed data and also naming it based on the filing name
    output_file_path = os.path.join(preprocessed_path, f"{file_name}_data.txt")

    if os.path.exists(output_file_path):
        print(f"File '{output_file_path}' already exists. Skipping processing.")
        return  # Skip processing this file
    
    # read the raw file that needs to be parsed
    soup = read_doc(raw_path)
    header, accession_number = header_data_parser(soup)
    if cmp_name not in all_headers:
        all_headers[cmp_name] = {}  # Initialize list for the company
    if file_name not in all_headers[cmp_name]:
        all_headers[cmp_name][file_name] = [] 

    all_headers[cmp_name][file_name].append(header['sec_header'])

    master_document_dict = document_data(soup, styles) 
    # consturct the master dictionary with all the data
    filing_dict = construct_master_dict(master_document_dict, header, accession_number)
    filing_docs = filing_dict[accession_number]['filing_documents']
    # normalize the filing documents
    normm_data = normalize_filing_docs(filing_docs)
    # create the preprocessed folder if it doesn't exist
    os.makedirs(preprocessed_path, exist_ok=True)
    output_file_path = os.path.join(preprocessed_path, f"{file_name}_data.txt")
    # write the preprocessed data to a file
    file_acumulated_data = parse_html(normm_data)
    if file_acumulated_data is None:
        print("No filing data found")
    else :
        file_acumulated_data = header['sec_header'] + "\n" + file_acumulated_data    
        with open(output_file_path, 'w', encoding='utf-8') as file:
            file.write(file_acumulated_data)



##############################################--MAIN END--####################################################