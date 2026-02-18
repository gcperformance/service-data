# Government of Canada Service Inventory
## Service Performance Data Review and Analysis

### Introduction

This Python project processes Government of Canada service-related data, merging historical and current datasets to produce structured CSV outputs for visualization and further analysis.

### Key Features
- **Data ingestion**: Downloads and processes service inventory and service standard performance data.
- **Dataset Merging**: Combines service inventory data from 2018-2023 historical datasets and 2024+ datasets from the Open Government Portal.
- **Quality Assurance**: Identifies and flags inconsistencies in datasets.
- **Output Generation**: Produces structured CSVs that reflect the latest information on the Open Government Portal.

Service inventory and service standard performance data are collected as a requirement under the [Policy on Service and Digital](https://www.tbs-sct.canada.ca/pol/doc-eng.aspx?id=32603).

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
- `--local`: Runs the script without downloading new datasets.
- `--help`: Provides additional help.

---
## Datasets Consulted

### [GC Service Inventory and Service Performance](https://open.canada.ca/data/en/dataset/3ac0d080-6149-499a-8b06-7ce5f00ec56c)
- **Files**: `si_2018.csv`, `si_2024.csv`, `ss_2018.csv`, `ss_2024.csv`
- **Content**: Government of Canada service inventory, associated standards, and performance, along with relevant data dictionaries.
- **Update Frequency**: Annually

### [Departmental Plans and Departmental Results Reports](https://open.canada.ca/data/en/dataset/a35cf382-690c-4221-a971-cf0fd189a46f/resource/64774bc1-c90a-4ae2-a3ac-d9b50673a895)
- **File**: `rbpo.csv`
- **Content**: Expenditures and Full-Time Equivalents (FTEs) by program and organization.
- **Update Frequency**: Annually

### [Program codes list as per the Government-wide Chart of Accounts](https://open.canada.ca/data/en/dataset/3c371e57-d487-49fa-bb0d-352ae8dd6e4e)
- **Files**: `cp-pc-XXYY-eng.csv`,`cp-pc-XXYY-fra.csv` 
- **Content**: List of valid programs in french and english by department for all fiscal years (20XX-20YY) from 2018-2019 to latest available.
- **Update Frequency**: Annually

### [Inventory of federal organisations and interests](https://open.canada.ca/data/en/dataset/a35cf382-690c-4221-a971-cf0fd189a46f/resource/7c131a87-7784-4208-8e5c-043451240d95)
- **Files**: `ifoi_en.csv`, `ifoi_fr.csv`
- **Content**: Comprehensive list of organizations relevant to the Government of Canada, notably departments and agencies.
- **Update Frequency**: Ad-hoc

### [Utilities developed for GC Service Inventory data analysis](https://github.com/gc-performance/utilities)
- **Files**: `org_var.csv`, `serv_prog.csv`
- **Content**: A manually updated list of every organization, department, and agency with their associated names mapped to a single numeric ID (`org_var.csv`). Long-form program names from the 2018-2023 service inventory mapped to program IDs from Departmental Plans and Results Reports (`serv_prog.csv`).
- **Update Frequency**: Ad-hoc

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

### Snapshots
- A copy of the datasets from a particular date (a snapshot) is maintained separately in order to have a consistent dataset with which to meet reporting requirements.
- Releases indicate which files are generated from the snapshot by prepending the date to the file name, for example `2025-03-01_si.csv` is equivalent to `si.csv`, but based on data from March 1, 2025.
- Running the main.py script will generate new outputs with the static snapshot input files for the service inventory (`si_2018.csv`, `si_2024.csv`), service standards (`ss_2018.csv`, `ss_2024.csv`), and departmental results (`rbpo.csv`) data, but retrieving the latest other data.

---
## Script outputs (outputs/)
*All script outputs are present in the releases and available to consult remotely*

- `si.csv`: Full service inventory merging 2018–2023 datasets with the 2024 dataset. *`service_scope` must contain `EXTERN` or `ENTERPRISE`*
- `ss.csv`: Full service standard dataset merging 2018–2023 datasets with the 2024 dataset. *`service_scope` must contain `EXTERN` or `ENTERPRISE`*
- `debug.log`: Log file of all processes run by script.
- `error.log`: Log file of all errors encountered by script while being run.

### Summary Files for Visualization and Review (outputs/indicators/)
For a more detailed description of each file and field, please consult [README_indicators](https://github.com/gcperformance/service-data/blob/master/README_indicators.md)

- `dp_metrics.csv`: Miscellaneous metrics used in preparation of the "Data pack" by fiscal year.
- `dp_services_rank.csv`: Top 20 services according to requirements for "Data pack" by fiscal year.
- `drr_all.csv`: DRR and PIP indicator scores by fiscal year.
- `ib_all.csv`: Table to review and confirm GC Infobase figures by organization and fiscal year.
- `maf_all.csv`: Results of MAF questions by organization and fiscal year.
- `oecd_digital_gov_survey.csv`: Results for OECD Digital Government Survey by fiscal year.
- `service_fte_spending.csv`: FTEs and spending for programs delivering services.
- `si_oip.csv`: Online interaction points activation status by service and fiscal year.
- `si_reviews.csv`: Count of services reviewed or improved in the past 5 years by organization and fiscal year.
- `si_vol.csv`: Service interaction volume by service, fiscal year, and channel.
- `ss_tml_perf_vol.csv`: Timeliness performance standards by service, fiscal year, and channel.

### Quality Assurance Review Files (outputs/qa/)
- `si_qa.csv`: Full service inventory dataset with QA issues identified as separate columns. All `service_scope` included.
- `ss_qa.csv`: Full service standards dataset with QA issues identified as separate columns. All `service_scope` included.
- `si_qa_report.csv`: Prioritized issues in service inventory.
- `ss_qa_report.csv`: Prioritized issues in service standards.

### Utilities and Supporting Files (outputs/utils/)
- `dd_choices.csv`: Correspondence table between codes that appear in `ss` and `si` and their names, "dd" referring to data dictionary.
- `dd_field_names.csv`: A list of translated field names and metadata for `si` (`resource_name`=`service`) and `ss` (`resource_name`=`service_std`).
- `dd_program`: List of valid program codes and names.
- `dept.csv`: A tidy unique list of departments with their IFOI IDs.
- `drf.csv`: A flattened Departmental plans and Departmental results report.
- `ifoi.csv`: Exhaustive list of departmental info in English and French
- `org_var.csv`: Duplicate-permitted list of variant department names and their IFOI ID.
- `program_list.csv`: 
- `sid_list.csv`: Unique list of service IDs with latest reporting year and department.
- `si_all.csv`: Full service inventory merging 2018–2023 datasets with the 2024 dataset. All `service_scope` included.
- `ss_all.csv`: Full service standard dataset merging 2018–2023 datasets with the 2024 dataset. All `service_scope` included.

---
## Other files
- `main.py` - Orchestrates the processing pipeline.
- `requirements.txt` - Lists python dependencies.
- `context.md` - Context on this dataset for use with LLM.
- `database.dbml` - **Draft** schema defining a database model.
- `tidy-script` - Bash script producing file paths for deleting inputs, outputs, caches, etc.


### Python script files (src/)
- `clean.py`: functions to clean and set up data
- `comp.py`: functions compare files against one another, for example for snapshots
- `export.py`: functions to export data to CSV (semi-colon delimited)
- `load.py`: functions to load csv files to dataframes and download / refresh all inputs
- `merge.py`: process to align 2018 and 2024 service inventory and service standard datasets
- `process.py`: produces summaries and indicator files (`outputs/indicators/` directory)
- `qa.py`: performs quality assurance checks and produces qa outputs (`outputs/qa/` directory)
- `qa_issues_descriptions.csv`: definitions file for qa issues
- `utils.py`: misc utility functions, produces some files for `outputs/utils/` directory

### Tests (tests/)

- `README.md`: placeholder readme documentation for tests
- `conftest.py`: configuration file for pytest
- `test_merge.py`: testing script for merge.py
- `test_outputs.py`: testing script for output files
- `generate_reference.py`: script for generating field names and types for all output files, see ref/ directory
- `reference_fields.csv`: Table of all tables, fields, and datatypes for use with test script

---

### Release Schedule

- **Automatic**: New release created on every push to master branch
- **Weekly**: Scheduled release on Tuesday mornings at midnight EST
- **Manual**: Can be triggered through GitHub Actions workflow

### Release Format

- **Tag**: `service_data-[commit_hash]`
- **Name**: `Service Data Release YYYY-MM-DD (commit_hash)`
- Each release includes:
  - All individual .csv files produced by script
  - Timestamp of generation (Eastern Time)
  - Git commit hash for traceability

---
## Directory structure for project
*Given that files produced by the script are made available in releases, all transitory input and output files are no longer tracked with git, or included in the repo. Releases have a flat structure, so the directory structure below is only relevant if you clone the repo and run the script.*

```
.
├── README.md
├── README_indicators.md
├── comparison.py
├── context.md
├── database.dbml
├── inputs
│   ├── backups
│   │   ├── cp-pc-1819-eng.csv
│   │   ├── cp-pc-1819-fra.csv
│   │   ├── cp-pc-1920-eng.csv
│   │   ├── cp-pc-1920-fra.csv
│   │   ├── cp-pc-2021-eng.csv
│   │   ├── cp-pc-2021-fra.csv
│   │   ├── cp-pc-2122-eng.csv
│   │   ├── cp-pc-2122-fra.csv
│   │   ├── cp-pc-2223-eng.csv
│   │   ├── cp-pc-2223-fra.csv
│   │   ├── cp-pc-2324-eng.csv
│   │   ├── cp-pc-2324-fra.csv
│   │   ├── cp-pc-2425-eng.csv
│   │   ├── cp-pc-2425-fra.csv
│   │   ├── cp-pc-2526-eng.csv
│   │   ├── cp-pc-2526-fra.csv
│   │   ├── ifoi_en.csv
│   │   ├── ifoi_fr.csv
│   │   ├── org_var.csv
│   │   ├── rbpo.csv
│   │   ├── serv_prog.csv
│   │   ├── service_data_dict.json
│   │   ├── si_2018.csv
│   │   ├── si_2024.csv
│   │   ├── sid_registry.csv
│   │   ├── ss_2018.csv
│   │   └── ss_2024.csv
│   ├── cp-pc-1819-eng.csv
│   ├── cp-pc-1819-fra.csv
│   ├── cp-pc-1920-eng.csv
│   ├── cp-pc-1920-fra.csv
│   ├── cp-pc-2021-eng.csv
│   ├── cp-pc-2021-fra.csv
│   ├── cp-pc-2122-eng.csv
│   ├── cp-pc-2122-fra.csv
│   ├── cp-pc-2223-eng.csv
│   ├── cp-pc-2223-fra.csv
│   ├── cp-pc-2324-eng.csv
│   ├── cp-pc-2324-fra.csv
│   ├── cp-pc-2425-eng.csv
│   ├── cp-pc-2425-fra.csv
│   ├── cp-pc-2526-eng.csv
│   ├── cp-pc-2526-fra.csv
│   ├── ifoi_en.csv
│   ├── ifoi_fr.csv
│   ├── org_var.csv
│   ├── rbpo.csv
│   ├── serv_prog.csv
│   ├── service_data_dict.json
│   ├── si_2018.csv
│   ├── si_2024.csv
│   ├── sid_registry.csv
│   ├── snapshots
│   │   ├── 2025-03-01
│   │   │   ├── rbpo.csv
│   │   │   ├── si_2018.csv
│   │   │   ├── si_2024.csv
│   │   │   ├── ss_2018.csv
│   │   │   └── ss_2024.csv
│   │   └── 2026-01-19
│   │       ├── rbpo.csv
│   │       ├── si_2018.csv
│   │       ├── si_2024.csv
│   │       ├── ss_2018.csv
│   │       └── ss_2024.csv
│   ├── ss_2018.csv
│   └── ss_2024.csv
├── main.py
├── notebooks
│   ├── dd.ipynb
│   ├── drf-yrs.ipynb
│   ├── experiment-snapshot-diff.ipynb
│   ├── experiment-template.ipynb
│   ├── program_list.ipynb
│   ├── qa-uris.ipynb
│   └── qa_checks.ipynb
├── outputs
│   ├── debug.log
│   ├── errors.log
│   ├── indicators
│   │   ├── dp_metrics.csv
│   │   ├── dp_services_rank.csv
│   │   ├── drr_all.csv
│   │   ├── ib_all.csv
│   │   ├── maf_all.csv
│   │   ├── service_fte_spending.csv
│   │   ├── si_oip.csv
│   │   ├── si_reviews.csv
│   │   ├── si_vol.csv
│   │   └── ss_tml_perf_vol.csv
│   ├── qa
│   │   ├── si_qa.csv
│   │   ├── si_qa_report.csv
│   │   ├── ss_qa.csv
│   │   └── ss_qa_report.csv
│   ├── si.csv
│   ├── snapshots
│   │   ├── 2025-03-01
│   │   │   ├── indicators
│   │   │   │   ├── dp_metrics.csv
│   │   │   │   ├── dp_services_rank.csv
│   │   │   │   ├── drr_all.csv
│   │   │   │   ├── ib_all.csv
│   │   │   │   ├── maf_all.csv
│   │   │   │   ├── service_fte_spending.csv
│   │   │   │   ├── si_fy_interaction_sum.csv
│   │   │   │   ├── si_fy_service_count.csv
│   │   │   │   ├── si_oip.csv
│   │   │   │   ├── si_reviews.csv
│   │   │   │   ├── si_vol.csv
│   │   │   │   └── ss_tml_perf_vol.csv
│   │   │   ├── qa
│   │   │   │   ├── si_qa.csv
│   │   │   │   ├── si_qa_report.csv
│   │   │   │   ├── ss_qa.csv
│   │   │   │   └── ss_qa_report.csv
│   │   │   ├── si.csv
│   │   │   ├── si_comparison.csv
│   │   │   ├── ss.csv
│   │   │   ├── ss_comparison.csv
│   │   │   └── utils
│   │   │       ├── drf.csv
│   │   │       ├── si_all.csv
│   │   │       ├── sid_list.csv
│   │   │       └── ss_all.csv
│   │   └── 2026-01-19
│   │       ├── indicators
│   │       │   ├── dp_metrics.csv
│   │       │   ├── dp_services_rank.csv
│   │       │   ├── drr_all.csv
│   │       │   ├── maf_all.csv
│   │       │   ├── service_fte_spending.csv
│   │       │   ├── si_oip.csv
│   │       │   ├── si_reviews.csv
│   │       │   ├── si_vol.csv
│   │       │   └── ss_tml_perf_vol.csv
│   │       ├── si.csv
│   │       ├── si_comparison.csv
│   │       ├── ss.csv
│   │       └── utils
│   │           ├── drf.csv
│   │           ├── si_all.csv
│   │           ├── sid_list.csv
│   │           └── ss_all.csv
│   ├── ss.csv
│   └── utils
│       ├── dd_choices.csv
│       ├── dd_field_names.csv
│       ├── dd_program.csv
│       ├── dept.csv
│       ├── drf.csv
│       ├── ifoi.csv
│       ├── org_var.csv
│       ├── program_list.csv
│       ├── si_all.csv
│       ├── sid_list.csv
│       └── ss_all.csv
├── requirements.txt
├── src
│   ├── __init__.py
│   ├── clean.py
│   ├── comp.py
│   ├── export.py
│   ├── load.py
│   ├── merge.py
│   ├── process.py
│   ├── qa.py
│   ├── qa_issues_descriptions.csv
│   └── utils.py
├── ssl_test.py
├── tests
│   ├── README.md
│   ├── conftest.py
│   ├── generate_reference.py
│   ├── ref
│   │   ├── gc_infobase_fields.csv
│   │   └── reference_fields.csv
│   ├── test_merge.py
│   └── test_outputs.py
└── tidy-script
```
