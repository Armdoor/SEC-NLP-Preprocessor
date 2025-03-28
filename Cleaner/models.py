import logging

class Item:
    def __init__(self,identifier: str, title: str, description: str = None):
        self.identifier = identifier
        self.title = title
        self.description = description
        self.sub_items = []
    def __repr__(self):
        return f"Item(title='{self.title}')"
    
    def to_dict(self):
        return {
            "identifier": self.identifier,
            "title": self.title,
            "description": self.description,
            "sub_items": [sub_item.to_dict() for sub_item in self.sub_items]
        }


class Part:
    def __init__(self, part_name: str):
        self.part_name = part_name
        self.items = {}

    def add_item(self, item_number: str, item: Item):
        if item_number in self.items:
            raise ValueError(f"Item {item_number} already exists in part {self.part_name}")
        self.items[item_number] = item

    def __repr__(self):
        return f"Part(part_name='{self.part_name}', items={list(self.items.keys())})"


class Report10K:
    def __init__(self):
        self.parts = {}

    def add_part(self, part_name: str, part: Part):
        self.parts[part_name] = part

    def get_part(self, part_name: str):
        return self.parts.get(part_name)
    
    def get_all_parts(self):
        if self.parts is not None:
            return self.parts

    def __repr__(self):
        return f"Report10K(parts={list(self.parts.keys())})"

class Section:
    def __init__(self, section_name: str):
        self.section_name = section_name
        self.items = {}

    def add_item(self, item_number: str, item: Item):
        if item_number in self.items:
            raise ValueError(f"Item {item_number} already exists in section {self.section_name}")
        self.items[item_number] = item

    def get_item(self, item_number: str):
        if item_number in self.items:
            return self.items.get(item_number)
        else:
            logging.error(f"Item {item_number} not found in section {self.section_name}")
    
    def get_all_items(self):
        if self.items is not None:
            return self.items
        else:
            logging.error("No items FOUND")
    
    def __repr__(self):
        return f"Section(section_name='{self.section_name}', items={list(self.items.keys())})"


class Report8K:
    existing_sections = {
            1: " Registrant’s Business and Operations", 2: " Financial Information", 3: "Securities and Trading Markets", 4: " Matters Related to Accountants and Financial Statements", 5: "Corporate Governance and Management", 6: "Asset-Backed Securities*", 7: " Regulation FD", 8: "Other Events", 9: "Financial Statements and Exhibits"
        }
    def __init__(self):
        self.sections = {}
        self.item = {}
    
    def add_section(self, section_number: int, section_name=None):
        if section_number in self.sections:
            raise ValueError(f"Section {section_number} already exists in report")
        if section_number in self.existing_sections:
            self.sections[section_number] = Section(self.existing_sections[section_number])
        else:
            if section_name:
                self.sections[section_number] = Section(section_name)
            else:
                raise ValueError(f"Section name not provided for section {section_number}")
    
    def get_section(self, section_number: int):
        return self.sections.get(section_number)

    def get_all_section(self):
        if self.sections is not None:
            return self.sections
        else:
            logging.error("Section is EMPTY")
            
    def __repr__(self):
        return f"Report8K(sections={list(self.sections.keys())}, item={list(self.item.keys())})"
    
    def get_all_data(self):
        return {
            "sections": {num: section.name for num, section in self.sections.items()},
            "items": dict(self.item) if self.item else None
        }