import json
import time
import overpy

def get_amenities(lat, lon, radius, api, allowed_amenities=None):
    # query overpass for nodes with an amenity tag in the given radius
    if allowed_amenities:
        # build a regex pattern from the allowed amenities list
        pattern = "^(%s)$" % "|".join(allowed_amenities)
        filter_str = f'["amenity"~"{pattern}"]'
    else:
        filter_str = '["amenity"]'
    
    query = f"""
    [out:json];
    node(around:{radius},{lat},{lon}){filter_str};
    out;
    """
    result = api.query(query)
    amenities = []
    for node in result.nodes:
        amenity = {
            "id": node.id,
            "name": node.tags.get("name", "n/a"),
            "amenity": node.tags.get("amenity", "n/a"),
            "lat": float(node.lat),
            "lon": float(node.lon)
        }
        amenities.append(amenity)
    return amenities

def main():
    input_file = 'rental_properties_geocoded.json'
    output_file = 'rental_properties_with_filtered_amenities.json'
    radius = 500  # search radius in meters

    # list of allowed amenities to search for
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

    # load the rental properties from the json file
    rental_props = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                rental_props.append(json.loads(line.strip()))

    api = overpy.Overpass()

    # for each property, get nearby allowed amenities
    for prop in rental_props:
        lat = prop.get("lat")
        lon = prop.get("lon")
        if lat is None or lon is None:
            prop["amenities"] = []
            continue
        try:
            ams = get_amenities(lat, lon, radius, api, allowed_amenities=allowed_amenities)
            prop["amenities"] = ams
            print(f"amenities for {prop['address']} at ({lat}, {lon}): {len(ams)} found")
        except Exception as e:
            print(f"error for {prop['address']} at ({lat}, {lon}): {e}")
            prop["amenities"] = []
        time.sleep(1)  # pause to respect api limits

    # write the updated data to a new json file
    with open(output_file, 'w', encoding='utf-8') as f:
        for prop in rental_props:
            f.write(json.dumps(prop, ensure_ascii=False) + "\n")

    print(f"data saved to {output_file}")

if __name__ == "__main__":
    main()
