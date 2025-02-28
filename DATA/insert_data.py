from db_setup import *
from models import *


class importer():
    def __init__(self):
        self.cleaned_data = CleanedData()

    def insert_item(self, item: Item):
        self.cleaned_data.cur.execute("""
        INSERT INTO Item (identifier, title, description)
        VALUES (%s, %s, %s)
        RETURNING item_id
        """, (item.identifier, item.title, item.description))
        return self.cleaned_data.cur.fetchone()[0]

    def insert_part(self,part: Part):
        self.cleaned_data.cur.execute("""
        INSERT INTO Part (part_name)
        VALUES (%s)
        RETURNING part_id
        """, (part.part_name,))
        return self.cleaned_data.cur.fetchone()[0]

    def insert_section(self,section: Section):
        self.cleaned_data.cur.execute("""
        INSERT INTO Section (section_name)
        VALUES (%s)
        RETURNING section_id
        """, (section.section_name,))
        return self.cleaned_data.cur.fetchone()[0]

    def insert_report10K(self,report10K: Report10K):
        for part_name, part in report10K.parts.items():
            part_id = self.insert_part(part)
            for item_number, item in part.items.items():
                item_id = self.insert_item(item)
                self.cleaned_data.cur.execute("""
                INSERT INTO Report10K (part_id, item_id)
                VALUES (%s, %s)
                """, (part_id, item_id))

    def insert_report8K(self,report8K: Report8K):
        for section_number, section in report8K.sections.items():
            section_id = self.insert_section(section)
            for item_number, item in section.items.items():
                item_id = self.insert_item(item)
                self.cleaned_data.cur.execute("""
                INSERT INTO Report8K (section_id, item_id)
                VALUES (%s, %s)
                """, (section_id, item_id))

    # self.cleaned_data.conn.commit()
    # self.cleaned_data.conn.close()    

