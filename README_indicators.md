# Government of Canada Service Inventory
## Script outputs

- `si.csv`: Full service inventory merging 2018–2023 datasets with the 2024 dataset. *`service_scope` must contain `EXTERN` or `ENTERPRISE`*
- `ss.csv`: Full service standard dataset merging 2018–2023 datasets with the 2024 dataset. *`service_scope` must contain `EXTERN` or `ENTERPRISE`*

Consult the data dictionaries on the Open Government Portal or "dd_field_names.csv" and "dd_choices.csv" for more detail on the fields contained in the service inventory and service standard datasets.


### Summary Files for Visualization and Review (outputs/indicators/)
*All tables were built with `service_scope` containing `EXTERN` or `ENTERPRISE`*
- `dp_metrics.csv`:
- `dp_services_rank.csv`:
- `drr_all.csv`: a concatenated table with all the drr indicator columns and scores (dr_2467: percentage of high-volume external services (>=45k applications) that are delivered online end-to-end, dr_2468: percentage of high-volume external services (>=45k applications and telephone enquiries) that met at least one service standard, dr_2469: percentage of applications for high-volume external services (>45k applications) that used the online channel), service_with_feedback_percentage: percentage of all services that have indicated something other than 'NON' in the client feedback channel field.
- `ib_all.csv`:
- `maf_all.csv`: a concatenated table with all the maf columns and scores (maf1: percentage of services that have service standards, maf2: percentage of service standards met, maf5: percentage of applicable services that can be completed online end-to-end, maf6: percentage of client interaction points that are available online, maf8: percentage of services which have used client feedback to improve services in the year prior to reporting)
- `oecd_digital_gov_survey.csv`:
- `service_fte_spending.csv`: FTEs and spending for programs delivering services.
- `si_oip.csv`: Online interaction points activation status by service for the latest available fiscal year.
- `si_reviews.csv`: Count of services reviewed or improved in the past 5 years.
- `si_vol.csv`: Service interaction volume by service, fiscal year, and channel.
- `ss_tml_perf_vol.csv`: Timeliness performance standards by service and fiscal year.

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
- `comparison.py` - Produces files that describe the differences between 2 files.
- `main.py` - Orchestrates the processing pipeline.
- `requirements.txt` - Lists python dependencies.
- `context.md` - Context on this dataset for use with LLM.
- `database.dbml` - **Draft** schema defining a database model.
- `tidy-script` - Bash script producing file paths for deleting inputs, outputs, caches, etc.


### Script files (src/)
- `clean.py`: functions to clean and set up data
- `create_sqlite.py`: process to generate the sqlite database
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
