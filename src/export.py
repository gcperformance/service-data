import os
import pandas as pd
import pytz
import sqlite3
from pathlib import Path

def export_to_csv(data_dict, output_dir):
    """
    Export DataFrames to CSV files in specified directories.

    Args:
        data_dict (dict): A dictionary of {file_name: DataFrame}.
        output_dir (Path): Path to the output directory.        
    Returns:
        None
    """
    # Specify date and time in correct timezone
    timezone = pytz.timezone('America/Montreal')
    current_datetime = pd.Timestamp.now(tz=timezone)
    current_datetime_str = current_datetime.strftime("%Y-%m-%d_%H:%M:%S")
    
    # Ensure directory exist
    output_dir.mkdir(parents=True, exist_ok=True)

    for name, df in data_dict.items():
        # Generate the full file path
        file_path = output_dir / f"{name}.csv"

        # Export the DataFrame to CSV
        df.to_csv(file_path, index=False, sep=';')

        # Append a timestamp if provided
        with open(file_path, 'a') as timestamped_file:
            timestamped_file.write(f"\nTimestamp:{current_datetime_str}\n")

        print(f"Exported {name}.csv to {output_dir}")

def csv_to_sqlite(directory=None):
    """
    Convert CSV files in the specified directory to SQLite database.
    
    Args:
        directory (str or Path, optional): Directory containing CSV files. 
            If None, uses the parent directory of the current file.
            
    Returns:
        str: Path to the created SQLite database
    """
    if directory is None:
        directory = Path(__file__).parent.parent
    else:
        directory = Path(directory)

    # Create SQLite database
    db_path = directory / 'service_data.db'
    conn = sqlite3.connect(db_path)

    # Get all CSV files in the directory
    csv_files = list(directory.glob('*.csv'))

    # Process each CSV file
    for csv_file in csv_files:
        try:
            # Read CSV file with semicolon separator
            df = pd.read_csv(
                csv_file,
                encoding='utf-8',
                sep=';',  # Use semicolon as separator
                on_bad_lines='skip'  # Skip problematic lines
            )
            
            # Use the CSV filename (without extension) as the table name
            table_name = csv_file.stem
            
            # Write to SQLite database
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            print(f"Processed {csv_file.name} -> {table_name} table")
            
        except Exception as e:
            print(f"Error processing {csv_file.name}: {str(e)}")
            
    conn.close()
    return str(db_path)