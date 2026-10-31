Maps
====

respysive takes two kinds of maps. A mappyng map is an SVG computed in
Python: it shows the same thing everywhere, works offline, and prints
sharply. A MapLibre map is a web map with tiles, zoom, and pan, which
needs a network connection while the deck is shown.

mappyng
-------

mappyng draws thematic maps (choropleth, proportional symbols, labels,
insets) from GeoDataFrames. A ``Map`` is passed to ``add_content`` as it
is, and ``to_interactive()`` adds the tooltips declared with
``mp.Tooltip``. The map below draws the European countries in the
background, lifts France with a drop shadow, puts the overseas departments
in insets, and ``border_contrast=True`` redraws the borders between
neighbours of similar colour. mappyng is installed with ``pip install mappyng-svg``
(`documentation <https://fbxyz.github.io/mappyng/>`_).

.. respysive-demo::

   import pandas as pd
   import mappyng as mp
   from mappyng.data import load_europe, load_france_departments, load_france_regions
   from respysive import Presentation, Slide

   europe = load_europe().to_crs(2154)
   regions = load_france_regions().to_crs(2154)
   rates = pd.read_csv("data/cardio_mortalite_dep.csv", dtype={"code_dep": str})
   deps = load_france_departments().to_crs(2154).merge(rates, left_on="COD_GEO", right_on="code_dep", how="left")
   overseas = {
       "Guadeloupe": [-6890454, 1780151, -6799589, 1874186],
       "Martinique": [-6826862, 1609607, -6759494, 1685367],
       "French Guiana": [-6136680, 235261, -5707791, 671780],
       "Reunion": [6136383, -2448160, 6226316, -2366992],
       "Mayotte": [5006226, -1459183, 5050208, -1416184],
   }

   m = (
       mp.Map(europe, bbox=[90000, 6040000, 1280000, 7150000], width=900, height=760, padding=20,
              facecolor="#B9D9EB", border_radius=10, box_shadow={"dx": 3, "dy": 3, "blur": 6, "opacity": 0.2})
       + mp.Insets([mp.Inset(name, bbox=bbox, crs=3857) for name, bbox in overseas.items()],
                   spacing=15, title_size=7, border_radius=6, box_shadow=True)
       + mp.OceanGradient(europe)
       + mp.Graticule(step=2, stroke="#ffffff", opacity=0.9, stroke_width=0.7)
       + mp.Basemap()
       + mp.DropShadow(europe, query="code_pays_iso3 == 'FRA'")
       + mp.Choropleth(deps, column="taux_mortalite", cmap="Reds", method="Quantiles", num_classes=5,
                       stroke="#ffffff", stroke_width=0.3, border_contrast=True,
                       legend=mp.Legend("Deaths / 100,000 inhabitants", orientation="horizontal", decimals=0,
                                        nodata_label="No data", swatch_shape="rounded"))
       + mp.Vector(regions, stroke="#333333", stroke_width=0.4, position="top")
       + mp.ScaleBar(length=100000, label="100 km", position=(0.55, 0.855), opacity=0.8)
       + mp.Source("Source: Sante publique France (ODISSE)")
       + mp.Tooltip(["libgeo", "taux_mortalite"], aliases={"libgeo": "Department", "taux_mortalite": "Rate"})
   )

   slide = Slide()
   slide.add_title("Heart failure deaths are lowest in the Paris area")
   slide.add_content(
       [m.to_interactive(), "Lowest in the Paris area, 25 per 100,000 in Val-de-Marne, highest in Creuse, 71."],
       columns=[8, 4],
       styles=[None, {"align-self": "center"}],
   )

   deck = Presentation()
   deck.add_slide([slide])
   deck.save_html("mappyng.html", theme="sober")

When several maps share SVG ids (clip paths, gradients), each copy is
renamed, so a map on one slide never depends on a map on another.

MapLibre
--------

Four helpers build MapLibre maps without writing JavaScript. Coordinates
are ``[longitude, latitude]`` and ``zoom`` is an integer. The base map is
the MapLibre demonstration style, and ``openstreetmap=True`` uses OpenStreetMap
tiles instead.

.. list-table::
   :header-rows: 1
   :widths: 38 62

   * - Method
     - Map
   * - ``add_maplibre_map``
     - Base map with markers (Font Awesome icons, popups) and a legend
   * - ``add_maplibre_circles_map``
     - Circles whose area is proportional to a value
   * - ``add_maplibre_lines_map``
     - Lines of varying width, for flows or traffic
   * - ``add_maplibre_choropleth_map``
     - GeoJSON polygons coloured by value rules

Circles are sized by the square root of their value, so their area is
proportional to it. A click on a circle opens its popup.

.. respysive-demo::

   import pandas as pd
   from respysive import Presentation, Slide

   traffic = pd.read_csv("data/paris_africa_air_traffic.csv")
   circles = [
       {"coordinates": [r.lon, r.lat], "value": int(r.passengers_2024), "color": "#e63946",
        "popup": f"<b>{r.city}</b><br>{r.passengers_2024:,} passengers"}
       for r in traffic.itertuples()
   ]

   slide = Slide()
   slide.add_title("Algiers and Tunis lead air traffic between Paris and Africa, 2024")
   slide.add_maplibre_circles_map(center=[10, 15], zoom=2, circles=circles,
                                  legend={"title": "Passengers"}, min_radius=6, max_radius=40)

   deck = Presentation()
   deck.add_slide([slide])
   deck.save_html("maplibre.html", theme="sober")

For a choropleth, ``color_rules`` are tested in order and the first match
gives the colour. The popup template reads the GeoJSON properties.

.. respysive-demo::

   import json
   import pandas as pd
   from respysive import Presentation, Slide

   rates = pd.read_csv("data/cardio_mortalite_dep.csv", dtype={"code_dep": str}).set_index("code_dep")
   with open("data/france_departments.geojson") as f:
       geojson = json.load(f)
   geojson["features"] = [f for f in geojson["features"] if f["properties"]["code_dep"] in rates.index]
   for feature in geojson["features"]:
       feature["properties"].update(rates.loc[feature["properties"]["code_dep"]].to_dict())

   slide = Slide()
   slide.add_title("14 departments count 55 heart failure deaths per 100,000 or more")
   slide.add_maplibre_choropleth_map(
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

   deck = Presentation()
   deck.add_slide([slide])
   deck.save_html("maplibre_choropleth.html", theme="sober")

When the same polygons appear on several slides with different values,
store the GeoJSON once with ``add_global_geojson`` and join the values on
each slide with ``add_maplibre_choropleth_with_data_join``.
:ref:`sphx_glr_gallery_plot_09_shared_geojson.py` draws the same
departments with mappyng, Plotly, and MapLibre, with one GeoJSON stored in
the deck for the two web maps.

Maps in exports
---------------

PDF and PowerPoint exports wait for the tiles, then include each MapLibre
map as a picture. mappyng maps stay vectors in PDF.
