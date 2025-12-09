import sys
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.context import SparkContext
import boto3
from pyspark.sql import functions as F

args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

bucket_name = "p2.ibrd"
csv_path = "s3://p2.ibrd/raw/synthetic_ibrd_loans.csv"

parquet_prefix = "parquet/synthetic_data/"
parquet_path   = f"s3://{bucket_name}/{parquet_prefix}"

# ✅ remove old parquet so Snowflake does not read stale data
s3 = boto3.resource("s3")
bucket = s3.Bucket(bucket_name)
bucket.objects.filter(Prefix=parquet_prefix).delete()

# ✅ read CSV with schema inference
df = spark.read.csv(csv_path, header=True, inferSchema=True)

# ✅ rename columns exactly matching Snowflake Bronze table
rename_map = {
    "End of Period": "END_OF_PERIOD",
    "Loan Number": "LOAN_NUMBER",
    "Region": "REGION",
    "Country / Economy Code": "COUNTRY_ECONOMY_CODE",
    "Country / Economy": "COUNTRY_ECONOMY",
    "Borrower": "BORROWER",
    "Guarantor Country / Economy Code": "GUARANTOR_COUNTRY_ECONOMY_CODE",
    "Guarantor": "GUARANTOR",
    "Loan Type": "LOAN_TYPE",
    "Loan Status": "LOAN_STATUS",
    "Interest Rate": "INTEREST_RATE",
    "Currency of Commitment": "CURRENCY_OF_COMMITMENT",
    "Project ID": "PROJECT_ID",
    "Project Name": "PROJECT_NAME",
    "Original Principal Amount (US$)": "ORIGINAL_PRINCIPAL_AMOUNT_USD",
    "Cancelled Amount (US$)": "CANCELLED_AMOUNT_USD",
    "Undisbursed Amount (US$)": "UNDISBURSED_AMOUNT_USD",
    "Disbursed Amount (US$)": "DISBURSED_AMOUNT_USD",
    "Repaid to IBRD (US$)": "REPAID_TO_IBRD_USD",
    "Due to IBRD (US$)": "DUE_TO_IBRD_USD",
    "Exchange Adjustment (US$)": "EXCHANGE_ADJUSTMENT_USD",
    "Borrower's Obligation (US$)": "BORROWERS_OBLIGATION_USD",
    "Sold 3rd Party (US$)": "SOLD_3RD_PARTY_USD",
    "Repaid 3rd Party (US$)": "REPAID_3RD_PARTY_USD",
    "Due 3rd Party (US$)": "DUE_3RD_PARTY_USD",
    "Loans Held (US$)": "LOANS_HELD_USD",
    "First Repayment Date": "FIRST_REPAYMENT_DATE",
    "Last Repayment Date": "LAST_REPAYMENT_DATE",
    "Agreement Signing Date": "AGREEMENT_SIGNING_DATE",
    "Board Approval Date": "BOARD_APPROVAL_DATE",
    "Effective Date (Most Recent)": "EFFECTIVE_DATE",
    "Closed Date (Most Recent)": "CLOSED_DATE",
    "Last Disbursement Date": "LAST_DISBURSEMENT_DATE"
}

for old, new in rename_map.items():
    if old in df.columns:
        df = df.withColumnRenamed(old, new)

# ✅ add metadata fields
df = df.withColumn("INGESTION_DATE", F.current_timestamp())
df = df.withColumn("SOURCE_FILE_NAME", F.input_file_name())

# ✅ ensure FLAT parquet output compatible with Snowflake COPY
df = df.select([F.col(c) for c in df.columns])  # removes struct wrapper

# ✅ write flattened parquet files
df.coalesce(10).write \
    .mode("overwrite") \
    .option("compression", "snappy") \
    .option("spark.sql.parquet.writeLegacyFormat", "true") \
    .parquet(parquet_path)

job.commit()
print("✅ CSV → FLAT Parquet completed. Ready for Bronze COPY.")
