"""Matplotlib figure handler."""

from typing import Any

from matplotlib.figure import Figure

from .base import BaseHandler


class MatplotlibHandler(BaseHandler):
    """Handler for Matplotlib Figure objects.

    Converts figures to inline SVG (or PNG) using the Content.add_fig method.

    Priority: 10.
    """

    @property
    def priority(self) -> int:
        return 10

    def can_handle(self, content: Any) -> bool:
        """Check if content is a Matplotlib Figure instance.

        Args:
            content: Content to check.

        Returns:
            bool: True if content is a matplotlib.figure.Figure.
        """
        return isinstance(content, Figure)

    def handle(self, content: Any, shared_data_id: str | None = None, forced: bool = False, **kwargs) -> str:
        """Render a Matplotlib figure as inline SVG.

        Args:
            content: Matplotlib Figure object.
            shared_data_id: Unused. Present for interface compatibility.
            forced: Whether the handler was explicitly selected.
            **kwargs: Additional styling options.

        Returns:
            str: HTML string containing the figure as inline SVG.

        Raises:
            ValueError: If content is not a Matplotlib Figure.
        """
        if not forced and not isinstance(content, Figure):
            raise ValueError("Content must be a Matplotlib Figure")

        center_style = {"class": ["d-flex", "justify-content-center", "mx-auto"]}
        combined_kwargs = {**center_style, **kwargs}

        from respysive.content import Content

        temp_content = Content()
        temp_content.add_fig(content, **combined_kwargs)

        return temp_content.content
