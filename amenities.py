import time
import os
import overpy
import helpers
import nn_isochrones

def get_amenities(lat, lon, api, radius=500, allowed_amenities=None):
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

# Get amenities within a polygon defined by an isochrone
# an isochrone is a polygon that defines the area reachable within a given time
def get_amenities_by_isochrone(lat, lon, api, transport_type, distance_in_minutes = 15, allowed_amenities=None):
    isochrone = None
    if transport_type == "walking":
        isochrone = nn_isochrones.get_isochrone_by_walking_distance(lat, lon, distance_in_minutes)
    elif transport_type == "driving":
        isochrone = nn_isochrones.get_isochrone_by_driving_distance(lat, lon, distance_in_minutes)
    else:
        raise ValueError("transport_type must be 'walking' or 'driving'")
    
    polygon_coords = isochrone['features'][0]['geometry']['coordinates'][0]
    radius = helpers.farthest_distance_from_center(lat, lon, polygon_coords)
    print(f"distance: {radius} m")
    all_amenities = get_amenities(lat, lon, api, radius, allowed_amenities=allowed_amenities)
    amenities_to_keep = []
    for amenity in all_amenities:
        if helpers.within_polygon(polygon_coords, (amenity['lat'], amenity['lon'])):
            amenities_to_keep.append(amenity)
    return amenities_to_keep

def get_amenities_by_walking(lat, lon, api, distance_in_minutes = 15, allowed_amenities=None):
    return get_amenities_by_isochrone(lat, lon, api,"walking", distance_in_minutes, allowed_amenities=allowed_amenities)

def get_amenities_by_driving(lat, lon, api, distance_in_minutes = 15, allowed_amenities=None):
    return get_amenities_by_isochrone(lat, lon, api, "driving", distance_in_minutes, allowed_amenities=allowed_amenities)

def add_amenities_to_properties(input_file, output_file, transport_type, radius=500, distance_in_minutes=15, allowed_amenities=None):
    # load the rental properties from the json file
    rental_props = helpers.read_json_clean(input_file)
    api = overpy.Overpass()
    # if api limits are reached, we still want to save the data
    # so we will save every n properties
    save_every_n = 10
    iteration = 0
    current_data = []
    # get output file data if file already exists
    if os.path.exists(output_file):
        current_data = helpers.read_json_clean(output_file)
    #max_iterations = 2
    # for each property, get nearby allowed amenities
    for prop in rental_props:
        """ if iteration >= max_iterations:
            print("max iterations reached, stopping...")
            break """
        lat = prop.get("lat")
        lon = prop.get("lon")
        if lat is None or lon is None:
            prop["amenities"] = []
            continue
        # we skip properties that already have amenities, to avoid overwriting them and reducing api calls
        if len(current_data) > iteration and current_data[iteration] and current_data[iteration].get("amenities") and current_data[iteration].get("amenities") != []:
            prop["amenities"] = current_data[iteration]["amenities"]
            print(f"skipping {prop['address']} at ({lat}, {lon}), because it already has amenities")
            iteration += 1
            continue
        try:
            if transport_type == "walking":
                ams = get_amenities_by_walking(lat, lon, api, distance_in_minutes=distance_in_minutes, allowed_amenities=allowed_amenities)
            elif transport_type == "driving":
                ams = get_amenities_by_driving(lat, lon, api, distance_in_minutes=distance_in_minutes, allowed_amenities=allowed_amenities)
            else:
                ams = get_amenities(lat, lon, api, radius=radius, allowed_amenities=allowed_amenities)
            prop["amenities"] = ams
            print(f"amenities for {prop['address']} at ({lat}, {lon}): {len(ams)} found")
        except Exception as e:
            print(f"error for {prop['address']} at ({lat}, {lon}): {e}")
            prop["amenities"] = []
        
        time.sleep(3)  # pause to respect api limits
        iteration += 1
        if iteration % save_every_n == 0:
            print(f"saving {iteration} properties...")
            # save the data to a json file if api limits are reached
            # we will save the data every n properties to avoid losing data
            helpers.save_json_clean(output_file, rental_props)

    # write the updated data to a new json file
    helpers.save_json_clean(output_file, rental_props)

def main():
    input_file = 'rental_properties_geocoded.json'
    radiuses = [500, 2000, 5000]  # search radius in meters
    distances_in_minutes = [5, 10, 15]  # distance in minutes for isochrone
    transport_types = ["walking", "driving"]
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
    for index, distance_in_minutes in enumerate(distances_in_minutes):
        #get amenties for all types
        for transport_type in transport_types:
            print(f"getting amenities for {transport_type}...")
            if transport_type == "walking":
                output_file = f'rental_properties_with_walking_{distance_in_minutes}_amenities.json'
            elif transport_type == "driving":
                output_file = f'rental_properties_with_driving_{distance_in_minutes}_amenities.json'
            else:
                output_file = f'rental_properties_with_radius_{radiuses[index]}_amenities.json'
            add_amenities_to_properties(input_file, output_file, transport_type, radius=radiuses[index], distance_in_minutes=distance_in_minutes, allowed_amenities=allowed_amenities)
    print("all done!")


if __name__ == "__main__":
    main()
