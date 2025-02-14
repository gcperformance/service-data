import pandas as pd
from pathlib import Path
import os
import pytz

OUTPUT_DIR = Path(__file__).parent.parent / "outputs"
REF_DIR = Path(__file__).parent / "ref"

def generate_reference_table(output_dir=OUTPUT_DIR, ref_dir=REF_DIR):
    """
    Scans the 'outputs' directory for CSV files and extracts field names with their Pandas data types.
    Saves the reference table with 3 columns: file_name, fields, datatype.

    :param output_dir: The directory containing CSV files.
    :param ref_dir: The directory where the reference file will be stored.
    """
    # Specify date and time in correct timezone
    timezone = pytz.timezone('America/Montreal')
    current_datetime = pd.Timestamp.now(tz=timezone)
    current_datetime_str = current_datetime.strftime("%Y-%m-%d_%H:%M:%S")
    
    ref_file = ref_dir / "reference_fields.csv"
    reference_data = []

    for root, _, files in os.walk(output_dir):
        for file in files:
            if file.endswith(".csv"):
                file_path = Path(root) / file  # Ensure cross-platform compatibility
                table_name = file_path.relative_to(output_dir)# Relative path as table name

                try:
                    df = pd.read_csv(file_path, delimiter=";", skipfooter=1, engine='python')  
                    df_inferred = df.convert_dtypes()  # Infer data types from all rows

                    for col in df.columns:
                        datatype = df_inferred[col].dtype  # Get Pandas dtype
                        reference_data.append({"file_path": str(file_path), "file_name": str(table_name), "fields": col, "datatype": datatype, "generated_date": current_datetime_str})

                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

    # Convert to DataFrame and save as reference CSV
    ref_df = pd.DataFrame(reference_data)
    ref_dir.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
    ref_df.to_csv(ref_file, index=False)

    print(f"Reference schema saved to {ref_file}")

if __name__ == "__main__":
    generate_reference_table()
