import pandas as pd
import pandas.testing as pdt
import pytest
from src.merge import merge_si, merge_ss
from src.load import load_csv
from main import get_config

# Mock export function to prevent file creation
@pytest.fixture(autouse=True)
def mock_export_to_csv(monkeypatch):
    config = get_config()
    monkeypatch.setattr("src.export.export_to_csv", lambda data_dict, output_dir: None, config)

# Test for merge_si
def test_merge_si_consistency():
    config = get_config()
    si_2018 = load_csv('si_2018.csv', config)
    si_2024 = load_csv('si_2024.csv', config)
    
    merged_df = merge_si()

    # Ensure the number of rows is correct (2018 + 2024 datasets should sum up)
    row_count_2018 = si_2018.shape[0]
    row_count_2024 = si_2024.shape[0]
    expected_total_rows = row_count_2018 + row_count_2024

    assert len(merged_df) == expected_total_rows, "Row count mismatch in merged service inventory dataset!"
    assert row_count_2018 > 1, "No data in si_2018!"
    assert row_count_2024 > 1, "No data in si_2024!"

# Test for merge_ss
def test_merge_ss_consistency():
    config = get_config()
    ss_2018 = load_csv('ss_2018.csv', config)
    ss_2024 = load_csv('ss_2024.csv', config)
    
    merged_df = merge_ss()

    # Ensure the number of rows is correct (2018 + 2024 datasets should sum up)
    row_count_2018 = ss_2018.shape[0]
    row_count_2024 = ss_2024.shape[0]
    expected_total_rows = row_count_2018 + row_count_2024

    assert len(merged_df) == expected_total_rows, "Row count mismatch in merged service service standard dataset!"
    assert row_count_2018 > 1, "No data in ss_2018!"
    assert row_count_2024 > 1, "No data in ss_2024!"
