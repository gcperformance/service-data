# Government of Canada Service Inventory
## Service Performance Data Review and Analysis

### Introduction

This Python project processes Government of Canada service-related data, merging historical and current datasets to produce structured CSV and SQLite outputs for visualization and further analysis.

### Key Features
- **Data ingestion**: Downloads and processes service inventory and performance data.
- **Dataset Merging**: Integrates 2018-2023 historical data with 2024+ Open Government datasets.
- **Quality Assurance**: Identifies and flags inconsistencies in datasets.
- **Output Generation**: Produces structured CSVs and an SQLite database for querying.

These data are collected as a requirement under the [Policy on Service and Digital](https://www.tbs-sct.canada.ca/pol/doc-eng.aspx?id=32603).

---
## Quick Start - Consulting remote datasets with MS Excel
- Select **From Web** in the **Get & Transform Data** section under the **Data** tab on the main ribbon.
- Paste the following URL in the dialog box that appears, replacing XXX with the filename of the desired dataset: `https://github.com/gcperformance/service-data/releases/latest/download/XXX.csv`.
  - *For example, to consult `si.csv`, use the following URL: `https://github.com/gcperformance/service-data/releases/latest/download/si.csv`*
  - *To consult a snapshot version, add the date of the snapshot in YYYY-MM-DD format to the front of the file name. For example, to consult `si.csv` generated from the snapshot taken March 1, 2025, use the following URL: `https://github.com/gcperformance/service-data/releases/latest/download/2025-03-01_si.csv`*
- Preview the data in the next dialog box and change the **Data Type Detection** to **Based on entire dataset** then click **Load**.
  - *Click **Transform Data** To open the dataset in Power Query and perform more advanced calculations*
- Delete the timestamp row at the bottom of the table.

## Quick Start - Running script locally
### Installation
```bash
# Clone the repository
git clone https://github.com/gc-performance/service-data.git
cd service-data

# Install dependencies
pip install -r requirements.txt
```
### Running the Script
```bash
python main.py  # Runs full processing pipeline
```
#### Optional Arguments:
- `--snapshot YYYY-MM-DD` : Runs the script using a specific snapshot dataset.
- `--local`: Runs the script without downloading new datasets.
- `--help`: Provides additional help for the above arguments.

---
## Datasets Consulted

### **[GC Service Inventory and Service Performance](https://open.canada.ca/data/en/dataset/3ac0d080-6149-499a-8b06-7ce5f00ec56c)**
- **Files**: `si_2018.csv`, `si_2024.csv`, `ss_2018.csv`, `ss_2024.csv`
- **Content**: Government of Canada service inventory, associated standards, and performance.
- **Update Frequency**: Annually

### **[Departmental Plans and Departmental Results Reports](https://open.canada.ca/data/en/dataset/a35cf382-690c-4221-a971-cf0fd189a46f/resource/64774bc1-c90a-4ae2-a3ac-d9b50673a895)**
- **File**: `rbpo.csv`
- **Content**: Expenditures and Full-Time Equivalents (FTEs) by program and organization.
- **Update Frequency**: Annually

---
## Conventions
### Service Scope Filtering
The [Policy on Service and Digital](https://www.tbs-sct.canada.ca/pol/doc-eng.aspx?id=32603) requirement to report services applies only to **external and internal enterprise services**. Any service without `service_scope=EXTERN` or `service_scope=ENTERPRISE` is **excluded** from consolidated datasets (`si.csv` and `ss.csv`).

### Data Format
- All CSV files use a semicolon (`;`) as a delimiter.

### Timestamps
- All CSV files produced by the script include a timestamp on the last row of the file.

### Accessing files remotely
- To access the files in the latest release, point your tool to the following url: `https://github.com/gcperformance/service-data/releases/latest/download/XXX.csv`, replacing xxx.csv with the file you want to access, for example `si.csv` 

---
## Project Structure
*Given that files produced by the script are available in releases, all transitory input and output files are no longer tracked with git, or included in the repo. Releases have a flat structure, so the directory structure below is only relevant if you clone the repo and run the script.*

### Root Folder
- `main.py` - Orchestrates the processing pipeline.
- `requirements.txt` - Lists python dependencies.
- `context.md` - Context on this dataset for use with LLM.
- `database.dbml` - **Draft** schema defining a database model.
- `tidy-script` - Bash script producing file paths for deleting inputs, outputs, caches, etc.

### `inputs/`: Files downloaded for Processing (Unmodified)
- `ifoi_en.csv`: [Inventory of federal organisations and interests - in English](https://open.canada.ca/data/en/dataset/a35cf382-690c-4221-a971-cf0fd189a46f/resource/7c131a87-7784-4208-8e5c-043451240d95)
- `ifoi_fr.csv`: [Répertoire des organisations et intérêts fédéraux - en français](https://open.canada.ca/data/en/dataset/a35cf382-690c-4221-a971-cf0fd189a46f/resource/45069fe9-abe3-437f-97dd-3f64958bfa85)
- `org_var.csv`: [Department Name Variant List](https://github.com/gc-performance/utilities): A list of every organization, department, and agency with their associated names mapped to a single numeric ID. Maintained manually. 
- `rbpo.csv`: [Departmental Plans and Departmental Results Reports](https://open.canada.ca/data/en/dataset/a35cf382-690c-4221-a971-cf0fd189a46f/resource/64774bc1-c90a-4ae2-a3ac-d9b50673a895)
- `serv_prog.csv`: [Program-Service ID Correspondence](https://github.com/gc-performance/utilities): Mapping long-form program names from the 2018 service inventory to program IDs from Departmental Plans and Results Reports
- `si_2018.csv`: [GC Service Inventory - Service Identification Information & Metrics (2018-2023)](https://open.canada.ca/data/en/dataset/3ac0d080-6149-499a-8b06-7ce5f00ec56c/resource/3acf79c0-a5f5-4d9a-a30d-fb5ceba4b60a)
- `si_2024.csv`: [GC Service Inventory - Service Identification Information & Metrics (2024)](https://open.canada.ca/data/en/dataset/3ac0d080-6149-499a-8b06-7ce5f00ec56c/resource/c0cf9766-b85b-48c3-b295-34f72305aaf6)
- `ss_2018.csv`: [GC Service Inventory - Service Standards & Performance Results (2018-2023)](https://open.canada.ca/data/en/dataset/3ac0d080-6149-499a-8b06-7ce5f00ec56c/resource/272143a7-533e-42a1-b72d-622116474a21)
- `ss_2024.csv`: [GC Service Inventory - Service Standards & Performance Results (2024)](https://open.canada.ca/data/en/dataset/3ac0d080-6149-499a-8b06-7ce5f00ec56c/resource/8736cd7e-9bf9-4a45-9eee-a6cb3c43c07e)
- `service_data_dict.json`: [GC Service Inventory - Data dictionary](https://open.canada.ca/data/en/recombinant-published-schema/service.json)

### `outputs/`: Files Produced by the Script

- `si.csv`: Full service inventory merging 2018–2023 datasets with the 2024 dataset. *`service_scope` must contain `EXTERN` or `ENTERPRISE`*
- `ss.csv`: Full service standard dataset merging 2018–2023 datasets with the 2024 dataset. *`service_scope` must contain `EXTERN` or `ENTERPRISE`*

#### `outputs/indicators/`: Summary Files for Visualization and Review

*All tables were built with `service_scope` containing `EXTERN` or `ENTERPRISE`*
- `drr_all.csv`: a concatenated table with all the drr indicator columns and scores (dr_2467: percentage of high-volume external services (>=45k applications) that are delivered online end-to-end, dr_2468: percentage of high-volume external services (>=45k applications and telephone enquiries) that met at least one service standard, dr_2469: percentage of applications for high-volume external services (>45k applications) that used the online channel)
- `maf_all.csv`: a concatenated table with all the maf columns and scores (maf1: percentage of services that have service standards, maf2: percentage of service standards met, maf5: percentage of applicable services that can be completed online end-to-end, maf6: percentage of client interaction points that are available online, maf8: percentage of services which have used client feedback to improve services in the year prior to reporting)
- `service_fte_spending.csv`: FTEs and spending for programs delivering services.
- `si_fy_interaction_sum.csv`: Sum of interactions by service, fiscal year, channel
- `si_fy_service_count.csv`: Unique services count by fiscal year.
- `si_oip.csv`: Online interaction points activation status by service for the latest available fiscal year.
- `si_reviews.csv`: Count of services reviewed or improved.
- `si_vol.csv`: Service interaction volume by service, fiscal year, and channel.
- `ss_tml_perf_vol.csv`: Timeliness performance standards by service and fiscal year.

#### `outputs/qa/`: Quality Assurance Review Files

- `si_qa.csv`: Full service inventory dataset with QA issues identified as separate columns. All `service_scope` included.
- `ss_qa.csv`: Full service standards dataset with QA issues identified as separate columns. All `service_scope` included.
- `si_qa_report.csv`: Critical errors for service inventory.
- `ss_qa_report.csv`: Critical errors for service standards.

#### `outputs/utils/`: Utilities and Supporting Files

- `dd_field_names.csv`: A list of translated field names and metadata for `si` (`resource_name`=`service`) and `ss` (`resource_name`=`service_std`).
- `dd_choices.csv`: Correspondence table between codes that appear in `ss` and `si` and their names.
- `dd_program`: List of valid program codes and names.
- `dept.csv`: A tidy unique list of departments with their IFOI IDs.
- `drf.csv`: A flattened Departmental plans and Departmental results report.
- `ifoi.csv`: Exhaustive list of departmental info in English and French
- `org_var.csv`: Duplicate-permitted list of variant department names and their IFOI ID.
- `sid_list.csv`: Unique list of service IDs with latest reporting year and department.
- `si_all.csv`: Full service inventory merging 2018–2023 datasets with the 2024 dataset. All `service_scope` included.
- `ss_all.csv`: Full service standard dataset merging 2018–2023 datasets with the 2024 dataset. All `service_scope` included.

### `src/`: Source Code for Script

- `clean.py`: functions to clean and set up data
- `create_sqlite.py`: process to generate the sqlite database
- `export.py`: functions to export data to CSV (semi-colon delimited)
- `load.py`: functions to load csv files to dataframes and download / refresh all inputs
- `merge.py`: process to align 2018 and 2024 service inventory and service standard datasets
- `process.py`: produces summaries and indicator files (`outputs/indicators/` directory)
- `qa.py`: performs quality assurance checks and produces qa outputs (`outputs/qa/` directory)
- `qa_issues_descriptions.csv`: definitions file for qa issues
- `utils.py`: misc utility functions, produces some files for `outputs/utils/` directory

### `tests/`: Script Tests

- `README.md`: placeholder readme documentation for tests
- `conftest.py`: configuration file for pytest
- `test_merge.py`: testing script for merge.py
- `test_outputs.py`: testing script for output files
- `generate_reference.py`: script for generating field names and types for all output files, see ref/ directory

#### `tests/ref`: Reference Files

- `reference_fields.csv`: Table of all tables, fields, and datatypes for use with test script

### `notebooks/`: Jupyter notebooks for testing and experiments

### `snapshots/`: Files generated based on data at a point in time, defined by the date in format YYYY-MM-DD
- Releases indicate which files are generated from the snapshot by prepending the date to the file name, for example `2025-03-01_si.csv` is equivalent to `si.csv`, but based on data from March 1, 2025.
- The python script expects the snapshot inputs and outputs to be defined by their directory.
- Running the main.py script with the command `--snapshot YYYY-MM-DD` will generate new outputs with the static snapshot input files for the service inventory (`si_2018.csv`, `si_2024.csv`), service standards (`ss_2018.csv`, `ss_2024.csv`), and departmental results (`rbpo.csv`) data, but retrieving the latest other data.

---
## SQLite Database Releases

In addition to CSV files, this repository automatically generates a SQLite database containing all processed data in table format for easier querying and analysis. The database is published as a GitHub release and can be downloaded from the [releases page](https://github.com/gc-performance/service-data/releases).

### Release Schedule

- **Automatic**: New release created on every push to master branch
- **Weekly**: Scheduled release on Tuesday mornings at midnight EST
- **Manual**: Can be triggered through GitHub Actions workflow

### Release Format

- **Tag**: `service_data-[commit_hash]`
- **Name**: `Service Data Release YYYY-MM-DD (commit_hash)`
- Each release includes:
  - SQLite database file
  - All individual .csv files produced by script
  - Timestamp of generation (Eastern Time)
  - Git commit hash for traceability

### Database Structure

- Tables are prefixed with their source directory for better organization
  - Example: `indicators_si_vol` for the file `si_vol.csv` from the indicators directory
- All CSV data is preserved with original column names and data types
- Tables use the same semicolon separator as CSV files

### Accessing the Database

1. Go to the [releases page](https://github.com/gc-performance/service-data/releases)
2. Download the `service_data.db` file from the latest release
3. Use any SQLite client (e.g., DBeaver, SQLite Browser) to open and query the database

---
## Directory structure
```
├── .
├── ..
├── README.md
├── context.md
├── database.dbml
├── main.py
├── requirements.txt
├── tidy-script
├── inputs
│   ├── ifoi_en.csv
│   ├── ifoi_fr.csv
│   ├── org_var.csv
│   ├── rbpo.csv
│   ├── serv_prog.csv
│   ├── service_data_dict.json
│   ├── si_2018.csv
│   ├── si_2024.csv
│   ├── ss_2018.csv
│   ├── ss_2024.csv
│   └── snapshots
│       └── 2025-03-01
│           ├── rbpo.csv
│           ├── si_2018.csv
│           ├── si_2024.csv
│           ├── ss_2018.csv
│           └── ss_2024.csv
├── notebooks
│   ├── experiments.ipynb
│   └── qa-uris.ipynb
├── outputs
│   ├── indicators
│   │   ├── drr_all.csv
│   │   ├── maf_all.csv
│   │   ├── service_fte_spending.csv
│   │   ├── si_fy_interaction_sum.csv
│   │   ├── si_fy_service_count.csv
│   │   ├── si_oip.csv
│   │   ├── si_reviews.csv
│   │   ├── si_vol.csv
│   │   └── ss_tml_perf_vol.csv
│   ├── qa
│   │   ├── si_qa.csv
│   │   ├── si_qa_report.csv
│   │   ├── ss_qa.csv
│   │   └── ss_qa_report.csv
│   ├── service_data.db
│   ├── si.csv
│   ├── ss.csv
│   ├── utils
│   │   ├── dd_choices.csv
│   │   ├── dd_field_names.csv
│   │   ├── dd_program.csv
│   │   ├── dept.csv
│   │   ├── drf.csv
│   │   ├── ifoi.csv
│   │   ├── org_var.csv
│   │   ├── si_all.csv
│   │   ├── sid_list.csv
│   │   └── ss_all.csv
│   └── snapshots
│       └── 2025-03-01
│           ├── indicators
│           │   ├── drr_all.csv
│           │   ├── maf_all.csv
│           │   ├── service_fte_spending.csv
│           │   ├── si_fy_interaction_sum.csv
│           │   ├── si_fy_service_count.csv
│           │   ├── si_oip.csv
│           │   ├── si_reviews.csv
│           │   ├── si_vol.csv
│           │   └── ss_tml_perf_vol.csv
│           ├── qa
│           │   ├── si_qa.csv
│           │   ├── si_qa_report.csv
│           │   ├── ss_qa.csv
│           │   └── ss_qa_report.csv
│           ├── si.csv
│           ├── ss.csv
│           └── utils
│               ├── drf.csv
│               ├── si_all.csv
│               ├── sid_list.csv
│               └── ss_all.csv
├── src
│   ├── __init__.py
│   ├── clean.py
│   ├── create_sqlite.py
│   ├── export.py
│   ├── load.py
│   ├── merge.py
│   ├── process.py
│   ├── qa.py
│   ├── qa_issues_descriptions.csv
│   └── utils.py
└── tests
    ├── ref
    │   └── reference_fields.csv
    ├── README.md
    ├── conftest.py
    ├── generate_reference.py
    ├── test_merge.py
    └── test_outputs.py
```
