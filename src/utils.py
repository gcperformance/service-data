import pandas as pd
import numpy as np
from pathlib import Path
import re

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

    for key in utils_file_dict.keys():
        utils_file_dict[key] = standardize_column_names(utils_file_dict[key])
    
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
        'orgid': 'org_id',
        'organizationid': 'org_id',
        'organization_id': 'org_id',
        'serviceid': 'service_id',
        'programid': 'program_id'
    }
    
    # Normalize column names to lowercase
    df.columns = df.columns.str.lower()
    df.columns = df.columns.str.strip()

    # Apply the mapping to column names
    df = df.rename(columns=name_mapping)
    
    # Apply the mapping to column names
    df = df.rename(columns=lambda col: to_snake_case(col))
    
    return df

def to_snake_case(input_string):
    """
    Converts a given string to snake_case.

    Args:
        input_string (str): The input string to convert.

    Returns:
        str: The converted string in snake_case.
    """
    # Replace spaces and hyphens with underscores
    processed_string = re.sub(r'[\s\-]+', '_', input_string)
    # Convert CamelCase or PascalCase to snake_case
    processed_string = re.sub(r'(?<!^)(?=[A-Z])', '_', processed_string)
    # Lowercase the entire string
    processed_string = processed_string.lower()
    # Remove any leading or trailing underscores
    processed_string = processed_string.strip('_')

    return processed_string
