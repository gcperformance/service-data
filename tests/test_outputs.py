import pandas as pd
import pandas.testing as pdt
from pathlib import Path
import os
import pytz
import pytest

OUTPUT_DIR = Path(__file__).parent.parent / "outputs"
REF_DIR = Path(__file__).parent / "ref"

def test_fields():
    ref_file = REF_DIR / "reference_fields.csv"
    reference_fields = pd.read_csv(ref_file)

    paths = reference_fields['file_path'].unique()
    
    for path in paths:
        df = pd.read_csv(path, delimiter=";", skipfooter=1, engine='python')  
        df_inferred = df.convert_dtypes()  # Infer data types from all rows
        df['breaking!'] = 1
        col_set_reference = set(reference_fields['fields'][reference_fields['file_path'] == path])
        col_set_test = set(df_inferred.columns)
        assert col_set_test == col_set_reference, "missing column!"            
      

if __name__ == "__main__":
    test_fields()
    