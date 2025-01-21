import pandas as pd
import numpy as np
from pathlib import Path

from src.load import load_csv_from_raw
from src.export import export_to_csv

UTILS_DIR = Path(__file__).parent.parent / "outputs" / "utils"

def dept_list():
    #Clean list of departments for use in other modules
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

    dept['org_id'] = dept['org_id'].astype(str)

    export_to_csv(
        data_dict={'dept': dept},
        output_dir=UTILS_DIR
    )
    
    return dept    