


# from db_setup import *
from .models import *
import psycopg
# import psycopg.extras
import logging
import os 

logging.basicConfig(level=logging.INFO)  # Set logging level

class Importer:
    def __init__(self):
        try:
            self.conn = psycopg.connect(
                                    host=os.environ.get("DB_HOST"),
                                    port=os.environ.get("DB_PORT"),
                                    user=os.environ.get("DB_USER"),
                                    password=os.environ.get("DB_PASSWORD"),
                                    dbname=os.environ.get("DB_NAME"))
            self.conn.autocommit = True
            self.cur = self.conn.cursor()
            logging.info("Connected to the database.")
            # self.cur = self.conn.cursor()
        except Exception as e:
            logging.error(f"Error connecting to the database: {e}")
            exit()
    def create_tables(self):
        try:
            

            # Create Item table
            self.cur.execute("""
            CREATE TABLE IF NOT EXISTS Item (
                item_id SERIAL PRIMARY KEY,
                identifier VARCHAR(255) NOT NULL,
                title TEXT NOT NULL,
                description TEXT
            );
            """)

            # Create Part table
            self.cur.execute("""
            CREATE TABLE IF NOT EXISTS Part (
                part_id SERIAL PRIMARY KEY,
                part_name VARCHAR(255) NOT NULL
            );
            """)

            # Create Section table
            self.cur.execute("""
            CREATE TABLE IF NOT EXISTS Section (
                section_id SERIAL PRIMARY KEY,
                section_name VARCHAR(255) NOT NULL
            );
            """)

            logging.info("Tables created successfully.")
            # self.cur.close()
            # self.conn.close()
        except Exception as e:
            logging.error(f"Error creating tables: {e}")



    def __del__(self):
        """Close the database connection when the object is deleted"""
        if hasattr(self, 'cur'):
            self.cur.close()
        if hasattr(self, 'conn'):
            self.conn.close()
        if logging:
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
        except psycopg.Error as e:
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
        except psycopg.Error as e:
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
        except psycopg.Error as e:
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
        except psycopg.Error as e:
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
        except psycopg.Error as e:
            self.conn.rollback()
            logging.error(f"Error inserting Report8K: {e.pgcode} - {e.pgerror}")
            raise





imp = Importer()