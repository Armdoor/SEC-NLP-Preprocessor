import re
import unicodedata
from bs4 import BeautifulSoup, Tag
import copy
import json

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
accession_number = ""
#############################################--Case InSensensetive--########################################################


def find_case_insensitive(soup, tag_name):
    """
    Find a tag in a case-insensitive manner.
    """
    for tag in soup.find_all(True):  # True finds all tags
        if tag.name.lower() == tag_name.lower():
            return tag
    return None

#############################################--READING THE DOC--########################################################

def read_doc(path):
    with open(path, 'r', encoding='utf-8') as file:
            response_content = file.read()
    # print("Type of response_content", type(response_content))
    # print(response_content[:100])
        # Use the HTML parser
    try:
        # Attempt to parse with lxml
        soup = BeautifulSoup(response_content, 'lxml')
    except Exception as e:
        print("Failed with lxml parser. Retrying with html5lib.")
        # Fall back to html5lib if lxml fails
        soup = BeautifulSoup(response_content, 'html5lib')
    tags = (soup.prettify())
    with open("tags.txt", 'w') as file:
        file.write(tags)
    return soup



#############################################--Header DATA--########################################################

'''
def header_data(soup, cmp_name):
    sec_header = find_case_insensitive(soup, "SEC-HEADER")
    if sec_header:
        sec_header_text = sec_header.get_text(separator='\n', strip=True)
        # with open("SectionHeader.txt", 'w') as file:
        #     file.write(sec_header_text)
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
'''
def header_data_parser(soup): 
    sec_header = find_case_insensitive(soup, "SEC-HEADER")
    if not sec_header:
        print("No <SEC-HEADER> tag found")
        return {}
    sec_header_text = sec_header.get_text(separator='\n', strip=True)
    header = {}
    header['sec_header'] = sec_header_text

    lines = sec_header_text.splitlines()
    value= ""
    for line in lines:
        line = line.strip()
        if line.startswith("ACCESSION NUMBER:"):
            current_section = line.rstrip(":")
            key, value = current_section.split(":",1)
            print("key", key , "value; ",value )
            accession_number = value
            break 

    return header, value


def header_data(soup):
    sec_header = find_case_insensitive(soup, "SEC-HEADER")
    if not sec_header:
        print("No <SEC-HEADER> tag found")
        return {}

    sec_header_text = sec_header.get_text(separator='\n', strip=True)
    lines = sec_header_text.splitlines()

    header = {}
    current_section = None

    for line in lines:
        current_section = line.rstrip(":")
        print("current_section", current_section)

        # Check if the line is a new section header (ends with ':')
        if line.endswith(":"):
            current_section = line.rstrip(":")
            if current_section not in header:
                header[current_section] = {}
            continue

        if current_section:
            # Parse key-value pairs within the current section
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()

                # Handle multiple occurrences of the same key
                if key not in header[current_section]:
                    header[current_section][key] = [value]
                else:
                    header[current_section][key].append(value)

    return header

#############################################--DOC DATA--########################################################



master_document_dict = {}
def check_style_match(hr_tag, style_condition):
    """
    Checks if the <hr> tag matches the given style condition.
    """
    style_value = hr_tag.get('style', '')

    # If the condition is a lambda function, apply it
    if isinstance(style_condition, dict) and 'style' in style_condition:
        if callable(style_condition['style']):
            return style_condition['style'](style_value)  # Apply lambda function
        else:
            return style_condition['style'] in style_value  # Check if string exists in style_value
    
    # If the condition is an exact string match, check if it exists in the style
    if isinstance(style_condition, dict) and 'width' in style_condition:
        return style_condition['width'] in style_value

    return False

def find_thematic_breaks(all_hr_tags, styles):
    thematic_breaks = []
    for hr in all_hr_tags:
        for style in styles:
            if check_style_match(hr, style):
                thematic_breaks.append(hr)
                break
    return thematic_breaks


def document_data(soup, styles):
    docs = soup.find_all("document")
    # print("Styling", style)
    # header = header_data(soup)
    print("len of docs", len(docs))
    thematic_breaks =[]
    for doc in docs:
        if not isinstance(doc, Tag):
            print("not a tag")
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
        if description_tag:
            document_description = ""
            for element in description_tag.contents:  
                if element.name == "text": 
                    break
                if isinstance(element, str):  
                    document_description += element.strip()
            # print("Document Description:", document_description)
        else:
            print("No description found")
            document_description = "No description"
        # print(document_id, document_sequence, document_filename)
        master_document_dict[document_id] = {}

        master_document_dict[document_id]['document_sequence'] = document_sequence
        master_document_dict[document_id]['document_filename'] = document_filename
        master_document_dict[document_id]['document_description'] = document_description
        cleaned_doc_html = ' '.join(str(doc).split())
        master_document_dict[document_id]['document_code']= cleaned_doc_html
        # exct = doc.extract()
        # with open("extract.txt", 'w') as file:
        #     file.write(str(exct))
        # check = str(doc)
        # with open("check.txt", 'w') as file:
        #     file.write(str(check))

        filing_doc_text = doc.find("text")

        if filing_doc_text:
            filing_doc_text = filing_doc_text.extract()
        else:
            print("No text found")
            continue
        for style in styles:
            thematic_breaks = filing_doc_text.find_all('hr', style)
            if len(thematic_breaks) > 0:
                print("Thematic breaks found")
                break
        # all_hr_tags= filing_doc_text.find_all('hr')
        # thematic_breaks = find_thematic_breaks(all_hr_tags, styles)

        if len(thematic_breaks) == 0:
            print("No thematic breaks found " )
        # thematic_breaks = filing_doc_text.find_all('hr', {'width':'100%'})
        # if len(thematic_breaks) == 0:
        #     print("No thematic breaks found for ", str(style[0]) )
        #     thematic_breaks = filing_doc_text.find_all('hr', style[1])
        # print("Thematic breaks", thematic_breaks)
        # print(style)
        # for thematic_break in thematic_breaks:
        #     print("Thematic break:", thematic_break)
        #     print("Parent:", thematic_break.parent)
        #     print("Grandparent:", thematic_break.parent.parent if thematic_break.parent else "No parent")
        #     print("Previous sibling:", thematic_break.parent.parent.previous_sibling if thematic_break.parent and thematic_break.parent.parent else "No grandparent")
        # all_page_numbers = [thematic_break.parent.parent.previous_sibling.get_text(strip=True) 
                        # for thematic_break in thematic_breaks]
        # all_page_numbers = [
        #     thematic_break.parent.parent.previous_sibling.get_text(strip=True) 
        #     if (thematic_break.parent and thematic_break.parent.parent and thematic_break.parent.parent.previous_sibling) 
        #     else (thematic_break.parent.get_text(strip=True) if thematic_break.parent else None) 
        #     for thematic_break in thematic_breaks
        #     if thematic_break.parent and thematic_break.parent.parent
        # ]
        all_page_numbers =[]
        for thematic_break in thematic_breaks:
            try:
                parent = thematic_break.parent
                grandparent = parent.parent if parent else None
                previous_sibling = grandparent.previous_sibling if grandparent else None

                # Log the parent and grandparent structures for inspection
                # print(f"Inspecting thematic_break: {thematic_break}")
                # print(f"Parent: {parent}")
                # print(f"Grandparent: {grandparent}")

                if previous_sibling:
                    page_number = previous_sibling.get_text(strip=True)
                    if page_number:
                        all_page_numbers.append(page_number)
                    else:
                        print(f"Previous sibling exists but contains no text: {previous_sibling}")
                elif parent:
                    page_number = parent.get_text(strip=True)
                    if page_number:
                        all_page_numbers.append(page_number)
                    else:
                        print(f"Parent exists but contains no text: {parent}")
                else:
                    print(f"Skipping thematic break due to missing or invalid previous sibling: {thematic_break}")

            except Exception as e:
                print(f"Error processing thematic break: {thematic_break}, error: {e}")



        length_of_page_numbers = len(all_page_numbers)
        print("length of page numbers", length_of_page_numbers)
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
            # store the page_numbers
            master_document_dict[document_id]['page_numbers'] = all_page_numbers
            # convert all thematic breaks to a string so it can be used for parsing
            thematic_breaks = [str(thematic_break) for thematic_break in thematic_breaks]
            
            # prep the document text for splitting, this means converting it to a string.
            filing_doc_string = ' '.join(str(filing_doc_text).split())
            # filing_doc_string = str(filing_doc_text)
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
            # else:
            #     master_document_dict[document_id]['pages_code'] = ["None"]
            print('-'*80)
            print('The document {} was parsed.'.format(document_id))
            print('There was {} page(s) found.'.format(len(all_page_numbers)))
            print('There was {} thematic breaks(s) found.'.format(len(thematic_breaks)))

    return master_document_dict  
#############################################--MASTER DICT--########################################################

def construct_master_dict(master_document_dict, header, accession_number):
    master_filings_dict[accession_number] = {}
    master_filings_dict[accession_number]['sec_header_content'] = header["sec_header"]
    # master_filings_dict[accession_number]['filer_data'] = header["filer"]
    master_filings_dict[accession_number]['filing_documents'] = master_document_dict
    # master_filings_dict_json = convert_tags_to_strings(master_filings_dict)
    with open("master_dict.txt", 'w', encoding='utf-8') as file:
        formatted_content = format_dict(header)
        # json.dump(master_filings_dict_json, file, indent=4)
        file.write(formatted_content)
    return master_filings_dict

    return master_filings_dict
def format_dict(dictionary, indent=0):
    formatted_str = ""
    for key, value in dictionary.items():
        if isinstance(value, dict):
            formatted_str += "  " * indent + f"{key}:\n"
            formatted_str += format_dict(value, indent + 1)  # Recursively format nested dictionaries
        else:
            formatted_str += "  " * (indent + 1) + f"{key}: {value}\n"
    return formatted_str

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

#############################################--NORMALIZE DATA--########################################################

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

def extract_text_from_html(html_str):
    """
    Extracts and normalizes text from an HTML string, handling <TEXT> content specifically.
    """
    try:
        # Parse the HTML string
        soup = BeautifulSoup(html_str, 'html5lib')
        # Extract all text within the <TEXT> tag
        text_content = soup.find('text')
        if text_content:
            raw_text = text_content.get_text(' ', strip=True)
        else:
            raw_text = ''
        return soup, raw_text
    except Exception as e:
        print(f"Error parsing HTML: {e}")
        return None, None

def normalize_text_content(raw_text):
    """
    Cleans and normalizes raw text extracted from HTML.
    """
    if not raw_text:
        return ''
    # Normalize Unicode characters
    unicode_normalized = unicodedata.normalize('NFKD', raw_text)
    # Restore Windows-specific characters if needed
    restored_text = restore_windows_1252_characters(unicode_normalized)
    # Remove excessive whitespace and newlines
    cleaned_text = re.sub(r'\s+', ' ', restored_text).strip()
    return cleaned_text

def process_document_data(filing_docs):
    """
    Processes and normalizes text for each document entry in filing_docs.
    """
    for document_id, document_data in filing_docs.items():
        print('-' * 80)
        print(f"Processing document ID: {document_id}")

        if 'pages_code' not in document_data:
            print(f"No pages_code found for document ID: {document_id}")
            continue

        # Extract the page code from the document
        pages_code = document_data['pages_code']  # Contains HTML as a string

        # Process the <TEXT> content from pages_code
        repaired_pages = {}
        normalized_text = {}
        for page_number, page_html in enumerate(pages_code, start=1):
            # Extract and normalize text from the HTML
            page_soup, raw_text = extract_text_from_html(page_html)
            if page_soup is None or raw_text is None:
                print(f"Skipping page {page_number} of document {document_id} due to errors.")
                continue

            # Normalize the extracted text
            cleaned_text = normalize_text_content(raw_text)

            # Store the results
            repaired_pages[page_number] = page_soup  # Repaired HTML
            normalized_text[page_number] = cleaned_text  # Cleaned text

            print(f"Page {page_number} has been normalized for document {document_id}.")

        # Update the document data
        document_data['pages_normalized_text'] = normalized_text
        document_data['pages_code'] = repaired_pages
        document_data['pages_numbers_generated'] = list(repaired_pages.keys())

        print(f"Finished processing document ID: {document_id}")
        filing_docs[document_id]['pages_code'] = document_data ['pages_code']
        filing_docs[document_id]['pages_normalized_text'] = document_data ['pages_normalized_text']
        filing_docs[document_id]['pages_numbers_generated'] = document_data ['pages_numbers_generated']
        filing_docs_json = convert_tags_to_strings(filing_docs)
        
    return filing_docs

def normalize_filing_docs(filing_docs):
    """
    Normalizes all documents in the filing_docs dictionary.
    """
    print("Starting normalization of filing documents...")
    doc_norm = process_document_data(filing_docs)
    filing_docs_json = convert_tags_to_strings(doc_norm)
    # with open("filing_docs_norm.txt", 'w', encoding='utf-8') as file:
    #         json.dump(filing_docs_json, file, indent=4)
    print("Normalization complete.")
    return doc_norm

##################################################----PARSE HTML----#############################################

def parse_html(filing_docs):
    doc_acumulated_data = ""
    for document_id, document_data in filing_docs.items():
        print('-' * 80)
        print(f"Extracting data from document ID: {document_id}")
        if 'pages_code' not in document_data:
            print(f"No pages_code found for document ID: {document_id}")
            continue
        
        pages_code = document_data['pages_code']
        for page_number, code in pages_code.items():
            print("-" * 80)
            print(f"Extracting data from page number: {page_number}")

            if not code:
                print(f"Warning: code is None or empty for page number: {page_number}")
                continue

            # Parse the HTML code
            soup_code = code.prettify()

            # Debug: Save prettified HTML for inspection
            # with open(f"page_code_{page_number}.html", 'w', encoding='utf-8') as file:
            #     file.write(soup_code)

            # Remove <ix:header> tags if present
            for header in code.find_all('ix:header'):
                header.decompose()

            # Find the <body> tag
            html_body = code.find('body')
            if html_body is None:
                print(f"Warning: No <body> tag found in page number: {page_number}")
                continue

            # Extract text from the <body>
            data_extracted = extract_text(html_body)
            print( "Data extracted type " ,type(data_extracted))
            doc_acumulated_data += "\n" + "PAGE NUMBER: "+str(page_number)+"\n"+"\n"+ "\n".join(data_extracted) + "\n"
            # Save extracted text to a file
            # output_file = f"Extracted_data_{document_id}_page_{page_number}.txt"
            # with open(output_file, 'w', encoding='utf-8') as file:
            #     print(f"Saving extracted data to: {output_file}")
            #     file.write("\n".join(data_extracted)) 
    return doc_acumulated_data

##################################################----EXTRACT TEXT----#############################################

def extract_text(element, handle_tables=True):
    """
    Recursive function to extract clean, de-duplicated text from a BeautifulSoup element.
    Tables are handled separately if `handle_tables` is True.
    """
    text = []

    # Traverse children of the element
    for child in element.children:
        if isinstance(child, str):  # If the child is a NavigableString
            stripped_text = child.strip()
            if stripped_text:  # Only add non-empty text
                text.append(stripped_text)
        elif child.name:  # If the child is a tag, process it recursively
            # Handle specific tags like <table>
            if child.name == 'table' and handle_tables:
                table_text = extract_table(child)
                if table_text:
                    text.append("\n")
                    text.append(table_text)  # Add entire table as a single string
            else:
                text.extend(extract_text(child))  # Recursively process non-table tags

    # Remove duplicates while preserving order
    unique_lines = list(dict.fromkeys(text))
    return unique_lines


##################################################----EXTRACT TABLE----#############################################


def extract_table(table_element):
    """
    Extracts text from a BeautifulSoup <table> element and formats it as a tab-separated string.
    """
    rows = []
    for row in table_element.find_all('tr'):  # Iterate through table rows
        cells = [cell.get_text(strip=True) for cell in row.find_all(['th', 'td'])]
        if cells:
            rows.append("\t".join(cells))  # Tab-separated values for each row
    return "\n".join(rows) if rows else None