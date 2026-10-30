"""Altair / Vega-Lite chart handler."""

import json
from typing import Any

from .base import BaseHandler


def _is_altair_chart(content: Any) -> bool:
    """Tell an Altair chart object by its module, without importing altair."""
    module = type(content).__module__ or ""
    return module.startswith("altair.") and callable(getattr(content, "to_json", None))


class AltairHandler(BaseHandler):
    """Handler for Altair and Vega-Lite chart specifications.

    Detects content containing a Vega-Lite schema URL and renders
    it using the vega-embed library.

    Priority: 30.
    """

    @property
    def priority(self) -> int:
        return 30

    def can_handle(self, content: Any) -> bool:
        """Check if content is a Vega-Lite specification.

        Looks for the Vega-Lite schema URL in the content string or dict, and
        accepts Altair chart objects (``alt.Chart``, layered, concatenated…).

        Args:
            content: Content to check.

        Returns:
            bool: True if content contains a Vega-Lite ``$schema`` reference.
        """
        if _is_altair_chart(content):
            return True
        if isinstance(content, str):
            return "https://vega.github.io/schema/vega-lite" in content
        elif isinstance(content, dict):
            content_str = json.dumps(content)
            return "https://vega.github.io/schema/vega-lite" in content_str
        return False

    def handle(self, content: Any, shared_data_id: str | None = None, forced: bool = False, **kwargs) -> str:
        """Render a Vega-Lite chart using vega-embed.

        Args:
            content: Altair chart, Vega-Lite JSON string or dict.
            shared_data_id: Unused. Present for interface compatibility.
            forced: Whether the handler was explicitly selected.
            **kwargs: Additional styling options.

        Returns:
            str: HTML string with vega-embed initialization.

        Raises:
            ValueError: If content is not a valid Vega-Lite specification.
        """
        if not self.can_handle(content):
            raise ValueError("Content is not a valid Altair chart")

        if _is_altair_chart(content):
            json_content = content.to_json()
        elif isinstance(content, dict):
            json_content = json.dumps(content)
        else:
            json_content = content

        center_style = {"class": ["d-flex", "justify-content-center", "mx-auto"]}
        combined_kwargs = {**center_style, **kwargs}

        from respysive.content import Content

        temp_content = Content()
        temp_content.add_altair(json_content, **combined_kwargs)

        return temp_content.content
