import json
import time
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

def geocode_address(address, geolocator, retries=3):
    # try to geocode the address, retry if needed
    for i in range(retries):
        try:
            # add ", switzerland" to improve accuracy
            return geolocator.geocode(address + ", switzerland")
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            print(f"error geocoding '{address}' (attempt {i+1}): {e}")
            time.sleep(1)
    return None

def main():
    input_file = 'rental_properties.json'
    output_file = 'rental_properties_geocoded.json'
    
    # load the rental properties from the file (one json per line)
    rental_properties = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                rental_properties.append(json.loads(line.strip()))
    
    # initialize the geolocator with a user agent
    geolocator = Nominatim(user_agent="rental_geocoder")

    # geocode each property and add lat/lon
    for prop in rental_properties:
        address = prop.get("address")
        location = geocode_address(address, geolocator)
        if location:
            prop["lat"] = location.latitude
            prop["lon"] = location.longitude
            print(f"geocoded: {address} -> ({location.latitude}, {location.longitude})")
        else:
            prop["lat"] = None
            prop["lon"] = None
            print(f"failed to geocode: {address}")
        # wait to respect api rate limits
        time.sleep(1)
    
    # write the updated properties to the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        for prop in rental_properties:
            f.write(json.dumps(prop, ensure_ascii=False) + "\n")
    
    print(f"geocoding complete. data saved to {output_file}")

if __name__ == "__main__":
    main()
