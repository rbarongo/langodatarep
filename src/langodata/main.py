from langodata.config import APP_NAME, ENV
from langodata.data_loader import load_sample_data


def run():
    print(f"Starting {APP_NAME} in {ENV} mode")

    data = load_sample_data()
    print("Loaded data:")
    for row in data:
        print(row)


if __name__ == "__main__":
    run()