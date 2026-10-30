"""Handler for Row and Column layout objects.

This module provides the LayoutHandler class for detecting and processing
Row and Column instances through the respysive content detection system.
"""

from typing import Any

from respysive.handlers.base import BaseHandler


class LayoutHandler(BaseHandler):
    """Handler for Row and Column layout objects.

    Detects Row and Column instances and generates Bootstrap grid HTML
    using the LayoutBuilder. This handler has high priority (6) to ensure
    layout objects are processed before generic content handlers.

    The handler integrates with the respysive content detection system,
    allowing Row and Column objects to contain any type of content
    (charts, images, text, etc.) which are recursively processed through
    their respective handlers.

    Priority: 6 (after CustomJsonHandler at 5, before charts at 10+)

    Example:
        >>> handler = LayoutHandler(content_obj)
        >>> row = Row([Column(8, chart), Column(4, text)])
        >>> html = handler.handle(row)
    """

    def __init__(self, content_instance):
        """Initialize LayoutHandler with content instance.

        Args:
            content_instance: Content object for data storage and management
        """
        super().__init__(content_instance)
        self._builder = None

    @property
    def priority(self) -> int:
        """Return handler priority (lower = higher priority).

        Returns:
            int: Priority value of 6 for layout objects
        """
        return 6

    def can_handle(self, content: Any) -> bool:
        """Check if content is a Row or Column object.

        Args:
            content: Content to check

        Returns:
            bool: True if content is Row or Column instance, False otherwise
        """
        from respysive.layout import Column, Row

        return isinstance(content, (Row, Column))

    def handle(self, content: Any, shared_data_id: str | None = None, forced: bool = False, **kwargs) -> str:
        """Process Row/Column and generate Bootstrap grid HTML.

        Uses LayoutBuilder to recursively generate HTML for Row and Column
        objects. Standalone Column objects are automatically wrapped in a
        row container.

        Args:
            content: Row or Column instance to process
            shared_data_id: Optional shared data ID (unused for layouts)
            forced: Whether handling was forced (unused)
            **kwargs: Additional styling options (unused, styles come from Row/Column)

        Returns:
            str: Generated Bootstrap grid HTML

        Example:
            >>> row = Row([Column(6, chart1), Column(6, chart2)])
            >>> html = handler.handle(row)
            >>> # Returns: <div class='row'><div class='col-md-6'>...</div>...</div>
        """
        from respysive.builders.layout import LayoutBuilder
        from respysive.layout import Column, Row

        if self._builder is None:
            content_detector = self._get_content_detector()
            self._builder = LayoutBuilder(self.content, content_detector)

        if isinstance(content, Row):
            return self._builder.build_row(content)
        elif isinstance(content, Column):
            return self._builder.build_standalone_column(content)

        return ""

    def _get_content_detector(self):
        """Get content detector from the handler registry.

        This method retrieves the content_detector that was used to register
        this handler. It's stored as a temporary attribute during registration.

        Returns:
            ContentDetector: The content detector instance

        Raises:
            AttributeError: If content_detector was not set during registration
        """
        if hasattr(self, "_content_detector"):
            return self._content_detector
        else:
            raise AttributeError(
                "LayoutHandler requires content_detector to be set during registration. "
                "This should be done automatically by the Slide class."
            )

    def set_content_detector(self, content_detector):
        """Set the content detector for this handler.

        This method is called during handler registration to provide access
        to the content detector for recursive content processing.

        Args:
            content_detector: ContentDetector instance to use
        """
        self._content_detector = content_detector
