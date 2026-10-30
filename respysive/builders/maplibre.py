"""MapLibre map configuration builder."""

from respysive.errors import ParameterValidationError, validate_maplibre_parameters


class MapLibreBuilder:
    """Builder for MapLibre GL JS map configurations.

    Handles creation of various map types including basic marker maps,
    line/flow maps, circle/bubble maps, and choropleth maps.

    Args:
        content_obj: Content object for data storage
    """

    def __init__(self, content_obj):
        """Initialize with a Content instance for data storage.

        Args:
            content_obj: Content instance used for shared data management.
        """
        self.content_obj = content_obj

    def build_map_config(
        self, center, zoom=10, style=None, markers=None, legend=None, openstreetmap=False, scale=True, navigation=True
    ):
        """Build configuration for basic MapLibre map with markers.

        Args:
            center: Center coordinates [longitude, latitude]
            zoom: Zoom level
            style: Map style URL
            markers: List of marker dictionaries
            legend: Legend configuration dictionary
            openstreetmap: Use OpenStreetMap background
            scale: Show scale control
            navigation: Show navigation controls

        Returns:
            dict: MapLibre configuration object
        """
        validate_maplibre_parameters(center, zoom, "build_map_config")

        if style is None:
            style = "https://demotiles.maplibre.org/style.json"

        if markers is None:
            markers = []

        maplibre_config = {
            "center": center,
            "zoom": zoom,
            "markers": markers,
            "scale": scale,
            "navigation": navigation,
            "openstreetmap": openstreetmap,
        }

        if not openstreetmap:
            maplibre_config["style"] = style

        if legend:
            maplibre_config["legend"] = legend

        return maplibre_config

    def build_lines_map_config(
        self, center, zoom=10, lines=None, markers=None, legend=None, openstreetmap=False, scale=True, navigation=True
    ):
        """Build configuration for MapLibre map with variable width lines.

        Args:
            center: Center coordinates [longitude, latitude]
            zoom: Zoom level
            lines: List of line dictionaries with coordinates, width, color, popup
            markers: List of marker dictionaries
            legend: Legend configuration dictionary
            openstreetmap: Use OpenStreetMap background
            scale: Show scale control
            navigation: Show navigation controls

        Returns:
            dict: MapLibre configuration object
        """
        validate_maplibre_parameters(center, zoom, "build_lines_map_config")

        if lines is None:
            lines = []

        if markers is None:
            markers = []

        maplibre_config = {
            "center": center,
            "zoom": zoom,
            "lines": lines,
            "markers": markers,
            "scale": scale,
            "navigation": navigation,
            "openstreetmap": openstreetmap,
        }

        if legend:
            maplibre_config["legend"] = legend

        return maplibre_config

    def build_circles_map_config(
        self,
        center,
        zoom=10,
        circles=None,
        markers=None,
        legend=None,
        openstreetmap=False,
        scale=True,
        navigation=True,
        min_radius=5,
        max_radius=50,
    ):
        """Build configuration for MapLibre map with proportional circles.

        Circle radius is calculated as square root of value.

        Args:
            center: Center coordinates [longitude, latitude]
            zoom: Zoom level
            circles: List of circle dictionaries with coordinates, value, color, popup
            markers: List of marker dictionaries
            legend: Legend configuration dictionary
            openstreetmap: Use OpenStreetMap background
            scale: Show scale control
            navigation: Show navigation controls
            min_radius: Minimum radius in pixels
            max_radius: Maximum radius in pixels

        Returns:
            dict: MapLibre configuration object
        """
        validate_maplibre_parameters(center, zoom, "build_circles_map_config")

        if circles is None:
            circles = []

        if markers is None:
            markers = []

        maplibre_config = {
            "center": center,
            "zoom": zoom,
            "circles": circles,
            "markers": markers,
            "scale": scale,
            "navigation": navigation,
            "openstreetmap": openstreetmap,
            "minRadius": min_radius,
            "maxRadius": max_radius,
        }

        if legend:
            maplibre_config["legend"] = legend

        return maplibre_config

    def build_choropleth_map_config(
        self,
        center,
        zoom=10,
        geojson=None,
        color_property=None,
        color_rules=None,
        legend=None,
        openstreetmap=False,
        scale=True,
        navigation=True,
        popup=None,
    ):
        """Build configuration for MapLibre choropleth map.

        Args:
            center: Center coordinates [longitude, latitude]
            zoom: Zoom level
            geojson: GeoJSON data dictionary
            color_property: Property name for coloring
            color_rules: List of color rule dictionaries
            legend: Legend configuration dictionary
            openstreetmap: Use OpenStreetMap background
            scale: Show scale control
            navigation: Show navigation controls
            popup: Popup template string with property variables

        Returns:
            dict: MapLibre configuration object

        Raises:
            ParameterValidationError: If geojson or color_property is missing
        """
        validate_maplibre_parameters(center, zoom, "build_choropleth_map_config")

        if not geojson or not color_property:
            if not geojson:
                raise ParameterValidationError(
                    "geojson",
                    "None or empty",
                    "is required for choropleth maps",
                    "Provide GeoJSON data with geographic features",
                    "build_choropleth_map_config",
                )
            if not color_property:
                raise ParameterValidationError(
                    "color_property",
                    "None or empty",
                    "is required for choropleth maps",
                    "Specify the property name to use for coloring (e.g., 'population', 'density')",
                    "build_choropleth_map_config",
                )

        maplibre_config = {
            "center": center,
            "zoom": zoom,
            "choropleth": {
                "geojson": geojson,
                "colorProperty": color_property,
                "colorRules": color_rules or [],
                "popup": popup,
                "fillOpacity": 0.7,
                "strokeColor": "#ffffff",
                "strokeWidth": 1,
                "showBorders": True,
            },
            "scale": scale,
            "navigation": navigation,
            "openstreetmap": openstreetmap,
        }

        if legend:
            maplibre_config["legend"] = legend

        return maplibre_config

    def build_choropleth_with_data_join_config(
        self,
        center,
        zoom=10,
        geojson_id=None,
        join_data=None,
        join_key=None,
        color_property=None,
        color_rules=None,
        legend=None,
        openstreetmap=False,
        scale=True,
        navigation=True,
        popup=None,
    ):
        """Build configuration for optimized MapLibre choropleth map with data join.

        Uses cache system to avoid GeoJSON data duplication.

        Args:
            center: Center coordinates [longitude, latitude]
            zoom: Zoom level
            geojson_id: Reference ID to global GeoJSON data
            join_data: Data dictionary to join with geometry
            join_key: Common key for joining
            color_property: Property to use for coloring after join
            color_rules: List of color rule dictionaries
            legend: Legend configuration dictionary
            openstreetmap: Use OpenStreetMap background
            scale: Show scale control
            navigation: Show navigation controls
            popup: Popup HTML template with variables

        Returns:
            dict: MapLibre configuration object

        Raises:
            ParameterValidationError: If geojson_id is missing
        """
        validate_maplibre_parameters(center, zoom, "build_choropleth_with_data_join_config")

        if not geojson_id:
            raise ParameterValidationError(
                "geojson_id",
                "None or empty",
                "is required for optimized choropleth maps",
                "Provide the ID of GeoJSON data added via presentation.add_global_geojson()",
                "build_choropleth_with_data_join_config",
            )

        config = {
            "center": center,
            "zoom": zoom,
            "openstreetmap": openstreetmap,
            "scale": scale,
            "navigation": navigation,
            "choropleth": {
                "_cache_ref": geojson_id,
                "joinData": join_data,
                "joinKey": join_key,
                "colorProperty": color_property,
                "colorRules": color_rules or [],
                "defaultColor": "#cccccc",
                "fillOpacity": 0.7,
                "strokeColor": "#ffffff",
                "strokeWidth": 1,
                "showBorders": True,
                "popup": popup,
            },
        }

        if legend:
            config["legend"] = legend

        return config
