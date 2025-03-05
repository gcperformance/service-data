import logging
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime

from src.load import download_csv_files, CSV_URLS, download_json_files, JSON_URLS
from src.merge import merge_si, merge_ss
from src.process import process_files
from src.qa import qa_check
from src.utils import copy_raw_to_utils, build_data_dictionary


def get_config(snapshot_date=None):
    """Returns a config dictionary containing input/output directories."""
    base_dir = Path(__file__).parent.parent
    
    input_dir = base_dir / "inputs"
    input_snapshot_dir = input_dir
    output_dir = base_dir / "outputs"
    indicators_dir = output_dir / "indicators"
    utils_dir = output_dir / "utils"
    qa_dir = output_dir / "qa"

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
        "qa_dir": qa_dir
    }


def main():
    """Process service data and generate outputs."""
    # Setup basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        handlers=[logging.StreamHandler()]
    )

    parser = argparse.ArgumentParser(description="Download and process snapshot data.")
    parser.add_argument("--snapshot", help="Optional snapshot date (YYYY-MM-DD).")
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
        snapshot_dir = Path(__file__).parent.parent / "inputs" / "snapshots" / snapshot_date

        if not snapshot_dir.exists():
            logging.error(f"Snapshot directory {snapshot_dir} does not exist. Exiting.")
            sys.exit(1)

    config = get_config(snapshot_date)

    try:
        # Track total time
        start_time = time.time()
        logging.info("Starting data processing")

        # Download and process raw data
        logging.info("Downloading raw data...")
        download_csv_files()
        download_json_files()

        # Merge historical data
        logging.info("Merging historical data...")
        si = merge_si(snapshot_date)
        ss = merge_ss(snapshot_date)

        # Generate processed files
        logging.info("Generating processed files...")
        process_files(si, ss, snapshot_date)

        # Run QA checks
        logging.info("Running QA checks...")
        qa_check(si, ss)

        # Copying files from raw to utils
        logging.info("Copying files from input to utils...")
        copy_raw_to_utils()
        build_data_dictionary()

        # Log completion time
        elapsed_time = time.time() - start_time
        logging.info(f"Processing completed in {elapsed_time:.2f} seconds")

    except Exception as e:
        logging.error("Error:",exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
