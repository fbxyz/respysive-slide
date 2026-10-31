Quickstart
==========

A presentation is a list of slides. Each :class:`~respysive.Slide` receives
its content through methods such as ``add_title`` and ``add_content``. The
:class:`~respysive.Presentation` collects the slides and writes the HTML
file.

.. respysive-demo::

   import plotly.express as px
   from respysive import Presentation, Slide

   df = px.data.gapminder().query("year == 2007")
   fig = px.scatter(df, x="gdpPercap", y="lifeExp", size="pop", color="continent",
                    hover_name="country", log_x=True, size_max=45, template="plotly_white",
                    labels={"gdpPercap": "GDP per capita (USD)", "lifeExp": "Life expectancy (years)"})
   fig.update_layout(height=520, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=1.1, title=None))

   title = Slide(center=True)
   title.add_title_page({"title": "World health", "subtitle": "Gapminder data, 2007"})

   chart = Slide()
   chart.add_title("Richer countries live longer")
   chart.add_content([fig, "Each bubble is a country, sized by its population."], columns=[8, 4])
   chart.add_notes("Start with the cluster of African countries on the left.")

   deck = Presentation()
   deck.add_slide([title, chart])
   deck.save_html("world_health.html", theme="sober")

Open ``world_health.html`` in a browser, or click the deck above. The right
arrow moves to the next slide, and ``S`` opens the speaker view with the
notes.

What ``add_content`` accepts
----------------------------

``add_content`` takes a list of items and places them side by side. The
type of each item is detected: a Plotly figure becomes an interactive
chart, a path ending in ``.png`` an image, a string an HTML or Markdown
block. :doc:`content` lists the types and how to force one when detection
is wrong.

``columns`` gives the width of each item on a 12-column grid, so
``[8, 4]`` gives two thirds of the width to the chart. A new call to
``add_content`` starts a new row below the previous one.

Styling
-------

Most methods take CSS as keyword arguments, with underscores in place of
dashes, and a ``class`` key for CSS classes. ``add_content`` takes one
dictionary per item in ``styles``. The look of the whole deck comes from
its theme, ``"sober"``, ``"science"``, or ``"corporate"`` (see
:doc:`appearance`), and ``add_custom_css`` adjusts it.

.. respysive-demo::

   from respysive import Presentation, Slide

   slide = Slide(center=True)
   slide.add_title("Richer countries live longer", tag="h2", color="#e63946")
   slide.add_content(
       ["Japan: 82.6 years", "Swaziland: 39.6 years"],
       columns=[6, 6],
       styles=[{"font-size": "120%"}, {"font-size": "120%", "color": "#457b9d"}],
   )

   deck = Presentation()
   deck.add_slide([slide])
   deck.save_html("styled.html", theme="sober")

The :doc:`../gallery/index` shows longer decks with their code.
