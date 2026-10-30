"""Text content handler (fallback for unrecognized content types)."""

from typing import Any

from .base import BaseHandler


class TextHandler(BaseHandler):
    """Fallback handler for plain text and pre-processed HTML content.

    Handles any content that no other handler matched. Detects whether
    the input already contains HTML or LaTeX markup and renders accordingly.

    Priority: 100 (lowest — acts as fallback).
    """

    @property
    def priority(self) -> int:
        return 100

    def can_handle(self, content: Any) -> bool:
        """Return True for any content (fallback).

        Args:
            content: Any content object.

        Returns:
            bool: Always True.
        """
        return True

    def handle(self, content: Any, shared_data_id: str | None = None, forced: bool = False, **kwargs) -> str:
        """Render content as text or HTML div.

        If the content contains HTML tags or LaTeX delimiters, it is
        wrapped in a div. Otherwise it is rendered as a paragraph.

        Args:
            content: Content to render.
            shared_data_id: Unused. Present for interface compatibility.
            forced: Whether the handler was explicitly selected.
            **kwargs: Additional styling options.

        Returns:
            str: HTML string.
        """
        content_str = str(content)

        from respysive.content import Content

        temp_content = Content()

        if "\\(" in content_str or "\\[" in content_str or "<" in content_str:
            temp_content.add_div(content_str)
        else:
            temp_content.add_text(content_str)

        return temp_content.content
