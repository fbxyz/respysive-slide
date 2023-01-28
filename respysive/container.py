from respysive.utils import _parse_style_class
from respysive import Content
import os
import re
import json


def _check_content_type(col: str):
    """
    Check if the content type is supported by the function

    :param col: The content type to check
    :type col: str
    """
    def _check_altair(_col):
        """
        Check if the input is a Altair chart

        :param chart: The chart to check
        :type chart: altair.vegalite.v3.api.Chart
        """
        if isinstance(_col, str):
            return "https://vega.github.io/schema/vega-lite" in _col
        elif isinstance(_col, dict):
            _col = json.dumps(_col)
            return "https://vega.github.io/schema/vega-lite" in _col

    def _check_plotly(_col):
        """
        Check if the input is a Plotly chart

        :param chart: The chart to check
        :type chart: plotly.graph_objs._figure.Figure
        """
        if isinstance(_col, str):
            return """{"data":[{"customdata""" in _col
        elif isinstance(_col, dict):
            _col = json.dumps(_col)
            return """{"data":[{"customdata""" in _col

    center = {'class': ['d-flex', 'justify-content-center', 'mx-auto']}

    if os.path.isfile(col):
        if os.path.splitext(col)[1].lower() in ['.jpg', '.jpeg', '.png', '.gif', '.tif', '.apng', '.bmp', '.svg']:
            c = Content()
            c.add_image(col, **center)
            col = c.render()
    elif re.match(
            r'(http(s)?:\/\/.)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)',
            col):
        if re.search(r'\.(jpg|jpeg|png|gif|tif|apng|bmp|svg)', col):
            c = Content()
            c.add_image(col, **center)
            col = c.render()

    elif _check_altair(col):
        c = Content()
        c.add_altair(col, **center)
        col = c.render()

    elif _check_plotly(col):
        c = Content()
        c.add_plotly(col, **center)
        col = c.render()

    else:
        c = Content()
        c.add_text(col)
        col = c.render()

    return col


def _add_list_classes(text: str):
    """
    Add 'list-classes' class to <ul> and <ol> tags in the text.
    :param text: str, the text where the class should be added
    :return: str, the text with the class added
    """
    text = re.sub(r'<ul>', '<ul class="list-group list-group-flush">', text)
    text = re.sub(r'<li>', '<li class="list-group-item" style="background-color: transparent;" >', text)
    return text


def _append_class(_style, _class):
    """
    Append a class to the style dictionary.
    :param _style: dict, the style dictionary
    :param _class: str, the class to append
    :return: dict, the style dictionary with the class appended
    """
    if 'class' not in _style:
        _style['class'] = []
    elif isinstance(_style['class'], str):
        _style['class'] = [_style['class']]
    _style['class'].append(_class)
    return _style


def _append_style(_style, _style_to_append):
    """
    Append a style to the style dictionary.
    :param _style: dict, the style dictionary
    :param _style_to_append: dict, the style to append
    :return: dict, the style dictionary with the style appended
    """
    _style.update(_style_to_append)
    return _style


def _check_styles(styles, *args):
    """
    Check the styles for each element.
    :param styles: list, a list of styles, one for each element
    :param args: list, a list of elements
    :return: list, a list of styles with the same length as the elements, with default styles for missing elements
    """
    if styles is None:
        styles = [{} for _ in range(len(args[0]))]
    for i, arg in enumerate(args):
        if len(arg) != len(styles):
            raise ValueError(f"{arg} and styles must have the same length")


class Slide:
    """
    A class representing a slide in a presentation.
    """
    def __init__(self, center=False, **kwargs):
        self.content = ""
        self.center = center
        self.kwargs = kwargs

    def add_title(self, text: str, tag: str = "h3", icon: str = None, **kwargs):
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
        c = Content()
        c.add_heading(text, tag, icon, **kwargs)


        row = "<div class='row'><div class='col-12 mx-auto'>"
        self.content += row + c.render() + "</div></div>"

    def add_content(self, content: list, columns=None, styles: list = None):
        """
        Add content to the slide
        :param content : list of strings
        :param columns : list of int representing the size of each column
        :param kwargs : list of additional css styles to apply to each column
        """

        if columns is None:
            columns = [12]

        _check_styles(styles, content, columns)

        row = "<div class='row'>"
        for i in range(len(content)):
            col = content[i]
            if isinstance(col, str):
                col = _check_content_type(col)
                if styles and len(styles) > i:
                    col = f"<div class='col-md-{columns[i]}' {_parse_style_class(styles[i])}>{col}</div>"
                else:
                    col = f"<div class='col-md-{columns[i]}'>{col}</div>"
            row += col
        self.content += row + "</div>"

    def add_card(self, cards: list, styles: list = None):
        """
        Add a card with a title and a content, to the slide.
        :param cards: list of dictionaries that contains the following keys: 'title', 'content', 'image'
        :param styles: list of dictionaries that contains the css styles for each card. The keys of the dictionaries are: 'title', 'content', 'image'
        """

        _check_styles(styles, cards)

        cards_html = ""
        for card, style in zip(cards, styles):
            if 'class' not in style:
                style['class'] = []
            elif isinstance(style['class'], str):
                style['class'] = [style['class']]
            style['class'].append('card h-100')

            s = _parse_style_class(style)
            card_html = ""
            for key in card.keys():
                if key == 'image':
                    card_html += f'<img src="{card[key]}" class="card-img-top mx-auto" alt="">'
                elif key == 'title':
                    card_html += f'<h4 class="card-title">{card[key]}</h4>'
                elif key == 'text':
                    card[key] = _add_list_classes(card[key])
                    card_html += f'<p class="card-text" style="font-size:60%">{card[key]}</p>'
            cards_html += f"""
            <div class="col">
                <div {s}> 
                    {card_html}
                </div>
            </div>"""
        self.content += f"<div class='row'>{cards_html}</div>"

    def add_title_page(self, title_page_content: dict, styles: list = None):
        """
        Add a title page to the slide
        :param title_page_content: dictionary that contains the following keys: 'title', 'subtitle', 'authors', 'logo'
        :param styles: list of dictionaries that contains the css styles for each element of the title page. The keys of the dictionaries are: 'title', 'subtitle', 'authors', 'logo'
        """

        title = title_page_content.get('title', '')
        subtitle = title_page_content.get('subtitle', '')
        authors = title_page_content.get('authors', '')
        logo = title_page_content.get('logo', '')

        _check_styles(styles, title_page_content)

        title_s = _parse_style_class(styles[0])
        subtitle_s = _parse_style_class(styles[1])
        authors_s = _parse_style_class(styles[2])
        logo_s = _parse_style_class(styles[3])

        title_html = f'<div class="row"><div class="col-12"><h1 {title_s}">{title}</h1></div></div>' if title else ''
        subtitle_html = f'<div class="row"><div class="col-12"><h2 {subtitle_s}">{subtitle}</h2></div></div>' if subtitle else ''
        authors_html = f'<div class="col-9"><h4 {authors_s}">{authors}</h3></div>' if authors else ''
        logo_html = f'<div class="col-3 "><img src="{logo}" {logo_s}"></div>' if logo else ''
        authors_logo_html = f'<div class="row align-items-center">{authors_html}{logo_html}</div>'

        title_page_html = f'<div class="title-page">{title_html}{subtitle_html}{authors_logo_html}</div>'
        self.content += title_page_html
