"""Layout classes for creating nested Bootstrap grid structures.

This module provides Row and Column classes for building complex nested layouts
as an alternative to the add_content() method. These classes enable explicit
control over Bootstrap grid structures while maintaining full compatibility with
the existing respysive architecture.

Example:
    >>> from respysive import Row, Column
    >>> layout = Row([
    ...     Column(8, my_chart),
    ...     Column(4, [
    ...         Row(text1),
    ...         Row(text2)
    ...     ])
    ... ])
    >>> slide.add_layout(layout)
"""


class Row:
    """Container for horizontal row layout in Bootstrap grid system.

    A Row creates a horizontal container (<div class="row">) that holds Column
    objects or other content. Rows can be nested inside Columns to create
    complex multi-level layouts.

    Args:
        content: Single content item or list of items. Items can be Column objects,
            Row objects (for nesting), or any content type supported by respysive
            (charts, images, text, etc.). Non-Column items are auto-wrapped in
            col-md-12 containers.
        gap (int or str, optional): Bootstrap gap utility for spacing between columns.
            Can be integer 0-5 for Bootstrap gap classes (g-0 to g-5), or a string
            for custom gap classes. Defaults to None (no gap).
        align_items (str, optional): Vertical alignment of columns within the row.
            One of: 'start', 'center', 'end', 'baseline', 'stretch'.
            Maps to Bootstrap align-items-* classes. Defaults to None.
        justify_content (str, optional): Horizontal alignment/distribution of columns.
            One of: 'start', 'center', 'end', 'between', 'around', 'evenly'.
            Maps to Bootstrap justify-content-* classes. Defaults to None.
        **kwargs: Additional CSS styles and classes to apply to the row.
            Use underscore notation for CSS properties (e.g., background_color='#fff').
            Use 'class' key for Bootstrap classes (string or list).

    Attributes:
        content (list): Normalized list of content items
        gap (int or str or None): Gap configuration
        align_items (str or None): Vertical alignment setting
        justify_content (str or None): Horizontal alignment setting
        kwargs (dict): Additional styling options

    Raises:
        ParameterValidationError: If parameters fail validation (empty content,
            invalid gap value, invalid alignment options, etc.)

    Examples:
        Simple two-column row::

            row = Row([
                Column(6, chart1),
                Column(6, chart2)
            ])

        Row with gap and alignment::

            row = Row([
                Column(4, image),
                Column(8, text)
            ], gap=3, align_items='center')

        Row with custom styling::

            row = Row([content1, content2],
                      background_color='#f8f9fa',
                      padding='20px',
                      **{'class': 'border'})

        Nested row structure::

            row = Row([
                Column(8, main_content),
                Column(4, [
                    Row(sidebar_item1),
                    Row(sidebar_item2)
                ])
            ])
    """

    def __init__(self, content, gap=None, align_items=None, justify_content=None, **kwargs):
        """Create a Row with the given content and layout options.

        Args:
            content: Single item or list of items (Column, Row, or raw content).
            gap: Bootstrap gap class (0-5) or custom string.
            align_items: Vertical alignment ('start', 'center', 'end', 'baseline', 'stretch').
            justify_content: Horizontal distribution ('start', 'center', 'end', 'between', 'around', 'evenly').
            **kwargs: CSS styles and classes for the row div.
        """
        if not isinstance(content, list):
            self.content = [content]
        else:
            self.content = content

        self.gap = gap
        self.align_items = align_items
        self.justify_content = justify_content
        self.kwargs = kwargs

        self._validate()

    def _validate(self):
        """Validate Row parameters at construction time.

        Raises:
            ParameterValidationError: If any parameter fails validation
        """
        from respysive.errors import validate_row_parameters

        validate_row_parameters(self.content, self.gap, self.align_items, self.justify_content, self.kwargs)


class Column:
    """Container for column layout in Bootstrap grid system.

    A Column creates a vertical container (``<div class="col-md-N">``) within a Row.
    Columns define the width and positioning of content within the Bootstrap
    12-column grid system. They can contain any content type, including nested Rows.

    Args:
        width (int or str or dict): Column width: an integer from 1 to 12
            (``col-md-{width}``), ``'auto'`` for a column sized by its content,
            or a dictionary of widths per breakpoint such as
            ``{'md': 8, 'sm': 12}`` (breakpoints ``'xs'``, ``'sm'``, ``'md'``,
            ``'lg'``, ``'xl'``, ``'xxl'``).
        content: Content to display in the column. Can be a single item or list of items.
            Items can be Row objects (for nesting), Column objects, or any content type
            supported by respysive (charts, images, text, etc.).
        offset (int, optional): Number of columns to offset (shift right) this column.
            Must be 0-11. Creates space before the column. Defaults to None.
        order (int or str, optional): Visual order of the column: an integer
            from 1 to 12, ``'first'`` or ``'last'``. Defaults to None (source order).
        **kwargs: Additional CSS styles and classes to apply to the column.
            Use underscore notation for CSS properties (e.g., padding='20px').
            Use 'class' key for Bootstrap classes (string or list).
            ``content_width`` and ``content_height`` set the size of the chart
            or map inside the column (e.g., 800, '90%', '500px').

    Attributes:
        width (int or str or dict): Width configuration
        content (list): Normalized list of content items
        offset (int or None): Offset setting
        order (int or str or None): Order setting
        kwargs (dict): Additional styling options

    Raises:
        ParameterValidationError: If parameters fail validation (invalid width,
            empty content, invalid offset/order values, etc.)

    Examples:
        Fixed width column::

            col = Column(8, my_chart)

        Auto-sized column::

            col = Column('auto', small_widget)

        Responsive column (8 cols on desktop, full width on mobile)::

            col = Column({'md': 8, 'sm': 12}, content)

        Column with offset and styling::

            col = Column(6, content,
                         offset=3,  # Center in 12-col grid
                         padding='15px',
                         **{'class': 'border'})

        Column with content dimensions::

            col = Column(8, map_config,
                        content_width=800,
                        content_height=600)

        Column with nested rows::

            col = Column(4, [
                Row(header_text),
                Row(image),
                Row(footer_text)
            ])

        Column with custom order (display second visually, first in markup)::

            col = Column(6, content, order=2)
    """

    def __init__(self, width, content, offset=None, order=None, **kwargs):
        """Create a Column with the given width and content.

        Args:
            width: Column width (int 1-12, 'auto', or dict of breakpoints).
            content: Single item or list of items to display.
            offset: Column offset in grid units (0-11).
            order: Visual order (int 1-12, 'first', or 'last').
            **kwargs: CSS styles, classes, and content dimension overrides
                (content_width, content_height).
        """
        self.width = width

        if not isinstance(content, list):
            self.content = [content]
        else:
            self.content = content

        self.offset = offset
        self.order = order
        self.kwargs = kwargs

        self._validate()

    def _validate(self):
        """Validate Column parameters at construction time.

        Raises:
            ParameterValidationError: If any parameter fails validation
        """
        from respysive.errors import validate_column_parameters

        validate_column_parameters(self.width, self.content, self.offset, self.order, self.kwargs)
