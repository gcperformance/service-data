import pandas as pd
import numpy as np
import logging, sys
logger = logging.getLogger(__name__)

from src.export import export_to_csv
from src.utils import build_drf, sid_list

def output_si_ss(si, ss, config, snapshot=False):
    try:
        logger.debug('...')
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

        # If running a snapshot run, change output directory accordingly
        if snapshot:
            OUTPUT_DIR = config['output_dir'] / 'snapshots' / snapshot
        else:
            OUTPUT_DIR = config['output_dir']
        
        export_to_csv(
            data_dict=output_exports,
            output_dir=OUTPUT_DIR
        )

        return output_exports
    
    except Exception as e:
        logger.error("Error: %s", e, exc_info=True)


def summary_si_ss(si, ss, config, snapshot=False):
    try:
        logger.debug('...')
        # === Summary tables based on si & ss ===   
        # =======================================
        # si_vol: Applications by service
        # Given a service, what is the volume of interactions (applications) by channel and fiscal year?

        # List of columns that contain application / interaction volumes
        # These also represent the channel through which the interaction took place
        APP_COLS = [
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
            value_vars=APP_COLS,
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
        
        
        # === EXPORT DATAFRAMES ===
        indicator_exports = {
            "si_vol": si_vol,
            "si_oip": si_oip,
            "ss_tml_perf_vol": ss_tml_perf_vol,
            # "si_fy_interaction_sum": si_fy_interaction_sum,
            # "si_fy_service_count": si_fy_service_count,
            "si_reviews": si_reviews
        }
        
        # If running a snapshot run, change output directory accordingly
        if snapshot:
            INDICATORS_DIR = config['output_dir'] / 'snapshots' / snapshot / config['indicators_dir']
        else:
            INDICATORS_DIR = config['output_dir'] / config['indicators_dir']
        
        export_to_csv(
            data_dict=indicator_exports,
            output_dir=INDICATORS_DIR
        )

    except Exception as e:
        logger.error("Error: %s", e, exc_info=True)



def maf(si, ss, config, snapshot=False):
    try:
        logger.debug('...')
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
        

        # === EXPORT DATAFRAMES ===
        indicator_exports = {
            # "maf1": maf1,
            # "maf2": maf2,
            # "maf5": maf5,
            # "maf6": maf6,
            # "maf8": maf8,
            "maf_all": maf_all
        }
        
        # If running a snapshot run, change output directory accordingly
        if snapshot:
            INDICATORS_DIR = config['output_dir'] / 'snapshots' / snapshot / config['indicators_dir']
        else:
            INDICATORS_DIR = config['output_dir'] / config['indicators_dir']

        export_to_csv(
            data_dict=indicator_exports,
            output_dir=INDICATORS_DIR
        )
    except Exception as e:
        logger.error("Error: %s", e, exc_info=True)


def drr(si, ss, config, snapshot=False):
    try:
        logger.debug('...')
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

        # === EXPORT DATAFRAMES ===
        indicator_exports = {
            # "dr2467": dr2467,
            # "dr2468": dr2468,
            # "dr2469": dr2469,
            "drr_all": drr_all
        }
        
        # If running a snapshot run, change output directory accordingly        
        if snapshot:
            INDICATORS_DIR = config['output_dir'] / 'snapshots' / snapshot / config['indicators_dir']
        else:
            INDICATORS_DIR = config['output_dir'] / config['indicators_dir']
        
        export_to_csv(
            data_dict=indicator_exports,
            output_dir=INDICATORS_DIR
        )

    except Exception as e:
        logger.error("Error: %s", e, exc_info=True)


def datapack(si, ss, config, snapshot=False):
    try:
        logger.debug('...')
        # === DATA PACK ===
        # Set up dataframes and columns for data pack analysis

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

        # Define application volume columns
        APP_COLS = [
            'num_applications_by_phone', 
            'num_applications_online', 
            'num_applications_in_person', 
            'num_applications_by_mail', 
            'num_applications_by_email', 
            'num_applications_by_fax', 
            'num_applications_by_other',
            'num_applications_total',
            'num_phone_enquiries',
        ]

        # Set si_dp and ss_dp as working DataFrames
        si_dp = si.copy()
        ss_dp = ss.copy()

        # Create a new column to identify 'omnichannel' services
        # Omnichannel = phone, online, and in-person applications are applicable
        # Note that in previous versions calculated in excel sheets the omnichannel boolean
        # was mistakenly ignoring phone channels. This adjustment ('or' on phones, 'and' with online & in person)
        # was defined in May 2025.
        def is_filled(col):
            return col.notna() & (col.astype(str).str.strip() != '') & (col != 'NA') & (col != 'ND')

        si_dp['omnichannel'] = (
            (is_filled(si_dp['num_phone_enquiries']) | is_filled(si_dp['num_applications_by_phone'])) &
            is_filled(si_dp['num_applications_online']) &
            is_filled(si_dp['num_applications_in_person'])
        )

        # Convert all application volume columns to numeric
        si_dp[APP_COLS] = si_dp[APP_COLS].apply(pd.to_numeric, errors='coerce').fillna(0)

        # Create 'num_phone_apps_enquiries' column (sum of phone enquiries + phone applications)
        si_dp['num_phone_apps_enquiries'] = si_dp['num_phone_enquiries'] + si_dp['num_applications_by_phone']

        # Create 'num_transactions_total' by summing all application channels and phone enquiries
        si_dp['num_transactions_total'] = si_dp['num_applications_total'] + si_dp['num_phone_enquiries']  

        # Create a new column to identify external services
        si_dp['external'] = si_dp['service_scope'].str.contains('EXTERN', na=False)

        # Create a new column to identify high-volume services
        si_dp['highvolume'] = si_dp['num_transactions_total'] >= HIGH_VOLUME_THRESHOLD

        # Count online interaction point statuses
        si_dp['online_enabled_Y'] = si_dp[OIP_COLS].apply(lambda row: (row == 'Y').sum(), axis=1)
        si_dp['online_enabled_N'] = si_dp[OIP_COLS].apply(lambda row: (row == 'N').sum(), axis=1)
        si_dp['online_enabled_NA'] = si_dp[OIP_COLS].apply(lambda row: (row == 'NA').sum(), axis=1)

        # Define total expected interaction points
        TOTAL_POINTS = len(OIP_COLS)

        # Determine if service is fully online end-to-end
        si_dp['online_e2e'] = (
            (si_dp['online_enabled_Y'] + si_dp['online_enabled_NA'] == TOTAL_POINTS) &
            (si_dp['online_enabled_Y'] > 0)
        )

        # Identify services with at least one online-enabled point
        si_dp['min_one_point_online'] = si_dp['online_enabled_Y'] > 0

        # Identify service standards for external services
        ss_dp = ss_dp.merge(
            si_dp[['fy_org_id_service_id','external', 'highvolume']],
            how = 'left',
            on='fy_org_id_service_id'
        )

        ss_dp['external'] = ss_dp['external'].fillna(False)
        ss_dp['highvolume'] = ss_dp['highvolume'].fillna(False)
        ss_dp['target_met'] = ss_dp['target_met'].fillna('NA')

        # === DATA PACK METRICS 2, 3a, 3b, 3c: external/enterprise services ===
        # 2: Total number of transactions
        dp_metrics = si_dp.copy().groupby('fiscal_yr').agg({
                'fy_org_id_service_id': 'nunique',
                'num_transactions_total': 'sum',
                'num_applications_online': 'sum',
                'num_phone_apps_enquiries': 'sum',
                'num_applications_in_person': 'sum',
            }).reset_index().rename(columns={'fy_org_id_service_id':'total_services'})

        # 3: Shares by channel
        dp_metrics['online_percentage'] = dp_metrics['num_applications_online'] / dp_metrics['num_transactions_total']
        dp_metrics['phone_percentage'] = dp_metrics['num_phone_apps_enquiries'] / dp_metrics['num_transactions_total']
        dp_metrics['in-person_percentage'] = dp_metrics['num_applications_in_person'] / dp_metrics['num_transactions_total']


        # === DATA PACK METRICS 4, 5a, 5b, 5c: omnichannel services ===
        # 4: Share of services that are omnichannel
        # 5: Shares by channel for omnichannel services

        dp_filtered = si_dp[si_dp['omnichannel']]
        dp_metrics = dp_metrics.merge(
            dp_filtered.groupby('fiscal_yr').agg({
                'fy_org_id_service_id': 'nunique',
                'num_transactions_total': 'sum',
                'num_applications_online': 'sum',
                'num_phone_apps_enquiries': 'sum',
                'num_applications_in_person': 'sum'
            }).reset_index().rename(columns={'fy_org_id_service_id':'total_services'}),
            on='fiscal_yr',
            how='left',
            suffixes=('', '_omni')
        )

        dp_metrics['omni_service_percentage'] = dp_metrics['total_services_omni'] / dp_metrics['total_services']

        dp_metrics['omni_online_percentage'] = dp_metrics['num_applications_online_omni'] / dp_metrics['num_transactions_total_omni']
        dp_metrics['omni_phone_percentage'] = dp_metrics['num_phone_apps_enquiries_omni'] / dp_metrics['num_transactions_total_omni']
        dp_metrics['omni_in-person_percentage'] = dp_metrics['num_applications_in_person_omni'] / dp_metrics['num_transactions_total_omni']


        # === DATA PACK METRIC 6, 8, 10, 11, 12, 13: external services ===
        # 6: Number of departments delivering external services
        # 8: Number of external services
        # 10: Total online transactions for external services
        # 11: Total phone transactions for external services
        # 12: Total in person transactions for external services
        # 13: Total mail transactions for external services
        # si_dp_ext = si_dp[si_dp['external']].copy()

        # Services excluded by convention or decision:
        # 669: Traveller / Highway traveller processing - decision prior to our arrival
        # 1677: The Canadian Astronomy Data Centre (CADC) - too many online apps
        EXCLUDED_SERVICES_ID = ['669', '1677']

        dp_filtered = si_dp[si_dp['external']]
        dp_metrics = dp_metrics.merge(
            dp_filtered.groupby('fiscal_yr').agg({
                'org_id': 'nunique',
                'fy_org_id_service_id': 'nunique',
                'num_applications_online':'sum', 
                'num_applications_in_person':'sum',
                'num_phone_apps_enquiries':'sum',
                'num_applications_by_mail':'sum'
            }).reset_index().rename(columns={'fy_org_id_service_id':'total_services', 'org_id': 'total_orgs_ext'}),
            on='fiscal_yr',
            how='left',
            suffixes=('', '_ext')
        )

        dp_filtered = si_dp[si_dp['external'] & ~si_dp['service_id'].isin(EXCLUDED_SERVICES_ID)]
        dp_metrics = dp_metrics.merge(
            dp_filtered.groupby('fiscal_yr').agg({
                'num_applications_online':'sum', # remove 1677
                'num_applications_in_person':'sum', # remove 669
            }).reset_index(),
            on='fiscal_yr',
            how='left',
            suffixes=('', '_ext_excl_services')
        )

        # === DATA PACK METRIC 7 ===
        # 7: External programs
        dp_filtered = si_dp[si_dp['external']].loc[:, ['service_id', 'fiscal_yr', 'program_id', 'org_id']].copy()
        dp_programs = dp_filtered.copy()

        dp_programs['program_id'] = dp_programs['program_id'].astype(str).str.split(',')
        dp_programs = dp_programs.explode('program_id')
        dp_programs = dp_programs[dp_programs['program_id'].notna()]
        dp_programs['program_id'] = dp_programs['program_id'].str.strip()

        dp_filtered = dp_programs
        dp_metrics = dp_metrics.merge(
            dp_filtered.groupby('fiscal_yr').agg({
                'program_id':'nunique'
            }).reset_index().rename(columns={'program_id':'total_programs_ext'}),
            on='fiscal_yr',
            how='left'
        )


        # === DATA PACK METRIC 14 ===
        # 14: Share of external services that are online end-to-end
        dp_filtered = si_dp[si_dp['external'] & si_dp['online_e2e']]
        dp_metrics = dp_metrics.merge(
            dp_filtered.groupby('fiscal_yr').agg({
                'fy_org_id_service_id': 'nunique'
            }).reset_index().rename(columns={'fy_org_id_service_id':'total_services'}),
            on='fiscal_yr',
            how='left',
            suffixes=('', '_ext_online')
        )

        dp_metrics['ext_online_service_percentage'] = dp_metrics['total_services_ext_online']/dp_metrics['total_services_ext']


        # === DATA PACK METRIC 15 ===
        # 15: Share of external services that have at least one online interaction point activated
        dp_filtered = si_dp[si_dp['external'] & si_dp['min_one_point_online']]
        dp_metrics = dp_metrics.merge(
            dp_filtered.groupby('fiscal_yr').agg({
                'fy_org_id_service_id': 'nunique'
            }).reset_index().rename(columns={'fy_org_id_service_id':'total_services'}),
            on='fiscal_yr',
            how='left',
            suffixes=('', '_ext_1oip')
        )

        dp_metrics['ext_1oip_service_percentage'] = dp_metrics['total_services_ext_1oip']/dp_metrics['total_services_ext']


        # === DATA PACK METRIC 16 ===
        # 16: Share of external service standards meeting target
        dp_filtered = ss_dp[ss_dp['external'] & ((ss_dp['target_met']=='Y') | (ss_dp['target_met']=='N'))]
        dp_metrics = dp_metrics.merge(
            dp_filtered.groupby('fiscal_yr').agg({
                'fy_org_id_service_id_std_id': 'nunique'
            }).reset_index().rename(columns={'fy_org_id_service_id_std_id': 'total_standards_ext'}),
            on='fiscal_yr',
            how='left',
        )

        dp_filtered = ss_dp[ss_dp['external'] & (ss_dp['target_met']=='Y')]
        dp_metrics = dp_metrics.merge(
            dp_filtered.groupby('fiscal_yr').agg({
                'fy_org_id_service_id_std_id': 'nunique'
            }).reset_index().rename(columns={'fy_org_id_service_id_std_id': 'total_standards_met_ext'}),
            on='fiscal_yr',
            how='left'
        )

        dp_metrics['ext_standard_met_percentage'] = dp_metrics['total_standards_met_ext'] / dp_metrics['total_standards_ext']


        # === DATA PACK METRIC 17 ===
        # 17: Share of external, high volume services that are online end-to-end
        dp_filtered = si_dp[si_dp['external'] & si_dp['highvolume']]
        dp_metrics = dp_metrics.merge(
            dp_filtered.groupby('fiscal_yr').agg({
                'fy_org_id_service_id': 'nunique'
            }).reset_index().rename(columns={'fy_org_id_service_id':'total_services'}),
            on='fiscal_yr',
            how='left',
            suffixes=('', '_ext_hv')
        )

        dp_filtered = si_dp[si_dp['external'] & si_dp['highvolume'] & si_dp['online_e2e']]
        dp_metrics = dp_metrics.merge(
            dp_filtered.groupby('fiscal_yr').agg({
                'fy_org_id_service_id': 'nunique'
            }).reset_index().rename(columns={'fy_org_id_service_id':'total_services'}),
            on='fiscal_yr',
            how='left',
            suffixes=('', '_ext_hv_online')
        )

        dp_metrics['ext_hv_online_service_percentage'] = dp_metrics['total_services_ext_hv_online']/dp_metrics['total_services_ext_hv']


        # === DATA PACK METRIC 18 ===
        # 17: Share of external, high volume services that have at least one online interaction point activated
        dp_filtered = si_dp[si_dp['external'] & si_dp['highvolume'] & si_dp['min_one_point_online']]
        dp_metrics = dp_metrics.merge(
            dp_filtered.groupby('fiscal_yr').agg({
                'fy_org_id_service_id': 'nunique'
            }).reset_index().rename(columns={'fy_org_id_service_id':'total_services'}),
            on='fiscal_yr',
            how='left',
            suffixes=('', '_ext_hv_1oip')
        )

        dp_metrics['ext_hv_1oip_service_percentage'] = dp_metrics['total_services_ext_hv_1oip']/dp_metrics['total_services_ext_hv']


        # === DATA PACK METRIC 19 ===
        # 19: Share of external high-volume service standards meeting target
        dp_filtered = ss_dp[ss_dp['external'] & ss_dp['highvolume'] & ((ss_dp['target_met']=='Y') | (ss_dp['target_met']=='N'))]
        dp_metrics = dp_metrics.merge(
            dp_filtered.groupby('fiscal_yr').agg({
                'fy_org_id_service_id_std_id': 'nunique'
            }).reset_index().rename(columns={'fy_org_id_service_id_std_id': 'total_standards_ext_hv'}),
            on='fiscal_yr',
            how='left',
        )

        dp_filtered = ss_dp[ss_dp['external'] & ss_dp['highvolume'] & (ss_dp['target_met']=='Y')]
        dp_metrics = dp_metrics.merge(
            dp_filtered.groupby('fiscal_yr').agg({
                'fy_org_id_service_id_std_id': 'nunique'
            }).reset_index().rename(columns={'fy_org_id_service_id_std_id': 'total_standards_met_ext_hv'}),
            on='fiscal_yr',
            how='left'
        )

        dp_metrics['ext_hv_standard_met_percentage'] = dp_metrics['total_standards_met_ext_hv']/dp_metrics['total_standards_ext_hv']
        
        dp_metrics = dp_metrics.T.reset_index()
        
        # Ranking services by application volume for top 15
        RANK_COLS = [
            'fy_org_id_service_id',
            'fiscal_yr', 
            'service_name_en', 
            'service_name_fr', 
            'online_enabled_Y', 
            'online_enabled_N', 
            'online_enabled_NA',
            'num_applications_total',
            'num_applications_by_phone', 
            'num_applications_online', 
            'num_applications_in_person', 
            'num_applications_by_mail', 
            'num_applications_by_email', 
            'num_applications_by_fax', 
            'num_applications_by_other'
        ]

        EXCLUDED_SERVICES_ID = ['1111', '1108', '3728', '669', '1677', '1112']

        # Filter and select columns
        dp_services_rank = si_dp[
            si_dp['external'] & 
            (si_dp['num_applications_total'] > 0) & 
            (~si_dp['service_id'].isin(EXCLUDED_SERVICES_ID))
        ][RANK_COLS].copy()

        # Add ranking
        dp_services_rank['num_applications_rank'] = (
            dp_services_rank
            .groupby('fiscal_yr')['num_applications_total']
            .rank(method='dense', ascending=False)
        )

        # Only bother keeping the top 20
        dp_services_rank = dp_services_rank[dp_services_rank['num_applications_rank'] <= 20]

        # === EXPORT DATAFRAMES ===
        indicator_exports = {
            "dp_metrics": dp_metrics,
            "dp_services_rank": dp_services_rank
        }
        
        # If running a snapshot run, change output directory accordingly
        if snapshot:
            INDICATORS_DIR = config['output_dir'] / 'snapshots' / snapshot / config['indicators_dir']
        else:
            INDICATORS_DIR = config['output_dir'] / config['indicators_dir']

        export_to_csv(
            data_dict=indicator_exports,
            output_dir=INDICATORS_DIR
        )

    except Exception as e:
        logger.error("Error: %s", e, exc_info=True)



def service_fte_spending(si, drf, config, snapshot=False):
    try:
        logger.debug('...')
        # === SPENDING & FTEs BY PROGRAM ===
        # Load DRF data from utils (i.e. RBPO)
        drf = build_drf(config, snapshot)
        drf['org_id'] = drf['org_id'].astype(int)

        # =================================
        # service_fte_spending: FTEs and spending by programs delivering services
        si_drf = si.loc[:, ['service_id', 'fiscal_yr', 'program_id', 'org_id']]
        si_drf['program_id'] = si_drf['program_id'].str.split(',')
        si_drf = si_drf.explode('program_id')
        si_drf = si_drf[si_drf['program_id'].notna()]
        si_drf['org_id'] = si_drf['org_id'].astype(int)
        
        service_fte_spending_df = pd.merge(
            si_drf, 
            drf, 
            how='left', 
            left_on=['fiscal_yr', 'program_id', 'org_id'], 
            right_on=['si_link_yr', 'program_id', 'org_id'],
            indicator='valid_program'
        )

        # Identify programs from service inventory that do not appear in the drf for that fy, org
        service_fte_spending_df['valid_program'] = (service_fte_spending_df['valid_program'] == 'both')

        # Drop duplicate si_link_yr in favor of just using fy. they should be the same.
        service_fte_spending_df.drop(columns="si_link_yr", inplace=True)

        # === EXPORT DATAFRAMES ===
        indicator_exports = {
            "service_fte_spending": service_fte_spending_df
        }

        # If running a snapshot run, change output directory accordingly
        if snapshot:
            INDICATORS_DIR = config['output_dir'] / 'snapshots' / snapshot / config['indicators_dir']
        else:
            INDICATORS_DIR = config['output_dir'] / config['indicators_dir']
        
        export_to_csv(
            data_dict=indicator_exports,
            output_dir=INDICATORS_DIR
        )

    except Exception as e:
        logger.error("Error: %s", e, exc_info=True)



def process_files(si, ss, config, snapshot=False):
    try:
        logger.debug('...')
        sid_list(si, config, snapshot)

        processed_si_ss = output_si_ss(si, ss, config, snapshot)
        si = processed_si_ss['si']
        ss = processed_si_ss['ss']
        
        summary_si_ss(si, ss, config, snapshot)
        maf(si, ss, config, snapshot)
        drr(si, ss, config, snapshot)
        datapack(si, ss, config, snapshot)
        
        drf = build_drf(config, snapshot)
        service_fte_spending(si, drf, config, snapshot)

        return processed_si_ss
        
    except Exception as e:
        logger.error("Error: %s", e, exc_info=True)
