"""
A first presentation
====================

Three slides on world health: a title page, a text slide written in
Markdown, and a chart with its comment. The whole deck is one HTML file
that opens in any browser.
"""

import plotly.express as px
from markdown import markdown

from respysive import Presentation, Slide

# %%
# A house style
# -------------
#
# The Reveal.js ``white`` theme gives the fonts. Three CSS variables give
# the colours and remove the capitals of the titles. Plotly charts follow
# with a white template and the same palette.

STYLE = """
:root {
  --r-heading-color: #1d3557;
  --r-heading-text-transform: none;
  --r-link-color: #e63946;
}
"""
PALETTE = ["#1d3557", "#e63946", "#457b9d", "#f4a261", "#2a9d8f"]
px.defaults.template = "plotly_white"
px.defaults.color_discrete_sequence = PALETTE

# %%
# Title page
# ----------
#
# ``add_title_page`` takes a title, a subtitle, and authors. ``styles``
# gives the CSS of each, in that order. The gradient is a slide background,
# which covers the whole screen.

title = Slide(center=True, **{"data-background-gradient": "linear-gradient(135deg, #1d3557, #457b9d)"})
title.add_title_page(
    {"title": "World health in 2007", "subtitle": "Life expectancy and income", "authors": "Gapminder data"},
    styles=[
        {"color": "#ffffff", "font-size": "88px"},
        {"color": "#a8dadc", "font-size": "44px"},
        {"color": "#f1faee", "font-size": "28px"},
    ],
)

# %%
# Text slide
# ----------
#
# Markdown is converted with the ``markdown`` package. The icon is a
# `Font Awesome <https://fontawesome.com/icons>`_ class.

text = Slide()
text.add_title("What the data cover", icon="fas fa-earth-africa")
text.add_content(
    [
        markdown(
            """
The Gapminder data set follows **142 countries** from 1952 to 2007,
every five years.

- Life expectancy at birth, in years
- GDP per capita, in US dollars adjusted for inflation
- Population
"""
        )
    ]
)
text.add_notes("The data set ships with Plotly: px.data.gapminder().")

# %%
# A chart and its comment
# -----------------------
#
# ``columns`` shares the 12 columns of the slide: 8 for the chart, 4 for
# the text. The chart stays interactive: hover a bubble to read the
# country.

df = px.data.gapminder().query("year == 2007")
fig = px.scatter(
    df,
    x="gdpPercap",
    y="lifeExp",
    size="pop",
    color="continent",
    hover_name="country",
    log_x=True,
    size_max=45,
    labels={"gdpPercap": "GDP per capita (USD, log scale)", "lifeExp": "Life expectancy (years)", "continent": ""},
)
fig.update_layout(height=540, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=1.08))

chart = Slide()
chart.add_title("Richer countries live longer")
chart.add_content(
    [
        fig,
        markdown("Japan leads with **82.6 years**.\n\nSwaziland comes last with **39.6 years**, 43 years less."),
    ],
    columns=[8, 4],
    styles=[None, {"font-size": "75%", "align-self": "center"}],
)

# %%
# Saving
# ------
#
# Slides are added in order, then ``save_html`` writes the file.

deck = Presentation()
deck.add_custom_css(STYLE)
deck.add_slide([title, text, chart])
deck.save_html("first_deck.html", theme="white")

# sphinx_gallery_thumbnail_number = 3
