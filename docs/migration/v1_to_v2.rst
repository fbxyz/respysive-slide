From version 1 to version 2
===========================

Version 2 replaces Reveal.js with its own slide runtime, written for
respysive. Scripts written for version 1 run unchanged in most cases, and
this page lists what differs.

What stays the same
-------------------

The Python API of version 1 is kept: ``Presentation``, ``Slide``, and
their methods take the same arguments, and ``save_html`` accepts the same
options. The HTML keeps Reveal.js class names (``.reveal``, ``.slides``,
``section``, ``.controls``, ``.progress``, ``.slide-number``), so Reveal.js
themes and custom CSS written for them still apply. Slide backgrounds
(``data-background-*``) cover the window, as they did, and the layout
classes ``r-stack``, ``r-hstack``, ``r-vstack``, and ``r-fit-text`` work as
in Reveal.js.

What changes
------------

Content taller than the slide is now fitted (:doc:`../guides/overflow`).
In version 1 it ran off the edges of the slide. Decks that relied on this
may look smaller on some slides. ``save_html(overflow="visible")``
restores the old behaviour.

The ``margin`` option of ``save_html`` now defaults to 0.04 instead of
0.05, which makes slides slightly larger in the window.

Only the libraries a deck uses are loaded, where version 1 loaded all of
them. A script added to the page by hand that expects Plotly or MathJax to
be present may need ``deck.add_library("plotly")``.

JavaScript that calls the Reveal.js API (``Reveal.slide``,
``Reveal.getCurrentSlide``, ``Reveal.on``) has to be adapted, since
``window.Reveal`` no longer exists. The runtime exposes
``window.respysive``:

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - Reveal.js
     - respysive
   * - ``Reveal.slide(h, v, f)``
     - ``respysive.go(h, v, f)``
   * - ``Reveal.next()``, ``Reveal.prev()``
     - ``respysive.next()``, ``respysive.prev()``
   * - ``Reveal.getIndices()``
     - ``respysive.state()``
   * - ``Reveal.getCurrentSlide()``
     - ``document.querySelector("section.present")``
   * - ``Reveal.on("slidechanged", fn)``
     - ``respysive.on("slidechanged", fn)``

Reveal.js plugins and configuration options that have no ``save_html``
counterpart (``autoSlide``, ``loop``, ``parallaxBackgroundImage``, and so
on) are not available. The ``stretch`` and ``r-stretch`` classes have no
effect.

Python 3.10 or later is required.

What is new
-----------

Nested layouts with :class:`~respysive.Row` and
:class:`~respysive.Column`, fragments on every content method, export to
PDF (``save_pdf``) and PowerPoint (``save_pptx``) from the layout rendered
by the browser, offline decks (``offline=True``), and direct support for
mappyng maps, Altair chart objects, videos, and objects with a
``_repr_html_`` method.

What is removed
---------------

Geoviz maps are no longer supported. mappyng covers the same thematic maps
as static SVG, and MapLibre covers web maps.

The PowerPoint exporter that computed the layout in Python is removed,
together with its ``ChartConverter`` and the kaleido, cairosvg, and
vl-convert dependencies. ``save_pptx`` now always needs Chromium.
