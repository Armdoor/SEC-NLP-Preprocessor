import sqlite3
import re
from rapidfuzz import process
import sys
import os
import tqdm

sys.path.append(os.path.abspath("/Users/akshitsanoria/Desktop/PythonP"))
from sec_parser.load import Loader

class FilingCleaner:

    # def __init__(self):
        # self.name = name
        # self.filing_id = filing_id
        # self.company_id = company_id
        # self.loader = Loader()

    
    def find_closest_pattern(self, pattern, text, threshold=85):
        # Search for closest substring in the text
        match, score, _ = process.extractOne(pattern, text.splitlines(), score_cutoff=threshold)
        print(match)
        return match

    def clean_data(self, data):

        # first remove the header data 
        start_pattern = r"PAGE NUMBER: 1"
        end_pattern = r"Check the appropriate box"
        pattern = re.compile(rf"({start_pattern})(.*?)({end_pattern})", re.DOTALL)
        cleaned_text = re.sub(pattern, r"\1\n\3", data).strip()
        
        # text_to_remove = re.compile( )
        cleaned_text = re.sub(r"PAGE NUMBER: \d*", '', cleaned_text).strip()
        with open("cleaned_text.txt", "w") as f:
            f.write(cleaned_text)

    def remove_unnecessary_data_8k(self, item_info, text):
        start_input = item_info[0]
        end_input = item_info[-1]
        start_pattern = self.find_closest_pattern(start_input, text) or start_input
        end_pattern = self.find_closest_pattern(end_input, text) or end_input

        if start_pattern and end_pattern and start_pattern != end_pattern:
            match = re.search(rf"{re.escape(start_pattern)}(.*?){re.escape(end_pattern)}", text, re.DOTALL)
            relevant_data = match.group(1) if match else ""
        else:
            print("No distinct start and end patterns found.")
            match = re.search(rf"{re.escape(start_pattern)}(.*)", text, re.DOTALL)
            relevant_data =  match.group(0) if match else ""
            # relevant_data = match.group(0) +'\n' + relevant_data
        with open("relevant_text.txt", "w") as f:
            f.write(relevant_data)
        matches = re.findall(r"Item\s\d+(?:\.\d+)?", text)
        print(matches)
        
        print("Relevant data successfully written to 'relevant_text.txt'")







# def clean_pages(company_name):
#     loader = Loader()
#     filing = loader.fetch_by_name(company_name)

#     company_id = filing['company_id']
#     footer_pattern = re.compile(r"^.*\|\s*\d{4}\s+Form\s+10-K\s*\|\s*\d+\s*$", re.IGNORECASE)

#     filings = loader.fetch_filing(company_id)
#     accession_number = filings['accession_number']
#     pages = loader.fetch_pages('0')
#     with open("pages.txt", "w") as f:
#         accumulator = ""
#         for page in pages:
#             if page['page_number'] in {1, 2}:  # Skip pages 1 and 2
#                 continue 

#             page_content = page['page_content']
#             # Remove trailing newlines to avoid empty splits
#             page_content = page_content.rstrip('\n')
#             # Split into lines and remove the last line
#             lines = page_content.split('\n')
#             if lines:  # Ensure there are lines to process
#                 lines = lines[:-1]  # Remove the last line (footer)
#             lines = clean_financial_text(lines)
#             # Rejoin the cleaned lines and add to accumulator
            
#             accumulator +=  lines + "\n"
        
#         # Write the cleaned content to the file
#         f.write(accumulator.strip())

#     return clean_10k_filing(accumulator)

# def clean_financial_text(lines):
#     if isinstance(lines, list):
#         cleaned_lines = []
        
#         for line in lines:
#             # Remove unwanted characters but keep spaces and financial symbols
#             cleaned_line = re.sub(r"[^A-Za-z0-9\s.,%$()-]", "", line)
#             cleaned_line = re.sub(r"\s+", " ", cleaned_line).strip()  # Normalize spaces
#             cleaned_lines.append(cleaned_line.lower())
        
#         return "\n".join(cleaned_lines)  # Join back lines preserving structure
#     else:
#         raise TypeError("Expected list of strings, got something else.")
def clean_pages(company_name):
    loader = Loader()
    filing = loader.fetch_by_name(company_name)

    company_id = filing['company_id']

    accession_number = '0000320193-24-000123'
    filings = loader.fetch_filing(company_id, accession_number)
    # accession_number = filings['accession_number']
    pages = loader.fetch_pages('174', accession_number)
    print(type(pages))

    with open("pages.txt", "w") as f:
        accumulator = ""
        for page in pages:
            if page['page_number'] in {1, 2}:  # Skip pages 1 and 2
                continue 

            page_content = page['page_content']
            # Remove trailing newlines to avoid empty splits
            page_content = page_content.rstrip('\n')
            # Split into lines and remove the last line
            lines = page_content.split('\n')
            if lines:  # Ensure there are lines to process
                lines = lines[:-1]  # Remove the last line (footer)
            lines = '\n'.join(lines)
            # print('len of lines', len(lines) , type)
            # lines = clean_financial_text(lines)
            
            # Rejoin the cleaned lines and add to accumulator
            accumulator += lines 
        
        # Write the cleaned content to the file
        f.write(accumulator.strip())
        print('type of accumulator', type(accumulator), len(accumulator))
        with open("clean.txt", "w") as f:
            f.write(accumulator)
    accumulator = clean_10k_filing(accumulator)
    print('len of accumulator', len(accumulator))
    return accumulator

def clean_10k_filing(text):
    print('len of text', len(text))
    # Only match 'Item X' at the beginning of a line
    item_patterns = re.finditer(r"^Item\s\d+(?:\.\d+)?[A-Za-z]?", text, re.MULTILINE| re.IGNORECASE)
    
    # Store matches as tuples: (item_text, start_position)
    matches = [(match.group(), match.start()) for match in item_patterns]
    print('len of matches', len(matches))
    result_str = ''
    last_main_item = None
    
    for i, (item, start_pos) in enumerate(matches):
        # Find the end boundary (start of next item or end of text)
        end_pos = matches[i + 1][1] if i + 1 < len(matches) else len(text)
        
        # Extract the section data
        section_data = text[start_pos:end_pos].strip()
        
        # Check if the item is a main section (e.g., "Item 1") or a subsection
        if re.match(r"^Item\s\d+$", item, re.IGNORECASE):
            last_main_item = item
            result_str += f"\n{section_data}\n\n"
        else:
            if last_main_item:
                result_str += f"\n{section_data}\n\n"
    with open("result.txt", "w") as f:
        f.write(result_str)
    result_str = clean_financial_text(result_str.strip())
    return result_str.strip()



def clean_financial_text(lines):
    # if isinstance(lines, list):
        lines = lines.splitlines()  
        cleaned_lines = []
        
        for line in lines:
            # Remove unwanted characters but keep spaces and financial symbols
            cleaned_line = re.sub(r"[^A-Za-z0-9\s.,%$()\[\]{}-]", "", line)
            cleaned_line = re.sub(r"\s+", " ", cleaned_line).strip()  # Normalize spaces
            cleaned_lines.append(cleaned_line.lower())  # Convert to lowercase
        
        return ("\n".join(cleaned_lines))  # Join back lines preserving structure
    # else:
    #     raise TypeError("Expected list of strings, got something else.")


# path = "/Users/akshitsanoria/Desktop/PythonP/data1/AAPL/preprocessed/10-K/filing_14_data.txt"
# with open(path, "r") as f:
#     text = f.read()

data = clean_pages("Apple Inc.")
with open("cleaned_text_10k.txt", "w") as f:    
    f.write(data)




def clean_text(text):
    # Remove extra spaces and line breaks
    text = re.sub(r'\s+', ' ', text).strip()
    # Fix possessive apostrophes
    text = re.sub(r"Companys", "Company’s", text)
    return text


def format_sections(text):
    # Break sections based on keywords like "Products"
    sections = re.split(r"(?i)(?=Products|Business|Background)", text)
    return "\n\n".join(f"- {section.strip()}" for section in sections if section.strip())

def process_files(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in tqdm(os.listdir(input_folder)):
        if filename.endswith(".txt"):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            with open(input_path, "r", encoding="utf-8") as file:
                raw_text = file.read()

            # Clean and format text
            cleaned_text = clean_text(raw_text)
            organized_text = format_sections(cleaned_text)

            # Save the cleaned text to the output folder
            with open(output_path, "w", encoding="utf-8") as file:
                file.write(organized_text)

    print("Processing complete!")





# so right now i am fetching the caompany data but what if only want to fetch company if and 



text ='''
PAGE NUMBER: 1

UNITED STATES
SECURITIES AND EXCHANGE COMMISSION
Washington, D.C. 20549
FORM
8-K
CURRENT REPORT
Pursuant to Section 13 or 15(d) of the Securities Exchange Act of 1934
December 26, 2024
Date of Report (Date of earliest event reported)
TPI Composites, Inc.
(Exact name of registrant as specified in its charter)


Delaware	001-37839	20-1590775
(State or other jurisdictionof incorporation)	(CommissionFile Number)	(I.R.S. EmployerIdentification No.)
9200 E. Pima Center Parkway
,
Suite 250
Scottsdale
Arizona
85258
(Address of principal executive offices) (Zip Code)
480
-
305-8910
(Registrant’s telephone number, including area code)
Not applicable
(Former name or former address, if changed since last report)
Check the appropriate box below if the Form 8-K filing is intended to simultaneously satisfy the filing obligation of the registrant under any of the following provisions:
☐	Written communications pursuant to Rule 425 under the Securities Act (17 CFR 230.425)
☐	Soliciting material pursuant to Rule 14a-12 under the Exchange Act (17 CFR 240.14a-12)
☐	Pre-commencement communications pursuant to Rule 14d-2(b) under the Exchange Act (17 CFR 240.14d-2(b))
☐	Pre-commencement communications pursuant to Rule 13e-4(c) under the Exchange Act (17 CFR 240.13e-4(c))
Securities registered pursuant to Section 12(b) of the Act:
Title of each class	Trading Symbol(s)	Name of each exchange on which registered
Common Stock, par value $0.01	TPIC	NASDAQ Global Market
Indicate by check mark whether the registrant is an emerging growth company as defined in Rule 405 of the Securities Act of 1933 (§230.405 of this chapter) or Rule 12b-2 of the Securities Exchange Act of 1934 (§240.12b-2 of this chapter).
Emerging growth company
☐
If an emerging growth company, indicate by check mark if the registrant has elected not to use the extended transition period for complying with any new or revised financial accounting standards provided pursuant to Section 13(a) of the Exchange Act. ☐
Item 2.05	Costs Associated with Exit or Disposal Activities.
In December 2024, TPI Composites, Inc. (the Company) committed to a restructuring plan in order to rationalize its workforce in Türkiye in response to lower forecasted demand in 2025 for wind blades primarily exported by the Company’s customers to the European market. This decline in forecasted demand is primarily attributed to the hyperinflationary environment in Türkiye, as previously disclosed in the Company’s Quarterly Report on Form 10-Q for the quarter ended September 30, 2024.
The Company is reducing its headcount at its Turkish manufacturing facilities by approximately 20%. The Company currently estimates that it will recognize pre-tax charges for severance and other one-time termination benefits in the range of $9 million to $11 million. These charges are expected to be paid in January 2025.
The Company may incur other charges or cash expenditures not currently contemplated due to unanticipated events that may occur as a result of or in connection with the implementation of the restructuring plan. The Company intends to exclude the charges associated with the restructuring plan from its non-GAAP financial measures.
Forward-Looking Statements
This Current Report on Form 8-K contains forward-looking statements within the meaning of the federal securities laws. All statements other than statements of historical facts contained in this Current Report on Form 8-K are forward-looking statements. In many cases, you can identify forward-looking statements by terms such as “may,” “should,” “expects,” “plans,” “anticipates,” “could,” “intends,” “target,” “projects,” “contemplates,” “believes,” “estimates,” “predicts,” “potential” or “continue” or the negative of these terms or other similar words. Forward-looking statements may involve known and unknown risks, uncertainties and other factors that may cause the Company’s actual results, performance or achievements to be materially different from those expressed or implied by the forward-looking statements. These statements include, but are not limited to, the size and scope of the restructuring plan; the number of employee positions that will be affected; the estimate and timing of the charges that we expect to incur in connection with the plan; and the impact on the Company’s financial results. Except as required by law, the Company assumes no obligation to update these forward-looking statements publicly, or to update the reasons actual results could differ materially from those anticipated in the forward-looking statements, even if new information becomes available in the future. Further information on factors that could cause the Company’s actual results to differ materially from the results anticipated by the Company’s forward-looking statements is included in the reports the Company has filed with the U.S. Securities and Exchange Commission, including the Company’s Quarterly Report on Form 10-Q for the quarter ended September 30, 2024 and Annual Report on Form 10-K for the year ended December 31, 2023.
SIGNATURE
Pursuant to the requirements of the Securities Exchange Act of 1934, the registrant PAGE NUMBER: 189 has duly caused this report to be signed on its behalf by the undersigned hereunto duly authorized.
	TPI Composites, Inc.
		PAGE NUMBER: 167
Date: December 31, 2024	By:	/s/ Ryan Miller
		Ryan Miller
		Chief Financial Officer
'''

cleaner = FilingCleaner()
# cleaner.clean_data(text)
# item_info = ["Cost Associated with Exit or Disposal Activities"]
# cleaner.remove_unnecessary_data_8k(item_info, text)



