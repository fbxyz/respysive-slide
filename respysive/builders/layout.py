"""Builder for Row and Column Bootstrap grid layouts.

This module provides the LayoutBuilder class for generating Bootstrap grid HTML
from Row and Column objects. It handles recursive layout generation, styling,
and content processing through the respysive handler system.
"""


class LayoutBuilder:
    """Builder for Row and Column Bootstrap grid layouts.

    Handles recursive HTML generation for nested Row/Column structures,
    applying Bootstrap grid classes, gap utilities, alignment, and custom styling.

    The builder integrates with the respysive content detection system to process
    nested content items through registered handlers (charts, images, text, etc.).

    Args:
        content_instance: Content object for shared data management
        content_detector: ContentDetector instance for processing nested content

    Attributes:
        content: Content object reference
        content_detector: ContentDetector reference for recursive processing

    Example:
        >>> builder = LayoutBuilder(content_obj, content_detector)
        >>> html = builder.build_row(row_instance)
    """

    def __init__(self, content_instance, content_detector):
        """Initialize LayoutBuilder with content and detector instances.

        Args:
            content_instance: Content object for data storage
            content_detector: ContentDetector for processing content items
        """
        self.content = content_instance
        self.content_detector = content_detector

    def build_row(self, row):
        """Build HTML for a Row object.

        Generates Bootstrap row HTML with appropriate grid classes, gap utilities,
        alignment classes, and custom styling. Processes each content item
        recursively, handling Columns, nested Rows, and regular content.

        Args:
            row: Row instance with content and styling parameters

        Returns:
            str: HTML string with row container and nested columns

        Example:
            >>> row = Row([Column(8, chart), Column(4, text)], gap=3)
            >>> html = builder.build_row(row)
            >>> # Returns: <div class='row g-3'><div class='col-md-8'>...</div>...</div>
        """
        from respysive.errors import validate_row_column_sum
        from respysive.layout import Column, Row
        from respysive.utils import _parse_style_class

        row_classes = ["row"]

        if row.gap is not None:
            if isinstance(row.gap, int):
                row_classes.append(f"g-{row.gap}")
            else:
                row_classes.append(str(row.gap))

        if row.align_items:
            row_classes.append(f"align-items-{row.align_items}")

        if row.justify_content:
            row_classes.append(f"justify-content-{row.justify_content}")

        row_kwargs = {"class": row_classes}
        if row.kwargs:
            if "class" in row.kwargs:
                user_classes = row.kwargs["class"]
                if isinstance(user_classes, str):
                    row_classes.append(user_classes)
                elif isinstance(user_classes, list):
                    row_classes.extend(user_classes)
                row_kwargs["class"] = row_classes
                for k, v in row.kwargs.items():
                    if k != "class":
                        row_kwargs[k] = v
            else:
                row_kwargs.update(row.kwargs)

        row_style_attr = _parse_style_class(row_kwargs)

        all_columns = all(isinstance(item, Column) for item in row.content)
        if all_columns:
            validate_row_column_sum(row.content, context="Row.build_row")

        columns_html = ""
        for item in row.content:
            if isinstance(item, Column):
                columns_html += self.build_column(item)
            elif isinstance(item, Row):
                columns_html += self.build_row(item)
            else:
                columns_html += self._build_auto_column(item)

        return f"<div {row_style_attr}>{columns_html}</div>"

    def build_column(self, column):
        """Build HTML for a Column object.

        Generates Bootstrap column HTML with appropriate grid classes, offset,
        order, and custom styling. Processes nested content recursively,
        handling Rows, Columns, and regular content items.

        Args:
            column: Column instance with width, content, and styling parameters

        Returns:
            str: HTML string with column container and nested content

        Example:
            >>> col = Column(8, chart, padding='10px', **{'class': 'border'})
            >>> html = builder.build_column(col)
            >>> # Returns: <div class='col-md-8 border' style='padding: 10px;'>...</div>
        """
        from respysive.layout import Column, Row
        from respysive.utils import _parse_style_class

        col_classes = []

        if isinstance(column.width, int):
            col_classes.append(f"col-md-{column.width}")
        elif isinstance(column.width, dict):
            for breakpoint, width in column.width.items():
                col_classes.append(f"col-{breakpoint}-{width}")
        elif column.width == "auto":
            col_classes.append("col-auto")

        if column.offset is not None:
            col_classes.append(f"offset-md-{column.offset}")

        if column.order is not None:
            if isinstance(column.order, int):
                col_classes.append(f"order-{column.order}")
            else:
                col_classes.append(f"order-{column.order}")

        dimension_params = ["content_height", "content_width"]
        content_kwargs = {}
        col_kwargs = {"class": col_classes}

        if column.kwargs:
            for param in dimension_params:
                if param in column.kwargs:
                    handler_param = param.replace("content_", "")
                    content_kwargs[handler_param] = column.kwargs[param]

            if "class" in column.kwargs:
                user_classes = column.kwargs["class"]
                if isinstance(user_classes, str):
                    col_classes.append(user_classes)
                elif isinstance(user_classes, list):
                    col_classes.extend(user_classes)
                col_kwargs["class"] = col_classes
                for k, v in column.kwargs.items():
                    if k != "class" and k not in dimension_params:
                        col_kwargs[k] = v
            else:
                for k, v in column.kwargs.items():
                    if k not in dimension_params:
                        col_kwargs[k] = v

        col_style_attr = _parse_style_class(col_kwargs)

        content_html = ""
        for item in column.content:
            if isinstance(item, Row):
                content_html += self.build_row(item)
            elif isinstance(item, Column):
                content_html += f"<div class='row'>{self.build_column(item)}</div>"
            else:
                content_html += self.content_detector.detect_and_handle(item, **content_kwargs)

        return f"<div {col_style_attr}>{content_html}</div>"

    def build_standalone_column(self, column):
        """Build HTML for a standalone Column (wrap in row).

        When a Column is used directly without being inside a Row, this method
        wraps it in a row container to maintain proper Bootstrap grid structure.

        Args:
            column: Column instance to wrap

        Returns:
            str: HTML with row wrapper around column

        Example:
            >>> col = Column(12, content)
            >>> html = builder.build_standalone_column(col)
            >>> # Returns: <div class='row'><div class='col-md-12'>...</div></div>
        """
        column_html = self.build_column(column)
        return f"<div class='row'>{column_html}</div>"

    def _build_auto_column(self, content):
        """Wrap regular content in full-width column.

        When content that is not a Row or Column is used in a Row, this method
        automatically wraps it in a full-width (col-md-12) column container.

        Args:
            content: Any content to wrap (chart, image, text, etc.)

        Returns:
            str: HTML with col-md-12 wrapper around processed content

        Example:
            >>> html = builder._build_auto_column(my_chart)
            >>> # Returns: <div class='col-md-12'>[processed chart HTML]</div>
        """
        content_html = self.content_detector.detect_and_handle(content)
        return f"<div class='col-md-12'>{content_html}</div>"
