import pandas as pd
import requests
from pathlib import Path

# Define the path to the raw data directory
RAW_DATA_DIR = Path(__file__).parent.parent / "inputs"

# Ensure the directory exists
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

# URLs for datasets
CSV_URLS = {
    'si_2018': 'https://open.canada.ca/data/dataset/3ac0d080-6149-499a-8b06-7ce5f00ec56c/resource/3acf79c0-a5f5-4d9a-a30d-fb5ceba4b60a/download/service_inventory_2018-2023.csv',
    'si_2024': 'https://open.canada.ca/data/dataset/3ac0d080-6149-499a-8b06-7ce5f00ec56c/resource/c0cf9766-b85b-48c3-b295-34f72305aaf6/download/service.csv',
    'ss_2018': 'https://open.canada.ca/data/dataset/3ac0d080-6149-499a-8b06-7ce5f00ec56c/resource/272143a7-533e-42a1-b72d-622116474a21/download/service_standards_2018-2023.csv',
    'ss_2024': 'https://open.canada.ca/data/dataset/3ac0d080-6149-499a-8b06-7ce5f00ec56c/resource/8736cd7e-9bf9-4a45-9eee-a6cb3c43c07e/download/service-std.csv',
    'org_var': 'https://raw.githubusercontent.com/gc-performance/utilities/master/goc-org-variants.csv',
    'serv_prog': 'https://raw.githubusercontent.com/gc-performance/utilities/master/goc-service-program.csv',
    'ifoi_en': 'https://open.canada.ca/data/dataset/a35cf382-690c-4221-a971-cf0fd189a46f/resource/7c131a87-7784-4208-8e5c-043451240d95/download/ifoi_roif_en.csv',
    'ifoi_fr': 'https://open.canada.ca/data/dataset/a35cf382-690c-4221-a971-cf0fd189a46f/resource/45069fe9-abe3-437f-97dd-3f64958bfa85/download/ifoi_roif_fr.csv',
    'rbpo': 'https://open.canada.ca/data/dataset/a35cf382-690c-4221-a971-cf0fd189a46f/resource/64774bc1-c90a-4ae2-a3ac-d9b50673a895/download/rbpo_rppo_en.csv',
    # 'op_cost': 'https://donnees-data.tpsgc-pwgsc.gc.ca/ba1/respessentielles-coreresp/respessentielles-coreresp.csv'   
}

JSON_URLS = {
    'service_data_dict': 'https://open.canada.ca/data/en/recombinant-published-schema/service.json'
}

def download_csv_files(urls=CSV_URLS):
    """
    Download CSV files from the given URLs into the RAW_DATA_DIR directory.

    Args:
        urls (dict): A dictionary where keys are filenames (without .csv extension)
                     and values are the URLs to the files.

    Returns:
        None
    """
    for name, url in urls.items():
        file_path = RAW_DATA_DIR / f"{name}.csv"
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
            

def download_json_files(urls=JSON_URLS):
    """
    Download JSON files from the given URLs into the RAW_DATA_DIR directory.

    Args:
        urls (dict): A dictionary where keys are filenames (without .json extension)
                     and values are the URLs to the files.

    Returns:
        None
    """
    for name, url in urls.items():
        file_path = RAW_DATA_DIR / f"{name}.json"
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
            

def load_csv_from_raw(file_name):
    """
    Load a CSV file from the RAW_DATA_DIR directory.

    Args:
        file_name (str): The name of the CSV file (e.g., "org_var.csv").

    Returns:
        pd.DataFrame: The loaded DataFrame.
    """
    file_path = RAW_DATA_DIR / file_name
    if file_path.exists():
        return pd.read_csv(file_path, keep_default_na=False, na_values='')
    else:
        raise FileNotFoundError(f"File not found: {file_path}")

    


