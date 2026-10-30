"""LaTeX and Markdown content handler."""

from typing import Any

from .base import BaseHandler


class LatexHandler(BaseHandler):
    """Handler for text containing LaTeX math expressions or Markdown syntax.

    Detects content with ``$``, ``$$``, ``#``, ``*``, ``_``, or ``[``
    markers and processes them through the Markdown/LaTeX pipeline.
    Already-processed content (with MathJax delimiters) is skipped.

    Priority: 50.
    """

    @property
    def priority(self) -> int:
        return 50

    def can_handle(self, content: Any) -> bool:
        """Check if content contains LaTeX or Markdown markers.

        Args:
            content: Content to check.

        Returns:
            bool: True if content is a string with unprocessed LaTeX/Markdown markers.
        """
        if not isinstance(content, str):
            return False

        return ("$" in content or "#" in content or "*" in content or "_" in content or "[" in content) and not (
            "\\(" in content or "\\[" in content
        )

    def handle(self, content: Any, shared_data_id: str | None = None, forced: bool = False, **kwargs) -> str:
        """Process LaTeX/Markdown content into HTML with MathJax support.

        Args:
            content: String containing LaTeX or Markdown markup.
            shared_data_id: Unused. Present for interface compatibility.
            forced: Whether the handler was explicitly selected.
            **kwargs: Additional styling options.

        Returns:
            str: HTML string with MathJax-compatible math delimiters.

        Raises:
            ValueError: If content is not a string.
        """
        if not isinstance(content, str):
            raise ValueError("Content must be a string")

        from respysive.utils import process_markdown_with_latex

        processed_text = process_markdown_with_latex(content)

        from respysive.content import Content

        temp_content = Content()
        temp_content.add_div(processed_text)

        return temp_content.content
