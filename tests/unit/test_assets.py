"""
Tests for respysive.assets: library detection, manual libraries, local cache
and offline inlining. Network access is mocked.
"""

import base64
import html

import pytest

from respysive import Presentation, Slide, assets
from respysive.assets import (
    ASSETS_MARKER,
    OfflineAssetError,
    detect_libraries,
    inline_css,
    inline_external_resources,
    library_urls,
)
from respysive.dependencies import CSS_URLS

pytestmark = pytest.mark.unit

FAKE_FILES = {
    "https://cdn.example/lib.js": b"window.fakeLib = 1; var s = 'srcdoc=\"x\" </body>'; var t = '</script>';",
    "https://cdn.example/style.css": b"@import url('extra.css'); .a { background: url(img/bg.png); }",
    "https://cdn.example/extra.css": b".b { color: red; }",
    "https://cdn.example/img/bg.png": b"PNGDATA",
    "https://cdn.example/fonts.css": (
        b"@font-face{font-family:'X';src:url(x.eot)}"
        b"@font-face{font-family:'X';src:url(x.eot?#iefix) format('embedded-opentype'),"
        b"url(x.woff) format('woff'),url(x.ttf) format('truetype')}"
        b'@font-face{font-family:"Font Awesome 6 Free";src:url(fa.woff2) format("woff2"),url(fa.ttf) format("truetype")}'
        b'@font-face{font-family:"FontAwesome";font-display:block;src:url(fa.woff2) format("woff2")}'
        b'@font-face{font-family:"Font Awesome 5 Free";font-weight:900;src:url(fa.woff2) format("woff2")}'
    ),
    "https://cdn.example/x.woff": b"WOFF",
    "https://cdn.example/x.ttf": b"TTF",
    "https://cdn.example/x.eot": b"EOT",
    "https://cdn.example/fa.woff2": b"WOFF2",
    "https://cdn.example/fa.ttf": b"FATTF",
    CSS_URLS["bootstrap"]: b".row{display:flex}",
}


@pytest.fixture
def fake_network(tmp_path, monkeypatch):
    """Serve FAKE_FILES instead of the network, with an isolated cache."""
    monkeypatch.setenv("RESPYSIVE_CACHE", str(tmp_path / "cache"))
    calls = []

    def download(url):
        calls.append(url)
        if url not in FAKE_FILES:
            raise ConnectionError("offline")
        return FAKE_FILES[url]

    monkeypatch.setattr(assets, "_download", download)
    return calls


class TestDetection:
    def test_detects_used_libraries_in_load_order(self):
        page = "<script>Plotly.newPlot('a')</script><i class='fas fa-star'></i> \\(x\\)"
        assert detect_libraries(page) == ["fontawesome", "mathjax", "plotly"]

    def test_text_only_deck_loads_nothing(self):
        assert detect_libraries("<p>Hello</p>") == []

    def test_iframe_content_is_ignored(self):
        frame = html.escape("<script>new maplibregl.Map({})</script>", quote=True)
        assert detect_libraries(f'<iframe srcdoc="{frame}"></iframe>') == []

    def test_library_urls(self):
        css, js = library_urls(["vega", "fontawesome"])
        assert [k for k, _ in css] == ["fontawesome"]
        assert [k for k, _ in library_urls(["fontawesome", "bootstrap"])[0]] == ["bootstrap", "fontawesome"]
        assert [k for k, _ in js] == ["vega", "vega-lite", "vega-embed"]

    def test_unknown_library(self):
        with pytest.raises(ValueError):
            library_urls(["nope"])


class TestPresentationLibraries:
    def _head(self, p, **kwargs):
        return p.to_html(theme=None, **kwargs).split("</head>")[0]

    def test_only_used_libraries_are_loaded(self):
        p = Presentation()
        s = Slide()
        s.add_content(["just text"])
        p.add_slide(s)
        head = self._head(p)
        assert "<script src=" not in head
        assert head.count("<link") == 1 and "bootstrap.min.css" in head

    def test_add_library_builtin(self):
        p = Presentation()
        p.add_slide(Slide())
        p.add_library("mathjax")
        assert "mathjax" in self._head(p)

    def test_add_library_urls(self):
        p = Presentation()
        p.add_slide(Slide())
        p.add_library(js="https://cdn.example/lib.js", css=["https://cdn.example/style.css"])
        head = self._head(p)
        assert "<script src='https://cdn.example/lib.js'" in head
        assert "href='https://cdn.example/style.css'" in head

    def test_add_library_unknown_name(self):
        with pytest.raises(ValueError):
            Presentation().add_library("chartjs")

    def test_plotly_tile_map_loads_maplibre_stylesheet(self):
        figure = {"data": [{"type": "scattermap", "lat": [45], "lon": [3]}], "layout": {}}
        p = Presentation()
        s = Slide()
        s.add_content([figure], content_types=["plotly"])
        p.add_slide(s)
        head = self._head(p)
        assert "maplibre-gl.css" in head and "maplibre-gl.js" not in head

    def test_plotly_chart_without_tiles_skips_maplibre(self):
        # The default Plotly template names every trace type, scattermap included
        figure = {"data": [{"type": "bar", "y": [1]}], "layout": {"template": {"data": {"scattermap": [{}]}}}}
        p = Presentation()
        s = Slide()
        s.add_content([figure], content_types=["plotly"])
        p.add_slide(s)
        assert "maplibre" not in self._head(p)

    def test_maplibre_stylesheet_listed_once(self):
        css, _ = library_urls(["plotly-map", "maplibre"])
        assert [k for k, _ in css] == ["maplibre"]

    def test_libraries_all_and_explicit(self):
        p = Presentation()
        p.add_slide(Slide())
        assert "cdn.plot.ly" in self._head(p, libraries="all")
        head = self._head(p, libraries=["d3"])
        assert "d3@7" in head and "cdn.plot.ly" not in head


class TestCache:
    def test_cache_dir_override(self, tmp_path, monkeypatch):
        monkeypatch.setenv("RESPYSIVE_CACHE", str(tmp_path / "c"))
        assert assets.cache_dir() == tmp_path / "c"
        assert (tmp_path / "c").is_dir()

    def test_fetch_uses_cache(self, fake_network):
        assert assets.fetch("https://cdn.example/lib.js") == FAKE_FILES["https://cdn.example/lib.js"]
        assets.fetch("https://cdn.example/lib.js")
        assert fake_network == ["https://cdn.example/lib.js"]

    def test_fetch_missing(self, fake_network):
        with pytest.raises(OfflineAssetError, match="download_libraries"):
            assets.fetch("https://cdn.example/missing.js")

    def test_fetch_local_file(self, tmp_path):
        f = tmp_path / "a.css"
        f.write_text("p{}")
        assert assets.fetch(str(f)) == b"p{}"
        assert assets.fetch(f.as_uri()) == b"p{}"

    def test_fetch_file_uri_with_space(self, tmp_path):
        f = tmp_path / "my libs" / "a.css"
        f.parent.mkdir()
        f.write_text("p{}")
        assert "%20" in f.as_uri()
        assert assets.fetch(f.as_uri()) == b"p{}"


class TestInlineCss:
    def test_imports_and_urls(self, fake_network):
        css = inline_css("https://cdn.example/style.css")
        assert ".b { color: red; }" in css
        assert "@import" not in css
        assert f'url("data:image/png;base64,{base64.b64encode(b"PNGDATA").decode()}")' in css

    def test_font_sources(self, fake_network):
        css = inline_css("https://cdn.example/fonts.css")
        woff = base64.b64encode(b"WOFF").decode()
        assert f"src: url(\"data:font/woff;base64,{woff}\") format('woff')" in css
        assert "https://cdn.example/x.eot" not in fake_network
        assert "https://cdn.example/x.ttf" not in fake_network
        assert "https://cdn.example/fa.ttf" not in fake_network

    def test_font_awesome_aliases_dropped(self, fake_network):
        css = inline_css("https://cdn.example/fonts.css")
        assert css.count(base64.b64encode(b"WOFF2").decode()) == 1
        assert '"FontAwesome"' not in css and "Font Awesome 5" not in css

    def test_local_stylesheet(self, tmp_path):
        (tmp_path / "f.woff2").write_bytes(b"LOCALFONT")
        theme = tmp_path / "theme.css"
        theme.write_text("@font-face{font-family:T;src:url(f.woff2) format('woff2')}")
        assert base64.b64encode(b"LOCALFONT").decode() in inline_css(str(theme))


class TestInliner:
    def _doc(self, body, head=""):
        return f"<html><head>{head}</head><body>{ASSETS_MARKER}{body}</body></html>"

    def test_page_resources_inlined_once(self, fake_network):
        tag = "<script src='https://cdn.example/lib.js'></script>"
        out = inline_external_resources(
            self._doc(tag + tag, "<link rel='stylesheet' href='https://cdn.example/style.css'>")
        )
        assert "src='https://cdn.example" not in out and "href='https://cdn.example" not in out
        assert out.count("window.fakeLib = 1") == 1

    def test_iframe_reads_library_from_page(self, fake_network):
        frame = html.escape(
            "<link href='https://cdn.example/style.css' rel='stylesheet'>"
            "<script src='https://cdn.example/lib.js'></script>",
            quote=True,
        )
        out = inline_external_resources(self._doc(f'<iframe srcdoc="{frame}"></iframe>' * 2))
        assert out.count("window.fakeLib = 1") == 1
        assert out.index('type="text/plain"') < out.index("<iframe")
        inner = html.unescape(out.split('<iframe srcdoc="', 1)[1].split('"', 1)[0])
        assert "parent.document.getElementById('rs-asset-" in inner
        assert "cdn.example" not in inner

    def test_iframe_shares_page_copy(self, fake_network):
        frame = html.escape("<script src='https://cdn.example/lib.js'></script>", quote=True)
        out = inline_external_resources(
            self._doc(f'<iframe srcdoc="{frame}"></iframe>', "<script src='https://cdn.example/lib.js'></script>")
        )
        assert out.count("window.fakeLib = 1") == 1
        assert 'type="text/plain"' not in out

    def test_closing_script_tag_escaped(self, fake_network):
        out = inline_external_resources(self._doc("", "<script src='https://cdn.example/lib.js'></script>"))
        assert "var t = '<\\/script>';" in out

    def test_library_code_with_srcdoc_text_untouched(self, fake_network):
        out = inline_external_resources(self._doc("", "<script src='https://cdn.example/lib.js'></script>"))
        assert "var s = 'srcdoc=\"x\" </body>';" in out


def test_offline_presentation(fake_network, tmp_path):
    p = Presentation()
    s = Slide()
    s.add_content(["text"])
    p.add_slide(s)
    p.add_library(js="https://cdn.example/lib.js", css="https://cdn.example/style.css")
    out = p.to_html(theme=None, offline=True)
    assert "window.fakeLib = 1" in out
    assert ".b { color: red; }" in out
    assert "https://cdn.example" not in out
    assert ".row{display:flex}" in out and "bootstrap.min.css" not in out


def test_offline_presentation_reports_missing_asset(fake_network):
    p = Presentation()
    p.add_slide(Slide())
    p.add_library(js="https://cdn.example/missing.js")
    with pytest.raises(OfflineAssetError):
        p.to_html(theme=None, offline=True)


class TestPlotlyGeoAssets:
    def test_topojson_from_scope_and_resolution(self):
        figure = {
            "data": [
                {"type": "choropleth", "locations": ["CA"]},
                {"type": "scattergeo", "geo": "geo2"},
                {"type": "choroplethmap"},
                {"type": "bar"},
            ],
            "layout": {"geo": {"scope": "usa"}, "geo2": {"scope": "north america", "resolution": 50}},
        }
        topojson, geojson = assets.plotly_geo_files([figure])
        assert topojson == {
            "usa_110m": "https://cdn.plot.ly/usa_110m.json",
            "north-america_50m": "https://cdn.plot.ly/north-america_50m.json",
        }
        assert geojson == set()

    def test_defaults_json_strings_and_geojson_urls(self):
        figure = '{"data": [{"type": "choropleth", "geojson": "https://cdn.example/regions.geojson"}]}'
        topojson, geojson = assets.plotly_geo_files([figure, "plain text", {"center": [0, 0]}])
        assert list(topojson) == ["world_110m"]
        assert geojson == {"https://cdn.example/regions.geojson"}

    def test_no_geo_chart_no_script(self):
        assert assets.plotly_geo_assets_script([{"data": [{"type": "bar"}]}]) == ""

    def test_slide_contents_walks_all_records(self):
        from respysive.layout import Column, Row
        from respysive.presentation import _slide_contents

        a, b = Slide(), Slide()
        a.add_content(["text", {"data": []}], columns=[6, 6])
        a.add_card([{"title": "t", "graph": "card graph"}])
        b.add_layout(Row([Column(6, "left"), Column(6, [Row("nested")])]))
        assert list(_slide_contents([a, [b]])) == ["text", {"data": []}, "card graph", "left", "nested"]

    def test_offline_deck_preloads_geo_files(self, fake_network, monkeypatch):
        monkeypatch.setitem(FAKE_FILES, "https://cdn.plot.ly/usa_110m.json", b'{"type": "Topology", "objects": {}}')
        monkeypatch.setattr("respysive.presentation.inline_external_resources", lambda doc: doc)
        s = Slide()
        s.add_content([{"data": [{"type": "choropleth"}], "layout": {"geo": {"scope": "usa"}}}])
        p = Presentation()
        p.add_slide(s)

        out = p.to_html(theme=None, offline=True)

        assert 'window.PlotlyGeoAssets = {"topojson":{"usa_110m":{"type":"Topology","objects":{}}}};' in out
        assert "PlotlyGeoAssets" not in p.to_html(theme=None)
