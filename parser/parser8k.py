import re
import requests
import unicodedata
from bs4 import BeautifulSoup
    
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

#######################################################################################################


def find_case_insensitive(soup, tag_name):
    """
    Find a tag in a case-insensitive manner.
    """
    for tag in soup.find_all(True):  # True finds all tags
        if tag.name.lower() == tag_name.lower():
            return tag
    return None

doc = "/Users/akshitsanoria/Desktop/PythonP/data1/AAPL/raw/8-K/filing_4.txt"

with open(doc, 'r', encoding='utf-8') as file:
    response_content = file.read()

# Use the HTML parser
soup = BeautifulSoup(response_content, 'html.parser') 

master_document_dict = {}

sec_header = find_case_insensitive(soup, "SEC-HEADER")

if sec_header:
    sec_header_text = sec_header.get_text(separator='\n', strip=True)
    with open("SectionHeader.txt", 'w') as file:
        file.write(sec_header_text)
else:
    print("No <SEC-HEADER> tag found")

header = {}

# Split the text into lines and iterate through it
lines = sec_header_text.splitlines()
current_section = None
current_subsection = None

for line in lines:
    line = line.strip()

    # Skip empty lines
    if not line:
        continue

    # Handle new sections (FILER, COMPANY DATA, etc.)
    if line.endswith(":"):
        section_name = line[:-1].strip()
        
        if section_name == "FILER":
            # Handle FILER section specifically
            current_section = section_name
            if current_section not in header:
                header[current_section] = {}

        elif section_name in ["COMPANY DATA", "FILING VALUES", "BUSINESS ADDRESS", "MAIL ADDRESS", "FORMER COMPANY"]:
            # For subsections, handle them under FILER
            current_subsection = section_name
            header["FILER"][current_subsection] = {}
        
        continue  # Skip to next line after processing section header

    # Handle key-value pairs
    match = re.match(r"(.+?):\s*(.+)", line)
    if match:
        key, value = match.groups()

        # If the current section is FILER, handle subsections
        if current_subsection:
            header["FILER"][current_subsection][key.strip()] = value.strip()

        elif current_section:
            header[current_section][key.strip()] = value.strip()

# Print out the resulting dictionary
import pprint
pprint.pprint(header)