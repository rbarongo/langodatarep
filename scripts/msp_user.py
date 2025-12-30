from langodata.data_loader import load_sample_data

def main():
    data = load_sample_data()
    print("Manual test output:")
    for row in data:
        print(row)

if __name__ == "__main__":
    main()
