respysive-slide
===============

respysive-slide builds HTML presentations from Python. Slides are laid out
on a Bootstrap grid and hold text, images, Plotly, Altair and Matplotlib
charts, maps, and equations. The result is a single HTML file that opens in
any browser and exports to PDF and PowerPoint.

.. respysive-demo::
   :file: showcase.py
   :hide-code:

The deck above was written in Python with respysive-slide: click it and use
the arrow keys, or open it `in a page of its own <showcase.html>`_. Its code
is in `docs/examples/showcase.py
<https://github.com/fbxyz/respysive-slide/blob/master/docs/examples/showcase.py>`_.

The HTML file keeps charts and maps interactive. The PDF keeps text and
charts as vectors. The PowerPoint file keeps text editable, and simple
Plotly charts become native charts. Charts it cannot rebuild, maps, and
equations become pictures. :doc:`guides/export` has the table for each
kind of content.

A slide is drawn at a fixed size (1280 x 720 pixels by default), then scaled
to the window. Line breaks and positions are therefore the same on a laptop,
a projector, and in the exported files.

New users can start with :doc:`guides/quickstart`, then browse the
:doc:`gallery/index`, where each example shows its code above the deck it
produces. Users of version 1 will find the differences in
:doc:`migration/v1_to_v2`.

.. toctree::
   :maxdepth: 2
   :caption: Guides
   :hidden:

   guides/installation
   guides/quickstart
   guides/content
   guides/layout
   guides/charts
   guides/maps
   guides/presenting
   guides/appearance
   guides/overflow
   guides/export
   guides/extending

.. toctree::
   :maxdepth: 2
   :caption: Gallery
   :hidden:

   gallery/index

.. toctree::
   :maxdepth: 2
   :caption: API reference
   :hidden:

   api/presentation
   api/slide
   api/layout
   api/handlers
   api/exporters
   api/utilities

.. toctree::
   :maxdepth: 1
   :caption: Migration
   :hidden:

   migration/v1_to_v2
