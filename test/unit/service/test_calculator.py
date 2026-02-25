import pytest


@pytest.fixture
def mock_data():
    return {"key": "value"}


def test_placeholder(mock_data):
    pass
