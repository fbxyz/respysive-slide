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
from mappyng.data import load_europe, load_france_departments, load_france_regions

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
# adds the tooltips declared with ``mp.Tooltip``. The European countries are
# drawn in the background, the overseas departments in insets, and
# ``border_contrast=True`` redraws the borders between neighbours of similar
# colour.

rates = pd.read_csv(DATA / "cardio_mortalite_dep.csv", dtype={"code_dep": str})
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
svg_map = (
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

svg_slide = Slide()
svg_slide.add_title("Mortality from heart failure, 2020-2022")
svg_slide.add_content(
    [svg_map.to_interactive(), "Lowest in the Paris area, highest in Creuse."],
    columns=[8, 4],
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
