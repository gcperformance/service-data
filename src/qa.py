import pandas as pd
import numpy as np
import pytz
from pathlib import Path

from src.export import export_to_csv
from src.load import load_csv_from_raw
from src.utils import dept_list


QA_DIR = Path(__file__).parent.parent / "outputs" / "qa"
CURRENT_DIR = Path(__file__).parent

def qa_check(si, ss):
    # Setup
    # Load extra files
    rbpo = load_csv_from_raw('rbpo.csv')
    org_var = load_csv_from_raw('org_var.csv')
    
    # Import qa issues descriptions file
    file_path = CURRENT_DIR / 'qa_issues_descriptions.csv'
    qa_issues_description = pd.read_csv(file_path)

    # Build then import department list from utilities
    dept = dept_list()

    # Determine the current date
    timezone = pytz.timezone('America/Montreal')
    current_datetime = pd.Timestamp.now(tz=timezone)
    current_date = current_datetime.date()
    
    # Coerce all numeric fields
    int_cols = {
        'num_phone_enquiries': si,
        'num_applications_by_phone': si,
        'num_website_visits': si,
        'num_applications_online': si,
        'num_applications_by_mail': si,
        'num_applications_by_email': si,
        'num_applications_by_fax': si,
        'num_applications_by_other': si,
        'num_applications_total': si,
        'volume_meeting_target': ss,
        'total_volume': ss
    }
    
    for column, df in int_cols.items():
        int_cols[column][column] = pd.to_numeric(df[column], errors = 'coerce').fillna(0).astype(int)

    # Create numeric ids, strip out prefixes
    si['service_id_numeric'] = si['service_id'].str.replace(r'^SRV', '', regex=True)
    si['service_id_numeric'] = pd.to_numeric(si['service_id_numeric'], errors = 'coerce')
    
    ss['service_standard_id_numeric'] = ss['service_standard_id'].str.replace(r'^STAN', '', regex=True)
    ss['service_standard_id_numeric'] = pd.to_numeric(ss['service_standard_id_numeric'], errors = 'coerce')
        
    # QA Check 1: Duplicate service ID conflict
    # Step 1: Flag rows where 'service_id' is duplicated within each 'fiscal_yr'
    si['qa_duplicate_sid'] = si.duplicated(subset=['fiscal_yr', 'service_id'], keep=False)
    
    # Step 2: Get unique 'service_id's that are flagged as duplicates
    duplicate_ids = si.loc[si['qa_duplicate_sid'], 'service_id'].unique()
    
    # Step 3: Filter rows with duplicate 'service_id's and group by 'service_id' and 'department_en'
    duplicate_groups = (
        si.loc[si['service_id'].isin(duplicate_ids), ['fiscal_yr', 'service_id', 'department_en']]
        .groupby(['service_id', 'department_en'])['fiscal_yr']  # Count occurrences of 'fiscal_yr'
        .nunique()  # Count unique fiscal years for each group
    )
    
    # Step 4: Identify groups with only one unique fiscal year (problematic cases)
    problematic_duplicates = duplicate_groups[duplicate_groups == 1].reset_index()
    
    # Step 5: Keep only 'service_id' and 'department_en' columns
    problematic_duplicates = problematic_duplicates[['service_id', 'department_en']]
    
    # Step 6: Create a set of tuples from 'problematic_duplicates' for efficient lookup
    problematic_set = set(zip(problematic_duplicates['service_id'], problematic_duplicates['department_en']))
    
    # Step 7: Update the 'qa_duplicate_sid' column based on whether each row matches a problematic duplicate
    si['qa_duplicate_sid'] = si.apply(
        lambda row: (row['service_id'], row['department_en']) in problematic_set, axis=1
    )    
    
    # Verify:
    # si.loc[:, ['fiscal_yr', 'department_en', 'service_id', 'qa_duplicate_sid']][si['qa_duplicate_sid']]
    
    # QA Check 2: Duplicate Service Standard ID conflict
    # Step 1: Flag rows where 'service_standard_id' is duplicated within each 'fiscal_yr'
    ss['qa_duplicate_stdid'] = ss.duplicated(subset=['fiscal_yr', 'service_standard_id'], keep=False)
    
    # Step 2: Get unique 'service_standard_id's that are flagged as duplicates
    duplicate_ids = ss.loc[ss['qa_duplicate_stdid'], 'service_standard_id'].unique()
    
    # Step 3: Filter rows with duplicate 'service_standard_id's and group by 'service_standard_id' and 'department_en'
    duplicate_groups = (
        ss.loc[ss['service_standard_id'].isin(duplicate_ids), ['fiscal_yr', 'service_standard_id', 'department_en']]
        .groupby(['service_standard_id', 'department_en'])['fiscal_yr']  # Count occurrences of 'fiscal_yr'
        .nunique()  # Count unique fiscal years for each group
    )
    
    # Step 4: Identify groups with only one unique fiscal year (problematic cases)
    problematic_duplicates = duplicate_groups[duplicate_groups == 1].reset_index()
    
    # Step 5: Keep only 'service_standard_id' and 'department_en' columns
    problematic_duplicates = problematic_duplicates[['service_standard_id', 'department_en']]
    
    # Step 6: Create a set of tuples from 'problematic_duplicates' for efficient lookup
    problematic_set = set(zip(problematic_duplicates['service_standard_id'], problematic_duplicates['department_en']))
    
    # Step 7: Update the 'qa_duplicate_sid' column based on whether each row matches a problematic duplicate
    ss['qa_duplicate_stdid'] = ss.apply(
        lambda row: (row['service_standard_id'], row['department_en']) in problematic_set, axis=1
    )    
    
    # Verify:
    # ss.loc[:, ['fiscal_yr', 'department_en', 'service_id', 'service_standard_id', 'qa_duplicate_stdid']][ss['qa_duplicate_stdid']]    
    
    # QA Check 3: Identify service IDs that have already been used by other departments in previous fiscal years
    si_filtered = si[['service_id', 'department_en', 'org_id', 'fiscal_yr']]
    si_filtered = si_filtered.sort_values(by=['service_id', 'fiscal_yr']).reset_index(drop=True)
    
    # Step 1: Self-join to compare records
    joined_df = si_filtered.merge(si_filtered, on='service_id', suffixes=('', '_prev'))
    
    # Step 2: Filter reused records
    reused_ids = joined_df[
        (joined_df['fiscal_yr'] > joined_df['fiscal_yr_prev']) & 
        (joined_df['department_en'] != joined_df['department_en_prev'])
    ]
    
    # Step 3: Select the record with the latest 'fiscal_yr_prev' for each 'service_id' and 'fiscal_yr'
    reused_ids = reused_ids.loc[reused_ids.groupby(['service_id', 'fiscal_yr'])['fiscal_yr_prev'].idxmax()].reset_index(drop=True)
    
    # Step 4: Identify which fiscal year and department previously used the id
    reused_ids['reused_id_from'] = reused_ids['fiscal_yr_prev']+' '+reused_ids['department_en_prev']
    
    # Step 5: Create a unique key for matching
    reused_ids['key'] = (
        reused_ids['fiscal_yr'].astype(str)+' '+
        reused_ids['org_id'].astype(str)+' '+
        reused_ids['service_id'].astype(str)
        )
    
    si['key'] = (
        si['fiscal_yr'].astype(str)+' '+
        si['org_id'].astype(str)+' '+
        si['service_id'].astype(str)
        )
    
    # Step 6: Map 'reused_id_from' to the original 'si' DataFrame
    reused_id_from_dict = dict(zip(reused_ids['key'], reused_ids['reused_id_from']))
    
    si['reused_id_from'] = si['key'].map(reused_id_from_dict)
    si['qa_reused_sid'] = si['reused_id_from'].notna()
    
    # Step 7: Drop the temporary key column
    si = si.drop(columns=['key'])
    
    # Verify:
    # si[['fiscal_yr', 'service_id', 'department_en', 'qa_reused_sid']][si['qa_reused_sid']]    
    
    # QA Check 4: Record is reported for a fiscal year that is incomplete or in the future.
    si['fiscal_yr_end_date'] = pd.to_datetime(si['fiscal_yr'].str.split('-').str[1]+'-04-01')
    si['qa_si_fiscal_yr_in_future'] = si['fiscal_yr_end_date'].dt.date >= current_date
    
    ss['fiscal_yr_end_date'] = pd.to_datetime(ss['fiscal_yr'].str.split('-').str[1]+'-04-01')
    ss['qa_ss_fiscal_yr_in_future'] = ss['fiscal_yr_end_date'].dt.date >= current_date

    # QA Check 5: Record has contradiction between client feedback channels and online interaction points for feedback
    si['qa_client_feedback_contradiction'] = (
    
        # Service accepts client feedback via the online channel (ONL) but online issue resolution or feedback is not applicable or not activated
        (
            si['client_feedback_channel'].str.contains('ONL') & 
            (
                si['os_issue_resolution_feedback'].isna() | 
                (si['os_issue_resolution_feedback'] == 'N')
            )
        ) |
        # Service has not listed the online channel (ONL) for client feedback but online issue resolution or feedback is activated
        (
            (~si['client_feedback_channel'].str.contains('ONL')) &
            (si['os_issue_resolution_feedback'] == 'Y')
        )
    )
    
    # Verify:
    # si[['client_feedback_channel', 'os_issue_resolution_feedback', 'client_feedback_contradiction']].loc[si['client_feedback_contradiction'] == True]
        
    # QA Check 6: Service reports no volume, but associated Service standards have volume
    ss_vol_by_service = (
        ss.groupby(['fiscal_yr', 'service_id'])['total_volume']
        .sum()
        .reset_index()
        .rename(columns={'total_volume':'total_volume_ss'})
    )
    
    si = si.merge(ss_vol_by_service, on=['fiscal_yr', 'service_id'], how='left').fillna(0)
    
    si['qa_ss_vol_without_si_vol'] = (
        (si['total_volume_ss'] > 0) & (si['num_applications_total'] == 0)
    )

    # QA Check 7: Service standard reports no volume
    ss['qa_no_ss_volume'] = (ss['total_volume'] == 0)
    
    
    # QA Check 8: Services that target society as a recipient type we would not expect to see specific interaction volume
    # Note that this assumption may be false
    si['num_applications_total'] = pd.to_numeric(si['num_applications_total'], errors = 'coerce').fillna(0).astype(int)
    
    si['qa_service_recipient_type_society_with_interactions'] = (
        (si['service_recipient_type'] == 'SOCIETY') &
        (si['num_applications_total'] > 0)
    )
        
    # QA Check 9: Services where 'persons' are a client type should not be 'NA' for SIN as ID
    si['qa_use_of_sin_applicable'] = (
        (si['client_target_groups'].str.contains('PERSON')) &
        (si['sin_usage'] == 'NA')
    )   
    
    # QA Check 10: Services where 'econom' (business) are a client type should not be 'NA' for CRA BN as ID
    si['qa_use_of_cra_bn_applicable'] = (
        (si['client_target_groups'].str.contains('ECONOM')) &
        (si['cra_bn_identifier_usage'] == 'NA')
    )

    # QA Check 11: Services must be associated to programs from the same department
    # Exception: we have provided instructions to use any of the ISS internal service
    # programs regardless of whether that program is listed for the department in 
    # the chart of accounts.

    # Filter and clean rbpo DataFrame to get a clean list of programs and departments
    rbpo_filtered = (
        rbpo[['organization', 'program_id']]  # Select relevant columns
        .merge(org_var, left_on='organization', right_on='org_name_variant', how='left')  # Merge with org_var
        .drop_duplicates()  # Remove duplicate rows
    )
    
    # Filter out internal programs containing 'ISS'
    rbpo_filtered['internal_program'] = rbpo_filtered['program_id'].str.contains('ISS')
    rbpo_filtered = rbpo_filtered[~rbpo_filtered['internal_program']]  # Keep only non-internal programs
    rbpo_filtered = rbpo_filtered[['program_id', 'org_id']]  # Keep only necessary columns
    
    rbpo_filtered['org_id']= rbpo_filtered['org_id'].astype(str)
    
    # Prepare si_prog DataFrame
    si_prog = si.loc[:,['fiscal_yr', 'service_id', 'program_id', 'org_id']]  # Select relevant columns
    si_prog['org_id'] = si_prog['org_id'].astype(str)
    
    
    # Split and explode program_id to handle multiple entries per cell
    si_prog['program_id'] = si_prog['program_id'].str.split(',')
    si_prog = si_prog.explode('program_id')
    
    # Filter out internal programs containing 'ISS'
    si_prog['internal_program'] = si_prog['program_id'].str.contains('ISS').astype(bool)
    si_prog = si_prog[~si_prog['internal_program']]  # Keep only non-internal programs
    
    #Join si_prog with rbpo_filtered (program list) on program_id
    si_prog = si_prog.merge(rbpo_filtered, on='program_id', how='left', suffixes=('_si', '_prog'))
    si_prog['qa_program_from_wrong_org'] = si_prog['org_id_si'] != si_prog['org_id_prog'] # Identify rows where org_id mismatch occurs
    si_prog = si_prog[si_prog['qa_program_from_wrong_org']]  # Keep only mismatched rows
    si_prog = si_prog[si_prog['program_id'] != ''] # Remove rows with empty program_id    
    
    # Merge si_prog with department information
    si_prog = si_prog.merge(dept, left_on='org_id_prog', right_on='org_id', how='left')
    
    # Create a field describing the correct organization associated to the program id
    si_prog['program_correct_org'] = (
        si_prog['program_id'] + ': ' + si_prog['department_en'] + '/' + si_prog['department_fr']
    )
    
    collapsed_si_prog = (
            si_prog.groupby(['fiscal_yr', 'service_id', 'org_id_si'], as_index=False)
            .agg({'program_correct_org': lambda x: '<>'.join(sorted(map(str, x.dropna())))})
        )
    
    collapsed_si_prog.rename(columns={'org_id_si': 'org_id'}, inplace=True)

    collapsed_si_prog['org_id'] = collapsed_si_prog['org_id'].astype(str)
    si['org_id'] = si['org_id'].astype(str)
    
    si=si.merge(collapsed_si_prog, on=['fiscal_yr', 'service_id', 'org_id'], how='left')
    si['qa_program_from_wrong_org'] = ~(si['program_correct_org'].isna())
    si['program_correct_org'] = si['program_correct_org'].fillna(False)

    # QA Check: Service standard performance is greater than 100%
    ss['qa_performance_over_100'] = ss['volume_meeting_target']>ss['total_volume']

    # Clean QA report
    # In order to have a clean report of issues to send to departments & agencies, the following bit of script re-organizes the information in the qa columns to a simple report for 2023-2024 data.
    si_qa_cols = si.columns.str.startswith('qa')
    ss_qa_cols = ss.columns.str.startswith('qa')

    # We are only including a specific set of checks in the report.
    critical_si_qa_cols = [
        'qa_duplicate_sid',
        'qa_si_fiscal_yr_in_future',
        'qa_ss_vol_without_si_vol',
        'qa_reused_sid',
        'qa_program_from_wrong_org'
    ]
    
    critical_ss_qa_cols = [
        'qa_duplicate_stdid',
        'qa_no_ss_volume',
        'qa_ss_fiscal_yr_in_future',
        'qa_performance_over_100'
    ]   
    
    # Preparing SI QA report
    si_report_cols = [
        'department_en',
        'fiscal_yr', 
        'service_id', 
        'service_name_en', 
        'service_name_fr',
        'num_applications_total',
        'total_volume_ss',
        'reused_id_from',
        'program_id',
        'program_correct_org'
    ]
    
    si_qa_report = pd.melt(si, id_vars=si_report_cols, value_vars=critical_si_qa_cols, var_name='issue', value_name='issue_present')
    
    si_qa_report = si_qa_report[(si_qa_report['issue_present'] & si_qa_report['fiscal_yr'].isin(['2023-2024', '2024-2025']))]
    
    si_qa_report = pd.merge(
        si_qa_report, 
        qa_issues_description.loc[:, [
            'qa_field_name', 
            'description_en', 
            'action_en',
            'description_fr',
            'action_fr'
        ]], 
        left_on='issue', 
        right_on='qa_field_name', 
        how='left'
    )
    
    si_qa_report = si_qa_report.drop(columns=['issue_present', 'qa_field_name'])
    
    si_qa_report = si_qa_report.sort_values(by=['department_en', 'service_id'])
    
    # Preparing SS QA report
    ss_report_cols = [
        'department_en',
        'fiscal_yr', 
        'service_id', 
        'service_name_en', 
        'service_name_fr',
        'service_standard_id',
        'service_standard_en',
        'service_standard_fr',
        'volume_meeting_target',
        'total_volume',
        'performance'
    ]
    
    ss_qa_report = pd.melt(ss, id_vars=ss_report_cols, value_vars=critical_ss_qa_cols, var_name='issue', value_name='issue_present')
    
    ss_qa_report = ss_qa_report[(ss_qa_report['issue_present'] & ss_qa_report['fiscal_yr'].isin(['2023-2024', '2024-2025']))]
    
    ss_qa_report = pd.merge(
        ss_qa_report, 
        qa_issues_description.loc[:, [
            'qa_field_name', 
            'description_en', 
            'action_en',
            'description_fr',
            'action_fr'
        ]], 
        left_on='issue', 
        right_on='qa_field_name', 
        how='left'
    )
    
    ss_qa_report = ss_qa_report.drop(columns=['issue_present', 'qa_field_name'])
    
    ss_qa_report = ss_qa_report.sort_values(by=['department_en', 'service_id', 'service_standard_id'])
    
    # ## Export data to CSV
    # Define the DataFrames to export to csv and their corresponding names
    csv_exports = {
        "si_qa": si,
        "ss_qa": ss,
        "si_qa_report": si_qa_report,
        "ss_qa_report": ss_qa_report
    }

    export_to_csv(
        data_dict=csv_exports,
        output_dir=QA_DIR
    )
