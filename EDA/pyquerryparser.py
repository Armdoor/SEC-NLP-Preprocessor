from pyquery import PyQuery as pq
import re
import os 
def extract_text_with_cleaning(element):
    """Cleans text by stripping whitespace and collapsing multiple spaces."""
    return ' '.join(element.text().strip().split())

def load_html(file_path):
    """Loads HTML content from a file and parses it using pyquery."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    with open(file_path, 'rb') as file:
        html_content = file.read()
        soup = pq(html_content)

        # Check if any matching div with style exists
        print(soup('div[style]').html())  # Debugging line

        return soup

def extract_tables_flexibly(soup):
    """Extract tables flexibly using pyquery."""
    tables = []
    for table in soup('table'):
        rows = []
        for row in pq(table).find('tr'):
            cells = [extract_text_with_cleaning(cell) for cell in pq(row).find(['td', 'th'])]
            rows.append(cells)
        if rows:
            tables.append(rows)
    return tables

def find_page_breaks(soup):
    """Check for elements with page-break style."""
    return soup('*[style*="page-break-after:always"]')

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
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in section_patterns)

    for item in soup('div[style]'):
        span_tag = pq(item).find('span')
        if span_tag and span_tag.text().strip():
            section_text = extract_text_with_cleaning(span_tag)
            print(f"Found section header: {section_text}")  # Debugging line

            if is_section_header(section_text):
                if current_section:
                    sections[current_section] = section_content

                current_section = section_text.strip()
                section_content = []
                continue

        if current_section:
            text = extract_text_with_cleaning(pq(item))
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
            file.write("\n\n")

file_path = "/Users/akshitsanoria/Desktop/PythonP/data/3M CO/raw/10-K/filing_93.html" # Update with the actual path to your HTML file
soup = load_html(file_path)

# Classify sections dynamically
classified_sections = classify_sections_dynamically(soup)
print(classified_sections)
# Save the classified sections to a text file
output_file = "sections.txt"  # Name of the output text file
save_classified_sections_to_txt(classified_sections, output_file)

# Alternatively, you can use the parser function
# classified_sections2 = parser(soup)
# output_file2 = "classified_sections2.txt"
# save_classified_sections_to_txt(classified_sections2, output_file2)

print("Parsing and classification complete. Results saved to text files.")