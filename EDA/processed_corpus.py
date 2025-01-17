from bs4 import BeautifulSoup
import os

# Main function to determine the filing type and call the appropriate parser
def parse_html_file(file_path, filing_type):
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
    
    if filing_type == "10-K":
        return parse_10K(soup)
    elif filing_type == "10-Q":
        return parse_10Q(soup)
    elif filing_type == "8-K":
        return parse_8K(soup)
    elif filing_type == "DEF 14A":
        return parse_DEF_14A(soup)
    elif filing_type == "S-1":
        return parse_S1(soup)
    elif filing_type == "13-D":
        return parse_13D(soup)
    else:
        return {"error": "Unknown filing type"}

# 10-K Parser
def parse_10K(soup):
    data = {}
    data['business_overview'] = extract_section(soup, "Item 1.")
    data['risk_factors'] = extract_section(soup, "Item 1A.")
    data['financial_statements'] = extract_tables(soup)
    return data

# 10-Q Parser
def parse_10Q(soup):
    data = {}
    data['financial_statements'] = extract_tables(soup)
    data['md&a'] = extract_section(soup, "Item 2.")
    return data

# 8-K Parser
def parse_8K(soup):
    data = {}
    data['material_events'] = extract_section(soup, "Item 1.01")
    return data

# DEF 14A Parser
def parse_DEF_14A(soup):
    data = {}
    data['executive_compensation'] = extract_tables(soup)
    data['voting_proposals'] = extract_lists(soup)
    return data

# S-1 Parser
def parse_S1(soup):
    data = {}
    data['business_overview'] = extract_section(soup, "Table of Contents")
    data['financial_summary'] = extract_tables(soup)
    return data

# 13-D Parser
def parse_13D(soup):
    data = {}
    data['reporting_person'] = extract_section(soup, "Identity and Background")
    return data

# Helper functions to extract data
def extract_section(soup, header_text):
    section = soup.find(string=lambda text: text and header_text in text)
    if section:
        return section.find_next().get_text()
    return None

def extract_tables(soup):
    tables = soup.find_all('table')
    return [table.get_text() for table in tables]

def extract_lists(soup):
    lists = soup.find_all(['ul', 'ol'])
    return [lst.get_text() for lst in lists]

# Example Usage
file_path = '/Users/akshitsanoria/Desktop/PythonP/data/3M CO/raw/10-K/filing_93.html'
filing_type = '10-K'  # Change based on the type of filing
parsed_data = parse_html_file(file_path, filing_type)

# Print parsed data
for key, value in parsed_data.items():
    print(f"{key}: {value}\n")
