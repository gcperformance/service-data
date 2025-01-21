import pandas as pd
import numpy as np
from pathlib import Path

from src.clean import clean_percentage, split_and_uppercase_to_sorted_string
from src.load import load_csv_from_raw
from src.export import export_to_csv

OUTPUT_DIR = Path(__file__).parent.parent / "outputs"

# Load org variant list and program-service correspondence table
org_var = load_csv_from_raw('org_var.csv').set_index('org_name_variant')
serv_prog = load_csv_from_raw('serv_prog.csv')

# Build department name list
ifoi_en = load_csv_from_raw('ifoi_en.csv')
ifoi_fr = load_csv_from_raw('ifoi_fr.csv')

dept_en = ifoi_en.iloc[:,:3]
dept_en['department_en'] = dept_en.iloc[:,2].fillna(dept_en.iloc[:,1])

dept_fr = ifoi_fr.iloc[:,:3]
dept_fr['department_fr'] = dept_fr.iloc[:,2].fillna(dept_fr.iloc[:,1])

dept = pd.merge(
    dept_en,
    dept_fr,
    on='OrgID',
)

dept = dept.loc[:, ['OrgID', 'department_en', 'department_fr']]
dept.rename(columns={'OrgID':'org_id'}, inplace=True)

def merge_si():
    """Combining historical and live service inventory data"""

    si_2018 = load_csv_from_raw('si_2018.csv')
    si_2024 = load_csv_from_raw('si_2024.csv')
    
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

    export_to_csv(
    data_dict={'si': si},
    output_dir=OUTPUT_DIR
    )

    return si

def merge_ss():
    """Combining historical and live service standards data"""
    ss_2018 = load_csv_from_raw('ss_2018.csv')
    ss_2024 = load_csv_from_raw('ss_2024.csv')
    
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

    export_to_csv(
        data_dict={'ss': ss},
        output_dir=OUTPUT_DIR
    )

    return ss