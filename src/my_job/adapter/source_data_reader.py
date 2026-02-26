import pandas as pd

from ..config import ProjectLogger


class SourceDataReader:
    def __init__(self):
        self._logger = ProjectLogger.for_name(__name__)

    def read_data(self, file_path: str) -> pd.DataFrame:
        df = pd.read_csv(file_path)
        self._logger.info(f"Read {len(df.index)} rows from {file_path}")
        return df
