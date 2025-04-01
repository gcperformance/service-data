
import pandas as pd
data = '/workspaces/service-data/outputs/si.csv'
si = pd.read_csv(data, sep=';')
print(si.head)
from datetime import datetime
import pytz

# Specify the timezone
timezone = pytz.timezone("America/Montreal")

# Get the current date and time in the specified timezone
current_date = datetime.now(timezone)

# Format the current date and time into the desired string format
current_datestr = current_date.strftime("%Y-%m-%d_%H:%M:%S")

# Print the current date and time
print(f"current date: {current_datestr}")

# to add a new column for phone apps inquiries
# phone apps inquiries are num_phone_enquiries plus num_applications_by_phone
# based on error received 'can only concatenate str (not int) to string

# Convert the columns to numeric, forcing any non-numeric values to NaN
si['num_phone_enquiries'] = pd.to_numeric(si['num_phone_enquiries'], errors='coerce')
si['num_applications_by_phone'] = pd.to_numeric(si['num_applications_by_phone'], errors='coerce')

# Add the new column 'phone_apps_inquiries' by filling NaN values with 0
si['phone_apps_inquiries'] = si['num_phone_enquiries'].fillna(0) + si['num_applications_by_phone'].fillna(0)

# adding a new column for total transactions
# to avoid error, convert the columns to numeric

si['num_applications_by_email'] = pd.to_numeric(si['num_applications_by_email'], errors='coerce')
si['num_applications_by_fax'] = pd.to_numeric(si['num_applications_by_fax'], errors='coerce')
si['num_applications_by_mail'] = pd.to_numeric(si['num_applications_by_mail'], errors='coerce')
si['num_applications_by_other'] = pd.to_numeric(si['num_applications_by_other'], errors='coerce')
si['num_applications_in_person'] = pd.to_numeric(si['num_applications_in_person'], errors='coerce')
si['num_applications_online'] = pd.to_numeric(si['num_applications_online'], errors='coerce')

# now add all six columns including the column phone apps inquiries to get the total transactions
si['total_transactions'] = (
si['num_applications_by_email'].fillna(0) + 
si['num_applications_by_fax'].fillna(0) + 
si['num_applications_by_mail'].fillna(0) + 
si['num_applications_by_other'].fillna(0) + 
si['num_applications_in_person'].fillna(0) + 
si['num_applications_online'].fillna(0) + 
si['phone_apps_inquiries'].fillna(0)
)

# adding a new column for applications done by phone, online and in person only
si['apps_online_and_per'] = (
    si['num_applications_in_person'].fillna(0) + 
    si['num_applications_online'].fillna(0) + 
    si['phone_apps_inquiries'].fillna(0)
)

# adding a new column for omnichannels
si['omnichannel'] = si.apply(
    lambda row: 1 if pd.notna(row['phone_apps_inquiries']) and pd.notna(row['num_applications_online']) and pd.notna(row['num_applications_in_person']) else 0, 
    axis=1
)

# adding a new column for external
si['external'] = si['service_scope'].str.contains('EXTERN', na=False).astype(int)
#convert the column to numeric 
si['external'] = pd.to_numeric(si['external'], errors='coerce')

# adding a new column for high volume services
si['highvolume'] = (si['total_transactions'] >= 45000).astype(int)

# adding a new column for online enabled Y
# creating columns to check which lists out the columns from os_account_registration to os_issue_resolution_feedback
columns_to_check = [ 'os_account_registration', 'os_authentication', 'os_application', 'os_decision', 'os_issuance', 'os_issue_resolution_feedback']

si['online_enabledY'] = si[columns_to_check].apply(lambda row: (row == 'Y').sum(), axis=1)

# adding column for online enabled N
si['online_enabledN'] = si[columns_to_check].apply(lambda row: (row == 'N').sum(), axis=1)

# adding column for online enabled NA
si['online_enabledNA'] = si[columns_to_check].isna().sum(axis=1)

# adding a new column for online end to end
si['onlineE2E'] = (
    si.apply(lambda row: "0" if row['online_enabledNA'] == 6 
    else "1" if row['online_enabledY'] + row['online_enabledNA'] == 6 
    else "0", axis=1)
    )

# adding a new column for online one or more points
si['onl_morepoints'] = si['online_enabledY'].apply(lambda x: '1' if x >= 1 else '0')

# importing the service standards data
ss_data = '/workspaces/service-data/outputs/ss.csv'
ss = pd.read_csv(ss_data, sep=';')

# to view the column names in the ss data frame
colnames_ss = ss.columns.tolist()
print(colnames_ss)

# adding column for services with standards and standards met
# grouping and summarizing the 'ss' DataFrame
ss_count = ss.groupby(['service_id', 'fiscal_yr']).agg(
    standards_count=('service_id', 'size'),  # Count the occurrences
    standards_met=('target_met', lambda x: (x == 'Y').sum())  # Count where target_met is 'Y'
).reset_index()

# merging the 'ss_count' DataFrame with the 'si' DataFrame
si = si.merge(ss_count, on=['service_id', 'fiscal_yr'], how='left')

# replacing NaN values in 'standards_count' and 'standards_met' with 0
si['standards_count'] = si['standards_count'].fillna(0)
si['standards_met'] = si['standards_met'].fillna(0)

# adding a new column for services that met at least one standard
si['STDS_metsome'] = (si['standards_met'] >= 1).astype(int)

# creating the FYSID column by merging fiscal_yr and service_id columns
si['FYSID'] = si['fiscal_yr'].astype(str) + si['service_id'].astype(str)

# BEGIN THE DATA PACK METRICS
# filter data for fiscal year 2023-2024
sidata = si[si['fiscal_yr'] == '2023-2024']

# metric 2: total number of transactions for fiscal year 2023-2024
# the number is in millions
totaltransactions = sidata['total_transactions'].sum() / 1000000
print(totaltransactions)

# count the number of transactions(services) in 2023-2024
count = sidata['total_transactions'].notna().sum()
print(count)

# metric 3a: online as a share of total transactions
# total online transactions for 2023-2024 (replacing NaN values with 0)
online_transactions = sidata['num_applications_online'].fillna(0).sum()

# total transactions
transactionstotal = sidata['total_transactions'].sum()

# fraction of online as a share of total transactions
online_fraction = (online_transactions / transactionstotal) * 100
print(online_fraction)

# metric 3b: telephone as a share of total transactions
# total telephone transactions for 2023-2024 (replacing NaN values with 0)
telephone_transactions = sidata['phone_apps_inquiries'].fillna(0).sum()

# fraction of telephone as a share of total transactions
telephone_fraction = (telephone_transactions / transactionstotal) * 100
print(telephone_fraction)

# metric 3c: in-person as a share of total transactions
# total in-person transactions for 2023-2024 (replacing NaN values with 0)
in_person_transactions = sidata['num_applications_in_person'].fillna(0).sum()

#fraction of in-person as a share of total transactions
in_person_fraction = ( in_person_transactions / transactionstotal) * 100
print(in_person_fraction)

# metric 4: share of GC services wih omnichannel offerings
# count of the distinct service_id where omnichannel is 1
omni_count = sidata[sidata['omnichannel'] == 1]['service_id'].nunique()

# count of the distinct service_id in the entire dataset
total_count = sidata['service_id'].nunique()

# share of omnichannel as a percentage
share_omni = (omni_count / total_count) * 100
print(share_omni)

# metric 5a: online as a share of omnichannel usage
# total transactions where omnichannel is 1
totaltransactions = sidata[sidata['omnichannel'] == 1]['total_transactions'].sum()

# sum of online applications where omnichannel is 1
sum_onlineapps = sidata[sidata['omnichannel'] == 1]['num_applications_online'].sum()

# online as a share of omnichannel usage
share_online = (sum_onlineapps / totaltransactions) * 100
print(share_online)

# metric 5b: phone as a share of omnichannel usage
# sum of phone app inquiries where omnichannel is 1
sum_phone = sidata[sidata['omnichannel'] == 1]['phone_apps_inquiries'].sum()

# phone as a share of omnichannel usage
share_phone = (sum_phone / totaltransactions) * 100
print(share_phone)

# metric 5c: in-person as a share of omnichannel usage
sum_in_person = sidata[sidata['omnichannel'] == 1]['num_applications_in_person'].sum()

# in_person as a share of omnichannel usage
share_in_person = (sum_in_person / totaltransactions) * 100
print(share_in_person)

# metric 6: number of external departments
no_departments = sidata[sidata['external'] == 1]['department_en'].nunique()
print(no_departments)

# metric 7: number of programs
no_programs = sidata['program_name_en'].nunique()
print(no_programs)

# metric 8: number of external services (data is already filtered for external)
no_external_service = sidata[sidata['external'] == 1]['service_id'].nunique()
print(no_external_service)

# metric 9: number of high volume services
no_highvolume_services = sidata[(sidata['external'] == 1) & (sidata['highvolume'] == 1)]['service_id'].nunique()
print(no_highvolume_services)

# metric 10: total online transactions (in millions)
total_online_transactions = sidata[sidata['external'] == 1]['num_applications_online'].sum() / 1000000
print(total_online_transactions)

# metric 11: total phone transactions (in millions)
total_phone_transactions = sidata[sidata['external'] == 1]['phone_apps_inquiries'].sum() / 1000000
print(total_phone_transactions)

# metric 12: total in person transactions (in millions)
in_person_applications = sidata[sidata['external'] == 1]['num_applications_in_person'].sum()
# look up canadian boarder services ending in 669 '2023-2024669'
lookup_value = "2023-2024669"
lookup_result = sidata[sidata['FYSID'] == lookup_value]['total_transactions'].iloc[0]
# subtract CBSA from in person applications
total_in_person_applications = (in_person_applications - lookup_result) / 1000000
print(total_in_person_applications)

# metric 13: total mail applications ( in millions)
total_mail_applications = sidata[sidata['external'] == 1]['num_applications_by_mail'].sum() / 1000000
print(total_mail_applications)

# metric 14: share of external services online end to end 
# convert the 'onlineE2E' column to numeric values (in case it's stored as strings)
sidata['onlineE2E'] = pd.to_numeric(sidata['onlineE2E'], errors='coerce')
# distinct services online end to end
onl_E2E = sidata[(sidata['external'] == 1) & (sidata['onlineE2E'] == 1)]['service_id'].nunique()
# distinct services where online enabled NA < 6
onl_enabledNA = sidata[(sidata['external'] == 1) & (sidata['online_enabledNA'] < 6)]['service_id'].nunique()
# share of external services online end to end
share_ext_onlE2E = (onl_E2E / onl_enabledNA) * 100
print(share_ext_onlE2E)

# metric 15: share of external serices that have at least one point online (data is already filtered for external services)

# convert the 'onl_morepoints' column to numeric values (in case it's stored as strings)
sidata['onl_morepoints'] = pd.to_numeric(sidata['onl_morepoints'], errors='coerce')

# services with atleast one point online
onl_onepoint = sidata[(sidata['external'] == 1) & (sidata['onl_morepoints'] == 1)]['service_id'].nunique()

# all services
all_services =  sidata[sidata['external'] == 1]['service_id'].nunique()
# share of services with one at least one point online
share_service = (onl_onepoint / all_services) * 100
print(share_service)


# metric 16: services meeting service standards
# services that met some standards
ser_metsome = sidata[(sidata['external'] == 1) & (sidata['STDS_metsome'] == 1)]['service_id'].nunique()

# share of services meeting service standards
ser_metstds = (ser_metsome / all_services) * 100
print(ser_metstds)

# metric 17: share of external high volume services online end to end 
# high volume services online end to end
highvol_E2E = sidata[(sidata['external'] == 1) & (sidata['highvolume'] == 1) & (sidata['onlineE2E'] == 1)]['service_id'].nunique()

# high volume online enabled NA services < 6
highvol_enabledNA = sidata[(sidata['external'] == 1) & (sidata['highvolume'] == 1) & (sidata['online_enabledNA'] < 6)]['service_id'].nunique()

# share of highvolume services online end to end as a percentage 
high_vol_E2E = (highvol_E2E / highvol_enabledNA) * 100
print(high_vol_E2E)

# metric 18: share of external high volume services which have at least one point online 
# high volume services with at least one point online
highvol_1point_count = sidata[(sidata['external'] == 1) & (sidata['highvolume'] == 1) & (sidata['onl_morepoints'] == 1)]['service_id'].nunique()

# high volume services
highvol_all_count = sidata[(sidata['external'] == 1) & (sidata['highvolume'] == 1)]['service_id'].nunique()

# share as a percentage
share_highvol_1point = (highvol_1point_count / highvol_all_count) * 100
print(share_highvol_1point)

# metric 19: high volume services meeting service standards
# high-volume services that meet service standards
high_vol_ser_metstds_count = sidata[(sidata['external'] == 1) & (sidata['highvolume'] == 1) & (sidata['STDS_metsome'] == 1)]['service_id'].nunique()

# share as a percentage
high_vol_ser_metstds = (high_vol_ser_metstds_count / highvol_all_count) * 100
print(high_vol_ser_metstds)

# plotting the top 15 department graphs
# top 15 departments based on number of total applications
# Replace NaN values with 0 for specific columns
columns_to_replace = [
    'num_applications_by_phone', 
    'num_applications_by_fax', 
    'num_applications_by_mail', 
    'num_applications_by_other', 
    'num_applications_in_person', 
    'num_applications_online', 
    'num_applications_by_email'
]
# Replace NaNs with 0
sidata[columns_to_replace] = sidata[columns_to_replace].fillna(0)
# Select the desired columns
topsi = sidata[['service_name_en', 'service_id'] + columns_to_replace + ['num_applications_total']]
# filterin for the top 15 and excluding certain service IDs
# Ensure 'service_id' is treated as string for proper comparison
topsi['service_id'] = topsi['service_id'].astype(str)
# List of service_ids to exclude
exclude_service_ids = ['669', '1677', '1108', '1111', 'SRV03577', '1112', '1242']
# Filter out rows with the specified service_ids
topsi_filtered = topsi[~topsi['service_id'].isin(exclude_service_ids)]
# Sort the filtered data by 'total_applications' in descending order
topsi_filtered = topsi_filtered.sort_values(by='num_applications_total', ascending=False)
# Select the top 15 rows
topsi_top_15 = topsi_filtered.head(15)

# online enablement based on top 15 number of total applications
# Select relevant columns for the new dataset
onldata = sidata[['service_name_en', 'service_id', 'online_enabledY', 'online_enabledN', 'online_enabledNA', 'num_applications_total']]
# Sort the data by 'num_applications_total' in descending order
onldata = onldata.sort_values(by='num_applications_total', ascending=False)
# List of service_ids to filter (exclude these from the top 15)
ser_ids_to_filter = ['669', '1677', '1108', '1111', 'SRV03577', '1112', '1242']
# Filter out the rows where the service_id is in the exclude list
onldata_filtered = onldata[~onldata['service_id'].isin(ser_ids_to_filter)]
# Select the top 15 services after excluding the specified service_ids
top15onl = onldata_filtered.head(15)
# Calculate the online service usage as a percentage
top15onl['online_enabled'] = (top15onl['online_enabledY'] / 6) * 100
top15onl['online_notenabled'] = (top15onl['online_enabledN'] / 6) * 100
top15onl['online_NA'] = (top15onl['online_enabledNA'] / 6) * 100
# Select relevant columns
top15serv = top15onl[['service_name_en', 'service_id', 'online_enabled', 'online_notenabled', 'online_NA', 'num_applications_total']]

# plotting top 10 services by applications
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter
# Reshaping the data to long format
top15si_long = topsi_top_15.melt(id_vars=['service_name_en'], 
                            value_vars=['num_applications_by_phone', 'num_applications_online', 
                                         'num_applications_in_person', 'num_applications_by_mail', 
                                         'num_applications_by_email', 'num_applications_by_fax', 'num_applications_by_other'], 
                            var_name='application_type', 
                            value_name='applications')
# Create the bar plot
plt.figure(figsize=(10, 6))
sns.barplot(data=top15si_long, x='applications', y='service_name_en', hue='application_type', 
            dodge=False, palette='Set1')
# Format x-axis labels to show in millions
formatter = FuncFormatter(lambda x, _: f'{x / 1e6:.1f}M')  # Format labels in millions
plt.gca().xaxis.set_major_formatter(formatter)
# Set plot labels and title
plt.title('Top 15 External Services based on Total Applications')
plt.xlabel('Total Applications (in millions)')
plt.ylabel('Service Name (English)')
plt.legend(title='Application Type')
# Adjust y-axis label size if needed
plt.xticks(rotation=45)  # Rotate x-axis labels for readability
plt.tight_layout()
# Show the plot
plt.show()

# to plot the chart for "online enablement of top 15 external services based on total applications"
# Reshaping the data to long format
top15serv_long = top15serv.melt(id_vars=['service_name_en'], 
                                value_vars=['online_enabled', 'online_notenabled', 'online_NA'], 
                                var_name='online_status', 
                                value_name='percentage')
# Normalize the percentages to ensure they sum to 100% for each service
top15serv_long['percentage'] = top15serv_long.groupby('service_name_en')['percentage'].transform(lambda x: x / x.sum() * 100)
# Calculate cumulative sum for stacked bars to position the labels
top15serv_long['cumsum_percentage'] = top15serv_long.groupby('service_name_en')['percentage'].cumsum()
# Create the stacked bar chart
plt.figure(figsize=(10, 6))
sns.barplot(data=top15serv_long, x='percentage', y='service_name_en', hue='online_status', 
            dodge=False, palette={'online_enabled': 'green', 
                                   'online_notenabled': 'gray', 
                                   'online_NA': 'blue'})
# Add the data labels
for index, row in top15serv_long.iterrows():
    plt.text(x=row['cumsum_percentage'] - row['percentage'] / 2, 
             y=index, 
             s=f"{round(row['percentage'], 1)}%", 
             color='white', 
             ha='center', va='center', fontsize=10)

# Format x-axis labels to show percentage
plt.gca().xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x}%'))
# Set plot labels and title
plt.title('Online Enablement of Top 15 External Services based on Total Applications')
plt.xlabel('Percentage (%)')
plt.ylabel('Service Name')
plt.legend(title='Online Status', loc='upper right')
# Adjust y-axis label size if needed
plt.xticks(rotation=45)  # Rotate x-axis labels for readability
plt.tight_layout()
# Show the plot
plt.show()