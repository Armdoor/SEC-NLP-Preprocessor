'''
This class is used to parse SEC filings and extract the relevant information while maining the structure of the filings.
'''

import re
import unicodedata
from bs4 import BeautifulSoup, Tag, NavigableString, Comment
import logging
import json
import os
    ##############################################--VARIABLE DECLARATION--#################################################
class Parser:
    def __init__(self):
        self.master_document_dict = {}
        self.master_filings_dict ={}
        self.accession_number = ""
        self.no_of_pages = 0
        self.pages = []
        self.table_no = 0
        self.filing_types = ['8-K', '10-K', '10-Q', '13-D', 'DEF 14A', 'S-1']
    ##############################################--VARIABLE DECLARATION ENDS--#############################################


    #############################################--CASE INSENSITIVE FUNCTION--##############################################

    #checks if the tag name is in the soup and returns the tag if it is regarderless of the casetype


    def find_case_insensitive(self, soup, tag_name):
        """
        Find a tag in a case-insensitive manner.
        """
        for tag in soup.find_all(True):  # True finds all tags
            if tag.name.lower() == tag_name.lower():
                return tag
        return None


#############################################--CASE INSENSITIVE FUNCTION--##############################################

#############################################--READING THE DOC--########################################################


    # reads the raw file and returns the soup
    def read_doc(self, path, empty_file=False):
        with open(path, 'r', encoding='utf-8') as file:
                response_content = file.read()
        
        # in case the file is empty, return None
        if response_content == "":
            empty_file = True
            return "Empty file", empty_file
        # try to parse the soup with lxml and if it fails, try with html5lib
        try:
            soup = BeautifulSoup(response_content, 'html5lib')
        except Exception as e:
            logging("Failed with html parser. Retrying with lxml in parser.py")
            
            # Fall back to html5lib if lxml fails
            soup = BeautifulSoup(response_content, 'lxml')
        return soup, empty_file

    #############################################--READING THE DOC ENDS--###################################################

    #############################################--Header DATA EXTRACTION--#################################################

    # parses the sec header and returns the header data and theaccession number
    def header_data_parser(self, soup): 
        sec_header = self.find_case_insensitive(soup, "SEC-HEADER")
        filing_data = dict()
        header = {}
        pat = r":\s*(\d{8})"
        if not sec_header:
            logging.error("No <SEC-HEADER> tag found in parser.py")
            return {}
        sec_header_text = sec_header.get_text(separator='\n', strip=True)
        header['sec_header'] = sec_header_text
        match = re.search(pat, sec_header_text)
        with open('filing_sex_header.txt', 'w') as f:
            f.write(sec_header_text)
        if match:
            date = match.group(1)
        else:
            date = ""
        
        filing_data['filing_date'] = date
        
        item_information =[]
        document_count = ""
        lines = sec_header_text.splitlines()
        for line in lines:
            line = line.strip()
            if line.startswith("ACCESSION NUMBER:"):
                current_section = line.rstrip(":")
                _, accession_number = current_section.split(":",1)
                filing_data["accession_number"] = accession_number.strip()
            elif line.startswith("PUBLIC DOCUMENT COUNT:"):
                current_section = line.rstrip(":")
                _, document_count = current_section.split(":",1)
                filing_data["document_count"] = document_count.strip()
            elif line.startswith("ITEM INFORMATION:"):
                current_section = line.rstrip(":")
                _, filing_type = current_section.split(":",1)
                item_information.append(filing_type.strip())
        filing_data["item_information"] = item_information


        ix_headers = soup.find_all(lambda tag: tag.name.lower() == 'ix:header')

        for hed in ix_headers:
            hed.decompose()
        with open('header.txt', 'w', encoding='utf-8') as file:
            file.write(str(soup))
        comments = soup.find_all(string=lambda text: isinstance(text, Comment))
        for comment in comments:
            comment.extract()
        return header, filing_data, soup

    #############################################--Header DATA EXTRACTION ENDS--############################################


    #############################################--DOC DATA EXTRACTION--####################################################

    # this function uses the <hr> tag to find the thematic breaks which then are used to find the pagenumbers and the 
    # <document> tag to find the document data like the document id, sequence, filename, description, and the text. Then we
    # use the tag <text> to store html code that contains the text of the document in the master_document_dict.
    def document_data(self, soup, styles):
        docs = soup.find_all("document")
        thematic_breaks =[]
        for doc in docs:
            if not isinstance(doc, Tag):
                logging.warning(f"Doc is not a tag in document_data in parser.py")
                continue  # Skip if `doc` is not a Tag object
            document_tag = doc.type.find(text=True, recursive=False)
            if document_tag:
                document_id = document_tag.strip()
                print("Doc ID: ",document_id)
            else:
                logging.warning("No document type found in document_data in parser.py")
                continue
            if document_id  in self.filing_types:
                sequence_tag = doc.sequence.find(text=True, recursive=False)
                if sequence_tag:
                    document_sequence = sequence_tag.strip()
                else:
                    logging.warning("No sequence found in document_data in parser.py")
                    document_sequence = None

                filename_tag = doc.filename.find(text=True, recursive=False)
                if filename_tag:
                    document_filename = filename_tag.strip()
                else:
                    logging.warning("No filename found in document_data in parser.py")
                    document_filename = None

                description_tag = doc.find("description")
                if description_tag:
                    document_description = ""
                    for element in description_tag.contents:  
                        if element.name == "text": 
                            break
                        if isinstance(element, str):  
                            document_description += element.strip()
                else:
                    logging.warning("No description found in document_data in parser.py")
                    document_description = "No description"
                self.master_document_dict[document_id] = {}
                self.master_document_dict[document_id]['document_sequence'] = document_sequence
                self.master_document_dict[document_id]['document_filename'] = document_filename
                self.master_document_dict[document_id]['document_description'] = document_description
                cleaned_doc_html = ' '.join(str(doc).split())
                self.master_document_dict[document_id]['document_code']= cleaned_doc_html

                filing_doc_text = doc.find("text")

                if filing_doc_text:
                    filing_doc_text = filing_doc_text.extract()
                else:
                    logging.warning("No text found in document_data in parser.py")
                    continue
                for style in styles:
                    thematic_breaks = filing_doc_text.find_all('hr', style)
                    if len(thematic_breaks) > 0:
                        break

                if len(thematic_breaks) == 0:
                    try:
                        thematic_breaks = filing_doc_text.find_all('div' , {'style': lambda value: value and 'border-bottom: Black 4pt solid' in value} )
                        
                    except:
                        logging.warning("No thematic breaks found in document_data in parser.py")
            
                all_page_numbers =[]
                for thematic_break in thematic_breaks:
                    try:
                        parent = thematic_break.parent
                        grandparent = parent.parent if parent else None
                        previous_sibling = grandparent.previous_sibling if grandparent else None

                        if previous_sibling:
                            page_number = previous_sibling.get_text(strip=True)
                            if page_number:
                                all_page_numbers.append(page_number)
                            else:
                                logging.warning(f"Previous sibling exists but contains no text: {previous_sibling}")
                        elif parent:
                            page_number = parent.get_text(strip=True)
                            if page_number:
                                all_page_numbers.append(page_number)
                            else:
                                logging.warning(f"Parent exists but contains no text: {parent}")
                        else:
                            logging.warning(f"Skipping thematic break due to missing or invalid previous sibling: {thematic_break}")

                    except Exception as e:
                        logging.error(f"Error processing thematic break: {thematic_break}, error: {e}")

                length_of_page_numbers = len(all_page_numbers)
                self.no_of_pages = length_of_page_numbers
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
                    self.master_document_dict[document_id]['page_numbers'] = all_page_numbers
                    # convert all thematic breaks to a string so it can be used for parsing
                    thematic_breaks = [str(thematic_break) for thematic_break in thematic_breaks]
                    
                    # prep the document text for splitting, this means converting it to a string.
                    filing_doc_string = ' '.join(str(filing_doc_text).split())
                    # filing_doc_string = str(filing_doc_text)
                    # handle the case where there are thematic breaks.
                    if len(thematic_breaks) > 0:
                        # define the regex delimiter pattern, this would just be all of our thematic breaks.
                        regex_delimiter_pattern = '|'.join(map(re.escape, thematic_breaks))

                        # split the document along each thematic break.
                        split_filing_string = re.split(regex_delimiter_pattern, filing_doc_string)

                        # store the document itself
                        self.master_document_dict[document_id]['pages_code'] = split_filing_string

                    # handle the case where there are no thematic breaks.
                    elif len(thematic_breaks) == 0:
                        # handles so it will display correctly.
                        split_filing_string = thematic_breaks
                        
                        # store the document as is, since there are no thematic breaks. In other words, no splitting.
                        self.master_document_dict[document_id]['pages_code'] = [filing_doc_string]
                    # else:
                    #     master_document_dict[document_id]['pages_code'] = ["None"]
                    logging.info(f"The document {document_id} was parsed.")
                    logging.info(f"There was {len(all_page_numbers)} page(s) found.")
                    logging.info(f"There was {len(thematic_breaks)} thematic breaks(s) found.")
                else:
                    logging.info(f"The document {document_id} is not relevant.")


        return self.master_document_dict  

    #############################################--DOC DATA EXTRACTION ENDS--###############################################

    #############################################--CONSTRUCT MASTER DICT--##################################################

    def construct_master_dict(self, master_document_dict, header, accession_number):
        self.master_filings_dict[accession_number] = {}
        self.master_filings_dict[accession_number]['sec_header_content'] = header["sec_header"]
        self.master_filings_dict[accession_number]['filing_documents'] = master_document_dict
        return self.master_filings_dict

    #############################################--CONSTRUCT MASTER DICT ENDS--#############################################

    #############################################--NORMALIZE DATA--#########################################################

    def restore_windows_1252_characters(self, restore_string):
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

    def extract_text_from_html(self, html_str):
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
            logging.error(f"Error parsing HTML: {e}")
            return None, None

    def normalize_text_content(self, raw_text):
        """
        Cleans and normalizes raw text extracted from HTML.
        """
        if not raw_text:
            return ''
        # Normalize Unicode characters
        unicode_normalized = unicodedata.normalize('NFKD', raw_text)
        # Restore Windows-specific characters if needed
        restored_text = self.restore_windows_1252_characters(unicode_normalized)
        # Remove excessive whitespace and newlines
        cleaned_text = re.sub(r'\s+', ' ', restored_text).strip()
        return cleaned_text

    def process_document_data(self, filing_docs):
        """
        Processes and normalizes text for each document entry in filing_docs.
        """
        for document_id, document_data in filing_docs.items():
            logging.info(f"Processing document ID: {document_id}")

            if 'pages_code' not in document_data:
                logging.warning(f"No pages_code found for document ID: {document_id}")
                continue

            # Extract the page code from the document
            pages_code = document_data['pages_code']  # Contains HTML as a string

            # Process the <TEXT> content from pages_code
            repaired_pages = {}
            normalized_text = {}
            for page_number, page_html in enumerate(pages_code, start=1):
                # Extract and normalize text from the HTML
                page_soup, raw_text = self.extract_text_from_html(page_html)
                if page_soup is None or raw_text is None:
                    logging.warning(f"Skipping page {page_number} of document {document_id} due to errors.")
                    continue

                # Normalize the extracted text
                cleaned_text = self.normalize_text_content(raw_text)
                # Store the results
                repaired_pages[page_number] = page_soup  # Repaired HTML
                normalized_text[page_number] = cleaned_text  # Cleaned text

            # Update the document data
            document_data['pages_normalized_text'] = normalized_text
            document_data['pages_code'] = repaired_pages
            document_data['pages_numbers_generated'] = list(repaired_pages.keys())

            logging.info(f"Finished processing document ID: {document_id}")
            filing_docs[document_id]['pages_code'] = document_data ['pages_code']
            filing_docs[document_id]['pages_normalized_text'] = document_data ['pages_normalized_text']
            filing_docs[document_id]['pages_numbers_generated'] = document_data ['pages_numbers_generated']
            
        return filing_docs

    def normalize_filing_docs(self, filing_docs):
        """
        Normalizes all documents in the filing_docs dictionary.
        """
        logging.info("Starting normalization of filing documents...")
        doc_norm = self.process_document_data(filing_docs)
        logging.info("Normalization complete.")
        return doc_norm

    #############################################--NORMALIZE DATA ENDS--####################################################

    ##################################################----PARSE HTML----####################################################
    def parse_html_context(self, filing_docs):
        '''
        Extracts text from a complex BeautifulSoup <table> element and formats it for embedding into text.
        Returns a list of dictionaries, where each dictionary represents a row.
        '''
        doc_acumulated_data = ""
        tb_no = [0]
        for document_id, document_data in filing_docs.items():
            print('-' * 80)
            logging.info(f"Extracting data from document ID: {document_id}")
            if 'pages_code' not in document_data:
                logging.warning("No pages code found")
                continue
            
            pages_code = document_data['pages_code']
            if not pages_code:
                logging.warning("No pages code found")
            for page_number, code in pages_code.items():
                print("-" * 80)
                logging.info(f"Extracting data from page number: {page_number}")

                if not code:
                    logging.warning(f"Warning: code is None or empty for page number: {page_number}")
                    continue
                html_body = code.find('body')
                if html_body is None:
                    logging.warning(f"Warning: No <body> tag found in page number: {page_number}")
                    continue

                # Extract text from the <body>
                data_extracted = self.extract_text_context(html_body, tb_no)
                # data_extracted = self.clean_filing_text(data_extracted)
                footer = f"\nPAGE NUMBER: {page_number}\n"
                data_extracted.append(footer)
                page_tuple = ('\n ', page_number, "\n".join(data_extracted) + "\n")
                # with open(f"page{page_number}.txt", "a") as f:
                #     f.write("\n".join(data_extracted) + "\n")
                self.pages.append(page_tuple)
                doc_acumulated_data += "\n"+"\n"+ "\n".join(data_extracted) + "\n"
        return doc_acumulated_data, self.pages
    

    #############################################--PARSE HTML ENDS--########################################################

    #############################################--EXTRACT TEXT--###########################################################

    def extract_text_context(self, element, tb_no, handle_tables=True):
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
                    table_data = self.extract_table_context(child)
                    if table_data:
                        # Append the table text as a single string
                        table_text = f" [TABLE_{tb_no[0] + 1}: {table_data}] "
                        text.append(table_text)
                        tb_no[0] += 1
                else:
                    text.extend(self.extract_text_context(child, tb_no))  # Recursively process non-table tags

        # Remove duplicates while preserving order
        unique_lines = list(dict.fromkeys(text))
        return unique_lines

    #############################################--EXTRACT TEXT ENDS--######################################################

    #############################################--EXTRACT TABLE--##########################################################

    def extract_table_context(self, table_element):
        """
        Extracts text from a BeautifulSoup <table> element and formats it as a tab-separated string.
        """
        rows = []
        headers = []

        # Extract headers (if present)
        all_row = table_element.find_all('tr')
        pos = 0
        # header_row = all_row[0]
        for i, header in enumerate(all_row):
            head = []
            if header:
                # print("header \n", header)
                for cell in header.find_all(['th', 'td']):
                    # colspan = int(cell.get('colspan', 1))  # Handle merged cells
                    # print(colspan)
                    cell_text = cell.get_text(strip=True)
                    # cell_text = ''.join(cell.stripped_strings)
                    # print("cell text \n",cell_text) 
                    if cell_text:
                        head.extend([cell_text])  # Repeat for merged cells
                if len(head) != 0:
                    headers = head
                    pos = i 
                    break

        # Extract rows
        pos = pos + 1
        for row in table_element.find_all('tr')[pos:]:  # Skip the header row
            cells = []
            for cell in row.find_all(['th', 'td']):
                colspan = int(cell.get('colspan', 1))  # Handle merged cells
                cell_text = cell.get_text(strip=True)
                
                

                if cell_text:  # Only add non-empty cells
                    cells.extend([cell_text] * colspan)  # Repeat for merged cells
                else:
                    cells.extend([""] * colspan)  # Add empty strings for empty cells

            if any(cells):  # Only add non-empty rows
                if headers:
                    row_dict = {headers[i]: cells[i] for i in range(len(headers))}  # Map cells to headers
                else:
                    row_dict = {f"col_{i}": cells[i] for i in range(len(cells))}  # Use generic column names
                rows.append(row_dict)

        # Format the table as a string
        table_text = ""
        for row in rows:
            row_text = ",\n ".join([f"{key}: {value}" for key, value in row.items()])
            table_text += row_text + "; "

        return table_text.strip("; ")


    
    

    


    
    #############################################--EXTRACT TABLE ENDS--#####################################################

    def clean_filing_text(self, text):
        # 1. Remove the XML declaration (e.g., <?xml ...?>)
        text = re.sub(r"<\?xml.*?\?>", "", text, flags=re.DOTALL)

        # 2. Remove lines that appear to be XBRL or copyright metadata
        #    Adjust the regex if there are variations in these metadata lines
        text = re.sub(r"XBRL Document Created with the Workiva Platform", "", text)
        text = re.sub(r"Copyright \d{4} Workiva", "", text)

        # 3. Remove any lines that consist only of metadata identifiers (e.g., IDs, hashes)
        text = re.sub(r"r:[\w\-]+,g:[\w\-]+,d:[\w\-]+\s*", "", text)

        # 4. Remove extra whitespace: collapse multiple spaces and newlines
        text = re.sub(r"\n\s*\n", "\n", text)  # collapse multiple newlines
        text = re.sub(r"[ \t]+", " ", text)      # collapse multiple spaces/tabs

        # 5. Trim leading and trailing whitespace
        text = text.strip()

        return text

styles = [
    {'style': lambda value: value and 'width: 100%' in value},  # Style condition using lambda
    {'width': '100%'},  # Checking for an exact width attribute
    {'style': 'page-break-after:always'}]

# path_t = "/Users/akshitsanoria/Desktop/PythonP/data1/AAPL/raw/10-K/filing_14.txt"

# parser = Parser()

# soup_t, empty_file = parser.read_doc(path_t)
# header_data, accession_number, soup_t = parser.header_data_parser(soup_t)
# doc_data = parser.document_data(soup_t, styles)
# normm_data = parser.normalize_filing_docs(doc_data)
# parsed_html, pages = parser.parse_html_context(doc_data)
# with open('/Users/akshitsanoria/Desktop/PythonP/printing_files/extrated.txt', 'w', encoding='utf-8') as file:
#     file.write(parsed_html)

 