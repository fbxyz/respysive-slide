"""
Layouts
=======

A slide is a grid of 12 columns. Each slide below shows one layout, with
the code of each block written above it in red, so the deck can be read
next to the code.
"""

import plotly.express as px

from respysive import Column, Presentation, Row, Slide

STYLE = """
:root {
  --r-heading-color: #1d3557;
  --r-heading-text-transform: none;
}
.reveal code.tag {
  display: inline-block;
  margin-bottom: 4px;
  padding: 1px 8px;
  border-radius: 4px;
  background: #fde8ea;
  color: #c1121f;
  font-size: 18px;
}
"""
px.defaults.template = "plotly_white"
px.defaults.color_discrete_sequence = ["#1d3557", "#e63946", "#457b9d", "#f4a261", "#2a9d8f"]


def tag(code):
    """The label written above a block."""
    return f'<code class="tag">{code}</code>'


def figure(value, label):
    """A key figure: a large number and its label."""
    return (
        '<div style="padding:16px;border-radius:10px;background:#f1faee;text-align:center;">'
        f'<div style="font-size:52px;font-weight:700;color:#1d3557;line-height:1.1;">{value}</div>'
        f'<div style="font-size:20px;color:#457b9d;">{label}</div></div>'
    )


gapminder = px.data.gapminder()
latest = gapminder.query("year == 2007")
by_continent = latest.groupby("continent", as_index=False)["lifeExp"].mean()
continent_mean = by_continent.set_index("continent")["lifeExp"]
first_year, last_year = gapminder["year"].min(), gapminder["year"].max()


def gain(country):
    """Years of life expectancy gained by a country over the period."""
    years = gapminder.query("country == @country").set_index("year")["lifeExp"]
    return years[last_year] - years[first_year]


world_mean = (latest["lifeExp"] * latest["pop"]).sum() / latest["pop"].sum()

# %%
# Two columns with ``add_content``
# --------------------------------
#
# ``columns=[8, 4]`` gives two thirds of the width to the chart and one
# third to the text. Widths add up to 12.

trend = px.line(
    gapminder.query("country in ['France', 'India', 'Nigeria']"),
    x="year",
    y="lifeExp",
    color="country",
    labels={"year": "", "lifeExp": "Life expectancy (years)", "country": ""},
)
trend.update_layout(height=460, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=1.1))

two = Slide()
two.add_title(f"India gained {gain('India'):.0f} years of life, Nigeria {gain('Nigeria'):.0f}")
two.add_content(
    [
        tag("columns=[8, 4] → item 1"),
        tag("item 2"),
    ],
    columns=[8, 4],
)
two.add_content(
    [trend, f"<p>Life expectancy at birth, {first_year} to {last_year}. France gained {gain('France'):.0f} years.</p>"],
    columns=[8, 4],
    styles=[None, {"font-size": "70%", "align-self": "center"}],
)

# %%
# Three equal columns
# -------------------
#
# Each call to ``add_content`` adds a row below the previous one.

three = Slide()
three.add_title(f"{len(latest)} countries, {latest['pop'].sum() / 1e9:.1f} billion people in {last_year}")
three.add_content([tag("item 1"), tag("item 2"), tag("item 3")], columns=[4, 4, 4])
three.add_content(
    [
        figure(len(latest), "countries"),
        figure(f"{world_mean:.1f}", "years of life, world average"),
        figure(f"{latest['pop'].sum() / 1e9:.1f} bn", "inhabitants"),
    ],
    columns=[4, 4, 4],
)

# %%
# A column split into two rows
# ----------------------------
#
# ``add_layout`` takes a ``Row`` of ``Column`` objects. A column holds a
# list of ``Row`` objects to stack blocks: here the right column holds a
# chart above a comment.

bars = px.bar(
    by_continent.sort_values("lifeExp"),
    x="lifeExp",
    y="continent",
    orientation="h",
    labels={"lifeExp": "Years", "continent": ""},
)
bars.update_layout(height=260, margin=dict(l=10, r=10, t=10, b=10))

world = px.choropleth(latest, locations="iso_alpha", color="lifeExp", color_continuous_scale="RdBu", labels={"lifeExp": "Years"})
world.update_layout(height=420, margin=dict(l=0, r=0, t=0, b=0), geo=dict(showframe=False))

split = Slide()
split.add_title(f"Europe lives {continent_mean['Europe'] - continent_mean['Africa']:.0f} years longer than Africa")
split.add_layout(
    Row(
        [
            Column(7, [tag("Column(7, map)"), world]),
            Column(
                5,
                [
                    Row([tag("Row(chart)"), bars]),
                    Row([tag("Row(text)"), f"<p>Mean of the countries of each continent, {last_year}.</p>"]),
                ],
                font_size="70%",
            ),
        ],
        gap=4,
    )
)

# %%
# Three levels
# ------------
#
# Rows and columns nest to any depth. The bottom row of the right column is
# itself split into two columns.

nested = Slide()
nested.add_title(f"Oceania and Europe live longest, Africa {continent_mean['Africa']:.0f} years")
nested.add_layout(
    Row(
        [
            Column(7, [tag("Column(7, map)"), world]),
            Column(
                5,
                [
                    Row([tag("Row(chart)"), bars]),
                    Row(
                        [
                            Column(6, [tag("Column(6)"), figure(f"{continent_mean['Europe']:.1f}", "Europe")]),
                            Column(6, [tag("Column(6)"), figure(f"{continent_mean['Africa']:.1f}", "Africa")]),
                        ],
                        gap=2,
                    ),
                ],
            ),
        ],
        gap=4,
    )
)

deck = Presentation()
deck.add_custom_css(STYLE)
deck.add_slide([two, three, split, nested])
deck.save_html("layouts.html", theme="white")

# sphinx_gallery_thumbnail_number = 4
