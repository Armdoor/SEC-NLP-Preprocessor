import re
import unicodedata
from bs4 import BeautifulSoup, Tag
import logging

    ##############################################--VARIABLE DECLARATION--#################################################
class Parser:
    def __init__(self):
        self.master_document_dict = {}
        self.master_filings_dict ={}
        self.accession_number = ""
        self.no_of_pages = 0
        self.pages = []
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
        pat = r":\s*(\d{8})"
        if not sec_header:
            logging.error("No <SEC-HEADER> tag found in parser.py")
            return {}
        sec_header_text = sec_header.get_text(separator='\n', strip=True)
        match = re.search(pat, sec_header_text)
        if match:
            date = match.group(1)
        else:
            date = ""
        header = {}
        filing_data['filing_date'] = date
        header['sec_header'] = sec_header_text
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
        return header, filing_data

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
            else:
                logging.warning("No document type found in document_data in parser.py")
                continue

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

    def parse_html(self, filing_docs):
        doc_acumulated_data = ""
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

                # Remove <ix:header> tags if present
                for header in code.find_all('ix:header'):
                    header.decompose()

                # Find the <body> tag
                html_body = code.find('body')
                if html_body is None:
                    logging.warning(f"Warning: No <body> tag found in page number: {page_number}")
                    continue

                # Extract text from the <body>
                data_extracted = self.extract_text(html_body)
                page_tuple = (page_number, "\n".join(data_extracted) + "\n")
                self.pages.append(page_tuple)
                doc_acumulated_data += "\n" + "PAGE NUMBER: "+str(page_number)+"\n"+"\n"+ "\n".join(data_extracted) + "\n"
        return doc_acumulated_data, self.pages
    #############################################--PARSE HTML ENDS--########################################################

    #############################################--EXTRACT TEXT--###########################################################

    def extract_text(self, element, handle_tables=True):
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
                    table_text = self.extract_table(child)
                    if table_text:
                        text.append("\n")
                        text.append(table_text)  # Add entire table as a single string
                else:
                    text.extend(self.extract_text(child))  # Recursively process non-table tags

        # Remove duplicates while preserving order
        unique_lines = list(dict.fromkeys(text))
        return unique_lines

    #############################################--EXTRACT TEXT ENDS--######################################################

    #############################################--EXTRACT TABLE--##########################################################


    def extract_table(self, table_element):
        """
        Extracts text from a BeautifulSoup <table> element and formats it as a tab-separated string.
        """
        rows = []
        for row in table_element.find_all('tr'):  # Iterate through table rows
            cells = [cell.get_text(strip=True) for cell in row.find_all(['th', 'td'])]
            if cells:
                rows.append("\t".join(cells))  # Tab-separated values for each row
        return "\n".join(rows) if rows else None


    #############################################--EXTRACT TABLE ENDS--#####################################################



# styles = [
#     {'style': lambda value: value and 'width: 100%' in value},  # Style condition using lambda
#     {'width': '100%'},  # Checking for an exact width attribute
#     {'style': 'page-break-after:always'}  # Checking for a specific page break style
# ]
