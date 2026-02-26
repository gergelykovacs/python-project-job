from unittest.mock import MagicMock

import pandas as pd
import pytest

from my_job.service.data_transformer import DataTransformer


class TestDataTransformer:
    @pytest.fixture
    def transformer(self):
        return DataTransformer()

    @pytest.fixture
    def sample_dataframe(self):
        return pd.DataFrame(
            {
                "product_id": [1, 2, 3, 4],
                "quantity": [10, -5, 0, 5],
                "price": [5.0, 10.0, 20.0, 2.5],
                "status": ["pending", "error", "processing", "completed"],
            }
        )

    def test_transform_data_calculates_total_cost(self, transformer, sample_dataframe):
        result = transformer.transform_data(sample_dataframe)

        # Check if total_cost column exists
        assert "total_cost" in result.columns

        # Verify calculation for valid rows
        # Row 1: 10 * 5.0 = 50.0
        # Row 4: 5 * 2.5 = 12.5
        assert result.iloc[0]["total_cost"] == 50.0
        assert result.iloc[1]["total_cost"] == 12.5

    def test_transform_data_uppercases_status(self, transformer, sample_dataframe):
        result = transformer.transform_data(sample_dataframe)

        # Verify status is uppercase
        assert result.iloc[0]["status"] == "PENDING"
        assert result.iloc[1]["status"] == "COMPLETED"

    def test_transform_data_filters_invalid_quantity(self, transformer, sample_dataframe):
        result = transformer.transform_data(sample_dataframe)

        # Original has 4 rows, 2 have quantity <= 0
        assert len(result) == 2

        # Verify only positive quantities remain
        assert all(result["quantity"] > 0)

        # Verify specific rows remained (ID 1 and 4)
        assert 1 in result["product_id"].values
        assert 4 in result["product_id"].values
        assert 2 not in result["product_id"].values
        assert 3 not in result["product_id"].values

    def test_transform_data_logs_filtered_count(self, transformer, sample_dataframe):
        # Mock the logger
        transformer._logger = MagicMock()

        transformer.transform_data(sample_dataframe)

        # Verify logger was called with correct message
        # 4 total rows - 2 valid rows = 2 filtered rows
        transformer._logger.info.assert_called_once_with("Filtered 2 invalid rows")

    def test_transform_data_empty_dataframe(self, transformer):
        empty_df = pd.DataFrame(columns=["product_id", "quantity", "price", "status"])
        result = transformer.transform_data(empty_df)

        assert len(result) == 0
        assert "total_cost" in result.columns
