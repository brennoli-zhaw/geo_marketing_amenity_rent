import pandas as pd
import re
import glob
import os

# List of allowed amenities (as used when creating the features)
allowed_amenities = [
    "cafe", "restaurant", "bar", "pub", "fast_food",
    "school", "university", "library", "hospital",
    "clinic", "pharmacy", "bank", "atm", "bus_station", "parking"
]

def convert_area(value):

    if pd.isnull(value):
        return 0
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, str):
        num = re.findall(r'\d+\.?\d*', value)
        if num:
            return float(num[0])
    return 0

def clean_csv_file(file_path, output_dir="cleaned_features"):
    # Read CSV into DataFrame
    df = pd.read_csv(file_path)

    # If there is an "area" column, convert it to a numeric value
    if "area" in df.columns:
        df["area"] = df["area"].apply(convert_area)
    else:
        df["area"] = 0

    # Get a list of count columns from the allowed amenities
    count_cols = [f"{amenity}_count" for amenity in allowed_amenities if f"{amenity}_count" in df.columns]

    # Create a condition to mark rows for removal:
    # - If area_numeric is 0 OR if the sum of all amenity count columns is 0.
    condition = (df["area"] == 0) | (df[count_cols].sum(axis=1) == 0)

    # Create the cleaned DataFrame by removing rows that match the condition
    df_clean = df[~condition].copy()

    # Prepare output file name and save the cleaned DataFrame
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    base_name = os.path.basename(file_path)
    output_file = os.path.join(output_dir, "cleaned_" + base_name)
    df_clean.to_csv(output_file, index=False)
    
    removed = len(df) - len(df_clean)
    print(f"File: {file_path} -> {output_file} ({removed} rows removed)")

def main():
    # Adjust the pattern here if needed:
    input_files = glob.glob("features/features_*.csv")
    print(input_files)
    if not input_files:
        print("No files found matching the pattern 'rental_features_*.csv'")
        return
    for file_path in input_files:
        clean_csv_file(file_path)

if __name__ == "__main__":
    main()
