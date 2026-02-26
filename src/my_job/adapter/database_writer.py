import os

import pandas as pd
from sqlalchemy import create_engine

from ..config import ProjectLogger


class DatabaseWriter:
    _table_name: str = "daily_sales"

    def __init__(self):
        db_conn: str = os.getenv("DB_CONN", "sqlite:///production.db")
        self._engine = create_engine(db_conn)
        self._logger = ProjectLogger.for_name(__name__)

    def write_data(self, df: pd.DataFrame):
        self._logger.info(f"Writing {len(df.index)} rows to {self._table_name} table")
        df.to_sql(self._table_name, self._engine, if_exists="append", index=False)
