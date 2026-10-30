"""
Pytest configuration file for respysive-slide tests.

This file contains shared fixtures, configuration, and setup
for the test suite.
"""

import os
import shutil
import sys
import tempfile
from unittest.mock import Mock, patch

import pytest

# Add the parent directory to the Python path so we can import respysive
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture
def temp_directory():
    """
    Provide a temporary directory for tests that need to create files.

    The directory is automatically cleaned up after the test.
    """
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_geojson():
    """Provide sample GeoJSON data for testing."""
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"name": "Test Location", "value": 100, "population": 50000},
                "geometry": {"type": "Point", "coordinates": [2.3522, 48.8566]},
            },
            {
                "type": "Feature",
                "properties": {"name": "Another Location", "value": 200, "population": 75000},
                "geometry": {"type": "Point", "coordinates": [2.3376, 48.8606]},
            },
        ],
    }


@pytest.fixture
def sample_plotly_data():
    """Provide sample Plotly chart data for testing."""
    return {
        "data": [
            {"x": [1, 2, 3, 4], "y": [10, 11, 12, 13], "type": "scatter", "mode": "lines+markers", "name": "Test Data"}
        ],
        "layout": {"title": "Test Chart", "xaxis": {"title": "X Axis"}, "yaxis": {"title": "Y Axis"}},
    }


@pytest.fixture
def sample_altair_data():
    """Provide sample Altair/Vega-Lite data for testing."""
    return {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "description": "A simple bar chart with embedded data.",
        "data": {
            "values": [
                {"a": "A", "b": 28},
                {"a": "B", "b": 55},
                {"a": "C", "b": 43},
                {"a": "D", "b": 91},
                {"a": "E", "b": 81},
                {"a": "F", "b": 53},
                {"a": "G", "b": 19},
                {"a": "H", "b": 87},
                {"a": "I", "b": 52},
            ]
        },
        "mark": "bar",
        "encoding": {
            "x": {"field": "a", "type": "ordinal", "axis": {"labelAngle": 0}},
            "y": {"field": "b", "type": "quantitative"},
        },
    }


@pytest.fixture
def mock_matplotlib_figure():
    """Provide a mock matplotlib figure for testing."""
    with patch("matplotlib.pyplot.figure") as mock_fig:
        # Create a mock figure with basic attributes
        mock_figure = Mock()
        mock_figure.get_size_inches.return_value = (6, 4)
        mock_figure.set_size_inches = Mock()
        mock_figure.savefig = Mock()
        mock_fig.return_value = mock_figure
        yield mock_figure


@pytest.fixture
def sample_maplibre_configs():
    """Provide various MapLibre configuration examples."""
    return {
        "basic": {"center": [2.3522, 48.8566], "zoom": 10, "openstreetmap": True},
        "with_markers": {
            "center": [2.3522, 48.8566],
            "zoom": 12,
            "openstreetmap": True,
            "markers": [
                {
                    "coordinates": [2.3522, 48.8566],
                    "icon": "fas fa-tower-broadcast",
                    "color": "#e74c3c",
                    "popup": "Eiffel Tower",
                }
            ],
        },
        "with_lines": {
            "center": [2.3522, 48.8566],
            "zoom": 11,
            "openstreetmap": True,
            "lines": [
                {
                    "coordinates": [[2.3522, 48.8566], [2.3376, 48.8606]],
                    "width": 6,
                    "color": "#e74c3c",
                    "popup": "Metro Line",
                }
            ],
        },
        "with_circles": {
            "center": [2.3522, 48.8566],
            "zoom": 8,
            "openstreetmap": True,
            "circles": [
                {"coordinates": [2.3522, 48.8566], "value": 2200000, "color": "#e74c3c", "popup": "Paris: 2.2M people"}
            ],
            "minRadius": 10,
            "maxRadius": 50,
        },
    }


@pytest.fixture
def sample_custom_content_configs():
    """Provide sample custom content configurations."""
    return {
        "leaflet": {
            "library": "leaflet",
            "config": {"center": [48.8566, 2.3522], "zoom": 12},
            "cdn": {
                "css": ["https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"],
                "js": ["https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"],
            },
            "init_script": "var map = L.map(parsedConfig.container).setView(parsedConfig.center, parsedConfig.zoom);",
            "div_style": {"height": "400px"},
        },
        "chartjs": {
            "library": "chartjs",
            "config": {
                "type": "bar",
                "data": {
                    "labels": ["Red", "Blue", "Yellow", "Green", "Purple", "Orange"],
                    "datasets": [{"label": "# of Votes", "data": [12, 19, 3, 5, 2, 3]}],
                },
            },
            "cdn": {"js": ["https://cdn.jsdelivr.net/npm/chart.js"]},
            "init_script": "var ctx = document.getElementById(parsedConfig.container).getContext('2d'); new Chart(ctx, parsedConfig);",
            "div_style": {"height": "300px"},
        },
    }


# Test markers for categorizing tests
pytest_markers = [
    "unit: marks tests as unit tests",
    "integration: marks tests as integration tests",
    "slow: marks tests as slow running",
    "maplibre: marks tests related to MapLibre functionality",
    "handlers: marks tests related to the handler system",
    "presentation: marks tests related to Presentation class",
    "slide: marks tests related to Slide class",
    "utilities: marks tests related to utility functions",
]


# Configure pytest markers
def pytest_configure(config):
    """Configure pytest markers."""
    for marker in pytest_markers:
        config.addinivalue_line("markers", marker)


# Skip tests that require external dependencies if they're not available
def pytest_runtest_setup(item):
    """Set up individual test runs with dependency checks."""
    if item.get_closest_marker("requires_matplotlib"):
        pytest.importorskip("matplotlib")

    if item.get_closest_marker("requires_plotly"):
        pytest.importorskip("plotly")

    if item.get_closest_marker("requires_network"):
        # Skip network-dependent tests in CI or offline environments
        if os.environ.get("CI") or os.environ.get("OFFLINE_TESTS"):
            pytest.skip("network tests disabled in CI/offline mode")
