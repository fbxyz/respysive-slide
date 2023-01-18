from bs4 import BeautifulSoup


class Container:
    def __init__(self, center=False):

        div = """<section class="center"><div class="container">""" if center else """<section><div class="container">"""
        self.container_html = div
        self.open_row = False
        self.col_count = 0

    def __enter__(self):
        self.add_row()
        return self

    def __exit__(self, *args):
        self.close_row()

    def add_row(self):
        self.container_html += """\n<!-- New Row -->\n<div class="row">"""
        self.open_row = True
        self.col_count = 0

    def add_col(
            self,
            content: str,
            col_class: str,
            **kwargs
    ):
        if not self.open_row:
            raise ValueError("You must open a row before adding a column")
        col_size = int(col_class.split("-")[-1])
        if self.col_count + col_size > 12:
            raise ValueError("Total number of columns in a row must not exceed 12")
        style_str = ""
        for key, value in kwargs.items():
            css_key = key.replace("_", "-")
            style_str += f"{css_key}: {value};"

        self.container_html += f'<div class="col {col_class}" style="{style_str}">{content}</div> '
        self.col_count += col_size

    def close_row(self):
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
