import re
import requests
import unicodedata
from bs4 import BeautifulSoup, Tag
import copy
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
filing_data ={
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

#############################################--Header--########################################################
pre_head = {
    'ACCESSION NUMBER': None,
    'CONFORMED SUBMISSION TYPE': None,
    'PUBLIC DOCUMENT COUNT': None,
    'CONFORMED PERIOD OF REPORT': None,
    'ITEM INFORMATION': None,
    'FILED AS OF DATE': None,
    'DATE AS OF CHANGE':None,
}
filer = {
    "COMPANY DATA": {
        "COMPANY CONFORMED NAME": None,
        "CENTRAL INDEX KEY": None,
        "IRS NUMBER": None,
        "STATE OF INCORPORATION": None,
        "FISCAL YEAR END": None,
    },
    "BUSINESS ADDRESS": {
        "STREET 1": None,
        "CITY": None,
        "STATE": None,
        "ZIP": None,
        "BUSINESS PHONE": None,
    },
    "MAIL ADDRESS": {
        "STREET 1": None,
        "CITY": None,
        "STATE": None,
        "ZIP": None,
    },
    "FILING VALUES": {
        "FORM TYPE": None,
        "SEC ACT": None,
        "SEC FILE NUMBER": None,
        "FILM NUMBER": None,
    },
    "FORMER COMPANY": {
        "FORMER CONFORMED NAME": None,
        "DATE OF NAME CHANGE": None,
    },
}
master_filings_dict ={}

def find_case_insensitive(soup, tag_name):
    """
    Find a tag in a case-insensitive manner.
    """
    for tag in soup.find_all(True):  # True finds all tags
        if tag.name.lower() == tag_name.lower():
            return tag
    return None

doc_read = "/Users/akshitsanoria/Desktop/PythonP/data1/AAPL/raw/8-K/filing_4.txt"
with open(doc_read, 'r', encoding='utf-8') as file:
        response_content = file.read()

    # Use the HTML parser
soup = BeautifulSoup(response_content, 'html.parser') 
tags = (soup.prettify())
with open("tags.txt", 'w') as file:
    file.write(tags)

master_document_dict = {}
def document_data(soup):
    docs = soup.find_all("document")

    thematic_breaks =[]
    for doc in docs:
        # document_tag = d.find( "type", recursive=False)
        # document_id= d.type.find(text=True, recursive=False).strip()
        # with open("document_id.txt", 'w') as file:
        #     file.write(document_id)
        # sequence_tag = d.find_all("sequence", recursive=False)  
        # document_sequence = d.sequence.find(text=True, recursive=False).strip() 
        # # if sequence_tag else print("No sequence found")

        # filename_tag = d.find_all("filename", recursive=False)
        # document_filename = d.filename.find(text=True, recursive=False).strip() 
        # # if filename_tag else print("No filename found")
        # description_tag = d.find_all("description")
        # document_description = d.description.find(text=True).strip() if description_tag else print("")
        # # print(document_id, document_sequence, document_filename, document_description)
        


        if not isinstance(doc, Tag):
            continue  # Skip if `doc` is not a Tag object

        document_tag = doc.type.find(text=True, recursive=False)
        if document_tag:
            document_id = document_tag.strip()
        else:
            print("No document type found")
            continue

        sequence_tag = doc.sequence.find(text=True, recursive=False)
        if sequence_tag:
            document_sequence = sequence_tag.strip()
        else:
            print("No sequence found")
            document_sequence = None

        filename_tag = doc.filename.find(text=True, recursive=False)
        if filename_tag:
            document_filename = filename_tag.strip()
        else:
            print("No filename found")
            document_filename = None

        description_tag = doc.find("description")
        if description_tag and description_tag.string:
            document_description = description_tag.string.strip()
        else:
            print("No description found")
            document_description = "No description"
            

        print(document_id, document_sequence, document_filename)
        master_document_dict[document_id] = {}

        master_document_dict[document_id]['document_sequence'] = document_sequence
        master_document_dict[document_id]['document_filename'] = document_filename
        master_document_dict[document_id]['document_description'] = document_description
        master_document_dict[document_id]['document_code']= str(doc)
        exct = doc.extract()
        with open("extract.txt", 'w') as file:
            file.write(str(exct))
        check = str(doc)
        with open("check.txt", 'w') as file:
            file.write(str(check))

        filing_doc_text = doc.find("text")

        if filing_doc_text:
            filing_doc_text = filing_doc_text.extract()
        else:
            print("No text found")
            continue

        with open(f"TagsContent{document_id}.txt", 'w') as file: 
            for tag in filing_doc_text.find_all(True): 
                tag_name = tag.name 
                tag_content = tag.get_text(strip=True)  
                file.write(f"<{tag_name}>\n{tag_content}\n</{tag_name}>\n\n")
       
        # thematic_breaks = filing_doc_text.find_all("div", {"style": "page-break-after: always;"})
        thematic_breaks = filing_doc_text.find_all('hr',{'width':'100%'})
        print("THEMATIC BREAKS")
        print(len(thematic_breaks))

        all_page_numbers = [thematic_break.parent.parent.previous_sibling.previous_sibling.get_text(strip=True) 
                        for thematic_break in thematic_breaks]
        
        length_of_page_numbers = len(all_page_numbers)
        
        if length_of_page_numbers > 0:
                
            # grab the last number
            previous_number = all_page_numbers[-1]
            # initalize a new list
            all_page_numbers_cleaned = []    
            # loop through the old list in reverse order.
            for number in reversed(all_page_numbers):
                # if it's blank proceed to cleaning.
                if number == '':
                    # the previous one we looped was 0 or 1.
                    if previous_number == '1' or previous_number == '0':    
                        # in this case, it means this is a "new section", so restart at 0.
                        all_page_numbers_cleaned.append(str(0))
                        # reset the page number and the previous number.
                        length_of_page_numbers = length_of_page_numbers - 1
                        previous_number = '0'
                    # the previous one we looped it wasn't either of those.
                    else:    
                        # if it was blank, take the current length, subtract 1, and add it to the list.
                        all_page_numbers_cleaned.append(str(length_of_page_numbers - 1))    
                        # reset the page number and the previous number.
                        length_of_page_numbers = length_of_page_numbers - 1
                        previous_number = number
                else:        
                    # add the number to the list.
                    all_page_numbers_cleaned.append(number)    
                    # reset the page number and the previous number.
                    length_of_page_numbers = length_of_page_numbers - 1
                    previous_number = number
            else:        
                # make sure that it has a page number even if there are none, just have it equal 0
                all_page_numbers_cleaned = ['0']
            # have the page numbers be the cleaned ones, in reversed order.
            all_page_numbers = list(reversed(all_page_numbers_cleaned))
            print('PAGE NO. ',all_page_numbers)
            # store the page_numbers
            master_document_dict[document_id]['page_numbers'] = all_page_numbers
            # convert all thematic breaks to a string so it can be used for parsing
            thematic_breaks = [str(thematic_break) for thematic_break in thematic_breaks]
            
            # prep the document text for splitting, this means converting it to a string.
            filing_doc_string = str(filing_doc_text)

            
            # handle the case where there are thematic breaks.
            if len(thematic_breaks) > 0:
                print("Document with thematic breaks ", document_id)
                # define the regex delimiter pattern, this would just be all of our thematic breaks.
                regex_delimiter_pattern = '|'.join(map(re.escape, thematic_breaks))

                # split the document along each thematic break.
                split_filing_string = re.split(regex_delimiter_pattern, filing_doc_string)

                # store the document itself
                master_document_dict[document_id]['pages_code'] = split_filing_string

            # handle the case where there are no thematic breaks.
            elif len(thematic_breaks) == 0:
                print("Document without thematic breaks ", document_id)
                # handles so it will display correctly.
                split_filing_string = thematic_breaks
                
                # store the document as is, since there are no thematic breaks. In other words, no splitting.
                master_document_dict[document_id]['pages_code'] = [filing_doc_string]

            print('-'*80)
            print('The document {} was parsed.'.format(document_id))
            print('There was {} page(s) found.'.format(len(all_page_numbers)))
            print('There was {} thematic breaks(s) found.'.format(len(thematic_breaks)))
            i +=1
    return master_document_dict    
# print(master_document_dict)
document_data(soup)
with open("master_doc.txt", 'w') as file:
    for k,v in master_document_dict.items():
        file.write(f"KEY IS : {k}: VALUE IS : {v}\n")



def parse_8k(soup):
    sec_header = find_case_insensitive(soup, "SEC-HEADER")
    if sec_header:
        sec_header_text = sec_header.get_text(separator='\n', strip=True)
        with open("SectionHeader.txt", 'w') as file:
            file.write(sec_header_text)
    else:
        print("No <SEC-HEADER> tag found")

    header = {}
    lines = sec_header_text.splitlines()

    parsed_pre_head = copy.deepcopy(pre_head)
    parsed_filer = copy.deepcopy(filer)
    current_section = None
    name_change = 1

    for line in lines:
        line = line.strip()
        # Parse the pre-head section
        for key in pre_head.keys():
            if line.startswith(key):
                _, value = line.split(":", 1)
                parsed_pre_head[key] = value.strip()
                break

        # Normalize section headers
        norm_line = line.rstrip(":")
        if norm_line in filer.keys():
            current_section = norm_line
            continue

        # Dynamically handle multiple `FORMER COMPANY` entries
        if current_section == "FORMER COMPANY":
            # Check if the current `FORMER COMPANY` has been filled
            if (parsed_filer[current_section]["FORMER CONFORMED NAME"] is not None and 
                parsed_filer[current_section]["DATE OF NAME CHANGE"] is not None):
                
                # Create a new key for the next `FORMER COMPANY`
                new_name = f"FORMER COMPANY {name_change}"
                parsed_filer[new_name] = {
                    "FORMER CONFORMED NAME": None,
                    "DATE OF NAME CHANGE": None
                }
                name_change += 1
                current_section = new_name

        # Parse the fields in the current section
        if current_section in parsed_filer:
            for key in parsed_filer[current_section]:
                if line.startswith(key):
                    _, value = line.split(":", 1)
                    parsed_filer[current_section][key] = value.strip()
                    break

    # Remove empty `FORMER COMPANY` entries if they exist
    parsed_filer = {
        key: value for key, value in parsed_filer.items()
        if not (key.startswith("FORMER COMPANY") and all(v is None for v in value.values()))
    }
    header["sec_header"] = parsed_pre_head
    header["filer"] = parsed_filer
    return header
import pprint
# pprint.pprint(parsed_pre_head)
# pprint.pprint(parse_8k(soup))

# Find the thematic breaks in the document
header = parse_8k(soup)
with open("header.txt", 'w') as file:
    for k,v in header.items():
        file.write(f"{k}: {v}" + "\n")
"""
<hr style="border: none; border-bottom: 1px solid black; border-top: 4px solid black; height: 10px; 
color: #ffffff; background-color: #ffffff; text-align: center; margin-left: auto; margin-right: auto;"/>



 <hr style="background-color: #000000; border-bottom: medium none; border-left: medium none; border-right: medium none; 
 border-top: medium none; margin: 0px auto; height: 2px; width: 20%; color: #000000; text-align: center; 
 margin-left: auto; margin-right: auto;"/>


 <hr style="background-color: #000000; border-bottom: medium none; border-left: medium none; border-right: medium none; 
 border-top: medium none; margin: 0px auto; height: 2px; width: 20%; color: #000000; text-align: center; 
 margin-left: auto; margin-right: auto;"/>

 <hr style="height: 2px; width: 20%; color: #000000; background-color: #000000; text-align: center; border: none; 
 margin-left: auto; margin-right: auto;"/>

<hr style="height: 2px; width: 20%; color: #000000; background-color: #000000; text-align: center; border: none; 
margin-left: auto; margin-right: auto;"/>

<hr style="border: none; border-bottom: 4px solid black; border-top: 1px solid black; height: 10px; color: #ffffff; 
background-color: #ffffff; text-align: center; margin-left: auto; margin-right: auto;"/>

<hr style="border-width: 0px; clear: both; margin: 4px 0px; width: 100%; height: 2px; color: #000000; 
background-color: #000000;"/>
"""
# for page in all_page_numbers:
#     print(page)
# with open("all_page_numbers.txt", 'w') as file:
#         file.write(all_page_numbers)
# count = 0
# for hr in thematic_breaks:
#     count += 1
#     print(count)
#     print("\n")


def parse_text(soup):
    # text = find_case_insensitive(soup, "TEXT")
    # if text:
    #     for tag in soup.find_all(['hr', 'p', 'div']): 
    #         if tag.name == 'hr': 
    #             print(f"Page {page_no}:\n{text_output}\n") 
    #             text_output = "" 
    #             page_no += 1 
    #         elif tag.name in ['p', 'div']: 
    #             text_output += tag.get_text() + "\n" 
        
    #     if text_output.strip(): 
    #         print(f"Page {page_no}:\n{text_output}\n")
    for text in soup:
        page = text.get_text()
        print(page)

accession_number = header["sec_header"]["ACCESSION NUMBER"]
master_filings_dict[accession_number] = {}
master_filings_dict[accession_number]['sec_header_content'] = header["sec_header"]
# master_filings_dict[accession_number]['filing_documents'] = None

master_filings_dict[accession_number]['filing_documents'] = master_document_dict
print('-'*80)
print('All the documents for filing {} were parsed and stored.'.format(accession_number))
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
master_filings_dict_json = convert_tags_to_strings(master_filings_dict)



import json
# parse_text(soup)
with open("master_dict.txt", 'w', encoding='utf-8') as file:
    json.dump(master_filings_dict_json, file, indent=4)

##################################-----NORMALIZE TEXT----############################################

# print 


filing_docs = master_filings_dict[accession_number]['filing_documents']



def restore_windows_1252_characters(restore_string):
    """
        Replace C1 control characters in the Unicode string s by the
        characters at the corresponding code points in Windows-1252,
        where possible.
    """

    def to_windows_1252(match):
        try:
            return bytes([ord(match.group(0))]).decode('windows-1252')
        except UnicodeDecodeError:
            # No character at the corresponding code point: remove it.
            return ''
        
    return re.sub(r'[\u0080-\u0099]', to_windows_1252, restore_string)

def normalize_text(filing_docs):
    for document_id in filing_docs:
        print('-'*80)
        # print('Puling document {} for text normilization.'.format(doc)) 
        print("document id : ",document_id)
        document_page = filing_docs[document_id]['pages_code']
        pages_length = len(document_page)
        repaired_page = {}
        normalize_text = {}
        for index, page in enumerate(document_page):
            # print("PAGE")
            # print(page)
            # pass it through the parser.
            page_soup = BeautifulSoup(page,'html5')
            # grab all the text, notice I go to the BODY tag to do this
            page_text = page_soup.html.body.get_text(' ',strip = True)
            # print("PAGE TEXT")
            # print(page_text)
            # normalize the text, remove messy characters. Additionally, restore missing window characters.
            page_text_norm = restore_windows_1252_characters(unicodedata.normalize('NFKD', page_text)) 
            # Additional cleaning steps, removing double spaces, and new line breaks.
            page_text_norm = page_text_norm.replace('  ', ' ').replace('\n',' ')
            # print("PAGE TEXT NORM")
            # print(page_text_norm)
            page_num = index +1
            normalize_text[page_num] = page_text_norm
            repaired_page[page_num] = page_soup
            # print('Page {} of {} from document {} has had their text normalized.'.format(index + 1,pages_length, doc))

# normalize_text(filing_docs)

# print(master_filings_dict[accession_number]['filing_documents']['8-K']['pages_code'])