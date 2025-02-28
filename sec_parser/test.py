from sec_parser_st import Parser


path = '/Users/akshitsanoria/Desktop/PythonP/data1/AAPL/raw/10-K/filing_14.txt'
parser = Parser()
styles = [
    {'style': lambda value: value and 'width: 100%' in value},  # Style condition using lambda
    {'width': '100%'},  # Checking for an exact width attribute
    {'style': 'page-break-after:always'}] # Checking for a specific page break style


soup , empty_file = parser.read_doc(path)

# Collect the SDEC-HEADER
header, filing_data, soup = parser.header_data_parser(soup)

document_dict = parser.document_data(soup, styles) 

accession_number = filing_data['accession_number']

filing_dict = parser.construct_master_dict(document_dict, header, accession_number)

filing_docs = filing_dict[accession_number]['filing_documents']

norm_data = parser.normalize_filing_docs(filing_docs)

file_acumulated_data, pages = parser.parse_html(norm_data)

type_2, pages_w = parser.parse_html_context(norm_data)

with open('/Users/akshitsanoria/Desktop/PythonP/printing_files/parsed_10k_filing.txt', 'w', encoding='utf-8') as file:
    file.write(file_acumulated_data)

with open('/Users/akshitsanoria/Desktop/PythonP/printing_files/parsed_10k_filing_2.txt', 'w', encoding='utf-8') as file:
    file.write(type_2   )


