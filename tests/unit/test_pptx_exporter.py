"""Tests for the PPTX exporter built from the layout rendered by Chromium."""

import pytest

from respysive import Presentation, Slide
from respysive.exporters import PptxExporter

pytestmark = [pytest.mark.slow, pytest.mark.runtime]

PX = 9525


@pytest.fixture
def exported():
    pytest.importorskip("playwright")
    pytest.importorskip("pptx")
    title = Slide()
    title.add_title("Hello <b>bold</b>", tag="h2", color="rgb(200, 0, 0)")
    title.add_content(["<ul><li>one</li><li>two<ul><li>nested</li></ul></li></ul>"])
    title.add_notes("Speaker notes here")
    cards = Slide()
    cards.add_card([{"title": "Card", "text": "Body"}], styles=[{"background-color": "#336699"}])
    cards.add_content(['<svg width="200" height="100"><rect width="200" height="100" fill="red"/></svg>'])
    p = Presentation()
    p.add_slide([title, cards])
    try:
        return PptxExporter(p).export(theme=None)
    except RuntimeError as err:
        pytest.skip(str(err))


def _texts(slide):
    return [shape for shape in slide.shapes if shape.has_text_frame and shape.text_frame.text.strip()]


def test_slide_size(exported):
    assert (exported.slide_width, exported.slide_height) == (1280 * PX, 720 * PX)


def test_title_is_native_text(exported):
    title = next(s for s in _texts(exported.slides[0]) if s.text_frame.text.startswith("Hello"))
    runs = title.text_frame.paragraphs[0].runs
    assert [r.text for r in runs] == ["Hello ", "bold"]
    assert runs[1].font.bold
    assert str(runs[0].font.color.rgb) == "C80000"
    assert runs[0].font.size.pt > 20


def test_list_has_native_bullets_and_levels(exported):
    shape = next(s for s in _texts(exported.slides[0]) if "one" in s.text_frame.text)
    paragraphs = shape.text_frame.paragraphs
    assert [p.text for p in paragraphs] == ["one", "two", "nested"]
    assert [p.level for p in paragraphs] == [0, 0, 1]
    assert all(
        p._p.pPr.find("{http://schemas.openxmlformats.org/drawingml/2006/main}buChar") is not None for p in paragraphs
    )


def test_notes(exported):
    assert exported.slides[0].notes_slide.notes_text_frame.text == "Speaker notes here"


def test_card_background_and_chart_picture(exported):
    from pptx.enum.shapes import MSO_SHAPE_TYPE

    shapes = list(exported.slides[1].shapes)
    fills = [
        str(s.fill.fore_color.rgb) for s in shapes if s.shape_type == MSO_SHAPE_TYPE.AUTO_SHAPE and s.fill.type == 1
    ]
    assert "336699" in fills
    pictures = [s for s in shapes if s.shape_type == MSO_SHAPE_TYPE.PICTURE]
    assert len(pictures) == 1
    assert pictures[0].width == pytest.approx(200 * PX, rel=0.05)


def test_fails_clearly_without_chromium(monkeypatch):
    def no_browser(*args, **kwargs):
        raise RuntimeError("Chromium is not available.")

    monkeypatch.setattr("respysive.exporters.pptx_exporter.run_in_browser", no_browser)
    s = Slide()
    s.add_title("No browser")
    p = Presentation()
    p.add_slide(s)
    with pytest.raises(RuntimeError, match="Chromium"):
        PptxExporter(p).export()


@pytest.fixture
def plotly_deck():
    pytest.importorskip("playwright")
    pytest.importorskip("pptx")
    from respysive.assets import OfflineAssetError, fetch
    from respysive.dependencies import JS_URLS

    try:
        fetch(JS_URLS["plotly"])  # exports below embed Plotly from the cache
    except OfflineAssetError as err:
        pytest.skip(str(err))

    def build(*figures):
        p = Presentation()
        for figure in figures:
            s = Slide()
            s.add_content([figure])
            p.add_slide(s)
        return p

    return build


def _export_offline(presentation, **options):
    try:
        return PptxExporter(presentation, **options).export(theme=None, offline=True)
    except RuntimeError as err:
        pytest.skip(str(err))


BARS = {
    "data": [
        {"type": "bar", "name": "gold", "x": ["A", "B"], "y": [3, 5], "marker": {"color": "#ff0000"}},
        {"type": "bar", "name": "silver", "x": ["A", "B"], "y": [2, 1]},
    ],
    "layout": {"barmode": "stack", "title": {"text": "Medals"}},
}
PIE = {"data": [{"type": "pie", "labels": ["A", "B", "C"], "values": [30, 50, 20]}], "layout": {}}
HEATMAP = {"data": [{"type": "heatmap", "z": [[1, 2], [3, 4]]}], "layout": {}}
BUBBLES = {"data": [{"type": "scatter", "mode": "markers", "x": [1, 2], "y": [3, 4], "marker": {"size": [10, 40]}}]}


def test_plotly_bars_become_native_chart(plotly_deck):
    from pptx.enum.chart import XL_CHART_TYPE

    prs = _export_offline(plotly_deck(BARS))
    chart = next(s for s in prs.slides[0].shapes if s.has_chart).chart
    assert chart.chart_type == XL_CHART_TYPE.COLUMN_STACKED
    assert list(chart.plots[0].categories) == ["A", "B"]
    assert [(s.name, list(s.values)) for s in chart.plots[0].series] == [("gold", [3, 5]), ("silver", [2, 1])]
    assert str(chart.plots[0].series[0].format.fill.fore_color.rgb) == "FF0000"
    assert chart.chart_title.text_frame.text == "Medals"


def test_plotly_pie_keeps_drawn_order(plotly_deck):
    prs = _export_offline(plotly_deck(PIE))
    chart = next(s for s in prs.slides[0].shapes if s.has_chart).chart
    # Plotly sorts slices by value (B, A, C) and turns counterclockwise, so
    # clockwise from 12 o'clock, as PowerPoint draws them: B, C, A
    assert list(chart.plots[0].categories) == ["B", "C", "A"]
    assert not chart.has_title


def test_unsupported_or_disabled_charts_are_pictures(plotly_deck):
    from pptx.enum.shapes import MSO_SHAPE_TYPE

    def kinds(prs):
        return [
            [s.shape_type for s in slide.shapes if s.shape_type in (MSO_SHAPE_TYPE.CHART, MSO_SHAPE_TYPE.PICTURE)]
            for slide in prs.slides
        ]

    picture, chart = [MSO_SHAPE_TYPE.PICTURE], [MSO_SHAPE_TYPE.CHART]
    assert kinds(_export_offline(plotly_deck(HEATMAP, BUBBLES, BARS))) == [picture, picture, chart]
    assert kinds(_export_offline(plotly_deck(BARS), native_charts=False)) == [picture]
