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
    feat['price'] = property_data.get('prise', '')
    feat['lat'] = property_data.get('lat', '')
    feat['lon'] = property_data.get('lon', '')
    feat['property_id'] = property_data.get('property_id', '')
    feat['rooms'] = property_data.get('rooms', 0)
    feat['area'] = property_data.get('area', 0)
    
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

def main():
    input_file = 'rental_properties_with_driving_5_amenities.json'
    output_csv = 'rental_features.csv'
    
    # load properties from the json file (one object per line)
    props = read_json_clean(input_file)
    
    # build a list of feature dicts
    features = [create_feature_dict(p) for p in props]
    
    # create a dataframe from features
    df = pd.DataFrame(features)
    
    # save the dataframe to csv
    df.to_csv(output_csv, index=False)
    print("dataframe saved to", output_csv)
    print(df.head())

if __name__ == "__main__":
    main()
