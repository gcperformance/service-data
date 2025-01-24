import pandas as pd
import numpy as np
from pathlib import Path

from src.load import load_csv_from_raw
from src.export import export_to_csv

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

def copy_raw_to_utils():
    ifoi_en = load_csv_from_raw('ifoi_en.csv')
    ifoi_fr = load_csv_from_raw('ifoi_fr.csv')
    org_var = load_csv_from_raw('org_var.csv')

    utils_file_dict = {
        'ifoi_en':ifoi_en,
        'ifoi_fr':ifoi_fr,
        'org_var':org_var
    }
    
    export_to_csv(
        data_dict=utils_file_dict,
        output_dir=UTILS_DIR
    )

def standardize_column_names(df):
    """
    Standardize DataFrame column names to snake_case format.
    
    Args:
        df (pd.DataFrame): Input DataFrame
        
    Returns:
        pd.DataFrame: DataFrame with standardized column names
    """
    # Create a mapping of common variations to standardized names
    name_mapping = {
        'OrgID': 'org_id',
        'OrganizationID': 'org_id',
        'organization_id': 'org_id',
        'ServiceID': 'service_id',
        'ProgramID': 'program_id'
    }
    
    # Apply the mapping to column names
    df = df.rename(columns=name_mapping)
    return df