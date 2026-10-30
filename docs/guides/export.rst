Saving and exporting
====================

One deck gives three files. What each one keeps:

.. list-table::
   :header-rows: 1
   :widths: 22 22 18 22 16

   * - Content
     - HTML
     - PDF
     - PowerPoint
     - ``offline=True``
   * - Text, lists, tables
     - Text
     - Vector text
     - Editable text
     - Works
   * - Equations
     - Rendered by MathJax
     - Vector
     - Picture
     - Works
   * - Plotly
     - Interactive
     - Vector
     - Native chart for bars, lines, scatter plots, and pies, picture otherwise
     - Works
   * - Altair
     - Interactive
     - Vector
     - Picture
     - Works
   * - Matplotlib, mappyng
     - SVG, with mappyng tooltips
     - Vector
     - Picture
     - Works
   * - MapLibre
     - Interactive
     - Picture
     - Picture
     - Needs the network for tiles
   * - Images
     - Embedded
     - Embedded
     - Picture
     - Works

:meth:`~respysive.Presentation.check` lists, slide by slide, what becomes a
picture and which hosts the deck still loads from, before any export (see
:ref:`checking-a-deck`).

HTML
----

``save_html`` writes the deck, and ``to_html`` returns the same document
as a string. The main options:

.. list-table::
   :header-rows: 1
   :widths: 22 18 60

   * - Option
     - Default
     - Effect
   * - ``theme``
     - ``"moon"``
     - Reveal.js theme name, ``"custom"``, or ``None``
   * - ``width``, ``height``
     - 1280, 720
     - Slide size in pixels
   * - ``margin``
     - 0.04
     - Space around the slide, as a share of the window
   * - ``center``
     - ``True``
     - Centre the content of each slide vertically
   * - ``transition``
     - ``"slide"``
     - ``"slide"``, ``"fade"`` or ``"none"``
   * - ``overflow``
     - ``"fit"``
     - See :doc:`overflow`
   * - ``controls``, ``progress``
     - ``True``
     - Navigation arrows and progress bar
   * - ``slide_number``
     - ``"c/t"``
     - ``"c/t"``, ``"c"``, ``"h.v"``, ``"h/v"`` or ``None``
   * - ``embedded``
     - ``False``
     - Size the deck to its parent element, to place it inside a page
   * - ``offline``
     - ``False``
     - Embed every library, stylesheet and font

Libraries
---------

The deck loads only the libraries its slides use: Plotly, Vega, MathJax,
D3, MapLibre, Font Awesome, and Bootstrap, which is always loaded.
``add_library`` forces one, or adds any script or stylesheet:

.. code-block:: python

   deck.add_library("mathjax")
   deck.add_library(js="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js")

Offline decks
-------------

With ``offline=True``, scripts, stylesheets, fonts, and Plotly's
geographic base maps are embedded in the HTML file, which then opens
without a network. Files are downloaded once into a local cache. To
prepare a computer that will be offline, fill the cache beforehand:

.. code-block:: python

   import respysive

   respysive.download_libraries()

Map tiles and remote images loaded by the page itself still need the
network.

PDF
---

.. code-block:: python

   deck.save_pdf("deck.pdf")
   deck.save_pdf("steps.pdf", fragments=True)

Headless Chromium prints one page per slide, at the size of the slide,
with the layout and fitting seen on screen. Text and charts stay vectors,
while MapLibre maps become pictures. With ``fragments=True``, a slide gets one
page per fragment step. ``save_pdf`` takes the options of ``save_html``.

The same layout comes from the browser: add ``?print-pdf`` to the address
of the deck, or print it with Ctrl+P.

PowerPoint
----------

.. code-block:: python

   deck.save_pptx("deck.pptx")

Each slide is rebuilt from the layout rendered by Chromium. Titles, text,
and lists become editable text boxes. Simple Plotly charts (bars, lines,
scatter plots, pies) become native PowerPoint charts, which can be edited
and restyled. Other charts, maps, images, and equations become pictures.
Card backgrounds and borders become shapes, and speaker notes are kept.

PowerPoint uses the fonts installed on the computer that opens the file.
Without the theme's fonts, text boxes shrink their text to fit. To keep
every chart as a picture:

.. code-block:: python

   from respysive.exporters import PptxExporter

   PptxExporter(deck, native_charts=False).save("deck.pptx")
