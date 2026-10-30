"""
Base handler class for content processing
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseHandler(ABC):
    """Abstract base class for content handlers.

    All content handlers must inherit from this class and implement
    the abstract methods for content detection and processing.
    """

    def __init__(self, content_instance):
        """Initialize the handler with a Content instance.

        Args:
            content_instance: Instance of Content class to add content to
        """
        self.content = content_instance

    @abstractmethod
    def can_handle(self, content: Any) -> bool:
        """Check if this handler can process the given content.

        Args:
            content: Content to check

        Returns:
            bool: True if this handler can process the content
        """
        pass

    @abstractmethod
    def handle(self, content: Any, shared_data_id: str | None = None, forced: bool = False, **kwargs) -> str:
        """Process the content and return HTML string.

        Args:
            content: Content to process
            shared_data_id: Optional shared data ID for Plotly charts
            forced: Whether content type detection was forced
            kwargs: Additional styling and configuration options

        Returns:
            str: HTML string
        """
        pass

    @property
    @abstractmethod
    def priority(self) -> int:
        """Handler priority for content routing.

        Returns:
            int: Priority value (lower number = higher priority)
        """
        pass
