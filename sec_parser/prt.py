from sec_parser_st import Parser
from bs4 import BeautifulSoup


# path = '/Users/akshitsanoria/Desktop/PythonP/data1/AAPL/raw/10-K/filing_14.txt'

# soup, check = parser.read_doc(path)


# pretty_html = soup.prettify()

# with open('/Users/akshitsanoria/Desktop/PythonP/printing_files/pretified.txt', 'w', encoding='utf-8') as file:
#     file.write(pretty_html)
path = '/Users/akshitsanoria/Desktop/PythonP/printing_files/table.txt'

with open(path, 'r', encoding='utf-8') as file:
    text = file.read()

try:
    soup = BeautifulSoup(text, 'html5lib')
except Exception as e:
            
            # Fall back to html5lib if lxml fails
    soup = BeautifulSoup(text, 'lxml')



def extract_table_context(table_element):
    """
    Extracts text from a complex BeautifulSoup <table> element and formats it for embedding into text.
    Returns a list of dictionaries, where each dictionary represents a row.
    """
    rows = []
    headers = []
    pos=1
    # Extract headers (if present)
    all_row = table_element.find_all('tr')
    # print(len(all_row))
    # header_row = all_row[0]
    for i, header in enumerate(all_row):
        head = []
        if header:
            # print("header \n", header)
            for cell in header.find_all(['th', 'td']):
                # colspan = int(cell.get('colspan', 1))  # Handle merged cells
                # print(colspan)
                cell_text = cell.get_text(strip=True)
                # print("cell text \n",cell_text) 
                if cell_text:
                    head.extend([cell_text])  # Repeat for merged cells
            if len(head) != 0:
                headers = head
                pos = i 
                break
    # print("Headers \n",headers)
    # Extract headers (if present)
    # header_row = table_element.find('tr')
    # if header_row:
    #     headers = [cell.get_text(strip=True) for cell in header_row.find_all(['th', 'td']) if cell.get_text(strip=True)]
    # print("Headers \n",headers)
    # Extract rows
    pos = pos + 1
    for row in table_element.find_all('tr')[pos:]:  # Skip the header row
        cells = []
        for cell in row.find_all(['th', 'td']):
            # Handle nested elements and empty cells
            cell_text = cell.get_text(strip=True)
            if cell_text:  # Only add non-empty cells
                cells.append(cell_text)
                   
            else:
                cells.append("")  # Add empty string for empty cells

        if cells:  # Only add non-empty rows
            if headers:
                row_dict = {headers[i]: cells[i] for i in range(len(headers))}  # Map cells to headers
            else:
                row_dict = {f"col_{i}": cells[i] for i in range(len(cells))}  # Use generic column names
            rows.append(row_dict)

    return rows

table = soup.find('table')

table_text = extract_table_context(table)
print(type(table_text))
print(len(table_text))
with open('/Users/akshitsanoria/Desktop/PythonP/printing_files/ex_table.txt', 'w', encoding='utf-8') as file:
    text =''
    for d in table_text:
        print(len(d))
        print(d, '\n')
        te = ''
        for k , v in d.items():
            te += k +': '+ v +'\n'
        text += te + '\n'
    file.write(text)