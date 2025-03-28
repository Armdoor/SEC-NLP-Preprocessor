
import re
from models import Report10K, Part, Item
from Normalization import Normalizer
PARTS_MAPPING = {"1": "PART 1", "1A": "PART 1","1B": "PART 1","1C": "PART 1", 
                 "2": "PART 1", "3": "PART 1", "4": "PART 1", "5": "PART 2",
                 "6": "PART 2", "7": "PART 2", "7A": "PART 2", "8": "PART 2",
                 "9": "PART 2", "9A": "PART 2", "9B": "PART 2", "9C": "PART 2",
                 "10": "PART 3", "11": "PART 3", "12": "PART 3", "13": "PART 3",
                 "14": "PART 3", "15": "PART 4", "16": "PART 4"}

class Clean10k:
    
    def __init__(self, text):
        self.text = text
        
# print(PARTS_MAPPING.get("1"))

    def structure_of_10k(self, text, report):
        normalizer = Normalizer(text)
        text = normalizer.clean_text(text)
        text = normalizer.remove_unnecessary_data(text)
        text = normalizer.remove_stopwords(text)
        pattern = re.finditer(r"^item\s+(\d+[A-Za-z]*)", text, re.MULTILINE| re.IGNORECASE)
        matches = [(match.group(), match.start()) for match in pattern]
        # print(matches)
        for i ,(item, start_pos) in enumerate(matches):
            part_id= str(i+1)  
            part_name = PARTS_MAPPING[part_id] if part_id in PARTS_MAPPING else None
            if not part_name:
                continue

            part = report.get_part(part_name)
            if not part:
                part = Part(part_name)
                report.add_part(part_name, part)

            new_item, identifier = self.create_part(i, start_pos, matches, text)
            part.add_item(identifier, new_item)
        
        

    def create_part(self, i, start_pos, matches, text, item_id=None):
        end_pos = matches[i + 1][1] if i + 1 < len(matches) else len(text)
        section_data = text[start_pos:end_pos].strip()
        pattern = r"item\s+(\d+[A-Za-z]*)\.\s+(.+)"
        
        split_item = re.match(pattern, section_data, re.IGNORECASE)
        if not split_item:
            identifier = f"Unknown-{i}"
            title = "Untitled"
        else:
            identifier = split_item.group(1)
            title = split_item.group(2)
            
        insert_item = Item(identifier, title, description=section_data)

        return insert_item, identifier



    def convert_10k(self, text ):
        # with open(path, "r") as f:
        #     text = f.read()
        report = Report10K()
        self.structure_of_10k(text, report)
        return report

    # part1 = report.get_part("PART 1")
    # print(part1 == None)
    # if part1:
    #     item1 = part1.items.get("1")
    #     print(f"Item 1 Title: {item1.title}")
    #     print(f"Item 1 Description Length: {len(item1.description)} characters")
    #     with open("item1.txt", "w") as f:
    #         f.write(item1.description)