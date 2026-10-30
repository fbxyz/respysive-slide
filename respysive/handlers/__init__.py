"""Content handlers for automatic type detection and rendering."""

from .altair import AltairHandler
from .base import BaseHandler
from .content_detector import ContentDetector
from .custom_json import CustomJsonHandler
from .html_repr import HtmlReprHandler
from .image import ImageHandler
from .latex import LatexHandler
from .layout import LayoutHandler
from .maplibre import MapLibreHandler
from .mappyng import MappyngHandler
from .matplotlib import MatplotlibHandler
from .plotly import PlotlyHandler
from .text import TextHandler
from .video import VideoHandler

__all__ = [
    "BaseHandler",
    "TextHandler",
    "LatexHandler",
    "ImageHandler",
    "VideoHandler",
    "MatplotlibHandler",
    "PlotlyHandler",
    "AltairHandler",
    "CustomJsonHandler",
    "MapLibreHandler",
    "MappyngHandler",
    "HtmlReprHandler",
    "LayoutHandler",
    "ContentDetector",
]
