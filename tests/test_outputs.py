import pandas as pd
import pandas.testing as pdt
from pathlib import Path
import pytest

OUTPUT_DIR = Path(__file__).parent.parent / "outputs"
REF_DIR = Path(__file__).parent / "ref"

def test_no_columns_dropped():
    ref_file = REF_DIR / "reference_fields.csv"
    reference_fields = pd.read_csv(ref_file)

    file_names = reference_fields['file_name'].unique()
    
    for file_name in file_names:
        path = OUTPUT_DIR / file_name
        df = pd.read_csv(path, delimiter=";", skipfooter=1, engine='python')

        col_set_reference = reference_fields['fields'][reference_fields['file_name'] == file_name]
        col_set_reference = set(col_set_reference)
        col_set_test = set(df.columns)
        
        assert col_set_test == col_set_reference, f"Missing column in {file_name}"

def test_column_types():    
    ref_file = REF_DIR / "reference_fields.csv"
    reference_fields = pd.read_csv(ref_file)

    file_names = reference_fields['file_name'].unique()

    for file_name in file_names:
        path = OUTPUT_DIR / file_name
        df = pd.read_csv(path, delimiter=";", skipfooter=1, engine='python')  
        df_inferred = df.convert_dtypes()  # Infer data types from all rows

        actual_dtypes = df_inferred.dtypes.astype(str).to_dict()
        expected_dtypes = dict(zip(reference_fields['fields'][reference_fields['file_name']==file_name], reference_fields['datatype'][reference_fields['file_name']==file_name]))

        mismatches = {
            col: (actual_dtypes[col], expected_dtypes[col])
            for col in expected_dtypes
            if actual_dtypes.get(col) != expected_dtypes[col]
            }

        assert not mismatches, f'Datatype mismatches: {mismatches}'
                  

if __name__ == "__main__":
    test_no_columns_dropped()
    test_column_types()
    