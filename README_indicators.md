# Government of Canada Service Inventory
## Detailed description of script outputs
Consult the data dictionaries on the Open Government Portal or "dd_field_names.csv" and "dd_choices.csv" for more detail on the fields contained in the service inventory and service standard datasets. This readme assumes basic familiarity with these datasets.

### `si.csv`
Full service inventory merging 2018–2023 datasets with the 2024+ dataset. *`service_scope` must contain `EXTERN` or `ENTERPRISE`*
- `fiscal_yr`: Federal government fiscal year, April 1, XXXX, to March 31, YYYY, in format XXXX-YYYY. Indicates the time period for which the data was reported.
- `service_id`: Identification number for a service in the service inventory
- `service_name_en`: Service name in English
- `service_name_fr`: Service name in French
- `service_description_en`: Short description of service in English
- `service_description_fr`: Short description of service in French
- `service_type`: Identifies the service type as outlined in the Guideline on Service and Digital. Multiple values are separated by a comma (,). Controlled values described in `dd_choices.csv`.
- `service_recipient_type`: Identifies whether the service serves specific clients or groups or benefit society at large, rather than specific clients.
- `service_scope`: Indicates whether the service is external or internal to government. Multiple values must be separated by a comma (,). Controlled values described in `dd_choices.csv`.
- `client_target_groups`: Identifies the clients or target groups of the service. Multiple values must be separated by a comma (,). Controlled values described in `dd_choices.csv`.
- `program_name_en`: English name of the program(s) responsible for delivering the service, as per the Chart of Accounts. Multiple values must be separated by a comma (,).
- `program_name_fr`: French name of the program(s) responsible for delivering the service, as per the Chart of Accounts. Multiple values must be separated by a comma (,).
- `client_feedback_channel`: Identifies which channels, if any, provide users of a service an opportunity to provide feedback on their level of satisfaction with the service. Multiple values must be separated by a comma (,). Controlled values described in `dd_choices.csv`.
- `service_fee`: Identifies whether a service fee is collected for the provision of the service
- `last_GBA`: *No longer collected as of 2023-24* Last year a GBA+ analysis was performed for the service. 
- `ident_platform`: *No longer collected as of 2023-24* Which sign-in platform is used for online service delivery.
- `ident_platform_comments`: *No longer collected as of 2023-24* Free-text comments regarding online sign-in platform.
- `os_account_registration`: Identifies whether a client can register or enroll for a personal account where they can make use of other interaction points.
- `os_authentication`: Identifies whether a client can authenticate their identity online.
- `os_application`: Identifies whether a client can apply for a service online.
- `os_decision`: Identifies whether a client can be notified online of the outcome of their request for this service.
- `os_issuance`: Identifies whether a client can receive the service output online, perhaps in the form of permits, certificates, money or information.
- `os_issue_resolution_feedback`: Identifies whether a client can seek resolution to their issues or provide feedback online.
- `os_comments_client_interaction_en`: English comments related to online services - client Interaction points. For any interaction points reported as "Not Applicable", comments have to be provided.
- `os_comments_client_interaction_fr`: French comments related to online services - client Interaction points. For any interaction points reported as "Not Applicable", comments have to be provided.
- `how_has_the_service_been_assessed_for_accessibility`: *No longer collected as of 2023-24* How the online component of the service has been assessed for ICT accessibility
- `last_service_review`: Identifies the fiscal year when the most recent service review was completed.
- `last_service_improvement`: Identifies the most recent year in which this service was improved based on client feedback.
- `sin_usage`: Identifies whether the Social Insurance Number (SIN) is used in the delivery of the service.
- `cra_bn_identifier_usage`: Identifies whether the Canada Revenue Agency's Business Number is used in the delivery of the service as the standard identifier in accordance with the Data reference standard on the business number.
- `num_phone_enquiries`: Identifies the number of enquiries about the service received in this fiscal year. Note: This field represents only requests for information about the service. Report service requests or applications submitted by telephone in the "telephone applications" field. Note: This field is not included in 'Total Applications'.
- `num_applications_by_phone`: Identifies the number of applications submitted in a fiscal year for the telephone channel.
- `num_website_visits`: Identifies the number of visits to the service's website in a fiscal year. Note: This field is not included in 'Total Applications'.
- `num_applications_online`: Identifies the number of applications submitted in a fiscal year for the online channel. Examples include applications received via a website/online portal, via web forms (e.g., MyPayEnquiry) and digitally administered audits and evaluations.
- `num_applications_in_person`: Identifies number of applications received in-person in a fiscal year for the service. Examples include in-person applications, volume of inspections, audits, evaluations, etc.
- `num_applications_by_mail`: Identifies the number of applications received through postal mail in a fiscal year.
- `num_applications_by_email`: Identifies the number of applications received through email in a fiscal year for the service.
- `num_applications_by_fax`: Identifies the number of applications received through fax in a fiscal year for the service. 
- `num_applications_by_other`: Identifies the number of applications received through other channels not listed in a fiscal year for the service. If service volumes are not tracked by channel, they are included in this field.
- `special_remarks_en`: Provides additional space for English comments related to volumetrics information.
- `special_remarks_fr`: Provides additional space for French comments related to volumetrics information.
- `service_uri_en`: Identifies the departmental webpage where the service is described and/or accessed in English.
- `service_uri_fr`: Identifies the departmental webpage where the service is described and/or accessed in French.
- `num_applications_total`: Identifies the total number of applications submitted in a fiscal year for all application channels.
- `org_name_variant`: The name or reference code for the organization submitting the information. There are different values for the 2018-2023 dataset and the 2024+ dataset.
- `org_id`: Unique numeric identifier for departments, agencies, and any other federal organization. Based on the "Inventory of Federal Organizations and Interests" which supports GC Infobase.
- `department_en`: Name of department or agency in English. Defaults to the "Applied title" when it is available, and "Legal title" when it is not. Based on the "Inventory of Federal Organizations and Interests" which supports GC Infobase.
- `department_fr`: Name of department or agency in French. Defaults to the "Applied title" when it is available, and "Legal title" when it is not. Based on the "Inventory of Federal Organizations and Interests" which supports GC Infobase.
- `program_id`: Alpha-numeric code that is uniquely tied to a program in the Chart of Accounts, and is used in DRR and DP reporting.
- `automated_decision_system_description_en`: Description of automated decision system in English.
- `automated_decision_system_description_fr`: Description of automated decision system in French.
- `automated_decision_system`: Identifies whether an automated decision system is used to make or assist officers in making administrative decisions.
- `service_scope_ext_or_ent`: Calculated field that indicates whether the service is external or internal enterprise to assist in quick filtering of relevant services.
- `fy_org_id_service_id`: Constructed unique key. `fiscal_yr` (underscore) `org_id` (underscore) `service_id`.

### `ss.csv`
Full service standard dataset merging 2018–2023 datasets with the 2024+ dataset. *`service_scope` must contain `EXTERN` or `ENTERPRISE`*
- `fiscal_yr`: Federal government fiscal year, April 1, XXXX, to March 31, YYYY, in format XXXX-YYYY. Indicates the time period for which the data was reported.
- `service_id`: Identification number for a service in the service inventory
- `service_name_en`: Service name in English
- `service_name_fr`: Service name in French
- `service_standard_id`: Identification number for a service standard in the service inventory
- `service_standard_en`: Service standard name in English
- `service_standard_fr`: Service standard name in French
- `type`: Identifies the type of service standard as defined in the Guideline on Service and Digital. Controlled values described in `dd_choices.csv`.
- `gcss_tool_fiscal_yr`: *No longer collected as of 2023-24* Identifies the fiscal year in which the service standard was last reviewed using the GC Service Standard Assessment Tool available in the Guideline on Service and Digital.
- `channel`: Identifies the service channel to which the service standard applies. Controlled values described in `dd_choices.csv`.
- `channel_comments_en`: Comments in English related to the service standard channel and provides explanation of "Other" channel selection.
- `channel_comments_fr`: Comments in French related to the service standard channel and provides explanation of "Other" channel selection.
- `target_type`: *No longer collected as of 2023-24* Indicates whether the results of the service standard are expressed as a percentage or reported directly without supporting volumes.
- `target`: The frequency that the organization expects to meet service standard (reported as a percentage).
- `volume_meeting_target`: Identifies the number of final outputs issued appropriate to the service (eg. payments issued, requests completed, etc) during the fiscal year that met a particular service standard target for a service. Blank indicates no information available, while 0 indicates that no final outputs issued met service standard targets.
- `total_volume`: Identifies the total number of final outputs issued appropriate to the service (eg. payments issued, requests completed, etc) during the fiscal year. Blank indicates no information available, while 0 indicates no final outputs issued.
- `performance`: Identifies the result achieved for this service standard. This is the "Business Volume That Met Service Standard Target" divided by the "Total Volume" and is automatically calculated for the 2024+ dataset.
- `comments_en`: Comments on the service standard in general (English)
- `comments_fr`: Comments on the service standard in general (French)
- `target_met`: Indicates whether the target was met. Automatically generated in the 2024+ dataset, see below for examples of how the calculation works.
- `standards_targets_uri_en`: Identifies the departmental webpage (Canada.ca) where the service standards and targets are published in English.
- `standards_targets_uri_fr`: Identifies the departmental webpage (Canada.ca) where the service standards and targets are published in French.
- `performance_results_uri_en`: Identifies the departmental webpage where the real-time performance results for a service are published in English.
- `performance_results_uri_fr`: Identifies the departmental webpage where the real-time performance results for a service are published in French.
- `org_name_variant`: The name or reference code for the organization submitting the information. There are different values for the 2018-2023 dataset and the 2024+ dataset.
- `org_id`: Unique numeric identifier for departments, agencies, and any other federal organization. Based on the "Inventory of Federal Organizations and Interests" which supports GC Infobase.
- `department_en`: Name of department or agency in English. Defaults to the "Applied title" when it is available, and "Legal title" when it is not. Based on the "Inventory of Federal Organizations and Interests" which supports GC Infobase.
- `department_fr`: Name of department or agency in French. Defaults to the "Applied title" when it is available, and "Legal title" when it is not. Based on the "Inventory of Federal Organizations and Interests" which supports GC Infobase.
- `fy_org_id_service_id`: Constructed unique key. `fiscal_yr` (underscore) `org_id` (underscore) `service_id`.
- `fy_org_id_service_id_std_id`: Constructed unique key. `fiscal_yr` (underscore) `org_id` (underscore) `service_id` (underscore) `service_standard_id`.

#### Examples for how `target_met` is calculated in the 2024+ dataset.
|target|volume_meeting_target|total_volume|performance|performance note|target_met|target_met note|
|---|---|---|---|---|---|---|
|0.2|0|50|0|Performance is calculated because both volumes are non-blank and total_volume is greater than 0.|N|	|
|0.2|5|50|0.1|Performance is calculated because both volumes are non-blank and total_volume is greater than 0.|N|Target met is calculated because there is a target and performance|
|0.2|10|50|0.2|Performance is calculated because both volumes are non-blank and total_volume is greater than 0. |Y|Target met is calculated because there is a target and performance|
|0.2|30|50|0.6|Performance is calculated because both volumes are non-blank and total_volume is greater than 0.|Y|Target met is calculated because there is a target and performance|
|0|10|50|0.2|Performance is calculated because both volumes are non-blank and total_volume is greater than 0.|NA|Target met is NA because there is no target.|
|blank|10|50|0.2|Performance is calculated because both volumes are non-blank and total_volume is greater than 0.|NA|Target met is NA because there is no target.|
|0.2|blank|50|blank|Performance is blank because one volume is blank.|NA|Target met is NA because performance is blank|
|blank|blank|50|blank|Performance is blank because one volume is blank.|NA|Target met is NA because performance is blank|
|blank|blank|blank|blank|Performance is blank because one volume is blank.|NA|Target met is NA because performance is blank|
|0.2|10|blank|blank|Performance is blank because one volume is blank.|NA|Target met is NA because performance is blank|
|0.2|blank|blank|blank|Performance is blank because one volume is blank.|NA|Target met is NA because performance is blank|
|0.2|10|0|blank|Performance is blank because total volume is 0.|NA|Target met is NA because performance is blank|
|0.2|0|0|blank|Performance is blank because total volume is 0.|NA|Target met is NA because performance is blank|


### Summary Files for Visualization and Review (outputs/indicators/)
#### `dp_metrics.csv`
Table that supports the creation of the "Data Pack" among many other products. Generated by `src/process.py/datapack`. This table is unusual in that the rows do not represent comparable records, but rather a set of distinct indicators. Comparison occurs across columns by fiscal year.

- `fiscal_yr`: Federal government fiscal year, April 1, XXXX, to March 31, YYYY, in format XXXX-YYYY.
- `total_services`: Number of distinct services in the service inventory. Counted using a constructed unique key `fy_org_id_service_id`, which is `fiscal_yr` (underscore) `org_id` (underscore) `service_id`. Filtered for `service_scope` containing `EXTERN` or `ENTERPRISE`.
- `num_transactions_total`: Sum of all application amounts with telephone enquiries added for services with `service_scope` containing `EXTERN` or `ENTERPRISE`.
- `num_applications_online`: Sum of online application amounts for services with `service_scope` containing `EXTERN` or `ENTERPRISE`.
- `num_phone_apps_enquiries`: Sum of telephone application amounts with telephone enquiries added for services with `service_scope` containing `EXTERN` or `ENTERPRISE`.
- `num_applications_in_person`: Sum of in-person application amounts for services with `service_scope` containing `EXTERN` or `ENTERPRISE`.
- `online_percentage`: Percentage of online applications as a fraction of total transactions. `num_applications_online / num_transactions_total`.
- `phone_percentage`: Percentage of telephone applications and enquiries as a fraction of total transactions. `num_phone_apps_enquiries / num_transactions_total`.
- `in-person_percentage`: Percentage of in-person applications as a fraction of total transactions. `num_applications_in_person / num_transactions_total`.
- `total_services_omni`: Number of distinct *omnichannel* services in the service inventory. Omnichannel is defined as there being a value reported for phone enquiries or applications, online applications, and in-person applications. Counted using a constructed unique key `fy_org_id_service_id`, which is `fiscal_yr` (underscore) `org_id` (underscore) `service_id`. Filtered for `service_scope` containing `EXTERN` or `ENTERPRISE`.
- `num_transactions_total_omni`: Sum of all application amounts with telephone enquiries added for omnichannel services with `service_scope` containing `EXTERN` or `ENTERPRISE`.
- `num_applications_online_omni`: Sum of online application amounts for omnichannel services with `service_scope` containing `EXTERN` or `ENTERPRISE`.
- `num_phone_apps_enquiries_omni`: Sum of telephone application amounts with telephone enquiries added for omnichannel services with `service_scope` containing `EXTERN` or `ENTERPRISE`.
- `num_applications_in_person_omni`: Sum of in-person application amounts for omnichannel services with `service_scope` containing `EXTERN` or `ENTERPRISE`.
- `online_percentage_omni`: Percentage of online applications as a fraction of total transactions for omnichannel services. `num_applications_online_omni / num_transactions_total_omni`.
- `phone_percentage`: Percentage of telephone applications and enquiries as a fraction of total transactions for omnichannel services. `num_phone_apps_enquiries_omni / num_transactions_total_omni`.
- `in-person_percentage`: Percentage of in-person applications as a fraction of total transactions. `num_applications_in_person_omni / num_transactions_total_omni`.
- `total_orgs_ext`: Number of distinct organizations in the service inventory that have external services. Counted using unique `org_id` for services with `service_scope` containing `EXTERN`.
- `total_services_ext`: Number of distinct external services in the service inventory. Counted using a constructed unique key `fy_org_id_service_id`, which is `fiscal_yr` (underscore) `org_id` (underscore) `service_id`. Filtered for `service_scope` containing `EXTERN`.
- `num_applications_online_ext`: Sum of online application amounts for external services (`service_scope` contains `EXTERN`).
- `num_applications_in_person_ext`: Sum of in-person application amounts for external services (`service_scope` contains `EXTERN`).
- `num_phone_apps_enquiries_ext`: Sum of telephone application amounts with telephone enquiries added for external services (`service_scope` contains `EXTERN`).
- `num_applications_by_mail_ext`: Sum of mail-in application amounts for external services with `service_scope` containing `EXTERN`.
- `num_transactions_total_ext`: Sum of all application amounts with telephone enquiries added for external services (`service_scope` contains `EXTERN`).
- `num_applications_online_ext_excl_services`: Sum of online application amounts for external services (`service_scope` contains `EXTERN`). Excludes a subset of services for historical comparability and relevance.
- `num_applications_in_person_ext_excl_services`: Sum of in-person application amounts for external services (`service_scope` contains `EXTERN`). Excludes a subset of services for historical comparability and relevance.
- `num_transactions_total_ext_excl_services`: Sum of all application amounts with telephone enquiries added for external services (`service_scope` contains `EXTERN`). Excludes a subset of services for historical comparability and relevance. Note that the services excluded only have an impact on the online and in-person application amounts.
- `total_programs_ext`: Number of distinct programs in the service inventory that deliver external services. Counted using unique `program_id` values, with records that have multiple ids being split up, for services where `service_scope` contains `EXTERN`.
- `total_services_ext_online`: Number of distinct external services (`service_scope` contains `EXTERN`) in the service inventory that are online end-to-end, which means all applicable interaction points are online and there is at least one interaction point online.
- `ext_online_service_percentage`: Percentage of external services (`service_scope` contains `EXTERN`) that are online end-to-end. `total_services_ext_online / total_services_ext`.
- `total_services_ext_1oip`: Number of distinct external services (`service_scope` contains `EXTERN`) in the service inventory that have at least one interaction point online.
- `ext_1oip_online_service_percentage`: Percentage of external services (`service_scope` contains `EXTERN`) that have at least one interaction point online. `total_services_ext_1oip / total_services_ext`.
- `total_standards_ext`: Number of distinct service standards in the service inventory. Excludes service standards that have no assessment of whether their target was met, i.e. excludes all `target_met=NA`. Counted using a constructed unique key `fy_org_id_service_id_std_id`, which is `fiscal_yr` (underscore) `org_id` (underscore) `service_id` (underscore) `service_standard_id`. Filtered for services where `service_scope` contains `EXTERN`.
- `total_standards_met_ext`: Number of distinct service standards that met their target (`target_met = Y`) in the service inventory. Counted using a constructed unique key `fy_org_id_service_id_std_id`, which is `fiscal_yr` (underscore) `org_id` (underscore) `service_id` (underscore) `service_standard_id`. Filtered for services where `service_scope` contains `EXTERN`.
- `ext_standard_met_percentage`: Percentage of external service standards that met their target. `total_standards_met_ext / total_standards_ext`
- `total_services_ext_hv`: Number of distinct external services in the service inventory that have a total number of interactions (applications from all channels + telephone enquiries) greater than or equal to 45,000. Counted using a constructed unique key `fy_org_id_service_id`, which is `fiscal_yr` (underscore) `org_id` (underscore) `service_id`. Filtered for `service_scope` containing `EXTERN`.
- `total_services_ext_hv_online`: Number of distinct external high-volume online-end-to-end services in the service inventory that have a total number of interactions. Counted using a constructed unique key `fy_org_id_service_id`, which is `fiscal_yr` (underscore) `org_id` (underscore) `service_id`. Filtered for `service_scope` containing `EXTERN`. Online end-to-end is defined as all applicable interaction points are online and there is at least one interaction point online.High volume services are those with total interactions (applications from all channels + telephone enquiries) greater than or equal to 45,000 in a year. 
- `ext_hv_online_service_percentage`: Percentage of external high volume services that are online end-to-end. `total_services_ext_hv_online / total_services_ext_hv`
- `total_services_ext_hv_1oip`: Number of distinct external high-volume services (`service_scope` contains `EXTERN`) in the service inventory that have at least one interaction point online. High volume services are those with total interactions (applications from all channels + telephone enquiries) greater than or equal to 45,000 in a year.
- `ext_hv_1oip_online_service_percentage`: Percentage of external high-volume services (`service_scope` contains `EXTERN`) that have at least one interaction point online. `total_services_ext_hv_1oip / total_services_ext_hv`.
- `total_standards_ext_hv`: Number of distinct service standards in the service inventory for high-volume, external services. Excludes service standards that have no assessment of whether their target was met, i.e. excludes all `target_met=NA`. Counted using a constructed unique key `fy_org_id_service_id_std_id`, which is `fiscal_yr` (underscore) `org_id` (underscore) `service_id` (underscore) `service_standard_id`. Filtered for services where `service_scope` contains `EXTERN`. High volume services are those with total interactions (applications from all channels + telephone enquiries) greater than or equal to 45,000 in a year.
- `total_standards_met_ext_hv`: Number of distinct service standards that met their target (`target_met = Y`) in the service inventory for high-volume, external services. Counted using a constructed unique key `fy_org_id_service_id_std_id`, which is `fiscal_yr` (underscore) `org_id` (underscore) `service_id` (underscore) `service_standard_id`. Filtered for services where `service_scope` contains `EXTERN`. High volume services are those with total interactions (applications from all channels + telephone enquiries) greater than or equal to 45,000 in a year.
- `ext_hv_standard_met_percentage`: Percentage of external, high volume service standards that met their target. `total_standards_met_ext_hv / total_standards_ext_hv`

#### `dp_services_rank.csv`
Table that supports the creation of the "Data Pack". Generated by `src/process.py/datapack`. This table displays the top 20 services by application volume for each fiscal year, along with service-level data to support the creation of specific visualizations. Each record (row) represents one service for one fiscal year. Only includes services with `service_scope` containing `EXTERN` or `ENTERPRISE`.

A handful of services are excluded from consideration due to being outliers, inconsistently reported, or for alignment with previous years reporting:
| Service ID  | Service Name (en) | Department / Agency|
| ------------- | ------------- |-------------|
|`669`|Traveller Processing|CRA|
|`1108`|Tax Credit Application|CRA|
|`1111`| Provincial and territorial tax credit payments| CRA |
|`1112`|Provincial and territorial child benefit program payments|CRA|
|`1677`|The Canadian Astronomy Data Centre (CADC)|CNRC|
|`3728`| Canada Carbon Rebate|CRA|


- `fy_org_id_service_id`: Constructed unique key. `fiscal_yr` (underscore) `org_id` (underscore) `service_id`.
- `fiscal_yr`: Federal government fiscal year, April 1, XXXX, to March 31, YYYY, in format XXXX-YYYY.
- `service_name_en`: Name of the service in English, as defined by reporting department.
- `service_name_fr`: Name of the service in French, as defined by reporting department.
- `online_enabled_Y`: Number of interaction points that are available online. Determined by counting how many interaction points are listed as `Y` for this service.
- `online_enabled_N`: Number of interaction points that are applicable to the service but are not yet online. Determined by counting how many interaction points are listed as `N` for this service.
- `online_enabled_NA`: Number of interaction points that are not applicable to the service. Determined by counting how many interaction points are listed as `NA` for this service.
- `num_applications_total`: Total number of applications reported for this service in the listed fiscal year, regardless of channel. Note that this **does not** include telephone enquiries.
- `num_applications_by_phone`: Total number of applications received by telephone and reported for this service in the listed fiscal year. Note that this **does not** include telephone enquiries.
- `num_applications_online`: Total number of applications received via an internet-based application or website and reported for this service in the listed fiscal year.
- `num_applications_by_mail`: Total number of applications received via postal mail and reported for this service in the listed fiscal year.
- `num_applications_by_email`: Total number of applications received via email and reported for this service in the listed fiscal year.
- `num_applications_by_fax`: Total number of applications received via fax and reported for this service in the listed fiscal year.
- `num_applications_by_other`: Total number of applications received where the channel could not be determined and reported for this service in the listed fiscal year.
- `num_applications_rank`: Rank of service in listed fiscal year according to `num_applications_total`, in descending order (rank 1 = highest value)

#### `drr_all.csv`
Table that supports the Departmental Results Report (DRR) and the Performance Information Profile (PIP) for Treasury Board of Canada Secretariat. Generated by `src/process.py/drr`. Each record (row) is a fiscal year, with columns indicating the relevant numerator, denominator, and result for each indicator. Only includes external services (`service_scope` containing `EXTERN`).

- `fiscal_yr`: Federal government fiscal year, April 1, XXXX, to March 31, YYYY, in format XXXX-YYYY.
- `hv_online_e2e_count`: Number of distinct high-volume external services in the service inventory that are online end-to-end, which means all applicable interaction points are online and there is at least one interaction point online. High volume services are those with total applications from all channels greater than or equal to 45,000 in a year, not including telephone enquiries. Numerator for `dr2467_pip9_score`.
- `hv_service_count`: Number of distinct high-volume external services in the service inventory. High volume services are those with total applications from all channels greater than or equal to 45,000 in a year, not including telephone enquiries. Denominator for `dr2467_pip9_score`.
- `dr2467_pip9_score`: percentage of high-volume external services (>=45k applications) that are delivered online end-to-end.
- `hvte_services_count_meeting_standard`: Number of distinct high-volume (with telephone enquiries) external services in the service inventory that have met at least one service standard. High volume services are those with total applications from all channels, including telephone enquiries, greater than or equal to 45,000 in a year. Numerator for `dr2468_pip10_score`.
- `hvte_services_count`: Number of distinct high-volume (with telephone enquiries) external services in the service inventory. High volume services are those with total applications from all channels, including telephone enquiries, greater than or equal to 45,000 in a year. Denominator for `dr2468_pip10_score`.
- `dr_2468_pip10_score`: percentage of high-volume external services (>=45k applications and telephone enquiries) that met at least one service standard.
- `hv_online_applications`: Total volume of applications submitted through the online channel for high volume external services. High volume services are those with total applications from all channels greater than or equal to 45,000 in a year, not including telephone enquiries. Numerator for `dr_2469_pip12_score`.
- `hv_total_applications`: Total volume of applications submitted through all channels for high volume external services. High volume services are those with total applications from all channels greater than or equal to 45,000 in a year, not including telephone enquiries. Denominator for `dr_2469_pip12_score`.
- `dr_2469_pip12_score`: percentage of applications for high-volume external services (>45k applications) that used the online channel
- `services_with_feedback_count`: Number of distinct external services that collect user feedback in the service inventory. Determined by excluding all the services that only report `NON` in the field `client_feedback_channel`. Numerator for `pip18_score`.
- `service_count`: Number of distinct external services in the service inventory. Counted using a constructed unique key `fy_org_id_service_id`, which is `fiscal_yr` (underscore) `org_id` (underscore) `service_id`. Denominator for `pip18_score`.
- `pip18_score`: percentage of external services that have indicated something other than 'NON' in the client feedback channel field.

#### `ib_all.csv`
Table that supports the verification of GC Infobase figures and charts at the departmental level based on the service inventory. Generated by `src/process.py/infobase`. Each record (row) lists values for a combination of fiscal year and organization (department/agency), with columns indicating the relevant values to verify and their underlying numerators and denominators if relevant. Only includes external and internal enterprise services (`service_scope` containing `EXTERN` or `ENTERPRISE`).

- `fiscal_yr`: Federal government fiscal year, April 1, XXXX, to March 31, YYYY, in format XXXX-YYYY.
- `org_id`: Unique numeric identifier for departments, agencies, and any other federal organization. Based on the "Inventory of Federal Organizations and Interests" which supports GC Infobase.
- `department_en`: Name of department or agency in English. Defaults to the "Applied title" when it is available, and "Legal title" when it is not. Based on the "Inventory of Federal Organizations and Interests" which supports GC Infobase.
- `department_fr`: Name of department or agency in French. Defaults to the "Applied title" when it is available, and "Legal title" when it is not. Based on the "Inventory of Federal Organizations and Interests" which supports GC Infobase.
- `online_e2e_count`: Number of distinct services in the service inventory that are online end-to-end, which means all applicable interaction points are online and there is at least one interaction point online. Numerator for `online_e2e_pc`.
- `service_count`: Number of distinct services in the service inventory. Counted using a constructed unique key `fy_org_id_service_id`, which is `fiscal_yr` (underscore) `org_id` (underscore) `service_id`. Denominator for `online_e2e_pc`.
- `online_e2e_pc`: Percentage of services that are online end-to-end.
- `num_applications_online`: Total number of applications received via an internet-based application or website.
- `num_applications_by_phone`: Total number of applications received by telephone. **Does not** include telephone enquiries.
- `num_applications_by_mail`: Total number of applications received via postal mail.
- `num_applications_in_person`: Total number of applications received via an in-person interaction at a federal government service center.
- `num_applications_by_other_fax_and_email`: Total number of applications received where the channel could not be determined, or by fax or email.
- `service_with_std_count`: Number of distinct services in the service inventory that have at least one service standard. The service standards do not have to have a well defined results, i.e. `target_met` can be `Y`, `N`, or `NA`. Numerator for `services_with_standards_percentage`.
- `service_count`: Number of distinct services in the service inventory. Counted using a constructed unique key `fy_org_id_service_id`, which is `fiscal_yr` (underscore) `org_id` (underscore) `service_id`. Denominator for `services_with_standards_percentage`.
- `services_with_standards_percentage`: Percentage of distinct services in the service inventory that have at least one service standard.
- `service_standard_met`: Number of distinct service standards that met their target (`target_met = Y`) in the service inventory. Numerator for `standards_met_percentage`.
- `service_standard_count`: Number of distinct well-defined service standards in the service inventory. Well-defined implies the result of the standard is not `NA`, i.e. `target_met` is either `Y` or `N`. Counted using a constructed unique key `fy_org_id_service_id_std_id`, which is `fiscal_yr` (underscore) `org_id` (underscore) `service_id` (underscore) `service_standard_id`. Denominator for `standards_met_percentage`.
- `standards_met_percentage`: Percentage of well defined service standards that met their target.

#### `maf_all.csv`
Table that supports the generation of long-standing useful indicators relating to the service inventory, formerly used for the Management Accountability Framework (MAF). Generated by `src/process.py/maf`. Each record (row) lists values for a combination of fiscal year and organization (department/agency), with columns indicating the relevant indicators their underlying numerators and denominators. Only includes external and internal enterprise services (`service_scope` containing `EXTERN` or `ENTERPRISE`).

- `fiscal_yr`: Federal government fiscal year, April 1, XXXX, to March 31, YYYY, in format XXXX-YYYY.
- `org_id`: Unique numeric identifier for departments, agencies, and any other federal organization. Based on the "Inventory of Federal Organizations and Interests" which supports GC Infobase.
- `department_en`: Name of department or agency in English. Defaults to the "Applied title" when it is available, and "Legal title" when it is not. Based on the "Inventory of Federal Organizations and Interests" which supports GC Infobase.
- `department_fr`: Name of department or agency in French. Defaults to the "Applied title" when it is available, and "Legal title" when it is not. Based on the "Inventory of Federal Organizations and Interests" which supports GC Infobase.
- `service_with_std_count`: Number of distinct services in the service inventory that have at least one service standard. The service standards do not have to have a well defined results, i.e. `target_met` can be `Y`, `N`, or `NA`. Numerator for `maf1_score`.
- `service_count_maf1`: Number of distinct services in the service inventory. Counted using a constructed unique key `fy_org_id_service_id`, which is `fiscal_yr` (underscore) `org_id` (underscore) `service_id`. Denominator for `maf1_score`.
- `maf1_score`: Percentage of distinct services in the service inventory that have at least one service standard. Answers the MAF question "As service standards are required under the Policy on Service and Digital, what is the percentage of services that have service standards?"
- `service_standard_met`: Number of distinct service standards that met their target (`target_met = Y`) in the service inventory. Numerator for `maf2_score`.
- `service_standard_count`: Number of distinct well-defined service standards in the service inventory. Well-defined implies the result of the standard is not `NA`, i.e. `target_met` is either `Y` or `N`. Counted using a constructed unique key `fy_org_id_service_id_std_id`, which is `fiscal_yr` (underscore) `org_id` (underscore) `service_id` (underscore) `service_standard_id`. Denominator for `maf2_score`.
- `maf2_score`: Percentage of well defined service standards that met their target. Answers the MAF question "What is the percentage of service standards that met their target?"
- `online_e2e_count`: Number of distinct services in the service inventory that are online end-to-end, which means all applicable interaction points are online and there is at least one interaction point online. Numerator for `maf5_score`
- `service_count_maf5`: Number of distinct services in the service inventory. Counted using a constructed unique key `fy_org_id_service_id`, which is `fiscal_yr` (underscore) `org_id` (underscore) `service_id`. Denominator for `maf5_score`.
- `maf5_score`: Percentage of applicable services that can be completed online end-to-end. Answers the MAF question "As online end-to-end availability of services is required under the Policy on Service and Digital, what is the percentage of applicable services that can be completed online end-to-end?"
- `activated_point_count`: Number of interaction points that are available online. Determined by counting how many interaction points are listed as `Y`. Numerator for `maf6_score`.
- `point_count`: Number of applicable interaction points. Determined by counting how many interaction points are either `Y` or `N`, i.e. excluding all `NA`. There is a maximum of 6 interaction points per service. Denominator for `maf6_score`.         
- `maf6_score`: percentage of client interaction points that are available online. Answers the MAF question "As online end-to-end availability of services is required under the Policy on Service and Digital, what is the percentage of client interaction points that are available online for services?"
- `improved_services_count`: Number of distinct services in the service inventory for which the `last_service_improvement` year occurs within either the reporting year, or the year prior. For example, if a service reported in 2024-25 listed "2023-24" in the `last_service_improvement` field, it counts as part of this metric. Numerator for `maf8_score`.
- `service_count_maf8`: Number of distinct services in the service inventory. Counted using a constructed unique key `fy_org_id_service_id`, which is `fiscal_yr` (underscore) `org_id` (underscore) `service_id`. Denominator for `maf8_score`.
- `maf8_score`: percentage of services which have used client feedback to improve services in the year prior to reporting. Answers the MAF question "As ensuring client feedback is used to inform continuous improvement of services is a requirement under the Directive on Service and Digital, what is the percentage of services which have used client feedback to improve services in the last year?"

#### `oecd_digital_gov_survey.csv`
Table that supports the generation of figures to respond to the OECD Digital Government Survey. Answers the question "What is the percentage of services in the catalogue/register that can be accessed through the following channels? (In person, web browser, app, phone). Generated by `src/process.py/oecd_digital_gov_survey`. Each record (row) lists values for a combination of fiscal year and organization (department/agency), with columns indicating the relevant indicators. Only includes external, client-based services (`service_scope` containing `EXTERN` and `service_recipient_type` = `CLIENT`).

- `fiscal_yr`: Federal government fiscal year, April 1, XXXX, to March 31, YYYY, in format XXXX-YYYY.
- `org_id`: Unique numeric identifier for departments, agencies, and any other federal organization. Based on the "Inventory of Federal Organizations and Interests" which supports GC Infobase.
- `department_en`: Name of department or agency in English. Defaults to the "Applied title" when it is available, and "Legal title" when it is not. Based on the "Inventory of Federal Organizations and Interests" which supports GC Infobase.
- `department_fr`: Name of department or agency in French. Defaults to the "Applied title" when it is available, and "Legal title" when it is not. Based on the "Inventory of Federal Organizations and Interests" which supports GC Infobase.
- `total_services`: Number of distinct services in the service inventory. Counted using a constructed unique key `fy_org_id_service_id`, which is `fiscal_yr` (underscore) `org_id` (underscore) `service_id`.
- `applications_in_person`: Number of distinct services in the service inventory that report a value greater than 0 in the `num_applications_in_person` field. Also excludes any result of `NA`, `ND`, or blank values.
- `applications_by_phone`: Number of distinct services in the service inventory that report a value greater than 0 in the `num_applications_by_phone` field. Also excludes any result of `NA`, `ND`, or blank values.
- `applications_online`: Number of distinct services in the service inventory that report a value greater than 0 in the `num_applications_online` field. Also excludes any result of `NA`, `ND`, or blank values.

#### `service_fte_spending.csv`
Table that shows actual and planned full-time equivalent positions (FTEs) and expenditures (spending) for all programs that deliver a service, using reported values in the DRR and DP. Connection between service and program determined by service inventory. Generated by `src/process.py/service_fte_spending`. Each record (row) lists the spending or ftes for programs reported by service in the service inventory. If the combination of fiscal year, organization, and program ID does not have any values associated in the DRR/DP, it is listed as `valid_program`=`False` and has no values for spending or fte. This table makes extensive use of the associated table `drf.csv`

- `service_id`: Identification number for a service in the service inventory.
- `fiscal_yr`: Federal government fiscal year, April 1, XXXX, to March 31, YYYY, in format XXXX-YYYY. In this case represents the fiscal year of the association between service and program.
- `program_id`: Alpha-numeric code that is uniquely tied to a program in the Chart of Accounts, and is used in DRR and DP reporting.
- `org_id`: Unique numeric identifier for departments, agencies, and any other federal organization. Based on the "Inventory of Federal Organizations and Interests" which supports GC Infobase.
- `latest_si_yr`: Latest fiscal year for which the organization has reported a service inventory.
- `report_yr`: Report year for the DRR or DP from which the spending and FTE figures are displayed.
- `measure_yr`: Year of the measure in question - ensures only actuals are reported for previous years and planned amounts are reported for the current and future years.
- `planned_actual`: Describes whether the spending on FTE value is actual or is planned.
- `spending_fte`: Indicates whether the measure described is spending (i.e. expenditures, not costs incurred) or number of FTEs
- `measure`: The amount or value in question.
- `valid_program`: Indicates True or False depending on if the program ID appears in that organization's Chart of Accounts for that fiscal year. Records indicating `False` exist because there is no strict control mechanism in the service inventory reporting process around which programs can be reported as delivering a service.

#### `si_oip.csv`
Table of online interaction points activation status by service. Generated by `src/process.py/summary_si_ss`. Each record (row) lists the activation status for each interaction point and service. Only includes external and internal enterprise services (`service_scope` containing `EXTERN` or `ENTERPRISE`).

- `fiscal_yr`: Federal government fiscal year, April 1, XXXX, to March 31, YYYY, in format XXXX-YYYY. 
- `org_id`: Unique numeric identifier for departments, agencies, and any other federal organization. Based on the "Inventory of Federal Organizations and Interests" which supports GC Infobase.
- `service_id`: Identification number for a service in the service inventory.
- `fy_org_id_service_id`: a constructed unique key which is `fiscal_yr` (underscore) `org_id` (underscore) `service_id`.
- `online_interaction_point`: the interaction point for the record in question.
- `activation`: the status of the interaction point's online activation. `Y` indicates "yes the interaction point is online", `N` indicates "no, the interaction point is not online, but it is applicable", and `NA` indicates "the interaction point does not apply to this service."
- `online_interaction_point_sort`: serves to help sort the online interaction points in a logical / chronological order.

#### `si_reviews.csv`
Table describing the count of services reviewed or improved in the past 5 years. Generated by `src/process.py/summary_si_ss`. Each record (row) lists the number of services that were reviewed or improved in the preceding 5 years by fiscal year and organization. Only includes external and internal enterprise services (`service_scope` containing `EXTERN` or `ENTERPRISE`).
- `fiscal_yr`: Federal government fiscal year, April 1, XXXX, to March 31, YYYY, in format XXXX-YYYY. 
- `org_id`: Unique numeric identifier for departments, agencies, and any other federal organization. Based on the "Inventory of Federal Organizations and Interests" which supports GC Infobase.
- `total_services`: Number of distinct services in the service inventory. Counted using a constructed unique key `fy_org_id_service_id`, which is `fiscal_yr` (underscore) `org_id` (underscore) `service_id`.
- `services_reviewed_in_past_5_yrs`: Number of distinct services in the service inventory for which the `last_service_review` year occurs within either the reporting year, or up to 5 years prior. For example, if a service reported in 2024-25 listed "2020-21" in the `last_service_review` field, it counts as part of this metric.
- `services_improved_in_past_5_yrs`: Number of distinct services in the service inventory for which the `last_service_improvement` year occurs within either the reporting year, or up to 5 years prior. For example, if a service reported in 2024-25 listed "2020-21" in the `last_service_improvement` field, it counts as part of this metric.

#### `si_vol.csv`
Table describing the volume of applications by service and channel. Excludes telephone enquiries and website visits. Generated by `src/process.py/summary_si_ss`. Each record (row) lists the number of applications that were reported by fiscal year, organization, service, and channel. Only includes external and internal enterprise services (`service_scope` containing `EXTERN` or `ENTERPRISE`).
- `fiscal_yr`: Federal government fiscal year, April 1, XXXX, to March 31, YYYY, in format XXXX-YYYY. 
- `org_id`: Unique numeric identifier for departments, agencies, and any other federal organization. Based on the "Inventory of Federal Organizations and Interests" which supports GC Infobase.
- `service_id`: Identification number for a service in the service inventory.
- `channel`: Channel through which the applications were received.
- `volume`: Volume of applications for the fiscal year, organization, service, and channel in question.

#### `ss_tml_perf_vol.csv`
Table describing the performance of timeliness service standards by service and channel. Generated by `src/process.py/summary_si_ss`. Each record (row) lists the volume meeting target, the total volume, and the volume not meeting target for all timeliness service standards associated to services, by channel. Only includes external and internal enterprise services (`service_scope` containing `EXTERN` or `ENTERPRISE`).
- `fiscal_yr`: Federal government fiscal year, April 1, XXXX, to March 31, YYYY, in format XXXX-YYYY. 
- `org_id`: Unique numeric identifier for departments, agencies, and any other federal organization. Based on the "Inventory of Federal Organizations and Interests" which supports GC Infobase.
- `service_id`: Identification number for a service in the service inventory.
- `channel`: Channel for which the the service standard measures performance.
- `volume_meeting_target`: Total volume of interactions that met the service standard target for all timeliness service standards by service and channel.
- `total_volume`: Total volume of interactions for all timeliness service standards by service and channel.
- `volume_not_meeting_target`: Total volume of interactions that did not meet the service standard target for all timeliness service standards by service and channel. Calculated as the difference between the `total_volume` and the `volume_meeting_target`.

### Quality Assurance Review Files (outputs/qa/)
- All `service_scope` included, not just `EXTERN` or `ENTERPRISE`.
- Fields beginning with `qa` are boolean values (True or False) indicating whether there is an issue. 
- See the file [src/qa_issues_descriptions.csv](https://github.com/gcperformance/service-data/blob/master/src/qa_issues_descriptions.csv) for more details on the QA issues being identified

#### `si_qa.csv`
Full service inventory dataset with QA issues identified as separate columns. Generated by `src/qa.py/qa_check`. All the fields from the service inventory dataset are identical to `si.csv` and are described earlier in this file.

- `service_id_numeric`: The numeric portion of the service ID number. This is no longer in use for any QA checks.
- `org_id_sid_registry`: Returns the org_id associated to the service according to the [service ID registry](https://github.com/gcperformance/utilities/blob/master/goc-service-id-registry.csv). Unique numeric identifier for departments, agencies, and any other federal organization. Based on the "Inventory of Federal Organizations and Interests" which supports GC Infobase.
- `department_en_sid_registry`: Name of department or agency in English from the [service ID registry](https://github.com/gcperformance/utilities/blob/master/goc-service-id-registry.csv). Defaults to the "Applied title" when it is available, and "Legal title" when it is not. Based on the "Inventory of Federal Organizations and Interests" which supports GC Infobase.
- `department_fr_sid_registry`: Name of department or agency in French from the [service ID registry](https://github.com/gcperformance/utilities/blob/master/goc-service-id-registry.csv). Defaults to the "Applied title" when it is available, and "Legal title" when it is not. Based on the "Inventory of Federal Organizations and Interests" which supports GC Infobase.
- `qa_unregistered_sid`: Boolean value (True or False) indicating whether `service_id` is absent from the [service ID registry](https://github.com/gcperformance/utilities/blob/master/goc-service-id-registry.csv)
- `qa_reused_sid`: Boolean value (True or False) indicating whether the organization reporting the service is the different from the one registered to the service in the [service ID registry](https://github.com/gcperformance/utilities/blob/master/goc-service-id-registry.csv). Compares `org_id` reported for the service to `org_id_sid_registry` from the registry.
- `reused_sid_correct_org`: If `qa_reused_sid` is true, then lists the organization that registered the service id in the registry. Concatenated field `org_id_sid_registry` (colon) `department_en_sid_registry` (pipe) `department_fr_sid_registry`
- `fiscal_yr_end_date`: The first day of the fiscal year (April 1) following the fiscal year being reported.
- `qa_si_fiscal_yr_out_of_scope`: Boolean value (True or False) indicating whether the current date is before `fiscal_yr_end_date`. If so, the fiscal year being reported is in the future or incomplete.
- `qa_client_feedback_contradiction`: Boolean value (True or False) indicating whether there is a contradiction between the `client_feedback_channel` and the `os_issue_resolution_feedback` fields.
- `total_volume_ss`: Total volume for all associated service standards.
- `qa_ss_vol_without_si_vol`: Boolean value (True or False) indicating whether there are service interactions being reported in the service standard and performance dataset (`ss.csv`), but are missing from the service inventory dataset.
- `qa_no_si_app_volume`: Boolean value (True or False) indicating whether application volumes are missing from the service inventory.
- `qa_use_of_cra_bn_applicable`: Boolean value (True or False) indicating whether there is a contradiction between the `cra_bn_identifier_usage` and `client_target_groups` fields.
- `program_id_latest_valid_fy`: Latest valid fiscal year for the program.
- `qa_program_id_old`: Boolean value (True or False) indicating whether the program being reported is no longer valid.
- `mismatched_program_ids`: Concatenated result of all the program IDs that do not belong to the reporting organization.
- `qa_program_id_wrong_org`: Boolean value (True or False) indicating whether the program being reported belongs to a different organization.

#### `ss_qa.csv`
Full service inventory dataset with QA issues identified as separate columns. Generated by `src/qa.py/qa_check`. All the fields from the service inventory dataset are identical to `ss.csv` and are described earlier in this file.

- `service_standard_id_numeric`: The numeric portion of the service standard ID number. This is no longer in use for any QA checks.
- `fiscal_yr_end_date`: The first day of the fiscal year (April 1) following the fiscal year being reported.
- `qa_ss_fiscal_yr_out_of_scope`: Boolean value (True or False) indicating whether the current date is before `fiscal_yr_end_date`. If so, the fiscal year being reported is in the future or incomplete.
- `qa_no_ss_volume`: Boolean value (True or False) indicating whether interaction volumes are missing from the service standard record.
- `qa_performance_over_100`: Boolean value (True or False) indicating whether there is more `volume_meeting_target` than `total_volume`


#### `si_qa_report.csv`
Table of QA issues identified in the service inventory. Generated by `src/qa.py/qa_report`. Each record (row) represents one QA issue.

- `department_en`: Name of department or agency in English. Defaults to the "Applied title" when it is available, and "Legal title" when it is not. Based on the "Inventory of Federal Organizations and Interests" which supports GC Infobase.
- `department_fr`: Name of department or agency in French. Defaults to the "Applied title" when it is available, and "Legal title" when it is not. Based on the "Inventory of Federal Organizations and Interests" which supports GC Infobase.
- `org_id`: Unique numeric identifier for departments, agencies, and any other federal organization. Based on the "Inventory of Federal Organizations and Interests" which supports GC Infobase.
- `fiscal_yr`: Federal government fiscal year, April 1, XXXX, to March 31, YYYY, in format XXXX-YYYY. Indicates the time period for which the data was reported.
- `service_id`: Identification number for a service in the service inventory
- `service_name_en`: Service name in English
- `service_name_fr`: Service name in French
- `issue`: Short code to identify the issue, identical to the columns in `si_qa.csv` that begin with `qa`
- `severity_en`: Severity of the issue, in English
- `description_en`: Description of the issue, in English
- `action_en`: Proposed action that would resolve the issue, in English
- `severity_fr`: Severity of the issue, in French
- `description_fr`: Description of the issue, in French
- `action_fr`: Proposed action that would resolve the issue, in French
- `context`: Additional information to help resolve the issue

#### `ss_qa_report.csv`
Table of QA issues identified in the service standards dataset. Generated by `src/qa.py/qa_report`. Each record (row) represents one QA issue.

- `department_en`: Name of department or agency in English. Defaults to the "Applied title" when it is available, and "Legal title" when it is not. Based on the "Inventory of Federal Organizations and Interests" which supports GC Infobase.
- `department_fr`: Name of department or agency in French. Defaults to the "Applied title" when it is available, and "Legal title" when it is not. Based on the "Inventory of Federal Organizations and Interests" which supports GC Infobase.
- `org_id`: Unique numeric identifier for departments, agencies, and any other federal organization. Based on the "Inventory of Federal Organizations and Interests" which supports GC Infobase.
- `fiscal_yr`: Federal government fiscal year, April 1, XXXX, to March 31, YYYY, in format XXXX-YYYY. Indicates the time period for which the data was reported.
- `service_id`: Identification number for a service in the service inventory
- `service_name_en`: Service name in English
- `service_name_fr`: Service name in French
- `service_standard_id`: Identification number for a service standard in the service inventory
- `service_standard_en`: Service standard name in English
- `service_standard_fr`: Service standard name in French
- `volume_meeting_target`: Identifies the number of final outputs issued appropriate to the service (eg. payments issued, requests completed, etc) during the fiscal year that met a particular service standard target for a service. Blank indicates no information available, while 0 indicates that no final outputs issued met service standard targets.
- `total_volume`: Identifies the total number of final outputs issued appropriate to the service (eg. payments issued, requests completed, etc) during the fiscal year. Blank indicates no information available, while 0 indicates no final outputs issued.
- `performance`: Identifies the result achieved for this service standard. This is the "Business Volume That Met Service Standard Target" divided by the "Total Volume" and is automatically calculated for the 2024+ dataset.
- `issue`: Short code to identify the issue, identical to the columns in `ss_qa.csv` that begin with `qa`
- `severity_en`: Severity of the issue, in English
- `description_en`: Description of the issue, in English
- `action_en`: Proposed action that would resolve the issue, in English
- `severity_fr`: Severity of the issue, in French
- `description_fr`: Description of the issue, in French
- `action_fr`: Proposed action that would resolve the issue, in French

### Utilities and Supporting Files (outputs/utils/)
#### `dd_choices.csv`
Correspondence table between codes that appear in `ss` and `si` and their English and French names, "dd" referring to data dictionary. Generated by `src/utils.py/build_data_dictionary`. Defined based on the .json version of the 2024+ service inventory datasets.

- `resource_name`: The table in which the field is found
- `id`: The column / field name
- `code`: The code as listed in the resource
- `en`: The longer English description of the code
- `fr`: The longer French description of the code

#### `dd_field_names.csv`
A list of translated field names and metadata for `si` (`resource_name`=`service`) and `ss` (`resource_name`=`service_std`). Generated by `src/utils.py/build_data_dictionary`. Defined based on the .json version of the 2024+ service inventory datasets. Each record (row) represents a field.

- `resource_name`: The table in which the field is found.
- `title_en`: The full English name of the table in which the field is found.
- `title_fr`: The full French name of the table in which the field is found.
- `id`: The column / field name.
- `datastore_type`: The data type for the allowed values in the field.
- `obligation_en`: Whether the field is mandatory or optional, in English.
- `obligation_fr`: Whether the field is mandatory or optional, in French.
- `label_en`: The full English name of the column / field.
- `label_fr`: The full French name of the column / field.
- `description_en`: A description of the field in English.
- `description_fr`: A description of the field in French.
- `validation_en`: Basic requirements for the field in English.
- `validation_fr`: Basic requirements for the field in French.
- `character_limit`: Maximum number of characters for text-based fields.

#### `dd_program`
List of valid program codes and names as described in the data dictionary. Follows the same structure as `dd_choices.csv`. Generated by `src/utils.py/build_data_dictionary`. For more detailed information on valid programs, refer to `program_list.csv`

#### `dept.csv`
A tidy unique list of departments with their IFOI IDs. Generated by `src/utils.py/dept_list`.

- `org_id`: Unique numeric identifier for departments, agencies, and any other federal organization. Based on the "Inventory of Federal Organizations and Interests" which supports GC Infobase.
- `department_en`: Name of department or agency in English. Defaults to the "Applied title" when it is available, and "Legal title" when it is not. Based on the "Inventory of Federal Organizations and Interests" which supports GC Infobase.
- `department_fr`: Name of department or agency in French. Defaults to the "Applied title" when it is available, and "Legal title" when it is not. Based on the "Inventory of Federal Organizations and Interests" which supports GC Infobase.

#### `drf.csv`
A flattened Departmental plans and Departmental results report. Generated by `src/utils.py/build_drf`. This table is directly referenced by `service_fte_spending.csv`

- `org_id`: Unique numeric identifier for departments, agencies, and any other federal organization. Based on the "Inventory of Federal Organizations and Interests" which supports GC Infobase.
- `latest_si_yr`: Latest fiscal year for which the organization has reported a service inventory.
- `program_id`: Alpha-numeric code that is uniquely tied to a program in the Chart of Accounts, and is used in DRR and DP reporting.
- `report_yr`: Report year (fiscal year) for the DRR or DP from which the spending and FTE figures are displayed.
- `measure_yr`: Fiscal year of the measure in question - ensures only actuals are reported for previous years and planned amounts are reported for the current and future years.
- `planned_actual`: Describes whether the spending on FTE value is actual or is planned.
- `spending_fte`: Indicates whether the measure described is spending (i.e. expenditures, not costs incurred) or number of FTEs
- `measure`: The amount or value in question.
- `si_link_yr`: Fiscal year used for the association between service and program. Either `measure_yr` or `latest_si_yr` depending on which is earlier, defaulting to `measure_yr` if they are the same.

#### `ifoi.csv`
Exhaustive list of departmental info from the Inventory of Federal Organizations and Interests in English and French. For more detail, see [GC InfoBase - Open Datasets - Inventory of Federal Organizations and Interests - English](https://open.canada.ca/data/en/dataset/a35cf382-690c-4221-a971-cf0fd189a46f/resource/7c131a87-7784-4208-8e5c-043451240d95) and [Répertoire des organisations et intérêts fédéraux - Français](https://ouvert.canada.ca/data/fr/dataset/a35cf382-690c-4221-a971-cf0fd189a46f/resource/45069fe9-abe3-437f-97dd-3f64958bfa85). Generated by `src/utils.py/build_ifoi`.

#### `org_var.csv` 
Duplicate-permitted list of variant department names and their IFOI ID. Retrieved from [gc-org-variants](https://github.com/gcperformance/utilities/blob/master/goc-org-variants.csv). Built to associate and assign a common standard ID number to all variations of federal organizations that might be found in other datasets.

#### `program_list.csv`
List of unique programs and their ID codes, defined by organization, along with the latest valid fiscal year. This is a combination of all the tables from the [Program codes list as per the Government-wide Chart of Accounts](https://open.canada.ca/data/en/dataset/3c371e57-d487-49fa-bb0d-352ae8dd6e4e). Generated by `src/utils.py/program_list`.

- `org_id`: Unique numeric identifier for departments, agencies, and any other federal organization. Based on the "Inventory of Federal Organizations and Interests" which supports GC Infobase.
- `program_id`: Alpha-numeric code that is uniquely tied to a program in the Chart of Accounts, and is used in DRR and DP reporting.
- `latest_valid_fy`: Latest fiscal year for which the combination of program ID and organization is valid 
- `program_name_en`: English name of the program as per the Chart of Accounts.
- `program_name_fr`: French name of the program as per the Chart of Accounts.

#### `sid_list.csv`
Unique list of service IDs with latest reporting year and department. Generated by `src/utils.py/sid_list`.

- `service_id`: Identification number for a service in the service inventory
- `service_name_en`: Service name in English
- `service_name_fr`: Service name in French
- `department_en`: Name of department or agency in English. Defaults to the "Applied title" when it is available, and "Legal title" when it is not. Based on the "Inventory of Federal Organizations and Interests" which supports GC Infobase.
- `department_fr`: Name of department or agency in French. Defaults to the "Applied title" when it is available, and "Legal title" when it is not. Based on the "Inventory of Federal Organizations and Interests" which supports GC Infobase.
- `org_id`: Unique numeric identifier for departments, agencies, and any other federal organization. Based on the "Inventory of Federal Organizations and Interests" which supports GC Infobase.
- `fiscal_yr_first`: First fiscal year the service was reported
- `fiscal_yr_latest`: Latest fiscal year the service was reported
- `service_scope_ext_or_ent`: Calculated field that indicates whether the service is external or internal enterprise to assist in quick filtering of relevant services. Refers to reported value from latest fiscal year

#### `si_all.csv`
Full service inventory merging 2018–2023 datasets with the 2024 dataset. All `service_scope` included, not just `EXTERN` and `ENTERPRISE`. See list of fields for `si.csv`. Generated by `src/merge.py/merge_si`.

#### `ss_all.csv`
Full service standard dataset merging 2018–2023 datasets with the 2024 dataset. All `service_scope` included, not just `EXTERN` and `ENTERPRISE`. See list of fields for `ss.csv`. Generated by `src/merge.py/merge_ss`.