from src.load import download_csv_files, CSV_URLS
from src.merge import merge_si, merge_ss
from src.process import process_files


print("Downloading raw data to data/raw/...")
download_csv_files(CSV_URLS)
print("Data download complete.")

print("Merging historical service inventory to latest...")
si = merge_si()
print("Service inventory merged.")

print("Merging historical service service standards to latest...")
ss = merge_ss()
print("Service standards merged.")

print("Generating summary/processed files...")
process_files(si, ss)
print("Summary/processed files created.")


