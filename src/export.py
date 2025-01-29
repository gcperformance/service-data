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

        # Export the DataFrame to CSV with semicolon separator (;)
        df.to_csv(file_path, index=False, sep=';')

        # Append a timestamp
        with open(file_path, 'a') as timestamped_file:
            timestamped_file.write(f"\nTimestamp:{current_datetime_str}\n")

        print(f"Exported {name}.csv to {output_dir}")

def csv_to_sqlite(directory=None, output_dir=None):
    """
    Convert CSV files from both inputs and outputs directories to SQLite database.
    Table names will be prefixed based on their source:
    - For files in inputs directory: "inputs_" + table_name
    - For files in outputs directory: directory_name + "_" + table_name
    
    Args:
        directory (str or Path, optional): Base directory containing the inputs and outputs folders. 
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
    inputs_dir = directory / 'inputs'
    outputs_dir = directory / 'outputs'
    if output_dir is None:
        output_dir = outputs_dir
    else:
        output_dir = Path(output_dir)

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create SQLite database in outputs directory
    db_path = output_dir / 'service_data.db'
    conn = sqlite3.connect(db_path)

    # Get current git commit hash
    try:
        import subprocess
        git_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=directory).decode('utf-8').strip()
    except:
        git_hash = 'unknown'

    # Create metadata table with creation timestamp
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    cursor.execute("""
        INSERT OR REPLACE INTO metadata (key, value)
        VALUES ('db_created_at', datetime('now'))
    """)
    cursor.execute("""
        INSERT OR REPLACE INTO metadata (key, value)
        VALUES ('db_commit_hash', ?)
    """, (git_hash,))
    conn.commit()

    # Keep track of processed tables to avoid duplicates
    processed_tables = set()

    # Process input directory files
    if inputs_dir.exists():
        input_csv_files = list(inputs_dir.rglob('*.csv'))
        for csv_file in input_csv_files:
            try:
                # Skip files in certain directories
                if any(part in csv_file.parts for part in ['.git', '__pycache__']):
                    continue

                # Read CSV file with semicolon separator
                df = pd.read_csv(
                    csv_file,
                    encoding='utf-8',
                    sep=';',
                    on_bad_lines='skip'
                )
                
                # For input files, simply prefix with "inputs_"
                table_name = f"inputs_{csv_file.stem}"
                
                # Skip if we've already processed this table name
                if table_name in processed_tables:
                    print(f"Skipping duplicate table name: {table_name}")
                    continue
                
                # Write to SQLite database
                df.to_sql(table_name, conn, if_exists='replace', index=False)
                processed_tables.add(table_name)
                print(f"Processed input file {csv_file.name} -> {table_name} table")
                
            except Exception as e:
                print(f"Error processing input file {csv_file.name}: {str(e)}")

    # Process output directory files
    if outputs_dir.exists():
        output_csv_files = list(outputs_dir.rglob('*.csv'))
        for csv_file in output_csv_files:
            try:
                # Skip files in certain directories
                if any(part in csv_file.parts for part in ['.git', '__pycache__']):
                    continue

                # Read CSV file with semicolon separator
                df = pd.read_csv(
                    csv_file,
                    encoding='utf-8',
                    sep=';',
                    on_bad_lines='skip'
                )
                
                # Create table name from directory structure
                relative_path = csv_file.relative_to(outputs_dir)
                parts = list(relative_path.parts)
                
                # If file is directly in outputs, prefix with "outputs_"
                if len(parts) == 1:
                    table_name = f"outputs_{csv_file.stem}"
                else:
                    # Use directory name as prefix
                    prefix = parts[0]  # First part is the directory name
                    table_name = f"{prefix}_{csv_file.stem}"
                
                # Skip if we've already processed this table name
                if table_name in processed_tables:
                    print(f"Skipping duplicate table name: {table_name}")
                    continue
                
                # Write to SQLite database
                df.to_sql(table_name, conn, if_exists='replace', index=False)
                processed_tables.add(table_name)
                print(f"Processed output file {csv_file.name} -> {table_name} table")
                
            except Exception as e:
                print(f"Error processing output file {csv_file.name}: {str(e)}")
            
    conn.close()
    return str(db_path)