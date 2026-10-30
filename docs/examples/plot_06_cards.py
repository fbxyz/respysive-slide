"""
Cards and title pages
=====================

Cards frame a title with a text, an image, or a chart. A split title page
puts the title on one side and any content on the other.
"""

import plotly.express as px

from respysive import Presentation, Slide

STYLE = """
:root {
  --r-heading-color: #1d3557;
  --r-heading-text-transform: none;
}
"""
px.defaults.template = "plotly_white"
px.defaults.color_discrete_sequence = ["#1d3557", "#e63946", "#457b9d", "#f4a261", "#2a9d8f"]

france = px.data.gapminder().query("country == 'France'")

# %%
# A split title page
# ------------------
#
# The right column takes any content, here a chart. ``full_height=True``
# makes both columns cover the slide.

curve = px.area(france, x="year", y="lifeExp", labels={"year": "", "lifeExp": ""}, range_y=[60, 85])
curve.update_traces(line_color="#e63946", fillcolor="rgba(230, 57, 70, 0.15)")
curve.update_layout(height=520, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)")

opening = Slide()
opening.add_split_title_page(
    {"title": "France in figures", "subtitle": "Life expectancy, 1952-2007", "authors": "Gapminder data"},
    custom_content=curve,
    title_column_width=5,
    custom_column_width=7,
    full_height=True,
    title_column_style={"background-color": "#1d3557", "padding": "50px"},
    title_styles=[
        {"font-size": "64px", "color": "#ffffff"},
        {"font-size": "34px", "color": "#a8dadc"},
        {"font-size": "26px", "color": "#f1faee"},
    ],
    custom_content_style={"background-color": "#ffffff", "padding": "30px"},
)

# %%
# Cards
# -----
#
# Each card is a dictionary: ``title``, ``text``, ``image``, or ``graph``.
# ``title_style`` and ``text_style`` set the CSS of its parts, and
# ``styles`` the classes or CSS of each card.

BIG = {"font-size": "140%", "color": "#e63946"}

trend = px.line(france, x="year", y="pop", markers=True, labels={"year": "", "pop": "Inhabitants"})
trend.update_layout(height=250, margin=dict(l=10, r=10, t=10, b=10))

cards = Slide()
cards.add_title("France, 1952-2007")
cards.add_card(
    [
        {"title": "80.7 years", "title_style": BIG, "text": "Life expectancy at birth in 2007, up from 67.4 in 1952."},
        {"title": "Population", "graph": trend},
        {"title": "61 million", "title_style": BIG, "text": "Inhabitants in 2007, up from 42 million in 1952."},
    ],
    styles=[{"class": "bg-light"}, {"class": "bg-light"}, {"class": "bg-light"}],
)

deck = Presentation()
deck.add_custom_css(STYLE)
deck.add_slide([opening, cards])
deck.save_html("cards.html", theme="white")
