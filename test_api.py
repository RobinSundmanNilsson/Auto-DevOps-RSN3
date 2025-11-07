from app import get_smhi_data

def test_get_smhi_data():
    data, status = get_smhi_data(59.3293, 18.0686)  # Call API
    assert status == "Success"                      # API call successful
    assert data is not None                         # Got data
    assert "timeSeries" in data                     # JSON structure
    assert isinstance(data["timeSeries"], list)     # timeSeries is list
    assert len(data["timeSeries"]) > 0              # Data in timeSeries