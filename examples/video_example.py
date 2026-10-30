"""Example demonstrating embedded base64 video support in respysive.

Videos are embedded inline as base64 data URIs, exactly like images.

Note on size:
    Base64 encoding inflates the binary by roughly 33% compared to the original
    file. A large video therefore makes the generated HTML much heavier; prefer
    short, web-optimized clips. ``autoplay`` only works reliably when the video
    is also ``muted`` (the defaults handle this for you).

Usage:
    Set VIDEO_SRC below to a local path or URL of a real video file
    (.mp4, .webm, .ogg/.ogv, .mov, .m4v), then run:

        python examples/video_example.py
"""

import os
import sys

# Add parent directory to path to use local respysive instead of installed version
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from respysive import Presentation, Slide

# A local path or URL to a real video file.
VIDEO_SRC = "my_clip.mp4"
# Optional preview image shown before playback (path or URL).
POSTER_SRC = None


def build_presentation(video_src, poster_src=None):
    """Build a 3-slide presentation showcasing the video API."""
    pres = Presentation()

    # Slide 1: video via auto-detection (extension-based)
    slide1 = Slide()
    slide1.add_title("Embedded video (auto-detected)")
    slide1.add_content([video_src], columns=[10])
    pres.add_slide(slide1)

    # Slide 2: customizing the <video> attributes
    slide2 = Slide()
    slide2.add_title("Video with custom attributes")
    slide2.content_obj.add_video(
        video_src,
        autoplay=False,  # show controls, don't autoplay
        loop=False,
        muted=False,
        poster=poster_src,
        max_width="80%",
    )
    slide2.content += slide2.content_obj.content
    pres.add_slide(slide2)

    # Slide 3: a video inside a card
    slide3 = Slide()
    slide3.add_title("Video in a card")
    slide3.add_card(
        [
            {"title": "Demo clip", "video": video_src, "video_style": {"max-height": "350px"}},
            {"title": "Notes", "text": "Cards accept a `video` key, just like `image`."},
        ]
    )
    pres.add_slide(slide3)

    return pres


if __name__ == "__main__":
    if not (VIDEO_SRC.startswith(("http://", "https://")) or os.path.isfile(VIDEO_SRC)):
        sys.exit(
            f"VIDEO_SRC '{VIDEO_SRC}' not found. Edit examples/video_example.py and point it at a real video file."
        )
    pres = build_presentation(VIDEO_SRC, POSTER_SRC)
    out = os.path.join(os.path.dirname(__file__), "video_example.html")
    pres.save_html(out)
    print(f"Saved {out}")
