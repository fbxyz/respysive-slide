"""Base exporter class for respysive presentations.

Defines the interface for all presentation exporters.
"""

from abc import ABC, abstractmethod


class BaseExporter(ABC):
    """Abstract base class for presentation exporters.

    All exporters must inherit from this class and implement the required methods.

    Args:
        presentation: A respysive Presentation object to export
    """

    def __init__(self, presentation):
        """Initialize the exporter with a presentation.

        Args:
            presentation: respysive.Presentation object
        """
        self.presentation = presentation

    @abstractmethod
    def save(self, output_path: str, **kwargs):
        """Save the presentation to a file.

        Args:
            output_path: Path where to save the exported file
            **kwargs: Additional exporter-specific options
        """
        pass

    @abstractmethod
    def export(self, **kwargs):
        """Export the presentation to the target format.

        Returns:
            The exported presentation object (format-specific)
        """
        pass
