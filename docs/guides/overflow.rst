Content taller than the slide
=============================

A slide has a fixed size, 1280 x 720 pixels unless ``save_html`` sets
another ``width`` and ``height``. The window only scales it. When the
content of a slide is taller than the slide, respysive fits it in two
stages.

First, the text shrinks, down to 60% of its size. Titles sized with
``r-fit-text``, images, and charts keep their size. This is often enough
for a long list or table, as on the first slide below.

If the text alone does not make it fit, the whole content scales down
instead, like a picture, as on the second slide. Line breaks stay where
they were. The browser console warns when a slide is scaled below 50%,
which usually means it should be split.

.. respysive-demo::

   import plotly.express as px
   from markdown import markdown
   from respysive import Presentation, Slide

   latest = px.data.gapminder().query("year == 2007").nlargest(14, "pop")
   items = markdown("\n".join(f"- {r.country}: {r.lifeExp:.1f} years" for r in latest.itertuples()))

   text = Slide()
   text.add_title(f"The {len(latest)} most populated countries live {latest.lifeExp.min():.0f} to {latest.lifeExp.max():.0f} years")
   text.add_content([items])

   bars = px.bar(latest.sort_values("lifeExp"), x="lifeExp", y="country", orientation="h",
                 template="plotly_white", labels={"lifeExp": "Years", "country": ""})
   bars.update_layout(height=640, margin=dict(l=10, r=10, t=10, b=10))

   both = Slide()
   both.add_title("Japan lives longest among them, Nigeria shortest")
   both.add_content([items, bars], columns=[5, 7])

   deck = Presentation()
   deck.add_slide([text, both])
   deck.save_html("overflow.html", theme="sober")

The fitting is computed at the native size of the slide, so the result is
identical in a small window, on a projector, and in the exported PDF and
PowerPoint files.

Choosing the behaviour
----------------------

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - ``overflow``
     - Behaviour
   * - ``"fit"``
     - Default. Shrink the text, then scale the content.
   * - ``"warn"``
     - Leave the content as it is and log the slide in the browser console.
   * - ``"visible"``
     - Leave the content as it is: it runs over the edges of the slide.

The value applies to one slide with ``Slide(overflow=...)``, or to every
slide with ``save_html(..., overflow=...)``.

.. _checking-a-deck:

Checking a deck
---------------

A slide that fits can still be too small to read. ``check`` opens the deck
in headless Chromium, as the exports do, and reports the scale of the text
on each slide. Slides below ``min_scale`` are flagged:

.. code-block:: python

   report = deck.check(min_scale=0.7, theme="sober")
   print(report)

.. code-block:: text

       1  A list of 14 countries: the text shrinks  text at 82%
       2  The same list next to a tall chart: eve…  text at 61%  too small; pictures: 1 Plotly chart

   1 slide(s) below 70%, 0 overflowing.
   Network: cdn.plot.ly, cdnjs.cloudflare.com, stackpath.bootstrapcdn.com

``report.small`` holds the slides below the threshold and ``report.ok`` is
``False`` when there is one, which suits a test or a build script:

.. code-block:: python

   assert deck.check().ok, "some slides are too dense"

The report also lists what becomes a picture in the PowerPoint export and
the hosts the deck loads from. ``check`` takes the options of
``save_html``, so the check matches the file.

In the browser, ``respysive.overflowReport()`` gives the same figures for
the open deck.
