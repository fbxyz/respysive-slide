Installation
============

respysive-slide requires Python 3.10 or later.

.. code-block:: bash

   pip install respysive-slide

The package itself depends on Bootstrap and a few browser libraries that
the HTML file loads from a CDN. Chart libraries are optional: install the
ones you use.

.. code-block:: bash

   pip install plotly altair matplotlib markdown

Exports
-------

PDF and PowerPoint files are rendered by headless Chromium, through
Playwright. PowerPoint also needs ``python-pptx``.

.. code-block:: bash

   pip install "respysive-slide[pptx]"
   python -m playwright install chromium

Without Chromium, ``save_pdf`` and ``save_pptx`` stop with an error that
gives these two commands.

Maps drawn with mappyng need that package. mappyng 2, the version
respysive works with, will be published soon. MapLibre maps need nothing more than a network connection when
the deck is shown.

Development version
-------------------

.. code-block:: bash

   git clone https://github.com/fbxyz/respysive-slide
   cd respysive-slide
   pip install -e ".[dev]"
   python -m playwright install chromium
   pytest tests/

The documentation is built with Sphinx:

.. code-block:: bash

   pip install -e ".[docs]"
   cd docs && make html
