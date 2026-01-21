"""
Geospatial calculation module for determining latitude, longitude, and directional information.
Uses GeoPandas to query India places shapefile and calculate bearings between locations.
"""

import geopandas as gpd
import math
from pathlib import Path

# Initialize geodataframe from shapefile
BASE_DIR = Path(__file__).resolve().parent.parent.parent
SHAPEFILE = BASE_DIR / "static" / "shp" / "india_places.shp"

gdf = gpd.read_file(SHAPEFILE)
gdf = gdf.to_crs(epsg=4326)  # Ensure coordinates are in WGS84 (lat/lon)


def get_lat_lon(place: str) -> tuple:
    """
    Get latitude and longitude for a given place name.
    
    Args:
        place (str): Place name to search for (case-insensitive)
    
    Returns:
        tuple: (latitude, longitude) or None if place not found
    """
    row = gdf[gdf["name"].str.lower() == place.lower()]
    
    if row.empty:
        return None
    
    geom = row.geometry.iloc[0]
    
    # If polygon, convert to centroid
    if geom.geom_type != "Point":
        geom = geom.centroid
    
    return geom.y, geom.x  # lat, lon


def calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate bearing (direction in degrees) from one coordinate to another.
    
    Args:
        lat1, lon1 (float): Starting latitude and longitude
        lat2, lon2 (float): Destination latitude and longitude
    
    Returns:
        float: Bearing in degrees (0-360, where 0/360 = North)
    """
    lat1, lat2 = map(math.radians, [lat1, lat2])
    dlon = math.radians(lon2 - lon1)
    
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - \
        math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    
    bearing = (math.degrees(math.atan2(x, y)) + 360) % 360
    return bearing


def bearing_to_direction(bearing: float) -> str:
    """
    Convert bearing (degrees) to cardinal direction name.
    
    Args:
        bearing (float): Bearing in degrees (0-360)
    
    Returns:
        str: Direction name (e.g., "North", "East", "South", "West")
    """
    directions = [
        "North",
        "East",
        "South",
        "West"
    ]
    return directions[round(bearing / 90) % 4]


def get_direction_info(source: str, destination: str) -> dict:
    """
    Get directional information between two places.
    
    Args:
        source (str): Starting place name
        destination (str): Destination place name
    
    Returns:
        dict: {
            "bearing_degree": float (0-360),
            "direction": str (cardinal/ordinal direction)
        }
        Returns None if either place is not found
    """
    src = get_lat_lon(source)
    dest = get_lat_lon(destination)
    
    if not src or not dest:
        return None
    
    bearing = calculate_bearing(src[0], src[1], dest[0], dest[1])
    direction = bearing_to_direction(bearing)
    
    return {
        "bearing_degree": round(bearing, 2),
        "direction": direction,
    }