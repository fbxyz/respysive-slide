"""
Unit tests for the Slide class.

Tests cover basic slide functionality including:
- Slide initialization
- Title addition
- Content addition with various types
- Card functionality
- Custom content integration
- MapLibre map integration
"""

import unittest
from unittest.mock import Mock, patch

import matplotlib.pyplot as plt

from respysive.container import Slide


def _image_response():
    """Fake HTTP response serving an image."""
    return Mock(headers={"content-type": "image/png"}, content=b"\x89PNG fake-image-bytes")


class TestSlideBasic(unittest.TestCase):
    """Test basic Slide functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.slide = Slide()

    def test_slide_initialization(self):
        """Test that Slide initializes correctly."""
        self.assertEqual(self.slide.content, "")
        self.assertFalse(self.slide.center)
        self.assertEqual(self.slide.kwargs, {})
        self.assertIsNotNone(self.slide.content_obj)
        self.assertIsNotNone(self.slide._content_detector)

    def test_slide_initialization_with_params(self):
        """Test Slide initialization with parameters."""
        slide = Slide(center=True, data_background="blue")
        self.assertTrue(slide.center)
        self.assertEqual(slide.kwargs["data_background"], "blue")

    @patch("respysive.utils.encode_image_to_data_uri")
    def test_slide_background_image_auto_encoding(self, mock_encode):
        """Test that background images are automatically encoded to base64."""
        mock_encode.return_value = "data:image/png;base64,fake_encoded_data"

        # Test with local file path
        slide = Slide(**{"data-background-image": "/path/to/image.png"})
        mock_encode.assert_called_once_with("/path/to/image.png")
        self.assertEqual(slide.kwargs["data-background-image"], "data:image/png;base64,fake_encoded_data")

        # Test with URL
        mock_encode.reset_mock()
        mock_encode.return_value = "data:image/jpeg;base64,fake_encoded_data"
        slide2 = Slide(**{"data-background-image": "https://example.com/bg.jpg"})
        mock_encode.assert_called_once_with("https://example.com/bg.jpg")
        self.assertEqual(slide2.kwargs["data-background-image"], "data:image/jpeg;base64,fake_encoded_data")

        # Test that data URIs are not re-encoded
        mock_encode.reset_mock()
        data_uri = "data:image/png;base64,already_encoded"
        slide3 = Slide(**{"data-background-image": data_uri})
        mock_encode.assert_not_called()
        self.assertEqual(slide3.kwargs["data-background-image"], data_uri)

    def test_add_title_basic(self):
        """Test basic title addition."""
        self.slide.add_title("Test Title")
        self.assertIn("Test Title", self.slide.content)
        self.assertIn("<h3", self.slide.content)
        self.assertIn("col-12", self.slide.content)

    def test_add_title_with_custom_tag(self):
        """Test title addition with custom HTML tag."""
        self.slide.add_title("Test Title", tag="h1")
        self.assertIn("<h1", self.slide.content)
        self.assertIn("Test Title", self.slide.content)

    def test_add_title_with_icon(self):
        """Test title addition with icon."""
        self.slide.add_title("Test Title", icon="fas fa-star")
        self.assertIn("fas fa-star", self.slide.content)
        self.assertIn("Test Title", self.slide.content)

    def test_add_title_with_styles(self):
        """Test title addition with custom styles."""
        self.slide.add_title("Test Title", color="blue", font_size="20px")
        self.assertIn("Test Title", self.slide.content)
        # The styles are passed to the Content object, so we just verify the title is added


class TestSlideContent(unittest.TestCase):
    """Test content addition functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.slide = Slide()

    def test_add_content_basic(self):
        """Test basic content addition."""
        content = ["Hello World"]
        self.slide.add_content(content)
        self.assertIn("Hello World", self.slide.content)
        self.assertIn("col-md-12", self.slide.content)

    def test_add_content_multiple_columns(self):
        """Test content addition with multiple columns."""
        content = ["Column 1", "Column 2"]
        columns = [6, 6]
        self.slide.add_content(content, columns=columns)
        self.assertIn("Column 1", self.slide.content)
        self.assertIn("Column 2", self.slide.content)
        self.assertIn("col-md-6", self.slide.content)

    def test_add_content_with_styles(self):
        """Test content addition with styles."""
        content = ["Styled content"]
        styles = [{"class": ["bg-primary", "text-white"]}]
        self.slide.add_content(content, styles=styles)
        self.assertIn("Styled content", self.slide.content)
        self.assertIn("bg-primary", self.slide.content)
        self.assertIn("text-white", self.slide.content)

    @patch("matplotlib.pyplot.figure")
    def test_add_content_with_matplotlib(self, mock_figure):
        """Test content addition with matplotlib figure."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 2])

        content = [fig]
        self.slide.add_content(content)
        # Verify that the content was processed
        self.assertIn("col-md-12", self.slide.content)

    def test_add_content_with_shared_data_ids(self):
        """Test content addition with shared data IDs."""
        content = ["Test content"]
        shared_data_ids = ["test_id"]

        # This should not raise an error
        self.slide.add_content(content, shared_data_ids=shared_data_ids)
        self.assertIn("Test content", self.slide.content)


class TestSlideCards(unittest.TestCase):
    """Test card functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.slide = Slide()

    def test_add_card_basic(self):
        """Test basic card addition."""
        cards = [{"title": "Test Card", "text": "Test content"}]
        self.slide.add_card(cards)
        self.assertIn("Test Card", self.slide.content)
        self.assertIn("Test content", self.slide.content)
        self.assertIn("card", self.slide.content)

    def test_add_card_with_styles(self):
        """Test card addition with styles."""
        cards = [{"title": "Styled Card"}]
        styles = [{"class": ["bg-primary", "text-white"]}]
        self.slide.add_card(cards, styles=styles)
        self.assertIn("Styled Card", self.slide.content)
        self.assertIn("bg-primary", self.slide.content)
        self.assertIn("text-white", self.slide.content)

    def test_add_card_with_image(self):
        """Test card addition with image."""
        # Use a data URI to avoid HTTP requests
        test_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        cards = [{"title": "Image Card", "image": test_image}]
        self.slide.add_card(cards)
        self.assertIn("Image Card", self.slide.content)
        self.assertIn("card-img-top", self.slide.content)

    def test_add_card_multiple_cards(self):
        """Test addition of multiple cards."""
        cards = [{"title": "Card 1", "text": "Content 1"}, {"title": "Card 2", "text": "Content 2"}]
        self.slide.add_card(cards)
        self.assertIn("Card 1", self.slide.content)
        self.assertIn("Card 2", self.slide.content)
        self.assertIn("col-6", self.slide.content)  # 2 cards = 6 columns each

    def test_add_card_title_tag_customization(self):
        """Test card title tag customization."""
        cards = [{"title": "Custom Size Card", "title_tag": "h2"}]
        self.slide.add_card(cards)
        self.assertIn("<h2", self.slide.content)
        self.assertIn("Custom Size Card", self.slide.content)

    def test_add_card_with_matplotlib_graph(self):
        """Test card with matplotlib graph."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 2])

        cards = [{"title": "Chart Card", "graph": fig}]
        self.slide.add_card(cards)
        self.assertIn("Chart Card", self.slide.content)

    def test_add_card_with_image_style(self):
        """Test card image with custom styling."""
        # Use a data URI to avoid HTTP requests
        test_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        cards = [
            {
                "title": "Styled Image Card",
                "image": test_image,
                "image_style": {"max-height": "300px", "object-fit": "contain"},
            }
        ]
        self.slide.add_card(cards)
        self.assertIn("Styled Image Card", self.slide.content)
        self.assertIn("card-img-top", self.slide.content)
        self.assertIn("max-height", self.slide.content)
        self.assertIn("300px", self.slide.content)
        self.assertIn("object-fit", self.slide.content)
        self.assertIn("contain", self.slide.content)


class TestSlideMapLibre(unittest.TestCase):
    """Test MapLibre functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.slide = Slide()

    def test_add_maplibre_map_basic(self):
        """Test basic MapLibre map addition."""
        center = [2.3522, 48.8566]
        self.slide.add_maplibre_map(center=center)

        # Verify that content was added (the actual map processing is handled by handlers)
        self.assertTrue(len(self.slide.content) > 0)
        self.assertIn("col-md-12", self.slide.content)

    def test_add_maplibre_map_with_markers(self):
        """Test MapLibre map with markers."""
        center = [2.3522, 48.8566]
        markers = [
            {
                "coordinates": [2.3522, 48.8566],
                "icon": "fas fa-tower-broadcast",
                "color": "#e74c3c",
                "popup": "Eiffel Tower",
            }
        ]

        self.slide.add_maplibre_map(center=center, markers=markers)
        self.assertTrue(len(self.slide.content) > 0)

    def test_add_maplibre_lines_map(self):
        """Test MapLibre lines map."""
        center = [2.3522, 48.8566]
        lines = [
            {
                "coordinates": [[2.3522, 48.8566], [2.3376, 48.8606]],
                "width": 8,
                "color": "#e74c3c",
                "popup": "Test line",
            }
        ]

        self.slide.add_maplibre_lines_map(center=center, lines=lines)
        self.assertTrue(len(self.slide.content) > 0)

    def test_add_maplibre_circles_map(self):
        """Test MapLibre circles map."""
        center = [2.3522, 48.8566]
        circles = [
            {"coordinates": [2.3522, 48.8566], "value": 2200000, "color": "#e74c3c", "popup": "Paris: 2.2M people"}
        ]

        self.slide.add_maplibre_circles_map(center=center, circles=circles)
        self.assertTrue(len(self.slide.content) > 0)

    def test_add_maplibre_choropleth_map(self):
        """Test MapLibre choropleth map."""
        center = [2.3522, 48.8566]
        geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"name": "Test", "value": 100},
                    "geometry": {"type": "Point", "coordinates": [2.3522, 48.8566]},
                }
            ],
        }
        color_rules = [{"operator": ">=", "value": 50, "color": "#ff0000"}]

        self.slide.add_maplibre_choropleth_map(
            center=center, geojson=geojson, color_property="value", color_rules=color_rules
        )
        self.assertTrue(len(self.slide.content) > 0)

    def test_add_maplibre_choropleth_with_data_join(self):
        """Test MapLibre choropleth with data join."""
        center = [2.3522, 48.8566]
        join_data = {"region1": {"population": 1000000}}

        self.slide.add_maplibre_choropleth_with_data_join(
            center=center,
            geojson_id="test_geojson",
            join_data=join_data,
            join_key="id",
            color_property="population",
            color_rules=[{"operator": ">=", "value": 500000, "color": "#ff0000"}],
        )
        self.assertTrue(len(self.slide.content) > 0)


class TestSlideCustomContent(unittest.TestCase):
    """Test custom content functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.slide = Slide()

    def test_add_custom_content_basic(self):
        """Test basic custom content addition."""
        self.slide.add_custom_content(
            library="test-lib",
            config={"key": "value"},
            cdn={"js": ["https://example.com/lib.js"]},
            init_script="console.log('test');",
        )

        self.assertTrue(len(self.slide.content) > 0)
        self.assertIn("col-md-12", self.slide.content)

    def test_add_custom_content_with_styles(self):
        """Test custom content with styling."""
        self.slide.add_custom_content(
            library="styled-lib", config={"theme": "dark"}, columns=[6], styles=[{"class": ["bg-dark"]}]
        )

        self.assertTrue(len(self.slide.content) > 0)
        self.assertIn("col-md-6", self.slide.content)


class TestSlideTitlePage(unittest.TestCase):
    """Test title page functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.slide = Slide()

    def test_add_title_page_basic(self):
        """Test basic title page addition."""
        title_content = {"title": "Test Presentation", "subtitle": "A test subtitle", "authors": "Test Author"}

        self.slide.add_title_page(title_content)
        self.assertIn("Test Presentation", self.slide.content)
        self.assertIn("A test subtitle", self.slide.content)
        self.assertIn("Test Author", self.slide.content)
        self.assertIn("title-page", self.slide.content)

    def test_title_page_markup_is_well_formed(self):
        """Each heading closes with its own tag, with no stray quote after its attributes."""
        styles = [{"color": "red"}, {"color": "blue"}, {"color": "green"}]
        self.slide.add_title_page({"title": "T", "subtitle": "S", "authors": "A"}, styles)
        self.assertIn("<h2 style='color: red;'>T</h2>", self.slide.content)
        self.assertIn("<h3 style='color: blue;'>S</h3>", self.slide.content)
        self.assertIn("<h4 style='color: green;'>A</h4>", self.slide.content)
        self.assertIn('<div class="col-12"><h4', self.slide.content)  # no logo: authors take the full row

    @patch("respysive.utils.requests.get", return_value=_image_response())
    def test_add_title_page_with_logo(self, mock_get):
        """Test that a remote logo is downloaded and embedded."""
        title_content = {"title": "Test Presentation", "logo": "https://example.com/logo.png"}

        self.slide.add_title_page(title_content)
        self.assertIn("Test Presentation", self.slide.content)
        self.assertIn("data:image/png;base64,", self.slide.content)
        mock_get.assert_called_once()

    @patch("respysive.utils.requests.get", return_value=_image_response())
    def test_add_title_page_with_background(self, mock_get):
        """Test title page with background image."""
        title_content = {"title": "Test Presentation"}

        self.slide.add_title_page(title_content, background_image="https://example.com/bg.jpg")

        self.assertIn("Test Presentation", self.slide.content)
        # Verify image is embedded as data URI
        self.assertTrue(
            self.slide.kwargs["data-background-image"].startswith("data:image/jpeg;base64,"),
            "Background image should be embedded as base64 data URI",
        )

    def test_add_split_title_page(self):
        """Test split title page functionality."""
        title_content = {"title": "Split Title", "subtitle": "Split Subtitle"}
        custom_content = "This is custom content for the right side"

        self.slide.add_split_title_page(title_content, custom_content)
        self.assertIn("Split Title", self.slide.content)
        self.assertIn("Split Subtitle", self.slide.content)
        self.assertIn("This is custom content", self.slide.content)
        self.assertIn("col-md-6", self.slide.content)


if __name__ == "__main__":
    unittest.main()
