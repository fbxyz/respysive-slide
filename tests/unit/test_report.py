"""Tests for Presentation.check(): fitting, pictures, and network report."""

import pytest

from respysive import Presentation, Slide
from respysive.report import DeckReport, SlideReport

pytestmark = [pytest.mark.runtime, pytest.mark.slow]

LONG = "<ul>" + "".join(f"<li>Item {i}</li>" for i in range(30)) + "</ul>"


@pytest.fixture(scope="module")
def report():
    pytest.importorskip("playwright")
    from respysive.assets import OfflineAssetError

    short = Slide()
    short.add_title("Short")
    short.add_content(["One line."])
    tall = Slide()
    tall.add_title("Tall")
    tall.add_content([LONG])
    warned = Slide(overflow="warn")
    warned.add_title("Warned")
    warned.add_content([LONG])
    stacked = Slide()
    stacked.add_title("Below")
    deck = Presentation()
    deck.add_slide([short, [tall, stacked], warned])
    try:
        return deck.check(min_scale=0.9, theme=None, offline=True)
    except OfflineAssetError as err:
        pytest.skip(f"assets not cached: {err}")
    except RuntimeError as err:
        pytest.skip(str(err))


def test_numbers_and_titles(report):
    assert [(s.number, s.title) for s in report.slides] == [
        ("1", "Short"),
        ("2.1", "Tall"),
        ("2.2", "Below"),
        ("3", "Warned"),
    ]


def test_fitted_slide_is_small(report):
    short, tall = report.slides[0], report.slides[1]
    assert short.scale == 1
    assert tall.scale < 0.9
    assert [s.number for s in report.small] == ["2.1"]


def test_warn_mode_reports_overflow(report):
    warned = report.slides[3]
    assert warned.scale == 1
    assert warned.overflow > 1
    assert report.overflowing == [warned]
    assert not report.ok


def test_offline_deck_uses_no_network(report):
    assert report.network == []
    assert "none, the deck works offline" in str(report)


@pytest.mark.unit
def test_report_text():
    report = DeckReport(
        slides=[
            SlideReport("1", "Title", 1.0),
            SlideReport("2", "Chart", 0.55, pictures=["Plotly chart", "Plotly chart", "equation"]),
        ],
        min_scale=0.7,
        network=["cdn.plot.ly"],
    )
    text = str(report)
    assert "text at 55%  too small" in text
    assert "pictures: 2 Plotly chart, 1 equation" in text
    assert "Network: cdn.plot.ly" in text
    assert [s.number for s in report.small] == ["2"]
