use sql_analytics3;

-- Checking for Missing Values in borrower_financials ----------------------------------------------------------------------
select 
sum(origination_salary is null) as null_origination_salary,
sum(current_salary is null) as null_current_salary,
sum(origination_credit_score is null) as null_origination_credit_score,
sum(current_credit_score is null) as null_current_credit_score
from borrower_financials;

-- Checking for Missing Values in loan_log ----------------------------------------------------------------------
select 
sum(loan_type is null) as null_loan_type,
sum(approved_amount is null) as null_approved_amount,
sum(interest_rate is null) as null_interest_rate,
sum(start_date is null) as null_start_date
from loan_log;

-- Checking for Missing Values in payment_ledger ----------------------------------------------------------------------
select 
sum(due_date is null) as null_due_date,
sum(paid_date is null) as null_paid_date,
sum(emi_due is null) as null_emi_due,
sum(emi_paid is null) as null_emi_paid
from payment_ledger;

-- Auditing Messy Columns in borrower_financials for python cleaning ----------------------------------------------------------------------
select origination_salary from borrower_financials 
where origination_salary like '%$%' or origination_salary like '%,%';

select current_salary from borrower_financials 
where current_salary like '%$%' or current_salary like '%,%';

-- Identifing impossible values for Python Transformations ----------------------------------------------------------------------
select origination_salary from borrower_financials where origination_salary < 0;
select current_salary from borrower_financials where current_salary < 0;
select origination_credit_score from borrower_financials where origination_credit_score < 0;
select current_credit_score from borrower_financials where current_credit_score < 0;


-- Auditing Messy Columns in loan_log for python cleaning ----------------------------------------------------------------------
select distinct loan_type from loan_log;

select approved_amount from loan_log 
where approved_amount like '%$%' or approved_amount like '%,%';

select interest_rate from loan_log 
where interest_rate like '%\%';

select start_date from loan_log
where start_date not like '____-__-__';

-- Identifing impossible values for Python Transformations ----------------------------------------------------------------------
select approved_amount from loan_log where approved_amount < 0;
select interest_rate from loan_log where interest_rate < 0;


-- Auditing Messy Columns in payment_ledger for python cleaning ----------------------------------------------------------------------
select due_date from payment_ledger
where due_date not like '____-__-__';

select paid_date from payment_ledger
where paid_date not like '____-__-__';

select emi_due from payment_ledger 
where emi_due like '%$%' or emi_due like '%,%';

select emi_paid from payment_ledger 
where emi_paid like '%$%' or emi_paid like '%,%';

-- Identifing impossible values for Python Transformations ----------------------------------------------------------------------
select emi_due from payment_ledger where emi_due < 0;
select emi_paid from payment_ledger where emi_paid < 0;

-- Excluding duplicate records -----------------------------
create table borrower_financials_clean select distinct * from borrower_financials;
create table loan_log_clean select distinct * from loan_log;
create table payment_ledger_clean select distinct * from payment_ledger;

-- View 1 ----------------------------------------------------------------------
create view v_loan_risk as
select 
	l.loan_id, 
    l.loan_type, 
    l.approved_amount,
    l.start_date,
	f.origination_salary, 
    f.current_salary, 
	f.origination_credit_score, 
    f.current_credit_score 
from loan_log_clean l
left join borrower_financials_clean f on l.loan_id = f.loan_id;

-- View 2 ----------------------------------------------------------------------
create view v_loan_payments as
select 
	l.loan_id, 
    l.loan_type,
	p.due_date, 
    p.paid_date, 
    p.emi_due, 
    p.emi_paid
from loan_log_clean l
left join payment_ledger_clean p on l.loan_id = p.loan_id;