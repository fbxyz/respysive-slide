Adding a content type
=====================

``add_content`` hands each item to a list of handlers, sorted by priority.
The first handler whose ``can_handle`` returns ``True`` renders the item
as HTML. A new content type is a new handler.

Writing a handler
-----------------

A handler subclasses :class:`~respysive.handlers.base.BaseHandler` and
defines three members: ``priority``, ``can_handle``, which tells whether
the handler accepts an item, and ``handle``, which receives the item and
the styles given to ``add_content`` for it, and returns HTML. The handler
is then registered on the slide's detector.

Below, a tuple of a quote and its author becomes a styled quotation:

.. respysive-demo::

   from respysive import Presentation, Slide
   from respysive.handlers.base import BaseHandler
   from respysive.utils import _parse_style_class


   class QuoteHandler(BaseHandler):
       """Render a (text, author) tuple as a quotation."""

       @property
       def priority(self):
           return 60

       def can_handle(self, content):
           return isinstance(content, tuple) and len(content) == 2 and all(isinstance(c, str) for c in content)

       def handle(self, content, shared_data_id=None, forced=False, **kwargs):
           text, author = content
           return (f"<blockquote {_parse_style_class(kwargs)}>{text}"
                   f"<br><small>{author}</small></blockquote>")


   slide = Slide(center=True)
   slide._content_detector.register_handler(QuoteHandler, slide.content_obj)
   slide.add_content([("The map is not the territory.", "Alfred Korzybski")], font_size="130%")

   deck = Presentation()
   deck.add_slide([slide])
   deck.save_html("quote.html", theme="sober")

Choosing the priority
---------------------

A lower number is tried first. The built-in handlers use these values:

.. list-table::
   :header-rows: 1
   :widths: 15 85

   * - Priority
     - Handlers
   * - 5 to 8
     - Custom JSON, layouts, mappyng, MapLibre, objects with ``_repr_html_``
   * - 10 to 30
     - Matplotlib, Plotly, Altair
   * - 40 to 50
     - Images, videos, LaTeX
   * - 100
     - Text, which accepts everything

A handler that recognises a narrow, unambiguous type can sit before the
others. One that relies on a loose test (a string containing some marker)
belongs after the chart handlers and before text, between 50 and 100.
