Handlers
========

Handlers turn an item given to ``add_content`` into HTML. See
:doc:`../guides/extending` to write one.

.. autoclass:: respysive.handlers.base.BaseHandler
   :members: priority, can_handle, handle

.. autoclass:: respysive.handlers.ContentDetector
   :members: register_handler, detect_and_handle

Built-in handlers
-----------------

.. autoclass:: respysive.handlers.PlotlyHandler
   :no-members:
   :no-special-members:

.. autoclass:: respysive.handlers.AltairHandler
   :no-members:
   :no-special-members:

.. autoclass:: respysive.handlers.MatplotlibHandler
   :no-members:
   :no-special-members:

.. autoclass:: respysive.handlers.MappyngHandler
   :no-members:
   :no-special-members:

.. autoclass:: respysive.handlers.MapLibreHandler
   :no-members:
   :no-special-members:

.. autoclass:: respysive.handlers.CustomJsonHandler
   :no-members:
   :no-special-members:

.. autoclass:: respysive.handlers.HtmlReprHandler
   :no-members:
   :no-special-members:

.. autoclass:: respysive.handlers.ImageHandler
   :no-members:
   :no-special-members:

.. autoclass:: respysive.handlers.VideoHandler
   :no-members:
   :no-special-members:

.. autoclass:: respysive.handlers.LatexHandler
   :no-members:
   :no-special-members:

.. autoclass:: respysive.handlers.TextHandler
   :no-members:
   :no-special-members:
