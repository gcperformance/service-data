# Government of Canada Service Inventory
## Service Performance Data Review and Analysis

### Introduction

This Python script ingests and processes service-related data into ready-to-use CSV files for visualization or further analysis.

In 2024, data collection processes changed to allow departments to publish their datasets directly to Open Government. This introduced minor differences in format and content between the 2018–2023 historical dataset and the 2024+ dataset. To create a comprehensive dataset spanning all years, this script merges historical and current service inventory and service standard datasets.

These data are collected as a requirement under the [Policy on Service and Digital](https://www.tbs-sct.canada.ca/pol/doc-eng.aspx?id=32603).

### Datasets Consulted

**[GC Service Inventory and Service Performance](https://open.canada.ca/data/en/dataset/3ac0d080-6149-499a-8b06-7ce5f00ec56c):**  
An inventory of Government of Canada services, their associated service standards, and performance.

**[Departmental Plans and Departmental Results Reports](https://open.canada.ca/data/en/dataset/a35cf382-690c-4221-a971-cf0fd189a46f/resource/64774bc1-c90a-4ae2-a3ac-d9b50673a895):**  
Expenditures and Full-Time Equivalents (FTE) by program and organization.

### [Utilities Built and Shared for This Purpose](https://github.com/gc-performance/utilities)

- **Department Name Variant List**: A list of every organization, department, and agency with their associated names mapped to a single numeric ID.  
- **Program-Service ID Correspondence**: Mapping long-form program names from the 2018 service inventory to program IDs from Departmental Plans and Results Reports.

### Utilities from External Sources

**Inventory of Federal Organizations and Interests:**  
A extensive list of federal organization with unique numeric IDs, forming the basis for the variant list ID. Built for GC Infobase.  
- English: [Inventory of federal organisations and interests](https://open.canada.ca/data/en/dataset/a35cf382-690c-4221-a971-cf0fd189a46f/resource/7c131a87-7784-4208-8e5c-043451240d95)  
- French: [Répertoire des organisations et intérêts fédéraux](https://open.canada.ca/data/en/dataset/a35cf382-690c-4221-a971-cf0fd189a46f/resource/45069fe9-abe3-437f-97dd-3f64958bfa85)

---
### Conventions

The [Policy on Service and Digital](https://www.tbs-sct.canada.ca/pol/doc-eng.aspx?id=32603) requirement to publish service inventory information only applies to external and internal enterprise services. For this reason, **any service with a `service_scope` that does not include `EXTERN` or `ENTERPRISE` is removed** from indicator table calculations and consolidated datasets (`si.csv` and `ss.csv`). For versions with all published records, use the `si_all.csv` and `ss_all.csv` in the `outputs/utils` directory or `si_qa.csv` and `ss_qa.csv` in the `outputs/qa` directory.

When a 4-digit year represents a fiscal year, it refers to the calendar year **ending** in that fiscal year.

All .csv files produced by the script are **semi-colon separated** (`;`)

---
## Project Structure

### Files

- `main.py`: Orchestration script that calls other modules
- `requirements.txt`: Python libraries used in scripts
- `database.dbml`: DBML format schema for database layout and joins of files produced by script

#### `inputs/`: Downloaded for Processing (Unmodified)

- `ifoi_en.csv`: [Inventory of federal organisations and interests - in English](https://open.canada.ca/data/en/dataset/a35cf382-690c-4221-a971-cf0fd189a46f/resource/7c131a87-7784-4208-8e5c-043451240d95)
- `ifoi_fr.csv`: [Répertoire des organisations et intérêts fédéraux - en français](https://open.canada.ca/data/en/dataset/a35cf382-690c-4221-a971-cf0fd189a46f/resource/45069fe9-abe3-437f-97dd-3f64958bfa85)
- `org_var.csv`: [Department Name Variant List](https://github.com/gc-performance/utilities): A list of every organization, department, and agency with their associated names mapped to a single numeric ID. 
- `rbpo.csv`: [Departmental Plans and Departmental Results Reports](https://open.canada.ca/data/en/dataset/a35cf382-690c-4221-a971-cf0fd189a46f/resource/64774bc1-c90a-4ae2-a3ac-d9b50673a895)
- `serv_prog.csv`: [Program-Service ID Correspondence](https://github.com/gc-performance/utilities): Mapping long-form program names from the 2018 service inventory to program IDs from Departmental Plans and Results Reports
- `si_2018.csv`: [GC Service Inventory - Service Identification Information & Metrics (2018-2023)](https://open.canada.ca/data/en/dataset/3ac0d080-6149-499a-8b06-7ce5f00ec56c/resource/3acf79c0-a5f5-4d9a-a30d-fb5ceba4b60a)
- `si_2024.csv`: [GC Service Inventory - Service Identification Information & Metrics (2024)](https://open.canada.ca/data/en/dataset/3ac0d080-6149-499a-8b06-7ce5f00ec56c/resource/c0cf9766-b85b-48c3-b295-34f72305aaf6)
- `ss_2018.csv`: [GC Service Inventory - Service Standards & Performance Results (2018-2023)](https://open.canada.ca/data/en/dataset/3ac0d080-6149-499a-8b06-7ce5f00ec56c/resource/272143a7-533e-42a1-b72d-622116474a21)
- `ss_2024.csv`: [GC Service Inventory - Service Standards & Performance Results (2024)](https://open.canada.ca/data/en/dataset/3ac0d080-6149-499a-8b06-7ce5f00ec56c/resource/8736cd7e-9bf9-4a45-9eee-a6cb3c43c07e)
- `service_data_dict.json`: [GC Service Inventory - Data dictionary](https://open.canada.ca/data/en/recombinant-published-schema/service.json)

#### `outputs/`: Produced by the Script

*All .csv files are semi-colon (`;`) delimited*
- `si.csv`: Full service inventory merging 2018–2023 datasets with the 2024 dataset. *`service_scope` must contain `EXTERN` or `ENTERPRISE`*
- `ss.csv`: Full service standard dataset merging 2018–2023 datasets with the 2024 dataset. *`service_scope` must contain `EXTERN` or `ENTERPRISE`*

##### `outputs/indicators/`: Summary Files for Visualization and Review

*All tables were built with `service_scope` containing `EXTERN` or `ENTERPRISE`*
- `maf_all.csv`: a concatenated table with all the maf columns and scores (percentage of services that have service standards, percentage of applicable services that can be completed online end-to-end, percentage of client interaction points that are available online, percentage of services which have used client feedback to improve services in the year prior to reporting)
- `service_fte_spending.csv`: FTEs and spending for programs delivering services.
- `si_fy_interaction_sum.csv`: Sum of interactions by service, fiscal year, channel
- `si_fy_service_count.csv`: Unique services count by fiscal year.
- `si_oip.csv`: Online interaction points activation status by service for the latest available fiscal year.
- `si_reviews.csv`: Count of services reviewed or improved.
- `si_vol.csv`: Service interaction volume by service, fiscal year, and channel.
- `ss_tml_perf_vol.csv`: Timeliness performance standards by service and fiscal year.

##### `outputs/qa/`: Quality Assurance Files

- `si_qa.csv`: Full service inventory dataset with QA issues identified as separate columns. All `service_scope` included.
- `ss_qa.csv`: Full service standards dataset with QA issues identified as separate columns. All `service_scope` included.
- `si_qa_report.csv`: Critical errors for service inventory.
- `ss_qa_report.csv`: Critical errors for service standards.

##### `outputs/utils/`: Supporting Files

- `dd_field_names`: A list of translated field names and metadata for `si` (`resource_name`=`service`) and `ss` (`resource_name`=`service_std`).
- `dd_choices`: Correspondence table between codes that appear in `ss` and `si` and their names.
- `dept.csv`: A tidy list of departments with their IFOI IDs.
- `drf.csv`: A flattened Departmental plans and Departmental results report.
- `ifoi`: Exhaustive list of departmental info in English and French
- `org_var.csv`: List of variant department names and their IFOI ID.
- `sid_list.csv`: Unique list of service IDs with latest reporting year and department.
- `si_all.csv`: Full service inventory merging 2018–2023 datasets with the 2024 dataset. All `service_scope` included.
- `ss_all.csv`: Full service standard dataset merging 2018–2023 datasets with the 2024 dataset. All `service_scope` included.

#### `src/`: Source Code for Script

- `clean.py`: functions to clean and set up data
- `export.py`: functions to export data to CSV and SQLite database
- `load.py`: functions to load csv files to dataframes and download / refresh all inputs
- `merge.py`: process to align 2018 and 2024 service inventory and service standard datasets
- `process.py`: produces summaries and indicator files (`outputs/indicators/` directory)
- `qa.py`: performs quality assurance checks and produces qa outputs (`outputs/qa/` directory)
- `qa_issues_descriptions.csv`: definitions file for qa issues
- `utils.py`: misc utility functions, produces some files for `outputs/utils/` directory

#### `tests/`: Script tests

- `README.md`: placeholder readme documentation for tests
- `conftest.py`: configuration file for pytest
- `test_merge.py`: testing script for merge.py
- `test_outputs.py`: testing script for output files
- `generate_reference.py`: script for generating field names and types for all output files, see ref/ directory

##### `tests/ref`: Reference files for use with test scripts

- `reference_fields.csv`: Table of all tables, fields, and datatypes for use with test script

#### `notebooks/`: Jupyter notebooks for testing and experiments

### Data Formats
All CSV text files produced by the script are **semi-colon separated** (`;`).

## SQLite Database Releases

In addition to CSV files, this repository automatically generates a SQLite database containing all processed data in table format for easier querying and analysis. The database is published as a GitHub release and can be downloaded from the [releases page](https://github.com/gc-performance/service-data/releases).

### Release Schedule

- **Automatic**: New release created on every push to master branch
- **Daily**: Scheduled release at midnight Eastern Time
- **Manual**: Can be triggered through GitHub Actions workflow

### Release Format

- **Tag**: `service_data-[commit_hash]`
- **Name**: `Service Data Release YYYY-MM-DD (commit_hash)`
- Each release includes:
  - SQLite database file
  - All indivisual .csv files produced by script
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
├── README.md
├── context.md
├── database-normalized.dbml
├── database.dbml
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
│   └── ss_2024.csv
├── main.py
├── notebooks
│   ├── experiments-drf.ipynb
│   ├── experiments-unique-sids.ipynb
│   ├── experiments.ipynb
│   └── qa-uris.ipynb
├── outputs
│   ├── indicators
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
│   └── utils
│       ├── dd_choices.csv
│       ├── dd_field_names.csv
│       ├── dept.csv
│       ├── drf.csv
│       ├── ifoi.csv
│       ├── org_var.csv
│       ├── si_all.csv
│       ├── sid_list.csv
│       └── ss_all.csv
├── requirements.txt
├── src
│   ├── __init__.py
│   ├── clean.py
│   ├── export.py
│   ├── load.py
│   ├── merge.py
│   ├── process.py
│   ├── qa.py
│   ├── qa_issues_descriptions.csv
│   └── utils.py
└── tests
    ├── README.md
    ├── conftest.py
    ├── generate_reference.py
    ├── ref
    │   └── reference_fields.csv
    ├── test_merge.py
    └── test_outputs.py
```