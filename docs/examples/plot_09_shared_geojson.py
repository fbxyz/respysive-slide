"""
One GeoJSON, three maps
=======================

The same departments drawn by mappyng, Plotly, and MapLibre, with the same
classes and colours. The polygons are loaded once, as a GeoDataFrame:

* mappyng draws the SVG in Python from the GeoDataFrame, so the deck holds
  no GeoJSON for it;
* the Plotly and MapLibre maps read one GeoJSON, stored once in the deck
  with ``add_global_geojson``, whatever the number of maps that use it.

Data: mortality from heart failure by department, 2020-2022 (Sante publique
France), and the departments of mappyng (IGN, GéoFLA).
"""

import json
from pathlib import Path

import mapclassify
import mappyng as mp
import pandas as pd
import plotly.express as px
from mappyng.data import load_france_departments

from respysive import Presentation, Slide

DATA = Path("data")

# %%
# The data, the classes, and the colours
# --------------------------------------
#
# The values are joined to the polygons on the department code. The five
# quantile classes and their colours are computed once, for the three maps.

rates = pd.read_csv(DATA / "cardio_mortalite_dep.csv", dtype={"code_dep": str})
departments = load_france_departments()[["COD_GEO", "LIB_GEO", "geometry"]]
departments = departments.merge(rates, left_on="COD_GEO", right_on="code_dep")

breaks = mapclassify.Quantiles(departments["taux_mortalite"], k=5).bins
colors = ["#fee5d9", "#fcae91", "#fb6a4a", "#de2d26", "#a50f15"]
lower = [departments["taux_mortalite"].min(), *breaks[:-1]]
labels = [f"{a:.0f} to {b:.0f}" for a, b in zip(lower, breaks)]
ranked = departments.sort_values("taux_mortalite")
highest = ranked.iloc[-1]
SOURCE = "Standardised rates, 2020-2022. Source: Sante publique France (ODISSE), IGN (GéoFLA)."
CAPTION = {"font-size": "50%", "text-align": "center", "color": "#6b7280", "margin-top": "8px"}
departments["class"] = pd.cut(departments["taux_mortalite"], [-float("inf"), *breaks], labels=labels).astype(str)

# %%
# The shared GeoJSON
# ------------------
#
# Web maps take longitude and latitude. Only the geometry and the join key go
# in the shared GeoJSON: each map brings its own values.

geojson = json.loads(departments[["COD_GEO", "geometry"]].to_crs(4326).to_json(drop_id=True))

deck = Presentation()
deck.add_global_geojson("departments", geojson)

# %%
# mappyng: an SVG drawn in Python
# -------------------------------
#
# A list of class edges as ``method`` reuses the classes computed above.
# ``border_contrast``
# redraws the borders between neighbours of similar colour.

svg_map = (
    mp.Map(departments.to_crs(2154), bbox=[90000, 6040000, 1280000, 7150000], width=600, height=560)
    + mp.Choropleth(
        departments.to_crs(2154),
        column="taux_mortalite",
        method=[float(v) for v in [lower[0], *breaks]],
        cmap=colors,
        stroke="#ffffff",
        stroke_width=0.3,
        border_contrast=True,
        legend=mp.Legend("Deaths per 100,000", decimals=0),
    )
    + mp.Tooltip(["libgeo", "taux_mortalite"], aliases={"libgeo": "Department", "taux_mortalite": "Rate"})
)

svg_slide = Slide()
svg_slide.add_title(
    f"{(departments['class'] == labels[-1]).sum()} departments count {lower[-1]:.0f} "
    "or more heart failure deaths per 100,000"
)
svg_slide.add_content([svg_map.to_interactive()])
svg_slide.add_content([f"Drawn by mappyng. {SOURCE}"], styles=[CAPTION])

# %%
# Plotly: a tile map that reads the shared GeoJSON
# ------------------------------------------------
#
# The figure is built with the GeoJSON as usual. ``shared_data_ids`` tells
# respysive to leave it out of the figure and to read the shared copy.

fig = px.choropleth_map(
    departments,
    geojson=geojson,
    locations="COD_GEO",
    featureidkey="properties.COD_GEO",
    color="class",
    color_discrete_map=dict(zip(labels, colors)),
    category_orders={"class": labels},
    hover_name="libgeo",
    hover_data={"taux_mortalite": True, "class": False, "COD_GEO": False},
    labels={"class": "Deaths per 100,000", "taux_mortalite": "Rate"},
    center={"lat": 46.6, "lon": 2.5},
    zoom=4.3,
    map_style="carto-positron",
)
fig.update_traces(marker_line_color="#ffffff", marker_line_width=0.5)
fig.update_layout(
    margin={"l": 0, "r": 0, "t": 0, "b": 0},
    height=540,
    legend={"x": 0.01, "y": 0.97, "xanchor": "left", "yanchor": "top", "bgcolor": "rgba(255,255,255,0.85)"},
)

plotly_slide = Slide()
plotly_slide.add_title(f"{ranked.iloc[0].libgeo} and {ranked.iloc[1].libgeo} have the lowest rates")
plotly_slide.add_content([fig], shared_data_ids=["departments"])
plotly_slide.add_content([f"Plotly tile map. {SOURCE}"], styles=[CAPTION])

# %%
# MapLibre: the values joined in the browser
# ------------------------------------------
#
# ``geojson_id`` points to the shared GeoJSON, and ``join_data`` gives the
# values of each department, keyed by the code in ``join_key``. The colour
# rules are tested in order, from the highest class down.

join_data = {
    row.COD_GEO: {"name": row.libgeo, "rate": round(row.taux_mortalite, 1)} for row in departments.itertuples()
}
rules = [{"operator": ">=", "value": round(float(low), 2), "color": color} for low, color in zip(lower, colors)]

web_slide = Slide()
web_slide.add_title(f"{highest.libgeo} has the highest rate, {highest.taux_mortalite:.0f} deaths per 100,000")
web_slide.add_maplibre_choropleth_with_data_join(
    center=[2.5, 46.6],
    zoom=4,
    geojson_id="departments",
    join_data=join_data,
    join_key="COD_GEO",
    color_property="rate",
    color_rules=rules[::-1],
    popup="<b>{name}</b><br>{rate} per 100,000",
    legend={
        "title": "Deaths per 100,000",
        "choropleth": {
            "type": "discrete",
            "items": [{"color": c, "label": label} for c, label in zip(colors[::-1], labels[::-1])],
        },
    },
)
web_slide.add_content([f"MapLibre map, values joined in the browser. {SOURCE}"], styles=[CAPTION])

deck.add_slide([svg_slide, plotly_slide, web_slide])
deck.save_html("shared_geojson.html", theme="sober")

# %%
# The GeoJSON is written once in the page, however many web maps use it.

first_point = json.dumps(geojson["features"][0]["geometry"]["coordinates"], separators=(",", ":"))[:40]
page = deck.to_html(theme="sober")
print(f"Shared GeoJSON: {len(json.dumps(geojson)) // 1024} KB, found {page.count(first_point)} time(s) in the page")
