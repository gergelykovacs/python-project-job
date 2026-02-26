import pandas as pd

from ..config import ProjectLogger


class DataTransformer:
    def __init__(self):
        self._logger = ProjectLogger.for_name(__name__)

    def transform_data(self, df: pd.DataFrame) -> pd.DataFrame:
        # 1. Calculate total_cost
        df["total_cost"] = df["quantity"] * df["price"]
        # 2. Uppercase status
        df["status"] = df["status"].str.upper()
        # 3. Filter invalid rows
        result = df[df["quantity"] > 0]
        self._logger.info(f"Filtered {len(df.index) - len(result.index)} invalid rows")
        return result
