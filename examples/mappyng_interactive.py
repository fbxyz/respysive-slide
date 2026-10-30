"""Example: mappyng interactive map in a respysive presentation.

Requires: mappyng, geopandas, numpy, pandas
"""

import sys

sys.path.insert(0, "/home/florian/Dropbox/git/mappyng/mappyng/src")

import geopandas as gpd
import numpy as np
import pandas as pd
from mappyng.map import Map

from respysive import Presentation, Slide

# ── Data ────────────────────────────────────────────────────────────────
url_ue = "https://raw.githubusercontent.com/fbxyz/data/refs/heads/main/abm_pays_europe_gen3.geojson"
gdf_UE = gpd.read_file(url_ue, crs="3857").to_crs(2154)

url_dep = "https://raw.githubusercontent.com/fbxyz/data/refs/heads/main/abm_pays_departement_gen3.geojson"
gdf_dep = gpd.read_file(url_dep, crs="3857").to_crs(2154)

np.random.seed(42)
df_data = pd.DataFrame(
    {
        "Code": gdf_dep["COD_GEO"].unique(),
        "Prev_dial_21": np.random.uniform(50, 200, size=len(gdf_dep["COD_GEO"].unique())),
    }
)
gdf_data = gdf_dep.merge(df_data, how="left", left_on="COD_GEO", right_on="Code")

# ── Map parameters ──────────────────────────────────────────────────────
bbox_test = [90000, 6040000, 1280000, 7150000]
bbox_pc = [637000, 6845000, 672000, 6879000]

cartouche_params = {
    0: {"name": "971", "bbox": [-6890454, 1780151, -6799589, 1874186], "crs": 3857},
    1: {"name": "972", "bbox": [-6826862, 1609607, -6759494, 1685367], "crs": 3857},
    2: {"name": "973", "bbox": [-6136680, 235261, -5707791, 671780], "crs": 3857},
    3: {"name": "974", "bbox": [6136383, -2448160, 6226316, -2366992], "crs": 3857},
    4: {"name": "976", "bbox": [5003748, -1469401, 5052841, -1409959], "crs": 3857},
}

q = "code_pays_iso3=='FRA'"
ocean = ["#7eb9daff", "#80badbff", "#87beddff", "#91c3dfff", "#97c6e1ff", "#9dc9e4ff"]

# ── Build the map ───────────────────────────────────────────────────────
m = Map(
    gdf_UE,
    bbox_test,
    style="modern",
    cartouche_params=cartouche_params,
    facecolor=ocean,
    shadow=q,
    grid_params={"spacing": 100000},
)

zoom_ax = m.add_zoom_ax(bbox_pc)
m.add_scale_bar(length=100000, units="100 km", location="lower left")
m.add_title("Prévalence de la maladie rénale chronique\ntraitée par dialyse en 2021 (simulé)")
m.add_source("Source: Agence de la biomédecine-REIN, 2023", font_size=8)

m.add_choropleth(
    gdf_data,
    column="Prev_dial_21",
    cmap="YlOrRd",
    contour_color="#4d4d4d",
    num_classes=5,
    method="Quantiles",
    legend_title="Taux standardisés sur le sexe",
    legend_spacing=0.0,
)

# ── Get the interactive version (InteractiveMap with _repr_html_) ───────
interactive = m.to_interactive(
    columns=["LIB_GEO", "COD_GEO", "Prev_dial_21"],
    aliases={
        "LIB_GEO": "Département",
        "COD_GEO": "Code",
        "Prev_dial_21": "Prévalence dialyse",
    },
    tooltip_style={
        "background": "#1a1a2e",
        "text_color": "#e0e0ff",
        "font_size": 12,
        "font_family": "Georgia, serif",
    },
)

# ── Presentation ────────────────────────────────────────────────────────
p = Presentation()

# Slide 1: title
slide1 = Slide(center=True)
slide1.add_title_page(
    {
        "title": "Mappyng + Respysive",
        "subtitle": "Carte interactive avec tooltips au survol",
        "authors": "Exemple mappyng.interactive → respysive",
    },
    [
        {"color": "#e63946", "class": "r-fit-text"},
        {},
        {},
    ],
)

# Slide 2: interactive map — auto-detected via HtmlReprHandler
slide2 = Slide()
slide2.add_title("Carte interactive — survol pour tooltip")
slide2.add_content([interactive], columns=[12])

# Slide 3: static matplotlib figure for comparison
slide3 = Slide()
slide3.add_title("Version statique (matplotlib)")
slide3.add_content([m.fig], columns=[12])

m.cleanup()

# ── Save ────────────────────────────────────────────────────────────────
p.add_slide([slide1, slide2, slide3])
p.save_html("examples/mappyng_interactive.html")
print("Saved: examples/mappyng_interactive.html")
