"""MapLibre GL JS map handler with iframe-based rendering."""

import html
import json
import uuid
from pathlib import Path
from typing import Any

from ..dependencies import CSS_URLS, JS_URLS, LOCAL_CSS_URLS, LOCAL_JS_URLS
from .base import BaseHandler

_STATIC = Path(__file__).parent.parent / "static"
_MAP_CSS = (_STATIC / "maplibre_map.css").read_text(encoding="utf-8")
_MAP_JS = (_STATIC / "maplibre_map.js").read_text(encoding="utf-8")


def _asset_url(kind, key):
    """URL of a library file, honouring set_local_js_urls/set_local_css_urls."""
    if kind == "css":
        return LOCAL_CSS_URLS.get(key, CSS_URLS[key])
    return LOCAL_JS_URLS.get(key, JS_URLS[key])


class MapLibreHandler(BaseHandler):
    """Handler for MapLibre GL JS interactive maps.

    Renders maps inside base64-encoded iframes to avoid RequireJS
    conflicts with Reveal.js. Supports markers, lines, circles,
    choropleth layers, legends, and OpenStreetMap tiles.

    Priority: 8.
    """

    @property
    def priority(self) -> int:
        return 8

    def can_handle(self, content: Any) -> bool:
        """Check if content is a MapLibre map configuration.

        Looks for MapLibre indicators: center/zoom keys, style URLs,
        openstreetmap flag, markers, lines, circles, or choropleth data.

        Args:
            content: Content to check.

        Returns:
            bool: True if content matches MapLibre configuration patterns.
        """
        if not isinstance(content, dict):
            return False

        maplibre_indicators = [
            "style" in content and isinstance(content.get("style"), str) and "http" in content["style"],
            all(key in content for key in ["center", "zoom"]) and "style" in content,
            content.get("openstreetmap") is True and all(key in content for key in ["center", "zoom"]),
            "markers" in content
            and isinstance(content["markers"], list)
            and len(content["markers"]) > 0
            and "coordinates" in content["markers"][0]
            and "center" in content,
            "lines" in content
            and isinstance(content["lines"], list)
            and len(content["lines"]) > 0
            and "coordinates" in content["lines"][0]
            and "center" in content,
            "circles" in content
            and isinstance(content["circles"], list)
            and len(content["circles"]) > 0
            and "coordinates" in content["circles"][0]
            and "value" in content["circles"][0]
            and "center" in content,
            "choropleth" in content
            and isinstance(content.get("choropleth"), dict)
            and "geojson" in content["choropleth"]
            and "colorProperty" in content["choropleth"]
            and "center" in content,
            "choropleth" in content
            and isinstance(content.get("choropleth"), dict)
            and "_cache_ref" in content["choropleth"]
            and "colorProperty" in content["choropleth"]
            and "center" in content,
            "legend" in content and "center" in content and "zoom" in content,
        ]

        return any(maplibre_indicators)

    def _prepare_config_with_references(self, config: dict) -> tuple[dict, dict]:
        """Replace GeoJSON references by cache entries.

        A reference names data stored on the slide (``Content.add_shared_data``)
        or on the deck (``Presentation.add_global_geojson``). Slide data is
        copied into the map. Deck data stays in the page once, and the map
        reads it when it is drawn; its id is recorded so that the deck can
        check it exists.

        Args:
            config: Map configuration dictionary.

        Returns:
            Tuple of (config with ``_cache_ref`` keys, GeoJSON cache dict).
        """
        config = {**config}
        cache = {}
        shared = getattr(self.content, "shared_data", {})

        def resolve(item, keys):
            ref = None
            for key in keys:
                value = item.get(key)
                if key == keys[0]:
                    if isinstance(value, str) and not value.lstrip().startswith("{"):
                        ref = value
                elif value:
                    ref = value
                    del item[key]
            if not ref:
                return
            item["_cache_ref"] = ref
            item.pop(keys[0], None)
            if ref in shared:
                cache[ref] = shared[ref]["data"]
            elif hasattr(self.content, "geojson_refs"):
                self.content.geojson_refs.add(ref)

        if config.get("choropleth"):
            config["choropleth"] = {**config["choropleth"]}
            resolve(config["choropleth"], ["geojson", "_geojson_ref", "_cache_ref"])
        for key in ("lines", "circles"):
            if config.get(key):
                config[key] = [{**item} for item in config[key]]
                for item in config[key]:
                    resolve(item, ["coordinates", "_coordinates_ref", "_cache_ref"])
        return config, cache

    def handle(self, content: Any, shared_data_id: str | None = None, forced: bool = False, **kwargs) -> str:
        """Render a MapLibre map as a base64-encoded iframe.

        Args:
            content: MapLibre configuration dictionary.
            shared_data_id: Unused. Present for interface compatibility.
            forced: Whether the handler was explicitly selected.
            **kwargs: Additional styling options.

        Returns:
            str: HTML string containing an iframe with the map.

        Raises:
            ValueError: If content is not a valid MapLibre configuration.
        """
        if not self.can_handle(content):
            raise ValueError("Content is not a valid MapLibre configuration")

        default_config = {
            "style": "https://demotiles.maplibre.org/style.json",
            "center": [0, 0],
            "zoom": 2,
            "height": "400px",
            "markers": [],
            "lines": [],
            "circles": [],
            "choropleth": None,
            "legend": None,
            "scale": True,
            "navigation": False,
            "openstreetmap": False,
        }

        config = {**default_config, **content}

        config, geojson_cache = self._prepare_config_with_references(config)

        if config.get("legend") and config["legend"].get("title"):
            title = config["legend"]["title"]
            if "\\n" in title:
                config["legend"]["title"] = title.replace("\\n", "\n")
                config["legend"]["_multiline"] = True
            elif "<br>" in title:
                config["legend"]["_useHTML"] = True

        container_id = f"maplibre-{str(uuid.uuid4())[:8]}"

        from respysive.utils import _parse_style_class

        center_style = {"class": ["d-flex", "justify-content-center", "mx-auto"]}
        combined_kwargs = {**center_style, **kwargs}
        style_attr = _parse_style_class(combined_kwargs)

        height = config.get("height", "400px")

        if config.get("openstreetmap", False):
            config["style"] = {
                "version": 8,
                "sources": {
                    "osm": {
                        "type": "raster",
                        "tiles": ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
                        "tileSize": 256,
                        "attribution": "&copy; OpenStreetMap Contributors",
                    }
                },
                "layers": [{"id": "osm", "type": "raster", "source": "osm"}],
            }

        def script_json(value):
            return json.dumps(value).replace("</", "<\\/")

        iframe_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>MapLibre Map</title>
<link href="{_asset_url("css", "maplibre")}" rel="stylesheet" />
<link href="{_asset_url("css", "fontawesome")}" rel="stylesheet" />
<style>{_MAP_CSS}</style>
</head>
<body>
<div id="map"></div>
<div id="legend-container"></div>
<script src="{_asset_url("js", "maplibre")}"></script>
<script>
var config = {script_json(config)};
var geojsonCache = {script_json(geojson_cache)};
{_MAP_JS}</script>
</body>
</html>"""

        # srcdoc (not a data: URL) keeps the iframe same-origin with the page,
        # so offline exports can share one copy of MapLibre between maps
        html_content = f"""
        <div {style_attr}>
            <iframe
                id="{container_id}"
                srcdoc="{html.escape(iframe_html, quote=True)}"
                style="height: {height}; width: 100%; border: none; border-radius: 8px;"
                frameborder="0">
            </iframe>
        </div>
        """

        return html_content
