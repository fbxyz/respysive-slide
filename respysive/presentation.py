from bs4 import BeautifulSoup


def create_slide_html(slide):
    if isinstance(slide, list):
        return "<section>" + "\n".join([create_slide_html(subslide) for subslide in slide]) + "</section>"

    kwargs_str = ' '.join([f'{k}="{v}"' for k, v in slide.kwargs.items()])
    return f"""<section {kwargs_str} class='{'center' if slide.center else ''}'>
        <div class='container' style='text-align: left;' >
            {slide.content}
        </div>
    </section>"""


class Presentation:
    """
    A class representing a presentation.
    """
    def __init__(self):
        self.slides = []

    def add_slide(self, slide):
        """
        Add a slide to the presentation.

        :param slide: The slide object to add to the presentation.
        """
        if isinstance(slide, list):
            for sl in slide:
                self.slides.append(sl)
        else:
            self.slides.append(slide)

    def to_html(self, theme="moon", width=960, height=600, minscale=0.2, maxscale=1.5, margin=0.1):
        """
        Generate the HTML code for the presentation.

        :param theme: The name of the theme to use for the presentation. Default is "moon".
        :param width: The width of the presentation in pixels. Default is 960.
        :param height: The height of the presentation in pixels. Default is 600.
        :param minscale: The minimum scale at which the presentation can be viewed. Default is 0.2.
        :param maxscale: The maximum scale at which the presentation can be viewed. Default is 1.5.
        :param margin: The margin around the presentation in percentage. Default is 0.1.
        :return: A string containing the HTML code for the presentation.
        """

        css_links = [
            "https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.4.0/reveal.min.css",
            f"https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.4.0/theme/{theme}.min.css",
            "https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css",
            "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css"
        ]
        js_links = [
            "https://cdn.jsdelivr.net/npm/vega@5",
            "https://cdn.jsdelivr.net/npm/vega-lite@5",
            "https://cdn.jsdelivr.net/npm/vega-embed@6",
            "https://cdn.plot.ly/plotly-2.17.1.min.js"
        ]

        css_links = "\n".join([f"<link href='{link}' rel='stylesheet'>" for link in css_links])
        js_links = "\n".join([f"<script src='{link}' type='text/javascript'></script>" for link in js_links])

        slides_html = "\n".join([create_slide_html(slide) for slide in self.slides])

        presentation_html = f"""
    <html>
     <head>
      <meta charset="UTF-8">
      {css_links}
      <style type='text/css'>svg{{max-width: 100%;}}</style>
      {js_links}
     </head>
     <body>
        <div class='reveal'>
            <div class='slides'>
                {slides_html}
            </div>
        </div>
        <!--Correction to allow transition between slides-->
        <style type='text/css'>[hidden] {{display: inherit !important;}}</style>
        <script src='https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.4.0/reveal.min.js'></script>
        <script>
         Reveal.initialize(
                    {{center: false,
                     pdfMaxPagesPerSlide: 1,
                     pdfSeparateFragments: false,
                     disableLayout: false,
                     slideNumber: 'c/t',  
                     
                    // The "normal" size of the presentation, aspect ratio will be preserved
                    // when the presentation is scaled to fit different resolutions. Can be
                    // specified using percentage units.
                    width: {width},
                    height: {height},
                    display:'block',
                
                    // Factor of the display size that should remain empty around the content
                    margin: {margin},
                
                    // Bounds for smallest/largest possible scale to apply to content
                    minScale: {minscale},
                    maxScale: {maxscale},
                    }});
        </script>
     </body>
    </html>"""
        soup = BeautifulSoup(presentation_html, "html.parser")

        return presentation_html

    def save_html(self, file_name, theme="moon", width=960, height=600, minscale=0.2, maxscale=1.5, margin=0.1):
        """
        Save the presentation in HTML format.

        :param file_name: The name of the file to save the HTML content to.
        :param theme: The name of the theme to use for the presentation. Default is "moon".
        :param width: The width of the presentation in pixels. Default is 960.
        :param height: The height of the presentation in pixels. Default is 600.
        :param minscale: The minimum scale at which the presentation can be viewed. Default is 0.2.
        :param maxscale: The maximum scale at which the presentation can be viewed. Default is 1.5.
        :param margin: The margin around the presentation in percentage. Default is 0.1.
        """
        presentation_html = self.to_html(theme=theme, width=width, height=height, minscale=minscale, maxscale=maxscale,
                                         margin=margin)

        with open(file_name, "w") as f:
            f.write(presentation_html)
