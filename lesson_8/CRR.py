import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import datetime as dt


# Open csv as DataFrame with necessary columns
df = pd.read_csv("data.csv", header=0)
df = df[['Customer ID', 'InvoiceDate']]
pd.set_option('display.max_columns', 10)
df = df[df['Customer ID'].notna()]
df['Customer ID'] = df['Customer ID'].astype(int)
df.InvoiceDate = pd.to_datetime(df.InvoiceDate)

for col in df.columns:
    if df[col].dtypes == 'object':
        df[col] = df[col].fillna(df[col].value_counts().index[0])


def get_month(x):
    return dt.datetime(x.year, x.month, 1)


# Create transaction_date column based on month
df['TransactionMonth'] = df['InvoiceDate'].apply(get_month)
# Grouping by Customer ID
grouping = df.groupby('Customer ID')['TransactionMonth']
# Assigning new column with a minimum InvoiceMonth value
df['CohortMonth'] = grouping.transform('min')


def get_date_int(df, column):
    year = df[column].dt.year
    month = df[column].dt.month
    day = df[column].dt.day
    return year, month, day


transcation_year, transaction_month, _ = get_date_int(df, 'TransactionMonth')
cohort_year, cohort_month, _ = get_date_int(df, 'CohortMonth')

#  Get the  difference in years and in in months
years_diff = transcation_year - cohort_year
months_diff = transaction_month - cohort_month
df['CohortIndex'] = years_diff * 12 + months_diff + 1

# Counting daily active customer from each cohort with counting number of unique customer
grouping = df.groupby(['CohortMonth', 'CohortIndex'])
cohort_data = grouping['Customer ID'].apply(pd.Series.nunique)
cohort_data = cohort_data.reset_index()

# Assigning column names to the dataframe created above
cohort_counts = cohort_data.pivot(index='CohortMonth',
                                  columns='CohortIndex',
                                  values='Customer ID')

cohort_sizes = cohort_counts.iloc[:, 0]
retention = cohort_counts.divide(cohort_sizes, axis=0)

# Coverting the retention rate into percentage
retention = retention.round(3) * 100
retention.index = retention.index.strftime('%Y-%m')

# Initialize the figure and creating the heatmap
plt.figure(figsize=(16, 10))
plt.title('Retention Rate in percentage: Monthly Cohorts', fontsize=14)
sns.heatmap(retention, annot=True, vmin=0.0, vmax=50, cmap="YlGnBu", fmt='g')
plt.ylabel('Cohort Month')
plt.xlabel('Cohort Index')
plt.yticks(rotation='360')
plt.savefig('retention_rate.png')
plt.show()
