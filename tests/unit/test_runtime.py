"""
Tests for the respysive v2 runtime: HTML structure, fragments, overflow
modes, backgrounds, and browser behaviour (navigation, fitting, print).
"""

import re

import pytest

from respysive import Column, Presentation, Row, Slide
from respysive.presentation import _background_layer, _bootstrap_canvas_css
from respysive.utils import _dedupe_svg_ids, _fragment_class

pytestmark = pytest.mark.runtime


def _deck(*slides, **kwargs):
    p = Presentation()
    p.add_slide(list(slides))
    return p.to_html(theme=None, **kwargs)


@pytest.mark.unit
@pytest.mark.presentation
class TestRuntimeHtml:
    """Structure of the generated document."""

    def test_no_reveal_js(self):
        html = _deck(Slide())
        assert "reveal.js@" not in html
        assert "require.min.js" not in html
        assert "window.respysive" in html

    def test_runtime_config(self):
        html = _deck(Slide(), width=1920, height=1080, transition="fade", overflow="warn")
        assert '"width": 1920' in html
        assert '"transition": "fade"' in html
        assert '"overflow": "warn"' in html
        assert "@page { size: 1920px 1080px; margin: 0; }" in html
        assert "--rs-w: 1920px; --rs-h: 1080px;" in html

    def test_vertical_stack(self):
        html = _deck(Slide(), [Slide(), Slide()])
        canvas = html.split('<div class="slides rs-canvas"', 1)[1].split("<script>", 1)[0]
        assert "<section class='stack'>" in canvas
        assert canvas.count('<section class="rs-slide') == 3

    def test_center_class(self):
        assert '<html class="rs-center">' in _deck(Slide())
        assert '<html class="">' in _deck(Slide(), center=False)

    def test_custom_class_and_attributes(self):
        html = _deck(Slide(**{"class": ["branded", "dark"], "id": "intro"}))
        assert 'class="rs-slide branded dark"' in html
        assert 'id="intro"' in html

    def test_invalid_transition(self):
        with pytest.raises(ValueError):
            _deck(Slide(), transition="zoom")

    def test_invalid_overflow(self):
        with pytest.raises(ValueError):
            _deck(Slide(), overflow="shrink")
        with pytest.raises(ValueError):
            Slide(overflow="shrink")

    def test_slide_overflow_attribute(self):
        assert 'data-overflow="visible"' in _deck(Slide(overflow="visible"))

    def test_scroll_mode_removed(self):
        with pytest.raises(ValueError):
            Slide(overflow="scroll")

    def test_notes_inside_slide(self):
        s = Slide()
        s.add_notes("Remember this")
        html = _deck(s)
        assert '<aside class="notes">' in html


@pytest.mark.unit
class TestBackgrounds:
    """data-background-* kwargs become a background layer."""

    def test_color(self):
        layer = _background_layer({"data-background-color": "#203040"})
        assert 'class="rs-bg"' in layer
        assert "background-color: #203040" in layer

    def test_image_and_gradient(self):
        layer = _background_layer(
            {
                "data-background-image": "data:image/png;base64,AAAA",
                "data-background-gradient": "linear-gradient(red, blue)",
                "data-background-size": "contain",
            }
        )
        assert "url(&#x27;data:image/png;base64,AAAA&#x27;), linear-gradient(red, blue)" in layer
        assert "background-size: contain" in layer

    def test_no_background(self):
        assert _background_layer({"id": "x"}) == ""

    def test_background_not_in_section_attributes(self):
        html = _deck(Slide(**{"data-background-color": "red"}))
        assert 'data-background-color="red"' not in html
        assert "background-color: red" in html


@pytest.mark.unit
class TestFragments:
    """Fragment options on Slide methods."""

    def test_fragment_class(self):
        assert _fragment_class(None) == ""
        assert _fragment_class(False) == ""
        assert _fragment_class(True) == "fragment"
        assert _fragment_class("fade-up") == "fragment fade-up"
        assert _fragment_class([True, None, "grow"], 0) == "fragment"
        assert _fragment_class([True, None, "grow"], 1) == ""
        assert _fragment_class([True, None, "grow"], 2) == "fragment grow"
        assert _fragment_class([True], 5) == ""

    def test_add_title_fragment(self):
        s = Slide()
        s.add_title("Hello", fragment="fade-up")
        assert "<div class='row fragment fade-up'>" in s.content

    def test_add_content_fragment_per_item(self):
        s = Slide()
        s.add_content(["a", "b"], columns=[6, 6], fragment=[None, True])
        assert "<div class='col-md-6'>" in s.content
        assert "<div class='col-md-6 fragment'>" in s.content

    def test_add_content_fragment_with_style_class(self):
        s = Slide()
        s.add_content(["a"], styles=[{"class": "bg-info", "color": "red"}], fragment=True)
        assert "class='col-md-12 fragment bg-info'" in s.content
        assert "color: red" in s.content

    def test_add_content_none_style(self):
        s = Slide()
        s.add_content(["a", "b"], columns=[6, 6], styles=[None, {"color": "red"}])
        assert "<div class='col-md-6' >" in s.content
        assert "<div class='col-md-6' style='color: red;'>" in s.content

    def test_fragment_items(self):
        s = Slide()
        s.add_content(["<ul><li>a</li><li>b</li></ul>"], fragment_items="fade-up")
        assert "class='fragment-items' data-fragment-style='fade-up'" in s.content

    def test_card_fragment(self):
        s = Slide()
        s.add_card([{"title": "A"}, {"title": "B"}], fragment=True)
        assert s.content.count(' fragment"') == 2


@pytest.mark.unit
class TestBootstrapCanvas:
    """Bootstrap is loaded, with breakpoints pinned to the fixed-size canvas."""

    def test_columns_without_media_queries(self):
        css = _bootstrap_canvas_css()
        assert ".reveal .col-md-6{flex:0 0 50%;max-width:50%}" in css
        assert ".reveal .col-xl-12{flex:0 0 100%;max-width:100%}" in css
        assert ".reveal .offset-md-3{margin-left:25%}" in css
        assert "@media" not in css

    def test_breakpoints_ordered(self):
        css = _bootstrap_canvas_css()
        assert css.index(".col-sm-6{") < css.index(".col-md-6{") < css.index(".col-xl-6{")

    def test_gutter_classes(self):
        assert ".reveal .row.g-3{" in _bootstrap_canvas_css()

    def test_bootstrap_always_loaded(self):
        assert "bootstrap.min.css" in _deck(Slide())
        assert "bootstrap.min.css" in _deck(Slide(), libraries=["d3"])


def _open_deck(presentation, tmp_path):
    """Save the deck and yield a Chromium page showing it, or skip without Playwright."""
    sync_api = pytest.importorskip("playwright.sync_api")
    html_file = tmp_path / "deck.html"
    presentation.save_html(str(html_file), theme=None)

    with sync_api.sync_playwright() as pw:
        try:
            browser = pw.chromium.launch()
        except Exception as exc:
            pytest.skip(f"Chromium not available: {exc}")
        pg = browser.new_page(viewport={"width": 1280, "height": 720})
        # keep the test offline: CDN libraries are not needed by the runtime
        pg.route("**/*", lambda r: r.abort() if r.request.url.startswith("http") else r.continue_())
        pg.goto(html_file.as_uri(), wait_until="load")
        pg.evaluate("respysive.ready")
        yield pg
        browser.close()


@pytest.mark.slow
class TestRuntimeBrowser:
    """Runtime behaviour in headless Chromium (skipped without Playwright)."""

    @pytest.fixture
    def page(self, tmp_path):
        s1 = Slide()
        s1.add_title("One")
        s1.add_notes("Notes one")
        s2 = Slide()
        s2.add_content(["<ul><li>a</li><li>b</li></ul>"], fragment_items=True)
        s2.add_content(["c"], fragment=True)
        s3 = Slide()
        s3.add_content(["<ul>" + "<li>line</li>" * 16 + "</ul>"])
        s4 = Slide()
        s4.add_content(["<div style='height: 2000px'>tall</div>"])
        s5 = Slide(overflow="visible")
        s5.add_content(["<div style='height: 2000px'>tall</div>"])
        p = Presentation()
        p.add_slide([s1, [s2, s3], s4, s5])
        yield from _open_deck(p, tmp_path)

    def test_navigation_and_fragments(self, page):
        steps = []
        for _ in range(6):
            page.keyboard.press("Space")
            steps.append(page.evaluate("respysive.state()"))
        assert steps == [
            {"h": 1, "v": 0, "f": -1},
            {"h": 1, "v": 0, "f": 0},
            {"h": 1, "v": 0, "f": 1},
            {"h": 1, "v": 0, "f": 2},
            {"h": 1, "v": 1, "f": -1},
            {"h": 2, "v": 0, "f": -1},
        ]
        page.keyboard.press("PageUp")
        assert page.evaluate("respysive.state()") == {"h": 1, "v": 1, "f": -1}
        page.keyboard.press("PageUp")
        assert page.evaluate("respysive.state()") == {"h": 1, "v": 0, "f": 2}
        assert page.evaluate("location.hash") == "#/1/0/2"

    def test_overflow_fit(self, page):
        report = {(r["h"], r["v"]): r for r in page.evaluate("respysive.overflowReport()")}
        assert report[(1, 1)]["fontScale"] < 1 and report[(1, 1)]["zoom"] == 1
        assert report[(2, 0)]["zoom"] < 1
        assert (3, 0) not in report

    def test_print_mode_keeps_fit(self, page):
        page.emulate_media(media="print")
        page.evaluate("window.dispatchEvent(new Event('beforeprint'))")
        report = {(r["h"], r["v"]): r for r in page.evaluate("respysive.overflowReport()")}
        assert report[(2, 0)]["zoom"] < 1
        assert (3, 0) not in report
        pdf = page.pdf(print_background=True, prefer_css_page_size=True)
        assert len(re.findall(rb"/Type\s*/Page[^s]", pdf)) == 5


_CLIPPED_SVG = (
    '<svg width="100" height="100"><defs><clipPath id="clip-main">'
    '<rect x="{x}" y="0" width="100" height="100"/></clipPath></defs>'
    '<rect id="shape" clip-path="url(#clip-main)" width="100" height="100" fill="red"/></svg>'
)


@pytest.mark.unit
class TestSvgIds:
    """Inline SVGs repeating an id get their own copy."""

    def test_repeated_ids_are_renamed_with_their_references(self):
        html = _dedupe_svg_ids(_CLIPPED_SVG.format(x=0) + "<p id='clip-main'></p>" + _CLIPPED_SVG.format(x=0))
        first, second = html.split("<p id='clip-main'></p>")
        assert 'id="clip-main"' in first and "url(#clip-main)" in first
        assert 'id="clip-main--2"' in second and "url(#clip-main--2)" in second
        assert 'id="shape--2"' in second

    def test_unique_ids_untouched(self):
        html = '<svg><g id="a"/><use href="#a"/></svg><svg><g id="b"/><use xlink:href="#b"/></svg>'
        assert _dedupe_svg_ids(html) == html

    def test_nested_svg_is_one_block(self):
        html = '<svg id="a"><svg><g id="a"/></svg></svg><svg><g id="a"/><use href="#a"/></svg>'
        assert _dedupe_svg_ids(html).endswith('<svg><g id="a--1"/><use href="#a--1"/></svg>')

    def test_applied_to_slides(self):
        slides = []
        for _ in range(2):
            s = Slide()
            s.add_content([_CLIPPED_SVG.format(x=0)])
            slides.append(s)
        html = _deck(*slides)
        assert html.count('id="clip-main"') == 1
        assert 'id="clip-main--2"' in html


@pytest.mark.slow
class TestLayoutHelpers:
    """Reveal.js layout classes (r-fit-text, r-stack), window backgrounds and inline SVG clips."""

    @pytest.fixture
    def page(self, tmp_path):
        s1 = Slide(**{"data-background-color": "rgb(10, 20, 30)"})
        s1.add_content([_CLIPPED_SVG.format(x=200)])  # clips everything away
        s2 = Slide()
        s2.add_title("A much longer title that would wrap on two lines at the theme size", **{"class": "r-fit-text"})
        s2.add_content(
            [
                '<div style="width: 300px"><span class="r-fit-text">Short</span></div>'
                '<div class="r-stack"><p>first</p><p class="fragment">second</p></div>'
            ]
        )
        s3 = Slide()
        s3.add_content([_CLIPPED_SVG.format(x=0)])
        # right column split in two rows of blocks sized by their width
        square = '<div style="width: 100%; aspect-ratio: 1; background: #888"></div>'
        s4 = Slide()
        s4.add_title("Nested")
        s4.add_layout(Row([Column(4, "text"), Column(8, [Row(square), Row(square)])]))
        p = Presentation()
        p.add_slide([s1, s2, s3, s4])
        yield from _open_deck(p, tmp_path)

    def test_fit_text_fills_width_on_one_line(self, page):
        page.evaluate("respysive.go(1, 0)")
        sizes = page.evaluate(
            """() => [...document.querySelectorAll('.present .r-fit-text')].map(el => ({
                size: parseFloat(getComputedStyle(el).fontSize),
                lines: Math.round(el.offsetHeight / parseFloat(getComputedStyle(el).lineHeight)),
                fill: el.getBoundingClientRect().width / el.parentNode.getBoundingClientRect().width}))"""
        )
        long, short = sizes
        assert short["size"] > long["size"]
        assert long["lines"] == 1
        assert all(abs(s["fill"] - 1) < 0.02 for s in sizes)

    def test_stack_overlaps_children(self, page):
        page.evaluate("respysive.go(1, 0)")
        tops = page.evaluate("[...document.querySelectorAll('.present .r-stack > p')].map(p => p.offsetTop)")
        assert tops[0] == tops[1]

    def test_clip_path_resolves_on_its_own_slide(self, page):
        page.evaluate("respysive.go(2, 0)")
        page.wait_for_timeout(600)
        box = page.evaluate("document.querySelector('.present svg').getBoundingClientRect().toJSON()")
        shot = page.screenshot(clip={k: box[k] for k in ("x", "y", "width", "height")})
        from io import BytesIO

        from PIL import Image

        r, g, b, *_ = Image.open(BytesIO(shot)).convert("RGB").getpixel((int(box["width"] / 2), int(box["height"] / 2)))
        assert r > 200 and g < 80 and b < 80

    def test_background_covers_window(self, page):
        page.evaluate("respysive.go(0, 0)")
        view = page.evaluate("document.querySelector('.rs-bg-view.present').getBoundingClientRect().toJSON()")
        assert (view["x"], view["y"], view["width"], view["height"]) == (0, 0, 1280, 720)
        in_slide = "getComputedStyle(document.querySelector('section.present > .rs-bg')).visibility"
        assert page.evaluate(in_slide) == "hidden"
        page.keyboard.press("Escape")
        assert page.evaluate(in_slide) == "visible"
        assert page.evaluate("getComputedStyle(document.querySelector('.rs-backgrounds')).display") == "none"

    def test_width_sized_content_scaled_to_fit(self, page):
        page.evaluate("respysive.go(3, 0)")
        fit = page.evaluate(
            """() => { const s = document.querySelector('section.present'), b = s.querySelector('.rs-body');
                return [b.getBoundingClientRect().height / s.getBoundingClientRect().height,
                        b.getBoundingClientRect().top - s.getBoundingClientRect().top, +s.dataset.rsZoom]; }"""
        )
        height, top, zoom = fit
        assert zoom < 0.5
        assert height <= 1 and top >= 0


@pytest.mark.slow
def test_runs_in_srcdoc_iframe():
    """A deck embedded with srcdoc has no URL to update, and still lays out its slides."""
    import html

    sync_api = pytest.importorskip("playwright.sync_api")
    slide = Slide()
    slide.add_title("Embedded")
    deck_html = _deck(slide)
    page_html = f'<iframe srcdoc="{html.escape(deck_html, quote=True)}" style="width:640px;height:360px"></iframe>'
    with sync_api.sync_playwright() as pw:
        try:
            browser = pw.chromium.launch()
        except Exception as exc:
            pytest.skip(f"Chromium not available: {exc}")
        page = browser.new_page()
        page.route("**/*", lambda r: r.abort() if r.request.url.startswith("http") else r.continue_())
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.set_content(page_html, wait_until="load")
        frame = page.frames[1]
        frame.evaluate("respysive.ready")
        assert "scale(" in frame.evaluate("document.querySelector('.rs-canvas').style.transform")
        assert errors == []
        browser.close()
