# Government of Canada Service Inventory
# Data review and analysis

This repository hosts tools for working with the Government of Canada Service Inventory.

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