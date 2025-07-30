import logging
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime

from src.load import download_csv_files, download_json_files
from src.merge import merge_si, merge_ss
from src.process import process_files
from src.qa import qa_check
from src.utils import copy_raw_to_utils, build_data_dictionary


def get_config(snapshot_date=None):
    """Returns a config dictionary containing input/output directories, urls, snapshot date"""
    base_dir = Path(__file__).parent
    
    input_dir = base_dir / "inputs"
    input_snapshot_dir = input_dir
    output_dir = base_dir / "outputs"
    indicators_dir = output_dir / "indicators"
    utils_dir = output_dir / "utils"
    qa_dir = output_dir / "qa"

    csv_urls = {
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

    if snapshot_date:
        input_snapshot_dir = input_dir / "snapshots" / snapshot_date
        output_dir = base_dir / "outputs" / "snapshots" / snapshot_date
        indicators_dir = base_dir / "outputs" / "snapshots" / snapshot_date / "indicators"
        utils_dir = base_dir / "outputs" / "snapshots" / snapshot_date / "utils"
        qa_dir = base_dir / "outputs" / "snapshots" / snapshot_date / "qa"

    return {
        "snapshot_date": snapshot_date,
        "input_dir": input_dir,
        "input_snapshot_dir": input_snapshot_dir,
        "output_dir": output_dir,
        "indicators_dir": indicators_dir,
        "utils_dir": utils_dir,
        "qa_dir": qa_dir,
        "csv_urls": csv_urls,
        "json_urls": json_urls,
        "program_csv_urls_en": program_urls_en,
        "program_csv_urls_fr": program_urls_fr
    }


def main():
    """Process service data and generate outputs."""
    # Setup basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        handlers=[logging.StreamHandler()]
    )

    parser = argparse.ArgumentParser(description="Process service data and generate outputs.")
    parser.add_argument("--snapshot", help="Optional snapshot date (YYYY-MM-DD).")
    parser.add_argument("--local", action="store_true", help="Use local inputs without downloading new ones.")
    args = parser.parse_args()

    # Validate and parse snapshot date
    snapshot_date = None

    if args.snapshot:
        try:
            datetime.strptime(args.snapshot, "%Y-%m-%d")
            snapshot_date = args.snapshot  # Assign only if valid
        except ValueError:
            logging.error("Invalid snapshot date format. Use YYYY-MM-DD.")
            sys.exit(1)

    # Define snapshot directory (if snapshot date is provided)
    if snapshot_date:
        snapshot_dir = Path(__file__).parent / "inputs" / "snapshots" / snapshot_date

        if not snapshot_dir.exists():
            logging.error(f"Snapshot directory {snapshot_dir} does not exist. Exiting.")
            sys.exit(1)

    config = get_config(snapshot_date)

    try:
        # Track total time
        start_time = time.time()
        logging.info("Starting data processing")

        # Download and process raw data
        if not args.local:
            logging.info("Downloading raw data...")
            download_csv_files(config)
            download_json_files(config)

        # Merge historical data
        logging.info("Merging historical data...")
        si = merge_si(config)
        ss = merge_ss(config)

        # Generate processed files
        logging.info("Generating processed files...")
        process_files(si, ss, config)

        # Run QA checks
        logging.info("Running QA checks...")
        qa_check(si, ss, config)

        # Copying files from raw to utils when the run is not for a snapshot
        snapshot_bool = bool(config['snapshot_date'])
        if not snapshot_bool:
            logging.info("Copying files from input to utils...")
            copy_raw_to_utils(config)
            build_data_dictionary(config)

        # Log completion time
        elapsed_time = time.time() - start_time
        logging.info(f"Processing completed in {elapsed_time:.2f} seconds")

    except Exception as e:
        logging.error("Error:",exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
