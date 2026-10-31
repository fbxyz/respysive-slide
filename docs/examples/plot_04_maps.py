"""
Maps
====

Thematic maps drawn in Python with mappyng, which are SVG and work
offline, and MapLibre web maps, with tiles, zoom, and pan, which need a
network connection while the deck is shown.

Data: mortality from heart failure by department (Sante publique France)
and air passengers between Paris and African cities in 2024 (Eurostat).
"""

import json
from pathlib import Path

import mappyng as mp
import pandas as pd
from mappyng.data import load_france_departments

from respysive import Presentation, Slide

STYLE = """
:root {
  --r-heading-color: #1d3557;
  --r-heading-text-transform: none;
}
"""
DATA = Path("data")

# %%
# A choropleth map with mappyng
# -----------------------------
#
# A mappyng ``Map`` is passed to ``add_content`` as it is. ``to_interactive()``
# adds the tooltips declared with ``mp.Tooltip``.

rates = pd.read_csv(DATA / "cardio_mortalite_dep.csv", dtype={"code_dep": str})
deps = load_france_departments().to_crs(2154).merge(rates, left_on="COD_GEO", right_on="code_dep")
svg_map = (
    mp.Map(deps, bbox=[90000, 6040000, 1280000, 7150000], width=600, height=560)
    + mp.Choropleth(
        deps,
        column="taux_mortalite",
        cmap="YlOrRd",
        method="Quantiles",
        num_classes=5,
        stroke="#ffffff",
        stroke_width=0.3,
        legend=mp.Legend("Deaths per 100,000", decimals=0),
    )
    + mp.Tooltip(["libgeo", "taux_mortalite"], aliases={"libgeo": "Department", "taux_mortalite": "Rate"})
)

svg_slide = Slide()
svg_slide.add_title("Mortality from heart failure, 2020-2022")
svg_slide.add_content(
    [svg_map.to_interactive(), "Lowest in the Paris area, highest in Creuse."],
    columns=[7, 5],
    styles=[None, {"align-self": "center"}],
)

# %%
# A choropleth map with MapLibre
# -------------------------------
#
# ``color_rules`` are tested in order and the first match gives the colour
# of each department. The popup template reads the GeoJSON properties.

rates = rates.set_index("code_dep")
geojson = json.loads((DATA / "france_departments.geojson").read_text())
geojson["features"] = [f for f in geojson["features"] if f["properties"]["code_dep"] in rates.index]
for feature in geojson["features"]:
    feature["properties"].update(rates.loc[feature["properties"]["code_dep"]].to_dict())

map_slide = Slide()
map_slide.add_title("Mortality from heart failure, 2020-2022")
map_slide.add_maplibre_choropleth_map(
    center=[2.5, 46.6],
    zoom=4,
    geojson=geojson,
    color_property="taux_mortalite",
    color_rules=[
        {"operator": ">=", "value": 55, "color": "#bd0026"},
        {"operator": ">=", "value": 45, "color": "#fd8d3c"},
        {"operator": "<", "value": 45, "color": "#fed976"},
    ],
    popup="<b>{libgeo}</b><br>{taux_mortalite} per 100,000",
)

# %%
# Proportional circles with MapLibre
# ----------------------------------
#
# ``add_maplibre_circles_map`` sizes each circle by the square root of its
# value, so its area is proportional to it. A click on a circle opens its
# popup.

traffic = pd.read_csv(DATA / "paris_africa_air_traffic.csv")
circles = [
    {
        "coordinates": [row.lon, row.lat],
        "value": int(row.passengers_2024),
        "color": "#e63946",
        "popup": f"<b>{row.city}</b><br>{row.passengers_2024:,} passengers",
    }
    for row in traffic.itertuples()
]

web_map = Slide()
web_map.add_title("Air passengers between Paris and Africa, 2024")
web_map.add_maplibre_circles_map(
    center=[10, 15],
    zoom=2,
    circles=circles,
    legend={"title": "Passengers"},
    min_radius=6,
    max_radius=40,
)

deck = Presentation()
deck.add_custom_css(STYLE)
deck.add_slide([svg_slide, map_slide, web_map])
deck.save_html("maps.html", theme="white")
