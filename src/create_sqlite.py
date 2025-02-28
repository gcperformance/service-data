#!/usr/bin/env python3
"""
Script to create an SQLite database from CSV files.
The database will be created in the outputs directory.
"""

import os
import sqlite3
import pandas as pd
import csv

# Define the output path for the SQLite database
OUTPUT_DB_PATH = 'outputs/service_data.sqlite'

# Define the CSV files to be imported
CSV_FILES = {
    'si': 'outputs/si.csv',
    'ss': 'outputs/ss.csv',
    'service_fte_spending': 'outputs/indicators/service_fte_spending.csv',
    'si_vol': 'outputs/indicators/si_vol.csv',
    'sid_list': 'outputs/utils/sid_list.csv',
    'maf_all': 'outputs/indicators/maf_all.csv',
}

def create_database():
    """Create the SQLite database and import the CSV files."""
    # Remove the database file if it already exists
    if os.path.exists(OUTPUT_DB_PATH):
        os.remove(OUTPUT_DB_PATH)
    
    # Connect to the database
    conn = sqlite3.connect(OUTPUT_DB_PATH)
    cursor = conn.cursor()
    
    # Create tables for each CSV file
    for table_name, csv_path in CSV_FILES.items():
        print(f"Importing {csv_path} into table {table_name}...")
        
        # Read the CSV file with pandas
        df = pd.read_csv(csv_path, sep=';', quoting=csv.QUOTE_MINIMAL, 
                         encoding='utf-8', low_memory=False)
        
        # Write the dataframe to the SQLite database
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        
        print(f"Successfully imported {len(df)} rows into table {table_name}")
    
    # Create the junction tables for many-to-many relationships
    
    # Create fy_list table (junction table between si and maf_all)
    print("Creating fy_list junction table...")
    cursor.execute('''
    CREATE TABLE fy_list AS
    SELECT DISTINCT fiscal_yr
    FROM si
    ''')
    
    # Create org_id table (junction table between maf_all and sid_list)
    print("Creating org_id junction table...")
    cursor.execute('''
    CREATE TABLE org_id AS
    SELECT DISTINCT org_id
    FROM maf_all
    ''')
    
    # Create indexes to improve query performance
    print("Creating indexes...")
    
    # Indexes for si table
    cursor.execute('CREATE INDEX idx_si_service_id ON si(service_id)')
    cursor.execute('CREATE INDEX idx_si_fiscal_yr ON si(fiscal_yr)')
    cursor.execute('CREATE INDEX idx_si_org_id ON si(org_id)')
    cursor.execute('CREATE INDEX idx_si_fy_org_id_service_id ON si(fy_org_id_service_id)')
    
    # Indexes for ss table
    cursor.execute('CREATE INDEX idx_ss_service_id ON ss(service_id)')
    cursor.execute('CREATE INDEX idx_ss_fy_org_id_service_id ON ss(fy_org_id_service_id)')
    
    # Indexes for service_fte_spending table
    cursor.execute('CREATE INDEX idx_service_fte_spending_service_id ON service_fte_spending(service_id)')
    cursor.execute('CREATE INDEX idx_service_fte_spending_fiscal_yr ON service_fte_spending(fiscal_yr)')
    cursor.execute('CREATE INDEX idx_service_fte_spending_org_id ON service_fte_spending(org_id)')
    
    # Indexes for si_vol table
    cursor.execute('CREATE INDEX idx_si_vol_service_id ON si_vol(service_id)')
    cursor.execute('CREATE INDEX idx_si_vol_fiscal_yr ON si_vol(fiscal_yr)')
    cursor.execute('CREATE INDEX idx_si_vol_org_id ON si_vol(org_id)')
    
    # Indexes for sid_list table
    cursor.execute('CREATE INDEX idx_sid_list_service_id ON sid_list(service_id)')
    cursor.execute('CREATE INDEX idx_sid_list_org_id ON sid_list(org_id)')
    
    # Indexes for maf_all table
    cursor.execute('CREATE INDEX idx_maf_all_fiscal_yr ON maf_all(fiscal_yr)')
    cursor.execute('CREATE INDEX idx_maf_all_org_id ON maf_all(org_id)')
    
    # Indexes for junction tables
    cursor.execute('CREATE INDEX idx_fy_list_fiscal_yr ON fy_list(fiscal_yr)')
    cursor.execute('CREATE INDEX idx_org_id_org_id ON org_id(org_id)')
    
    # Create views to demonstrate the relationships
    print("Creating views...")
    
    # View for si and ss relationship (1 to many)
    cursor.execute('''
    CREATE VIEW view_si_ss AS
    SELECT 
        si.*, 
        ss.service_standard_id, 
        ss.service_standard_en, 
        ss.service_standard_fr,
        ss.type,
        ss.channel,
        ss.target_type,
        ss.target,
        ss.volume_meeting_target,
        ss.total_volume,
        ss.performance,
        ss.target_met
    FROM 
        si
    LEFT JOIN 
        ss ON si.fy_org_id_service_id = ss.fy_org_id_service_id
    ''')
    
    # View for si and service_fte_spending relationship (1 to many)
    cursor.execute('''
    CREATE VIEW view_si_fte_spending AS
    SELECT 
        si.*, 
        sfs.ftes,
        sfs.spending,
        sfs.planned_actual
    FROM 
        si
    LEFT JOIN 
        service_fte_spending sfs ON si.service_id = sfs.service_id AND si.fiscal_yr = sfs.fiscal_yr AND si.org_id = sfs.org_id
    ''')
    
    # View for si and si_vol relationship (1 to many)
    cursor.execute('''
    CREATE VIEW view_si_vol AS
    SELECT 
        si.*, 
        sv.channel as vol_channel,
        sv.volume
    FROM 
        si
    LEFT JOIN 
        si_vol sv ON si.service_id = sv.service_id AND si.fiscal_yr = sv.fiscal_yr AND si.org_id = sv.org_id
    ''')
    
    # View for si and sid_list relationship (many to 1)
    cursor.execute('''
    CREATE VIEW view_si_sid_list AS
    SELECT 
        si.*, 
        sil.fiscal_yr_first,
        sil.fiscal_yr_latest
    FROM 
        si
    LEFT JOIN 
        sid_list sil ON si.service_id = sil.service_id
    ''')
    
    # View for si and maf_all relationship (many to many through fy_list)
    cursor.execute('''
    CREATE VIEW view_si_maf_all AS
    SELECT 
        si.*, 
        ma.org_id as maf_org_id,
        ma.department_en as maf_department_en,
        ma.department_fr as maf_department_fr,
        ma.maf1_score,
        ma.maf2_score,
        ma.maf5_score,
        ma.maf6_score,
        ma.maf8_score
    FROM 
        si
    JOIN 
        fy_list fl ON si.fiscal_yr = fl.fiscal_yr
    JOIN 
        maf_all ma ON fl.fiscal_yr = ma.fiscal_yr AND si.org_id = ma.org_id
    ''')
    
    # View for maf_all and sid_list relationship (many to many through org_id)
    cursor.execute('''
    CREATE VIEW view_maf_all_sid_list AS
    SELECT 
        ma.*, 
        sil.service_id,
        sil.service_name_en,
        sil.service_name_fr,
        sil.fiscal_yr_first,
        sil.fiscal_yr_latest
    FROM 
        maf_all ma
    JOIN 
        org_id o ON ma.org_id = o.org_id
    JOIN 
        sid_list sil ON o.org_id = sil.org_id
    ''')
    
    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    
    print(f"Database created successfully at {OUTPUT_DB_PATH}")

if __name__ == "__main__":
    create_database() 