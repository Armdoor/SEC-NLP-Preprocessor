import sqlite3


conn = sqlite3.connect("sec_filings.db")
cursor = conn.cursor()

# Company tables 
cursor.execute("""
CREATE TABLE IF NOT EXISTS companies (
    company_id INTEGER PRIMARY KEY AUTOINCREMENT,
    cik TEXT NOT NULL,
    company_name TEXT NOT NULL,
    ticker TEXT,
    industry TEXT
)
""")

# Filings 

cursor.execute("""
CREATE TABLE IF NOT EXISTS filing(
    filing_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    form_type TEXT NOT NULL,
    section TEXT,
    item TEXT,
    content TEXT,
    filing_date DATE,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)           
               )
""")

conn.commit()
conn.close()


# Function to insert data into the companies table
def insert_company(cik, company_name, ticker, industry):
    conn = sqlite3.connect("sec_filings.db")
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO companies (cik, company_name, ticker, industry)
    VALUES (?, ?, ?, ?)
    """, (cik, company_name, ticker, industry))
    conn.commit()
    conn.close()

# Function to insert filing data 
def insert_filing(company_id, form_type, section, item, content,filing_date ):
    conn = sqlite3.connect("sec_filings.db")
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO filing(company_id, form_type, section, item, content,filing_date)
                   VALUES (?, ?, ?, ?, ?, ?)
                   """,(company_id, form_type, section, item, content,filing_date))
    conn.commit()
    conn.close()

#  Function to store parsed filing
def store_parsed_filing(company_id, form_type, filing_date, parsed_data):
    for section, items in parsed_data.items():
        for item, content in items.items():
            insert_filing(company_id, form_type, section, item, content, filing_date)