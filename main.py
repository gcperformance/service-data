import logging
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime

from src.load import download_csv_files, download_json_files, download_program_csv_files, clean_out_input_directory
from src.merge import merge_si, merge_ss
from src.process import process_files
from src.qa import qa_check
from src.utils import build_ifoi, copy_org_var, build_data_dictionary
from src.comp import build_compare_file


def get_config():
    """Returns a config dictionary containing input/output directories, urls, snapshot dates"""
    base_dir = Path(__file__).parent
    
    # Default arrangement of directories
    input_dir = base_dir / "inputs"
    output_dir = base_dir / "outputs"
    
    # Sub-directories must be appended
    indicators_dir = "indicators"
    utils_dir = "utils"
    qa_dir = "qa"

    # List of valid snapshots to run
    snapshots_list = [
        '2025-03-01'
    ]

    csv_urls = {
        'si_2018': 'https://open.canada.ca/data/dataset/3ac0d080-6149-499a-8b06-7ce5f00ec56c/resource/3acf79c0-a5f5-4d9a-a30d-fb5ceba4b60a/download/service_inventory_2018-2023.csv',
        'si_2024': 'https://open.canada.ca/data/dataset/3ac0d080-6149-499a-8b06-7ce5f00ec56c/resource/c0cf9766-b85b-48c3-b295-34f72305aaf6/download/service.csv',
        'ss_2018': 'https://open.canada.ca/data/dataset/3ac0d080-6149-499a-8b06-7ce5f00ec56c/resource/272143a7-533e-42a1-b72d-622116474a21/download/service_standards_2018-2023.csv',
        'ss_2024': 'https://open.canada.ca/data/dataset/3ac0d080-6149-499a-8b06-7ce5f00ec56c/resource/8736cd7e-9bf9-4a45-9eee-a6cb3c43c07e/download/service-std.csv',
        'org_var': 'https://raw.githubusercontent.com/gc-performance/utilities/master/goc-org-variants.csv',
        'sid_registry': 'https://raw.githubusercontent.com/gcperformance/utilities/master/goc-service-id-registry.csv',
        'serv_prog': 'https://raw.githubusercontent.com/gc-performance/utilities/master/goc-service-program.csv',
        'ifoi_en': 'https://open.canada.ca/data/dataset/a35cf382-690c-4221-a971-cf0fd189a46f/resource/7c131a87-7784-4208-8e5c-043451240d95/download/ifoi_roif_en.csv',
        'ifoi_fr': 'https://open.canada.ca/data/dataset/a35cf382-690c-4221-a971-cf0fd189a46f/resource/45069fe9-abe3-437f-97dd-3f64958bfa85/download/ifoi_roif_fr.csv',
        'rbpo': 'https://open.canada.ca/data/dataset/a35cf382-690c-4221-a971-cf0fd189a46f/resource/64774bc1-c90a-4ae2-a3ac-d9b50673a895/download/rbpo_rppo_en.csv',
        # 'op_cost': 'https://donnees-data.tpsgc-pwgsc.gc.ca/ba1/respessentielles-coreresp/respessentielles-coreresp.csv'   no longer in use
    }

    json_urls = {
        'service_data_dict': 'https://open.canada.ca/data/en/recombinant-published-schema/service.json'
    }

    program_urls_en = {
        '2018-2019':'https://donnees-data.tpsgc-pwgsc.gc.ca/ba1/cp-pc/cp-pc-1819-eng.csv',
        '2019-2020':'https://donnees-data.tpsgc-pwgsc.gc.ca/ba1/cp-pc/cp-pc-1920-eng.csv',
        '2020-2021':'https://donnees-data.tpsgc-pwgsc.gc.ca/ba1/cp-pc/cp-pc-2021-eng.csv',
        '2021-2022':'https://donnees-data.tpsgc-pwgsc.gc.ca/ba1/cp-pc/cp-pc-2122-eng.csv',
        '2022-2023':'https://donnees-data.tpsgc-pwgsc.gc.ca/ba1/cp-pc/cp-pc-2223-eng.csv',
        '2023-2024':'https://donnees-data.tpsgc-pwgsc.gc.ca/ba1/cp-pc/cp-pc-2324-eng.csv',
        '2024-2025':'https://donnees-data.tpsgc-pwgsc.gc.ca/ba1/cp-pc/cp-pc-2425-eng.csv',
        '2025-2026':'https://donnees-data.tpsgc-pwgsc.gc.ca/ba1/cp-pc/cp-pc-2526-eng.csv'
    }
        

    program_urls_fr = {
        '2018-2019':'https://donnees-data.tpsgc-pwgsc.gc.ca/ba1/cp-pc/cp-pc-1819-fra.csv',
        '2019-2020':'https://donnees-data.tpsgc-pwgsc.gc.ca/ba1/cp-pc/cp-pc-1920-fra.csv',
        '2020-2021':'https://donnees-data.tpsgc-pwgsc.gc.ca/ba1/cp-pc/cp-pc-2021-fra.csv',
        '2021-2022':'https://donnees-data.tpsgc-pwgsc.gc.ca/ba1/cp-pc/cp-pc-2122-fra.csv',
        '2022-2023':'https://donnees-data.tpsgc-pwgsc.gc.ca/ba1/cp-pc/cp-pc-2223-fra.csv',
        '2023-2024':'https://donnees-data.tpsgc-pwgsc.gc.ca/ba1/cp-pc/cp-pc-2324-fra.csv',
        '2024-2025':'https://donnees-data.tpsgc-pwgsc.gc.ca/ba1/cp-pc/cp-pc-2425-fra.csv',
        '2025-2026':'https://donnees-data.tpsgc-pwgsc.gc.ca/ba1/cp-pc/cp-pc-2526-fra.csv'
    }
  
    return {
        "snapshots_list":snapshots_list,
        "input_dir": input_dir,
        "output_dir": output_dir,
        "indicators_dir": indicators_dir,
        "utils_dir": utils_dir,
        "qa_dir": qa_dir,
        "csv_urls": csv_urls,
        "json_urls": json_urls,
        "program_csv_urls_en": program_urls_en,
        "program_csv_urls_fr": program_urls_fr
    }

def setup_logging():
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    # one date format used everywhere
    datefmt = "%Y-%m-%d %H:%M:%S"

    # different message layouts
    fmt_simple  = "%(asctime)s [%(levelname)s] %(message)s"
    fmt_verbose   = "%(asctime)s [%(levelname)s] %(name)s:%(funcName)s:%(lineno)d - %(message)s"

    # define each formatter
    f_simple = logging.Formatter(fmt_simple, datefmt=datefmt)
    f_verbose  = logging.Formatter(fmt_verbose,  datefmt=datefmt)
    
    # console shows INFO and above, simple format
    h_console = logging.StreamHandler()
    h_console.setLevel(logging.INFO)
    h_console.setFormatter(f_simple)

    # debug file gets EVERYTHING with the verbose format
    h_debug = logging.FileHandler(Path("outputs") / "debug.log", encoding="utf-8", delay=True)
    h_debug.setLevel(logging.DEBUG)
    h_debug.setFormatter(f_verbose)

    # errors file gets ERROR and above with verbose format
    h_errors = logging.FileHandler(Path("outputs") / "errors.log", encoding="utf-8", delay=True)
    h_errors.setLevel(logging.ERROR)
    h_errors.setFormatter(f_verbose)

    if root.hasHandlers():
        root.handlers.clear()
    root.addHandler(h_console)
    root.addHandler(h_debug)
    root.addHandler(h_errors)

    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)

def main():
    """Process service data and generate outputs."""
    # Argument parsing
    parser = argparse.ArgumentParser(description="Process service data and generate outputs.")
    parser.add_argument("--local", action="store_true", help="Use local inputs without downloading new ones.")
    parser.add_argument("--live", action="store_true", help="Run process without running update for snapshots.")
    args = parser.parse_args()

    # Set up logging
    setup_logging()
    logger = logging.getLogger(__name__)

    # Define config dictionary
    config = get_config()

    try:
        # Track total time
        start_time = time.perf_counter()
        logger.info("Starting data processing")

        # Download and process raw data
        if not args.local: # If the "local" option was passed, do not download these files
            logger.info("Removing existing input files...")
            clean_out_input_directory(config)

            logger.info("Downloading raw data...")
            download_csv_files(config)
            download_json_files(config)
            download_program_csv_files(config)

        # Merge historical data
        try:
            logger.info("Merging historical data...")
            si = merge_si(config)
            ss = merge_ss(config)
        except:
            logger.error("Merging historical data failed", exc_info=True)
            sys.exit(1)

        # Generate processed files
        logger.info("Generating processed files...")
        si_ss_dict = process_files(si, ss, config)
        
        # Run QA checks
        logger.info("Running QA checks...")
        qa_check(si, ss, config)
        
        # Copying files from raw to utils
        logger.info("Copying files from input to utils...")
        build_ifoi(config)
        copy_org_var(config)
        build_data_dictionary(config)
        
        # Run snapshots unless "live" arg was passed
        if not args.live: # if the "live" option was passed, don't run the snapshots
            snapshots_list = config['snapshots_list']
            for snapshot in snapshots_list:
                # Merge historical snapshot data
                logger.info("Processing snapshots: %s", snapshot)
                try:
                    logger.info("Merging historical data for snapshots...")
                    si_snap = merge_si(config, snapshot)
                    ss_snap = merge_ss(config, snapshot)
                except:
                    logger.error("Merging historical data for snapshots failed", exc_info=True)
                    sys.exit(1)
                
                # Generate processed files 
                logger.info("Generating processed snapshot files...")
                si_ss_snap_dict = process_files(si_snap, ss_snap, config, snapshot)

                # Compare snapshots to live data
                logger.info("Comparing snapshot to live data...")

                si_compare_dict = {
                    'df_base': si_ss_snap_dict['si'],
                    'df_comp': si_ss_dict['si'],
                    'base_name': f"{snapshot}_si",
                    'comp_name':"si",
                    'key_name':"fy_org_id_service_id"
                }
                build_compare_file(si_compare_dict, config, snapshot)

                ss_compare_dict = {
                    'df_base': si_ss_snap_dict['ss'],
                    'df_comp': si_ss_dict['ss'],
                    'base_name': f"{snapshot}_ss",
                    'comp_name':"ss",
                    'key_name':"fy_org_id_service_id_std_id"
                }
                build_compare_file(ss_compare_dict, config, snapshot)
                

        # Log completion time
        elapsed_time = time.perf_counter() - start_time
        logger.info(f"Processing completed in {elapsed_time:.2f} seconds")

    except Exception as e:
        logger.error("Error: %s", e, exc_info=True)

if __name__ == "__main__":
    main()
