import pandas as pd
import pytz

def export_to_csv(data_dict, output_dir, config):
    """
    Export DataFrames to CSV files in specified directories.

    Args:
        data_dict (dict): A dictionary of {file_name: DataFrame}.
        output_dir (Path): Path to the output directory.
        config (dict): dictionary containig snapshot_date, directories, urls
    Returns:
        None
    """
    # Specify date and time in correct timezone
    timezone = pytz.timezone('America/Montreal')
    current_datetime = pd.Timestamp.now(tz=timezone)
    current_datetime_str = current_datetime.strftime("%Y-%m-%d_%H:%M:%S")
    
    # Ensure directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Appendix to add to bottom of file
    appendix = f"\nTimestamp:{current_datetime_str}\n"
    
    snapshot_bool = bool(config['snapshot_date'])
    if snapshot_bool:
        appendix =f"\nSNAPSHOT {config['snapshot_date']} Timestamp:{current_datetime_str}\n"

    for name, df in data_dict.items():
        # Generate the full file path
        file_path = output_dir / f"{name}.csv"

        # Export the DataFrame to CSV with semicolon separator (;)
        df.to_csv(file_path, index=False, sep=';')

        # Append a timestamp
        with open(file_path, 'a') as timestamped_file:
            timestamped_file.write(appendix)

        print(f"Exported {name}.csv to {output_dir}")
