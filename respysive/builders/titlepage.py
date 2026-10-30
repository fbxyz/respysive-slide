"""Title page builder for presentations."""

from respysive.errors import validate_split_title_page_columns, validate_styles_length, validate_title_page_parameters
from respysive.utils import _parse_style_class, encode_image_to_data_uri


class TitlePageBuilder:
    """Builder for presentation title pages.

    Handles creation of standard and split-column title pages with support
    for title, subtitle, authors, logos, and background images.

    Args:
        slide: Parent Slide instance for applying configurations
        content_detector: Content detector for processing custom content
    """

    def __init__(self, slide, content_detector):
        """Initialize with the parent slide and content detector.

        Args:
            slide: Parent Slide instance.
            content_detector: ContentDetector for processing custom content.
        """
        self.slide = slide
        self.content_detector = content_detector

    def build_title_page(
        self, title_page_content, styles=None, title_page_class="", background_image=None, background_style=None
    ):
        """Build HTML for standard title page.

        Args:
            title_page_content: Dictionary with 'title', 'subtitle', 'authors', 'logo' keys
            styles: List of style dictionaries for each element
            title_page_class: Additional CSS class for title-page div
            background_image: URL or path to background image
            background_style: Dictionary with background styling options

        Returns:
            str: HTML content for title page
        """
        validate_title_page_parameters(title_page_content, styles, "build_title_page")

        title = title_page_content.get("title", "")
        subtitle = title_page_content.get("subtitle", "")
        authors = title_page_content.get("authors", "")
        logo = title_page_content.get("logo", "")

        present_elements = []
        if title:
            present_elements.append("title")
        if subtitle:
            present_elements.append("subtitle")
        if authors:
            present_elements.append("authors")
        if logo:
            present_elements.append("logo")

        if styles is None:
            styles = []

        style_idx = 0
        title_s = _parse_style_class(styles[style_idx]) if styles and title else ""
        if title and styles:
            style_idx += 1

        subtitle_s = _parse_style_class(styles[style_idx]) if styles and subtitle else ""
        if subtitle and styles:
            style_idx += 1

        authors_s = _parse_style_class(styles[style_idx]) if styles and authors else ""
        if authors and styles:
            style_idx += 1

        logo_s = _parse_style_class(styles[style_idx]) if styles and logo else ""

        if logo:
            if not logo.startswith("data:"):
                logo = encode_image_to_data_uri(logo)

        title_html = f'<div class="row"><div class="col-12"><h2 {title_s}>{title}</h2></div></div>' if title else ""
        subtitle_html = (
            f'<div class="row"><div class="col-12"><h3 {subtitle_s}>{subtitle}</h3></div></div>' if subtitle else ""
        )
        authors_col = "col-9" if logo else "col-12"
        authors_html = f'<div class="{authors_col}"><h4 {authors_s}>{authors}</h4></div>' if authors else ""
        logo_html = f'<div class="col-3"><img src="{logo}" {logo_s}></div>' if logo else ""
        authors_logo_html = f'<div class="row align-items-center">{authors_html}{logo_html}</div>'

        page_class = f"title-page {title_page_class}".strip()

        if background_image:
            encoded_image = encode_image_to_data_uri(background_image)
            self.slide.kwargs["data-background-image"] = encoded_image

            if "data-background-size" not in self.slide.kwargs:
                self.slide.kwargs["data-background-size"] = "cover"
            if "data-background-position" not in self.slide.kwargs:
                self.slide.kwargs["data-background-position"] = "center"
            if "data-background-repeat" not in self.slide.kwargs:
                self.slide.kwargs["data-background-repeat"] = "no-repeat"

            if background_style:
                for key, value in background_style.items():
                    if key == "background-size":
                        self.slide.kwargs["data-background-size"] = value
                    elif key == "background-position":
                        self.slide.kwargs["data-background-position"] = value
                    elif key == "background-repeat":
                        self.slide.kwargs["data-background-repeat"] = value
                    elif key.startswith("data-"):
                        self.slide.kwargs[key] = value

        return f'<div class="{page_class}">{title_html}{subtitle_html}{authors_logo_html}</div>'

    def build_split_title_page(
        self,
        title_page_content,
        custom_content,
        title_column_width=6,
        custom_column_width=6,
        title_page_class="",
        custom_content_style=None,
        title_styles=None,
        title_column_style=None,
        background_image=None,
        background_style=None,
        full_height=False,
    ):
        """Build HTML for split-column title page.

        Args:
            title_page_content: Dictionary with 'title', 'subtitle', 'authors', 'logo' keys
            custom_content: Content for second column
            title_column_width: Bootstrap width for title column (1-12)
            custom_column_width: Bootstrap width for custom content column (1-12)
            title_page_class: Additional CSS class for title-page div
            custom_content_style: Style dictionary for custom content column
            title_styles: List of style dictionaries for title elements
            title_column_style: Style dictionary for title column container
            background_image: URL or path to background image
            background_style: Dictionary with background styling options
            full_height: If True, covers full slide viewport with no margins

        Returns:
            str: HTML content for split title page
        """
        validate_split_title_page_columns(title_column_width, custom_column_width, "build_split_title_page")

        title = title_page_content.get("title", "")
        subtitle = title_page_content.get("subtitle", "")
        authors = title_page_content.get("authors", "")
        logo = title_page_content.get("logo", "")

        present_elements = []
        if title:
            present_elements.append("title")
        if subtitle:
            present_elements.append("subtitle")
        if authors:
            present_elements.append("authors")
        if logo:
            present_elements.append("logo")

        if title_styles is not None:
            validate_styles_length(title_styles, present_elements, "build_split_title_page (title_styles)")

        if title_styles is None:
            title_styles = []

        style_idx = 0
        title_s = _parse_style_class(title_styles[style_idx]) if title_styles and title else ""
        if title and title_styles:
            style_idx += 1

        subtitle_s = _parse_style_class(title_styles[style_idx]) if title_styles and subtitle else ""
        if subtitle and title_styles:
            style_idx += 1

        authors_s = _parse_style_class(title_styles[style_idx]) if title_styles and authors else ""
        if authors and title_styles:
            style_idx += 1

        logo_s = _parse_style_class(title_styles[style_idx]) if title_styles and logo else ""

        if logo:
            if not logo.startswith("data:"):
                logo = encode_image_to_data_uri(logo)

        title_html = f"<h2 {title_s}>{title}</h2>" if title else ""
        subtitle_html = f"<h3 {subtitle_s}>{subtitle}</h3>" if subtitle else ""

        if authors and logo:
            authors_logo_html = f'''
                <div class="row align-items-center">
                    <div class="col-9"><h4 {authors_s}>{authors}</h4></div>
                    <div class="col-3"><img src="{logo}" {logo_s}></div>
                </div>'''
        elif authors:
            authors_logo_html = f"<h4 {authors_s}>{authors}</h4>"
        elif logo:
            authors_logo_html = f'<img src="{logo}" {logo_s}>'
        else:
            authors_logo_html = ""

        title_content_html = f"{title_html}{subtitle_html}{authors_logo_html}"

        processed_custom_content = self.content_detector.detect_and_handle(custom_content)

        default_title_column_style = {"color": "white", "padding": "30px"}
        if title_column_style:
            default_title_column_style.update(title_column_style)
        title_column_style_attr = _parse_style_class(default_title_column_style)

        default_custom_style = {"background-color": "white", "padding": "30px"}
        if custom_content_style:
            default_custom_style.update(custom_content_style)
        custom_style_attr = _parse_style_class(default_custom_style)

        page_class = f"title-page {title_page_class}".strip()

        if full_height:
            if "class" not in self.slide.kwargs:
                self.slide.kwargs["class"] = "full-height-slide"
            elif isinstance(self.slide.kwargs["class"], str):
                self.slide.kwargs["class"] = [self.slide.kwargs["class"], "full-height-slide"]
            elif isinstance(self.slide.kwargs["class"], list):
                if "full-height-slide" not in self.slide.kwargs["class"]:
                    self.slide.kwargs["class"].append("full-height-slide")

            self.slide.center = False

            title_width_pct = (title_column_width / 12) * 100
            custom_width_pct = (custom_column_width / 12) * 100

            page_class += " fullscreen-split"

            left_bg = default_title_column_style.get("background-color", "#1d3557")
            right_bg = default_custom_style.get("background-color", "white")

            self.slide.kwargs["data-background-gradient"] = (
                f"linear-gradient(to right, {left_bg} 0%, {left_bg} {title_width_pct}%, "
                f"{right_bg} {title_width_pct}%, {right_bg} 100%)"
            )

            left_styles = {
                k: v for k, v in default_title_column_style.items() if k not in ["background-color", "class"]
            }
            left_styles["width"] = f"{title_width_pct}%"
            left_style_str = "; ".join([f"{k}: {v}" for k, v in left_styles.items()])

            right_styles = {k: v for k, v in default_custom_style.items() if k not in ["background-color", "class"]}
            right_styles["width"] = f"{custom_width_pct}%"
            right_style_str = "; ".join([f"{k}: {v}" for k, v in right_styles.items()])

            return f'''
        <div class="fullscreen-split-container">
            <div class="split-left" style="{left_style_str}">
                {title_content_html}
            </div>
            <div class="split-right" style="{right_style_str}">
                {processed_custom_content}
            </div>
        </div>'''

        else:
            row_class = "row"
            col_class_extra = ""

        if background_image:
            encoded_image = encode_image_to_data_uri(background_image)
            self.slide.kwargs["data-background-image"] = encoded_image

            if "data-background-size" not in self.slide.kwargs:
                self.slide.kwargs["data-background-size"] = "cover"
            if "data-background-position" not in self.slide.kwargs:
                self.slide.kwargs["data-background-position"] = "center"
            if "data-background-repeat" not in self.slide.kwargs:
                self.slide.kwargs["data-background-repeat"] = "no-repeat"

            if background_style:
                for key, value in background_style.items():
                    if key == "background-size":
                        self.slide.kwargs["data-background-size"] = value
                    elif key == "background-position":
                        self.slide.kwargs["data-background-position"] = value
                    elif key == "background-repeat":
                        self.slide.kwargs["data-background-repeat"] = value
                    elif key.startswith("data-"):
                        self.slide.kwargs[key] = value

        return f'''
        <div class="{page_class}">
            <div class="{row_class}">
                <div class="col-md-{title_column_width}{col_class_extra}" {title_column_style_attr}>
                    {title_content_html}
                </div>
                <div class="col-md-{custom_column_width}{col_class_extra}" {custom_style_attr}>
                    {processed_custom_content}
                </div>
            </div>
        </div>'''
