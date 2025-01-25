from parser.parser import read_doc, header_data, document_data, normalize_filing_docs, parse_html,construct_master_dict


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


main()
# {'style':'page-break-after:always'}