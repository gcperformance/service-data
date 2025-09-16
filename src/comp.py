import pandas as pd




def compare(compare_dict):
    """
    Return a long-format DataFrame with:
      - per-field differences for common keys & columns
      - records that exist only in base or comp
      - fields (columns) that exist only in base or comp

    Columns:
      section            -> 'diffs' | 'records_only' | 'fields_only'
      side               -> 'base' | 'comp' | None (for diffs rows, side is None)
      key                -> the key value for diffs/records_only; NA for fields_only
      field              -> column name for diffs/fields_only; special label for records_only
      value_base         -> value in base (if applicable)
      value_comp         -> value in comp (if applicable)
      base_name, comp_name, key_name  -> metadata passthrough
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
        

    # Normalize: strip and replace all whitespace characters in strings with spaces
    def _strip_strings(df):
        obj_cols = df.select_dtypes(include='object').columns
        for c in obj_cols:
            df[c] = df[c].str.strip().str.replace(r"\s+", " ", regex=True)
        return df

    df_base = _strip_strings(df_base)
    df_comp = _strip_strings(df_comp)

    # Set index
    df_base = df_base.set_index(key_name, drop=True)
    df_comp = df_comp.set_index(key_name, drop=True)

    # Keys / records
    base_keys = pd.Index(df_base.index)
    comp_keys = pd.Index(df_comp.index)
    common_keys = base_keys.intersection(comp_keys)
    only_base_keys = base_keys.difference(comp_keys)
    only_comp_keys = comp_keys.difference(base_keys)

    # Columns (preserving base order)
    base_cols = pd.Index(df_base.columns)
    comp_cols = pd.Index(df_comp.columns)
    common_cols = base_cols.intersection(comp_cols)
    only_base_cols = base_cols.difference(comp_cols)
    only_comp_cols = comp_cols.difference(base_cols)

    # Align on common keys + cols
    base_common = df_base.loc[common_keys, common_cols]
    comp_common = df_comp.loc[common_keys, common_cols]

    # Main comparison function between aligned (common) dataframes
    # Compare the two aligned DataFrames field-by-field
    compared = base_common.compare(
        comp_common, 
        align_axis=1, 
        keep_shape=False,   # drop columns with no differences at all
        keep_equal=False,   # drop cells that are the same, even in diff columns
        result_names=('base_value', 'comp_value')  # label the two sides
    )

    # Reshape the comparison output into a tidy format
    diffs_long = (
        compared
        .melt(ignore_index=False)   # wide → long; stack diff values into rows
        .reset_index()              # bring the DataFrame index (keys) back as a column
        .rename(                    # give clearer names to auto-generated columns
            columns={key_name: "key", "variable_0": "field"}
        )
        .pivot(                     # pivot so base/comp values are side-by-side
            index=["key", "field"], 
            columns="variable_1",   # this holds 'base_value' or 'comp_value'
            values="value"
        )
        .reset_index()              # flatten back to normal columns
    )

    # Keep only rows where both base and comp values exist
    # (removes rows where one side was NaN and the other wasn’t)
    diffs_long = diffs_long.loc[
        diffs_long["base_value"].notna() & diffs_long["comp_value"].notna()
    ]

    # Try numeric conversion
    num_base = pd.to_numeric(diffs_long["base_value"], errors="coerce")
    num_comp = pd.to_numeric(diffs_long["comp_value"], errors="coerce")

    # Case 1: both values are numeric → compare numerically
    num_diff = (num_base != num_comp) & num_base.notna() & num_comp.notna()

    # Case 2: at least one value is non-numeric → fall back to string comparison
    non_numeric_mask = num_base.isna() | num_comp.isna()
    str_diff = (diffs_long["base_value"] != diffs_long["comp_value"]) & non_numeric_mask

    # Combine both cases
    diffs_long = diffs_long.loc[num_diff | str_diff]


    # Ignore results in fields for which the differences aren't important - 
    # the content is usually in the associated code
    ignored_fields = [
        'program_name_en', 
        'program_name_fr', 
        'org_name_variant'
    ]

    diffs_long = diffs_long.loc[~diffs_long['field'].isin(ignored_fields)]

    diffs_long["section"] = "diffs"
    diffs_long["side"] = None

    # Records only in one side
    records_only_base = pd.DataFrame({
        "section": "records_only",
        "side": "base",
        "key": only_base_keys,
        "field": f"record only in base ({base_name})",
        "base_value": only_base_keys.astype(object),
        "comp_value": pd.NA
    })

    records_only_comp = pd.DataFrame({
        "section": "records_only",
        "side": "comp",
        "key": only_comp_keys,
        "field": f"record only in comp ({comp_name})",
        "base_value": pd.NA,
        "comp_value": only_comp_keys.astype(object)
    })

    # Fields only in one side (no key)
    fields_only_base = pd.DataFrame({
        "section": "fields_only",
        "side": "base",
        "key": pd.NA,
        "field": only_base_cols.astype(object),
        "base_value": only_base_cols.astype(object),
        "comp_value": pd.NA
    })

    fields_only_comp = pd.DataFrame({
        "section": "fields_only",
        "side": "comp",
        "key": pd.NA,
        "field": only_comp_cols.astype(object),
        "base_value": pd.NA,
        "comp_value": only_comp_cols.astype(object)
    })

    out = pd.concat(
        [diffs_long, records_only_base, records_only_comp, fields_only_base, fields_only_comp],
        ignore_index=True
    )

    # Add metadata columns to help downstream writing/analysis
    out["base_name"] = base_name
    out["comp_name"] = comp_name
    out["key_name"] = key_name

    # Sorting: put sections in a friendly order, then by key/field
    cat = pd.CategoricalDtype(categories=["diffs", "records_only", "fields_only"], ordered=True)
    out["section"] = out["section"].astype(cat)
    out = out.sort_values(by=["section", "key", "field"], kind="stable").reset_index(drop=True)

    return out