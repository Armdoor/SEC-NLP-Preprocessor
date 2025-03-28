import sqlite3
import re
from rapidfuzz import process
import sys
import os
import tqdm


def clean_data(self, data, filing_type):

        if filing_type == '10-K':
              clean_for_10k(data)
        elif filing_type == '8-K':
              clean_for_8k(data)



def clean_for_10k(self, text):
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
        result_str = self.clean_financial_text(result_str.strip())
        return result_str.strip()




