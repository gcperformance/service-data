import pandas as pd
from pathlib import Path

from src.export import export_to_csv

def main():
    # The following definitions and calls are meant to be very specific.
    # General comparison procedure to follow in other functions

    # Read in CSV files to be compared
    si = pd.read_csv(
        "./outputs/si.csv", 
        keep_default_na=False, 
        na_values='',
        delimiter=';',
        engine='python',
        skipfooter=2
    )

    snap_si = pd.read_csv(
        "./outputs/snapshots/2025-03-01/si.csv", 
        keep_default_na=False, 
        na_values='',
        delimiter=';',
        engine='python',
        skipfooter=2
    )

    ss = pd.read_csv(
        "./outputs/ss.csv", 
        keep_default_na=False, 
        na_values='',
        delimiter=';',
        engine='python',
        skipfooter=2
    )

    snap_ss = pd.read_csv(
        "./outputs/snapshots/2025-03-01/ss.csv", 
        keep_default_na=False, 
        na_values='',
        delimiter=';',
        engine='python',
        skipfooter=2
    )

    # Define dictionaries that contain the information needed to run the comparisons
    compare_si_vs_snap_si = {
        'df_base': si,
        'df_comp': snap_si,
        'base_name': 'si',
        'comp_name': 'snap_si',
        'key_name': 'fy_org_id_service_id'
    }

    compare_ss_vs_snap_ss = {
        'df_base': ss,
        'df_comp': snap_ss,
        'base_name': 'ss',
        'comp_name': 'snap_ss',
        'key_name': 'fy_org_id_service_id_std_id'
    }

    prep_comparison_file(compare_si_vs_snap_si)
    prep_comparison_file(compare_ss_vs_snap_ss)


def prep_comparison_file(compare_dict):
    """Logistics around generating a csv file with comparison results"""
    # Run comparison on objects in compare_dict
    df = compare(compare_dict)
    
    # Prepare file name using specifics from compare_dict
    base_name = compare_dict['base_name']
    comp_name = compare_dict['comp_name']

    filename = f"compare_{base_name}_vs_{comp_name}"
    output_filepath = Path(__file__).parent / "outputs" / "compare"

    data_dict={
        filename: df
    }

    config = {
        'snapshot_date': None
    }

    export_to_csv(data_dict, output_filepath, config)



def compare(compare_dict):
    """
    Compare two DataFrames: return differences and unmatched records.
    
    Args:
        df_base (pd.DataFrame): Baseline DataFrame to compare from.
        df_comp (pd.DataFrame): DataFrame to compare against the baseline.
        key_name (str): Column used as a unique identifier. Must be present in both DataFrames

    Returns:
        pd.DataFrame: Long-format DataFrame with differing fields and unmatched records.
    """
    
    df_base = compare_dict['df_base'].copy()
    df_comp = compare_dict['df_comp'].copy()
    key_name = compare_dict['key_name']
    base_name = compare_dict['base_name']
    comp_name = compare_dict['comp_name']
    
    # Validation
    # For loop that works on tuples of *_name and df_*
    for name, df in ((base_name, df_base), (comp_name, df_comp)):
        # ensure key_name is a column in the dataframe
        if key_name not in df.columns:
            raise KeyError(f"'{key_name}' missing in {name}")
        
        # ensure there are no duplicate keys
        dups = df[key_name][df[key_name].duplicated()]
        if len(dups):
            raise ValueError(f"Duplicate keys in {name}: {dups.unique()[:5]}... (total {len(dups)})")
        
    # Normalize: trim strings;

    df_base = df_base.reset_index(drop=True)
    df_comp = df_comp.reset_index(drop=True)

    # Prepare series of keys for comparison
    base_keys = df_base[key_name]
    comp_keys = df_comp[key_name]

    # Set the key as index for easier row-wise comparison
    df_base.set_index(key_name, inplace=True)
    df_comp.set_index(key_name, inplace=True)

    # Identify which keys are common or unique between the two dataframes
    match_keys = pd.merge(base_keys, comp_keys, how='outer', indicator=True)
    common_keys = match_keys[match_keys['_merge'] == 'both'].iloc[:, 0]
    keys_only_in_base = match_keys[match_keys['_merge'] == 'left_only'].iloc[:, 0]
    keys_only_in_comp = match_keys[match_keys['_merge'] == 'right_only'].iloc[:, 0]

    # Identify which columns are common or unique between the two dataframes
    common_cols = list(set(df_base.columns) & set(df_comp.columns))
    cols_only_in_base = list(set(df_base.columns) - set(df_comp.columns))
    cols_only_in_comp = list(set(df_comp.columns) - set(df_base.columns))

    # Filter both DataFrames to only those with common keys
    df_base_common = df_base.loc[common_keys, common_cols]
    df_comp_common = df_comp.loc[common_keys, common_cols]

    # Set the name for the column that stores field names during the reshaping process
    var_name = 'field'

    # Compare values field-by-field, row-by-row after filling NaNs with 0
    diff_wide = df_base_common.fillna(0).ne(df_comp_common.fillna(0)).reset_index()
    diff = diff_wide.melt(
        id_vars=[key_name],
        var_name=var_name,
        value_vars=diff_wide.columns.drop(key_name)
    )
    # Filter for where values are different
    diff = diff[diff['value']].set_index([key_name, var_name])

    # Prepare long-format versions of base and comp DataFrames for comparison
    df_base_long = df_base_common.reset_index().melt(
        id_vars=[key_name],
        var_name=var_name,
        value_vars=df_base_common.columns
    ).set_index([key_name, var_name])

    df_comp_long = df_comp_common.reset_index().melt(
        id_vars=[key_name],
        var_name=var_name,
        value_vars=df_comp_common.columns
    ).set_index([key_name, var_name])

    # Merge differences with their respective base and comp values
    compare_result = diff.join(df_base_long, rsuffix=f'_{base_name}').join(df_comp_long, rsuffix=f'_{comp_name}')
    compare_result.drop(columns=['value'], inplace=True)  # Drop diff indicator
    compare_result.reset_index(inplace=True)

    # Add records that are only in one of the datasets
    records_only_in_base = pd.DataFrame({
        key_name: keys_only_in_base,
        var_name: f'record only in {base_name}',
        f'value_{base_name}': keys_only_in_base
    })

    records_only_in_comp = pd.DataFrame({
        key_name: keys_only_in_comp,
        var_name: f'record only in {comp_name}',
        f'value_{comp_name}': keys_only_in_comp
    })

    # Add fields that are only in one of the datasets
    fields_only_in_base = pd.DataFrame({
        key_name: cols_only_in_base,
        var_name: f'field only in {base_name}',
        f'value_{base_name}': cols_only_in_base
    })

    fields_only_in_comp = pd.DataFrame({
        key_name: cols_only_in_comp,
        var_name: f'field only in {comp_name}',
        f'value_{comp_name}': cols_only_in_comp
    })

    # Concatenate all results into a single DataFrame
    compare_result = pd.concat([
        compare_result, 
        records_only_in_base, 
        records_only_in_comp,
        fields_only_in_base,
        fields_only_in_comp
        ], ignore_index=True).sort_values(by=key_name)
    


    return compare_result


if __name__ == "__main__":
    main()


