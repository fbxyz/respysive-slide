"""
Themes and backgrounds
======================

A Reveal.js theme sets the fonts and colours, custom CSS adjusts them, and
``data-background-*`` arguments give a slide its own background, which
covers the whole window on screen.
"""

import plotly.express as px
from markdown import markdown

from respysive import Presentation, Slide

# %%
# A dark deck
# -----------
#
# The ``night`` theme is dark. Reveal.js themes read CSS variables such as
# ``--r-background-color``, so redefining them recolours every slide. A
# slide class (``branded``) lets the CSS add a label to some slides only.

CSS = """
:root {
  --r-background-color: #0b2545;
  --r-main-color: #eef4ed;
  --r-heading-color: #ffffff;
  --r-heading-text-transform: none;
}
.reveal .slides section.branded::after {
  content: "World health, 2007";
  position: absolute;
  right: 30px;
  bottom: 18px;
  font-size: 18px;
  opacity: 0.6;
}
"""

df = px.data.gapminder().query("year == 2007")
fig = px.box(
    df,
    x="continent",
    y="lifeExp",
    color="continent",
    points="all",
    template="plotly_dark",
    color_discrete_sequence=["#8da9c4", "#f4a261", "#e63946", "#2a9d8f", "#eef4ed"],
    labels={"continent": "", "lifeExp": "Life expectancy (years)"},
)
fig.update_layout(height=500, margin=dict(l=10, r=10, t=10, b=10), showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")

dark = Slide(**{"class": "branded"})
dark.add_title("Life expectancy by continent")
dark.add_content([fig])

# %%
# Slide backgrounds
# -----------------
#
# A colour, a gradient, or an image. Images are embedded in the HTML file,
# and ``data-background-opacity`` dims them behind the text.

gradient = Slide(
    center=True, **{"data-background-gradient": "linear-gradient(135deg, #0b2545 0%, #8da9c4 100%)"}
)
gradient.add_title("A gradient background", tag="h2")
gradient.add_content([markdown("`data-background-gradient` takes any CSS gradient.")])

image = Slide(
    center=True,
    **{
        "data-background-image": "data/fractal.jpg",
        "data-background-size": "cover",
        "data-background-opacity": "0.35",
    },
)
image.add_title("An image background", tag="h2")
image.add_content([markdown("`data-background-image` takes a path or a URL.")])

deck = Presentation()
deck.add_custom_css(CSS)
deck.add_slide([dark, gradient, image])
deck.save_html("theme.html", theme="night", transition="fade")
