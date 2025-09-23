import pandas as pd
import requests, os
from pathlib import Path
import logging
logger = logging.getLogger(__name__)

class MissingInput(Exception):
    pass

def clean_out_input_directory(config):
    """
    Delete all .csv and .json files in the inputs folder. Ignore the backups and snapshots folder.
    """
    # Directory path
    dir_path = config['input_dir']

    if len(os.listdir(dir_path)) > 0:
        # List all files in the directory
        for filename in os.listdir(dir_path):
            file_path = os.path.join(dir_path, filename)
            
            # Check if it is a file (not a subdirectory)
            if os.path.isfile(file_path):
                os.remove(file_path)  # Remove the file
                logger.debug("Deleted file: %s",filename)

    else: logger.debug("Input directory already empty")

def download_program_csv_files(config):
    """
    Download Program CSV files from the given URLs into the appropriate directory. See config dictionary in main.py

    Args:
        config (dict): dictionary containing valid snapshot dates, directories, urls

    Returns:
        None
    """
    for fiscal_yr, url in config['program_csv_urls_en'].items():
        filename = url.split('/')[-1].split('.')[0]

        INPUT_DIR = config['input_dir']
        file_path =  INPUT_DIR / f"{filename}.csv"
        
        try:
            # Fetch the file from the URL
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)

            # Save the content to a file
            with open(file_path, "wb") as file:
                file.write(response.content)

            logger.debug("Downloaded: %s.csv", filename)
        
        except requests.exceptions.RequestException as e:
            logger.info("Failed to download %s.csv from %s: %s", filename, url, e)

        except Exception as e:
            logger.error("Error: %s", e, exc_info=True)
            raise

    for fiscal_yr, url in config['program_csv_urls_fr'].items():
        filename = url.split('/')[-1].split('.')[0]

        INPUT_DIR = config['input_dir']
        file_path =  INPUT_DIR / f"{filename}.csv"
        
        try:
            # Fetch the file from the URL
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)

            # Save the content to a file
            with open(file_path, "wb") as file:
                file.write(response.content)

            logger.debug("Downloaded: %s.csv", filename)
        
        except requests.exceptions.RequestException as e:
            logger.info("Failed to download %s.csv from %s: %s", filename, url, e)

        except Exception as e:
            logger.error("Error: %s", e, exc_info=True)
            raise

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
            raise MissingInput(f"File not found in input_dir: {file_path}")

    except MissingInput as e:
        logger.info("Missing file: %s, will check for backup file", file_path)    
        try:
            INPUT_DIR = config['input_dir'] / 'backups'
            file_path = INPUT_DIR / file_name

            if not file_path.exists():
                raise FileNotFoundError(f"File not found in input_dir: {file_path}")

            df = pd.read_csv(file_path, keep_default_na=False, na_values='')
            logger.info("Loaded %s from input/backups (%d rows, %d columns)", file_path, df.shape[0], df.shape[1])
            return df
        
        except FileNotFoundError as e:
            logger.info("Missing file: %s", file_path)
            raise
                    
    except Exception as e:
        logger.error("Failed to load %s", file_path, exc_info=True)
        raise  # raises this exception to main.py - fatal error, will cause main.py to stop.

    else:
        df = pd.read_csv(file_path, keep_default_na=False, na_values='')
        logger.debug("Loaded %s from input (%d rows, %d columns)", file_path, df.shape[0], df.shape[1])
        return df
