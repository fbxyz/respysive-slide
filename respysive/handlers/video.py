"""Video file and URL handler."""

import os
import re
from typing import Any

from .base import BaseHandler


class VideoHandler(BaseHandler):
    """Handler for video files (local paths and URLs).

    Detects video content by file extension. Supported formats:
    MP4, WebM, OGG/OGV, MOV, M4V. The video binary is embedded inline
    as a base64 data URI (see the size trade-off note on
    :meth:`respysive.content.Content.add_video`).

    Priority: 40 (same as the image handler). Video and image extensions do
    not overlap, so animated WebP files are still routed to the image handler.
    """

    @property
    def priority(self) -> int:
        return 40

    def can_handle(self, content: Any) -> bool:
        """Check if content is a video file path or URL.

        Args:
            content: Content to check.

        Returns:
            bool: True if content is a string pointing to a video file.
        """
        if not isinstance(content, str):
            return False

        video_extensions = [".mp4", ".webm", ".ogg", ".ogv", ".mov", ".m4v"]

        if os.path.isfile(content):
            return os.path.splitext(content)[1].lower() in video_extensions

        # a URL holds no whitespace: a sentence naming a file is text
        if not re.search(r"\s", content.strip()) and re.match(
            r"(http(s)?:\/\/.)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)",
            content,
        ):
            return re.search(r"\.(mp4|webm|ogg|ogv|mov|m4v)\b", content, re.IGNORECASE) is not None

        return False

    def handle(self, content: Any, shared_data_id: str | None = None, forced: bool = False, **kwargs) -> str:
        """Encode and embed the video as a base64 data URI.

        Args:
            content: File path or URL to the video.
            shared_data_id: Unused. Present for interface compatibility.
            forced: Whether the handler was explicitly selected.
            **kwargs: Additional styling and `<video>` attribute options.

        Returns:
            str: HTML video element with embedded base64 data.

        Raises:
            ValueError: If content is not a valid video path or URL.
        """
        if not isinstance(content, str) or not (forced or self.can_handle(content)):
            raise ValueError("Content must be a valid video file path or URL")

        center_style = {"class": ["d-flex", "justify-content-center", "mx-auto"]}
        combined_kwargs = {**center_style, **kwargs}

        from respysive.content import Content

        temp_content = Content()
        temp_content.add_video(content, **combined_kwargs)

        return temp_content.content
