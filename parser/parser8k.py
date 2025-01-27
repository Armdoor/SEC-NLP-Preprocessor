from parser import read_doc, header_data, document_data, normalize_filing_docs, parse_html,construct_master_dict
import os
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
filing_sections ={
"Section 1 Registrant's Business and Operations":{
    "Item 1.01 Entry into a Material Definitive Agreement": str,
    "Item 1.02 Termination of a Material Definitive Agreement": str,
    "Item 1.03 Bankruptcy or Receivership": str,
    "Item 1.04 Mine Safety - Reporting of Shutdowns and Patterns of Violations": str
    },
    "Section 2 Financial Information":{
    "Item 2.01 Completion of Acquisition or Disposition of Assets": str,
    "Item 2.02 Results of Operations and Financial Condition": str,
    "Item 2.03 Creation of a Direct Financial Obligation or an Obligation under an Off-Balance Sheet Arrangement of a Registrant": str,
    "Item 2.04 Triggering Events That Accelerate or Increase a Direct Financial Obligation or an Obligation under an Off-Balance Sheet Arrangement": str,
    "Item 2.05 Costs Associated with Exit or Disposal Activities": str,
    "Item 2.06 Material Impairments": str
    },
    "Section 3 Securities and Trading Markets":{
    "Item 3.01 Notice of Delisting or Failure to Satisfy a Continued Listing Rule or Standard; Transfer of Listing": str,
    "Item 3.02 Unregistered Sales of Equity Securities": str,
    "Item 3.03 Material Modification to Rights of Security Holders": str
    },
    "Section 4 Matters Related to Accountants and Financial Statements":{
    "Item 4.01 Changes in Registrant's Certifying Accountant": str,
    "Item 4.02 Non-Reliance on Previously Issued Financial Statements or a Related Audit Report or Completed Interim Review": str
    },
    "Section 5 Corporate Governance and Management":{
    "Item 5.01 Changes in Control of Registrant": str,
    "Item 5.02 Departure of Directors or Certain Officers; Election of Directors; Appointment of Certain Officers; Compensatory Arrangements of Certain Officers": str,
    "Item 5.03 Amendments to Articles of Incorporation or Bylaws; Change in Fiscal Year": str,
    "Item 5.04 Temporary Suspension of Trading Under Registrant's Employee Benefit Plans": str,
    "Item 5.05 Amendment to Registrant's Code of Ethics, or Waiver of a Provision of the Code of Ethics": str,
    "Item 5.06 Change in Shell Company Status": str,
    "Item 5.07 Submission of Matters to a Vote of Security Holders": str,
    "Item 5.08 Shareholder Director Nominations": str
    },
    "Section 6 Asset-Backed Securities":{
    "Item 6.01 ABS Informational and Computational Material": str,
    "Item 6.02 Change of Servicer or Trustee": str,
    "Item 6.03 Change in Credit Enhancement or Other External Support": str,
    "Item 6.04 Failure to Make a Required Distribution": str,
    "Item 6.05 Securities Act Updating Disclosure": str
    },
    "Section 7 Regulation FD":{
    "Item 7.01 Regulation FD Disclosure": str
    },
    "Section 8 Other Events":{
    "Item 8.01 Other Events (The registrant can use this Item to report events that are not specifically called for by Form 8-K, that the registrant considers to be of importance to security holders.)": str
    },
    "Section 9 Financial Statements and Exhibits":{
    "Item 9.01 Financial Statements and Exhibits": str
    }
}
styles = [
    {'style': lambda value: value and 'width: 100%' in value},  # Style condition using lambda
    {'width': '100%'},  # Checking for an exact width attribute
    {'style': 'page-break-after:always'}  # Checking for a specific page break style
]
header ={}
def main_8k(path, file_name, preprocessed_path, cmp_name):
    output_file_path = os.path.join(preprocessed_path, f"{file_name}_data.txt")
    if os.path.exists(output_file_path):
        print(f"File '{output_file_path}' already exists. Skipping processing.")
        return  # Skip processing this file
    soup = read_doc(path)
    header = header_data(soup)
    style = [{'style': lambda value: value and 'width: 100%' in value}, {'style':'page-break-after:always'}]

    master_document_dict = document_data(soup, styles) 
    filing_dict, accession_number = construct_master_dict(master_document_dict, header)
    filing_docs = filing_dict[accession_number]['filing_documents']
    header.update(filing_dict[accession_number]['sec_header_content'])
    header.update(filing_dict[accession_number]['filer_data'])
    print(type(filing_docs))

    normm_data = normalize_filing_docs(filing_docs)
    # print(type(normm_data))
    os.makedirs(preprocessed_path, exist_ok=True)
    output_file_path = os.path.join(preprocessed_path, f"{file_name}_data.txt")

    file_acumulated_data = parse_html(normm_data)
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(file_acumulated_data)


def parse8Kfile(path, styles):
    soup = read_doc(path)
    header = header_data(soup)
    
    master_document_dict = document_data(soup, styles)  
    filing_dict, accession_number = construct_master_dict(master_document_dict, header)
    filing_docs = filing_dict[accession_number]['filing_documents']
    # print(type(filing_docs))
    normm_data = normalize_filing_docs(filing_docs)
     # print(type(normm_data))
    file_acumulated_data = parse_html(normm_data)
    with open(f'extracted_data15.txt', 'w', encoding='utf-8') as file:
        file.write(file_acumulated_data)
# main()
# parse8Kfile("/Users/akshitsanoria/Desktop/PythonP/data1/AAPL/raw/8-K/filing_204.txt", styles)


##############################################--FILING DATA LOADER--##################################################

def search_filing_purpose(path):  
    with open(path, 'r', encoding='utf-8') as file:
        response_content = file.read()
    if not response_content:
        print("No content found in the file")
        return None
    # for section in filing_sections:
    #     for item in filing_sections[section]:
    #         if item in response_content:

