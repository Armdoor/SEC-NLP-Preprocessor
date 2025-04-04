


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
                                    host="database-1.c9ko8uwa4nsf.us-east-1.rds.amazonaws.com",
                                    port=5432,
                                    user="bojackhorse",
                                    password="Iowa+25march",
                                    dbname="postgres")
            self.conn.autocommit = True
            self.cur = self.conn.cursor()
            logging.info("Connected to the database.")
            # self.cur = self.conn.cursor()
        except Exception as e:
            logging.error(f"Error connecting to the database: {e}")
            exit()

    def create_tables(self):
        try:
            # Create the Company table
            self.cur.execute("""
            CREATE TABLE IF NOT EXISTS Company (
                company_id SERIAL PRIMARY KEY,
                company_name VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );          
            """)

            # Create Item table
            self.cur.execute("""
            CREATE TABLE IF NOT EXISTS Item (
                item_id SERIAL PRIMARY KEY,
                filing_type VARCHAR(255) NOT NULL,
                identifier VARCHAR(255) NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                section_id INTEGER REFERENCES Section(section_id)
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
                section_name VARCHAR(255) NOT NULL,
                report_id INTEGER NOT NULL REFERENCES Report8K(report_id)
            );
            """)

            # Create Report8K table
            self.cur.execute("""
            CREATE TABLE IF NOT EXISTS Report8K(
                report_id SERIAL PRIMARY KEY,
                company_id INTEGER NOT NULL REFERENCES Company(company_id),
                accession_number VARCHAR(255) NOT NULL,
                filing_type VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
            """)

            logging.info("Tables created successfully.")
            # self.cur.close()
            # self.conn.close()
        except Exception as e:
            logging.error(f"Error creating tables: {e}")

    def insert_company(self, company_name: str) -> int:
        """
        Insert a company into the Company table and return its company_id.
        """
        company_query = """
        INSERT INTO Company (company_name)
        VALUES (%s)
        RETURNING company_id;
        """
        self.cur.execute(company_query, (company_name,))
        company_id = self.cur.fetchone()[0]
        return company_id

    def insert_report8K(self, company_id: int, accession_number, filing_type="8-K"):
        """Insert an 8K report into the database"""
        report_query = """
        INSERT INTO Report8K (company_id, accession_number, filing_type)
        VALUES (%s, %s, %s)
        RETURNING report_id;
        """
        self.cur.execute(report_query, (company_id, accession_number, filing_type))
        report_id = self.cur.fetchone()[0]
        return report_id

    def insert_section(self, section: Section, report_id):
        """Insert a section into the database and return its ID"""
        section_query = """
        INSERT INTO Section (section_name, report_id)
        VALUES (%s, %s)
        RETURNING section_id
        """
        try:
            self.cur.execute(section_query, (section.section_name, report_id))
            section_id = self.cur.fetchone()[0]
            self.conn.commit()
            return section_id
        except psycopg.Error as e:
            self.conn.rollback()
            logging.error(f"Error inserting section: {e.pgcode} - {e.pgerror}")
            raise

    def insert_item(self, item: Item, section_id: int) -> int:
        """Insert an item under a specific section and return its item_id."""
        item_query = """
        INSERT INTO Item (accession_number, filing_type, identifier, title, description, section_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING item_id;
        """
        self.cur.execute(item_query, (
            item.accession_number,
            item.filing_type,
            item.identifier,
            item.title,
            item.description,
            section_id
        ))
        item_id = self.cur.fetchone()[0]
        return item_id


    def __del__(self):
        """Close the database connection when the object is deleted"""
        if hasattr(self, 'cur'):
            self.cur.close()
        if hasattr(self, 'conn'):
            self.conn.close()
        if logging:
            logging.info("Database connection closed.")


    def delete_item(self, item_id: int):
        """Delete an item from the database by its ID"""
        delete_query = """
        DELETE FROM Item
        WHERE item_id = %s
        """
        try:
            self.cur.execute(delete_query, (item_id,))
            self.conn.commit()
            logging.info(f"Deleted item with ID: {item_id}")
        except psycopg.Error as e:
            self.conn.rollback()
            logging.error(f"Error deleting item: {e.pgcode} - {e.pgerror}")
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

    def item_exists(self, accession_number: str, identifier: str) -> bool:
        """Check if an item with the given accession_number and identifier already exists in the database."""
        query = """
        SELECT 1 FROM Item
        WHERE accession_number = %s AND identifier = %s
        LIMIT 1
        """
        try:
            self.cur.execute(query, (accession_number, identifier))
            result = self.cur.fetchone()
            return result is not None  # Returns True if a record exists, otherwise False
        except psycopg.Error as e:
            logging.error(f"Error checking item existence: {e.pgcode} - {e.pgerror}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error checking item existence: {e}")
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

    def process_report8k(self,company_name, report8k: Report8K, accession_number: str):
        """Process an 8-K report by inserting the report, its sections, and each section's items."""
        try:
            company_id = self.insert_company(company_name)
            report_id= self.insert_report8K(company_id, accession_number)
            for sec_num, section in report8k.sections.items():
                section_id = self.insert_section(report_id, sec_num)
                for item_num, item in section.items.items():
                    self.insert_item(item, section_id)
            self.conn.commit()
            logging.info("8-K report inserted successfully.")
        except Exception as e:
            self.conn.rollback()
            logging.error(f"Error inserting 8-K report: {e}")
            raise




# imp = Importer()