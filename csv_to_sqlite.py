import os
import pandas as pd
import sqlite3
import csv
from pathlib import Path

# Directory containing CSV files
directory = os.path.dirname(os.path.abspath(__file__))

# Create SQLite database
db_path = os.path.join(directory, 'service_data.db')
conn = sqlite3.connect(db_path)

# Get all CSV files in the directory
csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]

# Process each CSV file
for csv_file in csv_files:
    try:
        # Read CSV file with semicolon separator
        df = pd.read_csv(
            os.path.join(directory, csv_file),
            encoding='utf-8',
            sep=';',  # Use semicolon as separator
            on_bad_lines='skip',  # Skip problematic lines
            quoting=csv.QUOTE_MINIMAL,  # Handle quoted fields
            low_memory=False  # Avoid mixed type inference issues
        )
        
        # Get table name (filename without .csv extension)
        table_name = os.path.splitext(csv_file)[0]
        
        print(f"Processing {csv_file} into table {table_name}")
        
        # Write to SQLite database
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        print(f"Successfully created table {table_name}")
        
    except Exception as e:
        print(f"Error processing {csv_file}: {str(e)}")

conn.close()
print("\nDatabase creation complete. Database saved as 'service_data.db'")