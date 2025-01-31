'''
This code is called by the paser_main.py used to parse the filings for each company. It uses the functions from 
parser.py to process and store the extracted data into a preprocessed folder under each filing type of the company.
'''


from parser import Parser, JsonDataCollector
import os
import json



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

# called by the parser_main.py to parse the filing type for each company. 
def companies_main(raw_path, preprocessed_path,file_name, ticker, loader, company_id, entity):

    #  create the path to where we will be storing the preprocessed data and also naming it based on the filing name
    output_file_path = os.path.join(preprocessed_path, f"{file_name}_data.txt")

    if os.path.exists(output_file_path):
        print(f"File '{output_file_path}' already exists. Skipping processing.")
        return  # Skip processing this file
    print(f"Processing {file_name} filing for {ticker}")

    parser = Parser()
    


    # read the raw file that needs to be parsed
    soup , empty_file = parser.read_doc(raw_path)
    if empty_file:
        print(f"***********{file_name} is empty form {ticker}***********")
        return

    # Insert the json data into the database








    header, accession_number = parser.header_data_parser(soup)
    if ticker not in all_headers:
        all_headers[ticker] = {}  # Initialize list for the company
    if file_name not in all_headers[ticker]:
        all_headers[ticker][file_name] = [] 

    all_headers[ticker][file_name].append(header['sec_header'])

    master_document_dict = parser.document_data(soup, styles) 

    # consturct the master dictionary with all the data
    filing_dict = parser.construct_master_dict(master_document_dict, header, accession_number)
    filing_docs = filing_dict[accession_number]['filing_documents']

    # normalize the filing documents
    normm_data = parser.normalize_filing_docs(filing_docs)

    # create the preprocessed folder if it doesn't exist
    os.makedirs(preprocessed_path, exist_ok=True)
    output_file_path = os.path.join(preprocessed_path, f"{file_name}_data.txt")

    # write the preprocessed data to a file
    file_acumulated_data = parser.parse_html(normm_data)

    if file_acumulated_data is None:
        print("No filing data found")
    else :
        file_acumulated_data = header['sec_header'] + "\n" + file_acumulated_data    
        with open(output_file_path, 'w', encoding='utf-8') as file:
            file.write(file_acumulated_data)


    company_id = loader.insert_company("123456", "Example Inc.", "EXM", "Technology")
    parsed_filing_data = {
        "Financials": {"Balance Sheet": "Details here"},
        "Operations": {"Yearly Report": "Operational insights"}
    }
    json_data = {
        "market_cap": 50000000,
        "employees": 1200,
        "notes": ["Important information", "Additional details"]
    }
    loader.store_parsed_filing(company_id, "10-K", "2025-01-01", parsed_filing_data)
    loader.store_extra_json_data(company_id, json_data)
    loader.close()




def json_data_helper(json_data_collector):
    json_data = json_data_collector.collect_data()
    cik = json_data['']


def data_helper(loader, data):
    loader.insert_companies_bulk(data)




'''
 cik = "sample_cik"  # You can parse this from metadata if available
        ticker = "sample_ticker"
        industry = "sample_industry"
        company_id = loader.i

'''
    
##############################################--MAIN END--####################################################