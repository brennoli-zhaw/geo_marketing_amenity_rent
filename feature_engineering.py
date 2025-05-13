import re
from helpers import read_json_clean, save_json_clean, parse_price
import json
import pandas as pd

# allowed amenities list
allowed_amenities = [
    "cafe",
    "restaurant",
    "bar",
    "pub",
    "fast_food",
    "school",
    "university",
    "library",
    "hospital",
    "clinic",
    "pharmacy",
    "bank",
    "atm",
    "bus_station",
    "parking"
]

def create_feature_dict(property_data):
    # create a dict of features from one property
    feat = {}
    feat['address'] = property_data.get('address', '')
    feat['price'] = property_data.get('price', '')
    feat['lat'] = property_data.get('lat', '')
    feat['lon'] = property_data.get('lon', '')
    feat['property_id'] = property_data.get('property_id', '')
    feat['rooms'] = property_data.get('rooms', 0)
    
    # Get the raw area value; if it's not provided, default to '0'
    raw_area = property_data.get('area', '0')
    # Ensure raw_area is a string, then remove non-digit characters (like "m²")
    raw_area_str = str(raw_area)
    area_numeric = re.sub(r'[^\d.]', '', raw_area_str)
    try:
        feat['area'] = float(area_numeric) if area_numeric != '' else 0
    except ValueError:
        feat['area'] = 0

    # initialize count and flag for each allowed amenity
    for amenity in allowed_amenities:
        feat[f"{amenity}_count"] = 0
        feat[f"{amenity}_present"] = 0

    amenities = property_data.get('amenities', [])
    for amenity in amenities:
        a_type = amenity.get("amenity", "").lower()
        if a_type in allowed_amenities:
            feat[f"{a_type}_count"] += 1
            feat[f"{a_type}_present"] = 1
    feat['total_amenities'] = len(amenities)
    return feat

def extract_and_save_amenities(properties, output_csv):
    """
    Extract amenity-level records from the list of properties and
    save them to a CSV file. Each record will include property_id,
    address, amenity type, name, and coordinates.
    """
    amenity_records = []
    for prop in properties:
        property_id = prop.get("property_id")
        rental_address = prop.get("address", "n/a")
        for amenity in prop.get("amenities", []):
            amenity_records.append({
                "property_id": property_id,
                "rental_address": rental_address,
                "amenity_type": amenity.get("amenity", "n/a"),
                "amenity_name": amenity.get("name", "n/a"),
                "lat": amenity.get("lat"),
                "lon": amenity.get("lon")
            })
    if amenity_records:
        df_amenities = pd.DataFrame(amenity_records)
        df_amenities.to_csv(output_csv, index=False)
        print("Amenities CSV saved to", output_csv)
    else:
        print("No amenities found to save.")

def main():
    input_dir = "property_amenities_area/"
    input_files = [
        f"{input_dir}property_isochrone_driving_1.json",
        f"{input_dir}property_isochrone_driving_2.json",
        f"{input_dir}property_isochrone_driving_3.json",
        f"{input_dir}property_isochrone_driving_5.json",
        f"{input_dir}property_isochrone_driving_7.json",
        f"{input_dir}property_isochrone_driving_10.json",
        f"{input_dir}property_radius_100.json",
        f"{input_dir}property_radius_250.json",
        f"{input_dir}property_radius_400.json",
        f"{input_dir}property_radius_500.json",
        f"{input_dir}property_radius_1000.json",
        f"{input_dir}property_radius_1500.json",
        f"{input_dir}property_isochrone_driving_1.json",
        f"{input_dir}property_isochrone_driving_2.json",
        f"{input_dir}property_isochrone_walking_3.json",
        f"{input_dir}property_isochrone_walking_5.json",
        f"{input_dir}property_isochrone_walking_7.json",
        f"{input_dir}property_isochrone_walking_10.json",   
    ]

    output_dir = "features/"
    output_feature_files = [
        f"{output_dir}features_driving_1.csv",
        f"{output_dir}features_driving_2.csv",
        f"{output_dir}features_driving_3.csv",
        f"{output_dir}features_driving_5.csv",
        f"{output_dir}features_driving_7.csv",
        f"{output_dir}features_driving_10.csv",
        f"{output_dir}features_radius_100.csv",
        f"{output_dir}features_radius_250.csv",
        f"{output_dir}features_radius_400.csv",
        f"{output_dir}features_radius_500.csv",
        f"{output_dir}features_radius_1000.csv",
        f"{output_dir}features_radius_1500.csv",
        f"{output_dir}features_walking_1.csv",
        f"{output_dir}features_walking_2.csv",
        f"{output_dir}features_walking_3.csv",
        f"{output_dir}features_walking_5.csv",
        f"{output_dir}features_walking_7.csv",
        f"{output_dir}features_walking_10.csv",
    ]

    # Process each JSON file to build the features dataframe
    for index, input_file in enumerate(input_files):
        output_csv = output_feature_files[index]
        # Load properties from the JSON file (one object per line)
        props = read_json_clean(input_file)
        # Build a list of feature dicts for each property
        features = [create_feature_dict(p) for p in props]
        # Create a dataframe from features
        df = pd.DataFrame(features)
        # Save the dataframe to CSV for property-level features
        df.to_csv(output_csv, index=False)
        print("Dataframe saved to", output_csv)
        print(df.head())
        
        # Optionally, also save a CSV with individual amenity records
        # This CSV will include coordinates which you can later load into QGIS.
        amenities_output = output_csv.replace("features", "amenities").replace("amenities/", "amenity_coordinates/")
        extract_and_save_amenities(props, amenities_output)

if __name__ == "__main__":
    main()
