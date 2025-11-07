from unittest.mock import patch
import pandas as pd
from app import collect_smhi_data

@patch("app.get_smhi_data")  # Mock get_smhi_data
def test_collect_smhi_data_success(mock_get):
    # return fake data
    mock_smhi_json = {
        "timeSeries": [
            {
                "validTime": "2025-11-08T12:00:00Z",
                "parameters": [
                    {"name": "t", "values": [4.9]}, # tests to be rounded since app.py does that
                    {"name": "pcat", "values": [1]}
                ]
            }
        ]
    }
    mock_get.return_value = (mock_smhi_json, "Success")

    # call function mockdata test
    df, status = collect_smhi_data(59.3293, 18.0686)

    # checks the function processed the mock data correctly
    assert status == "Success"
    assert isinstance(df, pd.DataFrame)
    assert df["Temperature (°C)"].iloc[0] == 5
    assert df["Rain or Snow"].iloc[0] == True
