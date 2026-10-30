"""Tests for the PDF exporter (headless Chromium through Playwright)."""

import asyncio
import re

import pytest

from respysive import Presentation, Slide
from respysive.exporters import PdfExporter
from respysive.exporters.browser import run_in_browser

pytestmark = [pytest.mark.slow, pytest.mark.runtime]

WEBGL_CANVAS = """<canvas id="gl" width="60" height="40"></canvas>
<script>
const gl = document.getElementById("gl").getContext("webgl", {preserveDrawingBuffer: false});
gl.clearColor(1, 0, 0, 1);
gl.clear(gl.COLOR_BUFFER_BIT);
</script>"""


def _pages(pdf):
    return len(re.findall(rb"/Type\s*/Page[^s]", pdf))


def _page_size(pdf):
    match = re.search(rb"/MediaBox\s*\[\s*0\s+0\s+([\d.]+)\s+([\d.]+)\s*\]", pdf)
    return float(match.group(1)), float(match.group(2))


@pytest.fixture
def deck():
    pytest.importorskip("playwright")
    s1 = Slide()
    s1.add_title("One")
    s2 = Slide()
    s2.add_content(["<ul><li>a</li><li>b</li></ul>"], fragment_items=True)
    s3 = Slide()
    s3.add_title("Last", fragment=True)
    p = Presentation()
    p.add_slide([s1, [s2, Slide()], s3])
    return p


def _export(presentation, **kwargs):
    try:
        return PdfExporter(presentation, **kwargs).export(theme=None)
    except RuntimeError as err:
        pytest.skip(str(err))


def test_one_page_per_slide(deck):
    pdf = _export(deck)
    assert _pages(pdf) == 4
    assert _page_size(pdf) == (960, 540)  # 1280 x 720 px


def test_one_page_per_fragment_step(deck):
    # s2: 2 extra steps (none shown, "a" shown), s3: 1 extra step (title hidden)
    assert _pages(_export(deck, fragments=True)) == 7


def test_save_pdf(deck, tmp_path):
    target = tmp_path / "deck.pdf"
    try:
        deck.save_pdf(target, theme=None, width=1920, height=1080)
    except RuntimeError as err:
        pytest.skip(str(err))
    pdf = target.read_bytes()
    assert pdf.startswith(b"%PDF")
    assert _page_size(pdf) == (1440, 810)


def test_webgl_canvas_frozen():
    pytest.importorskip("playwright")
    s = Slide()
    s.add_content([WEBGL_CANVAS])
    p = Presentation()
    p.add_slide(s)

    def count(page):
        return page.evaluate(
            "() => [document.querySelectorAll('canvas').length, document.querySelectorAll('img').length]"
        )

    try:
        canvases, images = run_in_browser(p.to_html(theme=None), 1280, 720, count)
    except RuntimeError as err:
        pytest.skip(str(err))
    assert (canvases, images) == (0, 1)


def test_export_inside_event_loop(deck):
    async def notebook_cell():
        return _export(deck)

    assert _pages(asyncio.run(notebook_cell())) == 4
