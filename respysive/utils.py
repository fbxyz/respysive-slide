"""Utility functions for HTML generation, image encoding, and text processing."""

import base64
import re
from html import escape
from urllib.parse import urlparse

import requests

_REQUEST_TIMEOUT = 60  # seconds, for images and videos given as URLs

_IMAGE_MIME_TYPES = {
    ".svg": "image/svg+xml",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".apng": "image/apng",
    ".gif": "image/gif",
    ".avif": "image/avif",
    ".webp": "image/webp",
    ".bmp": "image/bmp",
    ".tif": "image/tiff",
    ".tiff": "image/tiff",
}


def _script_json(text: str) -> str:
    """Make JSON safe inside a ``<script>`` element.

    ``</script>`` or ``<!--`` in a string would end or corrupt the script.
    ``<`` only occurs inside JSON strings, where its unicode escape means the same.
    """
    return text.replace("</", "\\u003c/").replace("<!--", "\\u003c!--")


def encode_image_to_data_uri(image_path: str) -> str:
    """Encode an image file or URL to a base64 data URI.

    Args:
        image_path: Path to local image file, URL, or a data URI (returned as is)

    Returns:
        str: Data URI string (e.g., 'data:image/png;base64,...')
    """
    if image_path.startswith("data:"):
        return image_path
    if image_path.startswith(("http://", "https://")):
        headers = {"User-Agent": "respysive-slide/1.0 (Python; https://github.com/fbxyz/respysive-slide)"}
        response = requests.get(image_path, headers=headers, timeout=_REQUEST_TIMEOUT)
        response.raise_for_status()

        content_type = response.headers.get("content-type", "")
        if not content_type.startswith("image/"):
            raise ValueError(
                f"URL did not return an image. Content-Type: {content_type}. Response: {response.text[:200]}"
            )

        image_data = response.content
        # the extension of the path, without the query string; else what the server says
        path = urlparse(image_path).path.lower()
        suffix = "." + path.rsplit(".", 1)[-1] if "." in path else ""
        mime_type = _IMAGE_MIME_TYPES.get(suffix) or content_type.split(";")[0].strip()
    else:
        with open(image_path, "rb") as f:
            image_data = f.read()
        suffix = "." + image_path.lower().rsplit(".", 1)[-1] if "." in image_path else ""
        mime_type = _IMAGE_MIME_TYPES.get(suffix, "image/png")

    image_base64 = base64.b64encode(image_data).decode("utf-8")
    return f"data:{mime_type};base64,{image_base64}"


def encode_video_to_data_uri(video_path: str) -> str:
    """Encode a video file or URL to a base64 data URI.

    Mirror of :func:`encode_image_to_data_uri` for video content.

    Note:
        Base64 encoding inflates the binary size by roughly 33%. For large
        videos this can make the generated HTML very heavy; prefer short clips.

    Args:
        video_path: Path to local video file or URL

    Returns:
        str: Data URI string (e.g., 'data:video/mp4;base64,...')
    """
    if video_path.startswith(("http://", "https://")):
        headers = {"User-Agent": "respysive-slide/1.0 (Python; https://github.com/fbxyz/respysive-slide)"}
        response = requests.get(video_path, headers=headers, timeout=_REQUEST_TIMEOUT)
        response.raise_for_status()
        video_data = response.content
    else:
        with open(video_path, "rb") as f:
            video_data = f.read()

    mime_type = _video_mime_type(video_path)

    video_base64 = base64.b64encode(video_data).decode("utf-8")
    return f"data:{mime_type};base64,{video_base64}"


def _video_mime_type(video_path: str) -> str:
    """Return the MIME type for a video file based on its extension.

    Args:
        video_path: Path or URL to the video file

    Returns:
        str: MIME type (defaults to 'video/mp4' for unknown extensions)
    """
    path = video_path.lower()
    if path.endswith(".mp4") or path.endswith(".m4v"):
        return "video/mp4"
    elif path.endswith(".webm"):
        return "video/webm"
    elif path.endswith((".ogg", ".ogv")):
        return "video/ogg"
    elif path.endswith(".mov"):
        return "video/quicktime"
    else:
        return "video/mp4"


def _parse_style_class(style: dict):
    """Parse style dictionary into HTML style and class attributes.

    Args:
        style: Dictionary containing CSS properties and class names. None values
            are skipped. A ``style`` key holds raw CSS declarations.

    Returns:
        str: HTML attribute string for style and class
    """
    if style:
        style_str = ""
        class_str = ""
        for key, value in style.items():
            if value is None:
                continue
            if key == "style":
                style_str += str(value).strip().rstrip(";") + ";"
            elif key == "class":
                if isinstance(value, str):
                    class_str = f"class='{value}'"
                elif isinstance(value, list):
                    class_str = f"class='{' '.join(value)}'"
                else:
                    raise ValueError("Invalid class, the class must be a string or a list of strings")
            else:
                if isinstance(value, (str, int, float)):
                    css_key = key.replace("_", "-")
                    style_str += f"{css_key}: {value};"
                else:
                    raise ValueError(f"Invalid value for {key}, the value must be a string, int or float")

        result_parts = []
        if style_str:
            # values such as font-family: 'Open Sans' must not close the attribute
            style_str = style_str.replace("'", "&#39;")
            result_parts.append(f"style='{style_str}'")
        if class_str:
            result_parts.append(class_str)
        return " ".join(result_parts)
    return ""


def add_list_classes(text: str, text_size: str = "85%") -> str:
    """Convert HTML lists to Bootstrap list-group format.

    Args:
        text: Text containing HTML list elements
        text_size: CSS font-size value

    Returns:
        str: Text with Bootstrap list-group classes applied
    """
    text = re.sub(
        r"<ul(?:\s[^>]*)?>", f'<ul class="list-group list-group-flush" style="font-size: {text_size};">', text
    )
    text = re.sub(
        r"<ol(?:\s[^>]*)?>", f'<ol class="list-group list-group-flush" style="font-size: {text_size};">', text
    )
    text = re.sub(
        r"<li(?:\s[^>]*)?>",
        f'<li class="list-group-item" style="font-size: {text_size}; background: transparent; padding-left: 0; padding-right: 0;">',
        text,
    )
    return text


# $…$ is a formula when the first $ is followed by a character, and the last
# one follows a character and precedes no digit (the rule of pandoc). So
# "from $5 to $10" stays text, as does an escaped \\$.
_DISPLAY_MATH = re.compile(r"(?<!\\)\$\$(.*?)(?<!\\)\$\$", re.DOTALL)
_INLINE_MATH = re.compile(r"(?<![\\$])\$(?![\s$])((?:\\.|[^$\\\n])*?)(?<![\s\\])\$(?!\d)")


def _dollars_to_mathjax(text: str) -> str:
    """Rewrite ``$$…$$`` as ``\\[…\\]`` and ``$…$`` as ``\\(…\\)``."""
    text = _DISPLAY_MATH.sub(lambda m: f"\\[{m.group(1)}\\]", text)
    return _INLINE_MATH.sub(lambda m: f"\\({m.group(1)}\\)", text)


def process_markdown_with_latex(text: str) -> str:
    """Process markdown text with LaTeX math support.

    Converts $...$ to inline math and $$...$$ to display math.

    Args:
        text: Input text containing markdown and LaTeX expressions

    Returns:
        str: Processed HTML with LaTeX converted to MathJax format
    """
    try:
        import uuid

        import markdown

        is_already_html = bool(re.search(r"<[^>]+>", text))

        protected_formulas = {}

        def protect_formula(match):
            """Replace formula with unique placeholder."""
            placeholder = f"MATH_{uuid.uuid4().hex}_MATH"
            protected_formulas[placeholder] = escape(match.group(0), quote=False)
            return placeholder

        def restore_formulas(html):
            """Restore protected formulas."""
            for placeholder, formula in protected_formulas.items():
                html = html.replace(placeholder, formula)
            return html

        if not is_already_html:
            # formulas are set aside: Markdown would read their * and _ as
            # emphasis and drop the backslash of \\ or \{
            text = _dollars_to_mathjax(text)
            text = re.sub(r"\\\[.*?\\\]", protect_formula, text, flags=re.DOTALL)
            text = re.sub(r"\\\(.*?\\\)", protect_formula, text)
            text = text.replace("\\$", "$")  # an escaped dollar is a dollar

            md = markdown.Markdown(extensions=["extra", "codehilite"])
            html = md.convert(text)

            html = restore_formulas(html)
            return html
        else:
            return _dollars_to_mathjax(text)

    except ImportError:
        return _dollars_to_mathjax(text).replace("\n", "<br>")


def _fragment_class(spec, index=None):
    """Return the CSS classes making an element a fragment.

    Args:
        spec: None/False (no fragment), True ('fragment'), a style string such as
            'fade-up' or 'highlight-red', or a list of those (one per item).
        index: Item index when spec is a list.

    Returns:
        str: Class string, empty when the item is not a fragment.
    """
    if isinstance(spec, (list, tuple)):
        spec = spec[index] if index is not None and index < len(spec) else None
    if not spec:
        return ""
    if spec is True:
        return "fragment"
    return f"fragment {spec}"


_SVG_TAG = re.compile(r"<svg\b|</svg>", re.IGNORECASE)
_SVG_ID = re.compile(r"""(\sid=)(["'])([^"']+)\2""")


def _dedupe_svg_ids(html: str) -> str:
    """Rename the ids an inline SVG repeats from an earlier SVG of the document.

    Charts and maps often reuse the same ids (``clip-main``, glyph names…), and
    ``url(#id)`` / ``href="#id"`` resolve to the first element of the document
    carrying the id. When that element sits on a hidden slide, a clip path clips
    everything away. Each repeated id is suffixed, along with its references
    inside the same SVG.

    Args:
        html: HTML containing inline ``<svg>`` elements.

    Returns:
        str: HTML in which no two top-level SVGs share an id.
    """
    seen = set()
    out = []
    pos = depth = 0
    start = None
    for match in _SVG_TAG.finditer(html):
        if match.group(0)[1] != "/":
            if depth == 0:
                start = match.start()
            depth += 1
            continue
        if depth == 0:
            continue
        depth -= 1
        if depth:
            continue
        end = match.end()
        block = html[start:end]
        ids = {m.group(3) for m in _SVG_ID.finditer(block)}
        renamed = {i: f"{i}--{len(seen)}" for i in ids & seen}
        seen |= ids
        if renamed:
            block = _rename_svg_ids(block, renamed)
        out.append(html[pos:start])
        out.append(block)
        pos = end
    out.append(html[pos:])
    return "".join(out)


def _rename_svg_ids(block: str, renamed: dict) -> str:
    """Rename ids and their ``url(#…)`` / ``href="#…"`` references in an SVG."""
    block = _SVG_ID.sub(lambda m: f"{m.group(1)}{m.group(2)}{renamed.get(m.group(3), m.group(3))}{m.group(2)}", block)
    names = "|".join(map(re.escape, renamed))
    pattern = re.compile(rf"""(url\(\s*["']?#|href=["']#)({names})(?=["')])""")
    return pattern.sub(lambda m: m.group(1) + renamed[m.group(2)], block)
