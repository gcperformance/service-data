import pandas as pd
import requests, os
from pathlib import Path
import logging
# urllib3 is a HTTP client library that provides error handling
from urllib3.exceptions import InsecureRequestWarning
# Suppress the certificate verfiication/insecure request warnings by using the urllib3 disable warnings method.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

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
                logger.debug("Deleted file: %s",file_path)

    else: 
        logger.debug("Input directory already empty")

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

        headers = {
                    'User-Agent': 'tbs/service-policy/load.py'
                }
        
        try:
            # Set up a session
            s = requests.Session()

            # Fetch the file from the URL
            # verify is set to false on advice from PSPC, who acknowledged they will not be fixing the SSL certificate issue
            response = s.get(url, verify=False, headers=headers)
            response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)

            # Save the content to a file
            with open(file_path, "wb") as file:
                file.write(response.content)

            logger.debug("Downloaded: %s", file_path)
        
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
            # Set up a session
            s = requests.Session()

            # Fetch the file from the URL
            # verify is set to false on advice from PSPC, who acknowledged they will not be fixing the SSL certificate issue
            response = s.get(url, verify=False)
            response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)

            # Save the content to a file
            with open(file_path, "wb") as file:
                file.write(response.content)

            logger.debug("Downloaded: %s", file_path)
        
        except requests.exceptions.RequestException as e:
            logger.info("Failed to download %s.csv from %s: %s", filename, url, e)

        except Exception as e:
            logger.error("Error: %s", e, exc_info=True)
            raise

    for fiscal_yr, url in config['program_csv_urls_enfr'].items():
            filename = url.split('/')[-1].split('.')[0]
    
            INPUT_DIR = config['input_dir']
            file_path =  INPUT_DIR / f"{filename}.csv"
            
            try:
                # Set up a session
                s = requests.Session()
    
                # Fetch the file from the URL
                # verify is set to false on advice from PSPC, who acknowledged they will not be fixing the SSL certificate issue
                response = s.get(url, verify=False)
                response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
    
                # Save the content to a file
                with open(file_path, "wb") as file:
                    file.write(response.content)
    
                logger.debug("Downloaded: %s", file_path)
            
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
        headers = {
            'User-Agent': 'tbs/service-policy/load.py'
        }
        try:
            # Fetch the file from the URL
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)

            # Save the content to a file
            with open(file_path, "wb") as file:
                file.write(response.content)

            logger.debug("Downloaded: %s", file_path)
        
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
        headers = {
                    'User-Agent': 'tbs/service-policy/load.py'
                }
        try:
            # Fetch the file from the URL
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)

            # Save the content to a file
            with open(file_path, "wb") as file:
                file.write(response.content)

            logger.debug("Downloaded: %s", file_path)

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

def run_script_check(config):
    '''
    Return True if any configured local input table differs from its live version
    '''
    logger.info('Reviewing input files for differences with published data...')
    # Compare each configured local file with its live counterpart.
    # Pull relevant info from config file, convert to DataFrame for ease of use
    local_and_live_paths = config['run_flag_paths']
    local_and_live_paths = pd.DataFrame(local_and_live_paths, columns=['table', 'local_path', 'live_url'])
    run_flag = False

    # Iterate over the set of tables
    for table in local_and_live_paths['table']:
        # Read the local file
        local_path = local_and_live_paths.loc[local_and_live_paths['table']==table, 'local_path'].item()
        local = pd.read_csv(local_path, dtype=str, keep_default_na=False)

        # Read the remote file
        live_url =  local_and_live_paths.loc[local_and_live_paths['table']==table, 'live_url'].item()
        live = pd.read_csv(live_url, dtype=str, keep_default_na=False)

        # Create a boolean mask of which cells differ from one DF to the other 
        # ().ne() produces True if the cells differ; ne = not equal)
        # then melt into a single column
        check = live.ne(local).melt()

        # Filter the single column for entries that are True (i.e. differences)
        differences = check.loc[check['value']]

        # Publish flag is true when there are differences to report
        # if the length of the differences column is greater than 0, then 
        run_flag = differences.shape[0] > 0

        # Stop once a difference is found
        if run_flag:
            logger.info(f'{differences.shape[0]} differences identified in {table}, running script')
            break
        else:
            logger.info(f'No difference for input {table}. live:{live.shape[0]} rows, {live.shape[1]} cols; local:{local.shape[0]} rows, {local.shape[1]} cols')

    if not run_flag:
        logger.info('No differences identified in inputs. Script will not run.')    

    return run_flag