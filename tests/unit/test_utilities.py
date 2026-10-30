"""
Unit tests for utility functions and global data management.

Tests cover:
- Global data storage and retrieval
- Utility functions from utils module
- Content processing utilities
- Style parsing and processing
"""

import unittest
from unittest.mock import Mock, patch

from bs4 import BeautifulSoup

from respysive.content import Content
from respysive.utils import _parse_style_class, process_markdown_with_latex


def _attrs(fragment):
    """Parse an attribute string such as the output of _parse_style_class."""
    return BeautifulSoup(f"<div {fragment}></div>", "html.parser").div.attrs


def _styles(attrs):
    """Return the declarations of a style attribute as a dict."""
    declarations = (d.split(":", 1) for d in attrs.get("style", "").split(";") if d.strip())
    return {k.strip(): v.strip() for k, v in declarations}


class TestStyleParsing(unittest.TestCase):
    """Test style parsing utilities."""

    def test_parse_style_class_basic(self):
        """Test basic style parsing."""
        attrs = _attrs(_parse_style_class({"class": ["btn", "btn-primary"], "color": "red"}))

        self.assertEqual(attrs["class"], ["btn", "btn-primary"])
        self.assertEqual(_styles(attrs), {"color": "red"})

    def test_parse_style_class_single_class(self):
        """Test parsing with single class as string."""
        attrs = _attrs(_parse_style_class({"class": "btn-primary", "font-size": "16px"}))

        self.assertEqual(attrs["class"], ["btn-primary"])
        self.assertEqual(_styles(attrs), {"font-size": "16px"})

    def test_parse_style_class_no_class(self):
        """Test parsing with no class attribute."""
        attrs = _attrs(_parse_style_class({"color": "blue", "margin": "10px"}))

        self.assertNotIn("class", attrs)
        self.assertEqual(_styles(attrs), {"color": "blue", "margin": "10px"})

    def test_parse_style_class_empty_style(self):
        """Test parsing empty style dictionary."""
        self.assertEqual(_parse_style_class({}), "")

    def test_parse_style_class_none_values(self):
        """None values are skipped."""
        self.assertEqual(_parse_style_class({"class": None, "color": None}), "")
        self.assertEqual(_styles(_attrs(_parse_style_class({"color": None, "margin": "5px"}))), {"margin": "5px"})

    def test_parse_style_class_invalid_class(self):
        """Test rejection of a class that is neither a string nor a list."""
        with self.assertRaises(ValueError):
            _parse_style_class({"class": 42})

    def test_parse_style_class_underscore_conversion(self):
        """Test conversion of underscored CSS properties."""
        attrs = _attrs(_parse_style_class({"font_size": "16px", "background_color": "#fff", "margin_top": "5px"}))

        self.assertEqual(_styles(attrs), {"font-size": "16px", "background-color": "#fff", "margin-top": "5px"})

    def test_parse_style_class_mixed_properties(self):
        """Test mixing regular and underscored properties."""
        style = {"class": ["btn", "active"], "color": "red", "font_size": "14px", "margin": "5px"}
        attrs = _attrs(_parse_style_class(style))

        self.assertEqual(attrs["class"], ["btn", "active"])
        self.assertEqual(_styles(attrs), {"color": "red", "font-size": "14px", "margin": "5px"})

    def test_encode_data_uri_passthrough(self):
        """A data URI is already encoded."""
        from respysive.utils import encode_image_to_data_uri

        uri = "data:image/svg+xml;base64,PHN2Zy8+"
        self.assertEqual(encode_image_to_data_uri(uri), uri)

    def test_parse_style_class_raw_style(self):
        """A style key holds raw CSS declarations."""
        attrs = _attrs(_parse_style_class({"style": "border: 1px solid red;", "color": "blue"}))
        self.assertEqual(_styles(attrs), {"border": "1px solid red", "color": "blue"})


class TestMarkdownLatexProcessing(unittest.TestCase):
    """Test markdown and LaTeX processing utilities."""

    def test_process_markdown_basic(self):
        """Test basic markdown processing."""
        markdown_text = "**Bold text** and *italic text*"
        result = process_markdown_with_latex(markdown_text)

        self.assertIn("<strong>Bold text</strong>", result)
        self.assertIn("<em>italic text</em>", result)

    def test_process_markdown_with_links(self):
        """Test markdown link processing."""
        markdown_text = "[Link text](https://example.com)"
        result = process_markdown_with_latex(markdown_text)

        self.assertIn('<a href="https://example.com">Link text</a>', result)

    def test_process_markdown_with_lists(self):
        """Test markdown list processing."""
        markdown_text = "- Item 1\n- Item 2\n- Item 3"
        result = process_markdown_with_latex(markdown_text)

        self.assertIn("<ul>", result)
        self.assertIn("<li>Item 1</li>", result)
        self.assertIn("<li>Item 2</li>", result)
        self.assertIn("</ul>", result)

    def test_process_markdown_with_headers(self):
        """Test markdown header processing."""
        markdown_text = "# Header 1\n## Header 2\n### Header 3"
        result = process_markdown_with_latex(markdown_text)

        self.assertIn("<h1>Header 1</h1>", result)
        self.assertIn("<h2>Header 2</h2>", result)
        self.assertIn("<h3>Header 3</h3>", result)

    def test_process_latex_inline(self):
        """Test LaTeX inline math processing."""
        latex_text = "This is \\(x^2 + y^2 = z^2\\) inline math"
        result = process_markdown_with_latex(latex_text)

        # Should preserve LaTeX for MathJax processing
        self.assertIn("\\(x^2 + y^2 = z^2\\)", result)

    def test_process_latex_display(self):
        """Test LaTeX display math processing."""
        latex_text = "Display math: \\[\\int_0^1 x dx = \\frac{1}{2}\\]"
        result = process_markdown_with_latex(latex_text)

        # Should preserve LaTeX for MathJax processing
        self.assertIn("\\[\\int_0^1 x dx = \\frac{1}{2}\\]", result)

    def test_process_mixed_markdown_latex(self):
        """Test processing mixed markdown and LaTeX."""
        mixed_text = "**Bold**: \\(x^2\\) and *italic*: \\[y = mx + b\\]"
        result = process_markdown_with_latex(mixed_text)

        self.assertIn("<strong>Bold</strong>", result)
        self.assertIn("<em>italic</em>", result)
        self.assertIn("\\(x^2\\)", result)
        self.assertIn("\\[y = mx + b\\]", result)

    def test_process_empty_string(self):
        """Test processing empty string."""
        result = process_markdown_with_latex("")
        self.assertEqual(result, "")

    def test_process_plain_text(self):
        """Test processing plain text without markdown or LaTeX."""
        plain_text = "Just plain text with no special formatting"
        result = process_markdown_with_latex(plain_text)

        # process_markdown_with_latex wraps text in HTML tags
        self.assertIn(plain_text, result)
        self.assertTrue(result.startswith("<p>") or "<p>" in result)


class TestContentClass(unittest.TestCase):
    """Test Content class basic functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.content = Content()

    def test_content_initialization(self):
        """Test Content class initialization."""
        self.assertIsInstance(self.content, Content)
        self.assertTrue(hasattr(self.content, "shared_data"))

    def test_content_render_empty(self):
        """Test rendering empty content."""
        result = self.content.render()
        self.assertIsInstance(result, str)

    def test_content_add_text(self):
        """Test adding text content."""
        self.content.add_text("Hello World")
        result = self.content.render()

        self.assertIn("Hello World", result)

    def test_content_add_div(self):
        """Test adding div content."""
        self.content.add_div("<p>Test content</p>")
        result = self.content.render()

        self.assertEqual(BeautifulSoup(result, "html.parser").p.get_text(strip=True), "Test content")

    def test_content_add_heading(self):
        """Test adding heading content."""
        self.content.add_heading("Test Heading", "h2")
        result = self.content.render()

        self.assertIn("<h2", result)
        self.assertIn("Test Heading", result)

    def test_content_add_heading_with_icon(self):
        """Test adding heading with icon."""
        self.content.add_heading("Test Heading", "h3", "fas fa-star")
        result = self.content.render()

        self.assertIn("<h3", result)
        self.assertIn("Test Heading", result)
        self.assertIn("fas fa-star", result)

    @patch("matplotlib.pyplot.figure")
    def test_content_add_matplotlib_figure(self, mock_figure):
        """Test adding matplotlib figure."""
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 2])

        self.content.add_fig(fig)
        result = self.content.render()

        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

    @patch("respysive.utils.requests.get")
    def test_content_add_image_url(self, mock_get):
        """Test that an image URL is downloaded and embedded as a data URI."""
        mock_get.return_value = Mock(headers={"content-type": "image/jpeg"}, content=b"\xff\xd8\xff fake-jpeg-bytes")
        self.content.add_image("https://example.com/image.jpg")
        result = self.content.render()

        img = BeautifulSoup(result, "html.parser").img
        self.assertTrue(img["src"].startswith("data:image/jpeg;base64,"))
        self.assertIn("respysive-slide", mock_get.call_args.kwargs["headers"]["User-Agent"])

    @patch("respysive.utils.requests.get")
    def test_content_add_image_url_not_an_image(self, mock_get):
        """An error page served instead of the image is not embedded."""
        mock_get.return_value = Mock(headers={"content-type": "text/html"}, text="<html>Forbidden</html>")

        with self.assertRaisesRegex(ValueError, "did not return an image"):
            self.content.add_image("https://example.com/image.jpg")

    @patch("respysive.utils.requests.get")
    def test_content_add_video_url(self, mock_get):
        """Test adding a video from URL as an embedded base64 element."""
        mock_response = Mock()
        mock_response.content = b"\x00\x01\x02fake-mp4-bytes"
        mock_get.return_value = mock_response

        self.content.add_video("https://example.com/clip.mp4")
        result = self.content.render()

        self.assertIn("<video", result)
        self.assertIn("controls", result)
        self.assertIn("loop", result)
        self.assertIn("muted", result)
        self.assertIn("autoplay", result)
        self.assertIn("playsinline", result)
        self.assertIn("data:video/mp4;base64,", result)
        self.assertIn('type="video/mp4"', result)

    @patch("respysive.utils.requests.get")
    def test_content_add_video_disable_attributes(self, mock_get):
        """Test that boolean video attributes can be disabled."""
        mock_response = Mock()
        mock_response.content = b"fake-webm-bytes"
        mock_get.return_value = mock_response

        self.content.add_video(
            "https://example.com/clip.webm",
            controls=False,
            loop=False,
            muted=False,
            autoplay=False,
            playsinline=False,
        )
        result = self.content.render()

        self.assertIn("<video", result)
        self.assertNotIn("controls", result)
        self.assertNotIn("autoplay", result)
        self.assertIn("data:video/webm;base64,", result)

    def test_content_add_list(self):
        """Test adding list content."""
        list_items = ["Item 1", "Item 2", "Item 3"]
        self.content.add_list(list_items)
        result = self.content.render()

        self.assertIn("<ul", result)
        for item in list_items:
            self.assertIn(item, result)

    def test_content_shared_data_assignment(self):
        """Test shared data assignment."""
        shared_data = {"test_key": "test_value"}
        self.content.shared_data = shared_data

        self.assertEqual(self.content.shared_data, shared_data)


class TestIntegration(unittest.TestCase):
    """Test integration between different utility components."""

    def test_style_parsing_with_markdown(self):
        """Test integration of style parsing with markdown processing."""
        # Process markdown first
        markdown_text = "**Bold text** with formatting"
        processed_markdown = process_markdown_with_latex(markdown_text)

        # Then apply styling
        style = {"class": ["formatted-content"], "color": "blue"}
        style_string = _parse_style_class(style)

        # Both should work together
        self.assertIn("<strong>Bold text</strong>", processed_markdown)
        self.assertEqual(_attrs(style_string)["class"], ["formatted-content"])
        self.assertIn("color: blue", style_string)

    def test_multiple_utility_functions(self):
        """Test using multiple utility functions together."""
        # Start with markdown and LaTeX
        mixed_content = "**Formula**: \\(E = mc^2\\)"
        processed_content = process_markdown_with_latex(mixed_content)

        # Add to Content object
        content = Content()
        content.add_div(processed_content)

        # Apply styling
        style = {"class": ["math-content"], "font_size": "18px"}
        style_string = _parse_style_class(style)

        # Render content
        rendered = content.render()

        # Verify all components work together
        soup = BeautifulSoup(rendered, "html.parser")
        self.assertEqual(soup.strong.get_text(strip=True), "Formula")
        self.assertIn("\\(E = mc^2\\)", soup.get_text())
        self.assertEqual(_attrs(style_string)["class"], ["math-content"])
        self.assertIn("font-size: 18px", style_string)


if __name__ == "__main__":
    unittest.main()
