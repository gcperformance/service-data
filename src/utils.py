import pandas as pd
import numpy as np
from pathlib import Path
import re

from src.load import load_csv_from_raw
from src.export import export_to_csv
from src.clean import standardize_column_names

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
