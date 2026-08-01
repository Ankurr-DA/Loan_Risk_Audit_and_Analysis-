# =============================================================================
# LOAD RAW CSV FILES INTO MYSQL DATABASE
# =============================================================================
from sqlalchemy import create_engine
import pandas as pd

USER = 'root'
PASSWORD = 'ankur'  
HOST = 'localhost'
PORT = '3306'
DATABASE = 'sql_analytics3' 
 
engine = create_engine(f"mysql+mysqlconnector://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")

files = [
    'CSV/borrower_financials.csv',
    'CSV/loan_log.csv',
    'CSV/payment_ledger.csv'
]

try:
    for a in files:
        tables = a.replace('CSV/','').split('.')[0]
        df = pd.read_csv(a)
        df.to_sql(tables, engine, if_exists='replace', index=False)
        print(f'Success: {tables}')

except:
    print('Failed')
