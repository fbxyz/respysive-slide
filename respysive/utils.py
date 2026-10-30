"""Utility functions for HTML generation, image encoding, and text processing."""

import base64
import re

import requests


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
        response = requests.get(image_path, headers=headers)
        response.raise_for_status()

        content_type = response.headers.get("content-type", "")
        if not content_type.startswith("image/"):
            raise ValueError(
                f"URL did not return an image. Content-Type: {content_type}. Response: {response.text[:200]}"
            )

        image_data = response.content
    else:
        with open(image_path, "rb") as f:
            image_data = f.read()

    if image_path.lower().endswith(".svg"):
        mime_type = "image/svg+xml"
    elif image_path.lower().endswith((".jpg", ".jpeg")):
        mime_type = "image/jpeg"
    elif image_path.lower().endswith(".png"):
        mime_type = "image/png"
    elif image_path.lower().endswith(".gif"):
        mime_type = "image/gif"
    elif image_path.lower().endswith(".avif"):
        mime_type = "image/avif"
    elif image_path.lower().endswith(".webp"):
        mime_type = "image/webp"
    else:
        mime_type = "image/png"

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
        response = requests.get(video_path, headers=headers)
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
            protected_formulas[placeholder] = match.group(0)
            return placeholder

        def restore_formulas(html):
            """Restore protected formulas."""
            for placeholder, formula in protected_formulas.items():
                html = html.replace(placeholder, formula)
            return html

        if not is_already_html:
            text = re.sub(r"\\\[.*?\\\]", protect_formula, text, flags=re.DOTALL)
            text = re.sub(r"\\\(.*?\\\)", protect_formula, text)

            text = re.sub(r"\$\$(.*?)\$\$", r"\\\\[\1\\\\]", text, flags=re.DOTALL)
            text = re.sub(r"\$(.*?)\$", r"\\\\(\1\\\\)", text)

            md = markdown.Markdown(extensions=["extra", "codehilite"])
            html = md.convert(text)

            html = restore_formulas(html)
            return html
        else:
            text = re.sub(r"\$\$(.*?)\$\$", r"\\[\1\\]", text, flags=re.DOTALL)
            text = re.sub(r"\$(.*?)\$", r"\\(\1\\)", text)
            return text

    except ImportError:
        text = re.sub(r"\$\$(.*?)\$\$", r"\\\\[\1\\\\]", text, flags=re.DOTALL)
        text = re.sub(r"\$(.*?)\$", r"\\\\(\1\\\\)", text)
        return text.replace("\n", "<br>")


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
