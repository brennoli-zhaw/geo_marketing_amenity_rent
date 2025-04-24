import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
import os


base_path = os.getcwd()
print (base_path)
path = os.path.join (base_path, "cleaned", "cleaned_rental_features_driving_3_amenities.csv")

# Read the CSV file into a DataFrame
df = pd.read_csv(path)
print("Initial DataFrame shape:", df.shape)
print("Columns:", df.columns.tolist())

# ----------------------
# 1. Data Cleaning & Conversion
# ----------------------

# Convert 'price' to a numeric column, creating 'price_numeric'
# In case there are non-numeric characters, errors will be coerced to NaN
df["price_numeric"] = pd.to_numeric(df["price"], errors="coerce")

# Clean the 'area' column
# Remove any non-digit or non-decimal characters (like "m²")
def clean_area(area_val):
    if pd.isnull(area_val):
        return 0
    area_str = str(area_val)
    # Remove non-digit/non-period characters
    num_str = re.sub(r"[^\d.]", "", area_str)
    try:
        return float(num_str) if num_str != "" else 0
    except ValueError:
        return 0

df["area_numeric"] = df["area"].apply(clean_area)

# Print summary after conversion
print("\nSummary after conversion:")
print(df[["price_numeric", "area_numeric"]].describe())

# ----------------------
# 2. Exploratory Data Analysis (EDA)
# ----------------------

# a) Summary statistics for the numeric features
print("\n--- Summary Statistics ---")
print(df.describe())

# b) Check for missing values
print("\n--- Missing Values per Column ---")
print(df.isnull().sum())

# c) Distribution plots

# Rental Price Distribution
plt.figure(figsize=(8, 5))
plt.hist(df["price_numeric"].dropna(), bins=20, color="skyblue", edgecolor="black")
plt.xlabel("Rental Price")
plt.ylabel("Frequency")
plt.title("Distribution of Rental Price")
plt.show()

# Area Distribution
plt.figure(figsize=(8, 5))
plt.hist(df["area_numeric"].dropna(), bins=20, color="lightgreen", edgecolor="black")
plt.xlabel("Area (m²)")
plt.ylabel("Frequency")
plt.title("Distribution of Property Area")
plt.show()

# d) Correlation Matrix
# We'll include price_numeric, area_numeric, and amenity count columns
allowed_amenities = [
    "cafe", "restaurant", "bar", "pub", "fast_food",
    "school", "university", "library", "hospital",
    "clinic", "pharmacy", "bank", "atm", "bus_station", "parking"
]

cols_for_corr = ["price_numeric", "area_numeric"]
for amenity in allowed_amenities:
    col_name = f"{amenity}_count"
    if col_name in df.columns:
        cols_for_corr.append(col_name)

corr_matrix = df[cols_for_corr].corr()
print("\n--- Correlation Matrix ---")
print(corr_matrix)

plt.figure(figsize=(10, 8))
plt.imshow(corr_matrix, cmap="viridis", interpolation="nearest")
plt.title("Correlation Matrix")
plt.colorbar()
plt.xticks(range(len(corr_matrix.columns)), corr_matrix.columns, rotation=90)
plt.yticks(range(len(corr_matrix.index)), corr_matrix.index)
plt.tight_layout()
plt.show()

# ----------------------
# 3. Remove Outliers & Prepare Data for Modeling
# ----------------------

# Remove rows with missing critical values
model_df = df.dropna(subset=["price_numeric", "area_numeric"]).copy()

# Remove outliers:
#   - Rental price above 9000
#   - Area above 300 m²
initial_rows = model_df.shape[0]
model_df = model_df[(model_df["price_numeric"] <= 9000) & (model_df["area_numeric"] <= 300)]
removed_rows = initial_rows - model_df.shape[0]
print(f"\nRemoved {removed_rows} rows as outliers based on rental price and area criteria.")

# Drop non-modeling columns if not needed (e.g., address, lat, lon, property_id, area)
cols_to_drop = ["address", "price", "lat", "lon", "property_id", "area"]
model_df.drop(columns=[col for col in cols_to_drop if col in model_df.columns], inplace=True)

# Fill any remaining missing numeric values with 0 (or consider other imputation)
numeric_cols = model_df.select_dtypes(include=[np.number]).columns
model_df[numeric_cols] = model_df[numeric_cols].fillna(0)

print("\n--- Modeling Data Sample ---")
print(model_df.head())
print("Final modeling data shape:", model_df.shape)

# Save the modeling data to a CSV file for later use in modeling
modeling_output_file = "modeling_data.csv"
model_df.to_csv(modeling_output_file, index=False)
print(f"Modeling data saved to '{modeling_output_file}'")
