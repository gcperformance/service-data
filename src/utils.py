import pandas as pd
import numpy as np
from pathlib import Path
import re

from src.load import load_csv_from_raw
from src.export import export_to_csv
from src.clean import standardize_column_names, clean_fiscal_yr

UTILS_DIR = Path(__file__).parent.parent / "outputs" / "utils"

def dept_list():
    """
    Get a list of departments with their English and French names.
    """
    ifoi_en = load_csv_from_raw('ifoi_en.csv')
    ifoi_fr = load_csv_from_raw('ifoi_fr.csv')
    
    # Process English names
    dept_en = ifoi_en.iloc[:,:3]
    dept_en['department_en'] = dept_en.iloc[:,2].fillna(dept_en.iloc[:,1])
    dept_en = dept_en[['OrgID', 'department_en']]
    
    # Process French names
    dept_fr = ifoi_fr.iloc[:,:3]
    dept_fr['department_fr'] = dept_fr.iloc[:,2].fillna(dept_fr.iloc[:,1])
    dept_fr = dept_fr[['OrgID', 'department_fr']]
    
    # Merge English and French department names
    dept = pd.merge(
        dept_en,
        dept_fr,
        on='OrgID',
        how='outer'
    )
    
    # Standardize column names and convert org_id to string
    dept = standardize_column_names(dept)
    dept['org_id'] = dept['org_id'].astype(str)
    
    export_to_csv(
        data_dict={'dept': dept},
        output_dir=UTILS_DIR
    )
    
    return dept
    

def sid_list(si):
    # Unique list of service IDs as reported in the latest fy
    sid_list = si.loc[
        si.groupby('service_id')['fiscal_yr'].idxmax(), [
            'service_id', 
            'service_name_en', 
            'service_name_fr', 
            'fiscal_yr', 
            'department_en', 
            'department_fr', 
            'org_id'
        ]
    ]

    export_to_csv(
        data_dict={'sid_list': sid_list},
        output_dir=UTILS_DIR
    )

    return sid_list


def build_drf():
    # Load and clean DRF data (i.e. RBPO)
    drf = load_csv_from_raw('rbpo.csv')
    drf = standardize_column_names(drf)
    drf['fiscal_yr'] = drf['fiscal_yr'].apply(clean_fiscal_yr)
    
    # Define columns related to planned and actual measures: spending and FTEs 
    fte_spend_cols = [
        'planned_spending_1', 
        'actual_spending', 
        'planned_spending_2', 
        'planned_spending_3',
        'planned_ftes_1', 
        'actual_ftes', 
        'planned_ftes_2', 
        'planned_ftes_3'
    ]
    
    # Melt (unpivot) the DataFrame to long format
    drf = pd.melt(
        drf, 
        id_vars=['fiscal_yr', 'org_id', 'program_id'], 
        value_vars=fte_spend_cols, 
        var_name='plan_actual_spendfte_yr', 
        value_name='measure'
    )
    
    # Split 'plan_actual_yr' into separate columns for planned/actual, spending/FTEs, and year adjustment
    drf[['planned_actual', 'spending_fte', 'yr_adjust']] = drf['plan_actual_spendfte_yr'].str.split('_', expand=True)
    drf['yr_adjust'] = drf['yr_adjust'].fillna('1').astype(int) - 1
    
    # Calculate 4-digit 'measure_yr' and 'report_yr' from 'fiscal_yr' and 'yr_adjust'
    drf['measure_yr'] = drf['fiscal_yr'].str.split('-').str[1].astype(int) + drf['yr_adjust']
    drf['report_yr'] = drf['fiscal_yr'].str.split('-').str[1].astype(int)
    
    # Get the latest fiscal year from the Service inventory (four digit fy, year of end of fy)
    # latest_si_fy = si['fiscal_yr'].str.split('-').str[1].astype(int).max()
    latest_si_fy = 2024
    
    # Separate actuals and future planned data
    drf_actuals = drf[
        (drf['planned_actual'] == 'actual') & 
        (drf['report_yr'] <= latest_si_fy)
    ].dropna()
    
    drf_planned = drf[
        (drf['planned_actual'] == 'planned') &
        (drf['report_yr'] > latest_si_fy) 
    ].dropna()
    
    # Each report year has 3 measure years for planned values.
    # Only keep records that have the highest report year for that given program, measure type, and measure year
    idx = drf_planned.groupby(['program_id', 'spending_fte', 'measure_yr'])['report_yr'].idxmax()
    drf_planned = drf_planned.loc[idx]
    
    # Concatenate actuals and planned entries
    drf = pd.concat([drf_actuals, drf_planned])
        
    # Pivot to get a wide format table with spending/FTE columns
    drf = drf.pivot_table(
        index=['org_id', 'program_id', 'report_yr', 'measure_yr', 'planned_actual'], 
        columns=['spending_fte'], 
        values='measure'
    ).sort_values(
        by=['org_id', 'program_id', 'report_yr','measure_yr']
    ).reset_index()
       
    # Set up si_link_yr: a fiscal year column to be able to include years 
    # beyond the service inventory when joining by service id and fy.
    # if measure year > latest service fy, = latest service fy, else use measure_yr
    drf.loc[drf['measure_yr']>latest_si_fy, 'si_link_yr'] = latest_si_fy
    drf.loc[drf['measure_yr']<=latest_si_fy, 'si_link_yr'] = drf['measure_yr']
    drf['si_link_yr'] = drf['si_link_yr'].astype(int) 

    export_to_csv(
        data_dict={'drf': drf},
        output_dir=UTILS_DIR
    )

    return drf

def copy_raw_to_utils():
    ifoi_en = load_csv_from_raw('ifoi_en.csv')
    ifoi_fr = load_csv_from_raw('ifoi_fr.csv')
    org_var = load_csv_from_raw('org_var.csv')

    utils_file_dict = {
        'ifoi_en':ifoi_en,
        'ifoi_fr':ifoi_fr,
        'org_var':org_var
    }

    for key in utils_file_dict.keys():
        utils_file_dict[key] = standardize_column_names(utils_file_dict[key])
    
    export_to_csv(
        data_dict=utils_file_dict,
        output_dir=UTILS_DIR
    )
