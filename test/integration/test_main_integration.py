import os

import pandas as pd
import pytest
from prefect.testing.utilities import prefect_test_harness
from sqlalchemy import create_engine, text

from my_job.main import batch_job_main


class TestMainIntegration:
    @pytest.fixture
    def setup_test_environment(self, tmp_path):
        # Create a temporary CSV file
        csv_file = tmp_path / "test_sales_data.csv"
        df = pd.DataFrame(
            {
                "product_id": [1, 2, 3],
                "date": ["2023-01-01", "2023-01-02", "2023-01-03"],
                "quantity": [10, -5, 20],
                "price": [5.0, 10.0, 2.5],
                "status": ["pending", "error", "completed"],
            }
        )
        df.to_csv(csv_file, index=False)

        # Create a temporary SQLite database
        db_file = tmp_path / "test_db.sqlite"
        db_conn_str = f"sqlite:///{db_file}"

        # Set environment variables
        os.environ["SOURCE_DATA_PATH"] = str(csv_file)
        os.environ["DB_CONN"] = db_conn_str
        os.environ["PREFECT_SERVER_EPHEMERAL_STARTUP_TIMEOUT_SECONDS"] = "60"

        yield db_conn_str

        # Cleanup
        if os.path.exists(csv_file):
            os.remove(csv_file)
        if os.path.exists(db_file):
            os.remove(db_file)
        del os.environ["SOURCE_DATA_PATH"]
        del os.environ["DB_CONN"]
        del os.environ["PREFECT_SERVER_EPHEMERAL_STARTUP_TIMEOUT_SECONDS"]

    def test_batch_job_main(self, setup_test_environment):
        db_conn_str = setup_test_environment

        # Run the batch job
        with prefect_test_harness():
            batch_job_main()

        # Verify the results in the database
        engine = create_engine(db_conn_str)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM daily_sales")).fetchall()

            # We expect 2 rows (one filtered out due to negative quantity)
            assert len(result) == 2

            # Verify the content of the first row
            # Columns: product_id, date, quantity, price, status, total_cost
            # Row 1: 1, 2023-01-01, 10, 5.0, PENDING, 50.0
            row1 = result[0]
            assert row1[0] == 1
            assert row1[2] == 10
            assert row1[4] == "PENDING"
            assert row1[5] == 50.0

            # Verify content of the second row
            # Row 3: 3, 2023-01-03, 20, 2.5, COMPLETED, 50.0
            row2 = result[1]
            assert row2[0] == 3
            assert row2[2] == 20
            assert row2[4] == "COMPLETED"
            assert row2[5] == 50.0
