"""Export module for converting respysive presentations to various formats.

This module provides exporters to convert HTML presentations to static formats
like PDF and PPTX (PowerPoint).

Available exporters:
    - PdfExporter: Export to PDF, rendered by headless Chromium
    - PptxExporter: Export to Microsoft PowerPoint format (.pptx), from the
      layout rendered by headless Chromium

Example:
    >>> from respysive import Presentation
    >>> from respysive.exporters import PptxExporter
    >>>
    >>> presentation = Presentation()
    >>> # ... add slides ...
    >>>
    >>> exporter = PptxExporter(presentation)
    >>> exporter.save("output.pptx")
"""

from .pdf import PdfExporter
from .pptx_exporter import PptxExporter

__all__ = ["PdfExporter", "PptxExporter"]
