# ibrd-loan-management-efficiency

# 💸 Enhancing Loan Management Efficiency for IBRD  
### A Modern Data Engineering Case Study with Snowflake, dbt & AWS

---

## 🌍 Project Overview

The International Bank for Reconstruction and Development (IBRD), part of the World Bank Group, provides loans to middle and low-income countries for development projects. Loan cancellations (withdrawn before disbursement) create major time and financial inefficiencies.  

This project focuses on building a cloud-native data platform to analyze historical and streaming loan data, detect patterns in cancelled loans, and enable a downstream predictive model to proactively reduce cancellations.

---

## 🧩 Problem Statement

- Understand why and where loan cancellations occur.  
- Build a robust data pipeline to serve analytics and ML workloads.  
- Enable real-time monitoring of new loans and status changes using streaming data.  

---

## 🛠 Tech Stack

- ❄ Snowflake (Snowpark, Snowpipe, Streams & Tasks)  
- 🧱 dbt Cloud/Core  
- ☁ AWS S3 (external stages & storage options)  
- ⚡ Streaming / Real-time ingestion (Snowflake Streaming, optionally Spark Streaming)  
- 📊 BI / Dashboards (any tool – e.g., Power BI, Tableau, Streamlit, etc.)

---

## 📂 Datasets

- Batch / Historical Data  
  - IBRD Statement Of Loans – Historical Data  
  - https://finances.worldbank.org/Loans-and-Credits/IBRD-Statement-Of-Loans-Historical-Data/zucq-nrc3  

- Streaming / Latest Data  
  - GitHub: https://github.com/akgeoinsys/finance-ibrd  

---

## 🎯 Key Business Objectives

- ⏱ Calculate loan processing time (e.g., days between agreement signing and repayments).  
- 🥇 Identify top three countries with highest loan amounts and detect sudden drops.  
- 🚩 Detect countries with at least one loan cancellation (with sufficient borrowing history).  
- 📆 Compute average repayment period for each country.  

---

## 🧱 Architecture & Approach

### 🥉 Bronze / Raw Layer

- Ingest files from AWS S3 using:
  - External stages + file formats  
  - Snowpipe for auto-ingest  
- Store raw data as-is in schema like:  
  - team1_bronze, team2_bronze, etc.  
- No transformations; acts as the source of truth.

### 🥈 Silver / Cleaned Layer

- Use Snowflake SQL, **Snowpark and dbt to:
  - Clean and standardize data  
  - Handle nulls, parse dates, fix types  
  - Remove duplicates and bad records  
  - Apply basic business rules  
- Store cleaned tables in schemas like:  
  - team1_silver, team2_silver, etc.  

### 🥇 Gold / Curated Layer

- Build business-ready marts using dbt:
  - Fact and dimension tables (star schema)  
  - Aggregations for analytics & dashboards  
- Optimized for:
  - BI tools  
  - ML feature extraction  
  - Monitoring and reporting  

---

## 🔄 Orchestration & Streaming

- Snowpipe  
  - Auto-ingestion when new files land in S3.  
- Streams & Tasks  
  - Streams track incremental changes.  
  - Tasks schedule transformations and downstream jobs.  
- dbt Cloud Jobs  
  - Run staging → intermediate → marts models.  
  - Apply tests (unique, not_null, relationships) for data quality.  
- Real-time / Near Real-time  
  - Optional Snowflake Streaming / Spark Streaming to process latest loan feed.  

---

## 👥 Team Execution Plan

- 👨‍💻 3 members per team.  
- 🎯 Clear ownership of:
  - Ingestion  
  - Transformation (dbt / Snowpark)  
  - Streaming & orchestration  
  - Visualization / reporting  
- 🤝 Integrate all components at the end for a final presentation to SMEs and mentors.

---

## 📐 Data Model (Star Schema)

### 1️⃣ fact_loan – Central Fact Table

| Column                   | Type / Role      | Description                             |
|--------------------------|------------------|-----------------------------------------|
| loan_number            | PK               | Unique loan identifier                  |
| borrower_key           | FK               | Links to dim_borrower                 |
| guarantor_key          | FK               | Links to dim_guarantor                |
| country_key            | FK               | Links to dim_country                  |
| loan_type_key          | FK               | Links to dim_loan_type                |
| loan_status_key        | FK               | Links to dim_loan_status              |
| project_key            | FK               | Links to dim_project                  |
| time_key               | FK               | Links to dim_time                     |
| currency_key           | FK               | Links to dim_currency                 |
| original_principal_amount | Measure      | Original committed amount               |
| cancelled_amount       | Measure          | Amount cancelled                        |
| undisbursed_amount     | Measure          | Amount not yet disbursed                |
| disbursed_amount       | Measure          | Total disbursed amount                  |
| repaid_to_ibrd         | Measure          | Amount repaid to IBRD                   |
| due_to_ibrd            | Measure          | Amount still due to IBRD                |
| exchange_adjustment    | Measure          | FX adjustment value                     |
| borrowers_obligation   | Measure          | Outstanding borrower obligation         |
| sold_3rd_party         | Measure          | Amount sold to third parties            |
| repaid_3rd_party       | Measure          | Amount repaid to third parties          |
| due_3rd_party          | Measure          | Amount due to third parties             |
| loans_held             | Measure          | Loans currently held                    |

---

### 2️⃣ dim_time

| Column                    | Description                               |
|---------------------------|-------------------------------------------|
| time_key (PK)           | Surrogate time key                        |
| Date_ID                 | Numeric or string date ID                 |
| Full_Date               | Full calendar date                        |
| Year                    | Year                                      |
| Quarter                 | Quarter (e.g., Q1, Q2)                    |
| Month                   | Month number                              |
| Month_Name              | Month name (e.g., January)               |
| end_of_period           | End-of-period flag / date                |
| first_repayment_date    | First repayment date                      |
| last_repayment_date     | Last repayment date                       |
| agreement_signing_date  | Loan agreement signing date               |
| board_approval_date     | Board approval date                       |
| effective_date          | Date loan becomes effective               |
| closed_date             | Loan closure date                         |
| last_disbursement_date  | Last disbursement date                    |

---

### 3️⃣ dim_project

| Column         | Description                    |
|----------------|--------------------------------|
| project_key (PK) | Surrogate project key     |
| project_id   | Source project identifier      |
| project_name | Name of the project            |

---

### 4️⃣ dim_borrower

| Column             | Description              |
|--------------------|--------------------------|
| borrower_key (PK)| Surrogate borrower key   |
| borrower         | Borrower name            |

---

### 5️⃣ dim_guarantor

| Column              | Description               |
|---------------------|---------------------------|
| guarantor_key (PK)| Surrogate guarantor key   |
| guarantor         | Guarantor name            |

---

### 6️⃣ dim_country

| Column                 | Description                         |
|------------------------|-------------------------------------|
| country_key (PK)     | Surrogate country key              |
| country_economy_code | Economy/country code               |
| country_economy      | Country / economy name             |
| region               | Geographic region                  |

---

### 7️⃣ dim_loan_type

| Column               | Description                  |
|----------------------|------------------------------|
| loan_type_key (PK) | Surrogate loan type key      |
| loan_type          | Loan type (e.g., NPL, CPL)   |

---

### 8️⃣ dim_loan_status

| Column                 | Description                |
|------------------------|----------------------------|
| loan_status_key (PK) | Surrogate loan status key |
| loan_status          | Current status of loan    |

---

### 9️⃣ dim_currency

| Column                    | Description                        |
|---------------------------|------------------------------------|
| currency_key (PK)       | Surrogate currency key            |
| currency_of_commitment  | Currency of loan commitment       |

---

## 🚀 How to Get Started

1. Clone this repository.  
2. Configure Snowflake account, warehouses, and role-based access.  
3. Create schemas for bronze/silver/gold per team (e.g., team1_bronze).  
4. Set up AWS S3 buckets, external stages, and file formats.  
5. Configure Snowpipe for auto-ingestion of batch and streaming files.  
6. Run dbt models for staging, intermediate, and marts.  
7. Connect your BI tool or Streamlit app to gold layer tables for dashboards.  

---

## 📊 Optional: Streamlit / Dashboard Ideas

- 📈 Loan cancellation trends by country / region / year.  
- 🧮 Average processing time and repayment period per country.  
- 🧱 Drill-down by loan type, **status, and **project.  
- 🚨 Real-time view of new loans and potential cancellation risk signals.
