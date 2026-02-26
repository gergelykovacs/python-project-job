import os

import pandas as pd
from prefect import flow, task

from .adapter import DatabaseWriter, SourceDataReader
from .config import ProjectLogger, ProjectProperties
from .service import DataTransformer


@task
def extract_data(file_path: str) -> pd.DataFrame:
    return SourceDataReader().read_data(file_path)


@task
def transform_data(df: pd.DataFrame):
    return DataTransformer().transform_data(df)


@task
def load_data(df: pd.DataFrame):
    DatabaseWriter().write_data(df)


@flow(name="Daily Sales Batch")
def batch_job_main():
    logger = ProjectLogger.for_name(__name__)
    logger.info(f"Project name: {ProjectProperties().name()}")
    file_path = os.getenv("SOURCE_DATA_PATH", "source_data.csv")
    raw_data = extract_data(file_path)
    processed_data = transform_data(raw_data)
    load_data(processed_data)


if __name__ == "__main__":
    batch_job_main()
