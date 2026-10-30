"""
Utility functions for working with GeoJSON data in Respysive
"""


def filter_geojson(geojson, filter_func=None, properties=None):
    """Filter GeoJSON features based on properties.

    This function creates a subset of GeoJSON data by filtering features.
    Useful for creating regional views or thematic subsets that can be
    stored in separate hidden divs for optimized HTML size.

    Args:
        geojson (dict): GeoJSON FeatureCollection to filter
        filter_func (callable, optional): Function that takes a feature dict
            and returns True to include it. Example: lambda f: f['properties']['pop'] > 1000000
        properties (dict, optional): Dictionary of property key-value pairs to match.
            Features with ALL matching properties will be included.
            Example: {'continent': 'Europe'} or {'NAMEen': 'France'}

    Returns:
        dict: Filtered GeoJSON FeatureCollection with subset of features

    Examples:
        Filter by function::

            # Countries with population > 10M
            populous = filter_geojson(world_data,
                lambda f: f['properties'].get('pop', 0) > 10000000)

            # European countries
            europe = filter_geojson(world_data,
                lambda f: f['properties'].get('continent') == 'Europe')

        Filter by properties::

            # France only
            france = filter_geojson(world_data, properties={'NAMEen': 'France'})

            # France and Italy
            france_italy = filter_geojson(world_data,
                lambda f: f['properties'].get('NAMEen') in ['France', 'Italy'])

        Multiple filters::

            # European countries with high GDP
            rich_europe = filter_geojson(world_data,
                lambda f: (f['properties'].get('continent') == 'Europe' and
                          f['properties'].get('gdppc', 0) > 30000))

    Note:
        - Returns a new FeatureCollection with the same structure
        - Original data is not modified
        - If both filter_func and properties are provided, filter_func takes precedence
    """
    if not isinstance(geojson, dict) or geojson.get("type") != "FeatureCollection":
        raise ValueError("Input must be a GeoJSON FeatureCollection")

    features = geojson.get("features", [])

    if properties and not filter_func:

        def filter_func(feature):
            feat_props = feature.get("properties", {})
            return all(feat_props.get(key) == value for key, value in properties.items())

    if filter_func:
        filtered_features = [f for f in features if filter_func(f)]
    else:
        filtered_features = features.copy()

    return {"type": "FeatureCollection", "features": filtered_features}


def get_feature_property_values(geojson, property_name):
    """Get all unique values for a property across all features.

    Useful for discovering available values before filtering.

    Args:
        geojson (dict): GeoJSON FeatureCollection
        property_name (str): Name of the property to extract

    Returns:
        list: Sorted list of unique values for the property

    Examples:
        Find all country names::

            countries = get_feature_property_values(world_data, 'NAMEen')
            # ['Afghanistan', 'Albania', 'Algeria', ...]

        Find all continents::

            continents = get_feature_property_values(world_data, 'continent')
            # ['Africa', 'Asia', 'Europe', 'North America', ...]
    """
    if not isinstance(geojson, dict) or geojson.get("type") != "FeatureCollection":
        raise ValueError("Input must be a GeoJSON FeatureCollection")

    values = set()
    for feature in geojson.get("features", []):
        props = feature.get("properties", {})
        if property_name in props:
            values.add(props[property_name])

    return sorted(values)


def filter_geojson_bbox(geojson, bbox):
    """Filter features by bounding box.

    Args:
        geojson (dict): GeoJSON FeatureCollection
        bbox (list): Bounding box as [minx, miny, maxx, maxy]

    Returns:
        dict: Filtered GeoJSON FeatureCollection

    Example:
        # Europe bounding box (approximate)
        europe = filter_geojson_bbox(world_data, [-10, 35, 40, 70])
    """
    minx, miny, maxx, maxy = bbox

    def in_bbox(feature):
        geometry = feature.get("geometry", {})
        if geometry.get("type") == "Point":
            coords = geometry.get("coordinates", [])
            if len(coords) >= 2:
                lon, lat = coords[0], coords[1]
                return minx <= lon <= maxx and miny <= lat <= maxy
        return True

    return filter_geojson(geojson, filter_func=in_bbox)
