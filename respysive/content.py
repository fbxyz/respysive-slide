from bs4 import BeautifulSoup
import uuid
from respysive.utils import _parse_style_class


class Content:
    """
    A class representing a slide content.
    """
    def __init__(self):

        self.content = ""
        self.scripts = {}
        self.grid_cols = 0

    def clear(self):
        self.content = ""

    def add_script(self, name: str, script: str):
        """
        Add a script to the HTML document
        :param name : name of the script
        :param script : script to add
        """
        self.scripts[name] = script

    def add_heading(self, text: str, tag: str = "h3", icon: str = None, **kwargs):
        """
        Add a heading element to the HTML document.
        :param text: The text of the heading.
        :param tag: The HTML tag to use for the heading. Default is 'h1'.
        :param icon: The icon of the heading (optional).
        :param kwargs: Additional CSS styles and html class to apply to the image. (optional)
                The keys should be in the format of CSS property names with '_' instead of '-', example: font_size
                you can also pass the class key with a string or a list of strings
                example : {'font_size': '20px', 'color': 'blue', 'class':'my-class'} or  {'font_size': '20px',
                 'color': 'blue', 'class':['my-class','my-second-class']}
        """
        if tag not in ["h1", "h2", "h3", "h4", "h5"]:
            raise ValueError("Invalid tag, the tag must be one of h1, h2, h3, h4 or h5")

        s = _parse_style_class(kwargs)

        self.content += (

            f"<{tag} {s}><i class='{icon}'></i> {text}</{tag}>"
            if icon
            else f"<{tag} {s}>{text}</{tag}>"
        )

    def add_text(self, text: str, tag: str = "p", **kwargs):
        """
        Add a text element to the HTML document.
        :param text: The text to be added.
        :param tag: The HTML tag to use for the text. Default is 'p'.
        :param kwargs: Additional CSS styles and html class to apply to the image. (optional)
                The keys should be in the format of CSS property names with '_' instead of '-', example: font_size
                you can also pass the class key with a string or a list of strings
                example : {'font_size': '20px', 'color': 'blue', 'class':'my-class'} or  {'font_size': '20px',
                 'color': 'blue', 'class':['my-class','my-second-class']}
        """
        if tag not in ["p", "span"]:
            raise ValueError("Invalid tag, the tag must be one of p or span")

        s = _parse_style_class(kwargs)

        self.content += f"""<{tag} {s}>{text}</{tag}>"""

    def add_list(
            self, items: list, ordered=False, **kwargs):
        """
        Add a list element to the HTML document.
        :param items: The items of the list.
        :param ordered: Whether the list should be ordered or not.
        :param kwargs: Additional CSS styles and html class to apply to the image. (optional)
                The keys should be in the format of CSS property names with '_' instead of '-', example: font_size
                you can also pass the class key with a string or a list of strings
                example : {'font_size': '20px', 'color': 'blue', 'class':'my-class'} or  {'font_size': '20px',
                 'color': 'blue', 'class':['my-class','my-second-class']}
        """
        list_tag = "ol" if ordered else "ul"

        s = _parse_style_class(kwargs)

        list_items = "\n".join([f"<li>{item}</li>" for item in items])
        self.content += f"<{list_tag} {s}>\n{list_items}\n</{list_tag}>"

    def add_image(self, src: str, alt: str = "", **kwargs):
        """
        Add an image element to the HTML document.
        :param src: The source of the image.
        :param alt: The alternative text for the image.
        :param kwargs: Additional CSS styles and html class to apply to the image. (optional)
                The keys should be in the format of CSS property names with '_' instead of '-', example: font_size
                you can also pass the class key with a string or a list of strings
                example : {'font_size': '20px', 'color': 'blue', 'class':'my-class'} or  {'font_size': '20px',
                 'color': 'blue', 'class':['my-class','my-second-class']}
        """

        if 'class' not in kwargs:
            kwargs['class'] = []
        elif isinstance(kwargs['class'], str):
            kwargs['class'] = [kwargs['class']]
        kwargs['class'].append('img-fluid')

        s = _parse_style_class(kwargs)

        self.content += f"<img data-src='{src}' alt='{alt}' {s}>"

    def add_svg(self, svg: str,  **kwargs):
        """
        Add a svg to the document.
        :param svg : The code of the svg.
        :param kwargs: Additional CSS styles and html class to apply to the image. (optional)
                The keys should be in the format of CSS property names with '_' instead of '-', example: font_size
                you can also pass the class key with a string or a list of strings
                example : {'font_size': '20px', 'color': 'blue', 'class':'my-class'} or  {'font_size': '20px',
                 'color': 'blue', 'class':['my-class','my-second-class']}
        """

        if 'class' not in kwargs:
            kwargs['class'] = []
        elif isinstance(kwargs['class'], str):
            kwargs['class'] = [kwargs['class']]
        kwargs['class'].append('img-fluid')

        s = _parse_style_class(kwargs)

        self.content += f"""<div {s}>{svg}</div>"""

    def add_plotly(self, json: str, **kwargs):
        """
        Add a plotly json to the document.
        :param json : a plotly json (fig.to_json()).
        :param kwargs: Additional CSS styles and html class to apply to the image. (optional)
        The keys should be in the format of CSS property names with '_' instead of '-', example: font_size
        you can also pass the class key with a string or a list of strings
        example : {'font_size': '20px', 'color': 'blue', 'class':'my-class'} or  {'font_size': '20px',
         'color': 'blue', 'class':['my-class','my-second-class']}

        """
        if 'class' not in kwargs:
            kwargs['class'] = []
        elif isinstance(kwargs['class'], str):
            kwargs['class'] = [kwargs['class']]
        kwargs['class'].append('img-fluid')

        s = _parse_style_class(kwargs)

        chart_id = "chart-" + str(uuid.uuid4())
        self.content += f"""<div {s} id='{chart_id}'></div>
            <script>var Plotjson = '{json}';
            var figure = JSON.parse(Plotjson);
            Plotly.newPlot('{chart_id}', figure.data, figure.layout);</script>"""

    def add_altair(self, json: str, **kwargs):
        """
        Add an Altair json to the document.
        :param json : an Altair json (chart.to_json()).
        :param kwargs: Additional CSS styles and html class to apply to the image. (optional)
        The keys should be in the format of CSS property names with '_' instead of '-', example: font_size
        you can also pass the class key with a string or a list of strings
        example : {'font_size': '20px', 'color': 'blue', 'class':'my-class'} or  {'font_size': '20px',
        'color': 'blue', 'class':['my-class','my-second-class']}

        """
        if 'class' not in kwargs:
            kwargs['class'] = []
        elif isinstance(kwargs['class'], str):
            kwargs['class'] = [kwargs['class']]
        kwargs['class'].append('img-fluid')

        s = _parse_style_class(kwargs)

        chart_id = "chart-" + str(uuid.uuid4())
        self.content += f"""<div {s} id='{chart_id}'></div>
        <script>var opt = {{renderer: "svg"}};
        vegaEmbed("#{chart_id}", {json} , opt);</script>"""

    def add_div(self, div: str, **kwargs):
        """
        Add a simple div.
        :param div : whatever you want that can fit in a div .
        :param kwargs: Additional CSS styles and html class to apply to the image. (optional)
        The keys should be in the format of CSS property names with '_' instead of '-', example: font_size
        you can also pass the class key with a string or a list of strings
        example : {'font_size': '20px', 'color': 'blue', 'class':'my-class'} or  {'font_size': '20px',
        'color': 'blue', 'class':['my-class','my-second-class']}
        """

        s = _parse_style_class(kwargs)
        self.content += f"""<div {s}>{div}</div>"""

    def render(self):
        """
        Return the complete HTML document as a string.
        """
        html = f"""<div>{self.content}</div>"""
        soup = BeautifulSoup(html, "html.parser")
        ident_content = soup.prettify()
        return ident_content
