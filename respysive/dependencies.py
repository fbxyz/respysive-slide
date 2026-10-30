"""CDN dependency URLs and version management for external libraries.

Defines version constants and URL mappings for Bootstrap, Plotly, D3,
Font Awesome, Reveal.js themes and other libraries loaded via CDN. Provides functions
to override URLs with local paths.
"""

REVEAL_VERSION = "4.4.0"  # only Reveal.js theme stylesheets are used
BOOTSTRAP_VERSION = "4.5.2"
FONTAWESOME_VERSION = "6.2.1"
PLOTLY_VERSION = "3.0.1"
MAPLIBRE_VERSION = "3.6.2"

CSS_URLS = {
    "bootstrap": f"https://stackpath.bootstrapcdn.com/bootstrap/{BOOTSTRAP_VERSION}/css/bootstrap.min.css",
    "fontawesome": f"https://cdnjs.cloudflare.com/ajax/libs/font-awesome/{FONTAWESOME_VERSION}/css/all.min.css",
    "maplibre": f"https://unpkg.com/maplibre-gl@{MAPLIBRE_VERSION}/dist/maplibre-gl.css",
}

JS_URLS = {
    "vega": "https://cdn.jsdelivr.net/npm/vega@6",
    "vega-lite": "https://cdn.jsdelivr.net/npm/vega-lite@6",
    "vega-embed": "https://cdn.jsdelivr.net/npm/vega-embed@7",
    "plotly": f"https://cdn.plot.ly/plotly-{PLOTLY_VERSION}.min.js",
    "d3": "https://cdn.jsdelivr.net/npm/d3@7",
    # SVG output with all TeX extensions bundled: no font or extension is
    # fetched at runtime, so equations also render offline
    "mathjax": "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg-full.js",
    "maplibre": f"https://unpkg.com/maplibre-gl@{MAPLIBRE_VERSION}/dist/maplibre-gl.js",
}

LOCAL_JS_URLS = {}
LOCAL_CSS_URLS = {}


def get_theme_url(theme):
    """Return the CDN URL for a Reveal.js theme.

    Args:
        theme: Theme name (e.g. 'moon', 'white', 'black').

    Returns:
        str: Full CDN URL to the theme CSS file.
    """
    return f"https://cdnjs.cloudflare.com/ajax/libs/reveal.js/{REVEAL_VERSION}/theme/{theme}.min.css"


def set_local_js_urls(urls):
    """Override default CDN JavaScript URLs with local paths.

    Args:
        urls: Dictionary mapping library keys to local file paths.
            Valid keys: 'plotly', 'd3', 'mathjax', 'vega',
            'vega-lite', 'vega-embed', 'maplibre'.

    Example::

        set_local_js_urls({'plotly': '/static/plotly.min.js'})
    """
    global LOCAL_JS_URLS
    LOCAL_JS_URLS.update(urls)


def set_local_css_urls(urls):
    """Override default CDN CSS URLs with local paths.

    Args:
        urls: Dictionary mapping library keys to local file paths.
            Valid keys: 'theme', 'bootstrap', 'fontawesome', 'maplibre'.

    Example::

        set_local_css_urls({'fontawesome': '/static/fontawesome.min.css'})
    """
    global LOCAL_CSS_URLS
    LOCAL_CSS_URLS.update(urls)
