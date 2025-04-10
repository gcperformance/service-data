import pandas as pd
import numpy as np

from src.clean import clean_percentage, split_and_uppercase_to_sorted_string
from src.load import load_csv
from src.export import export_to_csv
from src.utils import dept_list

# UTILS_DIR = Path(__file__).parent.parent / "outputs" / "utils"

def merge_si(config):
    """Combining service inventory data from previous (2018) and current (2024) format"""
    
    # Load org variant list and program-service correspondence table
    org_var = load_csv('org_var.csv', config, snapshot=False)
    serv_prog = load_csv('serv_prog.csv', config, snapshot=False)
    
    # Load department list from utils
    dept = dept_list(config)
    
    si_2018 = load_csv('si_2018.csv', config, snapshot=True)
    si_2024 = load_csv('si_2024.csv', config, snapshot=True)
    
    # Test breaker - uncomment to break merge_si() and check the row count test
    # si_2024 = si_2024.head()
    
    # Compare columns
    # si_2018_columns = set(si_2018.columns)
    # si_2024_columns = set(si_2024.columns)
    # print('Columns only in 2018:', si_2018_columns-si_2024_columns)
    # print('Columns only in 2024:', si_2024_columns-si_2018_columns)
    
    #Rename columns in 2018 dataset to align to the 2024 dataset's conventions
    rename_2018_si_columns = {
        'client_feedback':'client_feedback_channel',
        'e_registration':'os_account_registration',
        'e_authentication':'os_authentication',
        'e_application':'os_application',
        'e_decision':'os_decision',
        'e_issuance':'os_issuance',
        'e_feedback':'os_issue_resolution_feedback',
        'online_comments_en':'os_comments_client_interaction_en',
        'online_comments_fr':'os_comments_client_interaction_fr',
        'last_year_of_service_review':'last_service_review',
        'last_year_of_service_improvement_based_on_client_feedback':'last_service_improvement',
        'use_of_CRA_number':'sin_usage',
        'use_of_SIN_number':'cra_bn_identifier_usage',
        'calls_received':'num_phone_enquiries',
        'telephone_applications':'num_applications_by_phone',
        'web_visits':'num_website_visits',
        'online_applications':'num_applications_online',
        'in_person_applications':'num_applications_in_person',
        'postal_mail_applications':'num_applications_by_mail',
        'email_applications':'num_applications_by_email',
        'fax_applications':'num_applications_by_fax',
        'other_applications':'num_applications_by_other',
        'total_applications':'num_applications_total',
        'service_url_en':'service_uri_en',
        'service_url_fr':'service_uri_fr'
    }
    
    si_2018.rename(columns=rename_2018_si_columns, inplace=True)
    
    si_2018_columns = set(si_2018.columns)
    si_2024_columns = set(si_2024.columns)
    
    
    # Add org_id to both datasets
    si_2018_tidy = pd.merge(si_2018, org_var, left_on='department_name_en', right_on='org_name_variant')
    si_2024_tidy = pd.merge(si_2024, org_var, left_on='owner_org', right_on='org_name_variant')
    
    # Drop specific org name fields from both
    si_2018_tidy = si_2018_tidy.drop(columns=['department_name_en', 'department_name_fr'])
    si_2024_tidy = si_2024_tidy.drop(columns=['owner_org', 'owner_org_title'])

    # Treat org_id as a string
    si_2018_tidy['org_id'] = si_2018_tidy['org_id'].astype(str)
    si_2024_tidy['org_id'] = si_2024_tidy['org_id'].astype(str)
    
    # Merge in en/fr department names from dept table
    si_2018_tidy = pd.merge(
        si_2018_tidy,
        dept,
        on='org_id',
        how='left'
    )
    
    si_2024_tidy = pd.merge(
        si_2024_tidy,
        dept,
        on='org_id',
        how='left'
    )
    
    # Add program_id to 2018 dataset
    # Collapse all the program id's in the serv_prog table for unique combinations of fiscal_yr and service_id
    collapsed_serv_prog = (
        serv_prog.groupby(['fiscal_yr', 'service_id'], as_index=False)
        .agg({'program_id': lambda x: ','.join(sorted(x))})
    )
    
    # Merge the collapsed program id table into the 2018 dataset
    si_2018_tidy = pd.merge(si_2018_tidy, collapsed_serv_prog, on=['fiscal_yr', 'service_id'], how='left')
    
    # Add missing columns to both datasets
    # Determine the set of columns for both datasets
    si_2018_columns = set(si_2018_tidy.columns)
    si_2024_columns = set(si_2024_tidy.columns)
    
    # Loop through the columns that do not appear in the other dataset, create the relevant field
    # Columns in 2018, but not in 2024
    for col in si_2018_columns-si_2024_columns: 
        si_2024_tidy[col] = None
    
    # Columns in 2024, but not in 2018
    for col in si_2024_columns-si_2018_columns: 
        si_2018_tidy[col] = None
    
    # Append / concatenate the datasets to one another
    si = pd.concat([si_2018_tidy, si_2024_tidy], ignore_index=True)
    
    # Normalize values across multiple-choice columns
    # and the associated mapping of values from one dataset to the other (2018 : 2024)
    replace_map_si = {
        'SOCIETAL':'SOCIETY', # Service recipient type    
        'PERSONS':'PERSON', # Client target groups
    }
    
    # Service type: Multiple values, split on comma, uppercase, sort
    si['service_type'] = si['service_type'].apply(split_and_uppercase_to_sorted_string)
    
    # Service recipient type: Single value, uppercase, replace values
    si['service_recipient_type'] = si['service_recipient_type'].str.upper()
    si['service_recipient_type'] = si['service_recipient_type'].replace(replace_map_si, regex=True)
    
    # Service scope: Multiple values, split on comma, uppercase, sort, replace values
    si['service_scope'] = si['service_scope'].apply(split_and_uppercase_to_sorted_string)
    si['service_scope'] = si['service_scope'].replace(replace_map_si)
    
    # Client target groups: Multiple values, split on comma, uppercase, sort, replace values
    si['client_target_groups'] = si['client_target_groups'].apply(split_and_uppercase_to_sorted_string)
    si['client_target_groups'] = si['client_target_groups'].replace(replace_map_si, regex=True)
    
    # Client feedback channel: Multiple values, split on comma, uppercase, sort
    si['client_feedback_channel'] = si['client_feedback_channel'].apply(split_and_uppercase_to_sorted_string)
    
    # Service fee: Single value, uppercase
    si['service_fee'] = si['service_fee'].str.upper()
    
    # Last service review, improvement: Single values, replacing "NA", "N" with blanks 
    si['last_service_review'] = si['last_service_review'].replace({np.nan: None, 'N':None})
    si['last_service_improvement'] = si['last_service_improvement'].replace({np.nan: None, 'N':None})

    # Boolean field to identify which services are in scope for typical reporting
    si['service_scope_ext_or_ent'] = (
        (si['service_scope'].str.contains('EXTERN', regex=True)) | 
        (si['service_scope'].str.contains('ENTERPRISE', regex=True))
    )

    # Unique row-level identifier (primary key)
    si['fy_org_id_service_id'] = si[['fiscal_yr', 'org_id', 'service_id']].agg('_'.join, axis=1)

    UTILS_DIR = config['utils_dir']
    export_to_csv(
        data_dict={'si_all': si},
        output_dir=UTILS_DIR,
        config=config
    )

    return si

def merge_ss(config):
    """Combining service standard data from previous (2018) and current (2024) format"""

    # Load org variant list and program-service correspondence table
    org_var = load_csv('org_var.csv', config, snapshot=False)

    # Load department list from utils
    dept = dept_list(config)
    
    ss_2018 = load_csv('ss_2018.csv', config, snapshot=True )
    ss_2024 = load_csv('ss_2024.csv', config, snapshot=True)

    # Test breaker - uncomment to break merge_ss() and check the row count test
    # ss_2024 = ss_2024.head()
    
    # Rename columns in 2018 dataset to align to the 2024 dataset's conventions
    rename_2018_ss_columns = {
        'service_std_id':'service_standard_id',
        'service_std_en':'service_standard_en',
        'service_std_fr':'service_standard_fr',
        'service_std_type':'type',    
        'standard_channel_comment_en':'channel_comments_en',
        'standard_channel_comment_fr':'channel_comments_fr',
        'service_std_target':'target',
        'standard_comment_en':'comments_en',
        'standard_comment_fr':'comments_fr',
        'service_std_url_en':'standards_targets_uri_en',
        'service_std_url_fr':'standards_targets_uri_fr',
        'realtime_result_url_en':'performance_results_uri_en',
        'realtime_result_url_fr':'performance_results_uri_fr'
    }
    
    ss_2018.rename(columns=rename_2018_ss_columns, inplace=True)
    
    # Add org_id to both datasets
    ss_2018_tidy = pd.merge(ss_2018, org_var, left_on='department_name_en', right_on='org_name_variant')
    ss_2024_tidy = pd.merge(ss_2024, org_var, left_on='owner_org', right_on='org_name_variant')
    
    # Drop specific org name fields from both
    ss_2018_tidy = ss_2018_tidy.drop(columns=['department_name_en', 'department_name_fr'])
    ss_2024_tidy = ss_2024_tidy.drop(columns=['owner_org', 'owner_org_title'])

    # Treat org_id as a string
    ss_2018_tidy['org_id'] = ss_2018_tidy['org_id'].astype(str)
    ss_2024_tidy['org_id'] = ss_2024_tidy['org_id'].astype(str)
    
    # Merge in en/fr department names from dept table
    ss_2018_tidy = pd.merge(
        ss_2018_tidy,
        dept,
        on='org_id',
        how='left'
    )
    
    ss_2024_tidy = pd.merge(
        ss_2024_tidy,
        dept,
        on='org_id',
        how='left'
    )
    
    # Add missing columns to both datasets
    # Determine the set of columns for both datasets
    ss_2018_columns = set(ss_2018_tidy.columns)
    ss_2024_columns = set(ss_2024_tidy.columns)
    
    # Loop through the columns that do not appear in the other dataset, create the relevant field
    # Columns in 2018, but not in 2024
    for col in ss_2018_columns-ss_2024_columns: 
        ss_2024_tidy[col] = None
    
    # Columns in 2024, but not in 2018
    for col in ss_2024_columns-ss_2018_columns: 
        ss_2018_tidy[col] = None
    
    # Service standard target & performance: 2018 has this as percentage (over 100), 2024 is as a decimal fraction
    # Convert 2018 to decimal fraction using percentage cleaner fuction defined above
    ss_2018_tidy['target'] = ss_2018_tidy['target'].apply(clean_percentage)
    ss_2018_tidy['performance'] = ss_2018_tidy['performance'].apply(clean_percentage)
    
    # Append / concatenate the datasets to one another
    ss = pd.concat([ss_2018_tidy, ss_2024_tidy], ignore_index=True)
    
    # Normalize values across multiple-choice columns
    # and the associated mapping of values from one dataset to the other (2018 : 2024)
    replace_map_ss = {
        'Timeliness':'TML', # Service standard type    
        'Accuracy':'ACY', # Service standard type
        'Access':'ACS', # Service standard type
        'Other':'OTH', # Service standard type
    }
    
    # Service standard type: single value, replace values
    ss['type'] = ss['type'].replace(replace_map_ss)
    
    # Service standard channel: single value, uppercase
    ss['channel'] = ss['channel'].str.upper()

    # Define identifier to connect to service inventory
    ss['fy_org_id_service_id'] = ss[['fiscal_yr', 'org_id', 'service_id']].agg('_'.join, axis=1)

    # Unique row-level identifier (primary key) to use in comparisons
    ss['fy_org_id_service_id_std_id'] = ss[['fiscal_yr', 'org_id', 'service_id', 'service_standard_id']].agg('_'.join, axis=1)

    UTILS_DIR = config['utils_dir']
    export_to_csv(
        data_dict={'ss_all': ss},
        output_dir=UTILS_DIR,
        config=config
    )

    return ss