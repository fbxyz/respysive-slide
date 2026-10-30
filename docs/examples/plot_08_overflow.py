"""
Content taller than the slide
=============================

A slide is 1280 x 720 pixels. When its content is taller, respysive fits
it: the text shrinks first, down to 60% of its size, then the whole
content scales down. The layout stays the same on screen, in PDF, and in
PowerPoint.
"""

import plotly.express as px

from respysive import Presentation, Slide

STYLE = """
:root {
  --r-heading-color: #1d3557;
  --r-heading-text-transform: none;
}
.reveal table { font-size: 22px; }
"""
px.defaults.template = "plotly_white"

latest = px.data.gapminder().query("year == 2007")
table = (
    latest.nlargest(15, "pop")[["country", "continent", "pop", "lifeExp"]]
    .assign(pop=lambda d: (d["pop"] / 1e6).round(1), lifeExp=lambda d: d["lifeExp"].round(1))
    .rename(columns={"country": "Country", "continent": "Continent", "pop": "Population (millions)", "lifeExp": "Life expectancy"})
    .set_index("Country")
)

# %%
# A long table
# ------------
#
# Fifteen rows do not fit at full size. The text shrinks until they do,
# while the title keeps its size. A pandas ``DataFrame`` is inserted as an
# HTML table.

long = Slide()
long.add_title("The fifteen most populated countries, 2007")
long.add_content([table])

# %%
# A table next to a chart
# -----------------------
#
# Shrinking the text is not enough when a chart is tall too. The whole
# content then scales down, like a picture, and keeps its layout.

bars = px.bar(
    latest.nlargest(15, "pop").sort_values("lifeExp"),
    x="lifeExp",
    y="country",
    orientation="h",
    color_discrete_sequence=["#457b9d"],
    labels={"lifeExp": "Life expectancy (years)", "country": ""},
)
bars.update_layout(height=640, margin=dict(l=10, r=10, t=10, b=10))

both = Slide()
both.add_title("Population and life expectancy")
both.add_content([table, bars], columns=[7, 5])

# %%
# The fitting can be turned off with ``Slide(overflow="visible")``, or
# reported in the browser console only with ``overflow="warn"``.
# ``save_html(overflow=...)`` sets the behaviour of every slide.

deck = Presentation()
deck.add_custom_css(STYLE)
deck.add_slide([long, both])
deck.save_html("overflow.html", theme="white")

# sphinx_gallery_thumbnail_number = 2
