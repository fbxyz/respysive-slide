"""Plotly chart handler."""

import json
from typing import Any

from .base import BaseHandler


class PlotlyHandler(BaseHandler):
    """Handler for Plotly charts and figures.

    Accepts Plotly Figure objects, JSON strings, or dictionaries containing
    a ``data`` list and an optional ``layout`` dict. Delegates rendering
    to Content.add_plotly.

    Priority: 20.
    """

    @property
    def priority(self) -> int:
        return 20

    def can_handle(self, content: Any) -> bool:
        """Check if content is a Plotly chart.

        Accepts Figure objects, dicts with a ``data`` key containing
        known trace types, or JSON strings with Plotly structure.

        Args:
            content: Content to check.

        Returns:
            bool: True if content matches Plotly structure.
        """
        return self._is_plotly_structure(content)

    def _is_plotly_structure(self, content: Any) -> bool:
        """Test whether content matches a Plotly data structure.

        Args:
            content: Object to test (dict, str, or Figure-like).

        Returns:
            bool: True if the structure contains Plotly traces.
        """

        def _check_plotly_dict(data):
            if not isinstance(data, dict):
                return False
            if "data" not in data:
                return False
            if not isinstance(data["data"], list):
                return False

            if len(data["data"]) > 0:
                plotly_types = {
                    "scatter",
                    "bar",
                    "line",
                    "histogram",
                    "box",
                    "violin",
                    "heatmap",
                    "contour",
                    "surface",
                    "mesh3d",
                    "scatter3d",
                    "choropleth",
                    "scattergeo",
                    "pie",
                    "sunburst",
                    "treemap",
                    "sankey",
                    "waterfall",
                    "funnel",
                    "indicator",
                    "scattergl",
                    "histogram2d",
                    "histogram2dcontour",
                    "parcoords",
                    "parcats",
                    "choroplethmap",
                    "scattermap",
                    "scattermapbox",
                }

                for trace in data["data"]:
                    if isinstance(trace, dict) and "type" in trace:
                        if trace["type"] in plotly_types:
                            return True
                    elif isinstance(trace, dict) and any(
                        key in trace for key in ["x", "y", "z", "locations", "values"]
                    ):
                        return True

            return "layout" in data

        if isinstance(content, str):
            try:
                parsed_data = json.loads(content)
                return _check_plotly_dict(parsed_data)
            except (json.JSONDecodeError, ValueError):
                return '{"data":[{' in content or '"data":' in content
        elif isinstance(content, dict):
            return _check_plotly_dict(content)
        else:
            try:
                if hasattr(content, "to_json") and hasattr(content, "data") and hasattr(content, "layout"):
                    return True
            except Exception:
                pass

        return False

    def handle(self, content: Any, shared_data_id: str | None = None, forced: bool = False, **kwargs) -> str:
        """Render a Plotly chart as an interactive HTML element.

        Args:
            content: Plotly Figure, dict, or JSON string.
            shared_data_id: Optional shared GeoJSON data identifier for
                choropleth maps.
            forced: Whether the handler was explicitly selected.
            **kwargs: Additional styling options (width, height, class, etc.).

        Returns:
            str: HTML string with Plotly.js initialization script.

        Raises:
            ValueError: If content is not a valid Plotly chart.
        """
        if not forced and not self.can_handle(content):
            raise ValueError("Content is not a valid Plotly chart")

        center_style = {"class": ["d-flex", "justify-content-center", "mx-auto"]}
        combined_kwargs = {**center_style, **kwargs}

        from respysive.content import Content

        temp_content = Content()
        if hasattr(self.content, "shared_data"):
            temp_content.shared_data = self.content.shared_data

        temp_content.add_plotly(content, shared_data_id=shared_data_id, **combined_kwargs)

        return temp_content.content
