# Import necessary modules and components from the application and third-party libraries

# from db_setup import *              # (Optional) Import database setup configurations (currently commented out)
from .models import *                 # Import models (e.g. Section, Item, Report8K, Report10K, Part) from the current package
import psycopg                       # Import the psycopg library for connecting to PostgreSQL
# import psycopg.extras              # (Optional) Import extras from psycopg if needed (currently commented out)
import logging                       # Import logging module for logging activities and errors
import os                            # Import os module for interacting with the operating system (unused in current code)

logging.basicConfig(level=logging.INFO)  # Configure logging to show informational messages and above
from model.config import DB_URI


class Importer:
    """
    A class to handle importing data into the PostgreSQL database.
    It manages connection establishment, table creation, and data insertion for various entities.
    """
    def __init__(self):
        """
        Initialize the Importer by connecting to the PostgreSQL database.
        The connection parameters (host, port, user, password, dbname) are hard-coded.
        """
        try:
            # Establish a connection to the PostgreSQL database using psycopg
            self.conn = psycopg.connect(DB_URI) 
            # Set autocommit to True so that each SQL command is immediately committed
            self.conn.autocommit = True

            # Create a database cursor to execute SQL queries
            self.cur = self.conn.cursor()

            # Log a successful connection message
            logging.info("Connected to the database.")
            # Optionally, a second cursor creation was considered (see commented line)
        except Exception as e:
            # Log an error message if connection fails and exit the program
            logging.error(f"Error connecting to the database: {e}")
            exit()

    def create_tables(self):
        try:
            # Create Company table
            self.cur.execute("""
            CREATE TABLE IF NOT EXISTS Company (
                company_id SERIAL PRIMARY KEY,
                company_name VARCHAR(255) NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # Create Report8K table (depends on Company)
            self.cur.execute("""
            CREATE TABLE IF NOT EXISTS Report8K(
                report_id SERIAL PRIMARY KEY,
                company_id INTEGER NOT NULL REFERENCES Company(company_id),
                accession_number VARCHAR(255) NOT NULL,
                filing_type VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # Create Section table (depends on Report8K)
            self.cur.execute("""
            CREATE TABLE IF NOT EXISTS Section (
                section_id SERIAL PRIMARY KEY,
                section_name VARCHAR(255) NOT NULL,
                report_id INTEGER NOT NULL REFERENCES Report8K(report_id)
            );
            """)

            # Create Item table (depends on Section)
            self.cur.execute("""
            CREATE TABLE IF NOT EXISTS Item (
                item_id SERIAL PRIMARY KEY,
                accession_number VARCHAR(255) NOT NULL,  -- Added missing column
                filing_type VARCHAR(255) NOT NULL,
                identifier VARCHAR(255) NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                section_id INTEGER REFERENCES Section(section_id)
            );
            """)

            # Create Part table (independent)
            self.cur.execute("""
            CREATE TABLE IF NOT EXISTS Part (
                part_id SERIAL PRIMARY KEY,
                part_name VARCHAR(255) NOT NULL
            );
            """)

            logging.info("Tables created successfully.")
        except Exception as e:
            logging.error(f"Error creating tables: {e}")

    def insert_company(self, company_name: str) -> int:
        """
        Insert a company into the Company table.
        
        Parameters:
            company_name (str): The name of the company to be inserted.
        
        Returns:
            int: The newly generated company_id.
        """
        company_query = """
        INSERT INTO Company (company_name)
        VALUES (%s)
        RETURNING company_id;
        """
        # Execute the insert query with the provided company_name
        self.cur.execute(company_query, (company_name,))
        # Retrieve and return the generated company_id
        company_id = self.cur.fetchone()[0]
        return company_id
    
    def get_or_create_company(self, company_name: str) -> int:
        """
        Retrieve the company_id for an existing company or insert the company if it does not exist.
        
        Parameters:
            company_name (str): The name of the company.
        
        Returns:
            int: The existing or newly created company_id.
        """
        select_query = "SELECT company_id FROM Company WHERE company_name = %s"
        self.cur.execute(select_query, (company_name,))
        row = self.cur.fetchone()
        if row is not None:
            return row[0]
        else:
            insert_query = """
            INSERT INTO Company (company_name)
            VALUES (%s)
            RETURNING company_id;
            """
            self.cur.execute(insert_query, (company_name,))
            company_id = self.cur.fetchone()[0]
            return company_id
        

    def insert_report8K(self, company_id: int, accession_number, filing_type="8-K"):
        """
        Insert an 8-K report into the Report8K table.

        Parameters:
            company_id (int): Foreign key linking the report to a company.
            accession_number: Unique identifier for the report.
            filing_type (str): Filing type for the report, defaulting to "8-K".

        Returns:
            int: The newly generated report_id.
        """
        report_query = """
        INSERT INTO Report8K (company_id, accession_number, filing_type)
        VALUES (%s, %s, %s)
        RETURNING report_id;
        """
        # Execute the query using the provided parameters and return the report_id
        self.cur.execute(report_query, (company_id, accession_number, filing_type))
        report_id = self.cur.fetchone()[0]
        return report_id

    def insert_section(self, section: Section, report_id):
        """
        Insert a section into the Section table.

        Parameters:
            section (Section): A Section object containing section details.
            report_id (int): The ID of the report to which this section belongs.

        Returns:
            int: The newly generated section_id.
        """
        section_query = """
        INSERT INTO Section (section_name, report_id)
        VALUES (%s, %s)
        RETURNING section_id
        """
        try:
            # Execute the insert query with the section name and report ID
            self.cur.execute(section_query, (section.section_name, report_id))
            section_id = self.cur.fetchone()[0]
            self.conn.commit()  # Commit the transaction
            return section_id
        except psycopg.Error as e:
            # Rollback the transaction on error and log details
            self.conn.rollback()
            logging.error(f"Error inserting section: {e.pgcode} - {e.pgerror}")
            raise

    def insert_item(self, item: Item, section_id: int) -> int:
        """
        Insert an item under a specific section into the Item table.

        Parameters:
            item (Item): The item object containing its details.
            section_id (int): The foreign key referencing the section.

        Returns:
            int: The newly generated item_id.
            
        Note:
            The query includes an 'accession_number' column which must be present in the Item model
            and in the actual table schema; otherwise, this may cause a mismatch.
        """
        item_query = """
        INSERT INTO Item (accession_number, filing_type, identifier, title, description, section_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING item_id;
        """
        # Execute the insert query using item attributes and the provided section ID
        self.cur.execute(item_query, (
            item.accession_number,
            item.filing_type,
            item.identifier,
            item.title,
            item.description,
            section_id
        ))
        # Retrieve and return the generated item_id
        item_id = self.cur.fetchone()[0]
        return item_id

    def __del__(self):
        """
        Destructor for the Importer class.
        Ensures that the database cursor and connection are closed when the object is deleted.
        """
        if hasattr(self, 'cur'):
            self.cur.close()
        if hasattr(self, 'conn'):
            self.conn.close()
        # Log the closing of the database connection
        if logging:
            logging.info("Database connection closed.")

    def delete_item(self, item_id: int):
        """
        Delete an item from the Item table by its item_id.

        Parameters:
            item_id (int): The ID of the item to be deleted.
        """
        delete_query = """
        DELETE FROM Item
        WHERE item_id = %s
        """
        try:
            # Execute the delete query for the specified item_id
            self.cur.execute(delete_query, (item_id,))
            self.conn.commit()  # Commit the deletion
            logging.info(f"Deleted item with ID: {item_id}")
        except psycopg.Error as e:
            # Rollback if deletion fails and log the error details
            self.conn.rollback()
            logging.error(f"Error deleting item: {e.pgcode} - {e.pgerror}")
            raise

    def insert_part(self, part: Part):
        """
        Insert a part into the Part table.

        Parameters:
            part (Part): The part object containing part details.

        Returns:
            int: The newly generated part_id.
        """
        insert_part = """
        INSERT INTO Part (part_name)
        VALUES (%s)
        RETURNING part_id
        """
        try:
            # Execute the insert query with the part name
            self.cur.execute(insert_part, (part.part_name,))
            part_id = self.cur.fetchone()[0]
            self.conn.commit()  # Commit the transaction
            return part_id
        except psycopg.Error as e:
            # Rollback on error and log the error details
            self.conn.rollback()
            logging.error(f"Error inserting part: {e.pgcode} - {e.pgerror}")
            raise

    def item_exists(self, accession_number: str, identifier: str) -> bool:
        """
        Check whether an item with a given accession number and identifier already exists in the Item table.
        
        Parameters:
            accession_number (str): The accession number of the item.
            identifier (str): An identifier associated with the item.
        
        Returns:
            bool: True if an item matching the criteria exists; otherwise, False.
        """
        query = """
        SELECT 1 FROM Item
        WHERE accession_number = %s AND identifier = %s
        LIMIT 1
        """
        try:
            # Execute the select query using provided parameters
            self.cur.execute(query, (accession_number, identifier))
            result = self.cur.fetchone()
            # Return True if a record exists, otherwise False
            return result is not None
        except psycopg.Error as e:
            # Log detailed error if query execution fails
            logging.error(f"Error checking item existence: {e.pgcode} - {e.pgerror}")
            raise
        except Exception as e:
            # Log unexpected errors
            logging.error(f"Unexpected error checking item existence: {e}")
            raise

    def insert_report10K(self, report10K: Report10K):
        """
        Insert a 10-K report and its related parts and items into the database.
        
        The process involves iterating over parts in the report, inserting each part, then
        inserting each item for the part, and finally mapping them in the Report10K association table.
        """
        try:
            # Iterate through each part in the report10K object's parts dictionary
            for part_name, part in report10K.parts.items():
                # Insert the part and retrieve its generated part_id
                part_id = self.insert_part(part)
                # Iterate over each item in the current part's items dictionary
                for item_number, item in part.items.items():
                    # Insert the item and retrieve its item_id
                    item_id = self.insert_item(item)
                    # Insert a mapping between the part and item in the Report10K table
                    self.cur.execute("""
                    INSERT INTO Report10K (part_id, item_id)
                    VALUES (%s, %s)
                    """, (part_id, item_id))
            self.conn.commit()  # Commit all changes after processing the report
        except psycopg.Error as e:
            # Rollback all changes if an error occurs and log the error details
            self.conn.rollback()
            logging.error(f"Error inserting Report10K: {e.pgcode} - {e.pgerror}")
            raise
    def get_item_description(self, accession_number: str, identifier: str) -> str:
        """
        Retrieve the description of an item based on accession number and identifier.

        Parameters:
            accession_number (str): The accession number of the item.
            identifier (str): The identifier of the item.

        Returns:
            str: The description of the item if found, otherwise None.
        """
        query = """
        SELECT description FROM Item
        WHERE accession_number = %s AND identifier = %s
        LIMIT 1;
        """
        try:
            self.cur.execute(query, (accession_number, identifier))
            result = self.cur.fetchone()
            if result:
                return result[0]  # This is the description
            return None
        except psycopg.Error as e:
            logging.error(f"Error fetching item description: {e.pgcode} - {e.pgerror}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            raise
        
    def get_all_item_descriptions(self) -> list:
        """
        Retrieve all descriptions from the Item table.

        Returns:
            list: A list of all non-null item descriptions.
        """
        query = "SELECT description FROM Item WHERE description IS NOT NULL;"
        try:
            self.cur.execute(query)
            results = self.cur.fetchall()
            # Return a flat list of descriptions
            return [row[0] for row in results]
        except psycopg.Error as e:
            logging.error(f"Error fetching all descriptions: {e.pgcode} - {e.pgerror}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            raise


    def process_report8k(self, company_name, report8k, accession_number: str):
        """
        Process an 8-K report by inserting the company, report, sections, and items.
        Uses get_or_create_company to ensure the company is only inserted once.
        """
        try:
            # Use the helper method to fetch or create the company record
            company_id = self.get_or_create_company(company_name)
            
            # Insert the 8-K report
            report_id = self.insert_report8K(company_id, accession_number)
            
            # Process each section and its items within the report
            for sec_num, section in report8k.sections.items():
                section_id = self.insert_section(section, report_id)
                for item_num, item in section.items.items():
                    self.insert_item(item, section_id)
            self.conn.commit()
            logging.info("8-K report inserted successfully.")
        except Exception as e:
            self.conn.rollback()
            logging.error(f"Error inserting 8-K report: {e}")
            raise
    def get_all_item_descriptions(self) -> list[str]:
        """
        Return every non‑NULL description from the Item table.
        """
        query = "SELECT description FROM Item WHERE description IS NOT NULL;"
        try:
            self.cur.execute(query)
            return [row[0] for row in self.cur.fetchall()]
        except psycopg.Error as e:
            logging.error(f"Error fetching descriptions: {e.pgcode} - {e.pgerror}")
            raise

# Optional instantiation of the Importer class for testing or immediate use:
# imp = Importer()




"""
Company → Report8K → Section → Item

Table	    Primary role	                                Typical real‑world example

Company	    Issuer metadata	                                Apple Inc.
Report8K	A single 8‑K filing	                            2024‑10‑31 8‑K for Apple
Section	    Logical headers inside the filing	            “Item 2.02 – Results of Operations…”
Item	    The actual disclosure text for that header	    Full paragraph(s) explaining Q3 earnings
Part	    Free‑floating lookup table	                    “Forward‑looking Statements” blurb you might reuse

"""