import sqlite3

# Connect to your database
conn = sqlite3.connect("sec_filings.db")
cursor = conn.cursor()

# SQL to delete the companies table
cursor.execute("DROP TABLE IF EXISTS companies")
cursor.execute("DROP TABLE IF EXISTS addresses")
cursor.execute("DROP TABLE IF EXISTS former_names")
cursor.execute("DROP TABLE IF EXISTS filings")
cursor.execute("DROP TABLE IF EXISTS documents")
cursor.execute("DROP TABLE IF EXISTS pages")
cursor.execute("DROP TABLE IF EXISTS headers")
# Commit and close the connection
conn.commit()
conn.close()

print("Table deleted successfully (if it existed).")
