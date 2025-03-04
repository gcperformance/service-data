import pandas as pd
import requests

def download_csv_files(config):
    """
    Download CSV files from the given URLs into the appropriate directory. See config dictionary in main.py

    Args:
        config (dict): dictionary containig snapshot_date, directories, urls

    Returns:
        None
    """
    for name, url in config['csv_urls'].items():
        INPUT_DIR = config['input_dir']
        file_path =  INPUT_DIR / f"{name}.csv"
        try:
            # Fetch the file from the URL
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)

            # Save the content to a file
            with open(file_path, "wb") as file:
                file.write(response.content)

            print(f"Downloaded: {name}.csv")
        except requests.exceptions.RequestException as e:
            print(f"Failed to download {name}.csv from {url}: {e}")
            

def download_json_files(config):
    """
    Download JSON files from the given URLs into the appropriate directory. See config dictionary in main.py

    Args:
        config (dict): dictionary containig snapshot_date, directories, urls

    Returns:
        None
    """
    for name, url in config['json_urls'].items():
        INPUT_DIR = config['input_dir']
        file_path = INPUT_DIR / f"{name}.json"
        try:
            # Fetch the file from the URL
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)

            # Save the content to a file
            with open(file_path, "wb") as file:
                file.write(response.content)

            print(f"Downloaded: {name}.json")
        except requests.exceptions.RequestException as e:
            print(f"Failed to download {name}.json from {url}: {e}")
            

def load_csv(file_name, config, snapshot=False):
    """
    Load a CSV file from the appropriate input directory as defined in config file

    Args:
        file_name (str): The name of the CSV file (e.g., "org_var.csv").
        config (dict): dictionary containing snapshot_date, directories, urls
        snapshot (bool): indicate whether to load from the snapshot. default false

    Returns:
        pd.DataFrame: The loaded DataFrame.
    """
    INPUT_DIR = config['input_dir']
    file_path = INPUT_DIR / file_name

    if snapshot:
        file_path = config['input_snapshot_dir'] / file_name

    if file_path.exists():
        return pd.read_csv(file_path, keep_default_na=False, na_values='')
    else:
        raise FileNotFoundError(f"File not found: {file_path}")
