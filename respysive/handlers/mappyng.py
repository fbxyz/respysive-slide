"""Handler for mappyng SVG-native cartographic maps."""

from typing import Any

from .base import BaseHandler


class MappyngHandler(BaseHandler):
    """Handler for mappyng ``Map`` and ``InteractiveMap`` objects.

    mappyng (https://codeberg.org/fbxyz/mappyng) is an SVG-native
    cartographic library. Two object types are supported:

    - ``mappyng.interactive.InteractiveMap``: produced by
      ``Map.to_interactive(...)``; embeds tooltips/hover JS in the SVG.
      Rendered via ``_repr_html_()``.
    - ``mappyng.map.Map``: static map. Rendered by calling
      ``to_string()`` to fetch the raw SVG.

    Priority is set just above ``HtmlReprHandler`` so that mappyng
    objects are routed here explicitly rather than through the
    generic ``_repr_html_`` fallback.
    """

    @property
    def priority(self) -> int:
        return 7

    def can_handle(self, content: Any) -> bool:
        """Detect mappyng Map / InteractiveMap by module + class name.

        Avoids importing mappyng at module load time so it stays an
        optional dependency.
        """
        module = type(content).__module__ or ""
        if not (module == "mappyng" or module.startswith("mappyng.")):
            return False

        class_name = type(content).__name__
        if class_name == "InteractiveMap":
            return callable(getattr(content, "_repr_html_", None))
        if class_name == "Map":
            return callable(getattr(content, "to_string", None))
        return False

    def handle(self, content: Any, shared_data_id: str | None = None, forced: bool = False, **kwargs) -> str:
        """Render mappyng content to HTML.

        Args:
            content: mappyng ``Map`` or ``InteractiveMap`` instance.
            shared_data_id: Unused. Present for interface compatibility.
            forced: Whether the handler was explicitly selected.
            **kwargs: Additional CSS styles / class for the wrapping div.

        Returns:
            str: HTML wrapping the SVG in a centered responsive div.
        """
        from respysive.utils import _parse_style_class

        class_name = type(content).__name__
        if class_name == "InteractiveMap":
            inner_html = content._repr_html_()
        elif class_name == "Map":
            inner_html = content.to_string()
        else:
            raise ValueError(f"MappyngHandler cannot render object of type {class_name}")

        if "class" not in kwargs:
            kwargs["class"] = []
        elif isinstance(kwargs["class"], str):
            kwargs["class"] = [kwargs["class"]]
        kwargs["class"].extend(["d-flex", "justify-content-center"])

        s = _parse_style_class(kwargs)
        return f"<div {s}>{inner_html}</div>"
