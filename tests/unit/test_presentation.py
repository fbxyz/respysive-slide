"""
Unit tests for the Presentation class.

Tests cover:
- Presentation initialization
- Slide management
- Global data management (GeoJSON)
- HTML generation and rendering
- Configuration and theming
- File operations (save, export)
"""

import json
import os
import unittest
from unittest.mock import mock_open, patch

from respysive.container import Slide
from respysive.presentation import Presentation


class TestPresentationBasic(unittest.TestCase):
    """Test basic Presentation functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.presentation = Presentation()

    def test_presentation_initialization(self):
        """Test that Presentation initializes correctly."""
        self.assertEqual(self.presentation.slides, [])
        self.assertEqual(repr(self.presentation), "Presentation(0 slides)")

    def test_presentation_str_representation(self):
        """Test string representation of Presentation."""
        self.presentation.add_slide(Slide())
        str_repr = str(self.presentation)
        self.assertIn("Presentation", str_repr)
        self.assertIn("1 slide", str_repr)

    def test_presentation_multiple_slides_str(self):
        """Test string representation with multiple slides."""
        self.presentation.add_slide(Slide())
        self.presentation.add_slide(Slide())
        str_repr = str(self.presentation)
        self.assertIn("2 slides", str_repr)


class TestPresentationSlideManagement(unittest.TestCase):
    """Test slide management functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.presentation = Presentation()

    def test_add_slide_basic(self):
        """Test basic slide addition."""
        slide = Slide()
        self.presentation.add_slide(slide)

        self.assertEqual(len(self.presentation.slides), 1)
        self.assertIs(self.presentation.slides[0], slide)

    def test_add_multiple_slides(self):
        """Test adding multiple slides."""
        slides = [Slide(), Slide(), Slide()]
        for slide in slides:
            self.presentation.add_slide(slide)

        self.assertEqual(len(self.presentation.slides), 3)
        for i, slide in enumerate(slides):
            self.assertIs(self.presentation.slides[i], slide)


class TestPresentationGlobalData(unittest.TestCase):
    """Test global data management functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.presentation = Presentation()

    def test_add_global_geojson_dict(self):
        """Test adding GeoJSON data as dictionary."""
        geojson_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"name": "Test"},
                    "geometry": {"type": "Point", "coordinates": [0, 0]},
                }
            ],
        }

        self.presentation.add_global_geojson("test_geojson", geojson_data)

        # Verify data was stored
        stored_data = self.presentation._global_geojson["test_geojson"]
        self.assertIsNotNone(stored_data)
        stored_dict = json.loads(stored_data)
        self.assertEqual(stored_dict["type"], "FeatureCollection")

    def test_add_global_geojson_string(self):
        """Test adding GeoJSON data as JSON string."""
        geojson_string = '{"type": "FeatureCollection", "features": []}'

        self.presentation.add_global_geojson("test_geojson", geojson_string)

        stored_data = self.presentation._global_geojson["test_geojson"]
        self.assertEqual(stored_data, geojson_string)

    @patch("builtins.open", new_callable=mock_open, read_data='{"type": "FeatureCollection"}')
    def test_add_global_geojson_file(self, mock_file):
        """Test adding GeoJSON data from file."""
        self.presentation.add_global_geojson("test_geojson", "/path/to/file.geojson")

        mock_file.assert_called_once_with("/path/to/file.geojson", encoding="utf-8")
        stored_data = self.presentation._global_geojson["test_geojson"]
        self.assertEqual(stored_data, '{"type": "FeatureCollection"}')

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_add_global_geojson_file_not_found(self, mock_file):
        """Test adding GeoJSON data from non-existent file."""
        with self.assertRaises(FileNotFoundError):
            self.presentation.add_global_geojson("test_geojson", "/path/to/nonexistent.geojson")

    def test_add_global_geojson_invalid_type(self):
        """Test adding invalid GeoJSON data type."""
        with self.assertRaises(TypeError):
            self.presentation.add_global_geojson("test_geojson", 123)

    def test_multiple_global_geojson(self):
        """Test adding multiple GeoJSON datasets."""
        geojson1 = {"type": "FeatureCollection", "features": []}
        geojson2 = {"type": "Feature", "properties": {}, "geometry": {"type": "Point", "coordinates": [0, 0]}}

        self.presentation.add_global_geojson("dataset1", geojson1)
        self.presentation.add_global_geojson("dataset2", geojson2)

        stored_data1 = self.presentation._global_geojson["dataset1"]
        stored_data2 = self.presentation._global_geojson["dataset2"]

        self.assertIsNotNone(stored_data1)
        self.assertIsNotNone(stored_data2)
        self.assertNotEqual(stored_data1, stored_data2)


class TestPresentationHTMLGeneration(unittest.TestCase):
    """Test HTML generation with to_html()."""

    def setUp(self):
        """Set up test fixtures."""
        self.presentation = Presentation()

    def test_empty_presentation(self):
        """Test rendering presentation with no slides."""
        html = self.presentation.to_html()

        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn('<div class="slides rs-canvas"', html)
        self.assertIn("theme/moon.min.css", html)

    def test_with_slides(self):
        """Test rendering presentation with slides."""
        slide = Slide()
        slide.add_title("Test Slide")
        self.presentation.add_slide(slide)

        html = self.presentation.to_html()

        self.assertIn("Test Slide", html)
        self.assertIn('<section class="rs-slide', html)

    def test_theme(self):
        """Test rendering with a Reveal.js theme and a custom theme."""
        self.assertIn("theme/white.min.css", self.presentation.to_html(theme="white"))
        html = self.presentation.to_html(theme="custom", custom_theme="my_theme.css")
        self.assertIn("href='my_theme.css'", html)
        with self.assertRaises(ValueError):
            self.presentation.to_html(theme="custom")

    def test_runtime_options(self):
        """Test that options reach the runtime configuration."""
        html = self.presentation.to_html(transition="fade", controls=False, progress=False, slide_number=None)
        config = json.loads(html.split("window.RESPYSIVE_CONFIG = ", 1)[1].split(";</script>", 1)[0])

        self.assertEqual(config["transition"], "fade")
        self.assertFalse(config["controls"])
        self.assertFalse(config["progress"])
        self.assertIsNone(config["slideNumber"])


class TestPresentationFileOperations(unittest.TestCase):
    """Test file operations (save, export)."""

    def setUp(self):
        """Set up test fixtures."""
        self.presentation = Presentation()
        self.test_filename = "test_presentation.html"

    def tearDown(self):
        """Clean up test files."""
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)

    @patch("builtins.open", new_callable=mock_open)
    def test_save_html_basic(self, mock_file):
        """Test basic HTML save functionality."""
        slide = Slide()
        slide.add_title("Test Slide")
        self.presentation.add_slide(slide)

        self.presentation.save_html(self.test_filename)

        mock_file.assert_called_once_with(self.test_filename, "w", encoding="utf-8")
        # Verify that write was called with HTML content
        mock_file().write.assert_called()
        written_content = mock_file().write.call_args[0][0]
        self.assertIn("Test Slide", written_content)
        self.assertIn("<!DOCTYPE html>", written_content)

    @patch("builtins.open", new_callable=mock_open)
    def test_save_html_with_custom_path(self, mock_file):
        """Test saving HTML to custom path."""
        custom_path = "/custom/path/presentation.html"
        self.presentation.save_html(custom_path)

        mock_file.assert_called_once_with(custom_path, "w", encoding="utf-8")

    @patch("builtins.open", side_effect=PermissionError)
    def test_save_html_permission_error(self, mock_file):
        """Test handling of permission errors during save."""
        with self.assertRaises(PermissionError):
            self.presentation.save_html("/root/forbidden.html")

    def test_save_html_creates_valid_file(self):
        """Test that saved HTML file is valid."""
        slide = Slide()
        slide.add_title("Test Slide")
        self.presentation.add_slide(slide)

        # Use actual file operations for this test
        self.presentation.save_html(self.test_filename)

        # Verify file was created and contains expected content
        self.assertTrue(os.path.exists(self.test_filename))

        with open(self.test_filename, encoding="utf-8") as f:
            content = f.read()

        self.assertIn("<!DOCTYPE html>", content)
        self.assertIn("Test Slide", content)
        self.assertIn("Reveal.js", content)


class TestPresentationSlideDataSharing(unittest.TestCase):
    """Test data sharing between slides."""

    def setUp(self):
        """Set up test fixtures."""
        self.presentation = Presentation()

    def test_slide_access_to_global_data(self):
        """Test that slides can access global data through presentation."""
        # Add global GeoJSON data
        geojson_data = {"type": "FeatureCollection", "features": []}
        self.presentation.add_global_geojson("shared_data", geojson_data)

        # Create slide that should be able to access this data
        slide = Slide()
        slide.add_maplibre_choropleth_with_data_join(
            center=[2.3, 46.8],
            zoom=6,
            geojson_id="shared_data",
            join_data={"region1": {"value": 100}},
            join_key="id",
            color_property="value",
        )

        self.presentation.add_slide(slide)

        # Verify that the slide was created successfully
        self.assertEqual(len(self.presentation.slides), 1)
        self.assertTrue(len(slide.content) > 0)
        # the GeoJSON is written once in the page, outside the map
        page = self.presentation.to_html()
        self.assertEqual(page.count('{"type":"FeatureCollection","features":[]}'), 1)

    def test_missing_global_geojson_raises(self):
        """A map referring to GeoJSON that was never added fails at render."""
        slide = Slide()
        slide.add_maplibre_choropleth_with_data_join(
            center=[2.3, 46.8],
            zoom=6,
            geojson_id="regions",
            join_data={"r1": {"value": 1}},
            join_key="id",
            color_property="value",
        )
        self.presentation.add_slide(slide)
        with self.assertRaisesRegex(ValueError, "'regions'"):
            self.presentation.to_html()

    def test_two_presentations_do_not_share_geojson(self):
        """GeoJSON added to one deck is not visible from another."""
        other = Presentation()
        other.add_global_geojson("regions", {"type": "FeatureCollection", "features": []})
        self.assertEqual(self.presentation._global_geojson, {})

    def test_multiple_slides_same_data(self):
        """Test multiple slides using the same global data."""
        # Add global GeoJSON data
        geojson_data = {"type": "FeatureCollection", "features": []}
        self.presentation.add_global_geojson("shared_map", geojson_data)

        # Create multiple slides using the same data
        slide1 = Slide()
        slide1.add_maplibre_choropleth_with_data_join(
            center=[2.3, 46.8],
            zoom=6,
            geojson_id="shared_map",
            join_data={"region1": {"value": 100}},
            join_key="id",
            color_property="value",
        )

        slide2 = Slide()
        slide2.add_maplibre_choropleth_with_data_join(
            center=[2.3, 46.8],
            zoom=8,
            geojson_id="shared_map",
            join_data={"region1": {"value": 200}},
            join_key="id",
            color_property="value",
        )

        self.presentation.add_slide(slide1)
        self.presentation.add_slide(slide2)

        # Verify both slides were created successfully
        self.assertEqual(len(self.presentation.slides), 2)
        self.assertTrue(len(slide1.content) > 0)
        self.assertTrue(len(slide2.content) > 0)


if __name__ == "__main__":
    unittest.main()
