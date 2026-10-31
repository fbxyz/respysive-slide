"""
Charts
======

Plotly and Altair charts stay interactive in the deck: hover a point to
read its values. Matplotlib figures become SVG. Figures are passed as
they are, without exporting them to JSON first.
"""

import altair as alt
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import plotly.express as px
from markdown import markdown

from respysive import Presentation, Slide

STYLE = """
:root {
  --r-heading-color: #1d3557;
  --r-heading-text-transform: none;
}
"""
PALETTE = ["#1d3557", "#e63946", "#457b9d", "#f4a261", "#2a9d8f"]
px.defaults.template = "plotly_white"
px.defaults.color_discrete_sequence = PALETTE

gapminder = px.data.gapminder()
latest = gapminder.query("year == 2007")
life = gapminder.pivot(index="year", columns="country", values="lifeExp")
first_year, last_year = life.index.min(), life.index.max()

# %%
# Plotly
# ------
#
# The chart takes the width of its column. Its height comes from the
# figure: an explicit height gives the same chart on screen and in exports.

bubbles = px.scatter(
    latest,
    x="gdpPercap",
    y="lifeExp",
    size="pop",
    color="continent",
    hover_name="country",
    log_x=True,
    size_max=50,
    labels={"gdpPercap": "GDP per capita (USD, log scale)", "lifeExp": "Life expectancy (years)", "continent": ""},
)
bubbles.update_layout(height=540, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=1.08))

plotly_slide = Slide()
plotly_slide.add_title(f"Richer countries live longer, {last_year}")
plotly_slide.add_content([bubbles])

# %%
# Altair
# ------
#
# An Altair chart is detected as it is. Its ``width`` and ``height``
# properties set its size in pixels.

countries = ["France", "Japan", "Brazil", "India", "Nigeria"]
lines = (
    alt.Chart(gapminder[gapminder["country"].isin(countries)])
    .mark_line(point=True, strokeWidth=3)
    .encode(
        x=alt.X("year:O", title=None, axis=alt.Axis(labelAngle=0)),
        y=alt.Y("lifeExp:Q", title="Life expectancy (years)", scale=alt.Scale(zero=False)),
        color=alt.Color("country:N", title=None, scale=alt.Scale(range=PALETTE)),
        tooltip=["country", "year", "lifeExp"],
    )
    .properties(width=900, height=430)
    .configure_axis(labelFontSize=14, titleFontSize=15)
    .configure_legend(labelFontSize=15)
)

altair_slide = Slide()
altair_slide.add_title(
    f"Japan rose from {life.loc[first_year, 'Japan']:.0f} to {life.loc[last_year, 'Japan']:.0f} years and overtook France"
)
altair_slide.add_content([lines])

# %%
# Matplotlib next to a comment
# ----------------------------
#
# A Matplotlib figure becomes an inline SVG, sharp at any zoom level.

means = gapminder.groupby(["year", "continent"])["lifeExp"].mean().unstack()
mpl_fig, ax = plt.subplots(figsize=(8, 4.8))
for colour, continent in zip(PALETTE, means.columns):
    ax.plot(means.index, means[continent], color=colour, linewidth=2.5, label=continent)
ax.set_ylabel("Mean life expectancy (years)")
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="y", alpha=0.3)
ax.legend(frameon=False, ncol=5, loc="upper center", bbox_to_anchor=(0.5, 1.12))
mpl_fig.tight_layout()

mpl_slide = Slide()
gain = means.loc[last_year] - means.loc[first_year]
gap = means["Europe"] - means["Asia"]
mpl_slide.add_title(f"Asia gained {gain['Asia']:.0f} years of life, Europe {gain['Europe']:.0f}")
mpl_slide.add_content(
    [
        mpl_fig,
        markdown(
            f"Mean of the countries of each continent. Europe led Asia by **{gap[first_year]:.0f} years** "
            f"in {first_year}, by **{gap[last_year]:.0f}** in {last_year}."
        ),
    ],
    columns=[8, 4],
    styles=[None, {"font-size": "75%", "align-self": "center"}],
)
plt.close(mpl_fig)

# %%
# Two charts side by side
# -----------------------
#
# Each chart takes its column. The same height keeps them aligned.

def top_countries(continent):
    data = latest.query("continent == @continent").nlargest(8, "pop").sort_values("lifeExp")
    fig = px.bar(
        data,
        x="lifeExp",
        y="country",
        orientation="h",
        text="lifeExp",
        title=f"{continent}, eight most populated countries",
        labels={"lifeExp": "Life expectancy (years)", "country": ""},
    )
    fig.update_traces(texttemplate="%{text:.0f}", textposition="inside")
    fig.update_layout(height=470, margin=dict(l=10, r=10, t=50, b=10), xaxis_range=[0, 85])
    return fig


pair = Slide()
pair.add_title("The most populated countries live longer in Asia than in Africa")
pair.add_content([top_countries("Africa"), top_countries("Asia")], columns=[6, 6])

deck = Presentation()
deck.add_custom_css(STYLE)
deck.add_slide([plotly_slide, altair_slide, mpl_slide, pair])
deck.save_html("charts.html", theme="white")
