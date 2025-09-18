import pandas as pd
import requests
import logging
logger = logging.getLogger(__name__)

def download_csv_files(config):
    """
    Download CSV files from the given URLs into the appropriate directory. See config dictionary in main.py

    Args:
        config (dict): dictionary containing valid snapshot dates, directories, urls

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

            logger.debug("Downloaded: %s.csv", name)
        
        except requests.exceptions.RequestException as e:
            logger.error("Failed to download %s.csv from %s: %s", name, url, e)
            raise

        except Exception as e:
            logger.error("Error: %s", e, exc_info=True)
            raise

def download_json_files(config):
    """
    Download JSON files from the given URLs into the appropriate directory. See config dictionary in main.py

    Args:
        config (dict): dictionary containing valid snapshot dates, directories, urls

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

            logger.debug("Downloaded: %s.json", name)

        except requests.exceptions.RequestException as e:
            logger.error("Failed to download %s.json from %s: %s", name, url, e)
            raise

        except Exception as e:
            logger.error('Error', exc_info=True)
            raise
            
def load_csv(file_name, config, snapshot=False):
    """
    Load a CSV file from the appropriate input directory as defined in config file

    Args:
        file_name (str): The name of the CSV file (e.g., "org_var.csv").
        config (dict): dictionary containing valid snapshot dates, directories, urls
        snapshot (str): String indicating the date of the snapshot. Defaults to False/blank

    Returns:
        pd.DataFrame: The loaded DataFrame.
    """
    
    # If running a snapshot run, change output directory accordingly
    if snapshot:
        INPUT_DIR = config['input_dir'] / 'snapshots' / snapshot
    else:
        INPUT_DIR = config['input_dir'] 
    
    file_path = INPUT_DIR / file_name

    try:
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        df = pd.read_csv(file_path, keep_default_na=False, na_values='')
        logger.debug("Loaded %s (%d rows, %d columns)", file_path, df.shape[0], df.shape[1])
        return df

    except FileNotFoundError as e:
        logger.error("Missing file: %s", file_path)
        raise  # raises this exception to main.py - fatal error, will cause main.py to stop.

    except Exception as e:
        logger.error("Failed to load %s", file_path, exc_info=True)
        raise  # raises this exception to main.py - fatal error, will cause main.py to stop.
