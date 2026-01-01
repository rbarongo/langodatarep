# import sys
# print(sys.path)

# from langodata.data_loader import load_sample_data


# def test_load_sample_data():
#     data = load_sample_data()

    
#     assert isinstance(data, list)
#     assert len(data) == 3
#     assert data[0]["value"] == "alpha"
from langodata.data_loader import load_sample_data


def test_load_sample_data_returns_expected_structure():
    """
    Verify that load_sample_data returns a list of dictionaries
    with the expected content.
    """
    data = load_sample_data()

    assert isinstance(data, list), "Expected data to be a list"
    assert len(data) == 3, "Expected exactly 3 records"

    first_record = data[0]
    assert isinstance(first_record, dict), "Each record should be a dictionary"
    assert first_record.get("value") == "alpha"