from bs4 import BeautifulSoup
import os  # Added for file path checking

def extract_text_with_cleaning(element):
    # Get the text and strip leading/trailing whitespace
    text = element.get_text(strip=True)
    # Replace multiple spaces with a single space
    cleaned_text = ' '.join(text.split())
    return cleaned_text


def load_html(file_path):
    if not os.path.exists(file_path):  # Check if the file exists
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    with open(file_path, 'r', encoding='utf-8') as file:
        return BeautifulSoup(file, 'xml')

soup = load_html("/Users/akshitsanoria/Desktop/PythonP/data/3M CO/raw/10-K/filing_93.html")
# print(soup)

with open('soup.txt', 'w', encoding='utf-8') as file: 
    for content in soup: 
        file.write(f"{content}")

def extract_sections_by_tags(soup, tag_name):
    sections = {}
    headers = soup.find_all(tag_name)  # Find all headers (e.g., <h2>)
    for header in headers:
        next_tag = header.find_next()  # Get the content after the header
        # Clean the header and the content
        cleaned_header = extract_text_with_cleaning(header)
        cleaned_content = extract_text_with_cleaning(next_tag) if next_tag else None
        sections[cleaned_header] = cleaned_content
    return sections


sections = extract_sections_by_tags(soup, 'span')
with open('sections.txt', 'w', encoding='utf-8') as file: 
    for header, content in sections.items(): 
        file.write(f"{header}\n{content}\n\n")



def extract_section(soup, section_name):
    header = soup.find('h2', string=section_name)
    if header:
        content = []
        next_tag = header.find_next_sibling()  # Get the next sibling
        while next_tag and next_tag.name != 'h2':  # Stop at the next section
            content.append(next_tag.get_text(strip=True))
            next_tag = next_tag.find_next_sibling()
        return ' '.join(content)
    return None



import csv

def save_table_to_csv(table, file_name):
    if table:  # Check if the table is not None or empty
        with open(file_name, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(table)
    else:
        print("No data to save to CSV.")







def extract_tablesSt(soup):
    tables = []
    for table in soup.find_all('table'):
        rows = []
        for row in table.find_all('tr'):  # Find rows
            cells = [extract_text_with_cleaning(cell) for cell in row.find_all(['td', 'th'])]  # Clean cell text
            rows.append(cells)
        tables.append(rows)  # Store each table as a list of rows
    return tables

def save_tables_to_txt(tables, file_name):
    with open(file_name, 'w', encoding='utf-8') as file:
        for table in tables:
            for row in table:
                file.write('\t'.join(row) + '\n')  # Join cells with a tab for structure
            file.write('\n')  # Add a newline between tables

# Usage
tables = extract_tablesSt(soup)
save_tables_to_txt(tables, "tables.txt")

save_table_to_csv(tables, "or.csv")