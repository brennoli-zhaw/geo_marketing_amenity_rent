# Nearest neighbor functions
from sklearn.neighbors import BallTree
import numpy as np
from openrouteservice import client
import os

open_route_key = os.getenv("OPENROUTE")

def get_nearest(src_points, candidates, k_neighbors=1):
    """Find nearest neighbors for all source points from a set of candidate points"""

    # Create tree from the candidate points
    tree = BallTree(candidates, leaf_size=15, metric='haversine')

    # Find closest points and distances
    distances, indices = tree.query(src_points, k=k_neighbors)

    # Transpose to get distances and indices into arrays
    distances = distances.transpose()
    indices = indices.transpose()

    # Get closest indices and distances (i.e. array at index 0)
    # note: for the second closest points, you would take index 1, etc.
    closest = indices[0]
    closest_dist = distances[0]

    # Return indices and distances
    return (closest, closest_dist)


def nearest_neighbor(left_gdf, right_gdf, return_dist=False):
    """
    For each point in left_gdf, find closest point in right GeoDataFrame and return them.

    NOTICE: Assumes that the input Points are in WGS84 projection (lat/lon).
    """

    left_geom_col = left_gdf.geometry.name
    right_geom_col = right_gdf.geometry.name

    # Ensure that index in right gdf is formed of sequential numbers
    right = right_gdf.copy().reset_index(drop=True)

    # Parse coordinates from points and insert them into a numpy array as RADIANS
    left_radians = np.array(left_gdf[left_geom_col].apply(lambda geom: (geom.x * np.pi / 180, geom.y * np.pi / 180)).to_list())
    right_radians = np.array(right[right_geom_col].apply(lambda geom: (geom.x * np.pi / 180, geom.y * np.pi / 180)).to_list())

    # Find the nearest points
    # -----------------------
    # closest ==> index in right_gdf that corresponds to the closest point
    # dist ==> distance between the nearest neighbors (in meters)

    closest, dist = get_nearest(src_points=left_radians, candidates=right_radians)

    # Return points from right GeoDataFrame that are closest to points in left GeoDataFrame
    closest_points = right.loc[closest]

    # Ensure that the index corresponds the one in left_gdf
    closest_points = closest_points.reset_index(drop=True)

    # Add distance if requested
    if return_dist:
        # Convert to meters from radians
        earth_radius = 6371000  # meters
        closest_points['distance'] = dist * earth_radius

    return closest_points

def get_isochrone_by_query(query=None):
    if query is None:
        return None
    ors = client.Client(key=open_route_key)
    # Get isochrones for the given query
    isochrones = ors.isochrones(**query)
    return isochrones

def get_isochrone_by_walking_distance(lat, lon, distance=10):
    """
    Get isochrone for a given lat/lon and walking distance.

    :param lat: Latitude of the point
    :param lon: Longitude of the point
    :param distance: Walking distance in minutes
    :return: Isochrone GeoJSON object
    """
    profile='foot-walking'
    query = {
        'locations': [[lon, lat]],  # Note: OpenRouteService uses [lon, lat] order
        'range': [distance * 60],
        'attributes': ['area'],
        'profile': profile,
    }
    return get_isochrone_by_query(query)

def get_isochrone_by_driving_distance(lat, lon, distance=10):
    """
    Get isochrone for a given lat/lon and driving distance.

    :param lat: Latitude of the point
    :param lon: Longitude of the point
    :param distance: Driving distance in minutes
    :return: Isochrone GeoJSON object
    """
    profile='driving-car'
    query = {
        'locations': [[lon, lat]],  # Note: OpenRouteService uses [lon, lat] order
        'range': [distance * 60],
        'attributes': ['area'],
        'profile': profile,
    }
    return get_isochrone_by_query(query)
    