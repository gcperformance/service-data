import re
import numpy as np

def clean_percentage(value):
    """Normalize percentages to 0-1 scale."""
    try:
        numeric_value = float(str(value).replace('%', '').strip())
        return numeric_value / 100
    except (ValueError, TypeError):
        return None

def clean_fiscal_yr(yr):
    """Convert fiscal years to XXXX-YYYY format"""
    # Dictionary-based simple replacements
    fy_cleanup = {'FY ': '', '/': '-'}
    for old, new in fy_cleanup.items():
        yr = yr.replace(old, new)

    # Regex transformation for fiscal years (XXXX-YY → XXXX-YYYY)
    yr = re.sub(
        r"(\d{4})-\d{2}", 
        lambda m: f"{m.group(1)}-{int(m.group(1)) + 1}",
        yr
    )

    return yr

def split_and_uppercase_to_sorted_string(s):
    return ', '.join(sorted(val.replace(' ','').upper() for val in s.split(',')))
    
def normalize_string(s):
    """Clean and normalize a string."""
    s = re.sub(r'[^A-Za-z0-9]', '', s)  # Remove non-alphanumeric characters
    return s.upper()

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
        'programid': 'program_id',
        'fy_ef': 'fiscal_yr'
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
