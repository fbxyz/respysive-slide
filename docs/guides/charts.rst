Charts
======

Plotly
------

A Plotly figure is passed as it is. It stays interactive: hover labels,
zoom, legend clicks. Its width follows the column, and its height comes
from the figure.

.. respysive-demo::

   import plotly.express as px
   from respysive import Presentation, Slide

   data = px.data.gapminder().query("country in ['Brazil', 'China', 'Japan', 'Nigeria']")
   fig = px.line(data, x="year", y="lifeExp", color="country", markers=True, template="plotly_white",
                 labels={"year": "", "lifeExp": "Life expectancy (years)", "country": ""})
   fig.update_layout(height=520, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=1.1, title=None))

   slide = Slide()
   slide.add_title("China gained 29 years in half a century")
   slide.add_content([fig])

   deck = Presentation()
   deck.add_slide([slide])
   deck.save_html("plotly.html", theme="sober")

The figure's dictionary and its JSON string (``fig.to_json()``) work too.
Plotly is loaded from a CDN once for the whole deck, whatever the number
of charts.

Altair and Matplotlib
---------------------

An Altair chart is passed as it is, or as a Vega-Lite specification
(``chart.to_dict()`` or ``chart.to_json()``). Its ``width`` and ``height``
properties set its size in pixels, and tooltips work as in a notebook.

A Matplotlib ``Figure`` is converted to SVG, so it stays sharp when the
slide is scaled. ``figsize`` sets its proportions, and the figure then
takes the width of its column.

.. respysive-demo::

   import altair as alt
   import matplotlib
   matplotlib.use("Agg")
   import matplotlib.pyplot as plt
   import plotly.express as px
   from respysive import Presentation, Slide

   latest = px.data.gapminder().query("year == 2007")

   chart = (
       alt.Chart(latest)
       .mark_circle(size=90, opacity=0.8)
       .encode(x=alt.X("gdpPercap:Q", scale=alt.Scale(type="log"), title="GDP per capita (USD)"),
               y=alt.Y("lifeExp:Q", scale=alt.Scale(zero=False), title="Life expectancy (years)"),
               color=alt.Color("continent:N", title=None), tooltip=["country", "lifeExp"])
       .properties(width=460, height=380)
   )

   fig, ax = plt.subplots(figsize=(6, 4.6))
   ax.hist(latest["lifeExp"], bins=15, color="#457b9d", edgecolor="white")
   ax.set_xlabel("Life expectancy (years)")
   ax.set_ylabel("Countries")
   ax.spines[["top", "right"]].set_visible(False)

   slide = Slide()
   slide.add_title("Altair on the left, Matplotlib on the right")
   slide.add_content([chart, fig], columns=[6, 6])
   plt.close(fig)

   deck = Presentation()
   deck.add_slide([slide])
   deck.save_html("altair_matplotlib.html", theme="sober")

Sharing GeoJSON between charts
------------------------------

Choropleth maps carry their GeoJSON, which can weigh several megabytes.
When several charts use the same one, it is stored once in the deck:

.. code-block:: python

   deck.add_global_geojson("counties", counties_geojson)
   slide.add_content([fig_2019, fig_2020], columns=[6, 6], shared_data_ids=["counties", "counties"])

The figures can be built with their GeoJSON as usual: respysive leaves it
out of the page, and the charts read the shared copy when the slide is
drawn. Saving the deck raises an error if the id was never added. This
works for the traces placed by ``locations``, such as ``choropleth`` and
``choroplethmap``. :ref:`sphx_glr_gallery_plot_09_shared_geojson.py`
shares one GeoJSON between Plotly and MapLibre.

Charts in cards
---------------

A card's ``graph`` key takes any of these chart types, see
:doc:`appearance` and :ref:`sphx_glr_gallery_plot_06_cards.py`.

Other JavaScript libraries
--------------------------

``add_custom_content`` draws a chart with a library respysive does not
know. It takes a name for the library (letters, digits, and dashes), the
configuration object, the URLs to load, and the script that draws the
chart. The script receives ``config``, whose ``config.container`` holds the
id of the ``div`` to draw in.

.. respysive-demo::

   from respysive import Presentation, Slide

   slide = Slide()
   slide.add_title("A Chart.js chart")
   slide.add_custom_content(
       library="chartjs",
       config={
           "type": "bar",
           "data": {
               "labels": ["Africa", "Americas", "Asia", "Europe", "Oceania"],
               "datasets": [{"label": "Life expectancy, 2007", "data": [54.8, 73.6, 70.7, 77.6, 80.7],
                             "backgroundColor": "#457b9d"}],
           },
           "options": {"maintainAspectRatio": False},
       },
       cdn={"js": ["https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"]},
       init_script=(
           "new Chart(document.getElementById(config.container)"
           ".appendChild(document.createElement('canvas')), config)"
       ),
       div_style={"height": "480px", "width": "100%"},
   )

   deck = Presentation()
   deck.add_slide([slide])
   deck.save_html("chartjs.html", theme="sober")
