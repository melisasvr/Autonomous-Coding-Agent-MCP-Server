import pandas as pd

def print_stats(csv_file):
    try:
        # Read the CSV file
        df = pd.read_csv(csv_file)
        
        # Print basic stats
        print("Data Shape:", df.shape)
        print("Data Columns:", df.columns)
        print("Data Types:\n", df.dtypes)
        print("Summary Stats:\n", df.describe())
        
    except Exception as e:
        print("An error occurred: ", str(e))

# Example usage
print_stats('data.csv')