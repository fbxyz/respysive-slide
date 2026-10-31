"""
Fragments, notes, and vertical slides
=====================================

Fragments show the content of a slide one step at a time: click the deck,
then press the right arrow to reveal each step. Speaker notes appear in
the speaker view (press ``S``). Slides grouped in a list form a vertical
stack, reached with the down arrow.
"""

import plotly.express as px
from markdown import markdown

from respysive import Column, Presentation, Row, Slide

STYLE = """
:root {
  --r-heading-color: #1d3557;
  --r-heading-text-transform: none;
}
"""
px.defaults.template = "plotly_white"
px.defaults.color_discrete_sequence = ["#1d3557", "#e63946", "#457b9d", "#f4a261", "#2a9d8f"]

gapminder = px.data.gapminder()
life = gapminder.pivot(index="year", columns="country", values="lifeExp")
first_year, last_year = life.index.min(), life.index.max()
weighted = gapminder.groupby("year").apply(lambda d: (d["lifeExp"] * d["pop"]).sum() / d["pop"].sum())


def bubbles(year):
    data = gapminder.query("year == @year")
    fig = px.scatter(
        data,
        x="gdpPercap",
        y="lifeExp",
        size="pop",
        color="continent",
        hover_name="country",
        log_x=True,
        size_max=45,
        range_x=[200, 120000],
        range_y=[25, 90],
        title=str(year),
        labels={"gdpPercap": "GDP per capita (USD, log scale)", "lifeExp": "Life expectancy (years)", "continent": ""},
    )
    fig.update_layout(height=500, margin=dict(l=10, r=10, t=50, b=10), title_font_size=26)
    return fig


# %%
# One step at a time
# ------------------
#
# ``fragment_items`` reveals the items of a list one by one, and
# ``fragment`` reveals a whole item. A string picks the effect (``fade-up``,
# ``highlight-red``, and others).

steps = Slide()
steps.add_title("Each bubble is a country, sized by its population")
steps.add_content(
    [
        markdown(
            "- One bubble per country\n"
            "- Area proportional to the population\n"
            "- Income runs from left to right\n"
            "- Life expectancy runs upwards"
        ),
        bubbles(2007),
    ],
    columns=[4, 8],
    styles=[{"font-size": "80%", "align-self": "center"}, None],
    fragment_items=["fade-up", None],
    fragment=[None, True],
)
steps.add_notes("Let the audience guess where China and India are before the chart appears.")

# %%
# Swapping two charts
# -------------------
#
# The ``r-stack`` class, as in Reveal.js, puts its children on top of each
# other. The 2007 chart is a fragment: it appears over the 1952 chart, at
# the same place, on the next step.

swap = Slide()
swap.add_title(
    f"{(life.loc[last_year] > life.loc[first_year]).sum()} of {life.shape[1]} countries "
    f"lived longer in {last_year} than in {first_year}"
)
swap.add_layout(
    Column(
        12,
        [
            Row(bubbles(1952)),
            Row(bubbles(2007), **{"class": "fragment"}),
        ],
        **{"class": "r-stack"},
    )
)

# %%
# A vertical stack
# ----------------
#
# The main slide gives the result. The slide below holds the method, for
# questions, and the arrows in the corner show it is there.

result = Slide(center=True)
result.add_title(
    f"World life expectancy rose by {weighted[last_year] - weighted[first_year]:.0f} years", tag="h2"
)
result.add_content(
    [
        f"<p>From {weighted[first_year]:.1f} years in {first_year} to {weighted[last_year]:.1f} years "
        f"in {last_year}. Press the down arrow for the method.</p>"
    ]
)

method = Slide()
method.add_title("Data and method")
method.add_content(
    [
        markdown(
            f"World life expectancy is the mean of the {life.shape[1]} countries, **weighted by their "
            "population**. The data come from Gapminder and ship with Plotly."
        )
    ]
)

deck = Presentation()
deck.add_custom_css(STYLE)
deck.add_slide([steps, swap, [result, method]])
deck.save_html("fragments.html", theme="white")

# sphinx_gallery_thumbnail_number = 2
