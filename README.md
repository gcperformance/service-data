# Government of Canada Service Inventory
# Data review and analysis

# Service performance data

## Introduction - what is this for

This notebook will ingest and process service-related data into ready-to-use csv files for visualization purposes or further analysis.

Data collection changed in 2024 to allow departments to publish their own datasets directly to Open Government. With this change came some minor differences in the format and content between the 2018-2023 historical dataset currently on open government. In order to use the full dataset with all years, the following script merges the historical and current service inventory and service standard datasets.

The following datasets will be consulted:

**GC Service Inventory and Service Performance**: An inventory of Government of Canada services, their associated service standards and performance<br>
https://open.canada.ca/data/en/dataset/3ac0d080-6149-499a-8b06-7ce5f00ec56c

**Departmental Plans and Departmental Results Reports**: Expenditures and Full Time Equivalents (FTE) by Program and by Organization<br>
https://open.canada.ca/data/en/dataset/a35cf382-690c-4221-a971-cf0fd189a46f/resource/64774bc1-c90a-4ae2-a3ac-d9b50673a895

### Utilities built and shared specifically for this purpose:
https://github.com/gc-performance/utilities

**Department name variant list**: A list of every organization, department, agency, with their various associated names in order to align to a single numeric ID per department.  

**Program-service id correspondence**: Converting the long-form program names in the 2018 service inventory to the program id's from the Departmental Plans, Departmental Results Reports.

### Utilities from elsewhere online
**Inventory of federal organisations and interests**: A tidy list of organisation names that includes a single numeric ID. Is the basis for the variant list id. Built for GC Infobase.<br>
English: https://open.canada.ca/data/en/dataset/a35cf382-690c-4221-a971-cf0fd189a46f/resource/7c131a87-7784-4208-8e5c-043451240d95

French: https://open.canada.ca/data/en/dataset/a35cf382-690c-4221-a971-cf0fd189a46f/resource/45069fe9-abe3-437f-97dd-3f64958bfa85




### Conventions

Whenever a 4-digit year represents a fiscal year, the 4-digit year is the calendar year during which the fiscal year **ended**

### Files produced by scripts

#### Main files
- si.csv: full service inventory merging 2018-2023 dataset to 2024 dataset
- ss.csv: full service standard dataset merging 2018-2023 dataset to 2024 dataset

#### Helper files
- service_id_list.csv: The complete list of service IDs, including the latest fiscal year that service was reported and the relevant department.

#### Summary files for visualizations
- si_fy_interaction_sum.csv: Total volume of service interactions (applications) by fiscal year
- si_fy_service_count: Total count of unique services by fiscal year
- si_oip.csv: Activation status of online interaction points by service, fiscal year
- si_reviews: Total count of services that have been reviewed or improved in the last 5 years, by fiscal year
- si_vol: Volume of service interactions by service, fiscal year, channel
- ss_tml_perf_vol: Performance of timeliness service standards by service, fiscal year
- service_fte_spending: FTEs and spending for the programs delivering the services, by service, fiscal year.

#### Quality assurance files
- si_qa.csv: full service inventory dataset with qa issues identified via individual columsn and true/false
- ss_qa.csv: full service standards dataset with qa issues identified via individual columns and true/false
- si_qa_report: only critical errors listed per-error for service inventory
- ss_qa_report: only critical errors listed per-error for service standards