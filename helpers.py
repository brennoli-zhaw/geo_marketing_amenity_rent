import json
import re
import pyproj
from shapely.geometry import Point, Polygon, LineString

def save_json_clean(file_name, dt_to_save):
    if not dt_to_save:
        print("No data to save.")
        return
    if not isinstance(dt_to_save, list):
        print("Data to save should be a list.")
        return
    # write the updated properties to the output file
    with open(file_name, 'w', encoding='utf-8') as f:
        for prop in dt_to_save:
            f.write(json.dumps(prop, ensure_ascii=False) + "\n")
    print(f"geocoding complete. data saved to {file_name}")

def read_json_clean(file_name):
    # load the rental properties from the file (one json per line)
    rental_properties = []
    with open(file_name, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                rental_properties.append(json.loads(line.strip()))
    return rental_properties

def parse_price(price_str):
    # convert price string like "chf 2’880.– / monat" to an int
    price_str = price_str.replace("CHF", "").replace("–", "").replace("’", "").strip()
    match = re.search(r'(\d+)', price_str)
    return int(match.group(1)) if match else None

def has_numbers(inputString):
    return any(char.isdigit() for char in inputString)

def within_polygon(polygon_coords, point):
    """
    Check if a point is within a polygon defined by its coordinates.
    :param polygon_coords: List of (lat, lon) tuples defining the polygon vertices
    :param point: (lat, lon) tuple of the point to check
    :return: True if the point is within the polygon, False otherwise
    """
    #convert point array to tuple
    if isinstance(point, list) and len(point) == 2:
        point = tuple(point)
    #convert polygon_coords array to list of tuples
    if isinstance(polygon_coords, list) and all(isinstance(coord, list) and len(coord) == 2 for coord in polygon_coords):
        polygon_coords = [tuple(coord) for coord in polygon_coords]
    #check if point is a tuple of (lat, lon)
    if not isinstance(point, tuple) or len(point) != 2:
        raise ValueError("point must be a (lat, lon) tuple")
    #check if polygon_coords is a list of tuples
    if not isinstance(polygon_coords, list) or not all(isinstance(coord, tuple) and len(coord) == 2 for coord in polygon_coords):
        raise ValueError("polygon_coords must be a list of (lat, lon) tuples")

    polygon = Polygon(polygon_coords)
    point = Point(point[1], point[0])  # Note: Point takes (lon, lat)
    
    return polygon.contains(point)

def farthest_distance_from_center(lat, lon, polygon_coords):
    """
    Calculate the farthest distance from the center of a polygon defined by its coordinates.
    :param polygon_coords: List of (lat, lon) tuples defining the polygon vertices
    :return: Farthest distance from the center of the polygon to its vertices in meters
    """
    # Convert polygon_coords array to list of tuples
    if isinstance(polygon_coords, list) and all(isinstance(coord, list) and len(coord) == 2 for coord in polygon_coords):
        polygon_coords = [tuple(coord) for coord in polygon_coords]
    
    # Check if polygon_coords is a list of tuples
    if not isinstance(polygon_coords, list) or not all(isinstance(coord, tuple) and len(coord) == 2 for coord in polygon_coords):
        raise ValueError("polygon_coords must be a list of (lat, lon) tuples")
    
    # calculate the farthest distance from coordinates to the farthest point in the polygon in meters
    polygon = Polygon(polygon_coords)
    center = Point(lon, lat)  # Note: Point takes (lon, lat)
    vertex = polygon.exterior.coords

    #calculate all distances from centroid to polygon vertex
    distances=[LineString([center, v]).length for v in vertex]
    farthest_point = Point(vertex[distances.index(max(distances))])
    
    #convert max_distance to meters using pyproj
    geod = pyproj.Geod(ellps="WGS84")
    _, _, max_distance = geod.inv(center.x, center.y, farthest_point.x, farthest_point.y)

    return max_distance  # Convert to meters (assuming the CRS is in degrees)