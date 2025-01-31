import sqlite3
import logging

class Loader:
    def __init__(self):
        self.conn = sqlite3.connect("sec_filings.db")
        self.cursor = self.conn.cursor()
        self._create_tables()
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler("error.log"), logging.StreamHandler()]
        )

    def _create_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            company_id INTEGER PRIMARY KEY AUTOINCREMENT,
            cik TEXT NOT NULL,
            entity_type VARCHAR(50) NOT NULL,
            company_name VARCHAR(255) NOT NULL,
            ticker VARCHAR(50) NOT NULL,
            industry VARCHAR(50),
            sic VARCHAR(50),
            sic_description VARCHAR(255),
            owner_org VARCHAR(50),
            insider_transaction_for_owner_exists INTEGER, -- BOOLEAN → INTEGER
            insider_transaction_for_issuer_exists INTEGER, -- BOOLEAN → INTEGER
            ein VARCHAR(50),
            description TEXT,
            website VARCHAR(255),
            investor_website VARCHAR(255),
            category VARCHAR(50),
            fiscal_year_end VARCHAR(50),
            state_of_incorporation VARCHAR(50),
            state_of_incorporation_description VARCHAR(255),
            phone TEXT
        )
        """)

        # Addresses table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS addresses (
            address_id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER REFERENCES companies(company_id), -- Simplified foreign key syntax
            address_type VARCHAR(50) NOT NULL,
            street1 VARCHAR(255), -- Consistent naming
            street2 VARCHAR(255), -- Consistent naming
            city VARCHAR(255),
            state VARCHAR(50),
            zip_code VARCHAR(50),
            country VARCHAR(50)
        )
        """)

        # Former names table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS former_names (
            former_name_id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER REFERENCES companies(company_id),
            former_name VARCHAR(255) NOT NULL,
            change_date DATE
        )
        """)

        # Filings table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS filings (
            filing_id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER REFERENCES companies(company_id),
            accession_number VARCHAR(50) NOT NULL,
            filing_type VARCHAR(50) NOT NULL,
            filing_date DATE NOT NULL,
            file_name VARCHAR(255) NOT NULL,
            document_count INTEGER NOT NULL -- Removed trailing comma
        )
        """)

        # Documents table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            document_id INTEGER PRIMARY KEY AUTOINCREMENT,
            filing_id INTEGER REFERENCES filings(filing_id),
            document_sequence INTEGER NOT NULL,
            document_filename VARCHAR(255) NOT NULL,
            document_description TEXT,
            page_count INTEGER -- Removed trailing comma
        )
        """)

        # Pages table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS pages (
            page_id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER REFERENCES documents(document_id),
            page_number INTEGER NOT NULL,
            page_content TEXT
        )
        """)

        # Headers table 
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS headers (
            header_id INTEGER PRIMARY KEY AUTOINCREMENT,
            filing_id INTEGER REFERENCES filings(filing_id), -- Correct reference
            sec_header TEXT
        )
        """)

        self.conn.commit()

    def insert_companies_bulk(self, data):
        """
        Insert multiple rows into the companies table efficiently.
        :param data: List of tuples containing company details.
        """
        try:
            with self.conn:
                self.cursor.executemany("""
                    INSERT INTO companies (
                        cik, entity_type, company_name, ticker, industry, sic, 
                        sic_description, owner_org, insider_transaction_for_owner_exists, 
                        insider_transaction_for_issuer_exists, ein, description, website, 
                        investor_website, category, fiscal_year_end, state_of_incorporation, 
                        state_of_incorporation_description, phone
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, data)
            logging.info(f"Successfully inserted {len(data)} rows into companies.")
        except sqlite3.Error as e:
            logging.error(f"Error inserting companies in bulk: {e}")

    def insert_addresses(self, data):
        try:
            with self.conn:
                self.cursor.executemany("""
                    INSERT INTO addresses (
                        company_id, address_type, street1, street2, city, state, zip_code, country
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, data)
            logging.info(f"Successfully inserted {len(data)} rows into addresses.")
        except sqlite3.Error as e:
            logging.error(f"Error inserting addresses: {e}")

    def insert_former_names(self, data):
        try:
            with self.conn:
                self.cursor.executemany("""
                    INSERT INTO former_names (
                        company_id, former_name, change_date
                    ) VALUES (?, ?, ?)
                """, data)
            logging.info(f"Successfully inserted {len(data)} rows into former names.")
        except sqlite3.Error as e:
            logging.error(f"Error inserting former names: {e}")

    def insert_filings(self, data):
        try:
            with self.conn:
                self.cursor.executemany("""
                    INSERT INTO filings (
                        company_id, accession_number, filing_type, filing_date, file_name, document_count
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, data)
            logging.info(f"Successfully inserted {len(data)} rows into filings.")
        except sqlite3.Error as e:
            logging.error(f"Error inserting filings: {e}")

    def insert_documents(self, data):
        try:
            with self.conn:
                self.cursor.executemany("""
                    INSERT INTO documents (
                        filing_id, document_sequence, document_filename, document_description, page_count
                    ) VALUES (?, ?, ?, ?, ?)
                """, data)
            logging.info(f"Successfully inserted {len(data)} rows into documents.")
        except sqlite3.Error as e:
            logging.error(f"Error inserting documents: {e}")

    def insert_pages(self, data):
        try:
            with self.conn:
                self.cursor.executemany("""
                    INSERT INTO pages (
                        document_id, page_number, page_content
                    ) VALUES (?, ?, ?)
                """, data)
            logging.info(f"Successfully inserted {len(data)} rows into pages.")
        except sqlite3.Error as e:
            logging.error(f"Error inserting pages: {e}")

    def insert_headers(self, data):
        try:
            with self.conn:
                self.cursor.executemany("""
                    INSERT INTO headers (
                        filing_id, sec_header
                    ) VALUES (?, ?)
                """, data)
            logging.info(f"Successfully inserted {len(data)} rows into headers.")
        except sqlite3.Error as e:
            logging.error(f"Error inserting headers: {e}")

    def close(self):
        self.cursor.close()
        self.conn.close()
