"""JavaScript/CSS libraries: detection, local cache and offline inlining.

A presentation only loads the libraries its slides use (see ``detect_libraries``).
With ``Presentation.to_html(offline=True)`` every external script and
stylesheet of the final document is fetched once into a local cache and
written into the HTML itself, so the file opens without network access.

Iframes created with ``srcdoc`` (MapLibre maps) do not get their own copy of a
library: the code is stored once in the parent page and each iframe evaluates
it from there.
"""

import base64
import hashlib
import html
import json
import mimetypes
import os
import re
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import url2pathname

from .dependencies import CSS_URLS, JS_URLS, LOCAL_CSS_URLS, LOCAL_JS_URLS

# Library name -> URL keys in dependencies.JS_URLS / CSS_URLS. Order matters:
# a library is listed after the libraries it depends on.
LIBRARIES = {
    "bootstrap": {"css": ["bootstrap"], "js": []},
    "fontawesome": {"css": ["fontawesome"], "js": []},
    "mathjax": {"css": [], "js": ["mathjax"]},
    "plotly": {"css": [], "js": ["plotly"]},
    # Plotly bundles MapLibre for its tile maps, but not the stylesheet of the map controls
    "plotly-map": {"css": ["maplibre"], "js": []},
    "vega": {"css": [], "js": ["vega", "vega-lite", "vega-embed"]},
    "d3": {"css": [], "js": ["d3"]},
    "maplibre": {"css": ["maplibre"], "js": ["maplibre"]},
}

# Markers in the slides HTML revealing that a library is needed
_DETECTORS = {
    "fontawesome": re.compile(r"""class=["'][^"']*\bfa(?:[srbl]|-solid|-regular|-brands)?\s+fa-"""),
    "mathjax": re.compile(r"\\\(|\\\[|\$\$"),
    "plotly": re.compile(r"\bPlotly\."),
    "plotly-map": re.compile(r"""class=["'][^"']*\brs-plotly-map\b"""),
    "vega": re.compile(r"\bvegaEmbed\("),
    "d3": re.compile(r"\bd3\."),
    "maplibre": re.compile(r"\bmaplibregl\."),
}

_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36 respysive-slide"
)


class OfflineAssetError(RuntimeError):
    """Raised when an asset is neither cached nor downloadable."""


def detect_libraries(slides_html):
    """Return the names of the libraries used by the slides, in load order.

    Args:
        slides_html: HTML of all slides.

    Returns:
        list: Library names (keys of LIBRARIES).
    """
    # iframes declare their own libraries (see _Inliner.frame)
    page_html = _SRCDOC.sub('srcdoc=""', slides_html)
    found = {name for name, rx in _DETECTORS.items() if rx.search(page_html)}
    return [name for name in LIBRARIES if name in found]


def library_urls(names):
    """Return the JS and CSS URLs of libraries, honouring local overrides.

    Args:
        names: Library names, or "all".

    Returns:
        tuple: (list of (css_key, url), list of (js_key, url)).

    Raises:
        ValueError: If a name is unknown.
    """
    if names == "all":
        names = list(LIBRARIES)
    unknown = [n for n in names if n not in LIBRARIES]
    if unknown:
        raise ValueError(f"Unknown libraries {unknown}; available: {list(LIBRARIES)}")
    css, js = [], []
    for name in LIBRARIES:
        if name not in names:
            continue
        css += [(k, LOCAL_CSS_URLS.get(k, CSS_URLS[k])) for k in LIBRARIES[name]["css"] if k not in dict(css)]
        js += [(k, LOCAL_JS_URLS.get(k, JS_URLS[k])) for k in LIBRARIES[name]["js"]]
    return css, js


# ------------------------------------------------------------------- cache


def cache_dir():
    """Return the cache directory, creating it if needed.

    ``RESPYSIVE_CACHE`` overrides the platform default
    (``%LOCALAPPDATA%\\respysive\\Cache``, ``~/Library/Caches/respysive`` or
    ``$XDG_CACHE_HOME/respysive``).

    Returns:
        Path: Cache directory.
    """
    if os.environ.get("RESPYSIVE_CACHE"):
        path = Path(os.environ["RESPYSIVE_CACHE"])
    elif sys.platform == "win32":
        path = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "respysive" / "Cache"
    elif sys.platform == "darwin":
        path = Path.home() / "Library" / "Caches" / "respysive"
    else:
        path = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "respysive"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _cache_path(url):
    suffix = Path(urlparse(url).path).suffix[:10]
    return cache_dir() / (hashlib.sha256(url.encode("utf-8")).hexdigest()[:24] + suffix)


def _download(url):
    import requests

    response = requests.get(url, headers={"User-Agent": _USER_AGENT}, timeout=60)
    response.raise_for_status()
    return response.content


def _local_path(url):
    """Path of a file:// URL (drive letters and %-escapes included) or of a plain path."""
    return Path(url2pathname(urlparse(url).path)) if url.startswith("file://") else Path(url)


def fetch(url):
    """Return the content of a URL or local file, through the cache.

    Args:
        url: http(s) URL, file:// URL or local path.

    Returns:
        bytes: Content.

    Raises:
        OfflineAssetError: If a remote asset is not cached and cannot be downloaded.
    """
    if not url.startswith(("http://", "https://")):
        return _local_path(url).read_bytes()
    cached = _cache_path(url)
    if cached.exists():
        return cached.read_bytes()
    try:
        data = _download(url)
    except Exception as exc:
        raise OfflineAssetError(
            f"Cannot download {url} ({exc}). Run respysive.download_libraries() once while online, or check the URL."
        ) from exc
    cached.write_bytes(data)
    return data


def download_libraries(names="all"):
    """Pre-fill the cache so that offline exports work without network.

    Args:
        names: Library names or "all" (default).

    Returns:
        list: Downloaded or already cached URLs.
    """
    css, js = library_urls(names)
    for _, url in css:
        inline_css(url)  # also caches the fonts the stylesheet references
    for _, url in js:
        fetch(url)
    return [url for _, url in css + js]


# ---------------------------------------------------------------- inlining

_CSS_IMPORT = re.compile(r"""@import\s+(?:url\(\s*)?["']?([^"')\s]+)["']?\s*\)?\s*([^;]*);""")
_CSS_URL = re.compile(r"""url\(\s*(["']?)([^"')]+)\1\s*\)""")
_FONT_SRC = re.compile(r"src\s*:([^;}]*)")
# Font Awesome 6 re-declares its fonts under its v4/v5 family names for old
# custom CSS; inlined, each alias would embed the whole font file again.
_LEGACY_FONT_FACE = re.compile(
    r"""@font-face\s*{[^}]*font-family\s*:\s*["']?(?:FontAwesome|Font Awesome 5 [^"';}]+)["']?\s*;[^}]*}"""
)


def _data_uri(url, data):
    mime = mimetypes.guess_type(urlparse(url).path)[0] or "application/octet-stream"
    if urlparse(url).path.endswith(".woff2"):
        mime = "font/woff2"
    elif urlparse(url).path.endswith(".woff"):
        mime = "font/woff"
    return f"data:{mime};base64,{base64.b64encode(data).decode('ascii')}"


_FONT_FORMATS = ("woff2", "woff", "truetype", "ttf", "opentype", "otf")


def _best_font_source(match):
    """Keep a single source in an @font-face src list: the most compact format.

    Every browser able to run the runtime reads woff2, so embedding eot, svg or
    ttf fallbacks next to it would only make the file heavier.
    """
    sources = [s.strip() for s in re.split(r",(?![^(]*\))", match.group(1)) if s.strip()]
    for fmt in _FONT_FORMATS:
        for source in sources:
            if re.search(rf"format\(\s*['\"]?{fmt}['\"]?\s*\)|\.{fmt}\b", source):
                return "src: " + source
    if all(re.search(r"\.(eot|svg)\b|embedded-opentype|format\(\s*['\"]?svg", s) for s in sources):
        return ""  # legacy IE / iOS 4 declaration, superseded by the next src
    return match.group(0)


def inline_css(url, text=None, _seen=None):
    """Return a stylesheet with its @imports and url() resources inlined.

    Fonts and images become data URIs; @font-face rules keep only their most
    compact source, and Font Awesome's v4/v5 family aliases are dropped.

    Args:
        url: URL or path of the stylesheet, used to resolve relative references.
        text: Stylesheet content, fetched from url when None.

    Returns:
        str: Self-contained CSS.
    """
    _seen = _seen if _seen is not None else set()
    if text is None:
        text = fetch(url).decode("utf-8", errors="replace")
    _seen.add(url)

    def resolve(ref):
        if url.startswith(("http://", "https://")) or ref.startswith(("http://", "https://")):
            return urljoin(url, ref)
        base = _local_path(url).parent
        return str((base / ref).resolve())

    def replace_import(m):
        target = resolve(m.group(1))
        if target in _seen:
            return ""
        media = m.group(2).strip()
        css = inline_css(target, _seen=_seen)
        return f"@media {media} {{\n{css}\n}}" if media else css

    def replace_url(m):
        ref = m.group(2).strip()
        if ref.startswith(("data:", "#")):
            return m.group(0)
        target = resolve(ref)
        try:
            return f'url("{_data_uri(target, fetch(target))}")'
        except (OfflineAssetError, OSError):
            return m.group(0)

    text = _CSS_IMPORT.sub(replace_import, text)
    text = _LEGACY_FONT_FACE.sub("", text)
    text = _FONT_SRC.sub(_best_font_source, text)
    return _CSS_URL.sub(replace_url, text)


_PLOTLY_TOPOJSON_URL = "https://cdn.plot.ly/{}.json"
_GEO_TRACES = ("choropleth", "scattergeo")


def _as_plotly_dict(content):
    """Return a Plotly figure as a dict, or None if content is not one."""
    if hasattr(content, "to_plotly_json"):
        return json.loads(content.to_json())
    if isinstance(content, str):
        try:
            content = json.loads(content)
        except ValueError:
            return None
    if isinstance(content, dict) and isinstance(content.get("data"), list):
        return content
    return None


def plotly_geo_files(contents):
    """List the files Plotly geo charts download when they are drawn.

    Plotly fetches the base map of each geo subplot from cdn.plot.ly, named
    after its scope and resolution, and GeoJSON given as a URL.

    Args:
        contents: Slide contents (Plotly figures, dicts, JSON strings; other
            objects are ignored).

    Returns:
        tuple: ({topojson name: url}, set of GeoJSON urls).
    """
    topojson, geojson = {}, set()
    for content in contents:
        figure = _as_plotly_dict(content)
        if not figure:
            continue
        layout = figure.get("layout") or {}
        for trace in figure["data"]:
            if not isinstance(trace, dict) or trace.get("type") not in _GEO_TRACES:
                continue
            geo = layout.get(trace.get("geo", "geo")) or {}
            scope = str(geo.get("scope", "world")).replace(" ", "-")
            name = f"{scope}_{int(geo.get('resolution', 110))}m"
            topojson[name] = _PLOTLY_TOPOJSON_URL.format(name)
            if isinstance(trace.get("geojson"), str) and trace["geojson"].startswith(("http://", "https://")):
                geojson.add(trace["geojson"])
    return topojson, geojson


def plotly_geo_assets_script(contents):
    """Script preloading the files of Plotly geo charts, for offline decks.

    Plotly reads ``window.PlotlyGeoAssets`` before downloading anything.

    Args:
        contents: Slide contents, see plotly_geo_files().

    Returns:
        str: ``<script>`` element, or an empty string when no geo chart is used.
    """
    topojson, geojson = plotly_geo_files(contents)
    if not topojson and not geojson:
        return ""
    assets = {"topojson": {name: json.loads(fetch(url)) for name, url in topojson.items()}}
    assets.update({url: json.loads(fetch(url)) for url in geojson})
    payload = _script_safe(json.dumps(assets, separators=(",", ":")))
    return f"<script>window.PlotlyGeoAssets = {payload};</script>"


def _script_safe(code):
    """Escape a closing script tag inside inline script content."""
    return re.sub(r"</(script)", r"<\\/\1", code, flags=re.IGNORECASE)


_SCRIPT_SRC = re.compile(r"""<script\b[^>]*\bsrc=["']((?:https?|file)://[^"']+)["'][^>]*>\s*</script>""", re.IGNORECASE)
_STYLESHEET = re.compile(
    r"""<link\b(?=[^>]*\brel=["']?stylesheet)[^>]*\bhref=["']((?:https?|file)://[^"']+)["'][^>]*>""", re.IGNORECASE
)
_SRCDOC = re.compile(r'srcdoc="([^"]*)"')

# Where offline exports put the libraries shared with iframes (start of <body>)
ASSETS_MARKER = "<!-- respysive:assets -->"


class _Inliner:
    """Rewrite a document so that it needs no external script or stylesheet.

    Each resource is embedded once: in the page where the page uses it, and as
    a ``text/plain`` block when only iframes do. Iframes read it from there.
    """

    def __init__(self):
        self.assets = {}  # url -> [element id, content, embedded in the page]

    def _asset(self, url, kind):
        if url not in self.assets:
            if kind == "js":
                content = fetch(url).decode("utf-8", errors="replace")
            else:
                content = inline_css(url)
            self.assets[url] = [f"rs-asset-{len(self.assets)}", _script_safe(content), False]
        return self.assets[url]

    def _page_tag(self, url, kind):
        asset = self._asset(url, kind)
        if asset[2]:
            return ""  # already in the page: browsers would run it twice
        asset[2] = True
        tag = "script" if kind == "js" else "style"
        return f'<{tag} id="{asset[0]}">\n{asset[1]}\n</{tag}>'

    def _frame_tag(self, url, kind):
        aid = self._asset(url, kind)[0]
        if kind == "js":
            return f"<script>(0, eval)(parent.document.getElementById('{aid}').textContent);</script>"
        return (
            "<style></style><script>document.currentScript.previousElementSibling.textContent = "
            f"parent.document.getElementById('{aid}').textContent;</script>"
        )

    def document(self, doc):
        # iframes first: inlined library code may itself contain 'srcdoc="'
        page_urls = set(_SCRIPT_SRC.findall(doc)) | set(_STYLESHEET.findall(doc))
        doc = _SRCDOC.sub(lambda m: f'srcdoc="{html.escape(self.frame(html.unescape(m.group(1))), quote=True)}"', doc)
        doc = _SCRIPT_SRC.sub(lambda m: self._page_tag(m.group(1), "js"), doc)
        doc = _STYLESHEET.sub(lambda m: self._page_tag(m.group(1), "css"), doc)
        blobs = "\n".join(
            f'<script type="text/plain" id="{aid}">{content}</script>'
            for url, (aid, content, _) in self.assets.items()
            if url not in page_urls
        )
        if not blobs:
            return doc
        # iframes run while the page is still parsed: the blobs must come
        # before them, at the ASSETS_MARKER placed by the page template
        if ASSETS_MARKER in doc:
            return doc.replace(ASSETS_MARKER, blobs, 1)
        end = doc.rfind("</body>")  # inlined libraries may contain "</body>"
        return doc[:end] + blobs + "\n" + doc[end:]

    def frame(self, doc):
        doc = _SCRIPT_SRC.sub(lambda m: self._frame_tag(m.group(1), "js"), doc)
        return _STYLESHEET.sub(lambda m: self._frame_tag(m.group(1), "css"), doc)


def inline_external_resources(doc):
    """Embed every external script and stylesheet of an HTML document.

    Args:
        doc: Complete HTML document.

    Returns:
        str: Document that loads no script or stylesheet from the network.

    Raises:
        OfflineAssetError: If a resource is neither cached nor downloadable.
    """
    return _Inliner().document(doc)
