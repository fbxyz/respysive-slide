"""Handler for objects implementing the _repr_html_ protocol (Jupyter-compatible)."""

from typing import Any

from .base import BaseHandler


class HtmlReprHandler(BaseHandler):
    """Handler for objects with a _repr_html_() method.

    Detects any object following the Jupyter _repr_html_ protocol
    (e.g. mappyng InteractiveMap, IPython.display.HTML, etc.)
    and embeds the returned HTML directly.

    Priority: 8 (before MatplotlibHandler to catch InteractiveMap
    before it falls through to the matplotlib Figure check).
    """

    @property
    def priority(self) -> int:
        return 8

    def can_handle(self, content: Any) -> bool:
        """Check if content has a _repr_html_ method.

        Excludes standard types already handled by other handlers
        (plotly Figure, altair Chart, etc.) to avoid conflicts.
        """
        if not hasattr(content, "_repr_html_") or not callable(content._repr_html_):
            return False

        # Exclude types that have their own dedicated handlers
        excluded_modules = ("plotly", "altair", "vegalite", "matplotlib")
        module = type(content).__module__ or ""
        if any(m in module for m in excluded_modules):
            return False

        return True

    def handle(self, content: Any, shared_data_id: str | None = None, forced: bool = False, **kwargs) -> str:
        """Render by calling _repr_html_() and wrapping in a responsive div.

        Args:
            content: Object with _repr_html_() method.
            shared_data_id: Unused. Present for interface compatibility.
            forced: Whether the handler was explicitly selected.
            **kwargs: Additional styling options.

        Returns:
            str: HTML string.
        """
        from respysive.utils import _parse_style_class

        if "class" not in kwargs:
            kwargs["class"] = []
        elif isinstance(kwargs["class"], str):
            kwargs["class"] = [kwargs["class"]]
        kwargs["class"].extend(["d-flex", "justify-content-center"])

        s = _parse_style_class(kwargs)
        html = content._repr_html_()

        return f"<div {s}>{html}</div>"
