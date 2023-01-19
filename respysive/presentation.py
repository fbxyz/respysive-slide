from bs4 import BeautifulSoup


class Presentation:
    def __init__(self, theme="white", custom_theme_url=None):
        self.presentation_html = "<html><head>"
        self.presentation_html += '</head><body><div class="reveal">'
        self.presentation_html += '<div class="slides">'
        self.theme = theme
        self.custom_theme_url = custom_theme_url

    def add_slide(self, container: list):
        for i in container:
            self.presentation_html += i.render()

    def render_presentation(self, theme: str = "white", custom_theme_url=None):
        self.presentation_html += "</div></div></body></html>"

        reveal_css = BeautifulSoup(
            '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.4.0/reveal.min.css">',
            "html.parser")

        revealtheme_css = (
            BeautifulSoup(f"""<link rel="stylesheet" href="{custom_theme_url}">""")
            if theme == "custom"
            else BeautifulSoup(
                f"""<link rel="stylesheet" 
                href="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.4.0/theme/{theme}.min.css"> """,
                "html.parser")
        )

        reveal_js = BeautifulSoup(
            """<script src=https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.4.0/reveal.min.js></script>""",
            "html.parser")

        plotly_js = BeautifulSoup(
            """<script src="https://cdn.plot.ly/plotly-2.17.1.min.js"></script>""", "html.parser"
        )

        altair_js = BeautifulSoup("""<script type="text/javascript" src="https://cdn.jsdelivr.net/npm/vega@5"></script>
            <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/vega-lite@5"></script>
            <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>""",
                                  "html.parser")

        bootstrap_css = BeautifulSoup(
            "<link rel='stylesheet' href='https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css'>",
            "html.parser")

        bootstrap_correction = BeautifulSoup(
            """
            <!--Correction to allow transition between slides-->
            <style type="text/css">[hidden] {display: inherit !important;}</style>""", "html.parser")

        fontawesome_css = BeautifulSoup(
            "<link rel='stylesheet' href='https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css'>",
            "html.parser")

        svg_width = BeautifulSoup("<style type='text/css'>svg{max-width: 100%;}</style>", "html.parser")

        reveal_init = BeautifulSoup(
            """<script>Reveal.initialize(
            {center: false,
             pdfMaxPagesPerSlide: 1,
             pdfSeparateFragments: false,
             disableLayout: false,
             slideNumber: true,  
            });</script>""", "html.parser")

        soup = BeautifulSoup(self.presentation_html, "html.parser")
        head = soup.head
        head.append(reveal_css)
        head.append(revealtheme_css)
        head.append(bootstrap_css)
        head.append(fontawesome_css)
        head.append(svg_width)
        head.append(altair_js)
        head.append(plotly_js)

        body = soup.body
        body.append(bootstrap_correction)
        body.append(reveal_js)
        body.append(reveal_init)
        return soup.prettify(formatter="html5")
