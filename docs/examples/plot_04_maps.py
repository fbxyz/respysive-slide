"""
Maps
====

MapLibre web maps, with tiles, zoom, and pan, which need a network
connection while the deck is shown. Maps drawn in Python with mappyng
will be added here once mappyng 2 is published.

Data: mortality from heart failure by department (Sante publique France)
and air passengers between Paris and African cities in 2024 (Eurostat).
"""

import json
from pathlib import Path

import pandas as pd

from respysive import Presentation, Slide

STYLE = """
:root {
  --r-heading-color: #1d3557;
  --r-heading-text-transform: none;
}
"""
DATA = Path("data")

# %%
# A choropleth map with MapLibre
# -------------------------------
#
# ``color_rules`` are tested in order and the first match gives the colour
# of each department. The popup template reads the GeoJSON properties.

rates = pd.read_csv(DATA / "cardio_mortalite_dep.csv", dtype={"code_dep": str}).set_index("code_dep")
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
deck.add_slide([map_slide, web_map])
deck.save_html("maps.html", theme="white")
