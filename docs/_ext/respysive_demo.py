"""Live respysive decks in the documentation.

``respysive-demo`` is a directive that runs the Python code it contains and
shows that code above the deck it saves, playable in the page. The gallery
scraper does the same for sphinx-gallery examples and also captures each
slide for the thumbnails.

Example scripts end with ``deck.save_html(...)`` as real scripts do. While
the documentation builds, that call records its options instead of writing
a file, and the deck is rendered with them.

Each deck is written to ``_decks/`` and the page loads it with ``src``. An
``srcdoc`` iframe would keep the page self-contained, but Plotly tile maps
never finish loading in one.
"""

import contextlib
import hashlib
import os
import tempfile
from pathlib import Path

from docutils import nodes
from docutils.parsers.rst import Directive, directives

EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "examples"
DECKS = {}  # file name in _decks/: deck HTML, written when the build ends


def record_save_options():
    """Make save calls record their options instead of writing files."""
    from respysive import Presentation

    def save_html(self, file_name, **kwargs):
        self._doc_options = kwargs

    def save_export(self, file_name, *args, **kwargs):
        pass

    Presentation.save_html = save_html
    Presentation.save_pdf = save_export
    Presentation.save_pptx = save_export


def saved_decks(namespace, seen):
    """Presentations of a namespace that were saved and not shown yet."""
    from respysive import Presentation

    for obj in list(namespace.values()):
        if isinstance(obj, Presentation) and hasattr(obj, "_doc_options") and id(obj) not in seen:
            seen.add(id(obj))
            yield obj


def deck_html(deck):
    return deck.to_html(**deck._doc_options)


def iframe_html(document, docname):
    """The deck in an iframe, on one line so that it fits in a raw block."""
    name = hashlib.sha1(document.encode("utf-8")).hexdigest()[:16] + ".html"
    DECKS[name] = document
    src = "../" * docname.count("/") + "_decks/" + name
    return (
        '<div class="rs-demo">'
        f'<iframe src="{src}" allowfullscreen loading="lazy" title="Live presentation"></iframe>'
        '<div class="rs-demo-bar"><span>Click the slide, then use the arrow keys.</span>'
        '<button type="button" onclick="this.parentNode.previousElementSibling.requestFullscreen()">'
        "Full screen</button></div></div>"
    )


@contextlib.contextmanager
def working_directory(path):
    previous = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def screenshot_slides(document, png_paths):
    """Save one screenshot per slide at 1280 x 720, with every fragment shown."""
    from playwright.sync_api import sync_playwright

    with tempfile.TemporaryDirectory() as tmp:
        page_file = Path(tmp) / "deck.html"
        page_file.write_text(document, encoding="utf-8")
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            page = browser.new_page(viewport={"width": 1280, "height": 720})
            page.goto(page_file.as_uri(), wait_until="load")
            page.add_style_tag(content="*, *::before, *::after { transition: none !important; }")
            page.evaluate("respysive.settled(20000)")
            # A slide change sent as soon as the deck settles can leave the slides
            # mid-way when a map iframe is still starting
            page.wait_for_timeout(1500)
            slides = page.evaluate("respysive.slides().map(s => [+s.dataset.rsH, +s.dataset.rsV])")
            for (h, v), png in zip(slides, png_paths, strict=False):
                page.evaluate(f"respysive.go({h}, {v}, 'last')")
                page.wait_for_function(
                    "(() => { const r = document.querySelector('section.rs-slide.present').getBoundingClientRect();"
                    " return r.left >= 0 && r.right <= innerWidth; })()",
                    timeout=10000,
                )
                page.wait_for_timeout(1500)
                page.screenshot(path=png)
            browser.close()


def _count_slides(slides):
    return sum(_count_slides(s) if isinstance(s, list) else 1 for s in slides)


def gallery_scraper(block, block_vars, gallery_conf):
    """sphinx-gallery scraper: embed each deck saved in a code block."""
    image_path_iterator = block_vars["image_path_iterator"]
    seen = block_vars.setdefault("_respysive_seen_ids", set())
    parts = []
    for deck in saved_decks(block_vars["example_globals"], seen):
        document = deck_html(deck)
        pngs = [next(image_path_iterator) for _ in range(_count_slides(deck.slides))]
        screenshot_slides(document, pngs)
        target = Path(block_vars["target_file"])  # the example copied into the gallery directory
        docname = f"{target.parent.name}/{target.stem}"
        parts.append(".. raw:: html\n\n   " + iframe_html(document, docname) + "\n")
    return "\n".join(parts)


class RespysiveDemo(Directive):
    """Run the code, show it, and embed the deck it saves.

    The code is complete: it runs alone, from the examples directory, so
    that ``data/...`` paths resolve. The ``file`` option runs a script of
    that directory instead of the directive content. The ``hide-code``
    option shows only the deck.
    """

    has_content = True
    option_spec = {"hide-code": directives.flag, "file": directives.unchanged_required}

    def run(self):
        if "file" in self.options:
            path = EXAMPLES_DIR / self.options["file"]
            self.state.document.settings.record_dependencies.add(str(path))
            code, source = path.read_text(encoding="utf-8"), str(path)
        else:
            code = "\n".join(self.content)
            source = f"{self.state.document.current_source}:{self.lineno}"
        namespace = {"__name__": "__respysive_demo__"}
        with working_directory(EXAMPLES_DIR):
            try:
                exec(compile(code, source, "exec"), namespace)
            except Exception as exc:
                raise self.error(f"respysive-demo failed: {exc!r}") from exc
        result = []
        if "hide-code" not in self.options:
            block = nodes.literal_block(code, code)
            block["language"] = "python"
            result.append(block)
        for deck in saved_decks(namespace, set()):
            docname = self.state.document.settings.env.docname
            result.append(nodes.raw("", iframe_html(deck_html(deck), docname), format="html"))
        if len(result) == (0 if "hide-code" in self.options else 1):
            raise self.error("respysive-demo: the code does not call save_html()")
        return result


def write_decks(app, exception):
    """Write the decks of the pages, and the showcase as a page of its own."""
    if exception is not None or app.builder.format != "html":
        return
    decks_dir = Path(app.outdir, "_decks")
    decks_dir.mkdir(exist_ok=True)
    for name, document in DECKS.items():
        (decks_dir / name).write_text(document, encoding="utf-8")
    path = EXAMPLES_DIR / "showcase.py"
    namespace = {"__name__": "__respysive_demo__"}
    with working_directory(EXAMPLES_DIR):
        exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), namespace)
    for deck in saved_decks(namespace, set()):
        Path(app.outdir, "showcase.html").write_text(deck_html(deck), encoding="utf-8")


def setup(app):
    record_save_options()
    app.add_directive("respysive-demo", RespysiveDemo)
    app.connect("build-finished", write_decks)
    return {"parallel_read_safe": False, "parallel_write_safe": True}
