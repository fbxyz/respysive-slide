Presenting
==========

Navigation
----------

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Key
     - Action
   * - Right, Left, Up, Down
     - Next or previous slide or fragment, in that direction
   * - Space, Page Down, Page Up
     - Next or previous step, in reading order
   * - Home, End
     - First or last slide
   * - Esc or O
     - Overview of all slides
   * - S
     - Speaker view
   * - F
     - Full screen
   * - B or .
     - Black screen

Swipes work on touch screens. The address ends with the current position
(``#/2/1`` for the second slide of the third column), so a link or a
reload opens the same slide.

Fragments
---------

Fragments make content appear one step at a time. ``fragment=True`` on
``add_title``, ``add_content``, or ``add_card`` reveals the whole item, and
``fragment_items`` reveals the items of a list one by one. A string picks
the effect. Click the deck below, then press the right arrow.

.. respysive-demo::

   from markdown import markdown
   from respysive import Presentation, Slide

   slide = Slide()
   slide.add_title("Three steps to a standardised rate")
   slide.add_content(
       [markdown("- Count the deaths by age group\n- Divide by the population of each group\n"
                 "- Weight the rates by a reference population")],
       fragment_items="fade-up",
   )
   slide.add_content(["The result no longer depends on the age structure."], fragment="highlight-red")

   deck = Presentation()
   deck.add_slide([slide])
   deck.save_html("fragments.html", theme="sober")

The effects are ``fade-up``, ``fade-down``, ``fade-left``,
``fade-right``, ``fade-out``, ``semi-fade-out``, ``grow``, ``shrink``,
``strike``, ``highlight-red``, ``highlight-green``, ``highlight-blue``, and
``current-visible``.

In raw HTML, the ``fragment`` class does the same, and Reveal.js layout
classes are supported: ``r-stack`` places its children on top of each
other (to swap two blocks), ``r-hstack`` and ``r-vstack`` line them up,
and ``r-fit-text`` sizes a line of text to the width of its container.
:ref:`sphx_glr_gallery_plot_05_fragments.py` swaps two charts this way.

Vertical slides
---------------

A list inside the list of slides makes a vertical stack: the first slide
is on the main row and the others are reached with the down arrow. This
suits details kept for questions.

.. respysive-demo::

   from respysive import Presentation, Slide

   def slide(title, text):
       s = Slide(center=True)
       s.add_title(title, tag="h2")
       s.add_content([text])
       return s

   deck = Presentation()
   deck.add_slide([
       slide("Introduction", "Right arrow: next topic."),
       [slide("Result", "Down arrow: the method."), slide("Method", "Up arrow: back to the result.")],
       slide("Conclusion", "Esc shows the overview of the whole deck."),
   ])
   deck.save_html("vertical.html", theme="sober")

Speaker view
------------

``S`` opens a second window with the current slide, the next one, the
notes, a clock, and a timer. A click on the timer resets it. Both windows
stay in step, and either one can be used to move through the deck.
