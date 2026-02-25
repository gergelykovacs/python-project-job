import os

import pandas as pd
from prefect import flow, task
from sqlalchemy import create_engine


@task
def extract_data(file_path: str):
    return pd.read_csv(file_path)


@task
def transform_data(df: pd.DataFrame):
    # Logic we want to test:
    # 1. Calculate total_cost
    df["total_cost"] = df["quantity"] * df["price"]
    # 2. Uppercase status
    df["status"] = df["status"].str.upper()
    # 3. Filter invalid rows
    return df[df["quantity"] > 0]


@task
def load_data(df: pd.DataFrame, table_name: str):
    # Allow overriding DB connection for testing
    db_conn = os.getenv("DB_CONN", "sqlite:///production.db")
    engine = create_engine(db_conn)
    df.to_sql(table_name, engine, if_exists="append", index=False)


@flow(name="Daily Sales Batch")
def batch_job_main():
    file_path = os.getenv("SOURCE_DATA_PATH", "source_data.csv")
    raw_data = extract_data(file_path)
    processed_data = transform_data(raw_data)
    load_data(processed_data, "daily_sales")


if __name__ == "__main__":
    batch_job_main()
