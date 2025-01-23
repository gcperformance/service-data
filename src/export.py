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

def csv_to_sqlite(directory=None, output_dir=None):
    """
    Convert CSV files from the outputs directory to SQLite database.
    Table names will be prefixed with their directory name, e.g., 'indicators_si_vol'.
    
    Args:
        directory (str or Path, optional): Base directory containing the outputs folder. 
            If None, uses the parent directory of the current file.
        output_dir (str or Path, optional): Directory to save the SQLite database.
            If None, uses the 'outputs' directory in the project root.
            
    Returns:
        str: Path to the created SQLite database
    """
    if directory is None:
        directory = Path(__file__).parent.parent
    else:
        directory = Path(directory)

    # Set input and output directories
    input_dir = directory / 'outputs'
    if output_dir is None:
        output_dir = input_dir
    else:
        output_dir = Path(output_dir)

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create SQLite database in outputs directory
    db_path = output_dir / 'service_data.db'
    conn = sqlite3.connect(db_path)

    # Recursively get all CSV files in the outputs directory
    csv_files = list(input_dir.rglob('*.csv'))

    # Keep track of processed tables to avoid duplicates
    processed_tables = set()

    # Process each CSV file
    for csv_file in csv_files:
        try:
            # Skip files in certain directories
            if any(part in csv_file.parts for part in ['.git', '__pycache__']):
                continue

            # Read CSV file with semicolon separator
            df = pd.read_csv(
                csv_file,
                encoding='utf-8',
                sep=';',  # Use semicolon separator
                on_bad_lines='skip'  # Skip problematic lines
            )
            
            # Create table name from directory structure
            relative_path = csv_file.relative_to(input_dir)
            parts = list(relative_path.parts)
            
            # If file is directly in outputs, don't use a prefix
            if len(parts) == 1:
                table_name = csv_file.stem
            else:
                # Use directory name as prefix, e.g., 'indicators_si_vol'
                prefix = parts[0]  # First part is the directory name
                table_name = f"{prefix}_{csv_file.stem}"
            
            # Skip if we've already processed this table name
            if table_name in processed_tables:
                print(f"Skipping duplicate table name: {table_name}")
                continue
            
            # Write to SQLite database
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            processed_tables.add(table_name)
            print(f"Processed {relative_path} -> {table_name} table")
            
        except Exception as e:
            print(f"Error processing {csv_file.name}: {str(e)}")
            
    conn.close()
    return str(db_path)