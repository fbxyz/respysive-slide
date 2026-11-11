"""Card builder for Bootstrap cards in presentations."""

import json

from matplotlib.figure import Figure

from respysive.errors import validate_card_parameters
from respysive.utils import (
    _fragment_class,
    _parse_style_class,
    add_list_classes,
    encode_image_to_data_uri,
    process_markdown_with_latex,
)


class CardBuilder:
    """Builder for Bootstrap card components.

    Handles creation of card layouts with support for titles, text, images,
    and embedded charts including MapLibre maps.

    Args:
        content_detector: Content detector for processing card content
    """

    def __init__(self, content_detector):
        """Initialize with a content detector for processing card graphs.

        Args:
            content_detector: ContentDetector instance for rendering chart content.
        """
        self.content_detector = content_detector

    def _process_graph_for_card(self, graph_content, bootstrap_width):
        """Process graph content and adapt size for card width.

        Args:
            graph_content: Chart object (matplotlib, plotly, altair, maplibre)
            bootstrap_width: Bootstrap column width (1-12) of card

        Returns:
            str: Processed HTML content with adapted size
        """
        approximate_width = int((bootstrap_width / 12) * 800)
        approximate_height = int(approximate_width * 0.6)

        if isinstance(graph_content, Figure):
            # drawn smaller so that its text stays readable in a narrow card,
            # with the same proportions; the figure gets its size back afterwards
            width, height = graph_content.get_size_inches()
            scale_factor = min(1.0, approximate_width / 600)
            scale_factor = min(1.0, max(scale_factor, 4 / width, 3 / height))
            graph_content.set_size_inches(width * scale_factor, height * scale_factor)
            try:
                return self.content_detector.detect_and_handle(graph_content)
            finally:
                graph_content.set_size_inches(width, height)

        elif isinstance(graph_content, (str, dict)):
            if isinstance(graph_content, str):
                try:
                    plotly_config = json.loads(graph_content)
                    if "layout" in plotly_config:
                        plotly_config["layout"]["width"] = approximate_width
                        plotly_config["layout"]["height"] = approximate_height
                        graph_content = json.dumps(plotly_config)
                except (json.JSONDecodeError, KeyError):
                    pass
            elif isinstance(graph_content, dict) and isinstance(graph_content.get("layout"), dict):
                # a copy: the caller's figure keeps its size
                layout = {**graph_content["layout"], "width": approximate_width, "height": approximate_height}
                graph_content = {**graph_content, "layout": layout}

        return self.content_detector.detect_and_handle(graph_content)

    def build_cards(self, cards, styles=None, fragment=None):
        """Build HTML for Bootstrap card grid.

        Args:
            cards: List of card dictionaries with title, text, image, or graph
            styles: List of style dictionaries for card containers
            fragment: Fragment spec (True, style string, or one value per card)

        Returns:
            str: HTML content with card grid
        """
        validate_card_parameters(cards, styles, None, None, None, "build_cards")

        if styles is None:
            styles = [{"class": "bg-info"}] * len(cards)
        # copies: classes are added below, and the caller may reuse its dicts
        styles = [dict(style or {}) for style in styles]

        num_cards = len(cards)
        if num_cards == 1:
            card_bootstrap_width = 12
        elif num_cards == 2:
            card_bootstrap_width = 6
        elif num_cards == 3:
            card_bootstrap_width = 4
        elif num_cards == 4:
            card_bootstrap_width = 3
        else:
            card_bootstrap_width = max(2, 12 // num_cards)

        cards_html = ""
        for i, (card, style) in enumerate(zip(cards, styles, strict=False)):
            classes = style.get("class") or []
            style["class"] = classes.split() if isinstance(classes, str) else list(classes)

            if "card" not in style["class"]:
                style["class"].append("card")
            if "h-100" not in style["class"]:
                style["class"].append("h-100")

            has_only_title = (
                "title" in card
                and "text" not in card
                and "image" not in card
                and "graph" not in card
                and "video" not in card
            )
            if has_only_title and "title-only" not in style["class"]:
                style["class"].append("title-only")

            s = _parse_style_class(style)

            image_html = ""
            card_body_content = ""

            for key in card.keys():
                if key == "image":
                    image_src = card[key]
                    if not image_src.startswith("data:"):
                        image_src = encode_image_to_data_uri(image_src)

                    image_style = dict(card.get("image_style") or {})

                    if "max-width" not in image_style and "width" not in image_style:
                        image_style["width"] = "100%"
                    if "max-height" not in image_style and "height" not in image_style:
                        image_style["max-height"] = "300px"
                    if "object-fit" not in image_style:
                        image_style["object-fit"] = "contain"

                    image_style_attr = _parse_style_class(image_style) if image_style else ""

                    wrapper_height = image_style.get("max-height", image_style.get("height", "300px"))
                    wrapper_style = f"overflow: hidden; display: flex; align-items: center; justify-content: center; background-color: #f8f9fa; max-height: {wrapper_height};"
                    image_html = f'<div style="{wrapper_style}"><img src="{image_src}" class="card-img-top" alt="" {image_style_attr}></div>'
                elif key == "video":
                    video_style = dict(card.get("video_style") or {})
                    if "max-width" not in video_style and "width" not in video_style:
                        video_style["width"] = "100%"
                    if "max-height" not in video_style and "height" not in video_style:
                        video_style["max-height"] = "300px"

                    from respysive.content import Content

                    temp_content = Content()
                    temp_content.add_video(card[key], **video_style)

                    wrapper_height = video_style.get("max-height", video_style.get("height", "300px"))
                    wrapper_style = f"overflow: hidden; display: flex; align-items: center; justify-content: center; background-color: #f8f9fa; max-height: {wrapper_height};"
                    image_html = f'<div style="{wrapper_style}">{temp_content.content}</div>'
                elif key == "title":
                    title_tag = card.get("title_tag", "h5")
                    default_title_style = {"font-size": "60%"}
                    title_style = card.get("title_style", {})
                    title_style = {**default_title_style, **title_style}

                    title_classes = "card-title text-center font-weight-bold"
                    if has_only_title:
                        title_classes += " m-0 p-0"

                    title_style_attr = _parse_style_class(title_style) if title_style else ""
                    processed_title = process_markdown_with_latex(card[key])
                    card_body_content += (
                        f'<{title_tag} class="{title_classes}" {title_style_attr}>{processed_title}</{title_tag}>'
                    )
                elif key == "text":
                    text_style = card.get("text_style", {})
                    processed_text = process_markdown_with_latex(card[key])
                    default_font_size = text_style.get("font-size", text_style.get("font_size", "85%"))
                    processed_text = add_list_classes(processed_text, default_font_size)
                    text_style_attr = _parse_style_class(text_style) if text_style else ""
                    card_body_content += f'<div class="card-text" {text_style_attr}>{processed_text}</div>'
                elif key == "graph":
                    graph_html = self._process_graph_for_card(card[key], card_bootstrap_width)
                    card_body_content += f'<div class="card-graph">{graph_html}</div>'

            if image_html:
                card_html = f'{image_html}<div class="card-body p-4">{card_body_content}</div>'
            else:
                card_html = f'<div class="card-body p-4">{card_body_content}</div>'

            cards_html += f"""
            <div class="col-{card_bootstrap_width} {_fragment_class(fragment, i)}">
                <div {s}>
                    {card_html}
                </div>
            </div>"""

        return f"<div class='row'>{cards_html}</div>"
