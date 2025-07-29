from respysive.utils import _parse_style_class, process_markdown_with_latex
from respysive import Content
import os
import re
import json
from matplotlib.figure import Figure


def _check_content_type(col: str, shared_data_id=None):
    """
    Check if the content type is supported by the function

    :param col: The content type to check
    :type col: str
    """

    def _check_matplotlib(_col):
        """
        Check if the input is a Matplotlib figure

        :param _col: The input to check
        :type _col: matplotlib.figure.Figure
        """
        if isinstance(_col, Figure):
            return _col

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

        def _is_plotly_structure(data):

            if not isinstance(data, dict):
                return False

            if 'data' not in data:
                return False

            if not isinstance(data['data'], list):
                return False

            if len(data['data']) > 0:
                plotly_types = {
                    'scatter', 'bar', 'line', 'histogram', 'box', 'violin',
                    'heatmap', 'contour', 'surface', 'mesh3d', 'scatter3d',
                    'choropleth', 'scattergeo', 'pie', 'sunburst', 'treemap',
                    'sankey', 'waterfall', 'funnel', 'indicator', 'scattergl',
                    'histogram2d', 'histogram2dcontour', 'parcoords', 'parcats'
                }

                for trace in data['data']:
                    if isinstance(trace, dict) and 'type' in trace:
                        if trace['type'] in plotly_types:
                            return True
                    elif isinstance(trace, dict) and any(
                            key in trace for key in ['x', 'y', 'z', 'locations', 'values']):
                        return True

            return 'layout' in data

        if isinstance(_col, str):
            try:
                parsed_data = json.loads(_col)
                return _is_plotly_structure(parsed_data)
            except (json.JSONDecodeError, ValueError):
                return '{"data":[{' in col or '"data":' in _col

        elif isinstance(_col, dict):
            return _is_plotly_structure(_col)

        else:
            try:
                if hasattr(_col, 'to_json') and hasattr(_col, 'data') and hasattr(_col, 'layout'):
                    return True
            except:
                pass

        return False

    center = {'class': ['d-flex', 'justify-content-center', 'mx-auto']}

    img_list = ['.jpg', '.jpeg', '.png', '.gif', '.tif', '.apng', '.bmp', '.svg']

    if _check_matplotlib(col):
        c = Content()
        c.add_fig(col, **center)
        col = c.render()

    elif os.path.isfile(col):
        if os.path.splitext(col)[1].lower() in img_list:
            c = Content()
            c.add_image(col, **center)
            col = c.render()
    elif re.match(
            r'(http(s)?:\/\/.)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)',
            col):
        if re.search(r'\.(jpg|jpeg|png|gif|tif|apng|bmp|svg)', col, re.IGNORECASE):
            c = Content()
            c.add_image(col, **center)
            col = c.render()

    elif _check_altair(col):
        c = Content()
        c.add_altair(col, **center)
        col = c.render()

    elif _check_plotly(col):
        c = Content()
        c.add_plotly(col, shared_data_id=shared_data_id, **center)
        col = c.render()

    else:
        if ('$' in col or '#' in col or '*' in col or '_' in col or '[' in col) and not ('\\(' in col or '\\[' in col):
            processed_text = process_markdown_with_latex(col)
            c = Content()
            c.add_div(processed_text)
            col = c.render()
        else:
            c = Content()
            if '\\(' in col or '\\[' in col or '<' in col:
                c.add_div(col)
            else:
                c.add_text(col)
            col = c.render()
    return col


def _check_content_type_with_shared_data(col, shared_data_id, content_obj):
    """

    """
    center = {'class': ['d-flex', 'justify-content-center', 'mx-auto']}
    img_list = ['.jpg', '.jpeg', '.png', '.gif', '.tif', '.apng', '.bmp', '.svg']

    def _check_matplotlib(_col):
        if isinstance(_col, Figure):
            return _col

    def _check_altair(_col):
        if isinstance(_col, str):
            return "https://vega.github.io/schema/vega-lite" in _col
        elif isinstance(_col, dict):
            _col = json.dumps(_col)
            return "https://vega.github.io/schema/vega-lite" in _col

    def _check_plotly(_col):
        def _is_plotly_structure(data):
            if not isinstance(data, dict):
                return False
            if 'data' not in data:
                return False
            if not isinstance(data['data'], list):
                return False
            return 'layout' in data

        if isinstance(_col, str):
            try:
                parsed_data = json.loads(_col)
                return _is_plotly_structure(parsed_data)
            except (json.JSONDecodeError, ValueError):
                return '{"data":[{' in col or '"data":' in _col
        elif isinstance(_col, dict):
            return _is_plotly_structure(_col)
        else:
            try:
                if hasattr(_col, 'to_json') and hasattr(_col, 'data') and hasattr(_col, 'layout'):
                    return True
            except:
                pass
        return False


    if _check_matplotlib(col):
        temp_content = Content()
        temp_content.add_fig(col, **center)
        col = temp_content.render()
    elif _check_plotly(col):
        temp_content = Content()
        temp_content.shared_data = content_obj.shared_data
        temp_content.add_plotly(col, shared_data_id=shared_data_id, **center)
        col = temp_content.render()
    elif _check_altair(col):
        temp_content = Content()
        temp_content.add_altair(col, **center)
        col = temp_content.render()
    elif isinstance(col, str) and os.path.isfile(col):
        if os.path.splitext(col)[1].lower() in img_list:
            temp_content = Content()
            temp_content.add_image(col, **center)
            col = temp_content.render()
    elif isinstance(col, str) and re.match(
            r'(http(s)?:\/\/.)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)',
            col):
        if re.search(r'\.(jpg|jpeg|png|gif|tif|apng|bmp|svg)', col, re.IGNORECASE):
            temp_content = Content()
            temp_content.add_image(col, **center)
            col = temp_content.render()
    elif isinstance(col, str):
        if ('$' in col or '#' in col or '*' in col or '_' in col or '[' in col) and not ('\\(' in col or '\\[' in col):
            processed_text = process_markdown_with_latex(col)
            temp_content = Content()
            temp_content.add_div(processed_text)
            col = temp_content.render()
        else:
            temp_content = Content()
            if '\\(' in col or '\\[' in col or '<' in col:
                temp_content.add_div(col)
            else:
                temp_content.add_text(col)
            col = temp_content.render()
    else:
        # Fallback pour les types non supportés
        temp_content = Content()
        temp_content.add_div(str(col))
        col = temp_content.render()
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
        self.content_obj = Content()

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

    def add_content(self, content: list, columns=None, styles: list = None, shared_data_ids: list = None):
        """
        Add content to the slide.

        :param content: List of content items to add (strings, figures).
        :param columns: List of integers representing the column size for each item.
                       Defaults to [12] if not provided.
        :param styles: List of style dictionaries to apply to each content item.
                       The length must match the length of the 'content' list.
        :param shared_data_ids: List of shared data IDs to use for each content item.
                               None values will use normal rendering.
        """

        if columns is None:
            columns = [12] * len(content)
        elif len(columns) == 1 and len(content) > 1:
            columns = columns * len(content)

        _check_styles(styles, content, columns)

        row = "<div class='row'>"
        for i in range(len(content)):
            col = content[i]
            shared_data_id = shared_data_ids[i] if shared_data_ids and i < len(shared_data_ids) else None

            col = _check_content_type_with_shared_data(col, shared_data_id, self.content_obj)
            if styles and len(styles) > i:
                col = f"<div class='col-md-{columns[i]} responsive-text' {_parse_style_class(styles[i])}>{col}</div>"
            else:
                col = f"<div class='col-md-{columns[i]} responsive-text'>{col}</div>"
            row += col
        self.content += row + "</div>"

    def add_card(self, cards: list, styles: list = None):
        """
        Add a card with a title and a content, to the slide.
        :param cards: list of dictionaries that contains the following keys: 'title', 'content', 'image'
        :param styles: list of dictionaries that contains the css styles for each card. The keys of the dictionaries are: 'title', 'content', 'image'
        """

        _check_styles(styles, cards)

        if styles is None:
            styles = [{'class': 'bg-info'}] * len(cards)

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

    def add_title_page(self, title_page_content: dict, styles: list = None, title_page_class: str = ""):
        """
        Add a title page to the slide
        :param title_page_content: dictionary that contains the following keys: 'title', 'subtitle', 'authors', 'logo'
        :param styles: list of dictionaries that contains the css styles for each element of the title page. The keys of the dictionaries are: 'title', 'subtitle', 'authors', 'logo'
        :param title_page_class: additional CSS class for the title-page div
        """

        title = title_page_content.get('title', '')
        subtitle = title_page_content.get('subtitle', '')
        authors = title_page_content.get('authors', '')
        logo = title_page_content.get('logo', '')

        present_elements = []
        if title: present_elements.append('title')
        if subtitle: present_elements.append('subtitle') 
        if authors: present_elements.append('authors')
        if logo: present_elements.append('logo')

        if styles and len(styles) != len(present_elements):
            raise ValueError(f"styles must have {len(present_elements)} elements (one for each present element: {present_elements})")

        if styles is None:
            styles = []

        style_idx = 0
        title_s = _parse_style_class(styles[style_idx]) if styles and title else ""
        if title and styles: style_idx += 1
        
        subtitle_s = _parse_style_class(styles[style_idx]) if styles and subtitle else ""
        if subtitle and styles: style_idx += 1
        
        authors_s = _parse_style_class(styles[style_idx]) if styles and authors else ""
        if authors and styles: style_idx += 1
        
        logo_s = _parse_style_class(styles[style_idx]) if styles and logo else ""

        title_html = f'<div class="row"><div class="col-12"><h2 {title_s}">{title}</h2></div></div>' if title else ''
        subtitle_html = f'<div class="row"><div class="col-12"><h3 {subtitle_s}">{subtitle}</h3></div></div>' if subtitle else ''
        authors_html = f'<div class="col-9"><h4 {authors_s}">{authors}</h3></div>' if authors else ''
        logo_html = f'<div class="col-3 "><img src="{logo}" {logo_s}"></div>' if logo else ''
        authors_logo_html = f'<div class="row align-items-center">{authors_html}{logo_html}</div>'

        page_class = f'title-page {title_page_class}'.strip()
        title_page_html = f'<div class="{page_class}">{title_html}{subtitle_html}{authors_logo_html}</div>'
        self.content += title_page_html

    def add_split_title_page(self, title_page_content: dict, custom_content, 
                       title_column_width: int = 6, custom_column_width: int = 6,
                       title_page_class: str = "", custom_content_style: dict = None,
                       title_styles: list = None, title_column_style: dict = None):
        """
        Add a split title page with two Bootstrap columns - one for title content, one for custom content.
        
        :param title_page_content: Dictionary with keys 'title', 'subtitle', 'authors', 'logo' (all optional)
        :param custom_content: Content to display in the second column (string, figure, image, etc.)
        :param title_column_width: Width of the title column (1-12, default 6)
        :param custom_column_width: Width of the custom content column (1-12, default 6) 
        :param title_page_class: Additional CSS class for the title-page div
        :param custom_content_style: Style dictionary for the custom content column
        :param title_styles: List of style dictionaries for title elements (title, subtitle, authors, logo)
        :param title_column_style: Style dictionary for the title column container
        """
        
        if title_column_width + custom_column_width > 12:
            raise ValueError("Sum of column widths cannot exceed 12")
            
        title = title_page_content.get('title', '')
        subtitle = title_page_content.get('subtitle', '')
        authors = title_page_content.get('authors', '')
        logo = title_page_content.get('logo', '')

        present_elements = []
        if title: present_elements.append('title')
        if subtitle: present_elements.append('subtitle') 
        if authors: present_elements.append('authors')
        if logo: present_elements.append('logo')

        if title_styles and len(title_styles) != len(present_elements):
            raise ValueError(f"title_styles must have {len(present_elements)} elements (one for each present element: {present_elements})")

        if title_styles is None:
            title_styles = []

        style_idx = 0
        title_s = _parse_style_class(title_styles[style_idx]) if title_styles and title else ""
        if title and title_styles: style_idx += 1
        
        subtitle_s = _parse_style_class(title_styles[style_idx]) if title_styles and subtitle else ""
        if subtitle and title_styles: style_idx += 1
        
        authors_s = _parse_style_class(title_styles[style_idx]) if title_styles and authors else ""
        if authors and title_styles: style_idx += 1
        
        logo_s = _parse_style_class(title_styles[style_idx]) if title_styles and logo else ""

        title_html = f'<h2 {title_s}>{title}</h2>' if title else ''
        subtitle_html = f'<h3 {subtitle_s}>{subtitle}</h3>' if subtitle else ''
        
        if authors and logo:
            authors_logo_html = f'''
                <div class="row align-items-center">
                    <div class="col-9"><h4 {authors_s}>{authors}</h4></div>
                    <div class="col-3"><img src="{logo}" {logo_s}></div>
                </div>'''
        elif authors:
            authors_logo_html = f'<h4 {authors_s}>{authors}</h4>'
        elif logo:
            authors_logo_html = f'<img src="{logo}" {logo_s}>'
        else:
            authors_logo_html = ''

        title_content_html = f'{title_html}{subtitle_html}{authors_logo_html}'
        
        processed_custom_content = _check_content_type(custom_content)
        
        default_title_column_style = {'color': 'white', 'padding': '30px'}
        if title_column_style:
            default_title_column_style.update(title_column_style)
        title_column_style_attr = _parse_style_class(default_title_column_style)
        
        default_custom_style = {'background-color': 'white', 'padding': '30px'}
        if custom_content_style:
            default_custom_style.update(custom_content_style)
        custom_style_attr = _parse_style_class(default_custom_style)
        
        page_class = f'title-page {title_page_class}'.strip()
        
        split_html = f'''
        <div class="{page_class}">
            <div class="row">
                <div class="col-md-{title_column_width}" {title_column_style_attr}>
                    {title_content_html}
                </div>
                <div class="col-md-{custom_column_width}" {custom_style_attr}>
                    {processed_custom_content}
                </div>
            </div>
        </div>'''
        
        self.content += split_html
