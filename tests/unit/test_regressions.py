"""Regression tests: content that used to break the page or change the caller's objects."""

import json
import re

import matplotlib.pyplot as plt
import pytest

from respysive import Presentation, Slide, filter_geojson_bbox, set_local_css_urls
from respysive.dependencies import LOCAL_CSS_URLS
from respysive.utils import _parse_style_class, encode_image_to_data_uri, process_markdown_with_latex

HOSTILE = 'Rate "raw" l’été\nline \\ end </script><!-- x'


def _figure(title=HOSTILE):
    return {"data": [{"type": "bar", "x": [1], "y": [2]}], "layout": {"title": {"text": title}}}


@pytest.mark.unit
@pytest.mark.handlers
class TestPlotlyScript:
    def test_figure_is_written_as_parseable_json(self):
        slide = Slide()
        slide.add_content([_figure()])
        literal = re.search(r"var figure = (.*);\n", slide.content).group(1)
        assert json.loads(literal)["layout"]["title"]["text"] == HOSTILE

    def test_figure_cannot_close_the_script(self):
        slide = Slide()
        slide.add_content([_figure()])
        assert slide.content.count("</script>") == 1
        assert "<!--" not in slide.content

    def test_shared_figure_cannot_close_the_script(self):
        slide = Slide()
        slide.add_content([_figure()], shared_data_ids=["geo"])
        assert slide.content.count("</script>") == 1


@pytest.mark.unit
@pytest.mark.presentation
class TestSharedGeojson:
    def test_geojson_is_stored_in_a_json_script(self):
        name = "A <b>bold</b> & <less than 5 </script>"
        deck = Presentation()
        deck.add_global_geojson("geo", {"type": "FeatureCollection", "features": [{"properties": {"n": name}}]})
        stored = re.search(r'<script type="application/json" id="geo">(.*?)</script>', deck.to_html()).group(1)
        assert json.loads(stored)["features"][0]["properties"]["n"] == name

    def test_libraries_accepts_a_single_name(self):
        assert "plotly" in Presentation().to_html(libraries="plotly")


@pytest.mark.unit
class TestCards:
    def test_title_only_class_stays_on_its_card(self):
        slide = Slide()
        slide.add_card([{"title": "Only"}, {"title": "Title", "text": "Body"}])
        classes = re.findall(r"<div class='([^']*\bcard\b[^']*)'", slide.content)
        assert ["title-only" in c.split() for c in classes] == [True, False]

    def test_styles_are_left_as_given(self):
        styles = [{"class": "bg-light"}]
        image_style = {}
        Slide().add_card([{"title": "Only", "image_style": image_style}], styles)
        assert styles == [{"class": "bg-light"}]
        assert image_style == {}

    @pytest.mark.requires_matplotlib
    def test_figure_keeps_its_size(self):
        fig, _ = plt.subplots(figsize=(10, 6))
        try:
            Slide().add_card([{"graph": fig}, {"title": "b"}, {"title": "c"}])
            assert list(fig.get_size_inches()) == [10, 6]
        finally:
            plt.close(fig)

    def test_plotly_dict_keeps_its_layout(self):
        figure = _figure("t")
        Slide().add_card([{"graph": figure}])
        assert "width" not in figure["layout"]


@pytest.mark.unit
@pytest.mark.utilities
class TestMarkdownWithLatex:
    def test_stars_in_formulas_are_not_emphasis(self):
        assert process_markdown_with_latex("Let $a*b$ and $c*d$") == "<p>Let \\(a*b\\) and \\(c*d\\)</p>"

    def test_backslashes_in_formulas_are_kept(self):
        html = process_markdown_with_latex(r"$$\begin{pmatrix} a \\ b \end{pmatrix}$$ and $\{x\}$")
        assert r"a \\ b" in html
        assert r"\(\{x\}\)" in html

    def test_comparison_in_formula_is_escaped(self):
        assert r"\(a&lt;b\)" in process_markdown_with_latex("So $a<b$")

    def test_amounts_are_not_formulas(self):
        assert process_markdown_with_latex("Cost $5 to $10") == "<p>Cost $5 to $10</p>"
        assert process_markdown_with_latex("From $5 to $10 and $x$") == "<p>From $5 to $10 and \\(x\\)</p>"
        assert process_markdown_with_latex("<b>$5</b> to $10 and $y^2$") == "<b>$5</b> to $10 and \\(y^2\\)"

    def test_escaped_dollar_is_a_dollar(self):
        assert process_markdown_with_latex(r"Price: \$5, $x_1$") == "<p>Price: $5, \\(x_1\\)</p>"

    def test_single_quotes_in_style_values(self):
        attrs = _parse_style_class({"font_family": "'Open Sans', sans-serif", "class": "a"})
        assert attrs == "style='font-family: &#39;Open Sans&#39;, sans-serif;' class='a'"


@pytest.mark.unit
@pytest.mark.handlers
class TestDetection:
    def test_sentence_naming_a_file_is_text(self):
        slide = Slide()
        slide.add_content(["respysive.org offers logo.png and more"])
        assert "<p" in slide.content

    def test_forced_image_without_extension(self, tmp_path):
        picture = tmp_path / "picture"
        picture.write_bytes(b"\x89PNG")
        slide = Slide()
        slide.add_content([str(picture)], content_types=["image"])
        assert "data:image/png;base64," in slide.content

    def test_forced_altair_without_schema(self):
        slide = Slide()
        slide.add_content([{"mark": "bar", "data": {"values": [{"a": 1}]}}], content_types=["altair"])
        assert "vegaEmbed(" in slide.content

    def test_custom_library_name_with_a_dot(self):
        slide = Slide()
        slide.add_custom_content("chart.js", {"type": "bar"})
        assert "function initialize_chart_js()" in slide.content

    def test_custom_config_can_be_reused(self):
        config = {"type": "bar"}
        ids = []
        for _ in range(2):
            slide = Slide()
            slide.add_custom_content("lib", config)
            ids.append(re.search(r'<div id="([^"]+)"', slide.content).group(1))
        assert ids[0] != ids[1]
        assert config == {"type": "bar"}

    def test_remote_image_type_ignores_the_query_string(self):
        class Response:
            headers = {"content-type": "image/svg+xml; charset=utf-8"}
            content = b"<svg/>"

            def raise_for_status(self):
                pass

        from unittest.mock import patch

        with patch("respysive.utils.requests.get", return_value=Response()) as get:
            uri = encode_image_to_data_uri("https://example.org/logo.svg?v=2")
        assert uri.startswith("data:image/svg+xml;base64,")
        assert get.call_args.kwargs["timeout"]


@pytest.mark.unit
@pytest.mark.utilities
class TestGeojsonBbox:
    def _collection(self, *geometries):
        return {
            "type": "FeatureCollection",
            "features": [{"type": "Feature", "properties": None, "geometry": g} for g in geometries],
        }

    def test_polygons_are_filtered(self):
        inside = {"type": "Polygon", "coordinates": [[[0, 40], [10, 40], [10, 50], [0, 40]]]}
        outside = {"type": "Polygon", "coordinates": [[[100, 0], [101, 0], [101, 1], [100, 0]]]}
        result = filter_geojson_bbox(self._collection(inside, outside, None), [-10, 35, 40, 70])
        assert [f["geometry"] for f in result["features"]] == [inside]


@pytest.mark.unit
@pytest.mark.presentation
class TestLocalTheme:
    def test_local_theme_replaces_the_reveal_stylesheet(self):
        set_local_css_urls({"theme": "themes/moon.css"})
        try:
            html = Presentation().to_html(theme="moon")
        finally:
            LOCAL_CSS_URLS.pop("theme", None)
        assert "href='themes/moon.css'" in html
        assert "reveal.js" not in html.split("</head>")[0].split("<style")[0]


@pytest.mark.unit
@pytest.mark.slide
class TestSplitTitlePage:
    def test_full_height_keeps_the_background_image(self, tmp_path):
        picture = tmp_path / "bg.png"
        picture.write_bytes(b"\x89PNG")
        slide = Slide()
        slide.add_split_title_page({"title": "T"}, "text", full_height=True, background_image=str(picture))
        assert slide.kwargs["data-background-image"].startswith("data:image/png")
