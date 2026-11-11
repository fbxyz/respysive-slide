"""Slide container with content management, handlers, and layout methods."""

from respysive.builders import CardBuilder, LayoutBuilder, MapLibreBuilder, TitlePageBuilder
from respysive.content import Content
from respysive.errors import validate_bootstrap_columns, validate_heading_tag, validate_styles_length
from respysive.handlers import (
    AltairHandler,
    ContentDetector,
    CustomJsonHandler,
    HtmlReprHandler,
    ImageHandler,
    LatexHandler,
    LayoutHandler,
    MapLibreHandler,
    MappyngHandler,
    MatplotlibHandler,
    PlotlyHandler,
    TextHandler,
    VideoHandler,
)
from respysive.utils import _fragment_class, _parse_style_class

OVERFLOW_MODES = ("fit", "visible", "warn")


class Slide:
    """Individual slide container with content management.

    Handles content addition, layout, and rendering for presentation slides.

    Args:
        center (bool): Enable vertical centering for slide content. Default: False
        overflow (str): How content taller than the slide is handled, overriding the
            presentation default: 'fit' (shrink text, then scale content), 'warn'
            or 'visible'. Default: None (use the presentation setting)
        **kwargs: Additional HTML attributes and CSS classes. Common kwargs include:
            'class' (str or list) for CSS classes, 'data-background-image' (str) for
            background image URL, 'data-background-size' (str) for background size,
            'data-background-position' (str) for background position,
            'data-background-color' (str) and 'data-background-gradient' (str).

    Example:
        Create slide with custom class for overlay::

            slide = Slide(**{'class': 'branded'})

        Multiple classes and background::

            slide = Slide(**{
                'class': ['branded', 'dark-theme'],
                'data-background-image': 'bg.jpg'
            })
    """

    def __init__(self, center=False, overflow=None, **kwargs):
        if overflow is not None and overflow not in OVERFLOW_MODES:
            raise ValueError(f"overflow must be one of {OVERFLOW_MODES}, got {overflow!r}")
        self.content = ""
        self.center = center
        self.overflow = overflow
        self.kwargs = kwargs
        self.content_obj = Content()
        self._export_data = []

        if "data-background-image" in self.kwargs:
            bg_image = self.kwargs["data-background-image"]
            if not bg_image.startswith("data:"):
                from respysive.utils import encode_image_to_data_uri

                self.kwargs["data-background-image"] = encode_image_to_data_uri(bg_image)

        self._content_detector = ContentDetector()
        self._content_detector.register_handler(MapLibreHandler, self.content_obj)
        self._content_detector.register_handler(MappyngHandler, self.content_obj)
        self._content_detector.register_handler(CustomJsonHandler, self.content_obj)
        self._content_detector.register_handler(HtmlReprHandler, self.content_obj)
        self._content_detector.register_handler(MatplotlibHandler, self.content_obj)
        self._content_detector.register_handler(PlotlyHandler, self.content_obj)
        self._content_detector.register_handler(AltairHandler, self.content_obj)
        self._content_detector.register_handler(ImageHandler, self.content_obj)
        self._content_detector.register_handler(VideoHandler, self.content_obj)
        self._content_detector.register_handler(LatexHandler, self.content_obj)
        self._content_detector.register_handler(TextHandler, self.content_obj)

        layout_handler = LayoutHandler(self.content_obj)
        layout_handler.set_content_detector(self._content_detector)
        self._content_detector._handlers.append(layout_handler)
        self._content_detector._handlers.sort(key=lambda h: h.priority)

        self._maplibre_builder = MapLibreBuilder(self.content_obj)
        self._titlepage_builder = TitlePageBuilder(self, self._content_detector)
        self._card_builder = CardBuilder(self._content_detector)
        self._layout_builder = LayoutBuilder(self.content_obj, self._content_detector)

    def _detect_content_type(self, content):
        """Detect content type using the handler chain without generating HTML.

        Args:
            content: Content to detect type for.

        Returns:
            str: Handler class name (e.g. 'PlotlyHandler', 'TextHandler').
        """
        for handler in self._content_detector.get_handlers():
            if handler.can_handle(content):
                return type(handler).__name__
        return "TextHandler"

    def _ensure_shared_data_available(self, shared_data_id: str):
        """Record a shared data id that the deck must provide.

        Args:
            shared_data_id: ID of the shared data to ensure availability
        """
        if shared_data_id not in self.content_obj.shared_data:
            self.content_obj.geojson_refs.add(shared_data_id)  # checked by Presentation when saving

    def _process_content_with_handlers(self, content, shared_data_id=None, content_type=None, **kwargs):
        """Process content using the handler system.

        Args:
            content: Content to process
            shared_data_id: Optional shared data ID for Plotly charts
            content_type: Optional content type to force handling
            **kwargs: Additional styling options for handlers

        Returns:
            str: Processed HTML content
        """
        return self._content_detector.detect_and_handle(content, shared_data_id, content_type, **kwargs)

    def add_custom_content(
        self,
        library: str,
        config: dict,
        cdn: dict = None,
        init_script: str = None,
        div_style: dict = None,
        columns: list = None,
        styles: list = None,
        **kwargs,
    ):
        """Add custom content using external JavaScript libraries via CDN.

        Args:
            library (str): Name of the library (e.g., "maplibre-gl")
            config (dict): Configuration object for the library
            cdn (dict): Dictionary with 'css' and 'js' lists of CDN URLs
            init_script (str): Custom initialization script
            div_style (dict): CSS styles for the container div
            columns (list, optional): Column widths (defaults to [12])
            styles (list, optional): Bootstrap styles for the content
            **kwargs: Additional styling options

        Example:
            >>> slide.add_custom_content(
            ...     library="maplibre-gl",
            ...     config={
            ...         "style": "https://demotiles.maplibre.org/style.json",
            ...         "center": [2.3522, 48.8566],
            ...         "zoom": 10
            ...     },
            ...     cdn={
            ...         "css": ["https://unpkg.com/maplibre-gl@2.4.0/dist/maplibre-gl.css"],
            ...         "js": ["https://unpkg.com/maplibre-gl@2.4.0/dist/maplibre-gl.js"]
            ...     },
            ...     div_style={"height": "500px"}
            ... )
        """
        if columns is None:
            columns = [12]

        custom_config = {
            "library": library,
            "config": config,
            "cdn": cdn or {},
            "init_script": init_script,
            "div_style": div_style or {"height": "400px", "width": "100%"},
        }

        self.add_content([custom_config], columns=columns, styles=styles)

    def add_maplibre_map(
        self,
        center: list,
        zoom: int = 10,
        style: str = None,
        markers: list = None,
        legend: dict = None,
        openstreetmap: bool = False,
        scale: bool = True,
        navigation: bool = True,
        columns: list = None,
        styles: list = None,
    ):
        """Add a MapLibre GL JS map easily.

        Args:
            center: Center coordinates [longitude, latitude]
            zoom: Zoom level (default 10)
            style: Map style URL (default: MapLibre demo, ignored if openstreetmap=True)
            markers: List of markers with coordinates, popup, icon (Font Awesome), color
            legend: Dictionary with title and items for legend
            openstreetmap: Use OpenStreetMap as background (default False)
            scale: Show scale control (default True)
            navigation: Show navigation controls (default True)
            columns: Column widths (default [12])
            styles: Bootstrap styles

        Example:
            >>> slide.add_maplibre_map(
            ...     center=[2.3522, 48.8566],
            ...     zoom=12,
            ...     openstreetmap=True,
            ...     markers=[
            ...         {
            ...             "coordinates": [2.3522, 48.8566],
            ...             "icon": "fas fa-tower-broadcast",
            ...             "color": "#e74c3c",
            ...             "popup": "Eiffel Tower"
            ...         }
            ...     ],
            ...     legend={
            ...         "title": "Points of Interest",
            ...         "items": [
            ...             {"icon": "fas fa-tower-broadcast", "color": "#e74c3c", "label": "Monuments"}
            ...         ]
            ...     }
            ... )
        """
        if columns is None:
            columns = [12]

        config = self._maplibre_builder.build_map_config(
            center, zoom, style, markers, legend, openstreetmap, scale, navigation
        )
        self.add_content([config], columns=columns, styles=styles)

    def add_maplibre_lines_map(
        self,
        center: list,
        zoom: int = 10,
        lines: list = None,
        markers: list = None,
        legend: dict = None,
        openstreetmap: bool = False,
        scale: bool = True,
        navigation: bool = True,
        columns: list = None,
        styles: list = None,
    ):
        """Add a MapLibre map with variable width lines.

        Args:
            center: Center coordinates [longitude, latitude]
            zoom: Zoom level (default 10)
            lines: List of lines with coordinates, width, color, popup
            markers: List of markers (optional)
            legend: Dictionary with title and items for legend
            openstreetmap: Use OpenStreetMap as background (default False)
            scale: Show scale control (default True)
            navigation: Show navigation controls (default True)
            columns: Column widths (default [12])
            styles: Bootstrap styles

        Example:
            >>> slide.add_maplibre_lines_map(
            ...     center=[2.3522, 48.8566],
            ...     zoom=12,
            ...     openstreetmap=True,
            ...     lines=[
            ...         {
            ...             "coordinates": [[2.3522, 48.8566], [2.3376, 48.8606]],
            ...             "width": 8,
            ...             "color": "#e74c3c",
            ...             "popup": "Main line - Traffic: 10000 vehicles/day"
            ...         },
            ...         {
            ...             "coordinates": [[2.3376, 48.8606], [2.3488, 48.8534]],
            ...             "width": 4,
            ...             "color": "#3498db",
            ...             "popup": "Secondary line - Traffic: 5000 vehicles/day"
            ...         }
            ...     ],
            ...     legend={
            ...         "title": "Road Traffic",
            ...         "items": [
            ...             {"type": "line", "width": 8, "color": "#e74c3c", "label": "High traffic (>8000)"},
            ...             {"type": "line", "width": 4, "color": "#3498db", "label": "Medium traffic (4000-8000)"}
            ...         ]
            ...     }
            ... )
        """
        if columns is None:
            columns = [12]

        config = self._maplibre_builder.build_lines_map_config(
            center, zoom, lines, markers, legend, openstreetmap, scale, navigation
        )
        self.add_content([config], columns=columns, styles=styles)

    def add_maplibre_circles_map(
        self,
        center: list,
        zoom: int = 10,
        circles: list = None,
        markers: list = None,
        legend: dict = None,
        openstreetmap: bool = False,
        scale: bool = True,
        navigation: bool = True,
        min_radius: int = 5,
        max_radius: int = 50,
        columns: list = None,
        styles: list = None,
    ):
        """Add a MapLibre map with proportional circles (radius = √value).

        Args:
            center: Center coordinates [longitude, latitude]
            zoom: Zoom level (default 10)
            circles: List of circles with coordinates, value, color, popup
            markers: List of markers (optional)
            legend: Dictionary with title (automatic legend with min/median/max)
            openstreetmap: Use OpenStreetMap as background (default False)
            scale: Show scale control (default True)
            navigation: Show navigation controls (default True)
            min_radius: Minimum radius in pixels (default 5)
            max_radius: Maximum radius in pixels (default 50)
            columns: Column widths (default [12])
            styles: Bootstrap styles

        Example:
            >>> slide.add_maplibre_circles_map(
            ...     center=[2.3522, 48.8566],
            ...     zoom=10,
            ...     openstreetmap=True,
            ...     circles=[
            ...         {
            ...             "coordinates": [2.3522, 48.8566],
            ...             "value": 2200000,
            ...             "color": "#e74c3c",
            ...             "popup": "Paris: 2.2M people"
            ...         },
            ...         {
            ...             "coordinates": [2.3376, 48.8606],
            ...             "value": 700000,
            ...             "color": "#3498db",
            ...             "popup": "Lyon: 700k people"
            ...         }
            ...     ],
            ...     legend={"title": "City Population"},
            ...     min_radius=10,
            ...     max_radius=60
            ... )
        """
        if columns is None:
            columns = [12]

        config = self._maplibre_builder.build_circles_map_config(
            center, zoom, circles, markers, legend, openstreetmap, scale, navigation, min_radius, max_radius
        )
        self.add_content([config], columns=columns, styles=styles)

    def add_maplibre_choropleth_map(
        self,
        center: list,
        zoom: int = 10,
        geojson: dict = None,
        color_property: str = None,
        color_rules: list = None,
        legend: dict = None,
        openstreetmap: bool = False,
        scale: bool = True,
        navigation: bool = True,
        popup: str = None,
        columns: list = None,
        styles: list = None,
    ):
        """Add a MapLibre choropleth map (color-filled areas).

        Args:
            center: Center coordinates [longitude, latitude]
            zoom: Zoom level (default 10)
            geojson: GeoJSON data with properties
            color_property: Property name for coloring
            color_rules: Color rules [{"operator": ">=", "value": 100, "color": "#ff0000"}]
            legend: Manual legend {"choropleth": {"type": "discrete", "items": [...]}}
            openstreetmap: Use OpenStreetMap as background (default False)
            scale: Show scale control (default True)
            navigation: Show navigation controls (default True)
            popup: Popup template with variables {propertyName}
            columns: Column widths (default [12])
            styles: Bootstrap styles

        Example:
            >>> slide.add_maplibre_choropleth_map(
            ...     center=[2.3522, 48.8566],
            ...     zoom=6,
            ...     geojson=regions_data,
            ...     color_property="population",
            ...     color_rules=[
            ...         {"operator": ">=", "value": 1000000, "color": "#d73027"},
            ...         {"operator": ">=", "value": 500000, "color": "#f46d43"},
            ...         {"operator": ">=", "value": 100000, "color": "#fdae61"},
            ...         {"operator": "<", "value": 100000, "color": "#fee08b"}
            ...     ],
            ...     legend={
            ...         "title": "Population by Region",
            ...         "choropleth": {
            ...             "type": "discrete",
            ...             "items": [
            ...                 {"color": "#d73027", "label": "> 1M inhabitants"},
            ...                 {"color": "#f46d43", "label": "500k - 1M inhabitants"},
            ...                 {"color": "#fdae61", "label": "100k - 500k inhabitants"},
            ...                 {"color": "#fee08b", "label": "< 100k inhabitants"}
            ...             ]
            ...         }
            ...     },
            ...     popup="<b>{name}</b><br>Population: {population} people"
            ... )
        """
        if columns is None:
            columns = [12]

        config = self._maplibre_builder.build_choropleth_map_config(
            center, zoom, geojson, color_property, color_rules, legend, openstreetmap, scale, navigation, popup
        )
        self.add_content([config], columns=columns, styles=styles)

    def add_maplibre_choropleth_with_data_join(
        self,
        center: list,
        zoom: int = 10,
        geojson_id: str = None,
        join_data: dict = None,
        join_key: str = None,
        color_property: str = None,
        color_rules: list = None,
        legend: dict = None,
        openstreetmap: bool = False,
        scale: bool = True,
        navigation: bool = True,
        popup: str = None,
        columns: list = None,
        styles: list = None,
    ):
        """Add an optimized MapLibre choropleth map with data join.

        This method uses the cache system to avoid GeoJSON data duplication.

        Args:
            center (list): Center coordinates [longitude, latitude]
            zoom (int): Zoom level (default 10)
            geojson_id (str): Reference ID to global GeoJSON data (via add_global_geojson)
            join_data (dict): Data to join with geometry (dict or list)
            join_key (str): Common key for joining (e.g., 'id', 'code_insee')
            color_property (str): Property to use for coloring after join
            color_rules (list): Color rules list [{'operator': '>=', 'value': 10, 'color': '#red'}]
            legend (dict): Legend configuration
            openstreetmap (bool): Use OpenStreetMap instead of default style
            scale (bool): Show scale control
            navigation (bool): Show navigation controls
            popup (str): Popup HTML template with variables {property_name}
            columns (list): Bootstrap layout [12]
            styles (list): CSS styles and Bootstrap classes

        Example:
            >>> presentation.add_global_geojson('france_regions', geojson_regions)
            >>> slide.add_maplibre_choropleth_with_data_join(
            ...     center=[2.3, 46.8], zoom=6,
            ...     geojson_id='france_regions',
            ...     join_data={'75': {'population': 2000000}, '69': {'population': 500000}},
            ...     join_key='code_insee',
            ...     color_property='population',
            ...     color_rules=[
            ...         {'operator': '>=', 'value': 1000000, 'color': '#d73027'},
            ...         {'operator': '>=', 'value': 500000, 'color': '#fc8d59'}
            ...     ]
            ... )
        """
        if columns is None:
            columns = [12]

        config = self._maplibre_builder.build_choropleth_with_data_join_config(
            center,
            zoom,
            geojson_id,
            join_data,
            join_key,
            color_property,
            color_rules,
            legend,
            openstreetmap,
            scale,
            navigation,
            popup,
        )
        self.add_content([config], columns=columns, styles=styles)

    def add_title(self, text: str, tag: str = "h3", icon: str = None, fragment=None, **kwargs):
        """Add a heading element to the slide.

        Args:
            text (str): The text of the heading
            tag (str): The HTML tag to use for the heading (h1-h6). Default is 'h3'
            icon (str, optional): FontAwesome icon class for the heading
            fragment (bool or str, optional): Reveal the title as a fragment. True for the
                default fade-in, or a fragment style such as 'fade-up'
            **kwargs: Additional CSS styles and HTML classes. Use underscore for CSS properties
                (e.g., font_size='20px'). The 'class' key accepts string or list of strings.

        Example:
            >>> slide.add_title("My Title", tag="h2", icon="fas fa-star")
            >>> slide.add_title("Styled Title", color="blue", **{"class": ["title", "highlight"]})
        """
        validate_heading_tag(tag, "add_title")

        c = Content()
        c.add_heading(text, tag, icon, **kwargs)

        frag = _fragment_class(fragment)
        row = f"<div class='row {frag}'>" if frag else "<div class='row'>"
        self.content += row + "<div class='col-12 mx-auto'>" + c.render() + "</div></div>"

        self._export_data.append(
            {
                "type": "title",
                "text": text,
                "tag": tag,
                "icon": icon,
                "fragment": fragment,
                "kwargs": kwargs,
            }
        )

    def add_notes(self, notes: str):
        """Add speaker notes to the slide.

        Speaker notes are visible in the speaker view opened by pressing 'S'
        during the presentation. They support plain text, HTML, and Markdown.

        Args:
            notes (str): Speaker notes content. Can be plain text, HTML, or Markdown.

        Example:
            >>> slide.add_notes("Remember to emphasize this point")
            >>> slide.add_notes("**Important:** This is a key concept")
            >>> slide.add_notes("<ul><li>Point 1</li><li>Point 2</li></ul>")

        Note:
            Press 'S' during presentation to open Speaker View with notes.
        """
        from respysive.utils import process_markdown_with_latex

        if "<aside" not in notes and "</aside>" not in notes:
            processed_notes = process_markdown_with_latex(notes)
            notes_html = f'<aside class="notes">{processed_notes}</aside>'
        else:
            notes_html = notes

        self.content += notes_html

        self._export_data.append(
            {
                "type": "notes",
                "text": notes,
            }
        )

    def add_content(
        self,
        content: list,
        columns=None,
        styles: list = None,
        shared_data_ids: list = None,
        content_types: list = None,
        dimensions: list = None,
        fragment=None,
        fragment_items=None,
        **kwargs,
    ):
        """Add content items to slide using Bootstrap grid layout.

        Args:
            content: List of content items (strings, figures, charts, etc.)
            columns: Bootstrap column sizes for each item (default: [12])
            styles: Style dictionaries for each content item
            shared_data_ids: Shared data IDs for each item (for Plotly charts)
            content_types: Content types to force for each item ('plotly', 'matplotlib', 'maplibre', 'altair', 'image', 'video', 'latex', 'text', 'json')
            dimensions: List of dimension dicts for each item (e.g., [{'width': 800, 'height': 600}, {'width': '90%'}])
            fragment: Reveal items one step at a time. True (default fade-in), a fragment style
                ('fade-up', 'highlight-red', ...) applied to every item, or a list with one
                value per item (None for items shown immediately)
            fragment_items: Reveal list items (<li>) inside the content one by one. True or a
                fragment style, or a list with one value per item
            **kwargs: Additional styling options applied to all items (overridden by individual dimensions)
        """
        validate_bootstrap_columns(content, columns, "add_content")

        if columns is None:
            columns = [12] * len(content)
        elif len(columns) == 1 and len(content) > 1:
            columns = columns * len(content)

        validate_styles_length(styles, content, "add_content")

        row_record = {"type": "row", "elements": []}
        for i in range(len(content)):
            detected_type = self._detect_content_type(content[i])
            element_record = {
                "col_width": columns[i],
                "content": content[i],
                "detected_type": detected_type,
                "shared_data_id": shared_data_ids[i] if shared_data_ids and i < len(shared_data_ids) else None,
                "style": styles[i] if styles and i < len(styles) else None,
                "dimensions": dimensions[i] if dimensions and i < len(dimensions) else None,
                "fragment": _fragment_class(fragment, i) or None,
            }
            row_record["elements"].append(element_record)
        self._export_data.append(row_record)

        row = "<div class='row'>"
        for i in range(len(content)):
            col = content[i]
            shared_data_id = shared_data_ids[i] if shared_data_ids and i < len(shared_data_ids) else None
            content_type = content_types[i] if content_types and i < len(content_types) else None

            item_kwargs = kwargs.copy()
            if dimensions and i < len(dimensions) and dimensions[i]:
                item_kwargs.update(dimensions[i])

            if shared_data_id:
                self._ensure_shared_data_available(shared_data_id)

            col = self._process_content_with_handlers(col, shared_data_id, content_type, **item_kwargs)

            col_class = f"col-md-{columns[i]}"
            frag = _fragment_class(fragment, i)
            if frag:
                col_class += f" {frag}"
            items_frag = _fragment_class(fragment_items, i)
            if items_frag:
                items_style = items_frag[len("fragment") :].strip()
                col = f"<div class='fragment-items' data-fragment-style='{items_style}'>{col}</div>"

            if styles and len(styles) > i:
                style = dict(styles[i] or {})
                extra = style.pop("class", None)
                if extra:
                    col_class += " " + (" ".join(extra) if isinstance(extra, list) else extra)
                col = f"<div class='{col_class}' {_parse_style_class(style)}>{col}</div>"
            else:
                col = f"<div class='{col_class}'>{col}</div>"
            row += col
        self.content += row + "</div>"

    def add_card(self, cards: list, styles: list = None, fragment=None):
        """Add Bootstrap cards to the slide.

        Args:
            cards: List of card dictionaries. Each card can contain:

                - title: Card title text
                - title_style: CSS dictionary for title (e.g., {'font-size': '20px', 'color': '#333'})
                - title_tag: HTML tag for title (h1-h6, default: 'h5')
                - text: Card body text (supports Markdown and LaTeX)
                - text_style: CSS dictionary for text (e.g., {'font-size': '85%', 'color': '#666'})
                - image: URL or path to image file
                - image_style: CSS dictionary for image (e.g., {'max-height': '300px', 'object-fit': 'contain'})
                - graph: Chart object (Matplotlib figure, Plotly JSON, Altair spec, MapLibre config)

            styles: List of style dictionaries for card containers (backgrounds, borders, etc.)
            fragment: Reveal cards one at a time. True, a fragment style such as 'fade-up',
                or a list with one value per card

        Example:
            >>> cards = [
            ...     {
            ...         'title': 'Sales Report',
            ...         'title_style': {'font-size': '24px', 'color': '#e63946'},
            ...         'title_tag': 'h3',
            ...         'text': 'Revenue data for Q3',
            ...         'text_style': {'font-size': '100%'},
            ...         'graph': plotly_chart
            ...     },
            ...     {
            ...         'title': 'Map View',
            ...         'graph': {'center': [2.35, 48.85], 'zoom': 10, 'openstreetmap': True}
            ...     }
            ... ]
            >>> slide.add_card(cards)
        """
        cards_record = {"type": "cards", "cards": [], "styles": styles, "fragment": fragment}
        for card in cards:
            cards_record["cards"].append(dict(card))
        self._export_data.append(cards_record)

        self.content += self._card_builder.build_cards(cards, styles, fragment=fragment)

    def add_title_page(
        self,
        title_page_content: dict,
        styles: list = None,
        title_page_class: str = "",
        background_image: str = None,
        background_style: dict = None,
    ):
        """Add a title page to the slide.

        Args:
            title_page_content: dictionary that contains the following keys: 'title', 'subtitle', 'authors', 'logo'
            styles: list of dictionaries that contains the css styles for each element of the title page. The keys of the dictionaries are: 'title', 'subtitle', 'authors', 'logo'
            title_page_class: additional CSS class for the title-page div
            background_image: URL or path to background image
            background_style: dictionary with background styling options like 'background-size', 'background-position', etc.
        """
        self._export_data.append(
            {
                "type": "title_page",
                "content": title_page_content,
                "styles": styles,
                "background_image": background_image,
            }
        )

        self.content += self._titlepage_builder.build_title_page(
            title_page_content, styles, title_page_class, background_image, background_style
        )

    def add_split_title_page(
        self,
        title_page_content: dict,
        custom_content,
        title_column_width: int = 6,
        custom_column_width: int = 6,
        title_page_class: str = "",
        custom_content_style: dict = None,
        title_styles: list = None,
        title_column_style: dict = None,
        background_image: str = None,
        background_style: dict = None,
        full_height: bool = False,
    ):
        """Add a split title page with two columns.

        Creates a title page divided into two columns using Bootstrap grid system.
        When full_height is enabled, the page covers the entire slide viewport with
        no margins using Reveal.js native background system and absolute positioning.

        Args:
            title_page_content (dict): Dictionary with keys 'title', 'subtitle', 'authors', 'logo' (all optional)
            custom_content: Content to display in the second column (string, figure, image, chart, etc.)
            title_column_width (int): Width of the title column in Bootstrap units (1-12, default: 6)
            custom_column_width (int): Width of the custom content column in Bootstrap units (1-12, default: 6)
            title_page_class (str): Additional CSS class for the title-page div
            custom_content_style (dict): Style dictionary for the custom content column
                (e.g., {'background-color': '#fff', 'padding': '40px'})
            title_styles (list): List of style dictionaries for title elements (title, subtitle, authors, logo)
            title_column_style (dict): Style dictionary for the title column container
                (e.g., {'background-color': '#1d3557', 'color': '#f1faee', 'padding': '40px'})
            background_image (str): URL or path to background image
            background_style (dict): Dictionary with background styling options
                ('background-size', 'background-position', etc.)
            full_height (bool): If True, the split page covers the full slide viewport with no margins.
                Uses Reveal.js background gradient system for optimal rendering. Default: False

        Example:
            Create a full-height split title page::

                slide = Slide()
                slide.add_split_title_page(
                    title_page_content={
                        'title': 'My Presentation',
                        'subtitle': 'A Great Topic',
                        'authors': 'Author Name'
                    },
                    custom_content=logo_url,
                    title_column_width=8,
                    custom_column_width=4,
                    full_height=True,
                    title_column_style={
                        'background-color': '#1d3557',
                        'color': '#f1faee',
                        'padding': '40px'
                    },
                    custom_content_style={
                        'background-color': '#e63946',
                        'padding': '30px',
                        'text-align': 'center'
                    }
                )
        """
        split_record = {
            "type": "split_title_page",
            "title_content": title_page_content,
            "custom_content": custom_content,
            "title_column_width": title_column_width,
            "custom_column_width": custom_column_width,
            "custom_content_type": self._detect_content_type(custom_content),
            "title_styles": title_styles,
        }
        self._export_data.append(split_record)

        self.content += self._titlepage_builder.build_split_title_page(
            title_page_content,
            custom_content,
            title_column_width,
            custom_column_width,
            title_page_class,
            custom_content_style,
            title_styles,
            title_column_style,
            background_image,
            background_style,
            full_height,
        )

    def add_layout(self, layout, **kwargs):
        """Add a Row or Column layout to the slide.

        This method provides an alternative to add_content() for creating
        complex nested Bootstrap grid layouts using Row and Column objects.
        It enables explicit control over layout structure while maintaining
        full integration with the respysive content handling system.

        Args:
            layout (Row or Column): Layout structure to add to the slide.
                Can be a Row containing Columns, a standalone Column,
                or nested Row/Column structures of any depth.
            **kwargs: Additional styling options applied to the layout.
                These are passed to the content handler system but are
                typically overridden by Row/Column kwargs.

        Raises:
            ValueError: If layout is not a Row or Column instance

        Examples:
            Simple two-column layout::

                layout = Row([
                    Column(8, my_chart),
                    Column(4, "Description text")
                ])
                slide.add_layout(layout)

            Nested layout with chart and stacked sidebar::

                layout = Row([
                    Column(8, my_chart),
                    Column(4, [
                        Row(header_text),
                        Row(sidebar_chart),
                        Row(footer_text)
                    ])
                ])
                slide.add_layout(layout)

            Layout with styling and alignment::

                layout = Row([
                    Column(6, map_visual, **{'class': 'border'}),
                    Column(6, [
                        Row(title, gap=2),
                        Row([
                            Column(6, chart1),
                            Column(6, chart2)
                        ])
                    ])
                ], gap=3, align_items='center')
                slide.add_layout(layout)

            Responsive layout::

                layout = Row([
                    Column({'md': 8, 'sm': 12}, chart),  # 8 cols desktop, full mobile
                    Column({'md': 4, 'sm': 12}, text)
                ])
                slide.add_layout(layout)

        Note:
            The existing add_content() method remains fully functional.
            Use add_layout() when you need explicit control over nested
            layouts, and use add_content() for simple grid layouts.
        """
        from respysive.layout import Column, Row

        if not isinstance(layout, (Row, Column)):
            raise ValueError("layout must be a Row or Column instance")

        self._export_data.append(
            {
                "type": "layout",
                "layout": layout,
            }
        )

        html = self._process_content_with_handlers(layout, **kwargs)
        self.content += html
