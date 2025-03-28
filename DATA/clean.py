import re
from clean_10k import *
from models import *

class Cleaner:

    def removemetadata(self, text, filing_type):
        # first remove the header data 
        start_pattern = r"PAGE NUMBER: 1"
        end_pattern = r"Check the appropriate box"
        pattern = re.compile(rf"({start_pattern})(.*?)({end_pattern})", re.DOTALL)
        cleaned_text = re.sub(pattern, r"\1\n\3", text).strip()
        # if filing_type == '8-K':
        #     return 
        return cleaned_text


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


path = '/Users/akshitsanoria/Desktop/PythonP/cleaned_text_10k.txt'
with open(path, "r") as f:
    text = f.read()

clean = Cleaner()
data = clean.removemetadata(text, '10-K')
with open("/Users/akshitsanoria/Desktop/PythonP/printing_files/cle.txt", "w") as f:
    f.write(data)

report = convert_10k(data)
all_data = report.get_all_parts()
val = ''
for k,v in all_data.items():
    val += f"{k}: {v}\n"
with open("/Users/akshitsanoria/Desktop/PythonP/printing_files/all_data.txt", "w") as f:
    f.write(val)

# text.__repr__()