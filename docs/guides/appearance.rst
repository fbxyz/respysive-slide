Appearance
==========

Themes
------

respysive has three themes of its own. Each sets the fonts, the sizes of
headings and text, the spacing, the style of lists and tables, and a
palette that Plotly and Altair charts take when the deck is drawn.

.. list-table::
   :header-rows: 1
   :widths: 18 82

   * - ``theme``
     - Look
   * - ``"sober"``
     - White page, dark grey text, one blue accent, system fonts
   * - ``"science"``
     - Serif headings, tables with rules above and below only, Okabe-Ito
       colours that stay distinct for colour-blind readers
   * - ``"corporate"``
     - Navy headings with an orange bar beside slide titles, dark table
       headers

The fonts are those installed on every computer (Segoe UI, Helvetica,
Georgia), so the PowerPoint export looks like the HTML deck.

.. respysive-demo::

   import plotly.express as px
   from respysive import Presentation, Slide

   data = px.data.gapminder().query("country in ['Brazil', 'China', 'France', 'Nigeria']")
   fig = px.line(data, x="year", y="lifeExp", color="country",
                 labels={"year": "", "lifeExp": "Life expectancy (years)", "country": ""})
   fig.update_layout(height=430, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=1.12))
   top = (px.data.gapminder().query("year == 2007").nlargest(5, "lifeExp")
          [["country", "lifeExp"]].set_index("country").round(1))

   chart = Slide()
   chart.add_title("China gained 29 years in half a century")
   chart.add_content([fig, "<ul><li>Brazil: 22 years</li><li>France: 13</li><li>Nigeria: 10</li></ul>"], columns=[8, 4])

   table = Slide()
   table.add_title("Japan has the longest lives in 2007")
   table.add_content([top], styles=[{"font-size": "80%"}])

   deck = Presentation()
   deck.add_slide([chart, table])
   deck.save_html("science.html", theme="science")

Charts keep the colours they set themselves. Only Plotly's default
colours are replaced, so a figure made with ``color_discrete_sequence`` or
explicit colours is drawn as it is. For a Matplotlib figure, which is drawn
in Python, :func:`respysive.palette` gives the colours of a theme:

.. code-block:: python

   import matplotlib.pyplot as plt
   import respysive

   plt.rc("axes", prop_cycle=plt.cycler(color=respysive.palette("science")))

Reveal.js themes and custom CSS
-------------------------------

``theme`` also takes the name of a `Reveal.js theme
<https://revealjs.com/themes/>`_: ``white``, ``black``, ``moon`` (the
default), ``night``, ``serif``, ``simple``, ``sky``, ``solarized``, and
others. Only the theme's CSS is used, and charts keep their own colours.
``theme="custom"`` with ``custom_theme`` loads your own stylesheet, from a
URL or a local file.

``add_custom_css`` adds CSS to every slide, after the theme. Themes read CSS variables, so a
few lines change the colours of the whole deck. A class given to a slide
lets the CSS target that slide alone.

.. respysive-demo::

   from respysive import Presentation, Slide

   CSS = """
   :root {
     --r-background-color: #0b2545;
     --r-main-color: #eef4ed;
     --r-heading-color: #f4a261;
     --r-heading-text-transform: none;
   }
   .reveal .slides section.branded::after {
     content: "World health, 2007"; position: absolute; right: 30px; bottom: 18px;
     font-size: 18px; opacity: 0.6;
   }
   """

   slide = Slide(center=True, **{"class": "branded"})
   slide.add_title("Life expectancy rose on every continent", tag="h2")
   slide.add_content(["From 1952 to 2007, Gapminder data."])

   deck = Presentation()
   deck.add_custom_css(CSS)
   deck.add_slide([slide])
   deck.save_html("dark.html", theme="night")

Backgrounds
-----------

A slide takes ``data-background-color``, ``data-background-gradient``,
``data-background-image``, ``data-background-size``,
``data-background-position``, ``data-background-repeat``, and
``data-background-opacity``, as in Reveal.js. On screen, the background
covers the whole window, beyond the edges of the slide, so a band or a
curve reaches the borders of the screen whatever its proportions. Sizes
and positions are therefore relative to the window. In the overview, in
PDF, and in PowerPoint, the background fills the slide. Images are
embedded in the HTML file.

.. respysive-demo::

   from respysive import Presentation, Slide

   gradient = Slide(center=True, **{"data-background-gradient": "linear-gradient(135deg, #1d3557, #457b9d)"})
   gradient.add_title("Does income explain longer lives?", tag="h2", color="#ffffff")

   image = Slide(center=True, **{
       "data-background-image": "data/life_curves.png",
       "data-background-size": "cover",
       "data-background-opacity": "0.25",
   })
   image.add_title("Life expectancy rose in 140 of 142 countries", tag="h2")

   deck = Presentation()
   deck.add_slide([gradient, image])
   deck.save_html("backgrounds.html", theme="sober")

Title pages
-----------

``add_title_page`` lays out a title, a subtitle, authors, and a logo.
``styles`` gives the CSS of each element, in that order, and
``background_image`` sets the slide background.

``add_split_title_page`` puts the title in one column and any content
(image, chart, text) in the other. ``title_column_width`` and
``custom_column_width`` share the 12 columns, and ``full_height=True``
makes both columns cover the slide.

.. respysive-demo::

   from respysive import Presentation, Slide

   slide = Slide()
   slide.add_split_title_page(
       {"title": "World health", "subtitle": "Gapminder data, 1952-2007", "authors": "Data team"},
       custom_content="data/life_curves.png",
       title_column_width=7,
       custom_column_width=5,
       full_height=True,
       title_column_style={"background-color": "#1d3557", "padding": "50px"},
       title_styles=[{"color": "#ffffff", "font-size": "70px"}, {"color": "#a8dadc"}, {"color": "#f1faee"}],
   )

   deck = Presentation()
   deck.add_slide([slide])
   deck.save_html("split_title.html", theme="sober")

Cards
-----

``add_card`` takes a list of dictionaries, one per card, with the keys
``title``, ``text``, ``image``, and ``graph``. ``title_style``,
``text_style``, and ``image_style`` hold the CSS of each part, and the
``styles`` argument holds the CSS or Bootstrap classes of each card.

.. respysive-demo::

   import plotly.express as px
   from respysive import Presentation, Slide

   japan = px.data.gapminder().query("country == 'Japan'")
   fig = px.line(japan, x="year", y="lifeExp", template="plotly_white", labels={"year": "", "lifeExp": ""})
   fig.update_layout(height=240, margin=dict(l=10, r=10, t=10, b=10))
   big = {"font-size": "140%", "color": "#e63946"}

   slide = Slide()
   slide.add_title("Japan gained 20 years to reach the longest lives")
   slide.add_card(
       [
           {"title": "82.6 years", "title_style": big, "text": "Life expectancy in 2007, the highest of the data set."},
           {"title": "Life expectancy", "graph": fig},
           {"title": "+19.6 years", "title_style": big, "text": "Gained since 1952."},
       ],
       styles=[{"class": "bg-light"}] * 3,
   )

   deck = Presentation()
   deck.add_slide([slide])
   deck.save_html("cards.html", theme="sober")
