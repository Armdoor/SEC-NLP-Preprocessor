


# from db_setup import *
from .models import *
import psycopg2 
import psycopg2.extras
import logging

logging.basicConfig(level=logging.INFO)  # Set logging level

class Importer:
    def __init__(self):
        self.conn = psycopg2.connect(database="sec_reports", 
                                        user="postgres", 
                                        host="localhost", 
                                        password="Iowa@25march",  
                                        port=5432)
        self.cur = self.conn.cursor()
        self._create_tables()
        logging.info("Connected to the database!")
        # except Exception as e:
        #     logging.error(f"Error connecting to the database: {e}")
        #     exit()

    def __del__(self):
        """Close the database connection when the object is deleted"""
        if hasattr(self, 'cur'):
            self.cur.close()
        if hasattr(self, 'conn'):
            self.conn.close()
        logging.info("Database connection closed.")

    def insert_item(self, item: Item):
        """Insert an item into the database and return its ID"""
        item_query = """
        INSERT INTO Item (identifier, title, description)
        VALUES (%s, %s, %s)
        RETURNING item_id
        """
        try:
            self.cur.execute(item_query, (item.identifier, item.title, item.description))
            item_id = self.cur.fetchone()[0]
            self.conn.commit()
            return item_id
        except psycopg2.Error as e:
            self.conn.rollback()
            logging.error(f"Error inserting item: {e.pgcode} - {e.pgerror}")
            raise

    def insert_part(self, part: Part):
        """Insert a part into the database and return its ID"""
        insert_part = """
        INSERT INTO Part (part_name)
        VALUES (%s)
        RETURNING part_id
        """
        try:
            self.cur.execute(insert_part, (part.part_name,))
            part_id = self.cur.fetchone()[0]
            self.conn.commit()
            return part_id
        except psycopg2.Error as e:
            self.conn.rollback()
            logging.error(f"Error inserting part: {e.pgcode} - {e.pgerror}")
            raise

    def insert_section(self, section: Section):
        """Insert a section into the database and return its ID"""
        section_query = """
        INSERT INTO Section (section_name)
        VALUES (%s)
        RETURNING section_id
        """
        try:
            self.cur.execute(section_query, (section.section_name,))
            section_id = self.cur.fetchone()[0]
            self.conn.commit()
            return section_id
        except psycopg2.Error as e:
            self.conn.rollback()
            logging.error(f"Error inserting section: {e.pgcode} - {e.pgerror}")
            raise

    def insert_report10K(self, report10K: Report10K):
        """Insert a 10K report into the database"""
        try:
            for part_name, part in report10K.parts.items():
                part_id = self.insert_part(part)
                for item_number, item in part.items.items():
                    item_id = self.insert_item(item)
                    self.cur.execute("""
                    INSERT INTO Report10K (part_id, item_id)
                    VALUES (%s, %s)
                    """, (part_id, item_id))
            self.conn.commit()
        except psycopg2.Error as e:
            self.conn.rollback()
            logging.error(f"Error inserting Report10K: {e.pgcode} - {e.pgerror}")
            raise

    def insert_report8K(self, report8K: Report8K):
        """Insert an 8K report into the database"""
        try:
            for section_number, section in report8K.sections.items():
                section_id = self.insert_section(section)
                for item_number, item in section.items.items():
                    item_id = self.insert_item(item)
                    self.cur.execute("""
                    INSERT INTO Report8K (section_id, item_id)
                    VALUES (%s, %s)
                    """, (section_id, item_id))
            self.conn.commit()
        except psycopg2.Error as e:
            self.conn.rollback()
            logging.error(f"Error inserting Report8K: {e.pgcode} - {e.pgerror}")
            raise
