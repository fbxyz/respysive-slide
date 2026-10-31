Layout
======

Slides use the `Bootstrap grid
<https://getbootstrap.com/docs/5.3/layout/grid/>`_. A row is divided into
12 columns, and each block takes a number of them. The grid is tied to the
slide, not to the window, so a block of 6 columns is always half the slide
wide.

Side by side with ``add_content``
---------------------------------

``columns`` gives one width per item. Each call to ``add_content`` adds a
row under the previous one.

.. respysive-demo::

   import plotly.express as px
   from respysive import Presentation, Slide

   data = px.data.gapminder().query("country in ['France', 'India', 'Nigeria']")
   fig = px.line(data, x="year", y="lifeExp", color="country", template="plotly_white",
                 labels={"year": "", "lifeExp": "Life expectancy (years)", "country": ""})
   fig.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=1.1, title=None))

   slide = Slide()
   slide.add_title("India gained 27 years of life, Nigeria 10")
   slide.add_content(
       [fig, "Life expectancy at birth, 1952 to 2007. France gained 13 years."],
       columns=[8, 4],
       styles=[None, {"font-size": "75%", "align-self": "center"}],
   )

   deck = Presentation()
   deck.add_slide([slide])
   deck.save_html("columns.html", theme="sober")

Nested blocks with ``Row`` and ``Column``
-----------------------------------------

``add_content`` builds one level of columns. For more, ``add_layout`` takes
a :class:`~respysive.Row`. A row holds :class:`~respysive.Column` objects
side by side, and a column holds rows stacked one above the other. The
classic case is a large map on the left and a column split into two rows
on the right:

.. raw:: html

   <div class="rs-figure"><img src="../_static/layout_nesting.svg" alt="A Row holding Column(7) and Column(5); Column(5) holds two Rows."></div>

.. respysive-demo::

   import plotly.express as px
   from respysive import Column, Presentation, Row, Slide

   latest = px.data.gapminder().query("year == 2007")
   world = px.choropleth(latest, locations="iso_alpha", color="lifeExp",
                         color_continuous_scale="RdBu", labels={"lifeExp": "Years"})
   world.update_layout(height=430, margin=dict(l=0, r=0, t=0, b=0))
   by_continent = latest.groupby("continent", as_index=False)["lifeExp"].mean().sort_values("lifeExp")
   bars = px.bar(by_continent, x="lifeExp", y="continent", orientation="h", template="plotly_white",
                 labels={"lifeExp": "Years", "continent": ""})
   bars.update_layout(height=260, margin=dict(l=10, r=10, t=10, b=10))

   slide = Slide()
   slide.add_title("Europe lives 23 years longer than Africa")
   slide.add_layout(
       Row(
           [
               Column(7, world),
               Column(5, [Row(bars), Row("Mean of the countries of each continent, 2007.")],
                      font_size="70%"),
           ],
           gap=4,
       )
   )

   deck = Presentation()
   deck.add_slide([slide])
   deck.save_html("nested.html", theme="sober")

Rows and columns nest to any depth: a row inside a column can hold columns
again. :ref:`sphx_glr_gallery_plot_02_layouts.py` shows three levels, with
the code of each block written above it.

Options
-------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Argument
     - Effect
   * - ``Row(gap=3)``
     - Space between the columns, from 0 to 5
   * - ``Row(align_items="center")``
     - Vertical alignment: ``"start"``, ``"center"``, ``"end"``, ``"stretch"``
   * - ``Row(justify_content="between")``
     - Spread of the columns: ``"start"``, ``"center"``, ``"between"``, ``"around"``, ``"evenly"``
   * - ``Column(6, x, offset=3)``
     - Shift the column right by 3 columns
   * - ``Column(6, x, order="first")``
     - Change the order in which columns are shown
   * - ``Column(6, x, content_height=500)``
     - Size of the chart or map inside the column

Both classes accept CSS as keyword arguments, written with underscores
(``background_color="#f1faee"``), plus ``class`` for Bootstrap classes and
``style`` for raw CSS.

Sizes that fit the slide
------------------------

A slide is 1280 x 720 pixels. Charts are easier to place with an explicit
height: about 500 pixels under a title for a full-width chart, half of
that for two stacked rows. When the content is taller than the slide, it
is scaled down to fit, as :doc:`overflow` explains, and the layout itself
is kept.
