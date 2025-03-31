from .models import *
import re
from .Normalization import Normalizer


class Clean8k:

    def __init__(self, text):
        self.text = text

    # def structure_of_8k(self, text,report):
    #     normalizer = Normalizer(text)
    #     text = normalizer.clean_text(text)
    #     text = normalizer.remove_unnecessary_data(text)
    #     text = normalizer.remove_stopwords(text)
    #     pattern = re.finditer(r'\bitem (\d+\.\d+)\b(.*)', text, re.MULTILINE| re.IGNORECASE)
    #     matches = [(match.group(), match.start()) for match in pattern]
    #     print("matches : ", len(matches))
    #     path1 = "/Users/akshitsanoria/Desktop/PythonP/printing_files/clean/num1.txt"
    #     with open(path1, "w") as f :
    #         f.write(f"{text} \n")
    #     # path2 = "/Users/akshitsanoria/Desktop/PythonP/printing_files/clean/num2.txt"
    #     for i, (item, start_pos) in enumerate(matches):
    #         # print(i, item, start_pos)
    #         if item:
    #             item_head = r"Item\s+([\d.]+)\s+(.+)"
    #             match = re.match(item_head , item, re.IGNORECASE)
    #             if match:
    #                 # print("start pos: ", start_pos)
    #                 # print("str pos str: " , text[start_pos:start_pos+20])
    #                 item_number = match.group(1)
    #                 item_title = match.group(2)
                   
    #                 # with open(path2, "w") as f :
    #                 #     f.write(f"{item_title} \n")
    #                 section_number = int(item_number.split('.')[0])
    #                 section= report.add_section(section_number)
    #                 section= report.get_section(section_number)
    #                 if section_number in report.sections:
    #                     new_item = self.create_item(item_number,item_title,i, start_pos, matches, text)
    #                     # print(type(section)) 211
    #                     section.add_item(item_number, new_item)

    # def create_item(self, item_number, item_title, i:int, start_pos, matches, text):
    #     end_pos = matches[i + 1][1] if i + 1 < len(matches) else len(text)
    #     section_data = text[start_pos:end_pos].strip()
        
            
    #     insert_item = Item(item_number, item_title, description=section_data)

    #     return insert_item
    def structure_of_8k(self, text, report):
        normalizer = Normalizer(text)
        text = normalizer.clean_text(text)
        text = normalizer.remove_unnecessary_data(text)
        text = normalizer.remove_stopwords(text)

        # Improved regex to match item headers like "Item 2.02", "Item 9.01", etc.
        item_pattern = re.compile(
            r'\bItem\s+(\d+\.\d+)\b[:\s]*(.*?)(?=\bItem\s+\d+\.\d+\b|$)', 
            re.IGNORECASE | re.DOTALL
        )

        matches = list(item_pattern.finditer(text))
        print("matches:", len(matches))

        for i, match in enumerate(matches):
            item_number = match.group(1).strip()
            item_title = match.group(2).strip()
            item_content = match.group(0).strip()  # Entire matched text (header + content)

            # Extract section number (e.g., "2" from "2.02")
            section_number = int(item_number.split('.')[0])

            # Add section to report if not already present
            if section_number not in report.sections:
                report.add_section(section_number)
            section = report.get_section(section_number)

            # Create and add the item
            new_item = self.create_item(item_number, item_title, item_content)
            section.add_item(item_number, new_item)

    def create_item(self, item_number, item_title, item_content):
        """
        Creates an Item object with the given number, title, and content.
        """
        return Item(item_number, item_title, description=item_content)


    # path= "/Users/akshitsanoria/Desktop/PythonP/data1/AAPL/preprocessed/8-K/filing_1_data.txt"
    def data_8k(self):
        # with open(path, "r") as f:
        #     text = f.read()

        report = Report8K()
        self.structure_of_8k(self.text, report)
        return report

    # print(report.__repr__())
    # rep = report.get_section(2)
    # print(rep)
    # if rep:
    #     item1 = rep.items.get("2.05")
    #     with open("/Users/akshitsanoria/Desktop/PythonP/printing_files/item1_8k.txt", "w") as f:
    #         f.write(item1.description)

# with open("/Users/akshitsanoria/Desktop/PythonP/Testing_Folder/AAPL/preprocessed/8-K/filing_15_data.txt", "r") as f:
#     text = f.read()
# clean = Clean8k(text)
# clean.data_8k()

