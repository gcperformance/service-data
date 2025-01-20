import re
import numpy as np

def clean_percentage(value):
    """Normalize percentages to 0-1 scale."""
    try:
        numeric_value = float(str(value).replace('%', '').strip())
        return numeric_value / 100
    except (ValueError, TypeError):
        return None

def split_and_uppercase_to_sorted_string(value):
    return ', '.join(sorted(val.replace(' ','').upper() for val in value.split(',')))
    
def normalize_string(s):
    """Clean and normalize a string."""
    s = re.sub(r'[^A-Za-z0-9]', '', s)  # Remove non-alphanumeric characters
    return s.upper()
