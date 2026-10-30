"""Centralized content detection and routing system."""

from typing import Any

from .base import BaseHandler


class ContentDetector:
    """Route content to the appropriate handler based on type detection.

    Maintains a priority-sorted list of handlers. When processing content,
    each handler is tried in priority order until one matches. A content
    type can also be forced explicitly.
    """

    def __init__(self):
        """Initialize with an empty handler list."""
        self._handlers: list[BaseHandler] = []

    def register_handler(self, handler_class: type[BaseHandler], content_instance) -> None:
        """Register a new content handler.

        Args:
            handler_class: Handler class to register
            content_instance: Content instance to pass to handler
        """
        handler = handler_class(content_instance)
        self._handlers.append(handler)
        self._handlers.sort(key=lambda h: h.priority)

    def detect_and_handle(
        self, content: Any, shared_data_id: str | None = None, content_type: str | None = None, **kwargs
    ) -> str:
        """Detect content type and delegate to appropriate handler.

        Args:
            content: Content to process
            shared_data_id: Optional shared data ID for Plotly charts
            content_type: Optional content type to force ('plotly', 'matplotlib', 'maplibre', 'altair', 'image', 'video', 'latex', 'text', 'json')
            kwargs: Additional styling and configuration options

        Returns:
            str: Processed HTML string
        """
        if content_type:
            handler_mapping = {
                "plotly": "PlotlyHandler",
                "matplotlib": "MatplotlibHandler",
                "maplibre": "MapLibreHandler",
                "mappyng": "MappyngHandler",
                "altair": "AltairHandler",
                "image": "ImageHandler",
                "video": "VideoHandler",
                "latex": "LatexHandler",
                "text": "TextHandler",
                "json": "CustomJsonHandler",
                "html": "HtmlReprHandler",
            }

            target_handler_name = handler_mapping.get(content_type.lower())
            if target_handler_name is None:
                raise ValueError(
                    f"Unknown content_type '{content_type}'. Available types: {list(handler_mapping.keys())}"
                )
            for handler in self._handlers:
                if type(handler).__name__ == target_handler_name:
                    return handler.handle(content, shared_data_id, forced=True, **kwargs)

            raise ValueError(f"Handler for content_type '{content_type}' is not registered.")

        for handler in self._handlers:
            if handler.can_handle(content):
                return handler.handle(content, shared_data_id, **kwargs)

        from .text import TextHandler

        fallback_handler = TextHandler(self._handlers[0].content if self._handlers else None)
        return fallback_handler.handle(str(content), shared_data_id, **kwargs)

    def get_handlers(self) -> list[BaseHandler]:
        """Get list of registered handlers.

        Returns:
            List[BaseHandler]: List of handlers sorted by priority
        """
        return self._handlers.copy()
