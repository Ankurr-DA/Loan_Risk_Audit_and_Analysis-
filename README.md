# Loan Risk Audit & Analysis

---

## Project Overview
This end-to-end data pipeline project transforms raw borrower financial data and loan payment logs into structured Excel risk reports and an interactive executive dashboard. The objective is to evaluate loan capital exposure, track payment performance, and categorize loans based on financial health metrics such as salary and credit score drops.

## Data Pipeline & Architecture
The project follows a structured ETL (Extract, Transform, Load) pipeline:  
**CSV → MySQL → SQL Views → Python Data Audit → Excel → Tableau**

1. **Database Ingestion:** Ingested three core raw datasets into a MySQL database (`sql_analytics3`) using the Python `sqlalchemy` engine.
2. **SQL Auditing & Views:** Ran comprehensive data quality checks to identify missing salaries, credit scores, unlinked loan IDs, and invalid date formats. Created optimized SQL views (`v_loan_risk` and `v_loan_payments`) for stream processing.
3. **Python Cleaning & Normalization:** Standardized text strings, parsed monetary values by removing `$` and `,` characters, handled missing values, and converted string dates to standard `datetime` objects using `pandas`.
4. **Audit Classification & Reporting:** Built a dynamic rule engine in Python (`np.select`) to flag non-compliant or risky transactions, producing two core executive exports:
   * **Risk Category Report:** Aggregates total loans, total approved capital, and average credit score changes across flagged audit statuses to determine if an account needs to be monitored or requires critical action.
   * **Payment Performance Report:** Evaluates expected versus collected EMI across timing statuses (e.g., "60+ Days Late", "Underpaid (Partial)") to calculate uncollected shortfalls.
5. **Dashboard Visualization:** Connected the output reports into a Tableau dashboard to highlight KPI metric cards and risk breakdowns.

---

## Project Deliverables & Visual Preview

### 1. Risk Category Report
Evaluates active loans based on borrower financial changes, specifically tracking drops in salary and credit score from origination to current status. It calculates total approved capital at risk and assigns a "System Action" (Performing, Monitor Account, Critical Action) to each risk bracket.

### 2. Payment Performance Report
Tracks expected EMI payments against actual collected amounts to identify uncollected cash shortfalls. It categorizes payment timing statuses (e.g., Unpaid, Paid Earlier, 1-30 Days Late) and assigns strict system actions for defaults and underpayments.

### 3. Live Tableau Executive Dashboard
An interactive dashboard displaying key financial metrics: **$1.55B** Total Capital Exposure, **$1.69M** Uncollected Cash Shortfall, **4,000** Active Loan Portfolio Count, and an **82.91%** Collection Recovery Rate. The dashboard features breakdown charts for Capital Exposure by Risk Category, Expected vs. Collected EMI, Credit Score Trajectory, and Uncollected Shortfall Breakdown.

![Dashboard 1 (1)](Dashboard%201%20(1).jpg)

## 📁 Project Files Arrenged According to WorkFlow

* [`borrower_financials.csv`](./borrower_financials.csv) 
* [`loan_log.csv`](./loan_log.csv) 
* [`payment_ledger.csv`](./payment_ledger.csv)

--- 
 
* [`data_transfer.py`](./data_transfer3.py) 
 --> [`SQL_Analytics.sql`](./SQL_Analytics3.sql) 
 --> [`python_analytics.py`](./python_analytics3.py)

 ---
 
* [`Risk_Category.xlsx`](./Risk_Category.xlsx) 
* [`Payment_Performance.xlsx`](./Payment_Performance.xlsx)

 ---
 
* [`Loan Risk Audit & Analysis.twbX`](./Loan%20Risk%20Audit%20%26%20Analysis.twbx)

---

## Technologies Used
* **Languages:** Python (`pandas`, `sqlalchemy`, `numpy`), SQL
* **Database:** MySQL
* **Reporting & Viz:** Excel, Tableau
* **Environment:** VS Code

  
