import re
import sys
import os
import re


# nltk.download('')
#Main beginere to cleaning
#  

'''
                              |-> 10-k -> clean_10k_filing-|
read_file -> remove_metadata ->                             clean_data -> remove_unnecessary_data -> remove_stopwords 
                              |-> 8-k

''' 

class FileCleaner:

    def __init__(self, filing_type, com_data):
      self.filing_type= filing_type
      self.com_data = com_data

    def remove_metadata(self):
       text = self.com_data
       if self.filing_type == '10-K':
           text = self.clean_data(text)
           return self.clean_10k_filing(text)
       elif self.filing_type == '8-K':
           return self.clean_8k_filing(text)

    def clean_8k_filing(self, text):
        last_line = "If an emerging growth company, indicate by check mark if the registrant has elected not to use the extended transition period for complying with any new or revised financial accounting standards provided pursuant to Section 13(a) of the Exchange Act."

        last_line_index = text.find(last_line)
        if last_line_index != -1:
            cleaned_text = text[last_line_index + len(last_line):].strip()
        else:
            cleaned_text = text.strip()
      
        return cleaned_text

    def clean_10k_filing(self, text):

       # Only match 'Item X' at the beginning of a line
       item_patterns = re.finditer(r"^Item\s\d+(?:\.\d+)?[A-Za-z]?", text, re.MULTILINE| re.IGNORECASE)
    #    print("len of item_patterns", len(item_patterns))
       # Store matches as tuples: (item_text, start_position)
       matches = [(match.group(), match.start()) for match in item_patterns]
       print("len of matches", len(matches))
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
            #    print(section_data)
           else:
               if last_main_item:
                   result_str += f"\n{section_data}\n\n"
    #    print(len(result_str) )
       with open("/Users/akshitsanoria/Desktop/PythonP/printing_files/clean/resultck10.txt", "w") as f:
           f.write(result_str)
    #    result_str = self.clean_financial_text(result_str.strip())
       return result_str.strip()
    

    # This function cleans the input data by removing header data between specific start and end patterns. It then writes
   # the cleaned text to a file named
    def clean_data(self, data):
       # first remove the header data
       start_pattern = r"PAGE NUMBER: 1"
       end_pattern = r"Check the appropriate box"
       pattern = re.compile(rf"({start_pattern})(.*?)({end_pattern})", re.DOTALL)
       cleaned_text = re.sub(pattern, r"\1\n\3", data).strip()
       # text_to_remove = re.compile( )
       cleaned_text = re.sub(r"PAGE NUMBER: \d*", '', cleaned_text).strip()
       cleaned_text = re.sub(r".*Form 10-K \| \d+.*\n?", '', cleaned_text).strip()
       part_i_index = cleaned_text.find("PART I\nItem 1. Business")
       if part_i_index != -1:
        cleaned_text = cleaned_text[part_i_index:]
    #    cleaned_text = re.sub(r".*?(PART I\nItem 1\. Business)", r"\1", cleaned_text, flags=re.DOTALL).strip()
    #    cd= self.clean_text(cleaned_text)
    #    cd = self.remove_unnecessary_data(cleaned_text)
    #    cd = self.remove_stopwords(cd)
    #    with open("/Users/akshitsanoria/Desktop/PythonP/printing_files/clean/clean_data.txt", "w") as f:
    #        f.write(cd)
       return cleaned_text
    

    

'''
Sentences that contained any of the following non-GAAP measures were then extracted, using a Python script: 
 - Revised Net Income 
 - Earnings Before Interest and Taxes (EBIT) 
 - Earnings Before Interest, Taxes, and Depreciation (EBITDA) 
 - Earnings Before Interest, Taxes, Depreciation, Amortization, and Rent/Restructuring (EBITDAR) 
 - Adjusted Earnings Per Share 
 - Free Cash Flow (FCF) 
 - Core Earnings 
 - Funds From Operations (FFO) 
 - Unbilled Revenue
 - Return on Capital Employed (ROCE) 
 - Non-GAAP 
 - Reconciliation

'''        
    