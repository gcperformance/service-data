import pandas as pd
import json

from src.load import load_csv
from src.export import export_to_csv
from src.clean import standardize_column_names, clean_fiscal_yr

def dept_list(config):
    """
    Get a list of departments with their English and French names.
    """
    ifoi_en = load_csv('ifoi_en.csv', config, snapshot=False)
    ifoi_fr = load_csv('ifoi_fr.csv', config, snapshot=False)
    
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
    
    if not config['snapshot_date']:
        UTILS_DIR = config['utils_dir']
        export_to_csv(
            data_dict={'dept': dept},
            output_dir=UTILS_DIR,
            config=config
        )
    
    return dept
    

def sid_list(si, config):
    """
    Unique list of service IDs as reported in the latest fy
    """
    sid_list = si.loc[:,
        [
            'service_id', 
            'service_name_en', 
            'service_name_fr', 
            'fiscal_yr', 
            'department_en', 
            'department_fr', 
            'org_id',
            'service_scope'
        ]
    ]

    # Determine the first and last fiscal years in which the service was reported
    sid_latest_fy = sid_list.loc[sid_list.groupby('service_id')['fiscal_yr'].idxmax(), ['service_id', 'fiscal_yr']]
    sid_first_fy = sid_list.loc[sid_list.groupby('service_id')['fiscal_yr'].idxmin(), ['service_id', 'fiscal_yr']]
    
    # Merge these first/last fiscal years back into list
    sid_list = sid_list.merge(sid_first_fy, on='service_id', suffixes=('', '_first'))
    sid_list = sid_list.merge(sid_latest_fy, on='service_id', suffixes=('', '_latest'))

    # Ignore all records that aren't from the latest fiscal year
    sid_list = sid_list[sid_list['fiscal_yr'] == sid_list['fiscal_yr_latest']]

    # Boolean field to identify which services are in scope for typical reporting
    sid_list['service_scope_ext_or_ent'] = (
        (sid_list['service_scope'].str.contains('EXTERN', regex=True)) |
        (sid_list['service_scope'].str.contains('ENTERPRISE', regex=True))
    )

    # Remove ambiguous or irrelevant fields
    sid_list = sid_list.drop(columns=['fiscal_yr', 'service_scope'])
    
    UTILS_DIR = config['utils_dir']
    export_to_csv(
        data_dict={'sid_list': sid_list},
        output_dir=UTILS_DIR,
        config=config
    )

    # return sid_list


def build_drf(config):
    """
    Load and clean DRF data (i.e. RBPO)
    Take from snapshot input if the snapshot argument is supplied
    """
    snapshot_bool = bool(config['snapshot_date'])
    
    drf = load_csv('rbpo.csv', config, snapshot_bool)
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

    # Return years to fiscal year YYYY-YYYY format
    drf['report_yr'] = (drf['report_yr']-1).apply(str) +"-"+ (drf['report_yr']).apply(str)
    drf['measure_yr'] = (drf['measure_yr']-1).apply(str) +"-"+ (drf['measure_yr']).apply(str)
    drf['si_link_yr'] = (drf['si_link_yr']-1).apply(str) +"-"+ (drf['si_link_yr']).apply(str)

    UTILS_DIR = config['utils_dir']
    export_to_csv(
        data_dict={'drf': drf},
        output_dir=UTILS_DIR,
        config=config
    )

    return drf

def copy_raw_to_utils(config):
    ifoi_en = load_csv('ifoi_en.csv', config, snapshot=False)
    ifoi_fr = load_csv('ifoi_fr.csv', config, snapshot=False)
    org_var = load_csv('org_var.csv', config, snapshot=False)

    # Set first column (OrgID) as index, drop the column from the actual table, add the en/fr suffix
    ifoi_en = ifoi_en.set_index(ifoi_en.columns[0], drop=True).add_suffix('_en')
    ifoi_fr = ifoi_fr.set_index(ifoi_fr.columns[0], drop=True).add_suffix('_fr')

    # Merge the two ifoi's together. concat works because the index is the same
    ifoi = pd.concat([ifoi_en, ifoi_fr], axis=1)
    
    # Extract column lists
    en_cols = ifoi_en.columns.tolist()
    fr_cols = ifoi_fr.columns.tolist()
    
    # Interleave them by index
    merged_cols = [col for pair in zip(en_cols, fr_cols) for col in pair]
    
    # Apply new column order, reset the index to make org_id reappear
    ifoi = standardize_column_names(ifoi[merged_cols].reset_index())

    utils_file_dict = {
        'ifoi':ifoi,
        'org_var':org_var
    }

    for key in utils_file_dict.keys():
        utils_file_dict[key] = standardize_column_names(utils_file_dict[key]) 
    
    UTILS_DIR = config['utils_dir']
    export_to_csv(
        data_dict=utils_file_dict,
        output_dir=UTILS_DIR,
        config=config
    )

def build_data_dictionary(config):
    """Builds a structured data dictionary from a JSON file, processes nested data, 
    renames columns, standardizes names, and exports to CSV."""
    
    INPUT_DIR = config['input_dir']
    file_path =  INPUT_DIR / 'service_data_dict.json'
    
    # Load JSON file into a dictionary
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Initial normalization of json file
    data_dict = pd.json_normalize(data)

    # Explode and normalize the 'resources' portion
    data_dict = data_dict.explode('resources').reset_index(drop=True)
    data_dict = pd.json_normalize(data_dict['resources'])

    # Explode the 'fields' portion
    data_dict = data_dict.explode('fields').reset_index(drop=True)

    # Tie the resource fields to the 'fields portion'
    data_dict_fields = pd.json_normalize(data_dict['fields'])
    data_dict = data_dict.merge(data_dict_fields, left_index=True, right_index=True)
    
    # List of field names and details about their type and requirements
    dd_field_names = data_dict.loc[:, ~data_dict.columns.str.startswith('choices.')].drop(columns=['fields'])
    
    # List of translated code labels for fields with restricted input choices
    dd_choices = data_dict.melt(
        id_vars = ['resource_name', 'title.en', 'title.fr','id','label.en', 'label.fr'], 
        value_vars=[col for col in data_dict.columns if col.startswith('choices.')]
    )
    
    dd_choices.dropna(subset=['value'], inplace=True)
    
    dd_choices['code'] = dd_choices['variable'].str.split('.').str[1]
    dd_choices['en_fr'] = dd_choices['variable'].str.split('.').str[2]
    dd_choices = dd_choices.dropna(subset='en_fr')
    
    
    dd_choices = dd_choices.pivot(index=['resource_name', 'id', 'code'], columns='en_fr', values='value')
    dd_choices = dd_choices.reset_index()

    # Keep dd_choices tidy by removing program_id and splitting into its own file (dd_program)
    dd_program = dd_choices.loc[dd_choices['id'] == 'program_id']
    dd_choices = dd_choices.loc[dd_choices['id'] != 'program_id']
    
    # Standardize column names
    dd_field_names = standardize_column_names(dd_field_names)
    dd_program = standardize_column_names(dd_program)
    dd_choices = standardize_column_names(dd_choices)

    data_dictionary_file_dict = {
        'dd_field_names': dd_field_names,
        'dd_program': dd_program,
        'dd_choices': dd_choices
    }

    # Export to CSV

    UTILS_DIR = config['utils_dir']
    export_to_csv(
        data_dict=data_dictionary_file_dict, 
        output_dir=UTILS_DIR,
        config=config
    )
    