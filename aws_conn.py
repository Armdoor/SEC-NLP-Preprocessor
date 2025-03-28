import psycopg2
from psycopg2 import postgres

# Database connection parameters
db_config = {
    'dbname': 'SEC_DB',  # Replace with your database name
    'user': 'bojack1',         # Replace with your master username
    'password': 'Kcajob+25',     # Replace with your master password
    'host': 'sec-db-1.cm3gcyikmv3b.us-east-1.rds.amazonaws.com',     # Replace with your RDS endpoint
    'port': 5432                     # Default PostgreSQL port
}

# Connect to the database
try:
    conn = psycopg2.connect(**db_config)
    print("Connected to the database!")
except Exception as e:
    print(f"Error connecting to the database: {e}")
    exit()

# Create a cursor object to execute SQL commands
cur = conn.cursor()

# Create a table (if it doesn't exist)
try:
    cur.execute("""
        CREATE TABLE IF NOT EXISTS example_table (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            age INT
        );
    """)
    conn.commit()
    print("Table created successfully!")
except Exception as e:
    print(f"Error creating table: {e}")
    conn.rollback()

# Insert data into the table
try:
    insert_query = postgres.SQL("""
        INSERT INTO example_table (name, age)
        VALUES (%s, %s);
    """)
    data = ("John Doe", 30)  # Example data
    cur.execute(insert_query, data)
    conn.commit()
    print("Data inserted successfully!")
except Exception as e:
    print(f"Error inserting data: {e}")
    conn.rollback()

# Query data from the table
try:
    cur.execute("SELECT * FROM example_table;")
    rows = cur.fetchall()
    print("Data from the table:")
    for row in rows:
        print(row)
except Exception as e:
    print(f"Error querying data: {e}")

# Close the cursor and connection
cur.close()
conn.close()
print("Connection closed.")