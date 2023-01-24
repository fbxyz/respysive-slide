from bs4 import BeautifulSoup
from respysive.utils import _parse_style_class


class Container:
    def __init__(self, center=False, text_align='left'):

        div = f"""<section class="center"><div class="container" style="text-align: {text_align};" >""" \
            if center else f"""<section><div class="container" style="text-align: {text_align};" >"""
        self.container_html = div
        self.open_row = False
        self.col_count = 0

    def __enter__(self):
        self._add_row()
        return self

    def __exit__(self, *args):
        self._close_row()

    def _add_row(self, **kwargs):
        dic = kwargs

        for key, value in dic.items():
            if key == 'class':
                if isinstance(value, str):
                    dic[key] = [value]
                    dic[key].append("row")
        if 'class' not in dic:
            dic['class'] = ['row']

        s = _parse_style_class(dic)

        self.container_html += f"<div {s}>"
        self.open_row = True
        self.col_count = 0

    def add_col(self, content: str, col_class: str = "col-12", **kwargs):
        if not self.open_row:
            raise ValueError("You must open a row before adding a column")
        col_size = int(col_class.split("-")[-1])
        if self.col_count + col_size > 12:
            raise ValueError("Total number of columns in a row must not exceed 12")
        if 'class' not in kwargs:
            kwargs['class'] = []
        elif isinstance(kwargs['class'], str):
            kwargs['class'] = [kwargs['class']]
        kwargs['class'].append(col_class)
        s = _parse_style_class(kwargs)
        self.container_html += f'<div {s}>{content}</div> '
        self.col_count += col_size

    def _close_row(self):
        if self.open_row:
            self.container_html += "</div>"
            self.open_row = False
            self.col_count = 0

    def _close_container(self):
        self.container_html += "</div></section>"

    def render(self):
        self._close_container()
        html = f"""{self.container_html}"""
        soup = BeautifulSoup(html, "html.parser")
        return soup.prettify()


class SubSlides:
    def __init__(self):
        self.sub_slides = []

    def add_sub_slide(self):
        sub_slide = Container()
        self.sub_slides.append(sub_slide)
        return sub_slide

    def _add_section(self):
        self.html = "<section>"

    def _close_section(self):
        self.html += "</section>"

    def render(self):
        self._add_section()
        for sub_slide in self.sub_slides:
            self.html += sub_slide.render()
        self._close_section()
        return self.html
