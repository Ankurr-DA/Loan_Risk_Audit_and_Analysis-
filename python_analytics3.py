# -----------------------------------------------------------------------------
# LOAD SQL VIEWS INTO PANDAS DATAFRAMES
# -----------------------------------------------------------------------------
from sqlalchemy import create_engine
import pandas as pd
import numpy as np

USER = 'root'
PASSWORD = 'ankur'  
HOST = 'localhost'
PORT = '3306'
DATABASE = 'sql_analytics3' 
 
engine = create_engine(f"mysql+mysqlconnector://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")

#importing views from SQL
sql_query1 = 'select * from v_loan_risk;'
sql_query2 = 'select * from v_loan_payments;'

df_risk = pd.read_sql(sql_query1, con=engine)
df_payment = pd.read_sql(sql_query2, con=engine)

# Fixing Loan_id & loan_type
df_risk['loan_id'] = df_risk['loan_id'].str.strip()
df_risk['loan_type'] = df_risk['loan_type'].str.strip().str.upper()

# Fixing approved_amount
df_risk['approved_amount'] = df_risk['approved_amount'].str.replace('$','')
df_risk['approved_amount'] = df_risk['approved_amount'].str.replace(',','')
df_risk['approved_amount'] = pd.to_numeric(df_risk['approved_amount'],errors='coerce')

# Fixing start_date
df_risk['start_date'] = pd.to_datetime(df_risk['start_date'], dayfirst=False, errors='coerce')

# Fixing origination_salary
df_risk['origination_salary'] = df_risk['origination_salary'].str.replace('$','')
df_risk['origination_salary'] = df_risk['origination_salary'].str.replace(',','')
df_risk['origination_salary'] = pd.to_numeric(df_risk['origination_salary'],errors='coerce')

# Fixing current_salary
df_risk['current_salary'] = df_risk['current_salary'].str.replace('$','')
df_risk['current_salary'] = df_risk['current_salary'].str.replace(',','')
df_risk['current_salary'] = pd.to_numeric(df_risk['current_salary'],errors='coerce')

# Fixing loan_id & loan_type
df_payment['loan_id'] = df_payment['loan_id'].str.strip()
df_payment['loan_type'] = df_payment['loan_type'].str.strip().str.upper()

# Fixing due_date & paid_date
df_payment['due_date'] = pd.to_datetime(df_payment['due_date'], dayfirst=False, errors='coerce')
df_payment['paid_date'] = pd.to_datetime(df_payment['paid_date'], dayfirst=False, errors='coerce')

# Fixing emi_due
df_payment['emi_due'] = df_payment['emi_due'].str.replace('$','')
df_payment['emi_due'] = df_payment['emi_due'].str.replace(',','')
df_payment['emi_due'] = pd.to_numeric(df_payment['emi_due'],errors='coerce')

# Fixing emi_paid
df_payment['emi_paid'] = df_payment['emi_paid'].str.replace('$','')
df_payment['emi_paid'] = df_payment['emi_paid'].str.replace(',','')
df_payment['emi_paid'] = pd.to_numeric(df_payment['emi_paid'],errors='coerce')

# Droping Empty transaction rows 
df_payment = df_payment.dropna(subset=['due_date', 'emi_due', 'emi_paid'], how='all')

# Identify salary_drop & credit_drop
salary_drop = df_risk['current_salary'] - df_risk['origination_salary']
credit_drop = df_risk['current_credit_score'] - df_risk['origination_credit_score']

# Making Conditions 
conditions1 = [
    df_risk['start_date'].isnull(),
    (df_risk['origination_salary'].isnull()) | (df_risk['current_salary'].isnull()) | (df_risk['origination_credit_score'].isnull()) | (df_risk['current_credit_score'].isnull()),
    (salary_drop < 0) & (credit_drop < 0),
    salary_drop < 0,
    credit_drop < 0
] 
# Condition Labeling
label1 = [
    'Missing Start Date',  
    'Incomplete Credentials', 
    'High Risk (Both Salary & Credit Drops)',
    'At-Risk (Salary Drop)', 
    'At-Risk (Credit Drop)'
]
# Putting conditions and labels in numpy
df_risk['Risk_Category'] = np.select(conditions1, label1, default='Safe / Healthy')

# Identity raw days 
raw_days = (df_payment['paid_date'] - df_payment['due_date']).dt.days

# Making Conditions
conditions2 = [
    df_payment['due_date'].isnull(),
    df_payment['paid_date'].isnull(),
    raw_days < 0,
    raw_days > 60,
    raw_days.between(31, 60),
    raw_days.between(1, 30),

] 
# Condition Labeling
label2 = [

    'Missing Due Date',
    'Unpaid / Pending',
    'Paid Earlier',
    '60+ Days Late (Default)',
    '31 - 60 Days Late',
    '1 - 30 Days Late'
]
# Putting conditions and labels in numpy
df_payment['Timing Status'] = np.select(conditions2, label2, default='On-Time / Active')

# Identify emi difference
emi_difference = df_payment['emi_paid'] - df_payment['emi_due']
# Making Conditions
conditions3 = [
    df_payment['paid_date'].isnull() | (df_payment['emi_paid'] == 0),
    emi_difference < 0,
    emi_difference > 0
]
# Condition Labeling
label3 = [
    'No Payment',
    'Underpaid (Partial)',
    'Overpaid (Surplus)'
]
# Putting conditions and labels in numpy
df_payment['Payment Status'] = np.select(conditions3,label3,default='Fully Paid (Exact)')

# Report 1 Risk Category--------------------------------------------------------------------------------------
df_risk['salary_change'] = df_risk['current_salary'] - df_risk['origination_salary']
df_risk['credit_change'] = df_risk['current_credit_score'] - df_risk['origination_credit_score']
  
Risk_Category = df_risk.groupby('Risk_Category').agg(
    Total_Loans = ('loan_id','count'),
    Total_Approved_Capital = ('approved_amount','sum'),
    Avg_Credit_Score_Change = ('credit_change','mean')
).reset_index()

Risk_Category['Total_Approved_Capital'] = Risk_Category['Total_Approved_Capital'].round(2)
Risk_Category['Avg_Credit_Score_Change'] = Risk_Category['Avg_Credit_Score_Change'].round(2)

Risk_Category.insert(1, 'System Action', 'Performing')

# Creating System Action column for report 1
Risk_Category.loc[Risk_Category['Risk_Category'].str.contains('High Risk|Missing|Incomplete', na=False), 'System Action'] = 'Critical Action'
Risk_Category.loc[Risk_Category['Risk_Category'].str.contains('At-Risk', na=False), 'System Action'] = 'Monitor Account'
Risk_Category.loc[Risk_Category['Risk_Category'].str.contains('Safe', na=False), 'System Action'] = 'Performing'

Risk_Category.to_excel('Risk_Category.xlsx',index=False)
print('Risk_Category.xlsx Exported Successfully')


# Report 2 Payment Performance-----------------------------------------------------------------------------------
Payment_Performance = df_payment.groupby(['Timing Status','Payment Status']).agg(
    Transaction_Count = ('loan_id','nunique'),
    Total_EMI_Due = ('emi_due','sum'),
    Total_EMI_Paid = ('emi_paid','sum')
).reset_index()

Payment_Performance['Total_EMI_Due'] = Payment_Performance['Total_EMI_Due'].round(2)
Payment_Performance['Total_EMI_Paid'] = Payment_Performance['Total_EMI_Paid'].round(2)
Payment_Performance['Uncollected Shortfall'] = Payment_Performance['Total_EMI_Due'] - Payment_Performance['Total_EMI_Paid']
Payment_Performance['Uncollected Shortfall'] = Payment_Performance['Uncollected Shortfall'].round(2)

Payment_Performance.insert(2, 'System Action', 'Performing')

# Creating System Action column for report 2
monitor_list = ['1 - 30 Days Late', '31 - 60 Days Late', 'Unpaid / Pending']
Payment_Performance.loc[Payment_Performance['Timing Status'].isin(monitor_list), 'System Action'] = 'Monitor Account'
Payment_Performance.loc[Payment_Performance['Payment Status'] == 'Underpaid (Partial)', 'System Action'] = 'Monitor Account'

critical_list = ['60+ Days Late (Default)', 'Missing Due Date']
Payment_Performance.loc[Payment_Performance['Timing Status'].isin(critical_list), 'System Action'] = 'Critical Action'
Payment_Performance.loc[Payment_Performance['Payment Status'] == 'No Payment', 'System Action'] = 'Critical Action'

Payment_Performance.to_excel('Payment_Performance.xlsx',index=False)
print('Payment_Performance.xlsx Exported Successfully')

