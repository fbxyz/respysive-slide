from bs4 import BeautifulSoup
import uuid

class Content:
    def __init__(self):
        self.content = ""
        self.scripts = {}
        self.grid_cols = 0

    @staticmethod
    def _parse_style(style: str):
        if style:
            return f"style='{style}'"
        return ""

    def add_script(self, name: str, script: str):
        """
        Add a script to the HTML document
        :param name : name of the script
        :param script : script to add
        """
        self.scripts[name] = script

    def add_title_page(
            self, title: str, subtitle: str = None, authors: list = None, logo: str = None,
            title_color: str = None, subtitle_color: str = None, authors_colors: str = None

    ):
        """
        Add a title page to the HTML document.
        :param title: The title of the page.
        :param subtitle: The subtitle of the page.
        :param authors: List of authors of the page.
        :param logo: The logo of the page.
        :param title_color: The title color.
        :param subtitle_color: The subtitle color.
        :param authors_colors: The authors names color.
        :return: The generated content
        """
        self.content += "<div class='row h-100 d-flex align-items-center'>"
        self.content += "<div class='col-12'>"

        if title_color:
            self.add_heading(title, tag="h1", text_align="center", font_size="4rem", color=title_color)
        else:
            self.add_heading(title, tag="h1", text_align="center", font_size="4rem")

        self.content += "</div>"
        if subtitle:
            self.content += "<div class='col-12' style='margin-top:120px;'>"
            if subtitle_color:
                self.add_heading(subtitle, tag="h2", text_align="center", font_size="2rem", color=subtitle_color)
            else:
                self.add_heading(subtitle, tag="h2", text_align="center", font_size="2rem")

            self.content += "</div>"
        self.content += "</div>"

        if authors or logo:
            self.content += "<div class='row h-100 d-flex align-items-end'>"
            if authors:
                author_str = ", ".join(authors)
                self.content += "<div class='col-8 pull-left'>"

                if authors_colors:
                    self.add_text(author_str, tag="p", text_align="left", font_size="1rem", color=authors_colors)
                else:
                    self.add_text(author_str, tag="p", text_align="left", font_size="1rem")

                self.content += "</div>"
            if logo:
                self.content += "<div class='col-4 img-responsive pull-right'>"
                self.add_image(logo)
                self.content += "</div>"
            self.content += "</div>"

        return self.content

    def add_subtitle(self, text: str, icon: str = None, **kwargs):
        """
        Add a subtitle to the HTML document.
        :param text: The text of the subtitle.
        :param icon: The icon of the subtitle.
        :param kwargs: Additional CSS styles to apply to the image. (optional)
                The keys should be in the format of CSS property names with '_' instead of '-', example: font_size
        """
        style_str = ""
        for key, value in kwargs.items():
            css_key = key.replace("_", "-")
            style_str += f"{css_key}: {value};"
        self.content += (
            f"<h2 class='mx-auto text-center' style='padding-top: 25%;{style_str}'><i class='{icon}'></i> {text}</h2>"
            if icon
            else f"<h2 class='mx-auto text-center' style='padding-top: 25%;{style_str}'>{text}</h2>"
        )

    def add_heading(
            self,
            text: str,
            tag: str = "h1",
            margin_bottom: str = "30px",
            icon: str = None,
            **kwargs
    ):
        """
        Add a heading element to the HTML document.
        :param text: The text of the heading.
        :param tag: The HTML tag to use for the heading. Default is 'h1'.
        :param margin_bottom: The margin-bottom property of the heading. Default is '30px'.
        :param icon: The icon of the heading.
        :param kwargs: Additional CSS styles to apply to the image. (optional)
                The keys should be in the format of CSS property names with '_' instead of '-', example: font_size
        """
        if tag not in ["h1", "h2", "h3", "h4", "h5"]:
            raise ValueError("Invalid tag, the tag must be one of h1, h2, h3, h4 or h5")
        style_str = ""
        for key, value in kwargs.items():
            css_key = key.replace("_", "-")
            style_str += f"{css_key}: {value};"
        self.content += (
            f"<{tag} style='margin-top-bottom: {margin_bottom}; {style_str}'><i class='{icon}'></i> {text}</{tag}>"
            if icon
            else f"<{tag} style='margin-top-bottom: {margin_bottom}; {style_str}'>{text}</{tag}>"
        )

    def add_text(self, text: str, tag: str = "p", font_size="calc(1vw + 1vh)", **kwargs):
        """
        Add a text element to the HTML document.
        :param text: The text to be added.
        :param tag: The HTML tag to use for the text. Default is 'p'.
        :param font_size: the font-size to fit in boostrap container.
        :param kwargs: Additional CSS styles to apply to the image. (optional)
                The keys should be in the format of CSS property names with '_' instead of '-', example: font_size
        """
        if tag not in ["p", "span"]:
            raise ValueError("Invalid tag, the tag must be one of p or span")
        style_str = ""
        for key, value in kwargs.items():
            css_key = key.replace("_", "-")
            style_str += f"{css_key}: {value};"
        self.content += f"<{tag} style='font-size:{font_size}; {style_str}'>{text}</{tag}>"

    def add_list(
            self, items: list, ordered=False, font_size="1rem", **kwargs
    ):
        """
        Add a list element to the HTML document.
        :param items: The items of the list.
        :param ordered: Whether the list should be ordered or not.
        :param font_size: the font-size to fit in boostrap container.
        :param kwargs: Additional CSS styles to apply to the image. (optional)
                The keys should be in the format of CSS property names with '_' instead of '-', example: font_size
        """
        list_tag = "ol" if ordered else "ul"
        style_str = ""
        for key, value in kwargs.items():
            css_key = key.replace("_", "-")
            style_str += f"{css_key}: {value};"
        list_items = "\n".join([f"<li>{item}</li>" for item in items])
        self.content += f"<{list_tag} style='font-size:{font_size}; {style_str}'>\n{list_items}\n</{list_tag}>"

    def add_image(self, img_src: str, alt: str = "", **kwargs):
        """
        Add an image element to the HTML document.
        :param img_src: The source of the image.
        :param alt: The alternative text for the image.
        :param kwargs: Additional CSS styles to apply to the image. (optional)
                The keys should be in the format of CSS property names with '_' instead of '-', example: font_size
        """
        style_str = ""
        for key, value in kwargs.items():
            css_key = key.replace("_", "-")
            style_str += f"{css_key}: {value};"
        self.content += (
            f"<img src='{img_src}' alt='{alt}' class='img-fluid' style='{style_str}'>"
        )

    def add_svg(self, svg_code: str, width: str = None, height: str = None, **kwargs):
        """
        Add a svg to the document.

        :param svg_code : The code of the svg.
        :param width : The width of the svg.
        :param height : The height of the svg.
        :param kwargs: Additional CSS styles to apply to the svg. (optional)
                The keys should be in the format of CSS property names with '_' instead of '-', example: font_size
        """
        width_str = f'width="{width}"' if width else ""
        height_str = f'height="{height}"' if height else ""
        style_str = ""
        for key, value in kwargs.items():
            css_key = key.replace("_", "-")
            style_str += f"{css_key}: {value};"
        self.content += f"""<svg {width_str} {height_str} class='img-fluid' style='{style_str}'>{svg_code}</svg>"""

    def add_plotly(self, json: str):
        """
        Add a plotly json to the document.

        :param json : a plotly json (fig.to_json()).

        """
        chart_id = "chart-" + str(uuid.uuid4())
        self.content += f"""<div id='{chart_id}'></div>
            <script>var Plotjson = '{json}';
            var figure = JSON.parse(Plotjson);
            Plotly.newPlot('{chart_id}', figure.data, figure.layout);</script>"""

    def add_altair(self, json: str):
        """
        Add an Altair json to the document.

        :param json : an Altair json (chart.to_json()).

        """
        chart_id = "chart-" + str(uuid.uuid4())
        self.content += f"""<div id='{chart_id}'></div>
        <script>var opt = {{renderer: "svg"}};
        vegaEmbed("#{chart_id}", {json} , opt);</script>"""

    def render(self):
        """
        Return the complete HTML document as a string.
        """
        html = f"""<div>{self.content}</div>"""
        soup = BeautifulSoup(html, "html.parser")
        ident_content = soup.prettify()
        return ident_content

