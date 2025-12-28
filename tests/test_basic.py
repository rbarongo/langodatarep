from langodata.data_loader import load_sample_data

def test_load_sample_data():
    data = load_sample_data()

    assert isinstance(data, list)
    assert len(data) == 3
    assert data[0]["value"] == "alpha"