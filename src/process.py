import pandas as pd
import numpy as np
from pathlib import Path

from src.clean import clean_percentage, normalize_string, standardize_column_names, clean_fiscal_yr
from src.load import load_csv_from_raw
from src.export import export_to_csv
from src.utils import build_drf

INDICATORS_DIR = Path(__file__).parent.parent / "outputs" / "indicators"
UTILS_DIR = Path(__file__).parent.parent / "outputs" / "utils"

def process_files(si, ss):
    # === SPECIFIC INDICATOR TABLES ===   
    # =================================
    # si_vol: Applications by service
    # Given a service, what is the volume of interactions (applications) by channel and fiscal year?

    # List of columns that contain application / interaction volumes
    # These also represent the channel through which the interaction took place
    app_cols = [
        'num_applications_by_phone', 
        'num_applications_online', 
        'num_applications_in_person', 
        'num_applications_by_mail', 
        'num_applications_by_email', 
        'num_applications_by_fax', 
        'num_applications_by_other'
    ]

    # Unpivot (i.e. melt) application volume columnns
    si_vol = pd.melt(si, id_vars=['fiscal_yr', 'service_id'], value_vars=app_cols, var_name='channel', value_name='volume')
    
    # remove "_applications" from the channel column to get a clean channel name
    si_vol['channel'] = si_vol['channel'].str.replace('num_applications_', '', regex=True).str.replace('by_', '', regex=True)
    
    # remove 'NaN', 'ND' values in volume
    si_vol = si_vol.dropna(subset=['volume'])
    si_vol = si_vol[si_vol['volume'] != 'ND']
    si_vol = si_vol[si_vol['volume'] != 'NA']
    
    # only take entries where the volume is > 0
    si_vol['volume'] = pd.to_numeric(si_vol['volume'])
    si_vol = si_vol[si_vol['volume'] > 0]
    
    # =================================
    # si_oip: Online interaction points
    # Given a service, which online interaction points are activated as of the latest fiscal year those services reported?

    # List of columns that represent online interaction point activation
    oip_cols = [
        'os_account_registration', 
        'os_authentication', 
        'os_application', 
        'os_decision', 
        'os_issuance', 
        'os_issue_resolution_feedback', 
    ]
       
    # Unpivot (i.e. melt) online interaction point columns
    si_oip = pd.melt(si, id_vars=['fiscal_yr', 'service_id'], value_vars=oip_cols, var_name='online_interaction_point', value_name='activation')
    
    # Add a column to indicate the sort position of the online interaction point
    si_oip['online_interaction_point_sort'] = si_oip['online_interaction_point'].apply(lambda x: oip_cols.index(x)+1)
    
    # Remove "os_" from the online interaction point column to get a clean name
    si_oip['online_interaction_point'] = si_oip['online_interaction_point'].str.replace('os_', '')
    
    # Dump old years, only take latest year
    si_oip = si_oip.loc[si_oip.groupby(['service_id', 'online_interaction_point'])['fiscal_yr'].idxmax()].sort_values(by=['service_id', 'online_interaction_point_sort'])
    
    # =================================
    # ss_tml_perf_vol: Timeliness service standard performance
    # Given a service, what is the volume of interactions that met the target vs not, by fiscal year?
    
    # Filter the DataFrame for rows where (service standard type) 'type' is 'TML' (Timeliness), group by 'fiscal_yr' 
    # and 'service_id', sum the 'volume_meeting_target' and 'total_volume' columns, and reset the index.
    ss_tml_perf_vol = ss.loc[ss['type'] == 'TML'].groupby(['fiscal_yr', 'service_id'])[['volume_meeting_target', 'total_volume']].sum().reset_index()
    
    ss_tml_perf_vol['total_volume'] = pd.to_numeric(ss_tml_perf_vol['total_volume'], errors='coerce').fillna(0)
    ss_tml_perf_vol['volume_meeting_target'] = pd.to_numeric(ss_tml_perf_vol['volume_meeting_target'], errors='coerce').fillna(0)
    ss_tml_perf_vol['volume_not_meeting_target'] = ss_tml_perf_vol['total_volume']-ss_tml_perf_vol['volume_meeting_target']

    # =================================
    # si_fy_service_count: Total number of services by fiscal year
    # Given a fiscal year, how many services were reported?    
    si_fy_service_count = si.groupby(['fiscal_yr'])['service_id'].count().reset_index()
    si_fy_service_count.rename(columns={'service_id': 'total_services'}, inplace=True)
    
    # =================================
    # si_fy_interaction_sum: Total number of service interactions
    # Given a fiscal year, how many service interactions were reported?
    si_fy_interaction_sum = si_vol.groupby(['fiscal_yr'])['volume'].sum().reset_index()

    # =================================
    # si_reviews: Service reviews 
    # What fraction of services have met the requirement to be reviewed in the past 5 years?
    si_reviews = si.loc[:,['fiscal_yr', 'service_id', 'org_id', 'last_service_review', 'last_service_improvement']]
    
    si_reviews['report_yr'] = pd.to_numeric(si_reviews['fiscal_yr'].str.split('-').str[1], errors='coerce').astype(int)
    
    si_reviews['last_service_review_yr'] = pd.to_numeric(si_reviews['last_service_review'].str.split('-').str[1], errors='coerce')
    si_reviews['yrs_since_last_service_review'] = si_reviews['report_yr']-si_reviews['last_service_review_yr']
    si_reviews['last_service_review_within_5_yrs'] = si_reviews['yrs_since_last_service_review'] <= 5
    
    si_reviews['last_service_improvement_yr'] = pd.to_numeric(si_reviews['last_service_improvement'].str.split('-').str[1], errors='coerce')
    si_reviews['yrs_since_last_service_improvement'] = si_reviews['report_yr']-si_reviews['last_service_improvement_yr']
    si_reviews['last_service_improvement_within_5_yrs'] = si_reviews['yrs_since_last_service_improvement'] <= 5
    
    si_reviews = si_reviews.groupby(['fiscal_yr']).agg(
        total_services = ('service_id', 'count'),
        services_reviewed_in_past_5_yrs = ('last_service_review_within_5_yrs', 'sum'),
        services_improved_in_past_5_yrs = ('last_service_improvement_within_5_yrs', 'sum')
        ).reset_index()

    
    # === MAF INDICATORS ===
    # References to methodology can be found here
    # https://www.canada.ca/en/treasury-board-secretariat/services/management-accountability-framework/maf-methodologies/2022-2023-im-it.html#toc-1
    
    # Setting up the score bins and corresponding results for use with pd.cut
    score_bins = [0, 50, 80, 101]
    score_results = ['low', 'medium', 'high']

    # =================================
    # MAF Question 1: Existence of service standards
    # As service standards are required under the Policy on Service and Digital, what is the percentage of services that have service standards?
    
    maf1 = si.loc[:, ['fiscal_yr', 'service_id', 'department_en','department_fr', 'org_id']]
    maf1['service_std_tf'] = si[['fiscal_yr', 'service_id']].isin(ss[['fiscal_yr', 'service_id']].to_dict(orient='list')).all(axis=1)
    
    maf1_num = maf1.groupby(['fiscal_yr', 'department_en','department_fr', 'org_id'])['service_id'].count().reset_index()
    maf1_denom = maf1.groupby(['fiscal_yr', 'department_en','department_fr','org_id'])['service_std_tf'].sum().reset_index()
    
    maf1 = pd.merge(
        maf1_num,
        maf1_denom,
        on=['fiscal_yr', 'department_en','department_fr', 'org_id'],
        how='left'
    ).rename(columns={'service_id':'service_count', 'service_std_tf':'service_with_std_count'})
    
    maf1['maf1_score'] = (maf1['service_with_std_count']/maf1['service_count'])*100
    # maf1['maf1_result'] = pd.cut(maf1['maf1_score'], bins=score_bins, labels=score_results, right=False)

    # =================================
    # MAF Question 2: Service standard targets
    # What is the percentage of service standards that met their target?
    
    maf2 = ss.loc[:, ['fiscal_yr', 'service_standard_id', 'department_en','department_fr', 'org_id', 'target_met']].dropna()
    
    maf2_num = maf2[maf2['target_met']=='Y'].groupby(['fiscal_yr', 'department_en','department_fr', 'org_id'])['service_standard_id'].count().reset_index()
    maf2_denom = maf2.groupby(['fiscal_yr', 'department_en','department_fr', 'org_id'])['service_standard_id'].count().reset_index()
    
    maf2 = pd.merge(
        maf2_num,
        maf2_denom,
        suffixes=['_met','_total'],
        on=['fiscal_yr', 'department_en','department_fr', 'org_id'],
        how='left'
    )
    
    maf2['maf2_score'] = (maf2['service_standard_id_met']/maf2['service_standard_id_total'])*100
    # maf2['maf2_result'] = pd.cut(maf2['maf2_score'], bins=score_bins, labels=score_results, right=False)
    
    # =================================
    # MAF Question 3: Real-time performance for service standards
    # As real-time performance reporting is required under the Directive on Service and Digital, what is the extent to which real-time performance reporting for services is published?
    # Real-time URL data is unreliable

    # =================================
    # MAF Question 4: Service standards reviews
    # What is the percentage of service standards which have been reviewed?
    # GCSS review field is no longer being collected as of 2023-24 dataset

    # =================================
    # MAF Question 5: Online end-to-end
    # As online end-to-end availability of services is required under the Policy on Service and Digital, what is the percentage of applicable services that can be completed online end-to-end?
    oip_cols = [
        'os_account_registration', 
        'os_authentication', 
        'os_application', 
        'os_decision', 
        'os_issuance', 
        'os_issue_resolution_feedback', 
    ]
    
    # Melt the DataFrame
    maf5 = pd.melt(si, id_vars=['fiscal_yr', 'service_id', 'department_en','department_fr', 'org_id'], value_vars=oip_cols, var_name='online_interaction_point', value_name='activation')
    
    # Create boolean columns for activation states
    maf5['activation_y'] = (maf5['activation'] == 'Y')
    maf5['activation_n'] = (maf5['activation'] == 'N')
    maf5['activation_na'] = (maf5['activation'] == 'NA')
    
    # Group by and sum the activation columns
    maf5 = maf5.groupby(['fiscal_yr', 'department_en','department_fr', 'org_id', 'service_id'])[['activation_y', 'activation_n', 'activation_na']].sum().reset_index()
    
    # Determine conditions for online_e2e
    conditions = [
        (maf5['activation_na'] == 6),  # All interaction points are NaN
        (maf5['activation_n'] > 0)      # Some interaction points are 'N'
    ]
    choices = [None, False]
    
    maf5['online_e2e'] = np.select(conditions, choices, default=True).astype(bool)
    
    # remove all Nan/Nones
    maf5 = maf5.dropna(subset=['online_e2e'])
    
    # Determine department-level counts for online e2e services and all services
    maf5 = maf5.groupby(['fiscal_yr', 'department_en','department_fr', 'org_id']).agg(
        online_e2e_count=('online_e2e', 'sum'), # this is wizardry to me... still not sure what is happening
        service_count=('service_id', 'nunique')
    ).reset_index()
    
    # Determine score and associated result
    maf5['maf5_score'] = (maf5['online_e2e_count']/maf5['service_count'])*100
    # maf5['maf5_result'] = pd.cut(maf5['maf5_score'], bins=score_bins, labels=score_results, right=False)
    
    # =================================
    # MAF Question 6: Online client interaction points
    # As online end-to-end availability of services is required under the Policy on Service and Digital, what is the percentage of client interaction points that are available online for services?
    oip_cols = [
        'os_account_registration', 
        'os_authentication', 
        'os_application', 
        'os_decision', 
        'os_issuance', 
        'os_issue_resolution_feedback', 
    ]
    
    # Melt the DataFrame
    maf6 = pd.melt(si, id_vars=['fiscal_yr', 'service_id', 'department_en','department_fr', 'org_id'], value_vars=oip_cols, var_name='online_interaction_point', value_name='activation').dropna()
    
    maf6['activation'] = (maf6['activation'] == 'Y')
    
    maf6 = maf6.groupby(['fiscal_yr', 'department_en','department_fr', 'org_id']).agg(
        activated_point_count=('activation', 'sum'), # this is wizardry to me... still not sure what is happening
        point_count=('service_id', 'count')
    ).reset_index()
    
    # Determine score and associated result
    maf6['maf6_score'] = (maf6['activated_point_count']/maf6['point_count'])*100
    # maf6['maf6_result'] = pd.cut(maf6['maf6_score'], bins=score_bins, labels=score_results, right=False)
    
    # =================================
    # MAF Question 7: ICT Accessibility
    # As accessibility is required under the Policy on Service and Digital, what is the percentage of services available online that have been assessed for ICT accessibility?
    # Accessibility data from the service inventory is of poor quality, and we are no longer collecting it

    # =================================
    # MAF Question 8: Client feedback
    # As ensuring client feedback is used to inform continuous improvement of services is a requirement under the Directive on Service and Digital, what is the percentage of services which have used client feedback to improve services in the last year?
    
    maf8 = si.loc[:,['fiscal_yr', 'service_id', 'org_id', 'department_en','department_fr', 'last_service_review', 'last_service_improvement']]
    
    maf8['report_yr'] = pd.to_numeric(maf8['fiscal_yr'].str.split('-').str[1], errors='coerce').astype(int)
    maf8['last_service_improvement_yr'] = pd.to_numeric(maf8['last_service_improvement'].str.split('-').str[1], errors='coerce')
    
    maf8['yrs_since_last_service_improvement'] = maf8['report_yr']-maf8['last_service_improvement_yr']
    maf8['last_service_improvement_within_1_yr'] = maf8['yrs_since_last_service_improvement'] <= 1
    
    maf8 = maf8.groupby(['fiscal_yr', 'department_en', 'org_id']).agg(
        improved_services_count=('last_service_improvement_within_1_yr', 'sum'),
        service_count=('service_id', 'nunique')
    ).reset_index()
    
    # Determine score and associated result
    maf8['maf8_score'] = (maf8['improved_services_count']/maf8['service_count'])*100
    # maf8['maf8_result'] = pd.cut(maf8['maf8_score'], bins=score_bins, labels=score_results, right=False)

    
    # === SPENDING & FTEs BY PROGRAM ===
    # Load DRF data from utils (i.e. RBPO)
    drf = build_drf()

    # =================================
    # service_fte_spending: FTEs and spending by programs delivering services
    si_drf = si.loc[:, ['service_id', 'fiscal_yr', 'program_id']]
    si_drf = si_drf.explode('program_id')
    si_drf['si_yr'] = si_drf['fiscal_yr'].str.split('-').str[1].astype(int)
    si_drf = si_drf[si_drf['program_id'].notna()]
    
    service_fte_spending = pd.merge(
        si_drf, 
        drf, 
        how='left', 
        left_on=['si_yr', 'program_id'], 
        right_on=['si_link_yr', 'program_id']
    )
       
    # === EXPORT DATAFRAMES ===
    indicator_exports = {
        "si_vol": si_vol,
        "si_oip": si_oip,
        "ss_tml_perf_vol": ss_tml_perf_vol,
        "si_fy_interaction_sum": si_fy_interaction_sum,
        "si_fy_service_count": si_fy_service_count,
        "si_reviews": si_reviews,
        "service_fte_spending": service_fte_spending,
        "maf1": maf1,
        "maf2": maf2,
        "maf5": maf5,
        "maf6": maf6,
        "maf8": maf8,
    }
    
    export_to_csv(
        data_dict=indicator_exports,
        output_dir=INDICATORS_DIR
    )
