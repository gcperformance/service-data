import pandas as pd
import numpy as np
import pytz
from pathlib import Path
import logging
logger = logging.getLogger(__name__)

from src.export import export_to_csv
from src.load import load_csv
from src.utils import dept_list, program_list

def qa_check(si, ss, config, snapshot=False):
    try:
        # === SETUP ===
        # Load extra files
        org_var = load_csv('org_var.csv', config)
        sid_registry = load_csv('sid_registry.csv', config)
        
        # Build then import department, program list from utilities
        dept = dept_list(config)
        program = program_list(config)

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

        # Harmonize all org_id datatypes across all dataframes
        org_id_dfs = [si, ss, dept, org_var, program, sid_registry]

        for df in org_id_dfs:
            df['org_id'] = pd.to_numeric(df['org_id'], errors = 'coerce').fillna(0).astype('Int64')


        # Create numeric ids, strip out prefixes
        si['service_id_numeric'] = si['service_id'].str.replace(r'^SRV', '', regex=True)
        si['service_id_numeric'] = pd.to_numeric(si['service_id_numeric'], errors = 'coerce')
        
        ss['service_standard_id_numeric'] = ss['service_standard_id'].str.replace(r'^STAN', '', regex=True)
        ss['service_standard_id_numeric'] = pd.to_numeric(ss['service_standard_id_numeric'], errors = 'coerce')


        # === QUALITY ASSURANCE CHECKS ===
        # =================================
        # Merge in the org_id from the service id registry
        si = pd.merge(si, sid_registry[['service_id', 'org_id']], how='left', on='service_id', suffixes=['', '_sid_registry'])
        si = pd.merge(si, dept.rename(columns={'org_id': 'org_id_sid_registry'}), how='left', on='org_id_sid_registry', suffixes=['', '_sid_registry'])
        
        # QA check: unregistered service ID
        # This service id is not registered in the service id registry
        si['qa_unregistered_sid'] = si['org_id_sid_registry'].isna()
        
        # QA check: reused service ID
        # This service id is registered to a different organization
        si['qa_reused_sid'] = (si['org_id'] != si['org_id_sid_registry']) & ~(si['qa_unregistered_sid'])
        si['reused_sid_correct_org'] = si['org_id'].astype(str) +' : ' + si['department_en_sid_registry'] + ' | ' + si['department_fr_sid_registry']

        # QA check: Record is reported for a fiscal year that is incomplete or in the future.
        si['fiscal_yr_end_date'] = pd.to_datetime(si['fiscal_yr'].str.split('-').str[1]+'-04-01')
        si['qa_si_fiscal_yr_out_of_scope'] = si['fiscal_yr_end_date'].dt.date >= current_date
        
        ss['fiscal_yr_end_date'] = pd.to_datetime(ss['fiscal_yr'].str.split('-').str[1]+'-04-01')
        ss['qa_si_fiscal_yr_out_of_scope'] = ss['fiscal_yr_end_date'].dt.date >= current_date

        # QA check: Record has contradiction between client feedback channels and online interaction points for feedback
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
        
        # QA check: Service reports no volume, but associated Service standards have volume
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

        si['qa_no_si_app_volume'] = (si['num_applications_total'] == 0)

        # QA check: Service standard reports no volume
        ss['qa_no_ss_volume'] = (ss['total_volume'] == 0)
        
        # QA check: Services where 'econom' (business) are a client type should not be 'NA' for CRA BN as ID
        si['qa_use_of_cra_bn_applicable'] = (
            (si['client_target_groups'].str.contains('ECONOM')) &
            (si['cra_bn_identifier_usage'] == 'NA')
        )

        # QA check for programs
        # Prepare a dataframe that splits service inventory into one-program-per-row: si_prog
        si['org_id'] = si['org_id'].astype(str)
        program['org_id'] = program['org_id'].astype(str)

        # Exclude empty program ID rows, select relevant columns
        si_prog = si.loc[
            ~si['program_id'].isnull(),
            ['fiscal_yr', 'service_id', 'program_id', 'org_id']]
        si_prog['org_id'] = si_prog['org_id'].astype(str)

        # Split and explode program_id to handle multiple program_id entries per cell
        si_prog['program_id'] = si_prog['program_id'].str.split(',')
        si_prog = si_prog.explode('program_id')

        # Join si_prog with program_list on program_id and org_id
        si_prog = si_prog.merge(program, on=['program_id', 'org_id'], how='left', suffixes=('_si', '_prog'), indicator=True)

        # qa check: program id belongs to different department
        si_prog_wrong_org = si_prog[si_prog['_merge'] == 'left_only']  # Keep only mismatched rows
        si_prog_wrong_org = si_prog_wrong_org.groupby(['fiscal_yr', 'service_id', 'org_id'], as_index=False).agg({'program_id': lambda x: '<>'.join(sorted(map(str, x.dropna())))})
        si_prog_wrong_org.rename(columns={'program_id':'mismatched_program_ids'}, inplace=True)

        # qa check: program id is old/expired
        si_prog['latest_valid_fy_ending_in'] = pd.to_numeric(si_prog['latest_valid_fy'].str.split('-').str[1].fillna(0), errors = 'coerce').astype(int)
        si_prog['reported_fy_ending_in'] = pd.to_numeric(si_prog['fiscal_yr'].str.split('-').str[1].fillna(0), errors = 'coerce').astype(int)
        si_prog['program_id_latest_valid_fy'] = si_prog['program_id']+': '+si_prog['latest_valid_fy']

        si_prog_old = si_prog[(si_prog['latest_valid_fy_ending_in'] < si_prog['reported_fy_ending_in']) & (si_prog['_merge'] =='both')]
        si_prog_old = si_prog_old.groupby(['fiscal_yr', 'service_id', 'org_id'], as_index=False).agg({'program_id_latest_valid_fy': lambda x: '<>'.join(sorted(map(str, x.dropna())))})

        # Merge into si
        si = pd.merge(si, si_prog_old, on=['fiscal_yr', 'service_id', 'org_id'], how='left')
        si['qa_program_id_old'] = ~(si['program_id_latest_valid_fy'].isnull())

        si = pd.merge(si, si_prog_wrong_org, on=['fiscal_yr', 'service_id', 'org_id'], how='left')
        si['qa_program_id_wrong_org'] = ~(si['mismatched_program_ids'].isnull())

        # QA check: Service standard performance is greater than 100%
        ss['qa_performance_over_100'] = ss['volume_meeting_target']>ss['total_volume']

        # === EXPORT DATA TO CSV ===
        # Define the DataFrames to export to csv and their corresponding names
        csv_exports = {
            "si_qa": si,
            "ss_qa": ss
        }

        # If running a snapshot run, change output directory accordingly
        if snapshot:
            QA_DIR = config['output_dir'] / 'snapshots' / snapshot / config['qa_dir']
        else:
            QA_DIR = config['output_dir'] / config['qa_dir']
        
        export_to_csv(
            data_dict=csv_exports,
            output_dir=QA_DIR
        )

        # === Run/build QA report ===
        qa_report(si, ss, config)
    
    except Exception as e:
        logger.error("Error: %s", e, exc_info=True)


def qa_report(si_qa, ss_qa, config, snapshot=False):
    def generate_context(row):
        issue_messages = {
            'qa_reused_sid': f"{row['reused_sid_correct_org']}",
            'qa_unregistered_sid': f"{row['service_id']}",
            'qa_program_id_wrong_org': f"{row['mismatched_program_ids']}",
            'qa_program_id_old': f"{row['program_id_latest_valid_fy']}",
            'qa_ss_vol_without_si_vol': f"service applications: {row['num_applications_total']}, standard volumes: {row['total_volume_ss']}",
            'qa_si_fiscal_yr_out_of_scope': f"{row['fiscal_yr']}",
            'qa_ss_fiscal_yr_out_of_scope': f"{row['fiscal_yr']}"
            }

        return issue_messages.get(row['qa_field_name'])

    try:
        # === CLEAN QA REPORT ===
        # In order to have a clean report of issues to send to departments & agencies, the following 
        # re-organizes the information in the qa columns to a simple report.
        si_qa_cols = si_qa.columns[si_qa.columns.str.startswith('qa')].to_list()
        ss_qa_cols = ss_qa.columns[ss_qa.columns.str.startswith('qa')].to_list()

        # Import qa issues descriptions file
        CURRENT_DIR = Path(__file__).parent
        file_path = CURRENT_DIR / 'qa_issues_descriptions.csv'
        qa_issues_description = pd.read_csv(file_path)
        # qa_issues_description = pd.read_csv('/workspaces/service-data/src/qa_issues_descriptions.csv')

        # We are only including a specific set of checks in the report.
        # critical_si_qa_cols = [
        #     'qa_duplicate_sid',
        #     'qa_si_fiscal_yr_in_future',
        #     'qa_ss_vol_without_si_vol',
        #     'qa_reused_sid',
        #     'qa_program_id'
        # ]

        # critical_ss_qa_cols = [
        #     'qa_duplicate_stdid',
        #     'qa_no_ss_volume',
        #     'qa_ss_fiscal_yr_in_future',
        #     'qa_performance_over_100'
        # ]   

        critical_si_qa_cols = si_qa_cols
        critical_ss_qa_cols = ss_qa_cols

        # === PREPARING SI QA REPORT ===
        si_report_cols = [
            'department_en',
            'department_fr',
            'org_id',
            'fiscal_yr', 
            'service_id', 
            'service_name_en', 
            'service_name_fr',
            'num_applications_total',
            'total_volume_ss',
            'reused_sid_correct_org',
            'program_id',
            'program_id_latest_valid_fy',
            'mismatched_program_ids'
        ]

        # Transform data to have all qa issues in a single column
        si_qa_report = pd.melt(
            si_qa, 
            id_vars=si_report_cols, 
            value_vars=critical_si_qa_cols, 
            var_name='issue', 
            value_name='issue_present')

        # Filter data only for records where there is a qa issue
        si_qa_report = si_qa_report[
            (si_qa_report['issue_present']) & 
            (si_qa_report['fiscal_yr'].isin(['2023-2024', '2024-2025']))
        ]

        si_qa_report = pd.merge(
            si_qa_report, 
            qa_issues_description.loc[:, [
                'qa_field_name',
                'severity_en', 
                'description_en', 
                'action_en',
                'severity_fr',
                'description_fr',
                'action_fr'
            ]], 
            left_on='issue', 
            right_on='qa_field_name', 
            how='left'
        )

        # Consolidate additional context to a single field specific to each qa issue
        si_qa_report['context'] = si_qa_report.apply(generate_context, axis=1)

        # Tidy up dataframe
        si_qa_report = si_qa_report.drop(columns=[
            'issue_present',
            'qa_field_name',
            'num_applications_total', # replaced by context field
            'total_volume_ss',  # replaced by context field
            'reused_sid_correct_org', # replaced by context field
            'program_id', # replaced by context field
            'program_id_latest_valid_fy', # replaced by context field
            'mismatched_program_ids' # replaced by context field
            ])

        si_qa_report = si_qa_report.sort_values(by=['org_id', 'severity_en', 'service_id'])

        # ==============================
        # === PREPARING SS QA REPORT ===

        ss_report_cols = [
            'department_en',
            'department_fr',
            'org_id',
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

        ss_qa_report = pd.melt(ss_qa, id_vars=ss_report_cols, value_vars=critical_ss_qa_cols, var_name='issue', value_name='issue_present')

        ss_qa_report = ss_qa_report[(ss_qa_report['issue_present'] & ss_qa_report['fiscal_yr'].isin(['2023-2024', '2024-2025']))]

        ss_qa_report = pd.merge(
            ss_qa_report, 
            qa_issues_description.loc[:, [
                'qa_field_name',
                'severity_en', 
                'description_en', 
                'action_en',
                'severity_fr',
                'description_fr',
                'action_fr'
            ]],
            left_on='issue', 
            right_on='qa_field_name', 
            how='left'
        )

        ss_qa_report = ss_qa_report.drop(columns=['issue_present', 'qa_field_name'])

        ss_qa_report = ss_qa_report.sort_values(by=['org_id', 'severity_en', 'service_id', 'service_standard_id'])

        # === EXPORT TO CSV ===
        # Define the DataFrames to export to csv and their corresponding names
        csv_exports = {
            "si_qa_report": si_qa_report,
            "ss_qa_report": ss_qa_report
        }

        # If running a snapshot run, change output directory accordingly
        if snapshot:
            QA_DIR = config['output_dir'] / 'snapshots' / snapshot / config['qa_dir']
        else:
            QA_DIR = config['output_dir'] / config['qa_dir']
        
        export_to_csv(
            data_dict=csv_exports,
            output_dir=QA_DIR
        )

    except Exception as e:
        logger.error("Error: %s", e, exc_info=True)