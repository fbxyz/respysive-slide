"""Tests for the respysive themes: slide CSS and chart colours."""

import pytest

from respysive import Presentation, Slide, palette
from respysive.themes import THEMES, theme_script

pytestmark = pytest.mark.presentation


def _html(theme):
    deck = Presentation()
    slide = Slide()
    slide.add_title("Title")
    deck.add_slide(slide)
    return deck.to_html(theme=theme)


@pytest.mark.unit
@pytest.mark.parametrize("name", list(THEMES))
def test_theme_loads_base_css_and_chart_script(name):
    html = _html(name)
    assert f"/theme/{THEMES[name]['base']}.min.css" in html
    assert f'respysive theme "{name}"' in html
    assert "window.respysiveTheme" in html
    # the theme script runs before the slides and their chart scripts
    assert html.index("window.respysiveTheme") < html.index('class="slides rs-canvas"')


@pytest.mark.unit
def test_user_css_comes_after_theme():
    deck = Presentation()
    deck.add_custom_css(".marker-for-test { color: red; }")
    deck.add_slide(Slide())
    html = deck.to_html(theme="sober")
    assert html.index('respysive theme "sober"') < html.index(".marker-for-test")


@pytest.mark.unit
def test_reveal_theme_has_no_chart_script():
    html = _html("moon")
    assert "/theme/moon.min.css" in html
    assert "window.respysiveTheme" not in html


@pytest.mark.unit
def test_palette():
    assert palette("science")[0] == "#0072b2"
    with pytest.raises(ValueError, match="Unknown respysive theme"):
        palette("dark")


@pytest.mark.slow
def test_plotly_default_colours_follow_theme():
    sync_api = pytest.importorskip("playwright.sync_api")
    with sync_api.sync_playwright() as pw:
        try:
            browser = pw.chromium.launch()
        except Exception as exc:
            pytest.skip(f"Chromium not available: {exc}")
        page = browser.new_page()
        page.set_content(f"<script>{theme_script('sober')}</script>")
        figure = page.evaluate(
            """() => respysiveTheme.plotly({
                data: [
                    {line: {color: '#636efa'}},
                    {marker: {color: ['#EF553B', '#123456']}},
                    {marker: {color: [1, 2, 3]}},
                    {line: {color: '#fecb52'}}
                ],
                layout: {template: {layout: {plot_bgcolor: '#E5ECF6', xaxis: {gridcolor: 'white'}}}}
            })"""
        )
        browser.close()
    sober = palette("sober")
    assert figure["data"][0]["line"]["color"] == sober[0]
    assert figure["data"][1]["marker"]["color"] == [sober[1], "#123456"]
    assert figure["data"][2]["marker"]["color"] == [1, 2, 3]
    # tenth default colour: beyond the 7 theme colours, kept as it is
    assert figure["data"][3]["line"]["color"] == "#fecb52"
    template = figure["layout"]["template"]["layout"]
    assert template["colorway"] == sober
    assert template["plot_bgcolor"] == "rgba(0,0,0,0)"
    assert template["xaxis"]["gridcolor"] == "#e5e7eb"
