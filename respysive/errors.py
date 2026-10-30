"""Parameter validation and error handling for Respysive Slide.

This module provides detailed error checking and user-friendly messages
for common parameter validation issues in slide creation.
"""


class RespysiveError(Exception):
    """Base exception for Respysive Slide errors."""

    pass


class ParameterValidationError(RespysiveError):
    """Exception raised for parameter validation errors with detailed guidance.

    This exception provides detailed error messages that include context,
    the problematic value, and actionable suggestions for fixing the issue.

    Attributes:
        parameter_name (str): Name of the parameter that caused the error
        provided_value: The actual value that was provided
        error_type (str): Description of the validation error
        suggestion (str, optional): Actionable suggestion for fixing the error
        context (str, optional): Method or context where the error occurred
    """

    def __init__(self, parameter_name, provided_value, error_type, suggestion=None, context=None):
        """Initialize the parameter validation error.

        Args:
            parameter_name (str): Name of the parameter that caused the error
            provided_value: The actual value that was provided
            error_type (str): Description of the validation error
            suggestion (str, optional): Actionable suggestion for fixing the error.
                Defaults to None.
            context (str, optional): Method or context where the error occurred.
                Defaults to None.
        """
        self.parameter_name = parameter_name
        self.provided_value = provided_value
        self.error_type = error_type
        self.suggestion = suggestion
        self.context = context

        message = self._build_message()
        super().__init__(message)

    def _build_message(self):
        """Build a detailed error message with context and suggestions.

        Returns:
            str: Complete formatted error message with context, problem description,
                provided value, and solution suggestion.
        """
        message_parts = []

        if self.context:
            message_parts.append(f"Error in {self.context}:")

        message_parts.append(f"Invalid '{self.parameter_name}': {self.error_type}")

        if self.provided_value is not None:
            message_parts.append(f"Provided: {self.provided_value}")

        if self.suggestion:
            message_parts.append(f"Solution: {self.suggestion}")

        return " ".join(message_parts)


def validate_bootstrap_columns(content_list, columns, context="add_content"):
    """Validate Bootstrap column configuration against content list.

    Validates that Bootstrap column specifications are properly formatted,
    contain valid values (1-12), and match the content list requirements.
    Ensures column sums don't exceed Bootstrap's 12-column grid system.

    Args:
        content_list (list): List of content items to be displayed.
            Must be non-empty list.
        columns (list or None): List of integer column widths (1-12).
            If None, defaults to [12] * len(content_list).
            Single values are automatically repeated.
        context (str, optional): Method name for error context.
            Defaults to "add_content".

    Raises:
        ParameterValidationError: If any of the following conditions are met:
            - content_list is not a list or is empty
            - columns is not a list (when not None)
            - column values are not integers between 1-12
            - column list length doesn't match content length
            - sum of columns exceeds 12 for multi-column layouts

    Example:
        >>> validate_bootstrap_columns(["text1", "text2"], [6, 6], "add_content")
        >>> validate_bootstrap_columns(["text"], [12])  # Valid
        >>> validate_bootstrap_columns(["a", "b"], [8, 6])  # Raises error: sum > 12
    """
    if not isinstance(content_list, list):
        raise ParameterValidationError(
            "content",
            type(content_list).__name__,
            "must be a list",
            "Pass content items as a list: [text1, text2] or [figure]",
            context,
        )

    if not content_list:
        raise ParameterValidationError(
            "content", "empty list", "cannot be empty", "Add at least one content item to the list", context
        )

    if columns is None:
        return  # Will use default [12] * len(content_list)

    if not isinstance(columns, list):
        raise ParameterValidationError(
            "columns",
            type(columns).__name__,
            "must be a list of integers",
            "Use [12] for single column, [6, 6] for two columns, [4, 4, 4] for three columns",
            context,
        )

    for i, col in enumerate(columns):
        if not isinstance(col, int):
            raise ParameterValidationError(
                f"columns[{i}]",
                f"{col} ({type(col).__name__})",
                "must be an integer between 1 and 12",
                "Use integers only: [6, 6] not [6.0, 6.0]",
                context,
            )

        if col < 1 or col > 12:
            raise ParameterValidationError(
                f"columns[{i}]",
                col,
                "must be between 1 and 12",
                "Bootstrap grid uses 12 columns max. Use values like 1, 2, 3, 4, 6, 8, 12",
                context,
            )

    if len(columns) != len(content_list):
        if len(columns) == 1 and len(content_list) > 1:
            return

        raise ParameterValidationError(
            "columns",
            f"length {len(columns)} for {len(content_list)} content items",
            "length mismatch",
            f"Use {len(content_list)} column values: {_suggest_columns(len(content_list))} or single value [12] to repeat",
            context,
        )

    if len(columns) > 1:
        total = sum(columns)
        if total > 12:
            raise ParameterValidationError(
                "columns",
                f"sum = {total}",
                "total width exceeds 12",
                f"Use combinations that sum to 12 or less: {_suggest_valid_combinations(len(columns))}",
                context,
            )


def validate_styles_length(styles, content_list, context="add_content"):
    """Validate that styles list length matches content list length.

    Ensures that when styles are provided, there is exactly one style
    dictionary for each content item to maintain consistent styling.

    Args:
        styles (list or None): List of style dictionaries, one per content item.
            Each dictionary contains CSS properties and Bootstrap classes.
            If None, validation passes (defaults will be used).
        content_list (list): List of content items that need styling.
        context (str, optional): Method name for error context.
            Defaults to "add_content".

    Raises:
        ParameterValidationError: If any of the following conditions are met:
            - styles is not a list (when not None)
            - length of styles doesn't match length of content_list

    Example:
        >>> content = ["text1", "text2"]
        >>> styles = [{'color': 'red'}, {'color': 'blue'}]  # Valid
        >>> validate_styles_length(styles, content)
        >>> validate_styles_length([{'color': 'red'}], content)  # Raises error
    """
    if styles is None:
        return  # Will use default empty styles

    if not isinstance(styles, list):
        raise ParameterValidationError(
            "styles",
            type(styles).__name__,
            "must be a list of dictionaries",
            "Use [{'class': 'bg-primary'}, {'color': 'blue'}] or None",
            context,
        )

    if len(styles) != len(content_list):
        raise ParameterValidationError(
            "styles",
            f"length {len(styles)} for {len(content_list)} content items",
            "length mismatch",
            f"Provide {len(content_list)} style dictionaries or use None for default styling",
            context,
        )


def validate_card_parameters(
    cards, styles=None, title_styles=None, text_styles=None, title_tags=None, context="add_card"
):
    """Validate card parameters for Bootstrap card creation.

    Performs comprehensive validation of card dictionaries and associated
    styling parameters to ensure proper card rendering.

    Args:
        cards (list): List of card dictionaries. Each dictionary can contain:
            - 'title' (str): Card title text
            - 'text' (str): Card body content
            - 'image' (str): Image URL or path
            - 'image_style' (dict): CSS styles for image
            - 'graph': Chart/graph object (matplotlib, plotly, etc.)
            Must be non-empty list of dictionaries.
        styles (list, optional): List of style dictionaries for each card.
            Length must match cards list. Defaults to None.
        title_styles (list, optional): List of style dictionaries for card titles.
            Length must match cards list. Defaults to None.
        text_styles (list, optional): List of style dictionaries for card text.
            Length must match cards list. Defaults to None.
        title_tags (list, optional): List of HTML heading tags (h1-h6) for titles.
            Length must match cards list. Defaults to None.
        context (str, optional): Method name for error context.
            Defaults to "add_card".

    Raises:
        ParameterValidationError: If any of the following conditions are met:
            - cards is not a list or is empty
            - any card is not a dictionary or is empty
            - cards contain invalid keys (not in: title, text, image, image_style, graph)
            - any style list length doesn't match cards list length
            - title_tags contains invalid HTML heading tags

    Example:
        >>> cards = [{'title': 'Card 1', 'text': 'Content'}]
        >>> validate_card_parameters(cards)  # Valid
        >>> validate_card_parameters([])  # Raises error: empty list
    """
    if not isinstance(cards, list):
        raise ParameterValidationError(
            "cards",
            type(cards).__name__,
            "must be a list of dictionaries",
            "Use [{'title': 'Card 1', 'text': 'Content'}]",
            context,
        )

    if not cards:
        raise ParameterValidationError(
            "cards", "empty list", "cannot be empty", "Add at least one card dictionary", context
        )

    for i, card in enumerate(cards):
        if not isinstance(card, dict):
            raise ParameterValidationError(
                f"cards[{i}]",
                type(card).__name__,
                "must be a dictionary",
                "Use {'title': 'My Title', 'text': 'My content'}",
                context,
            )

        valid_keys = {
            "title",
            "text",
            "image",
            "video",
            "graph",
            "title_style",
            "title_tag",
            "text_style",
            "image_style",
            "video_style",
        }
        invalid_keys = set(card.keys()) - valid_keys
        if invalid_keys:
            raise ParameterValidationError(
                f"cards[{i}]",
                f"invalid keys: {list(invalid_keys)}",
                "contains unsupported keys",
                f"Use only: {list(valid_keys)}",
                context,
            )

        if not card:
            raise ParameterValidationError(
                f"cards[{i}]", "empty dictionary", "cannot be empty", "Add at least 'title' or 'text' key", context
            )

    if styles is not None:
        validate_styles_length(styles, cards, f"{context} (styles)")

    if title_styles is not None:
        validate_styles_length(title_styles, cards, f"{context} (title_styles)")

    if text_styles is not None:
        validate_styles_length(text_styles, cards, f"{context} (text_styles)")

    if title_tags is not None:
        if not isinstance(title_tags, list):
            raise ParameterValidationError(
                "title_tags",
                type(title_tags).__name__,
                "must be a list of strings",
                "Use ['h2', 'h3', 'h4'] for different heading levels",
                context,
            )

        if len(title_tags) != len(cards):
            raise ParameterValidationError(
                "title_tags",
                f"length {len(title_tags)} for {len(cards)} cards",
                "length mismatch",
                f"Provide {len(cards)} title tags or use None for default",
                context,
            )

        valid_tags = ["h1", "h2", "h3", "h4", "h5", "h6"]
        for i, tag in enumerate(title_tags):
            if tag not in valid_tags:
                raise ParameterValidationError(
                    f"title_tags[{i}]", tag, "invalid HTML tag", f"Use one of: {valid_tags}", context
                )


def validate_title_page_parameters(title_page_content, styles=None, context="add_title_page"):
    """Validate title page parameters for presentation title slides.

    Validates the structure and content of title page dictionaries,
    ensuring all required elements are present and properly formatted.

    Args:
        title_page_content (dict): Dictionary containing title page elements.
            Valid keys are: 'title', 'subtitle', 'authors', 'logo'.
            At least one key must have a non-empty value.
        styles (list, optional): List of style dictionaries for each present element.
            Length must match number of non-empty elements in title_page_content.
            Order follows: title, subtitle, authors, logo (only present elements).
            Defaults to None.
        context (str, optional): Method name for error context.
            Defaults to "add_title_page".

    Raises:
        ParameterValidationError: If any of the following conditions are met:
            - title_page_content is not a dictionary
            - contains invalid keys (not in: title, subtitle, authors, logo)
            - all values are empty or missing
            - styles length doesn't match number of present elements

    Example:
        >>> content = {'title': 'My Presentation', 'authors': 'John Doe'}
        >>> validate_title_page_parameters(content)  # Valid
        >>> validate_title_page_parameters({})  # Raises error: empty content
    """
    if not isinstance(title_page_content, dict):
        raise ParameterValidationError(
            "title_page_content",
            type(title_page_content).__name__,
            "must be a dictionary",
            "Use {'title': 'My Title', 'subtitle': 'Subtitle', 'authors': 'Author Name'}",
            context,
        )

    valid_keys = {"title", "subtitle", "authors", "logo"}
    invalid_keys = set(title_page_content.keys()) - valid_keys
    if invalid_keys:
        raise ParameterValidationError(
            "title_page_content",
            f"invalid keys: {list(invalid_keys)}",
            "contains unsupported keys",
            f"Use only: {list(valid_keys)}",
            context,
        )

    present_elements = []
    for key in ["title", "subtitle", "authors", "logo"]:
        if title_page_content.get(key):
            present_elements.append(key)

    if not present_elements:
        raise ParameterValidationError(
            "title_page_content",
            "all values empty or missing",
            "must contain at least one non-empty element",
            "Add 'title', 'subtitle', 'authors', or 'logo'",
            context,
        )

    if styles is not None:
        if not isinstance(styles, list):
            raise ParameterValidationError(
                "styles",
                type(styles).__name__,
                "must be a list of dictionaries",
                f"Use [{len(present_elements)}] style dictionaries for: {present_elements}",
                context,
            )

        if len(styles) != len(present_elements):
            raise ParameterValidationError(
                "styles",
                f"length {len(styles)} for {len(present_elements)} elements",
                "length mismatch",
                f"Provide {len(present_elements)} style dictionaries for: {present_elements}",
                context,
            )


def validate_split_title_page_columns(title_column_width, custom_column_width, context="add_split_title_page"):
    """Validate Bootstrap column widths for split title page layout.

    Ensures that column widths for split title pages follow Bootstrap
    grid constraints and don't exceed the 12-column limit.

    Args:
        title_column_width (int): Width of the title column (1-12).
            Bootstrap column width for the title content section.
        custom_column_width (int): Width of the custom content column (1-12).
            Bootstrap column width for the custom content section.
        context (str, optional): Method name for error context.
            Defaults to "add_split_title_page".

    Raises:
        ParameterValidationError: If any of the following conditions are met:
            - either width is not an integer
            - either width is not between 1 and 12
            - sum of both widths exceeds 12

    Example:
        >>> validate_split_title_page_columns(6, 6)  # Valid: sum = 12
        >>> validate_split_title_page_columns(8, 4)  # Valid: sum = 12
        >>> validate_split_title_page_columns(8, 6)  # Raises error: sum > 12
    """
    for name, width in [("title_column_width", title_column_width), ("custom_column_width", custom_column_width)]:
        if not isinstance(width, int):
            raise ParameterValidationError(
                name,
                f"{width} ({type(width).__name__})",
                "must be an integer",
                "Use integer values between 1 and 12",
                context,
            )

        if width < 1 or width > 12:
            raise ParameterValidationError(
                name, width, "must be between 1 and 12", "Bootstrap grid uses 12 columns max", context
            )

    total = title_column_width + custom_column_width
    if total > 12:
        raise ParameterValidationError(
            "column widths",
            f"sum = {total}",
            "total exceeds 12",
            "Use combinations like (6,6), (8,4), (4,8), (3,9), (9,3)",
            context,
        )


def validate_maplibre_parameters(center, zoom=None, context="maplibre"):
    """Validate MapLibre GL JS map parameters for geographic correctness.

    Validates geographic coordinates and zoom levels to ensure MapLibre
    maps can be properly rendered with valid geographic data.

    Args:
        center (list): Center coordinates as [longitude, latitude].
            Longitude must be between -180 and 180 degrees.
            Latitude must be between -90 and 90 degrees.
            Both values must be numeric (int or float).
        zoom (int, optional): Map zoom level (0-20).
            0 = world view, 10 = city view, 15 = street view.
            If None, validation passes. Defaults to None.
        context (str, optional): Method name for error context.
            Defaults to "maplibre".

    Raises:
        ParameterValidationError: If any of the following conditions are met:
            - center is not a list
            - center doesn't contain exactly 2 coordinates
            - coordinates are not numeric (int/float)
            - longitude not in range [-180, 180]
            - latitude not in range [-90, 90]
            - zoom is not an integer (when provided)
            - zoom not in range [0, 20] (when provided)

    Example:
        >>> validate_maplibre_parameters([2.3522, 48.8566], 12)  # Paris, valid
        >>> validate_maplibre_parameters([0, 0])  # Equator/Prime meridian, valid
        >>> validate_maplibre_parameters([250, 0])  # Raises error: longitude > 180
    """
    if not isinstance(center, list):
        raise ParameterValidationError(
            "center",
            type(center).__name__,
            "must be a list of coordinates",
            "Use [longitude, latitude] like [2.3522, 48.8566]",
            context,
        )

    if len(center) != 2:
        raise ParameterValidationError(
            "center",
            f"length {len(center)}",
            "must contain exactly 2 coordinates",
            "Use [longitude, latitude] format",
            context,
        )

    for i, coord in enumerate(center):
        coord_name = "longitude" if i == 0 else "latitude"
        if not isinstance(coord, (int, float)):
            raise ParameterValidationError(
                f"center[{i}] ({coord_name})",
                f"{coord} ({type(coord).__name__})",
                "must be a number",
                "Use decimal coordinates like 2.3522 or 48.8566",
                context,
            )

    if not -180 <= center[0] <= 180:
        raise ParameterValidationError(
            "center[0] (longitude)",
            center[0],
            "must be between -180 and 180",
            "Check coordinate system. Paris longitude is 2.3522",
            context,
        )

    if not -90 <= center[1] <= 90:
        raise ParameterValidationError(
            "center[1] (latitude)",
            center[1],
            "must be between -90 and 90",
            "Check coordinate system. Paris latitude is 48.8566",
            context,
        )

    if zoom is not None:
        if not isinstance(zoom, int):
            raise ParameterValidationError(
                "zoom",
                f"{zoom} ({type(zoom).__name__})",
                "must be an integer",
                "Use integer values like 10, 12, 15",
                context,
            )

        if not 0 <= zoom <= 20:
            raise ParameterValidationError(
                "zoom",
                zoom,
                "must be between 0 and 20",
                "Use 0 for world view, 10 for city view, 15 for street view",
                context,
            )


def validate_heading_tag(tag, context="add_heading"):
    """Validate HTML heading tag for proper semantic structure.

    Ensures that heading tags conform to HTML5 semantic standards
    and accessibility best practices.

    Args:
        tag (str): HTML heading tag to validate.
            Must be one of: 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'.
        context (str, optional): Method name for error context.
            Defaults to "add_heading".

    Raises:
        ParameterValidationError: If tag is not a valid HTML heading tag.

    Example:
        >>> validate_heading_tag('h1')  # Valid
        >>> validate_heading_tag('h3')  # Valid
        >>> validate_heading_tag('h7')  # Raises error: invalid tag
    """
    valid_tags = ["h1", "h2", "h3", "h4", "h5", "h6"]
    if tag not in valid_tags:
        raise ParameterValidationError("tag", tag, "invalid HTML heading tag", f"Use one of: {valid_tags}", context)


def validate_text_tag(tag, context="add_text"):
    """Validate HTML text tag for proper content structure.

    Ensures that text tags are appropriate for inline or block text content
    and follow HTML5 semantic guidelines.

    Args:
        tag (str): HTML text tag to validate.
            Must be one of: 'p' (paragraph), 'span' (inline).
        context (str, optional): Method name for error context.
            Defaults to "add_text".

    Raises:
        ParameterValidationError: If tag is not a valid HTML text tag.

    Example:
        >>> validate_text_tag('p')    # Valid: paragraph
        >>> validate_text_tag('span') # Valid: inline span
        >>> validate_text_tag('div')  # Raises error: not supported
    """
    valid_tags = ["p", "span"]
    if tag not in valid_tags:
        raise ParameterValidationError("tag", tag, "invalid HTML text tag", f"Use one of: {valid_tags}", context)


def _suggest_columns(num_items):
    """Suggest valid Bootstrap column configurations for given number of items.

    Provides commonly used column combinations that work well for different
    numbers of content items while respecting the 12-column Bootstrap grid.

    Args:
        num_items (int): Number of content items that need column layout.

    Returns:
        str: Suggested column combinations as formatted string.
            Examples: "[6, 6] or [8, 4] or [4, 8]" for 2 items.

    Note:
        This is an internal helper function for generating user-friendly
        suggestions in error messages.
    """
    suggestions = {
        1: "[12]",
        2: "[6, 6] or [8, 4] or [4, 8]",
        3: "[4, 4, 4] or [6, 3, 3] or [3, 6, 3] or [3, 3, 6]",
        4: "[3, 3, 3, 3] or [6, 2, 2, 2]",
        5: "[2, 2, 2, 3, 3]",
        6: "[2, 2, 2, 2, 2, 2]",
    }
    return suggestions.get(num_items, "[2, 2, 2, 2, 2, 2] (adjust to fit 12 columns)")


def _suggest_valid_combinations(num_columns):
    """Suggest valid Bootstrap column combinations that sum to 12 or less.

    Provides practical column width combinations for multi-column layouts
    that respect Bootstrap's 12-column grid system constraints.

    Args:
        num_columns (int): Number of columns in the layout.

    Returns:
        str: Suggested valid column combinations as formatted string.
            Examples: "[6, 6], [8, 4], [4, 8], [9, 3], [3, 9]" for 2 columns.

    Note:
        This is an internal helper function for generating user-friendly
        suggestions in error messages when column sums exceed 12.
    """
    suggestions = {
        2: "[6, 6], [8, 4], [4, 8], [9, 3], [3, 9]",
        3: "[4, 4, 4], [6, 3, 3], [3, 6, 3], [3, 3, 6]",
        4: "[3, 3, 3, 3], [6, 2, 2, 2], [2, 2, 2, 6]",
    }
    return suggestions.get(num_columns, "combinations that sum to 12 or less")


def validate_row_parameters(content, gap=None, align_items=None, justify_content=None, kwargs=None, context="Row"):
    """Validate Row constructor parameters for Bootstrap grid layouts.

    Ensures that Row parameters conform to Bootstrap grid specifications
    and respysive conventions for creating valid horizontal layouts.

    Args:
        content (list): List of content items (Columns or other content).
            Must be non-empty list.
        gap (int or str, optional): Bootstrap gap utility (0-5 or CSS value).
            Integer values map to Bootstrap gap classes (g-0 to g-5).
            String values are used as-is for custom gap classes.
            Defaults to None.
        align_items (str, optional): Vertical alignment option.
            One of: 'start', 'center', 'end', 'baseline', 'stretch'.
            Defaults to None.
        justify_content (str, optional): Horizontal alignment option.
            One of: 'start', 'center', 'end', 'between', 'around', 'evenly'.
            Defaults to None.
        kwargs (dict, optional): Additional styling parameters.
            Defaults to None.
        context (str, optional): Error context for messages.
            Defaults to "Row".

    Raises:
        ParameterValidationError: If any of the following conditions are met:
            - content is empty
            - gap is not a valid Bootstrap value (0-5) when integer
            - align_items is not in valid alignment options
            - justify_content is not in valid justification options

    Example:
        >>> validate_row_parameters([col1, col2], gap=3, align_items='center')
        >>> validate_row_parameters([content], gap='g-custom')  # Valid
        >>> validate_row_parameters([], gap=2)  # Raises error: empty content
        >>> validate_row_parameters([col], gap=10)  # Raises error: invalid gap
    """
    if not content:
        raise ParameterValidationError(
            "content", "empty list", "cannot be empty", "Row must contain at least one item or Column", context
        )

    if gap is not None:
        valid_gaps = [0, 1, 2, 3, 4, 5]
        if isinstance(gap, int) and gap not in valid_gaps:
            raise ParameterValidationError(
                "gap",
                gap,
                "invalid gap value",
                f"Use Bootstrap gap values: {valid_gaps} or CSS string like 'g-2'",
                context,
            )

    if align_items is not None:
        valid_alignments = ["start", "center", "end", "baseline", "stretch"]
        if align_items not in valid_alignments:
            raise ParameterValidationError(
                "align_items", align_items, "invalid alignment", f"Use one of: {valid_alignments}", context
            )

    if justify_content is not None:
        valid_justify = ["start", "center", "end", "between", "around", "evenly"]
        if justify_content not in valid_justify:
            raise ParameterValidationError(
                "justify_content", justify_content, "invalid justification", f"Use one of: {valid_justify}", context
            )


def validate_column_parameters(width, content, offset=None, order=None, kwargs=None, context="Column"):
    """Validate Column constructor parameters for Bootstrap grid layouts.

    Ensures that Column parameters conform to Bootstrap grid specifications
    and respysive conventions for creating valid vertical column containers.

    Args:
        width (int or str or dict): Column width specification.
            - int: Must be 1-12 for Bootstrap grid
            - str: Must be 'auto' for auto-sized columns
            - dict: Responsive widths with valid breakpoints and values
        content (list): Content items for column. Must be non-empty.
        offset (int, optional): Column offset (0-11). Defaults to None.
        order (int or str, optional): Column order (1-12 or 'first'/'last').
            Defaults to None.
        kwargs (dict, optional): Additional styling. Defaults to None.
        context (str, optional): Error context. Defaults to "Column".

    Raises:
        ParameterValidationError: If any of the following conditions are met:
            - width is integer not in range 1-12
            - width is dict with invalid breakpoints or values
            - width is string other than 'auto'
            - content is empty
            - offset is not integer 0-11
            - order is not integer 1-12 or 'first'/'last'

    Example:
        >>> validate_column_parameters(8, [content])  # Valid
        >>> validate_column_parameters('auto', [widget])  # Valid
        >>> validate_column_parameters({'md': 8, 'sm': 12}, [content])  # Valid
        >>> validate_column_parameters(0, [content])  # Raises error: width < 1
        >>> validate_column_parameters(8, [])  # Raises error: empty content
    """
    if isinstance(width, int):
        if width < 1 or width > 12:
            raise ParameterValidationError(
                "width",
                width,
                "must be between 1 and 12",
                "Bootstrap grid uses 12 columns max. Use values like 4, 6, 8, 12",
                context,
            )
    elif isinstance(width, dict):
        valid_breakpoints = ["xs", "sm", "md", "lg", "xl", "xxl"]
        for bp, w in width.items():
            if bp not in valid_breakpoints:
                raise ParameterValidationError(
                    f"width['{bp}']",
                    bp,
                    "invalid breakpoint",
                    f"Use Bootstrap breakpoints: {valid_breakpoints}",
                    context,
                )
            if not isinstance(w, int) or w < 1 or w > 12:
                raise ParameterValidationError(
                    f"width['{bp}']", w, "must be integer between 1 and 12", "Use values like 4, 6, 8, 12", context
                )
    elif width != "auto":
        raise ParameterValidationError(
            "width",
            width,
            "invalid width type",
            "Use integer (1-12), 'auto', or dict for responsive {'md': 8}",
            context,
        )

    if not content:
        raise ParameterValidationError(
            "content", "empty", "cannot be empty", "Column must contain at least one content item", context
        )

    if offset is not None:
        if not isinstance(offset, int) or offset < 0 or offset > 11:
            raise ParameterValidationError(
                "offset",
                offset,
                "must be integer between 0 and 11",
                "Use offset to shift columns right (0-11)",
                context,
            )

    if order is not None:
        if isinstance(order, int):
            if order < 1 or order > 12:
                raise ParameterValidationError(
                    "order", order, "must be between 1 and 12", "Use order to reorder columns visually (1-12)", context
                )
        elif order not in ["first", "last"]:
            raise ParameterValidationError(
                "order", order, "invalid order value", "Use integer (1-12) or 'first'/'last'", context
            )


def validate_row_column_sum(columns, context="Row"):
    """Validate that Column widths in a Row don't exceed 12.

    Ensures that the sum of column widths within a Row respects Bootstrap's
    12-column grid constraint. Handles fixed widths, responsive widths, and
    auto-sized columns appropriately.

    Args:
        columns (list): List of Column objects to validate.
            Only Column objects with integer or dict widths are checked.
            Auto-sized columns ('auto') are ignored in sum calculation.
        context (str, optional): Error context for messages.
            Defaults to "Row".

    Raises:
        ParameterValidationError: If sum of column widths exceeds 12.

    Example:
        >>> col1 = Column(8, content)
        >>> col2 = Column(4, content)
        >>> validate_row_column_sum([col1, col2])  # Valid: 8 + 4 = 12

        >>> col1 = Column(8, content)
        >>> col2 = Column(6, content)
        >>> validate_row_column_sum([col1, col2])  # Raises error: 8 + 6 = 14

        >>> col1 = Column({'md': 8, 'sm': 12}, content)
        >>> col2 = Column(4, content)
        >>> validate_row_column_sum([col1, col2])  # Valid: uses 'md' → 8 + 4 = 12
    """
    from respysive.layout import Column

    widths = []
    for col in columns:
        if isinstance(col, Column):
            if isinstance(col.width, int):
                widths.append(col.width)
            elif isinstance(col.width, dict):
                w = col.width.get("md", col.width.get(list(col.width.keys())[0]))
                widths.append(w)
        else:
            widths.append(12)

    if widths and sum(widths) > 12:
        raise ParameterValidationError(
            "columns",
            f"sum = {sum(widths)}",
            "total width exceeds 12",
            f"Reduce column widths to sum ≤ 12. Current: {widths}",
            context,
        )
