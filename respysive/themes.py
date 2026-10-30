"""Themes made for respysive: slide styles plus a matching chart palette.

A theme is a Reveal.js base stylesheet, a CSS file in static/themes, and a
categorical palette. Plotly and Altair charts take the palette and font of
the theme when the deck is drawn. Palettes are checked for colour-blind
separation and contrast on the theme background.
"""

import json
from pathlib import Path

_STATIC = Path(__file__).parent / "static"

THEMES = {
    "sober": {
        "base": "white",
        "palette": ["#2563eb", "#ea580c", "#059669", "#9333ea", "#db2777", "#0891b2", "#a16207"],
        "font": 'system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
        "color": "#1f2937",
    },
    "science": {
        "base": "white",
        # Okabe and Ito (2008), distinguishable with every common colour-vision deficiency
        "palette": ["#0072b2", "#e69f00", "#009e73", "#d55e00", "#cc79a7", "#56b4e9"],
        "font": '"Source Sans 3", "Source Sans Pro", system-ui, -apple-system, "Segoe UI", Arial, sans-serif',
        "color": "#222222",
    },
    "corporate": {
        "base": "white",
        "palette": ["#3a6ea5", "#e76f51", "#2a9d8f", "#8e5ea2", "#b8860b", "#d6457a"],
        "font": '"Segoe UI", "Helvetica Neue", Helvetica, Arial, sans-serif',
        "color": "#2b2f36",
    },
}


def palette(name):
    """Colours of a respysive theme, in the order charts use them.

    Useful for charts drawn in Python, such as Matplotlib figures:
    ``plt.rc("axes", prop_cycle=plt.cycler(color=palette("sober")))``.

    Args:
        name: "sober", "science", or "corporate".

    Returns:
        list[str]: Hex colours.
    """
    return list(_theme(name)["palette"])


def _theme(name):
    try:
        return THEMES[name]
    except KeyError:
        raise ValueError(f"Unknown respysive theme {name!r}. Available: {list(THEMES)}") from None


def theme_css(name):
    """CSS of a respysive theme, applied over its Reveal.js base theme."""
    _theme(name)
    return (_STATIC / "themes" / f"{name}.css").read_text(encoding="utf-8")


def theme_script(name):
    """Script defining window.respysiveTheme, run before the slides' charts."""
    theme = _theme(name)
    data = {"name": name, "palette": theme["palette"], "font": theme["font"], "color": theme["color"]}
    code = (_STATIC / "theme_charts.js").read_text(encoding="utf-8")
    return code.replace("RESPYSIVE_THEME", json.dumps(data))
