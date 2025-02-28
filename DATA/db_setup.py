
import psycopg2
# Define the database connection
from models import *

class CleanedData:
    def __init__(self):
        self.conn = psycopg2.connect(database="sec_reports", 
                                        user="postgres", 
                                        host="localhost", 
                                        password="Iowa@25march",  
                                        port=5433)
        self.cur = self.conn.cursor()
        self._create_tables()
        


    def _create_tables(self):
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS Item (
                    item_id SERIAL PRIMARY KEY,
                    identifier VARCHAR(50) NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    description TEXT
                    )
                    """)

        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS Part (
                    part_id SERIAL PRIMARY KEY,
                    part_name VARCHAR(50) NOT NULL
                    )
                    """)

        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS Section (
                    section_id SERIAL PRIMARY KEY,
                    section_name VARCHAR(50) NOT NULL
                    )
                    """)

        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS Report10K (
                    report10k_id SERIAL PRIMARY KEY,
                    part_id INTEGER NOT NULL,
                    item_id INTEGER NOT NULL,
                    FOREIGN KEY (part_id) REFERENCES Part(part_id) ON DELETE CASCADE,
                    FOREIGN KEY (item_id) REFERENCES Item(item_id) ON DELETE CASCADE
                    )
                    """)

        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS Report8K (
                    report8k_id SERIAL PRIMARY KEY,
                    section_id INTEGER NOT NULL,
                    item_id INTEGER NOT NULL,
                    FOREIGN KEY (section_id) REFERENCES Section(section_id) ON DELETE CASCADE, 
                    FOREIGN KEY (item_id) REFERENCES Item(item_id) ON DELETE CASCADE
                    )
                    """)

        self.conn.commit()


    def insert_item(self, item: Item):
        self.cur.execute("""
        INSERT INTO Item (identifier, title, description)
        VALUES (%s, %s, %s)
        RETURNING item_id
        """, (item.identifier, item.title, item.description))
        return self.cur.fetchone()[0]

    def insert_part(self,part: Part):
        self.cur.execute("""
        INSERT INTO Part (part_name)
        VALUES (%s)
        RETURNING part_id
        """, (part.part_name,))
        return self.cur.fetchone()[0]

    def insert_section(self,section: Section):
        self.cur.execute("""
        INSERT INTO Section (section_name)
        VALUES (%s)
        RETURNING section_id
        """, (section.section_name,))
        section_id = self.cur.fetchone()[0]
        if section_id:
            logging.info(f"Section {section.section_name} inserted with id {section_id}")
            return section_id
        else:
            logging.error(f"Section {section.section_name} not inserted")
            return None

    def insert_report10K(self,report10K: Report10K):
        for part_name, part in report10K.parts.items():
            part_id = self.insert_part(part)
            for item_number, item in part.items.items():
                item_id = self.insert_item(item)
                self.cur.execute("""
                INSERT INTO Report10K (part_id, item_id)
                VALUES (%s, %s)
                """, (part_id, item_id))

    def insert_report8K(self,report8K: Report8K):
        for section_number, section in report8K.sections.items():
            logging.info(f"Inserting section {section.section_name} with id {section_number}")
            section_id = self.insert_section(section)
            logging.info(f"Section {section.section_name} with id {section_id} inserted")
            for item_number, item in section.items.items():
                logging.info(f"Inserting item {item.identifier} with id {item_number}")
                item_id = self.insert_item(item)
                self.cur.execute("""
                INSERT INTO Report8K (section_id, item_id)
                VALUES (%s, %s)
                """, (section_id, item_id))

    def close(self):                
        self.cur.close()
        self.conn.close()