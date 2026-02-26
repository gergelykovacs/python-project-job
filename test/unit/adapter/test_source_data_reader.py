from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from my_job.adapter.source_data_reader import SourceDataReader


class TestSourceDataReader:
    @pytest.fixture
    def reader(self):
        return SourceDataReader()

    @patch("pandas.read_csv")
    def test_read_data_returns_dataframe(self, mock_read_csv, reader):
        # Mock pandas.read_csv to return a sample DataFrame
        mock_df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
        mock_read_csv.return_value = mock_df

        file_path = "test_data.csv"
        result = reader.read_data(file_path)

        # Verify read_csv was called with the correct path
        mock_read_csv.assert_called_once_with(file_path)

        # Verify the result is the mocked DataFrame
        pd.testing.assert_frame_equal(result, mock_df)

    @patch("pandas.read_csv")
    def test_read_data_logs_row_count(self, mock_read_csv, reader):
        # Mock pandas.read_csv
        mock_df = pd.DataFrame({"col1": [1, 2, 3]})
        mock_read_csv.return_value = mock_df

        # Mock the logger
        reader._logger = MagicMock()

        file_path = "test_data.csv"
        reader.read_data(file_path)

        # Verify logger was called with the correct message
        reader._logger.info.assert_called_once_with(f"Read 3 rows from {file_path}")

    @patch("pandas.read_csv")
    def test_read_data_empty_file(self, mock_read_csv, reader):
        # Mock an empty DataFrame
        mock_df = pd.DataFrame()
        mock_read_csv.return_value = mock_df

        # Mock the logger
        reader._logger = MagicMock()

        file_path = "empty.csv"
        result = reader.read_data(file_path)

        assert result.empty
        reader._logger.info.assert_called_once_with(f"Read 0 rows from {file_path}")

    def test_read_data_file_not_found(self, reader):
        # This test relies on pandas raising FileNotFoundError for a non-existent file
        # We don't mock read_csv here to test the actual exception propagation,
        # or we can mock the side_effect if we want to isolate from FS.
        # Given unit test best practices, mocking side_effect is preferred.

        with patch("pandas.read_csv", side_effect=FileNotFoundError("File not found")):
            with pytest.raises(FileNotFoundError):
                reader.read_data("non_existent.csv")
