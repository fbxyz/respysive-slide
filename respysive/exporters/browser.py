"""Render a presentation in headless Chromium (Playwright) for static exports."""

import asyncio
import base64
import concurrent.futures
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path

_INSTALL_HINT = "pip install playwright && python -m playwright install chromium"


def run_in_browser(html, width, height, action, timeout=60, requests=None):
    """Open a presentation in headless Chromium and run ``action(page)``.

    The deck is loaded in print mode and ``action`` runs once everything is
    drawn (charts, equations, maps) and WebGL canvases are frozen as images. Relative paths in the HTML resolve
    against the current directory, as when the HTML file is saved there.

    Works from scripts and from Jupyter: Playwright's sync API cannot run
    inside an asyncio loop, so the work then moves to a separate thread.

    Args:
        html: Complete HTML document from Presentation.to_html().
        width: Slide width in pixels.
        height: Slide height in pixels.
        action: Function receiving the Playwright page; its result is returned.
        timeout: Seconds allowed for loading and drawing.
        requests: Optional list, filled with the URL of every request.

    Returns:
        The value returned by action.

    Raises:
        ImportError: If Playwright is not installed.
        RuntimeError: If Chromium is not installed.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return _render(html, width, height, action, timeout, requests)
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(_render, html, width, height, action, timeout, requests).result()


_ISOLATE_JS = """(element, children) => {
    const style = element.ownerDocument.createElement('style');
    style.id = 'rs-capture-style';
    style.textContent = '* { visibility: hidden !important; } .rs-capture' +
        (children ? ', .rs-capture *' : '') + ' { visibility: visible !important; }';
    element.ownerDocument.head.appendChild(style);
    element.classList.add('rs-capture');
}"""

_RESTORE_JS = """element => {
    element.classList.remove('rs-capture');
    element.ownerDocument.getElementById('rs-capture-style').remove();
}"""


@contextmanager
def isolate(element, children=True):
    """Hide everything in the element's document but the element itself.

    Screenshots of a region show whatever is painted there; isolating keeps
    overlapping content (legends, text, other slides) out of the capture.

    Args:
        element: Playwright element handle.
        children: Keep the element's descendants visible.
    """
    element.evaluate(_ISOLATE_JS, children)
    try:
        yield
    finally:
        element.evaluate(_RESTORE_JS)


def freeze_webgl(page):
    """Replace WebGL canvases (maps, 3D charts) by screenshots of themselves.

    Chromium prints WebGL canvases blank unless they were created with
    preserveDrawingBuffer, which neither MapLibre nor Plotly do. A canvas is
    WebGL when it refuses a 2D context.

    Args:
        page: Playwright page, deck in print mode.

    Returns:
        int: Number of canvases replaced.
    """
    count = 0
    for frame in page.frames:
        for canvas in frame.query_selector_all("canvas"):
            if not canvas.evaluate("c => c.getContext('2d') === null && c.width > 0 && c.height > 0"):
                continue
            # capture the canvas alone: overlays (legends, attributions) stay live
            with isolate(canvas, children=False):
                png = base64.b64encode(canvas.screenshot(omit_background=True)).decode("ascii")
            canvas.evaluate(
                """(c, src) => {
                    const img = document.createElement('img');
                    img.src = src;
                    img.className = c.className;
                    img.style.cssText = c.style.cssText;
                    img.style.width = c.clientWidth + 'px';
                    img.style.height = c.clientHeight + 'px';
                    c.replaceWith(img);
                }""",
                f"data:image/png;base64,{png}",
            )
            count += 1
    return count


def _track_requests(page, seen=None):
    """Return the live set of requests in flight on the page and its frames."""
    pending = set()

    def start(request):
        pending.add(request)
        if seen is not None:
            seen.append(request.url)

    page.on("request", start)
    page.on("requestfinished", lambda request: pending.discard(request))
    page.on("requestfailed", lambda request: pending.discard(request))
    return pending


def _wait_network_quiet(page, pending, timeout, quiet=0.5):
    """Wait until no request has been in flight for ``quiet`` seconds.

    Playwright's own "networkidle" state never comes on pages holding srcdoc
    iframes. Gives up silently after ``timeout`` seconds (e.g. streaming).
    """
    deadline = time.monotonic() + timeout
    calm_since = time.monotonic()
    while time.monotonic() < deadline:
        page.wait_for_timeout(100)
        if pending:
            calm_since = time.monotonic()
        elif time.monotonic() - calm_since >= quiet:
            return


def _render(html, width, height, action, timeout, requests=None):
    try:
        from playwright.sync_api import Error as PlaywrightError
        from playwright.sync_api import sync_playwright
    except ImportError as err:
        raise ImportError(f"Static exports need Playwright: {_INSTALL_HINT}") from err

    base = f'<base href="{Path.cwd().as_uri()}/">'
    html = html.replace("<head>", f"<head>\n{base}", 1)

    with tempfile.TemporaryDirectory() as tmp, sync_playwright() as pw:
        deck = Path(tmp) / "deck.html"
        deck.write_text(html, encoding="utf-8")
        try:
            browser = pw.chromium.launch()
        except PlaywrightError as err:
            raise RuntimeError(f"Chromium is not available for Playwright: {_INSTALL_HINT}") from err
        try:
            # scale 2: sharp screenshots of WebGL canvases (text stays vector)
            page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=2)
            page.set_default_timeout(timeout * 1000)
            pending = _track_requests(page, requests)
            page.goto(f"{deck.as_uri()}?print-pdf", wait_until="load")
            page.wait_for_function("() => window.respysive")
            _wait_network_quiet(page, pending, timeout)
            page.evaluate("(ms) => window.respysive.settled(ms)", timeout * 1000)
            freeze_webgl(page)
            return action(page)
        finally:
            browser.close()
