import pandas as pd
import numpy as np

from src.export import export_to_csv
from src.utils import build_drf, sid_list

def process_files(si, ss, config):
    OUTPUT_DIR = config['output_dir']
    INDICATORS_DIR = config['indicators_dir']
    
    sid_list(si, config)

    # === RE-SCOPE SERVICE INVENTORY ===
    # Only include external or enterprise services in all indicators and analysis
    # Filter out NaN and False values from 'service_scope_ext_or_ent'
    si = si.loc[si['service_scope_ext_or_ent'] == True]
    
    # Set index for `si`
    si = si.set_index(['fiscal_yr', 'org_id', 'service_id'])
    
    # Merge `ss` with `si` using left join and keep only matching rows
    ss = ss.set_index(['fiscal_yr', 'org_id', 'service_id']).merge(
        si[['service_scope_ext_or_ent']],  # Ensure only the necessary column is merged
        how='left',
        left_index=True,
        right_index=True
    )
    
    # Filter out NaN and False values from 'service_scope_ext_or_ent'
    ss = ss.loc[ss['service_scope_ext_or_ent'] == True]
    ss = ss.drop(columns=['service_scope_ext_or_ent']).reset_index()

    # Reset the index for si, drop the filtering column from the final si
    si = si.drop(columns=['service_scope_ext_or_ent']).reset_index()

    output_exports = {
        "si": si,
        "ss": ss,
    }

    export_to_csv(
        data_dict=output_exports,
        output_dir=OUTPUT_DIR,
        config=config
    )
    
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
    si_vol = pd.melt(
        si, 
        id_vars=['fiscal_yr','org_id', 'service_id'], 
        var_name='channel',
        value_vars=app_cols,
        value_name='volume'
    )
    
    # remove "_applications" from the channel column to get a clean channel name
    si_vol['channel'] = (
        si_vol['channel']
        .str.replace('num_applications_', '', regex=True)
        .str.replace('by_', '', regex=True)
    )

    
    # remove 'NaN', 'ND' values in volume
    si_vol = (
        si_vol
        .dropna(subset=['volume'])
        .loc[~si_vol['volume'].isin(['ND', 'NA'])]
    )
    
    # only take entries where the volume is > 0
    si_vol['volume'] = pd.to_numeric(si_vol['volume'], errors='coerce')
    si_vol = si_vol[si_vol['volume'] > 0]
    
    # =================================
    # si_oip: Online interaction points
    # Given a service, which online interaction points are activated by fiscal year for those services reported?

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
    si_oip = pd.melt(
        si, 
        id_vars=['fiscal_yr', 'org_id', 'service_id', 'fy_org_id_service_id'],
        var_name='online_interaction_point', 
        value_vars=oip_cols, 
        value_name='activation')
    
    # Add a column to indicate the sort position of the online interaction point
    si_oip['online_interaction_point_sort'] = si_oip['online_interaction_point'].apply(lambda x: oip_cols.index(x)+1)
    
    # Remove "os_" from the online interaction point column to get a clean name
    si_oip['online_interaction_point'] = si_oip['online_interaction_point'].str.replace('os_', '')

    # Commenting this out for now. It is more useful to have all the oip statuses for all yrs
    # Dump old years, only take latest year
    # si_oip = si_oip.loc[si_oip.groupby(['service_id', 'online_interaction_point'])['fiscal_yr'].idxmax()].sort_values(by=['service_id', 'online_interaction_point_sort'])

    # =================================
    # ss_tml_perf_vol: Timeliness service standard performance
    # Given a service, what is the volume of interactions that met the target vs not, by channel and fiscal year?
    
    # Filter for 'TML' type and aggregate volume-related columns by service and channel
    ss_tml_perf_vol = (
        ss.loc[ss['type'] == 'TML']
        .groupby(['fiscal_yr', 'org_id', 'service_id', 'channel']).agg(
            volume_meeting_target = ('volume_meeting_target', 'sum'),
            total_volume = ('total_volume', 'sum')
        ).reset_index()
    )
    
    # Convert volume columns to numeric and fill missing values with 0
    ss_tml_perf_vol[['total_volume', 'volume_meeting_target']] = (
        ss_tml_perf_vol[['total_volume', 'volume_meeting_target']]
        .apply(pd.to_numeric, errors='coerce')
        .fillna(0)
    )
    
    # Calculate the volume that did not meet the target
    ss_tml_perf_vol['volume_not_meeting_target'] = (
        ss_tml_perf_vol['total_volume'] - ss_tml_perf_vol['volume_meeting_target']
    )

    # =================================
    # si_fy_service_count: Total number of services by fiscal year
    # Given a fiscal year, how many services were reported? This is included in other tables now
    # si_fy_service_count = si.groupby(['fiscal_yr'])['service_id'].count().reset_index()
    # si_fy_service_count.rename(columns={'service_id': 'total_services'}, inplace=True)
    
    # =================================
    # si_fy_interaction_sum: Total number of service interactions
    # Given a fiscal year, how many service interactions were reported? This is included in other tables now
    # si_fy_interaction_sum = si_vol.groupby(['fiscal_yr'])['volume'].sum().reset_index()

    # =================================
    # si_reviews: Service reviews 
    # What fraction of services have met the requirement to be reviewed in the past 5 years?
    si_reviews = si.loc[:,['fiscal_yr','org_id','service_id', 'last_service_review', 'last_service_improvement']]
    
    si_reviews['report_yr'] = pd.to_numeric(si_reviews['fiscal_yr'].str.split('-').str[1], errors='coerce').astype(int)
    
    si_reviews['last_service_review_yr'] = pd.to_numeric(si_reviews['last_service_review'].str.split('-').str[1], errors='coerce')
    si_reviews['yrs_since_last_service_review'] = si_reviews['report_yr']-si_reviews['last_service_review_yr']
    si_reviews['last_service_review_within_5_yrs'] = si_reviews['yrs_since_last_service_review'] <= 5
    
    si_reviews['last_service_improvement_yr'] = pd.to_numeric(si_reviews['last_service_improvement'].str.split('-').str[1], errors='coerce')
    si_reviews['yrs_since_last_service_improvement'] = si_reviews['report_yr']-si_reviews['last_service_improvement_yr']
    si_reviews['last_service_improvement_within_5_yrs'] = si_reviews['yrs_since_last_service_improvement'] <= 5
    
    si_reviews = si_reviews.groupby(['fiscal_yr', 'org_id']).agg(
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

    # Select relevant columns from service inventory
    maf1 = si.loc[:, ['fiscal_yr', 'service_id', 'department_en','department_fr', 'org_id']]

    # Deduplicate service standards to prevent one-to-many expansion
    ss_unique = ss[['fiscal_yr', 'service_id']].drop_duplicates()
    
    # Determine whether each service has a standard by checking for existence in 'service standards'
    # Merge with 'ss' to check if (fiscal_yr, service_id) exists
    maf1 = maf1.merge(
        ss_unique,  # Use de-duplicated version to check 
        on=['fiscal_yr', 'service_id'],  # Merge on fiscal year and service ID
        how='left',  # Keep all 'maf1' records, add matches from 'ss'
        indicator=True  # Adds a column "_merge" to show if a match was found
    )
    
    # Create boolean column: True if the service exists in 'ss', otherwise False
    maf1['service_std_tf'] = maf1['_merge'] == 'both'
    
    # Drop the '_merge' column (no longer needed)
    maf1 = maf1.drop(columns=['_merge'])
    
    # Group by department and fiscal year, counting services with and without standards
    maf1 = maf1.groupby(['fiscal_yr', 'department_en', 'department_fr', 'org_id']).agg(
        service_with_std_count=('service_std_tf', 'sum'),  # Count services that have standards (True = 1)
        service_count_maf1=('service_id', 'count')  # Count all services
    ).reset_index()
    
    maf1['maf1_score'] = (maf1['service_with_std_count']/maf1['service_count_maf1'])*100
    # maf1['maf1_result'] = pd.cut(maf1['maf1_score'], bins=score_bins, labels=score_results, right=False)

    # =================================
    # MAF Question 2: Service standard targets
    # What is the percentage of service standards that met their target?
    
    # Select relevant columns and drop rows with missing values
    maf2 = ss.loc[:, ['fiscal_yr', 'service_standard_id', 'department_en', 'department_fr', 'org_id', 'target_met']].dropna()

    maf2['service_standard_met'] = maf2['target_met'] == 'Y'
    maf2['service_standard_count'] = maf2['target_met'].isin(['Y', 'N'])
    
    maf2 = maf2.groupby(['fiscal_yr', 'department_en', 'department_fr', 'org_id']).agg(
        service_standard_met=('service_standard_met', 'sum'),
        service_standard_count=('service_standard_count', 'sum')
    ).reset_index()

    maf2['maf2_score'] = (maf2['service_standard_met']/maf2['service_standard_count'])*100
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
    maf5 = pd.melt(
        si, 
        id_vars=['fiscal_yr', 'service_id', 'department_en','department_fr', 'org_id'], 
        value_vars=oip_cols, 
        var_name='online_interaction_point', 
        value_name='activation')
    
    # Create boolean columns for activation states
    maf5['activation_y'] = (maf5['activation'] == 'Y')
    maf5['activation_n'] = (maf5['activation'] == 'N')
    maf5['activation_na'] = (maf5['activation'] == 'NA')
    
    # Group by and sum the activation columns
    maf5 = maf5.groupby(['fiscal_yr', 'department_en', 'department_fr', 'org_id', 'service_id']).agg(
        activation_y=('activation_y', 'sum'),
        activation_n=('activation_n', 'sum'),
        activation_na=('activation_na', 'sum')
    ).reset_index()

    # Determine conditions for online_e2e
    conditions = [
        (maf5['activation_na'] == 6),  # All interaction points are NaN
        (maf5['activation_n'] > 0)      # Some interaction points are 'N'
    ]
    choices = [None, False]
    
    maf5['online_e2e'] = np.select(conditions, choices, default=True).astype(bool)
    
    # Remove all NaN/Nones
    maf5 = maf5.dropna(subset=['online_e2e'])
    
    # Determine department-level counts for online e2e services and all services
    maf5 = maf5.groupby(['fiscal_yr', 'department_en','department_fr', 'org_id']).agg(
        online_e2e_count=('online_e2e', 'sum'),
        service_count_maf5=('service_id', 'nunique')
    ).reset_index()
    
    # Determine score and associated result
    maf5['maf5_score'] = (maf5['online_e2e_count']/maf5['service_count_maf5'])*100
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
    maf6 = pd.melt(
        si, 
        id_vars=['fiscal_yr', 'service_id', 'department_en','department_fr', 'org_id'], 
        value_vars=oip_cols, 
        var_name='online_interaction_point', 
        value_name='activation')

    # Exclude points that are not applicable or blank
    maf6 = maf6.loc[maf6['activation'].isin(['Y','N'])]

    maf6['activation'] = (maf6['activation'] == 'Y')
    
    maf6 = maf6.groupby(['fiscal_yr', 'department_en','department_fr', 'org_id']).agg(
        activated_point_count=('activation', 'sum'),
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
    
    maf8 = si.loc[:,['fiscal_yr', 'service_id', 'org_id', 'department_en','department_fr', 'last_service_improvement']]
    
    maf8['report_yr'] = pd.to_numeric(maf8['fiscal_yr'].str.split('-').str[1], errors='coerce').astype(int)
    maf8['last_service_improvement_yr'] = pd.to_numeric(maf8['last_service_improvement'].str.split('-').str[1], errors='coerce')
    
    maf8['yrs_since_last_service_improvement'] = maf8['report_yr']-maf8['last_service_improvement_yr']
    maf8['last_service_improvement_within_1_yr'] = (maf8['yrs_since_last_service_improvement'] <= 1) & (maf8['yrs_since_last_service_improvement'] >= 0)
    
    maf8 = maf8.groupby(['fiscal_yr', 'department_en','department_fr', 'org_id']).agg(
        improved_services_count=('last_service_improvement_within_1_yr', 'sum'),
        service_count_maf8=('service_id', 'nunique')
    ).reset_index()
    
    # Determine score and associated result
    maf8['maf8_score'] = (maf8['improved_services_count']/maf8['service_count_maf8'])*100
    # maf8['maf8_result'] = pd.cut(maf8['maf8_score'], bins=score_bins, labels=score_results, right=False)

    # === SUMMARY MAF TABLE === 
    maf_dfs = [maf1, maf2, maf5, maf6, maf8]
    index_cols = ['fiscal_yr', 'org_id', 'department_en', 'department_fr']
    
    # Set index for each DataFrame in the list
    maf_temps = [df.set_index(index_cols) for df in maf_dfs]
    
    # Concatenate along columns and reset index
    maf_all = pd.concat(maf_temps, axis=1).reset_index()
    

    # === DRR INDICATORS ===

    # =================================
    # DRR Indicator ID DR-2467: Fraction of high-volume services that are fully available online
    
    # Define high-volume threshold
    HIGH_VOLUME_THRESHOLD = 45000

    # Define online interaction point (OIP) columns
    OIP_COLS = [
        'os_account_registration',
        'os_authentication',
        'os_application',
        'os_decision',
        'os_issuance',
        'os_issue_resolution_feedback',
    ]

    # Filter service inventory for high-volume and external services
    si_hv = si[
        ((si['num_applications_total'] >= HIGH_VOLUME_THRESHOLD) &
        (si['service_scope'].str.contains('EXTERN', regex=True)))].copy()

    # Melt the DataFrame for activation analysis
    dr2467 = si_hv.melt(
        id_vars=['fiscal_yr', 'fy_org_id_service_id'],
        value_vars=OIP_COLS,
        var_name='online_interaction_point',
        value_name='activation'
    )

    # Create boolean indicators for activation states
    dr2467['activation_y'] = dr2467['activation'].eq('Y')
    dr2467['activation_n'] = dr2467['activation'].eq('N')
    dr2467['activation_na'] = dr2467['activation'].eq('NA')

    # Aggregate activations at service level
    dr2467 = dr2467.groupby(['fiscal_yr', 'fy_org_id_service_id'], as_index=False).agg(
        activation_y=('activation_y', 'sum'),
        activation_n=('activation_n', 'sum'),
        activation_na=('activation_na', 'sum')
    )

    # Determine end-to-end online availability (online_e2e)
    dr2467['online_e2e'] = np.select(
        [
            dr2467['activation_na'] == len(OIP_COLS),  # All interaction points are 'NA', len(OIP_COLS)=6
            dr2467['activation_n'] > 0                # At least one interaction point is 'N'
        ],
        [
            None,  # Fully NA services are excluded
            False  # Services with any 'N' are not fully online
        ],
        default=True  # Services without 'N' are fully online
    ).astype('bool')

    # Remove services with all NA activation states
    dr2467 = dr2467[dr2467['activation_na'] < len(OIP_COLS)]

    # Aggregate at the fiscal year level
    dr2467 = dr2467.groupby('fiscal_yr', as_index=False).agg(
        hv_online_e2e_count=('online_e2e', 'sum'),
        hv_service_count=('fy_org_id_service_id', 'nunique')
    )

    # Compute DR-2467 score
    dr2467['dr2467_score'] = (dr2467['hv_online_e2e_count'] / dr2467['hv_service_count']) * 100

    # =================================
    # DRR Indicator ID DR-2468: Fraction of high-volume (applications & telephone enquiries) 
    # services that meet one or more service standard
    
    # Define high-volume threshold
    HIGH_VOLUME_THRESHOLD = 45000

    # Select relevant columns and ensure numeric conversion for 'num_phone_enquiries'
    si_hvte = si[['service_id', 'fiscal_yr', 'org_id', 'fy_org_id_service_id', 'num_applications_total', 'num_phone_enquiries', 'service_scope']].copy()
    si_hvte['num_phone_enquiries'] = pd.to_numeric(si_hvte['num_phone_enquiries'], errors='coerce').fillna(0)

    # Compute total applications including phone enquiries
    si_hvte['num_applications_total_plus_phone_enquiries'] = si_hvte['num_applications_total'] + si_hvte['num_phone_enquiries']

    # Filter for high-volume (apps+te) external services
    si_hvte = si_hvte[
        (si_hvte['num_applications_total_plus_phone_enquiries'] >= HIGH_VOLUME_THRESHOLD) &
        (si_hvte['service_scope'].str.contains('EXTERN', regex=True))]
    
    # Filter service standards that met their target
    ss_met = ss.loc[ss['target_met'] == 'Y', ['fy_org_id_service_id']]

    # Identify services for which their associated standards met at least one target
    si_hvte['ss_target_met'] = si_hvte['fy_org_id_service_id'].isin(ss_met['fy_org_id_service_id'])

    # Aggregate data at fiscal year level
    dr2468 = si_hvte.groupby('fiscal_yr').agg(
        hvte_services_count_meeting_standard=('ss_target_met', 'sum'),
        hvte_services_count=('fy_org_id_service_id', 'count')
    ).reset_index()

    # Compute DR-2468 score
    dr2468['dr2468_score'] = (dr2468['hvte_services_count_meeting_standard'] / dr2468['hvte_services_count']) * 100

    # =================================
    # DRR Indicator ID DR-2469: Fraction of service applications submitted online 
    # for high volume external services

    HIGH_VOLUME_THRESHOLD = 45000
    si_hv = si[
        ((si['num_applications_total'] >= HIGH_VOLUME_THRESHOLD) &
        (si['service_scope'].str.contains('EXTERN', regex=True)))].copy()

    # Select relevant columns and ensure numeric conversion for 'num_applications_online'
    dr2469 = si_hv[['service_id', 'fiscal_yr', 'fy_org_id_service_id', 'num_applications_total', 'num_applications_online']].copy()
    dr2469['num_applications_online'] = pd.to_numeric(dr2469['num_applications_online'], errors='coerce').fillna(0)

    # Determine fy-level counts for applications
    dr2469 = dr2469.groupby(['fiscal_yr'], as_index=False).agg(
        hv_online_applications=('num_applications_online', 'sum'),
        hv_total_applications=('num_applications_total', 'sum')
    )

    # Determine score
    dr2469['dr2469_score'] = (dr2469['hv_online_applications']/dr2469['hv_total_applications'])*100

    # === SUMMARY DRR TABLE === 
    drr_dfs = [dr2467, dr2468, dr2469]
    index_cols = ['fiscal_yr']
    
    # Set index for each DataFrame in the list
    drr_temps = [df.set_index(index_cols) for df in drr_dfs]
    
    # Concatenate along columns and reset index
    drr_all = pd.concat(drr_temps, axis=1).reset_index()



    # === SPENDING & FTEs BY PROGRAM ===
    # Load DRF data from utils (i.e. RBPO)
    drf = build_drf(config)
    drf['org_id'] = drf['org_id'].astype(int)

    # =================================
    # service_fte_spending: FTEs and spending by programs delivering services
    si_drf = si.loc[:, ['service_id', 'fiscal_yr', 'program_id', 'org_id']]
    si_drf['program_id'] = si_drf['program_id'].str.split(',')
    si_drf = si_drf.explode('program_id')
    si_drf = si_drf[si_drf['program_id'].notna()]
    si_drf['org_id'] = si_drf['org_id'].astype(int)
    
    service_fte_spending = pd.merge(
        si_drf, 
        drf, 
        how='left', 
        left_on=['fiscal_yr', 'program_id', 'org_id'], 
        right_on=['si_link_yr', 'program_id', 'org_id'],
        indicator='valid_program'
    )

    # Identify programs from service inventory that do not appear in the drf for that fy, org
    service_fte_spending['valid_program'] = (service_fte_spending['valid_program'] == 'both')

    # Drop duplicate si_link_yr in favor of just using fy. they should be the same.
    service_fte_spending.drop(columns="si_link_yr", inplace=True)
       
    # === EXPORT DATAFRAMES ===
    indicator_exports = {
        "si_vol": si_vol,
        "si_oip": si_oip,
        "ss_tml_perf_vol": ss_tml_perf_vol,
        # "si_fy_interaction_sum": si_fy_interaction_sum,
        # "si_fy_service_count": si_fy_service_count,
        "si_reviews": si_reviews,
        "service_fte_spending": service_fte_spending,
        # "maf1": maf1,
        # "maf2": maf2,
        # "maf5": maf5,
        # "maf6": maf6,
        # "maf8": maf8,
        "maf_all": maf_all,
        # "dr2467": dr2467,
        # "dr2468": dr2468,
        # "dr2469": dr2469,
        "drr_all": drr_all
    }
    
    export_to_csv(
        data_dict=indicator_exports,
        output_dir=INDICATORS_DIR,
        config=config
    )
