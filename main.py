import logging
import sys
import time
from pathlib import Path

from src.load import download_csv_files, CSV_URLS
from src.merge import merge_si, merge_ss
from src.process import process_files
from src.qa import qa_check
from src.export import csv_to_sqlite
from src.utils import copy_raw_to_utils


def main():
    """Process service data and generate outputs."""
    # Setup basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        handlers=[logging.StreamHandler()]
    )

    try:
        # Track total time
        start_time = time.time()
        logging.info("Starting data processing")

        # Download and process raw data
        logging.info("Downloading raw data...")
        download_csv_files()

        # Merge historical data
        logging.info("Merging historical data...")
        si = merge_si()
        ss = merge_ss()

        # Generate processed files
        logging.info("Generating processed files...")
        process_files(si, ss)

        # Run QA checks
        logging.info("Running QA checks...")
        qa_check(si, ss)

        # Copying files from raw to utils
        logging.info("Copying files from input to utils...")
        copy_raw_to_utils()

        # Create SQLite database
        logging.info("Creating SQLite database...")
        db_path = csv_to_sqlite()

        # Log completion time
        elapsed_time = time.time() - start_time
        logging.info(f"Processing completed in {elapsed_time:.2f} seconds")

    except Exception as e:
        logging.error("Error:",exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
