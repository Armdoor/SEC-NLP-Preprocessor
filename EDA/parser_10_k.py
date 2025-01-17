from bs4 import BeautifulSoup
import os

def extract_text_with_cleaning(element):
    """Cleans text by stripping whitespace and collapsing multiple spaces."""
    text = element.get_text(strip=True)
    cleaned_text = ' '.join(text.split())
    return cleaned_text

def load_html(file_path):
    """Loads HTML content from a file and parses it using lxml."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    with open(file_path, 'r', encoding='utf-8') as file:
        return BeautifulSoup(file, 'lxml')

def extract_tables_flexibly(soup):
    """Extracts tables using <table> tags and flexible methods for poorly formatted tables."""
    tables = []
    for table in soup.find_all('table'):  # Proper tables
        rows = []
        for row in table.find_all('tr'):
            cells = [extract_text_with_cleaning(cell) for cell in row.find_all(['td', 'th'])]
            rows.append(cells)
        if rows:  # Add table only if it has content
            tables.append(rows)

    # Handle "pseudo-tables" (e.g., rows/columns formatted using <div>, <span>, or <p>)
    pseudo_tables = soup.find_all(lambda tag: tag.name in ['div', 'p'] and tag.find_all(['div', 'span']))
    for pseudo_table in pseudo_tables:
        rows = []
        for row in pseudo_table.find_all('div', recursive=False):  # Each <div> as a row
            cells = [extract_text_with_cleaning(cell) for cell in row.find_all(['div', 'span'], recursive=False)]
            rows.append(cells)
        if rows:
            tables.append(rows)

    return tables


def parse_html_document(soup):
    """
    Parses the entire HTML document, differentiating between text, tables, and other sections.
    """
    parsed_content = []
    current_section = None
    for element in soup.body.find_all(recursive=False):  # Limit to direct children of <body>
        if element.name == 'table':
            # Extract and store table
            table_data = extract_tables_flexibly(BeautifulSoup(str(element), 'html.parser'))
            parsed_content.append({'type': 'table', 'content': table_data})
        else:
            # Treat as text or section
            text = extract_text_with_cleaning(element)
            if text:  # Skip empty elements
                parsed_content.append({'type': 'text', 'content': text})
    
    return parsed_content


def save_parsed_content(parsed_content, file_name):
    """Saves parsed content to a file."""
    with open(file_name, 'w', encoding='utf-8') as file:
        for item in parsed_content:
            if isinstance(item, dict):  # Ensure item is a dictionary before accessing 'type'
                if item['type'] == 'text':
                    file.write(item['content'] + '\n\n')
                elif item['type'] == 'table':
                    for table in item['content']:
                        for row in table:
                            file.write('\t'.join(row) + '\n')
                        file.write('\n')
            else:
                # Handle the case where item is not a dictionary (optional logging)
                print("Non-dictionary item found:", item)

# Example Usage
file_path = "/Users/akshitsanoria/Desktop/PythonP/data/3M CO/raw/10-K/filing_93.html"
soup = load_html(file_path)
parsed_content = parse_html_document(soup)
save_parsed_content(parsed_content, "parsed_document_fixed.txt")



possible_items = [
        "Business", "Properties", "Legal Proceedings", "Mine Safety Disclosures", "Market for Securities",
        "Selected Financial Data", "Management’s Discussion and Analysis (MD&A)", "Market Risk",
        "Financial Statements and Supplementary Data", "Change in and Disagreements with Accountants",
        "Directors & Executive Officers", "Executive Compensation", "Ownership", "Relations & Related Transactions",
        "Principal Accountant Fees and Services", "Exhibits and Financial Statement Schedules", "Form 10-K Summary"
    ]


import re

def classify_sections_dynamically(soup):
    sections = {}
    current_section = None
    section_content = []

    section_patterns = [
        r"Item\s*1[^\d]*Business",
        r"Item\s*2[^\d]*Properties",
        r"Item\s*3[^\d]*Legal Proceedings",
        r"Item\s*4[^\d]*Mine Safety Disclosures",
        r"Item\s*5[^\d]*Market for Securities",
        r"Item\s*6[^\d]*Selected Financial Data",
        r"Item\s*7[^\d]*Management[’']?s Discussion and Analysis",
        r"Item\s*7A[^\d]*Quantitative and Qualitative Disclosures About Market Risk",
        r"Item\s*8[^\d]*Financial Statements and Supplementary Data",
        r"Item\s*9[^\d]*Change in and Disagreements with Accountants",
        r"Item\s*10[^\d]*Directors[’']? and Executive Officers",
        r"Item\s*11[^\d]*Executive Compensation",
        r"Item\s*12[^\d]*Security Ownership",
        r"Item\s*13[^\d]*Relations and Related Transactions",
        r"Item\s*14[^\d]*Principal Accountant Fees and Services",
        r"Item\s*15[^\d]*Exhibits and Financial Statement Schedules",
        r"Item\s*16[^\d]*Form 10-K Summary"
    ]

    def is_section_header(text):
        for pattern in section_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    for item in soup.body.find_all('div', style=True):
        span_tag = item.find('span', style=True)
        if span_tag and span_tag.get_text(strip=True):
            section_text = extract_text_with_cleaning(span_tag)

            if is_section_header(section_text):
                # Debugging: Print transition between sections
                if current_section:
                    print(f"Ending Section: {current_section}")
                    sections[current_section] = section_content

                print(f"Starting Section: {section_text}")
                current_section = section_text.strip()
                section_content = []
                continue

        if current_section:
            text = extract_text_with_cleaning(item)
            if text:
                section_content.append(text)

    if current_section:
        sections[current_section] = section_content

    return sections


def parser(text):
    section_patterns = [
        r"Item\s*1[^\d]*Business",
        r"Item\s*2[^\d]*Properties",
        r"Item\s*3[^\d]*Legal Proceedings",
        r"Item\s*4[^\d]*Mine Safety Disclosures",
        r"Item\s*5[^\d]*Market for Securities",
        r"Item\s*6[^\d]*Selected Financial Data",
        r"Item\s*7[^\d]*Management[’']?s Discussion and Analysis",
        r"Item\s*7A[^\d]*Quantitative and Qualitative Disclosures About Market Risk",
        r"Item\s*8[^\d]*Financial Statements and Supplementary Data",
        r"Item\s*9[^\d]*Change in and Disagreements with Accountants",
        r"Item\s*10[^\d]*Directors[’']? and Executive Officers",
        r"Item\s*11[^\d]*Executive Compensation",
        r"Item\s*12[^\d]*Security Ownership",
        r"Item\s*13[^\d]*Relations and Related Transactions",
        r"Item\s*14[^\d]*Principal Accountant Fees and Services",
        r"Item\s*15[^\d]*Exhibits and Financial Statement Schedules",
        r"Item\s*16[^\d]*Form 10-K Summary"
    ]
    sections = {}
    current_section = None
    section_content = []

    def is_section_header(text):
        for pattern in section_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    for item in text.body.find_all('div'):
        div_text = "" # Iterate through all <span> elements within the current <div> 
        for span_tag in item.find_all('span'): 
            div_text += extract_text_with_cleaning(span_tag)
        
        if is_section_header(div_text):
            if current_section:
                sections[current_section] = section_content

            current_section = div_text
            section_content = []
            continue
        if current_section:
            text = extract_text_with_cleaning(item)
            if text:
                section_content.append(text)
    if current_section:
        sections[current_section] = section_content

    return sections

  

def save_classified_sections_to_txt(classified_sections, output_file):
    """Saves the dynamically classified sections to a text file."""
    with open(output_file, 'w', encoding='utf-8') as file:
        for section, content in classified_sections.items():
            file.write(f"Section: {section}\n")
            for line in content:
                file.write(f"{line}\n")
            file.write("\n\n")  # Adding extra space between sections

# Example Usage
classified_sections = classify_sections_dynamically(soup)
save_classified_sections_to_txt(classified_sections, 'classified_sections.txt')


classified_sections = parser(soup)
save_classified_sections_to_txt(classified_sections, 'classified_sections2.txt')