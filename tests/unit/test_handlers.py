"""
Unit tests for the handler system.

Tests cover:
- ContentDetector functionality
- Individual handler behavior
- Handler registration and priority
- Content type detection
- Handler processing
"""

import json
import unittest
from unittest.mock import patch

import matplotlib.pyplot as plt
import pytest

from respysive import Content
from respysive.handlers.altair import AltairHandler
from respysive.handlers.base import BaseHandler
from respysive.handlers.content_detector import ContentDetector
from respysive.handlers.custom_json import CustomJsonHandler
from respysive.handlers.html_repr import HtmlReprHandler
from respysive.handlers.image import ImageHandler
from respysive.handlers.latex import LatexHandler
from respysive.handlers.maplibre import MapLibreHandler
from respysive.handlers.mappyng import MappyngHandler
from respysive.handlers.matplotlib import MatplotlibHandler
from respysive.handlers.plotly import PlotlyHandler
from respysive.handlers.text import TextHandler
from respysive.handlers.video import VideoHandler


class TestContentDetector(unittest.TestCase):
    """Test ContentDetector class."""

    def setUp(self):
        """Set up test fixtures."""
        self.content_obj = Content()
        self.detector = ContentDetector()

    def test_detector_initialization(self):
        """Test ContentDetector initializes correctly."""
        self.assertEqual(len(self.detector._handlers), 0)
        self.assertIsInstance(self.detector._handlers, list)

    def test_register_handler(self):
        """Test handler registration."""
        self.detector.register_handler(TextHandler, self.content_obj)
        self.assertEqual(len(self.detector._handlers), 1)
        self.assertIsInstance(self.detector._handlers[0], TextHandler)

    def test_register_multiple_handlers(self):
        """Test multiple handler registration and priority sorting."""
        self.detector.register_handler(TextHandler, self.content_obj)  # priority 100
        self.detector.register_handler(MatplotlibHandler, self.content_obj)  # priority 10
        self.detector.register_handler(PlotlyHandler, self.content_obj)  # priority 20

        self.assertEqual(len(self.detector._handlers), 3)
        # Check priority ordering (lower number = higher priority)
        priorities = [handler.priority for handler in self.detector._handlers]
        self.assertEqual(priorities, sorted(priorities))

    def test_detect_and_handle_text(self):
        """Test detection and handling of text content."""
        self.detector.register_handler(TextHandler, self.content_obj)

        result = self.detector.detect_and_handle("Hello World")
        self.assertIn("Hello World", result)
        self.assertIsInstance(result, str)

    def test_detect_and_handle_matplotlib(self):
        """Test detection and handling of matplotlib content."""
        self.detector.register_handler(MatplotlibHandler, self.content_obj)
        self.detector.register_handler(TextHandler, self.content_obj)

        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 2])

        result = self.detector.detect_and_handle(fig)
        self.assertIsInstance(result, str)
        # Should contain SVG or image content
        self.assertTrue(len(result) > 0)

    def test_detect_and_handle_fallback(self):
        """Test fallback to text handler when no specific handler matches."""
        self.detector.register_handler(TextHandler, self.content_obj)

        # Use an object that no handler specifically recognizes
        unknown_object = object()
        result = self.detector.detect_and_handle(unknown_object)

        self.assertIsInstance(result, str)
        self.assertIn(str(unknown_object), result)

    def test_unknown_content_type_raises(self):
        """A misspelt content_type is an error, not a silent fallback."""
        self.detector.register_handler(TextHandler, self.content_obj)
        with self.assertRaisesRegex(ValueError, "Unknown content_type 'plotyl'"):
            self.detector.detect_and_handle("x", content_type="plotyl")

    def test_get_handlers(self):
        """Test get_handlers method."""
        self.detector.register_handler(TextHandler, self.content_obj)
        self.detector.register_handler(MatplotlibHandler, self.content_obj)

        handlers = self.detector.get_handlers()
        self.assertEqual(len(handlers), 2)
        self.assertIsInstance(handlers, list)
        # Should return a copy, not the original list
        self.assertIsNot(handlers, self.detector._handlers)


class TestBaseHandler(unittest.TestCase):
    """Test BaseHandler abstract class."""

    def test_base_handler_is_abstract(self):
        """Test that BaseHandler cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            BaseHandler(Content())


class TestMatplotlibHandler(unittest.TestCase):
    """Test MatplotlibHandler."""

    def setUp(self):
        """Set up test fixtures."""
        self.content_obj = Content()
        self.handler = MatplotlibHandler(self.content_obj)

    def test_handler_initialization(self):
        """Test handler initializes correctly."""
        self.assertIsInstance(self.handler, MatplotlibHandler)
        self.assertEqual(self.handler.priority, 10)
        self.assertIs(self.handler.content, self.content_obj)

    def test_can_handle_matplotlib_figure(self):
        """Test matplotlib figure detection."""
        fig, ax = plt.subplots()
        self.assertTrue(self.handler.can_handle(fig))

    def test_can_handle_non_matplotlib(self):
        """Test rejection of non-matplotlib objects."""
        self.assertFalse(self.handler.can_handle("not a figure"))
        self.assertFalse(self.handler.can_handle(123))
        self.assertFalse(self.handler.can_handle({}))

    def test_handle_matplotlib_figure(self):
        """Test matplotlib figure processing."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 2])

        result = self.handler.handle(fig)
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)


class TestPlotlyHandler(unittest.TestCase):
    """Test PlotlyHandler."""

    def setUp(self):
        """Set up test fixtures."""
        self.content_obj = Content()
        self.handler = PlotlyHandler(self.content_obj)

    def test_handler_initialization(self):
        """Test handler initializes correctly."""
        self.assertIsInstance(self.handler, PlotlyHandler)
        self.assertEqual(self.handler.priority, 20)

    def test_can_handle_plotly_dict(self):
        """Test plotly dictionary detection."""
        plotly_data = {"data": [{"x": [1, 2, 3], "y": [4, 5, 6], "type": "scatter"}], "layout": {"title": "Test Chart"}}
        self.assertTrue(self.handler.can_handle(plotly_data))

    def test_can_handle_plotly_json_string(self):
        """Test plotly JSON string detection."""
        plotly_data = {"data": [{"x": [1, 2, 3], "y": [4, 5, 6], "type": "scatter"}], "layout": {"title": "Test Chart"}}
        plotly_json = json.dumps(plotly_data)
        self.assertTrue(self.handler.can_handle(plotly_json))

    def test_can_handle_non_plotly(self):
        """Test rejection of non-plotly objects."""
        self.assertFalse(self.handler.can_handle("not plotly"))
        self.assertFalse(self.handler.can_handle({"not": "plotly"}))
        self.assertFalse(self.handler.can_handle(123))

    def test_handle_plotly_data(self):
        """Test plotly data processing."""
        plotly_data = {"data": [{"x": [1, 2, 3], "y": [4, 5, 6], "type": "scatter"}], "layout": {"title": "Test Chart"}}

        result = self.handler.handle(plotly_data)
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)


class TestAltairHandler(unittest.TestCase):
    """Test AltairHandler."""

    def setUp(self):
        """Set up test fixtures."""
        self.content_obj = Content()
        self.handler = AltairHandler(self.content_obj)

    def test_handler_initialization(self):
        """Test handler initializes correctly."""
        self.assertIsInstance(self.handler, AltairHandler)
        self.assertEqual(self.handler.priority, 30)

    def test_can_handle_altair_dict(self):
        """Test altair dictionary detection."""
        altair_data = {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "data": {"values": [{"a": "A", "b": 28}]},
            "mark": "bar",
        }
        self.assertTrue(self.handler.can_handle(altair_data))

    def test_can_handle_altair_json_string(self):
        """Test altair JSON string detection."""
        altair_json = '{"$schema": "https://vega.github.io/schema/vega-lite/v5.json"}'
        self.assertTrue(self.handler.can_handle(altair_json))

    def test_can_handle_non_altair(self):
        """Test rejection of non-altair objects."""
        self.assertFalse(self.handler.can_handle("not altair"))
        self.assertFalse(self.handler.can_handle({"not": "altair"}))
        self.assertFalse(self.handler.can_handle(123))

    def test_altair_chart_object(self):
        """An Altair chart object is rendered without calling to_json() first."""
        alt = pytest.importorskip("altair")
        chart = alt.Chart(alt.Data(values=[{"a": 1}])).mark_point().encode(x="a:Q")
        self.assertTrue(self.handler.can_handle(chart))
        self.assertIn("vegaEmbed(", self.handler.handle(chart))


@pytest.mark.unit
def test_figures_reach_their_handler():
    """Chart objects passed as is are not taken by an earlier handler."""
    go = pytest.importorskip("plotly.graph_objects")
    alt = pytest.importorskip("altair")
    from respysive import Slide

    slide = Slide()
    slide.add_content(
        [go.Figure(go.Bar(y=[1, 2])), alt.Chart(alt.Data(values=[{"a": 1}])).mark_point()], columns=[6, 6]
    )
    assert "Plotly.newPlot" in slide.content or "Plotly.react" in slide.content
    assert "vegaEmbed(" in slide.content


class TestImageHandler(unittest.TestCase):
    """Test ImageHandler."""

    def setUp(self):
        """Set up test fixtures."""
        self.content_obj = Content()
        self.handler = ImageHandler(self.content_obj)

    def test_handler_initialization(self):
        """Test handler initializes correctly."""
        self.assertIsInstance(self.handler, ImageHandler)
        self.assertEqual(self.handler.priority, 40)

    def test_can_handle_image_url(self):
        """Test image URL detection."""
        image_urls = [
            "https://example.com/image.jpg",
            "https://example.com/image.png",
            "https://example.com/image.gif",
            "https://example.com/image.svg",
        ]
        for url in image_urls:
            self.assertTrue(self.handler.can_handle(url), f"Failed for {url}")

    @patch("os.path.isfile")
    def test_can_handle_local_image_file(self, mock_isfile):
        """Test local image file detection."""
        mock_isfile.return_value = True

        image_files = ["/path/to/image.jpg", "/path/to/image.png", "relative/path/image.gif"]
        for file_path in image_files:
            self.assertTrue(self.handler.can_handle(file_path), f"Failed for {file_path}")

    def test_can_handle_non_image(self):
        """Test rejection of non-image content."""
        self.assertFalse(self.handler.can_handle("not an image"))
        self.assertFalse(self.handler.can_handle(123))
        self.assertFalse(self.handler.can_handle({}))


class TestVideoHandler(unittest.TestCase):
    """Test VideoHandler."""

    def setUp(self):
        """Set up test fixtures."""
        self.content_obj = Content()
        self.handler = VideoHandler(self.content_obj)

    def test_handler_initialization(self):
        """Test handler initializes correctly."""
        self.assertIsInstance(self.handler, VideoHandler)
        self.assertEqual(self.handler.priority, 40)

    def test_can_handle_video_url(self):
        """Test video URL detection."""
        video_urls = [
            "https://example.com/clip.mp4",
            "https://example.com/clip.webm",
            "https://example.com/clip.ogv",
            "https://example.com/clip.mov",
            "https://example.com/clip.m4v",
        ]
        for url in video_urls:
            self.assertTrue(self.handler.can_handle(url), f"Failed for {url}")

    @patch("os.path.isfile")
    def test_can_handle_local_video_file(self, mock_isfile):
        """Test local video file detection."""
        mock_isfile.return_value = True

        video_files = [
            "/path/to/clip.mp4",
            "/path/to/clip.webm",
            "relative/path/clip.mov",
        ]
        for file_path in video_files:
            self.assertTrue(self.handler.can_handle(file_path), f"Failed for {file_path}")

    def test_does_not_handle_images(self):
        """Test that image content (incl. animated WebP) is not handled as video."""
        self.assertFalse(self.handler.can_handle("https://example.com/image.png"))
        self.assertFalse(self.handler.can_handle("https://example.com/animated.webp"))

    def test_can_handle_non_video(self):
        """Test rejection of non-video content."""
        self.assertFalse(self.handler.can_handle("not a video"))
        self.assertFalse(self.handler.can_handle(123))
        self.assertFalse(self.handler.can_handle({}))


class TestLatexHandler(unittest.TestCase):
    """Test LatexHandler."""

    def setUp(self):
        """Set up test fixtures."""
        self.content_obj = Content()
        self.handler = LatexHandler(self.content_obj)

    def test_handler_initialization(self):
        """Test handler initializes correctly."""
        self.assertIsInstance(self.handler, LatexHandler)
        self.assertEqual(self.handler.priority, 50)

    def test_can_handle_dollar_math(self):
        """Test detection of $-delimited math."""
        for latex in ["This is $x^2 + y^2 = z^2$ inline math", "$$\\int_0^1 x dx = \\frac{1}{2}$$"]:
            self.assertTrue(self.handler.can_handle(latex), f"Failed for {latex}")

    def test_skips_mathjax_delimited_content(self):
        """Content already converted to MathJax delimiters is left to TextHandler."""
        for latex in ["This is \\(x^2 + y^2 = z^2\\) inline math", "\\[x^2 + y^2 = z^2\\]"]:
            self.assertFalse(self.handler.can_handle(latex), f"Failed for {latex}")

    def test_can_handle_non_latex(self):
        """Test rejection of non-LaTeX content."""
        self.assertFalse(self.handler.can_handle("regular text"))
        self.assertFalse(self.handler.can_handle(123))
        self.assertFalse(self.handler.can_handle({}))


class TestTextHandler(unittest.TestCase):
    """Test TextHandler."""

    def setUp(self):
        """Set up test fixtures."""
        self.content_obj = Content()
        self.handler = TextHandler(self.content_obj)

    def test_handler_initialization(self):
        """Test handler initializes correctly."""
        self.assertIsInstance(self.handler, TextHandler)
        self.assertEqual(self.handler.priority, 100)

    def test_can_handle_string(self):
        """Test string content detection."""
        self.assertTrue(self.handler.can_handle("Hello World"))
        self.assertTrue(self.handler.can_handle(""))
        self.assertTrue(self.handler.can_handle("123"))

    def test_can_handle_anything_as_fallback(self):
        """TextHandler is the last resort and accepts any content."""
        self.assertTrue(self.handler.can_handle(123))
        self.assertTrue(self.handler.can_handle({}))
        self.assertTrue(self.handler.can_handle([]))

    def test_handle_text_content(self):
        """Test text content processing."""
        result = self.handler.handle("Hello World")
        self.assertIsInstance(result, str)
        self.assertIn("Hello World", result)


class TestCustomJsonHandler(unittest.TestCase):
    """Test CustomJsonHandler."""

    def setUp(self):
        """Set up test fixtures."""
        self.content_obj = Content()
        self.handler = CustomJsonHandler(self.content_obj)

    def test_handler_initialization(self):
        """Test handler initializes correctly."""
        self.assertIsInstance(self.handler, CustomJsonHandler)
        self.assertEqual(self.handler.priority, 5)

    def test_can_handle_custom_json(self):
        """Test custom JSON configuration detection."""
        custom_config = {
            "library": "leaflet",
            "config": {"center": [48.8566, 2.3522], "zoom": 12},
            "cdn": {"js": ["https://unpkg.com/leaflet/dist/leaflet.js"]},
        }
        self.assertTrue(self.handler.can_handle(custom_config))

    def test_can_handle_non_custom_json(self):
        """Test rejection of non-custom JSON content."""
        self.assertFalse(self.handler.can_handle("not json"))
        self.assertFalse(self.handler.can_handle({"not": "custom"}))
        self.assertFalse(self.handler.can_handle(123))


class TestMapLibreHandler(unittest.TestCase):
    """Test MapLibreHandler."""

    def setUp(self):
        """Set up test fixtures."""
        self.content_obj = Content()
        self.handler = MapLibreHandler(self.content_obj)

    def test_handler_initialization(self):
        """Test handler initializes correctly."""
        self.assertIsInstance(self.handler, MapLibreHandler)
        self.assertEqual(self.handler.priority, 8)

    def test_can_handle_basic_maplibre_config(self):
        """Test basic MapLibre configuration detection."""
        maplibre_config = {"center": [2.3522, 48.8566], "zoom": 10, "openstreetmap": True}
        self.assertTrue(self.handler.can_handle(maplibre_config))

    def test_can_handle_maplibre_with_markers(self):
        """Test MapLibre configuration with markers detection."""
        maplibre_config = {
            "center": [2.3522, 48.8566],
            "zoom": 10,
            "markers": [{"coordinates": [2.3522, 48.8566], "popup": "Test"}],
        }
        self.assertTrue(self.handler.can_handle(maplibre_config))

    def test_can_handle_maplibre_choropleth(self):
        """Test MapLibre choropleth configuration detection."""
        maplibre_config = {
            "center": [2.3522, 48.8566],
            "zoom": 10,
            "choropleth": {"geojson": {"type": "FeatureCollection", "features": []}, "colorProperty": "value"},
        }
        self.assertTrue(self.handler.can_handle(maplibre_config))

    def test_can_handle_non_maplibre(self):
        """Test rejection of non-MapLibre content."""
        self.assertFalse(self.handler.can_handle("not maplibre"))
        self.assertFalse(self.handler.can_handle({"not": "maplibre"}))
        self.assertFalse(self.handler.can_handle(123))


class TestHandlerIntegration(unittest.TestCase):
    """Test handler system integration."""

    def setUp(self):
        """Set up test fixtures."""
        self.content_obj = Content()
        self.detector = ContentDetector()

        # Register all handlers
        self.detector.register_handler(MapLibreHandler, self.content_obj)
        self.detector.register_handler(CustomJsonHandler, self.content_obj)
        self.detector.register_handler(ImageHandler, self.content_obj)
        self.detector.register_handler(MatplotlibHandler, self.content_obj)
        self.detector.register_handler(PlotlyHandler, self.content_obj)
        self.detector.register_handler(AltairHandler, self.content_obj)
        self.detector.register_handler(LatexHandler, self.content_obj)
        self.detector.register_handler(TextHandler, self.content_obj)

    def test_priority_ordering(self):
        """Test that handlers are ordered by priority."""
        priorities = [handler.priority for handler in self.detector._handlers]
        self.assertEqual(priorities, sorted(priorities))

        # CustomJson should be first (priority 5)
        self.assertIsInstance(self.detector._handlers[0], CustomJsonHandler)
        # Text should be last (priority 100)
        self.assertIsInstance(self.detector._handlers[-1], TextHandler)

    def test_content_routing_maplibre(self):
        """Test that MapLibre content routes to MapLibre handler."""
        maplibre_config = {"center": [2.3522, 48.8566], "zoom": 10, "openstreetmap": True}

        # Find which handler would be used
        for handler in self.detector._handlers:
            if handler.can_handle(maplibre_config):
                self.assertIsInstance(handler, MapLibreHandler)
                break
        else:
            self.fail("No handler found for MapLibre config")

    def test_content_routing_matplotlib(self):
        """Test that matplotlib content routes to matplotlib handler."""
        fig, ax = plt.subplots()

        # Find which handler would be used
        for handler in self.detector._handlers:
            if handler.can_handle(fig):
                self.assertIsInstance(handler, MatplotlibHandler)
                break
        else:
            self.fail("No handler found for matplotlib figure")

    def test_content_routing_text_fallback(self):
        """Test that unknown content falls back to text handler."""
        simple_text = "Hello World"

        # Find which handler would be used
        for handler in self.detector._handlers:
            if handler.can_handle(simple_text):
                self.assertIsInstance(handler, TextHandler)
                break
        else:
            self.fail("No handler found for simple text")


class _FakeMappyngInteractiveMap:
    """Stand-in for mappyng.interactive.InteractiveMap (no mappyng dep needed)."""

    __module__ = "mappyng.interactive"

    def __init__(self, svg='<svg id="fake-interactive"><g/></svg>'):
        self._svg = svg

    def _repr_html_(self):
        return f'<div style="display:inline-block;">{self._svg}</div>'


_FakeMappyngInteractiveMap.__name__ = "InteractiveMap"


class _FakeMappyngMap:
    """Stand-in for mappyng.map.Map."""

    __module__ = "mappyng.map"

    def __init__(self, svg='<svg id="fake-static"><g/></svg>'):
        self._svg = svg

    def to_string(self):
        return self._svg


_FakeMappyngMap.__name__ = "Map"


class TestMappyngHandler(unittest.TestCase):
    """Test MappyngHandler routing and rendering."""

    def setUp(self):
        self.content_obj = Content()
        self.handler = MappyngHandler(self.content_obj)

    def test_priority_below_html_repr(self):
        """MappyngHandler must run before HtmlReprHandler."""
        html_handler = HtmlReprHandler(self.content_obj)
        self.assertLess(self.handler.priority, html_handler.priority)

    def test_can_handle_interactive_map(self):
        self.assertTrue(self.handler.can_handle(_FakeMappyngInteractiveMap()))

    def test_can_handle_static_map(self):
        self.assertTrue(self.handler.can_handle(_FakeMappyngMap()))

    def test_can_not_handle_other_types(self):
        self.assertFalse(self.handler.can_handle("plain text"))
        self.assertFalse(self.handler.can_handle({"foo": "bar"}))
        self.assertFalse(self.handler.can_handle(plt.figure()))

    def test_handle_interactive_map_returns_html(self):
        result = self.handler.handle(_FakeMappyngInteractiveMap())
        self.assertIn("<svg", result)
        self.assertIn("fake-interactive", result)
        self.assertIn("d-flex", result)

    def test_handle_static_map_returns_svg(self):
        result = self.handler.handle(_FakeMappyngMap())
        self.assertIn("fake-static", result)
        self.assertIn("<svg", result)

    def test_routing_prefers_mappyng_over_html_repr(self):
        """A mappyng InteractiveMap must be routed to MappyngHandler,
        not the generic HtmlReprHandler."""
        detector = ContentDetector()
        detector.register_handler(MappyngHandler, self.content_obj)
        detector.register_handler(HtmlReprHandler, self.content_obj)

        obj = _FakeMappyngInteractiveMap()
        for handler in detector._handlers:
            if handler.can_handle(obj):
                self.assertIsInstance(handler, MappyngHandler)
                break
        else:
            self.fail("No handler matched fake InteractiveMap")

    def test_forced_content_type_mappyng(self):
        detector = ContentDetector()
        detector.register_handler(MappyngHandler, self.content_obj)
        result = detector.detect_and_handle(_FakeMappyngMap(), content_type="mappyng")
        self.assertIn("fake-static", result)


if __name__ == "__main__":
    unittest.main()
