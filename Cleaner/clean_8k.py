from models import *
import re
class Clean8k:

    def __init__(self, text):
        self.text = text

    def structure_of_8k(self, text,report):
        pattern = re.finditer(r'item (\d+)\.(.*)', text, re.MULTILINE| re.IGNORECASE)
        matches = [(match.group(), match.start()) for match in pattern]
        for i, (item, start_pos) in enumerate(matches):
            # print(i, item, start_pos)
            if item:
                item_head = r"Item\s+([\d.]+)\s+(.+)"
                match = re.match(item_head , item, re.IGNORECASE)
                if match:
                    item_number = match.group(1)
                    item_title = match.group(2)
                    section_number = int(item_number.split('.')[0])
                    section= report.add_section(section_number)
                    section= report.get_section(section_number)
                    if section_number in report.sections:
                        new_item = self.create_item(item_number,item_title,i, start_pos, matches, text)
                        # print(type(section)) 211
                        section.add_item(item_number, new_item)

    def create_item(self, item_number, item_title, i:int, start_pos, matches, text):
        end_pos = matches[i + 1][1] if i + 1 < len(matches) else len(text)
        section_data = text[start_pos:end_pos].strip()
        
            
        insert_item = Item(item_number, item_title, description=section_data)

        return insert_item


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