# Government of Canada Service Inventory
## Service Performance Data Review and Analysis

### Introduction
This Python script ingests and processes service-related data into ready-to-use CSV files for visualization or further analysis.

In 2024, data collection processes changed to allow departments to publish their datasets directly to Open Government. This introduced minor differences in format and content between the 2018–2023 historical dataset and the 2024+ dataset. To create a comprehensive dataset spanning all years, this script merges historical and current service inventory and service standard datasets.

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
A tidy list of organization names with unique numeric IDs, forming the basis for the variant list ID. Built for GC Infobase.  
- English: [Inventory of federal organisations and interests](https://open.canada.ca/data/en/dataset/a35cf382-690c-4221-a971-cf0fd189a46f/resource/7c131a87-7784-4208-8e5c-043451240d95)  
- French: [Répertoire des organisations et intérêts fédéraux](https://open.canada.ca/data/en/dataset/a35cf382-690c-4221-a971-cf0fd189a46f/resource/45069fe9-abe3-437f-97dd-3f64958bfa85)

---

### Conventions
When a 4-digit year represents a fiscal year, it refers to the calendar year **ending** in that fiscal year.

All csv text files produced by the script are **semi-colon separated** (`;`)

---
## Project Structure

### Files

#### `inputs/`: Files Downloaded for Processing (Unmodified)
- Data such as `ifoi_en.csv`, `ifoi_fr.csv`, `si_2018.csv`, `si_2024.csv`, etc.

#### `outputs/`: Produced by the Script
- `si.csv`: Full service inventory merging 2018–2023 datasets with the 2024 dataset.
- `ss.csv`: Full service standard dataset merging 2018–2023 datasets with the 2024 dataset.

##### `utils/`: Supporting Files
- `dept.csv`: A tidy list of departments with their IFOI IDs.
- `drf.csv`: A flattened Departmental plans and Departmental results report.
- `ifoi_en.csv`: Exhaustive list of departmental info in english
- `ifoi_fr.csv`: Exhaustive list of departmental info in french
- `org_var.csv`: List of variant department names and their IFOI ID.

##### `indicators/`: Summary Files for Visualization and Review
- `maf1.csv`: .
- `maf2.csv`: .
- `maf5.csv`: Total service interactions by fiscal year.
- `maf6.csv`: Total service interactions by fiscal year.
- `maf8.csv`: Total service interactions by fiscal year.
- `service_fte_spending.csv`: FTEs and spending for programs delivering services.
- `service_id_list.csv`: List of service IDs with reporting year and department.
- `si_fy_interaction_sum.csv`: Unique services count by fiscal year.
- `si_fy_service_count.csv`: Unique services count by fiscal year.
- `si_oip.csv`: Online interaction points activation status by service and fiscal year.
- `si_reviews.csv`: Count of services reviewed or improved over the last 5 years.
- `si_vol.csv`: Service interaction volume by service, fiscal year, and channel.
- `ss_tml_perf_vol.csv`: Timeliness performance standards by service and fiscal year.

##### `qa/`: Quality Assurance Files
- `si_qa.csv`: Full service inventory dataset with QA issues identified.
- `ss_qa.csv`: Full service standards dataset with QA issues identified.
- `si_qa_report.csv`: Critical errors for service inventory.
- `ss_qa_report.csv`: Critical errors for service standards.

#### `src/`: Source Code for Script
- `clean.py`: functions to clean and set up data
- `export.py`: functions to export data to CSV and SQLite database
- `load.py`: functions to load csv files to dataframes and download / refresh all inputs
- `merge.py`: process to align 2018 and 2024 datasets
- `process.py`: produces summaries
- `qa.py`: performs quality assurance checks and produces qa outputs (in `outputs/qa/` directory)
- `qa_issues_descriptions.csv`: definitions file for qa issues
- `utils.py`: misc utility functions

### Data Formats

All CSV text files produced by the script are **semi-colon separated** (`;`).

In addition to CSV files, the script also generates a SQLite database (`service_data.db`) containing all CSV data in table format for easier querying and analysis.

---

## Directory structure
```
├── README.md
├── inputs
│   ├── ifoi_en.csv
│   ├── ifoi_fr.csv
│   ├── op_cost.csv
│   ├── org_var.csv
│   ├── rbpo.csv
│   ├── serv_prog.csv
│   ├── si_2018.csv
│   ├── si_2024.csv
│   ├── ss_2018.csv
│   └── ss_2024.csv
├── main.py
├── notebooks
│   ├── gc-service-data-script.ipynb
│   ├── qa-uris.ipynb
│   └── qa.ipynb
├── outputs
│   ├── indicators
│   │   ├── maf1.csv
│   │   ├── maf2.csv
│   │   ├── maf5.csv
│   │   ├── maf6.csv
│   │   ├── maf8.csv
│   │   ├── service_fte_spending.csv
│   │   ├── service_id_list.csv
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
│   ├── si.csv
│   ├── ss.csv
│   └── utils
│       ├── dept.csv
│       ├── drf.csv
│       ├── ifoi_en.csv
│       ├── ifoi_fr.csv
│       └── org_var.csv
├── requirements.txt
└── src
    ├── __init__.py
    ├── clean.py
    ├── export.py
    ├── load.py
    ├── merge.py
    ├── process.py
    ├── qa.py
    ├── qa_issues_descriptions.csv
    └── utils.py