"""Example: mappyng v2 maps (static + interactive) in a respysive presentation.

Requires: mappyng v2, geopandas, numpy.
"""

import sys
from pathlib import Path

sys.path.insert(0, "/home/florian/Dropbox/git/mappyng_v2/src")

import geopandas as gpd
import numpy as np
from mappyng import Map

from respysive import Presentation, Slide

# ── Data ────────────────────────────────────────────────────────────────
DATA = Path("/home/florian/Dropbox/git/mappyng_v2/src/mappyng/data")

gdf_UE = gpd.read_file(DATA / "abm_pays_europe_gen3.geojson").to_crs(2154)
gdf_DEP = gpd.read_file(DATA / "abm_pays_departement_gen3.geojson").to_crs(2154)

np.random.seed(42)
gdf_DEP["population"] = np.random.randint(50_000, 3_000_000, size=len(gdf_DEP))

bbox_metro = [90000, 6040000, 1280000, 7150000]

# ── Build the map (v2 API) ──────────────────────────────────────────────
m = Map(
    gdf_UE,
    bbox=bbox_metro,
    width=900,
    height=650,
    style="modern",
)

m.add_basemap()
m.add_shadow(gdf_UE, {"query": "code_pays_iso3=='FRA'"})

m.add_choropleth(
    gdf_DEP,
    {
        "column": "population",
        "cmap": "YlOrRd",
        "method": "Quantiles",
        "num_classes": 5,
        "contour_width": 0.15,
        "legend": {
            "title": "Population fictive par département",
            "orientation": "horizontal",
        },
    },
)

m.add_title({"text": "Mappyng v2 + Respysive", "loc": "center", "font_size": 14})
m.add_scale_bar({"length": 200000, "label": "200 km"})
m.add_source({"text": "Source : données fictives — démo mappyng v2"})

# ── Presentation ────────────────────────────────────────────────────────
p = Presentation()

slide1 = Slide(center=True)
slide1.add_title_page(
    {
        "title": "Mappyng v2 + Respysive",
        "subtitle": "Cartes SVG statiques et interactives",
        "authors": "Démo MappyngHandler",
    },
    [
        {"color": "#e63946", "class": "r-fit-text"},
        {},
        {},
    ],
)

# Slide 2 — static SVG map (routed via MappyngHandler → Map.to_string())
slide2 = Slide()
slide2.add_title("Carte statique (SVG)")
slide2.add_content([m], columns=[12])

# Slide 3 — interactive map (routed via MappyngHandler → InteractiveMap._repr_html_())
interactive = m.to_interactive(
    columns=["LIB_GEO", "population"],
    aliases={"LIB_GEO": "Département", "population": "Population"},
    tooltip={
        "background": "#1a1a2e",
        "text_color": "#e0e0ff",
        "font_size": 12,
        "font_family": "Georgia, serif",
    },
    hover_opacity=0.7,
)

slide3 = Slide()
slide3.add_title("Carte interactive — survol pour tooltip")
slide3.add_content([interactive], columns=[12])

# ── Save ────────────────────────────────────────────────────────────────
p.add_slide([slide1, slide2, slide3])
out = Path(__file__).parent / "mappyng_v2_interactive.html"
p.save_html(str(out))
print(f"Saved: {out}")
