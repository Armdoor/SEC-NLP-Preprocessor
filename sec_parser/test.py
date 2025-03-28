from sec_parser_st import Parser
import os
from datetime import datetime

path = '/Users/akshitsanoria/Desktop/PythonP/data1/AAPL/raw/10-K/filing_14.txt'
parser = Parser()
styles = [
    {'style': lambda value: value and 'width: 100%' in value},  # Style condition using lambda
    {'width': '100%'},  # Checking for an exact width attribute
    {'style': 'page-break-after:always'}] # Checking for a specific page break style



all_headers ={}

def test_parser(raw_path, file_name, filing_type, ticker, company_id):
    # output_file_path = os.path.join(preprocessed_path, f"{file_name}_data.txt")
    # output_file_path2 = os.path.join(preprocessed_path2, f"{file_name}_data.txt")
    # if os.path.exists(output_file_path2):
        
    #     return  # Skip processing this file
    # declaring the parser object
    parser = Parser()
    parsed_file_data = dict()

    # read the raw file that needs to be parsed
    soup , empty_file = parser.read_doc(raw_path)
    if empty_file:
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
    # filing_id= loader.insert_filings([record])

    # header_filing_id = filing_id
    # pages_filing_id = filing_id
    # print(filing_id)
    # if filing_id is not None:
    #     header_data = (header_filing_id, header['sec_header'])
    #     loader.insert_headers([header_data])

    # all_headers[ticker][file_name].append(header['sec_header'])

    document_dict = parser.document_data(soup, styles) 

    # # consturct the master dictionary with all the data
    accession_number = filing_data['accession_number']
    filing_dict = parser.construct_master_dict(document_dict, header, accession_number)
    filing_docs = filing_dict[accession_number]['filing_documents']

    # # normalize the filing documents
    normm_data = parser.normalize_filing_docs(filing_docs)

    # # create the preprocessed folder if it doesn't exist
    output_file_path = "/Users/akshitsanoria/Desktop/PythonP/printing_files/Test/parsed.txt"

    # # write the preprocessed data to a file
    file_acumulated_data, pages = parser.parse_html_context(normm_data)
    # file_acumulated_data2, pages2 = parser.parse_html2(normm_data)
    # print('filing_id before pages: ', filing_id)
    with open(output_file_path, "w") as f:
        f.write(file_acumulated_data)
    page_records = [(filing_type, accession_number, page[0], page[1]) for page in pages]
    
    # loader.insert_pages(page_records)


    parsed_file_data['accession_number'] = accession_number
    parsed_file_data['ticker']= ticker
    parsed_file_data['filing_type'] = filing_type
    parsed_file_data['filing_date'] = filing_data['filing_date']
    # parsed_file_data['header'] = header_data
    parsed_file_data['records'] = record
    parsed_file_data['pages'] = page_records
    # pages_filing_id['pages_accumulated'] = file_acumulated_data
    with open("/Users/akshitsanoria/Desktop/PythonP/printing_files/Test/dict.txt", 'w') as f:
        t =''
        for k , v in parsed_file_data.items():
            t+= k + ": \n \t"+ str(v) + "\n"
        f.write(t)
    return parsed_file_data, file_acumulated_data

path = "/Users/akshitsanoria/Desktop/PythonP/data1/AAPL/raw/10-K/filing_14.txt"
test, pages_data =  test_parser(path, 'filing_14', '10-K', 'AAPL', 3)