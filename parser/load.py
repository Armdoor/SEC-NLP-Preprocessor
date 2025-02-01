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
            cik TEXT NOT NULL UNIQUE,
            entityType VARCHAR(50) NOT NULL,
            sic VARCHAR(50),
            sicDescription VARCHAR(255),
            ownerOrg VARCHAR(50),
            insiderTransactionForOwnerExists INTEGER, 
            insiderTransactionForIssuerExists INTEGER, 
            name VARCHAR(255) NOT NULL,
            tickers TEXT NOT NULL,
            exchanges TEXT NOT NULL,
            ein VARCHAR(50),
            description TEXT,
            website VARCHAR(255),
            investorWebsite VARCHAR(255),
            category VARCHAR(50),
            fiscalYearEnd VARCHAR(50),
            stateOfIncorporation VARCHAR(50),
            stateOfIncorporationDescription VARCHAR(255),
            phone TEXT,
            total_num_of_filings INTEGER
        );
        """)

        # Addresses table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS addresses (
            address_id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER REFERENCES companies(company_id),
            address_type VARCHAR(50) NOT NULL,
            street1 VARCHAR(255),
            street2 VARCHAR(255), 
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
            from_date DATE,
            from_time TIME,
            to_date DATE,   
            to_time TIME
        )
        """)
##############################################################################################################################################################################################################################################################################################################################################################################
        # Filings table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS filings (
            filing_id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER REFERENCES companies(company_id),
            accession_number VARCHAR(50) NOT NULL,
            filing_type VARCHAR(50) NOT NULL,
            filing_date DATE NOT NULL,
            file_name VARCHAR(255) NOT NULL,
            document_count INTEGER NOT NULL,
            item_information TEXT NOT NULL
        )
        """)

        # Documents table
        # self.cursor.execute("""
        # CREATE TABLE IF NOT EXISTS documents (
        #     document_id INTEGER PRIMARY KEY AUTOINCREMENT,
        #     filing_id INTEGER REFERENCES filings(filing_id),
        #     document_sequence INTEGER NOT NULL,
        #     document_filename VARCHAR(255) NOT NULL,
        #     document_description TEXT,
        #     page_count INTEGER -- Removed trailing comma
        # )
        # """)

        # Pages table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS pages (
            page_id INTEGER PRIMARY KEY AUTOINCREMENT,
            filing_id INTEGER REFERENCES filings(filing_id),
            page_number INTEGER NOT NULL,
            page_content TEXT
        )
        """)

        # Headers table 
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS headers (
            header_id INTEGER PRIMARY KEY AUTOINCREMENT,
            filing_id INTEGER REFERENCES filings(filing_id), 
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
                        cik, entityType, sic, sicDescription, ownerOrg,
                        insiderTransactionForOwnerExists, 
                        insiderTransactionForIssuerExists, name, tickers, 
                        exchanges, ein, description, website, 
                        investorWebsite, category, fiscalYearEnd, stateOfIncorporation, 
                        stateOfIncorporationDescription, phone, total_num_of_filings
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?) 
                """, data)
            logging.info(f"Successfully inserted {len(data)} rows into companies.")
            company_id = self.cursor.lastrowid
            return True, None, company_id
        except sqlite3.Error as e:
            logging.error(f"Error inserting companies in bulk: {e}")
            return False, e, None

    def insert_addresses(self, data):
        try:
            with self.conn:
                self.cursor.executemany("""
                    INSERT OR IGNORE INTO addresses (
                        company_id, address_type, street1, street2, city, state, zip_code, country
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, data)
            logging.info(f"Successfully inserted {len(data)} rows into addresses.")
            return True, None

        except sqlite3.Error as e:
            logging.error(f"Error inserting addresses: {e}")
            return False, e
        

    def insert_former_names(self, data):
        try:
            with self.conn:
                self.cursor.executemany("""
                    INSERT OR IGNORE INTO former_names (
                        company_id, former_name, from_date, from_time, to_date, to_time
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, data)
            logging.info(f"Successfully inserted {len(data)} rows into former names.")
            return True, None
        except sqlite3.Error as e:
            logging.error(f"Error inserting former names: {e}")
            return False, e

    def insert_filings(self, data):
        try:
            with self.conn:
                self.cursor.executemany("""
                    INSERT INTO filings (
                        company_id, accession_number, filing_type, filing_date, file_name, document_count, item_information
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, data)
                logging.info(f"Successfully inserted {len(data)} rows into filings.")
                filing_id = self.cursor.lastrowid
                return filing_id
        except sqlite3.Error as e:
            logging.error(f"Error inserting filings: {e}")
            return None
    # def insert_documents(self, data):
    #     try:
    #         with self.conn:
    #             self.cursor.executemany("""
    #                 INSERT INTO documents (
    #                     filing_id, document_sequence, document_filename, document_description, page_count
    #                 ) VALUES (?, ?, ?, ?, ?)
    #             """, data)
    #         logging.info(f"Successfully inserted {len(data)} rows into documents.")
    #     except sqlite3.Error as e:
    #         logging.error(f"Error inserting documents: {e}")

    def insert_pages(self, data):
        try:
            with self.conn:
                self.cursor.executemany("""
                    INSERT INTO pages (
                        filing_id, page_number, page_content
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
