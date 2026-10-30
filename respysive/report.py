"""Check a deck before showing or exporting it: fitting, pictures, network."""

from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit

_EXTRACT_JS = (Path(__file__).parent / "static" / "pptx_extract.js").read_text(encoding="utf-8")

_SLIDES_JS = """() => window.respysive.slides().map((s) => ({
    h: +s.dataset.rsH,
    v: +s.dataset.rsV,
    stacked: !!s.parentElement.closest('section'),
    title: ((s.querySelector('h1, h2, h3, h4, h5, h6') || {}).textContent || '').trim(),
    fontScale: s.dataset.rsFit ? +s.dataset.rsFit : 1,
    zoom: s.dataset.rsZoom ? +s.dataset.rsZoom : 1,
    overflow: s.dataset.rsOverflow ? +s.dataset.rsOverflow : null
}))"""


@dataclass
class SlideReport:
    """How one slide renders.

    Attributes:
        number: Slide number as shown in the deck, "3" or "3.2" in a vertical stack.
        title: Text of the first heading, empty when the slide has none.
        scale: Size of the text relative to its normal size, after fitting
            (1 when nothing was shrunk).
        overflow: With ``overflow="warn"``, the height of the content
            relative to the slide when it does not fit, else None.
        pictures: What becomes a picture in the PowerPoint export
            ("Plotly chart", "MapLibre map", "equation", ...). Plotly charts
            simple enough are rebuilt as native charts instead.
    """

    number: str
    title: str
    scale: float = 1.0
    overflow: float | None = None
    pictures: list[str] = field(default_factory=list)


@dataclass
class DeckReport:
    """Result of :meth:`Presentation.check`.

    Attributes:
        slides: One :class:`SlideReport` per slide, in order.
        min_scale: Readability threshold used for :attr:`small`.
        network: Hosts the deck loaded resources from. Empty for a deck
            that works offline.
    """

    slides: list[SlideReport]
    min_scale: float
    network: list[str]

    @property
    def small(self) -> list[SlideReport]:
        """Slides whose text was shrunk below ``min_scale``."""
        return [s for s in self.slides if s.scale < self.min_scale]

    @property
    def overflowing(self) -> list[SlideReport]:
        """Slides whose content runs past the bottom (fitting turned off)."""
        return [s for s in self.slides if s.overflow]

    @property
    def ok(self) -> bool:
        """True when every slide fits and stays readable."""
        return not self.small and not self.overflowing

    def __str__(self):
        lines = []
        for s in self.slides:
            notes = []
            if s.scale < 1:
                flag = "  too small" if s.scale < self.min_scale else ""
                notes.append(f"text at {s.scale:.0%}{flag}")
            if s.overflow:
                notes.append(f"content {s.overflow:.0%} of the slide height")
            if s.pictures:
                counts = {}
                for what in s.pictures:
                    counts[what] = counts.get(what, 0) + 1
                notes.append("pictures: " + ", ".join(f"{n} {what}" for what, n in counts.items()))
            title = s.title if len(s.title) <= 40 else s.title[:39] + "…"
            lines.append(f"{s.number:>5}  {title:<40}  {'; '.join(notes)}".rstrip())
        lines.append("")
        lines.append(f"{len(self.small)} slide(s) below {self.min_scale:.0%}, {len(self.overflowing)} overflowing.")
        lines.append("Network: " + (", ".join(self.network) if self.network else "none, the deck works offline."))
        return "\n".join(lines)

    def _repr_pretty_(self, printer, cycle):
        printer.text(str(self))


def check(presentation, min_scale=0.7, timeout=60, **kwargs):
    """Render the deck in headless Chromium and report how each slide fits.

    Args:
        presentation: respysive.Presentation to check.
        min_scale: Text scale under which a slide is reported as too small.
        timeout: Seconds allowed for loading charts, equations and maps.
        **kwargs: Presentation.to_html() options (theme, width, height, ...).

    Returns:
        DeckReport: the fitting of each slide, its pictures in a PowerPoint
        export, and the hosts the deck depends on.
    """
    from .exporters.browser import run_in_browser

    width = kwargs.get("width", 1280)
    height = kwargs.get("height", 720)
    requests = []

    def measure(page):
        return page.evaluate(_SLIDES_JS), page.evaluate(_EXTRACT_JS)

    slides, extracted = run_in_browser(
        presentation.to_html(**kwargs), width, height, measure, timeout, requests=requests
    )
    reports = []
    for info, layout in zip(slides, extracted, strict=True):
        number = f"{info['h'] + 1}.{info['v'] + 1}" if info["stacked"] else str(info["h"] + 1)
        pictures = [item["what"] for item in layout["items"] if item.get("what") and item["what"] != "icon"]
        reports.append(
            SlideReport(
                number=number,
                title=info["title"],
                scale=round(info["fontScale"] * info["zoom"], 3),
                overflow=info["overflow"],
                pictures=pictures,
            )
        )
    hosts = sorted({urlsplit(url).hostname for url in requests if url.startswith(("http:", "https:"))})
    return DeckReport(slides=reports, min_scale=min_scale, network=hosts)
