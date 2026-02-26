from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from my_job.adapter.database_witer import DatabaseWriter


class TestDatabaseWriter:
    @pytest.fixture
    def writer(self):
        # Mock create_engine to avoid actual DB connection during init
        with patch("my_job.adapter.database_witer.create_engine") as mock_engine:
            writer = DatabaseWriter()
            writer._engine = mock_engine.return_value
            return writer

    def test_write_data_calls_to_sql(self, writer):
        # Create a sample DataFrame
        df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})

        # Mock the logger
        writer._logger = MagicMock()

        # Mock to_sql on the DataFrame (since it's called on the df instance)
        with patch.object(pd.DataFrame, "to_sql") as mock_to_sql:
            writer.write_data(df)

            # Verify logger was called
            writer._logger.info.assert_called_once_with(f"Writing 2 rows to {writer._table_name} table")

            # Verify to_sql was called with correct arguments
            mock_to_sql.assert_called_once_with(writer._table_name, writer._engine, if_exists="append", index=False)

    def test_write_data_empty_dataframe(self, writer):
        df = pd.DataFrame()

        # Mock the logger
        writer._logger = MagicMock()

        with patch.object(pd.DataFrame, "to_sql") as mock_to_sql:
            writer.write_data(df)

            writer._logger.info.assert_called_once_with(f"Writing 0 rows to {writer._table_name} table")
            mock_to_sql.assert_called_once()

    def test_init_uses_env_var(self):
        # Test that __init__ uses the DB_CONN environment variable
        test_conn_str = "sqlite:///test_db.sqlite"
        with patch.dict("os.environ", {"DB_CONN": test_conn_str}):
            with patch("my_job.adapter.database_witer.create_engine") as mock_create_engine:
                DatabaseWriter()
                mock_create_engine.assert_called_once_with(test_conn_str)

    def test_init_uses_default_conn(self):
        # Test that __init__ uses the default connection string if env var is not set
        # We need to ensure DB_CONN is not set
        with patch.dict("os.environ", {}, clear=True):
            with patch("my_job.adapter.database_witer.create_engine") as mock_create_engine:
                DatabaseWriter()
                mock_create_engine.assert_called_once_with("sqlite:///production.db")
