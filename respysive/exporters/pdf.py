"""PDF exporter: prints the HTML presentation with headless Chromium."""

from pathlib import Path

from .base import BaseExporter
from .browser import freeze_webgl, run_in_browser


class PdfExporter(BaseExporter):
    """Export a presentation to PDF, one page per slide.

    Pages have the size of the slides and look like the slides on screen:
    same layout, same overflow fitting, vector text and charts. Requires
    Playwright and Chromium (``pip install playwright`` then
    ``python -m playwright install chromium``).

    Args:
        presentation: respysive.Presentation object to export
        fragments: One page per fragment step instead of the final state
        timeout: Seconds allowed for loading charts, equations and maps
    """

    def __init__(self, presentation, fragments: bool = False, timeout: int = 60):
        super().__init__(presentation)
        self.fragments = fragments
        self.timeout = timeout

    def export(self, **kwargs) -> bytes:
        """Render the presentation to PDF.

        Args:
            **kwargs: Presentation.to_html() options (theme, width, height, …).

        Returns:
            bytes: PDF document.
        """
        html = self.presentation.to_html(**kwargs)
        width = kwargs.get("width", 1280)
        height = kwargs.get("height", 720)

        def print_pdf(page):
            if self.fragments:
                page.evaluate("() => window.respysive.printSteps()")
                # copied map iframes reload: wait for them, then freeze them too
                page.evaluate("(ms) => window.respysive.settled(ms)", self.timeout * 1000)
                freeze_webgl(page)
            return page.pdf(print_background=True, prefer_css_page_size=True)

        return run_in_browser(html, width, height, print_pdf, timeout=self.timeout)

    def save(self, output_path: str, **kwargs):
        """Save the presentation as a PDF file.

        Args:
            output_path: Path of the PDF file.
            **kwargs: Presentation.to_html() options (theme, width, height, …).
        """
        Path(output_path).write_bytes(self.export(**kwargs))
