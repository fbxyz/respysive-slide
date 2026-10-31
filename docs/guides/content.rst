Slide content
=============

Titles, text, and equations
---------------------------

``add_title`` writes a heading, ``h3`` by default. The ``icon`` argument
takes a `Font Awesome <https://fontawesome.com/icons>`_ class.

A string given to ``add_content`` is inserted as HTML. Markdown goes
through the ``markdown`` package first. Equations use LaTeX, between ``$``
signs inline and ``$$`` for a displayed formula. MathJax is loaded only
when a slide contains one.

.. respysive-demo::

   from markdown import markdown
   from respysive import Presentation, Slide

   slide = Slide()
   slide.add_title("A standardised rate does not depend on age structure", icon="fas fa-calculator")
   slide.add_content([markdown(
       "A crude rate divides the deaths by the population.\n\n"
       "- It depends on the **age structure**\n"
       "- Standardisation removes that effect"
   )])
   slide.add_content([r"$$\text{rate} = \sum_{a} w_a \, \frac{d_a}{p_a} \times 10^5$$"])

   deck = Presentation()
   deck.add_slide([slide])
   deck.save_html("text.html", theme="sober")

Images, videos, and tables
--------------------------

A local path or a URL ending in an image extension (``.png``, ``.jpg``,
``.svg``, ``.webp``, and others) becomes an image. Images are embedded in
the HTML file, which can then be moved or sent alone.

Videos (``.mp4``, ``.webm``, ``.ogg``, ``.mov``) are embedded the same
way. They play muted and in a loop, with the browser's controls. The
``autoplay``, ``loop``, ``muted``, and ``controls`` arguments of
``add_content`` change that, for example ``autoplay=False``. An embedded
video weighs about a third more than the original file, so short clips
work best.

Any object with a ``_repr_html_`` method, the protocol Jupyter uses, is
inserted through that method. A pandas ``DataFrame`` becomes a table.

.. respysive-demo::

   import plotly.express as px
   from respysive import Presentation, Slide

   top = (px.data.gapminder().query("year == 2007").nlargest(8, "lifeExp")
          [["country", "lifeExp"]].set_index("country").round(1))

   slide = Slide()
   slide.add_title("Japan, Hong Kong, and Iceland have the longest lives in 2007")
   slide.add_content(["data/life_curves.png", top], columns=[7, 5], styles=[None, {"font-size": "70%"}])

   deck = Presentation()
   deck.add_slide([slide])
   deck.save_html("media.html", theme="sober")

How the type is detected
------------------------

Each item goes through a list of handlers, and the first one that
recognises it renders it. When the guess is wrong, ``content_types`` names
the handler, one value per item (``None`` keeps the detection):

.. code-block:: python

   slide.add_content([fig_json, "plain text with a $ sign"], content_types=["plotly", "text"])

.. list-table::
   :header-rows: 1
   :widths: 18 82

   * - Name
     - Content
   * - ``"plotly"``
     - Plotly figure, its dictionary or JSON string
   * - ``"altair"``
     - Altair chart, or a Vega-Lite specification
   * - ``"matplotlib"``
     - Matplotlib ``Figure``, inserted as SVG
   * - ``"mappyng"``
     - mappyng ``Map`` or ``InteractiveMap``
   * - ``"maplibre"``
     - MapLibre map configuration (see :doc:`maps`)
   * - ``"json"``
     - ``{"library": ..., "config": ...}`` for another JavaScript library
   * - ``"html"``
     - Object with a ``_repr_html_`` method
   * - ``"image"``
     - Path or URL of an image
   * - ``"video"``
     - Path or URL of a video
   * - ``"latex"``
     - Text with LaTeX formulas
   * - ``"text"``
     - Text or HTML, inserted as it is

Speaker notes
-------------

``add_notes`` takes text, Markdown, or HTML. The notes appear in the
speaker view and are copied into the notes of the PowerPoint export.

.. code-block:: python

   slide.add_notes("Give the 2019 value for comparison.")
