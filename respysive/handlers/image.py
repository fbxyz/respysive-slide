"""Image file and URL handler."""

import os
import re
from typing import Any

from .base import BaseHandler


class ImageHandler(BaseHandler):
    """Handler for image files (local paths and URLs).

    Detects image content by file extension. Supported formats:
    JPEG, PNG, GIF, TIFF, APNG, BMP, SVG, AVIF, WebP (incl. animated).

    Priority: 40.
    """

    @property
    def priority(self) -> int:
        return 40

    def can_handle(self, content: Any) -> bool:
        """Check if content is an image file path or URL.

        Args:
            content: Content to check.

        Returns:
            bool: True if content is a string pointing to an image file.
        """
        if not isinstance(content, str):
            return False

        img_extensions = [".jpg", ".jpeg", ".png", ".gif", ".tif", ".apng", ".bmp", ".svg", ".avif", ".webp"]

        if os.path.isfile(content):
            return os.path.splitext(content)[1].lower() in img_extensions

        if re.match(
            r"(http(s)?:\/\/.)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)",
            content,
        ):
            return re.search(r"\.(jpg|jpeg|png|gif|tif|apng|bmp|svg|avif|webp)", content, re.IGNORECASE) is not None

        return False

    def handle(self, content: Any, shared_data_id: str | None = None, forced: bool = False, **kwargs) -> str:
        """Encode and embed the image as a base64 data URI.

        Args:
            content: File path or URL to the image.
            shared_data_id: Unused. Present for interface compatibility.
            forced: Whether the handler was explicitly selected.
            **kwargs: Additional styling options.

        Returns:
            str: HTML img element with embedded base64 data.

        Raises:
            ValueError: If content is not a valid image path or URL.
        """
        if not isinstance(content, str) or not self.can_handle(content):
            raise ValueError("Content must be a valid image file path or URL")

        center_style = {"class": ["d-flex", "justify-content-center", "mx-auto"]}
        combined_kwargs = {**center_style, **kwargs}

        from respysive.content import Content

        temp_content = Content()
        temp_content.add_image(content, **combined_kwargs)

        return temp_content.content
