import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
import os
import glob

def sum_column(df, columns, sum_name, drop = False):
    df[sum_name] = df[columns].sum(axis=1)
    if drop:
        df = df.drop(columns, axis=1)
    return df

def amenity_present(df, columns, present_name, drop = False):
    df[present_name] = df[columns].sum(axis=1) >= 1
    df[present_name] = df[present_name].astype(int)
    df = df.dropna(subset=[present_name]).copy()
    if drop:
        df = df.drop(columns, axis=1)
    return df

def get_combined_count(df):
    model_df = df
    combined = {
        "food_beverage_count" : ['cafe_count', 'restaurant_count', 'bar_count', 'pub_count', 'fast_food_count'],
        "education_count" : ['school_count', 'university_count', 'library_count'],
        "healthcare_count" : ['hospital_count', 'clinic_count', 'pharmacy_count'],
        "financial_services_count" : ['bank_count', 'atm_count'],
        "transportation_count" : ['bus_station_count', 'parking_count']
    }
    allowed_columns = ["price", "area"]
    for key in combined:
        model_df = sum_column(model_df, combined[key], key)
        allowed_columns.append(key)
    model_df = model_df[allowed_columns]
    return model_df

def get_count(df):
    allowed_columns = [
        "price", "area",
        "cafe_count", "restaurant_count", "bar_count", "pub_count", "fast_food_count",
        "school_count", "university_count", "library_count", "hospital_count",
        "clinic_count", "pharmacy_count", "bank_count", "atm_count", "bus_station_count", "parking_count",
    ]
    model_df = df[allowed_columns]
    return model_df

def get_combined_present(df):
    model_df = df
    combined = {
        "food_beverage_present" : ['cafe_present', 'restaurant_present', 'bar_present', 'pub_present', 'fast_food_present'],
        "education_present" : ['school_present', 'university_present', 'library_present'],
        "healthcare_present" : ['hospital_present', 'clinic_present', 'pharmacy_present'],
        "financial_services_present" : ['bank_present', 'atm_present'],
        "transportation_present" : ['bus_station_present', 'parking_present']
    }
    allowed_columns = ["price", "area"]
    for key in combined:
        model_df = sum_column(model_df, combined[key], key)
        allowed_columns.append(key)
    model_df = model_df[allowed_columns]
    return model_df

def get_present(df):
    allowed_columns = [
        "price", "area",
        "cafe_present", "restaurant_present", "bar_present", "pub_present", "fast_food_present",
        "school_present", "university_present", "library_present", "hospital_present",
        "clinic_present", "pharmacy_present", "bank_present", "atm_present", "bus_station_present", "parking_present",
    ]
    model_df = df[allowed_columns]
    return model_df

def save_correlation_matrix(df, feature_type = "Correlation Matrix"):
    corr_matrix = df[df.columns].corr()
    price_correlations = corr_matrix['price']
    if sum(abs(price_correlations)) >= 2: 
        print(f"\n--- {feature_type} ---")
        print(corr_matrix)
        
    plt.figure(figsize=(10, 8))
    plt.imshow(corr_matrix, cmap="viridis", interpolation="nearest")
    plt.title(f"{feature_type}")
    plt.colorbar()
    plt.xticks(range(len(corr_matrix.columns)), corr_matrix.columns, rotation=90)
    plt.yticks(range(len(corr_matrix.index)), corr_matrix.index)
    plt.tight_layout()
    plt.savefig(f'correlation_matrices/{feature_type}.png')

def save_model_data(area_range, feature_type, show_correlation = False):
    base_path = os.getcwd()
    path = os.path.join (base_path, "cleaned_features", f"cleaned_features_{area_range}.csv")

    # Read the CSV file into a DataFrame
    df = pd.read_csv(path)

    # ----------------------
    # Remove Outliers & Prepare Data for Modeling
    # ----------------------

    # Remove rows with missing critical values
    model_df = df.dropna(subset=["price", "area"]).copy()

    # Remove outliers:
    #   - Rental price above 9000
    #   - Area above 300 m²
    initial_rows = model_df.shape[0]
    model_df = model_df[(model_df["price"] <= 9000) & (model_df["area"] <= 300)]
    removed_rows = initial_rows - model_df.shape[0]
    print(f"\nRemoved {removed_rows} rows as outliers based on rental price and area criteria.")

    # Drop non-modeling columns if not needed (e.g., address, lat, lon, property_id, area)
    cols_to_drop = ["address", "lat", "lon", "property_id", "rooms"]
    model_df.drop(columns=[col for col in cols_to_drop if col in model_df.columns], inplace=True)

    # Fill any remaining missing numeric values with 0 (or consider other imputation)
    numeric_cols = model_df.select_dtypes(include=[np.number]).columns
    model_df[numeric_cols] = model_df[numeric_cols].fillna(0)

    # Use select features for modeling
    model_df = globals()[f"get_{feature_type}"](model_df)
    """ print("\n--- Modeling Data Sample ---")
    print(model_df.head())
    print("Final modeling data shape:", model_df.shape) """
    if show_correlation:
        save_correlation_matrix(model_df, feature_type = f"{feature_type}_{area_range}")

    # Save the modeling data to a CSV file for later use in modeling
    modeling_output_file = f"modeling/{feature_type}_{area_range}.csv"
    model_df.to_csv(modeling_output_file, index=False)
    print(f"Modeling data saved to '{modeling_output_file}'")


#get_model_data("driving_2", "combined_count", show_correlation = True)
input_files = glob.glob("cleaned_features/cleaned_features_*.csv")
print(input_files)
if not input_files:
    print("No files found matching the pattern 'rental_features_*.csv'")
else:
    feature_types = ["combined_count", "count", "combined_present", "present"]
    for file_path in input_files:
        for f_type in feature_types:
            a_range = file_path.replace("cleaned_features\cleaned_features_", "").replace(".csv", "")
            save_model_data(a_range, f_type, show_correlation = True)