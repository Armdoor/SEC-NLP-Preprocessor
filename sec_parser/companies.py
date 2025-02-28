'''
This code is called by the paser_main.py used to parse the filings for each company. It uses the functions from 
parser.py to process and store the extracted data into a preprocessed folder under each filing type of the company.
'''


from sec_parser_st import Parser
from load import Loader
import os
import json
import logging
from datetime import datetime


##############################################--VARIABLE DECLARATION--#################################################
styles = [
    {'style': lambda value: value and 'width: 100%' in value},  # Style condition using lambda
    {'width': '100%'},  # Checking for an exact width attribute
    {'style': 'page-break-after:always'}] # Checking for a specific page break style

# styles = [
#     {'style': lambda value: value and 'width: 100%' in value}, 
#     {'style': 'page-break-after:always'},  # Specific page break style
#     {'width': '100%'},  # Specific width condition
# ]

all_headers ={}


##############################################--VARIABLE DECLARATION ENDS--#############################################

##############################################--MAIN--##################################################################
i  = 0
# called by the parser_main.py to parse the filing type for each company. 
def companies_main(raw_path, preprocessed_path,preprocessed_path2, file_name, filing_type, ticker, loader, company_id):

    #  create the path to where we will be storing the preprocessed data and also naming it based on the filing name
    output_file_path = os.path.join(preprocessed_path, f"{file_name}_data.txt")
    output_file_path2 = os.path.join(preprocessed_path2, f"{file_name}_data.txt")

    if os.path.exists(output_file_path):
        logging.info(f"File '{output_file_path}' already exists. Skipping processing in companies.py")
        return  # Skip processing this file
    logging.info(f"Processing {file_name} filing for {ticker} in companies.py")
    if os.path.exists(output_file_path2):
        logging.info(f"File '{output_file_path2}' already exists. Skipping processing in companies.py")
        return  # Skip processing this file
    # declaring the parser object
    parser = Parser()

    # read the raw file that needs to be parsed
    soup , empty_file = parser.read_doc(raw_path)
    if empty_file:
        logging.ERROR(f"***********{file_name} is empty form {ticker} in companies.py**********")
        return

    # Collect the SDEC-HEADER
    header, filing_data, soup = parser.header_data_parser(soup)
    if ticker not in all_headers:
        all_headers[ticker] = {}  # Initialize list for the company
    if file_name not in all_headers[ticker]:
        all_headers[ticker][file_name] = [] 
    
    filing_data['filing_type'] = filing_type
    filing_data['company_id'] = company_id
    filing_data['file_name'] = file_name
    info = filing_data['item_information']
    filing_data['item_information'] = ",".join(info) if info else ""
    
    date_obj = datetime.strptime(filing_data["filing_date"], "%Y%m%d")

# Format the datetime object into a desired format
    filing_data['filing_date'] = date_obj.strftime("%Y-%m-%d") 
    record = (
        filing_data["company_id"],
        filing_data["accession_number"],
        filing_data["filing_type"],
        filing_data["filing_date"],
        filing_data["file_name"],
        int(filing_data["document_count"]),
        filing_data["item_information"]
    )
    filing_id= loader.insert_filings([record])

    header_filing_id = filing_id
    pages_filing_id = filing_id
    print(filing_id)
    if filing_id is not None:
        header_data = (header_filing_id, header['sec_header'])
        loader.insert_headers([header_data])

    # all_headers[ticker][file_name].append(header['sec_header'])

    document_dict = parser.document_data(soup, styles) 

    # # consturct the master dictionary with all the data
    accession_number = filing_data['accession_number']
    filing_dict = parser.construct_master_dict(document_dict, header, accession_number)
    filing_docs = filing_dict[accession_number]['filing_documents']

    # # normalize the filing documents
    normm_data = parser.normalize_filing_docs(filing_docs)

    # # create the preprocessed folder if it doesn't exist
    os.makedirs(preprocessed_path, exist_ok=True)
    output_file_path = os.path.join(preprocessed_path, f"{file_name}_data.txt")
    output_file_path2 = os.path.join(preprocessed_path2, f"{file_name}_data.txt")

    # # write the preprocessed data to a file
    file_acumulated_data, pages = parser.parse_html(normm_data)
    # file_acumulated_data2, pages2 = parser.parse_html2(normm_data)
    print('filing_id before pages: ', filing_id)
    page_records = [(pages_filing_id, filing_type, accession_number, page[0], page[1]) for page in pages]
    # page_records2 = [(pages_filing_id, page[0], page[1]) for page in pages2]
    # page_data = [(filing_id, page_number, page_content) for page_number, page_content in pages.items()]
    # data = [
    #         (filing_id, page_number, json.dumps(page_content))
    #         for page_number, page_content in pages.items()
    #     ]
    # Insert the data
    loader.insert_pages(page_records)
    # with open("extraction2.txt", 'w', encoding='utf-8') as file: 
    #     file.write(file_acumulated_data)

    if file_acumulated_data is None:
        logging.error("No filing data found in companies.py")
    # else :
    #     file_acumulated_data = header['sec_header'] + "\n" + file_acumulated_data    
    #     with open(output_file_path, 'w', encoding='utf-8') as file:
    #         file.write(file_acumulated_data)


    # if file_acumulated_data2 is None:
    #     logging.error("No filing data found in companies.py for file_acumulated_data2")
    # else :
    #     file_acumulated_data2 = header['sec_header'] + "\n" + file_acumulated_data2  
    #     with open(output_file_path2, 'w', encoding='utf-8') as file:
    #         file.write(file_acumulated_data2)
    

    
##############################################--MAIN END--####################################################


# loader= Loader()
# rp = "/Users/akshitsanoria/Desktop/PythonP/data1/ASB/raw/8-K/filing_25.txt"
# pp = "/Users/akshitsanoria/Desktop/PythonP/data1/ASB/preprocessed/8-K"
# companies_main(rp, pp,'filing_25', '8-K','ASB',loader , 3)