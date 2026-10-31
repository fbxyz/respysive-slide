"""The respysive-slide showcase.

One deck that goes through the main features: title page, Markdown,
fragments, Plotly, Altair and Matplotlib charts, a table, an equation, cards,
nested layouts, a mappyng map, and a web map. It opens the documentation, is published as
``showcase.html`` next to it, and gives the picture of the README.

Run from this directory: ``python showcase.py`` writes ``showcase.html``.
"""

from pathlib import Path

import altair as alt
import matplotlib

matplotlib.use("Agg")
import mappyng as mp
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
from mappyng.data import load_europe, load_france_departments, load_france_regions
from markdown import markdown

from respysive import Column, Presentation, Row, Slide, palette

DATA = Path("data")
COLORS = palette("sober")
gapminder = px.data.gapminder()
latest = gapminder.query("year == 2007")


def key_figure(value, label):
    return (
        '<div style="padding:14px 10px;border-radius:10px;background:#eef2fb;text-align:center;">'
        f'<div style="font-size:46px;font-weight:700;color:#1d4ed8;line-height:1.1;">{value}</div>'
        f'<div style="font-size:19px;color:#374151;">{label}</div></div>'
    )


# World life expectancy, weighted by population
world = gapminder.groupby("year", as_index=False).apply(
    lambda g: pd.Series({"lifeExp": (g["lifeExp"] * g["pop"]).sum() / g["pop"].sum()}), include_groups=False
)

# Title page: the title on the left, the story of the deck on the right
start, end = world.iloc[0], world.iloc[-1]
headline = px.area(world, x="year", y="lifeExp", range_y=[40, 75])
headline.update_traces(line=dict(color="#2563eb", width=4), fillcolor="rgba(37, 99, 235, 0.12)", hoverinfo="skip")
for point, position in ((start, "bottom right"), (end, "top left")):
    headline.add_scatter(
        x=[point["year"]],
        y=[point["lifeExp"]],
        mode="markers+text",
        text=[f"<b>{point['lifeExp']:.0f} years</b><br>in {point['year']:.0f}"],
        textposition=position,
        textfont=dict(size=22, color="#1e3a8a"),
        marker=dict(size=14, color="#1e3a8a"),
        showlegend=False,
        hoverinfo="skip",
    )
headline.update_layout(
    height=560,
    margin=dict(l=20, r=20, t=70, b=30),
    title=dict(text="World life expectancy at birth", x=0.03, font=dict(size=24, color="#374151")),
    xaxis=dict(title=None, showgrid=False, tickvals=[1952, 1967, 1982, 1997, 2007], tickfont=dict(size=16)),
    yaxis=dict(visible=False),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
)
headline.update_layout(modebar=dict(remove=["zoom", "pan", "select", "lasso", "zoomIn", "zoomOut", "autoScale"]))

opening = Slide()
opening.add_split_title_page(
    {
        "title": "respysive-slide",
        "subtitle": "Interactive presentations written in Python",
        "authors": "A tour of world health, 1952-2007",
    },
    custom_content=headline,
    title_column_width=6,
    custom_column_width=6,
    full_height=True,
    title_column_style={"background-color": "#1e3a8a", "padding": "60px", "align-items": "flex-start"},
    title_styles=[
        {"font-size": "62px", "color": "#ffffff", "white-space": "nowrap"},
        {"font-size": "32px", "color": "#bfdbfe"},
        {"font-size": "24px", "color": "#e5e7eb", "margin-top": "20px"},
    ],
    custom_content_style={"padding": "30px 20px"},
)
opening.add_notes("Press the right arrow to start. S opens this speaker view.")

# Markdown, an icon, and a list revealed one item at a time
intro = Slide()
intro.add_title("One Python script, one HTML file", icon="fas fa-file-code")
intro.add_content(
    [
        markdown(
            """
- Text in **Markdown** or HTML, equations in LaTeX
- **Plotly**, **Altair** and **Matplotlib** charts, passed as they are
- Tables, images, videos, cards and web maps
- A Bootstrap grid of 12 columns, rows and columns nested at will
- Export to **PDF** and **PowerPoint**, or to a file that works offline
"""
        )
    ],
    fragment_items="fade-up",
)
intro.add_notes("Each item appears with the right arrow.")

# Plotly, with its comment beside it
bubbles = px.scatter(
    latest,
    x="gdpPercap",
    y="lifeExp",
    size="pop",
    color="continent",
    hover_name="country",
    log_x=True,
    size_max=45,
    labels={"gdpPercap": "GDP per capita (USD, log scale)", "lifeExp": "Life expectancy (years)", "continent": ""},
)
bubbles.update_layout(height=500, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=1.1))

plotly_slide = Slide()
plotly_slide.add_title("Richer countries live longer")
plotly_slide.add_content(
    [
        bubbles,
        markdown(
            "Each bubble is a country, sized by its population.\n\n"
            "**Japan** leads with 82.6 years, **Swaziland** comes last with 39.6.\n\n"
            "Hover a bubble to read its values."
        ),
    ],
    columns=[8, 4],
    styles=[None, {"font-size": "72%", "align-self": "center"}],
)

# Altair and Matplotlib side by side
countries = ["Japan", "France", "Brazil", "India", "Nigeria"]
altair_chart = (
    alt.Chart(gapminder[gapminder["country"].isin(countries)])
    .mark_line(point=True, strokeWidth=3)
    .encode(
        x=alt.X("year:O", title=None, axis=alt.Axis(labelAngle=0, values=[1952, 1967, 1982, 1997, 2007])),
        y=alt.Y("lifeExp:Q", title="Life expectancy (years)", scale=alt.Scale(zero=False)),
        color=alt.Color("country:N", title=None),
        tooltip=["country", "year", "lifeExp"],
    )
    .properties(width=470, height=380, title="Altair: five countries")
)

means = gapminder.groupby(["year", "continent"])["lifeExp"].mean().unstack()
mpl_fig, ax = plt.subplots(figsize=(6.2, 4.6))
for colour, continent in zip(COLORS, means.columns, strict=False):
    ax.plot(means.index, means[continent], color=colour, linewidth=2.5, label=continent)
ax.set_title("Matplotlib: mean by continent", loc="left")
ax.set_ylabel("Life expectancy (years)")
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="y", alpha=0.3)
ax.legend(frameon=False, fontsize=9)
mpl_fig.tight_layout()

charts_slide = Slide()
charts_slide.add_title("Three chart libraries, one deck")
charts_slide.add_content([altair_chart, mpl_fig], columns=[6, 6])
plt.close(mpl_fig)

# A table and an equation
rates = pd.read_csv(DATA / "cardio_mortalite_dep.csv", dtype={"code_dep": str})
extremes = pd.concat([rates.nsmallest(3, "taux_mortalite"), rates.nlargest(3, "taux_mortalite")])
table = extremes[["libgeo", "taux_mortalite"]].rename(columns={"libgeo": "Department", "taux_mortalite": "Rate"})
table = table.round(1).to_html(index=False, border=0)

table_slide = Slide()
table_slide.add_title("Tables and equations")
table_slide.add_content(
    [
        table,
        markdown(
            "Deaths from heart failure, per 100,000 inhabitants, 2020-2022, "
            "standardised on the age structure of a reference population:\n\n"
            "$$T = \\sum_{a} \\frac{d_a}{p_a} \\, \\frac{P_a}{P}$$\n\n"
            "with $d_a$ deaths and $p_a$ inhabitants in age group $a$, "
            "$P_a$ and $P$ the reference population."
        ),
    ],
    columns=[5, 7],
    styles=[{"font-size": "80%"}, {"font-size": "70%", "align-self": "center"}],
)
table_slide.add_notes("Source: Sante publique France.")

# Cards: key figures and a chart
trend = px.area(world, x="year", y="lifeExp", labels={"year": "", "lifeExp": ""}, range_y=[45, 72])
trend.update_layout(height=230, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)")

BIG = {"font-size": "150%", "color": "#1d4ed8"}
cards = Slide()
cards.add_title("Cards")
cards.add_card(
    [
        {"title": "+20 years", "title_style": BIG, "text": "World life expectancy, from 49 in 1952 to 69 in 2007."},
        {"title": "World average, weighted by population", "graph": trend},
        {"title": "142", "title_style": BIG, "text": "Countries followed every five years by Gapminder."},
    ],
    styles=[{"class": "bg-light"}, {"class": "bg-light"}, {"class": "bg-light"}],
    fragment=True,
)

# Rows inside columns
by_continent = latest.groupby("continent", as_index=False)["lifeExp"].mean().sort_values("lifeExp")
bars = px.bar(
    by_continent,
    x="lifeExp",
    y="continent",
    orientation="h",
    text="lifeExp",
    labels={"lifeExp": "Mean life expectancy in 2007 (years)", "continent": ""},
)
bars.update_traces(texttemplate="%{text:.1f}", textposition="inside")
bars.update_layout(height=440, margin=dict(l=10, r=10, t=10, b=10))

layout_slide = Slide()
layout_slide.add_title("Nested layouts")
layout_slide.add_layout(
    Row(
        [
            Column(8, bars),
            Column(
                4,
                [
                    Row(key_figure("80.7", "years in Oceania")),
                    Row(key_figure("54.8", "years in Africa")),
                    Row(key_figure("25.9", "years between them")),
                ],
            ),
        ],
        gap=3,
    )
)

# A thematic map drawn in Python with mappyng
europe = load_europe().to_crs(2154)
regions = load_france_regions().to_crs(2154)
deps = load_france_departments().to_crs(2154).merge(rates, left_on="COD_GEO", right_on="code_dep", how="left")
OVERSEAS = {
    "Guadeloupe": [-6890454, 1780151, -6799589, 1874186],
    "Martinique": [-6826862, 1609607, -6759494, 1685367],
    "French Guiana": [-6136680, 235261, -5707791, 671780],
    "Reunion": [6136383, -2448160, 6226316, -2366992],
    "Mayotte": [5006226, -1459183, 5050208, -1416184],
}
france = (
    mp.Map(
        europe,
        bbox=[90000, 6040000, 1280000, 7150000],
        width=900,
        height=760,
        padding=20,
        facecolor="#B9D9EB",
        border_radius=10,
        box_shadow={"dx": 3, "dy": 3, "blur": 6, "opacity": 0.2},
    )
    + mp.Insets(
        [mp.Inset(name, bbox=bbox, crs=3857) for name, bbox in OVERSEAS.items()],
        spacing=15,
        title_size=7,
        border_radius=6,
        box_shadow=True,
    )
    # Lighter water along the coasts, meridians and parallels under the land
    + mp.OceanGradient(europe)
    + mp.Graticule(step=2, stroke="#ffffff", opacity=0.9, stroke_width=0.7)
    # European countries as background, France lifted by a drop shadow
    + mp.Basemap()
    + mp.DropShadow(europe, query="code_pays_iso3 == 'FRA'")
    + mp.Choropleth(
        deps,
        column="taux_mortalite",
        cmap="Reds",
        method="Quantiles",
        num_classes=5,
        stroke="#ffffff",
        stroke_width=0.3,
        border_contrast=True,
        legend=mp.Legend(
            "Deaths / 100,000 inhabitants",
            orientation="horizontal",
            decimals=0,
            label_rotation=0,
            nodata_label="No data",
            swatch_shape="rounded",
        ),
    )
    + mp.Vector(regions, stroke="#333333", stroke_width=0.4, position="top")
    + mp.ScaleBar(length=100000, label="100 km", position=(0.55, 0.855), opacity=0.8)
    + mp.Source("Source: Sante publique France (ODISSE)")
    + mp.Tooltip(["libgeo", "taux_mortalite"], aliases={"libgeo": "Department", "taux_mortalite": "Rate"})
)

choropleth = Slide()
choropleth.add_title("Thematic maps: heart failure in France")
choropleth.add_content(
    [
        france.to_interactive(),
        markdown(
            "Drawn in Python with [mappyng](https://fbxyz.github.io/mappyng/): an SVG that works "
            "offline and stays sharp in PDF.\n\n"
            "Lowest in the Paris area, **25** per 100,000 in Val-de-Marne, highest in Creuse, **71**."
        ),
    ],
    columns=[8, 4],
    styles=[None, {"align-self": "center"}],
)
choropleth.add_notes("Hover a department to read its rate.")

# Proportional circles, with a vertical slide below
traffic = pd.read_csv(DATA / "paris_africa_air_traffic.csv")
circles = Slide()
circles.add_title("Air passengers between Paris and Africa, 2024")
circles.add_maplibre_circles_map(
    center=[8, 18],
    zoom=2,
    circles=[
        {
            "coordinates": [row.lon, row.lat],
            "value": int(row.passengers_2024),
            "color": "#2563eb",
            "popup": f"<b>{row.city}</b><br>{row.passengers_2024:,} passengers",
        }
        for row in traffic.itertuples()
    ],
    legend={"title": "Passengers"},
    min_radius=6,
    max_radius=40,
)
circles.add_content(
    ["Circle areas are proportional to the passengers. Source: Eurostat, avia_par_fr."],
    styles=[{"font-size": "60%", "text-align": "center", "color": "#6b7280", "margin-top": "12px"}],
)

below = Slide(center=True)
below.add_title("A vertical slide", tag="h2")
below.add_content(
    [markdown("Slides grouped in a list are stacked: the down arrow reaches them, Esc shows the overview.")],
    styles=[{"text-align": "center"}],
)

# Closing slide: the code that wrote this deck
closing = Slide(center=True, **{"data-background-gradient": "linear-gradient(135deg, #1e3a8a, #2563eb)"})
closing.add_title("Save, export, check", color="#ffffff")
CODE = """deck.save_html("showcase.html", theme="sober")
deck.save_pdf("showcase.pdf", theme="sober")
deck.save_pptx("showcase.pptx", theme="sober")
report = deck.check(theme="sober")"""
closing.add_content(
    [
        f'<pre style="background:rgba(255,255,255,0.12);color:#ffffff;padding:20px 24px;border-radius:8px;'
        f'text-align:left;font-size:24px;line-height:1.5;margin:0;">{CODE}</pre>',
        "pip install respysive-slide · fbxyz.github.io/respysive-slide",
    ],
    styles=[None, {"color": "#bfdbfe", "font-size": "70%", "margin-top": "30px"}],
)

deck = Presentation()
deck.add_slide(
    [
        opening,
        intro,
        plotly_slide,
        charts_slide,
        table_slide,
        cards,
        layout_slide,
        choropleth,
        [circles, below],
        closing,
    ]
)
deck.save_html("showcase.html", theme="sober")
