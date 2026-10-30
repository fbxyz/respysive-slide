"""Low-level content rendering for HTML elements, charts, and maps."""

import base64
import json
import uuid
from io import BytesIO

from bs4 import BeautifulSoup
from matplotlib.figure import Figure

from respysive.errors import validate_heading_tag, validate_text_tag
from respysive.utils import _parse_style_class, _video_mime_type, encode_image_to_data_uri, encode_video_to_data_uri

# Plotly traces drawn on MapLibre tiles, whose controls need the MapLibre stylesheet
_TILE_MAP_TRACES = {"scattermap", "choroplethmap", "densitymap"}


def _uses_tile_maps(plotly_data):
    try:
        if hasattr(plotly_data, "to_plotly_json"):
            traces = plotly_data.to_plotly_json().get("data", [])
        elif isinstance(plotly_data, str):
            traces = json.loads(plotly_data).get("data", [])
        elif isinstance(plotly_data, dict):
            traces = plotly_data.get("data", [])
        else:
            return False
        return any(isinstance(t, dict) and t.get("type") in _TILE_MAP_TRACES for t in traces)
    except (ValueError, AttributeError, TypeError):
        return False


class Content:
    """Content container for slide elements and data management.

    Handles content rendering, script management, and shared data storage.
    """

    def __init__(self):
        """Initialize an empty content container."""
        self.content = ""
        self.shared_data = {}
        self.geojson_refs = set()  # deck GeoJSON ids used by MapLibre maps

    def clear(self):
        """Reset all content and shared data."""
        self.content = ""
        self.shared_data = {}
        self.geojson_refs = set()  # deck GeoJSON ids used by MapLibre maps

    def add_shared_data(self, data_id: str, data, data_type: str = "json"):
        """Store shared data (JSON/GeoJSON) that can be referenced by multiple charts.

        Args:
            data_id (str): Unique identifier for the data
            data: The data to store (dict, str, or object with to_json method)
            data_type (str): Type of data ('json', 'geojson')
        """
        if hasattr(data, "to_json"):
            json_str = data.to_json()
        elif isinstance(data, dict):
            json_str = json.dumps(data, separators=(",", ":"))
        elif isinstance(data, str):
            json_str = data
        else:
            raise ValueError("data must be an object with to_json method, a dictionary, or a JSON string")

        self.shared_data[data_id] = {"data": json_str, "type": data_type}

        self.content += (
            f'<div id="shared-data-{data_id}" style="display:none;" data-type="{data_type}">{json_str}</div>'
        )

    def add_heading(self, text: str, tag: str = "h3", icon: str = None, **kwargs):
        """Add a heading element to the HTML document.

        Args:
            text: The text of the heading.
            tag: The HTML tag to use for the heading. Default is 'h1'.
            icon: The icon of the heading (optional).
            kwargs: Additional CSS styles and html class to apply to the image. (optional)
                The keys should be in the format of CSS property names with '_' instead of '-',
                example: font_size. You can also pass the class key with a string or a list of strings.
                Example: {'font_size': '20px', 'color': 'blue', 'class':'my-class'} or
                {'font_size': '20px', 'color': 'blue', 'class':['my-class','my-second-class']}
        """
        validate_heading_tag(tag, "add_heading")

        s = _parse_style_class(kwargs)

        self.content += f"<{tag} {s}><i class='{icon}'></i> {text}</{tag}>" if icon else f"<{tag} {s}>{text}</{tag}>"

    def add_text(self, text: str, tag: str = "p", **kwargs):
        """Add a text element to the HTML document.

        Args:
            text: The text to be added.
            tag: The HTML tag to use for the text. Default is 'p'.
            kwargs: Additional CSS styles and html class to apply to the image. (optional)
                The keys should be in the format of CSS property names with '_' instead of '-',
                example: font_size. You can also pass the class key with a string or a list of strings.
                Example: {'font_size': '20px', 'color': 'blue', 'class':'my-class'} or
                {'font_size': '20px', 'color': 'blue', 'class':['my-class','my-second-class']}
        """
        validate_text_tag(tag, "add_text")

        s = _parse_style_class(kwargs)

        self.content += f"""<{tag} {s}>{text}</{tag}>"""

    def add_list(self, items: list, ordered=False, **kwargs):
        """Add a list element to the HTML document.

        Args:
            items: The items of the list.
            ordered: Whether the list should be ordered or not.
            kwargs: Additional CSS styles and html class to apply to the image. (optional)
                The keys should be in the format of CSS property names with '_' instead of '-',
                example: font_size. You can also pass the class key with a string or a list of strings.
                Example: {'font_size': '20px', 'color': 'blue', 'class':'my-class'} or
                {'font_size': '20px', 'color': 'blue', 'class':['my-class','my-second-class']}
        """
        list_tag = "ol" if ordered else "ul"

        s = _parse_style_class(kwargs)

        list_items = "\n".join([f"<li>{item}</li>" for item in items])
        self.content += f"<{list_tag} {s}>\n{list_items}\n</{list_tag}>"

    def add_image(self, src: str, alt: str = "", **kwargs):
        """Add an image element to the HTML document.

        Args:
            src: The source of the image (local file path or URL).
            alt: The alternative text for the image.
            kwargs: Additional CSS styles and html class to apply to the image. (optional)
                The keys should be in the format of CSS property names with '_' instead of '-',
                example: font_size. You can also pass the class key with a string or a list of strings.
                Example: {'font_size': '20px', 'color': 'blue', 'class':'my-class'} or
                {'font_size': '20px', 'color': 'blue', 'class':['my-class','my-second-class']}
        """

        if "class" not in kwargs:
            kwargs["class"] = []
        elif isinstance(kwargs["class"], str):
            kwargs["class"] = [kwargs["class"]]
        kwargs["class"].append("img-fluid")

        if src.lower().endswith(".svg") and "max_width" not in kwargs:
            kwargs["max_width"] = "100%"

        image_src = encode_image_to_data_uri(src)

        s = _parse_style_class(kwargs)
        self.content += f"""<img src="{image_src}" alt="{alt}" {s}>"""

    def add_video(
        self,
        src: str,
        controls: bool = True,
        loop: bool = True,
        muted: bool = True,
        autoplay: bool = True,
        playsinline: bool = True,
        poster: str = None,
        **kwargs,
    ):
        """Add an embedded base64 video element to the HTML document.

        The video binary is read from a local path or URL, encoded in base64
        and embedded inline through a ``data:video/...;base64,...`` URI inside a
        ``<video>`` element with a ``<source>`` child. This mirrors
        :meth:`add_image`.

        Supported formats: ``.mp4``, ``.webm``, ``.ogg`` / ``.ogv``, ``.mov``,
        ``.m4v``. The MIME type is deduced from the extension
        (``video/mp4``, ``video/webm``, ``video/ogg``, ``video/quicktime``).

        Note:
            Base64 encoding inflates the binary size by roughly 33% compared to
            the original file. A large video therefore makes the generated HTML
            much heavier; prefer short, web-optimized clips. ``autoplay`` only
            works reliably in browsers when the video is also ``muted``.

        Args:
            src: The source of the video (local file path or URL).
            controls: Show the native playback controls. Defaults to True.
            loop: Restart the video when it ends. Defaults to True.
            muted: Start muted (required for autoplay to work). Defaults to True.
            autoplay: Start playing automatically. Defaults to True.
            playsinline: Play inline on mobile instead of fullscreen.
                Defaults to True.
            poster: Optional preview image (path or URL) shown before playback.
            kwargs: Additional CSS styles and html class to apply to the video.
                The keys should be in the format of CSS property names with '_'
                instead of '-', example: font_size. You can also pass the class
                key with a string or a list of strings.

        Example:
            >>> content = Content()
            >>> content.add_video("clip.mp4", autoplay=False,
            ...                   poster="preview.png", max_width="80%")
        """

        if "class" not in kwargs:
            kwargs["class"] = []
        elif isinstance(kwargs["class"], str):
            kwargs["class"] = [kwargs["class"]]
        kwargs["class"].append("img-fluid")

        video_src = encode_video_to_data_uri(src)
        mime_type = _video_mime_type(src)

        bool_attrs = ""
        if controls:
            bool_attrs += " controls"
        if loop:
            bool_attrs += " loop"
        if muted:
            bool_attrs += " muted"
        if autoplay:
            bool_attrs += " autoplay"
        if playsinline:
            bool_attrs += " playsinline"

        poster_attr = ""
        if poster:
            if not poster.startswith("data:"):
                poster = encode_image_to_data_uri(poster)
            poster_attr = f' poster="{poster}"'

        s = _parse_style_class(kwargs)
        self.content += f'<video{bool_attrs}{poster_attr} {s}><source src="{video_src}" type="{mime_type}"></video>'

    def add_svg(self, svg: str, **kwargs):
        """Add a svg to the document.

        Args:
            svg: The code of the svg.
            kwargs: Additional CSS styles and html class to apply to the image. (optional)
                The keys should be in the format of CSS property names with '_' instead of '-',
                example: font_size. You can also pass the class key with a string or a list of strings.
                Example: {'font_size': '20px', 'color': 'blue', 'class':'my-class'} or
                {'font_size': '20px', 'color': 'blue', 'class':['my-class','my-second-class']}
        """

        if "class" not in kwargs:
            kwargs["class"] = []
        elif isinstance(kwargs["class"], str):
            kwargs["class"] = [kwargs["class"]]
        kwargs["class"].append("img-fluid")

        s = _parse_style_class(kwargs)

        self.content += f"""<div {s}>{svg}</div>"""

    def add_plotly(self, plotly_data, shared_data_id=None, **kwargs):
        """Add a Plotly chart with optional shared data support.

        This method renders interactive Plotly charts with full responsiveness and
        automatic shared data integration. It supports all Plotly chart types including
        choropleth maps, scatter plots, bar charts, and geographic visualizations.

        Args:
            plotly_data: Plotly chart data in multiple formats:

                - plotly.graph_objects.Figure: Plotly Figure object
                - dict: Plotly configuration dictionary with 'data' and 'layout'
                - str: JSON string representation of Plotly chart

            shared_data_id (str, optional): Identifier for shared GeoJSON/data.
                References data stored via Presentation.add_global_geojson() or
                local shared data for optimized choropleth maps and geographic charts.
            **kwargs: Additional styling options:

                - width (str|int|float): Override chart width ('100%', 800, '600px').
                  Priority: kwargs > plotly layout > default ('100%')
                - height (str|int|float): Override chart height ('400px', 500, '50vh').
                  Priority: kwargs > plotly layout > default ('400px')
                - class (str|list): Bootstrap CSS classes
                - CSS properties: Use underscores instead of hyphens (font_size, background_color)

        Examples:
            Basic chart (uses fig.layout dimensions if set)::

                fig.update_layout(width=900, height=500)  # These will be used
                content.add_plotly(fig)

            Override chart dimensions::

                content.add_plotly(fig, width=800, height=600)  # Overrides fig.layout
                content.add_plotly(fig, width='90%', height='50vh')

            With shared GeoJSON for choropleth::

                presentation.add_global_geojson('france_regions', geojson_data)
                content.add_plotly(choropleth_config, shared_data_id='france_regions')

            With styling::

                content.add_plotly(fig, margin_top='20px', **{'class': 'border rounded'})

        Note:
            - Automatically includes 'img-fluid' class for responsive behavior
            - Supports both local and global shared data sources
            - Handles GeoJSON data injection for choropleth maps automatically
            - Replaces the deprecated add_optimized_plotly() method
        """

        chart_width = "100%"
        chart_height = "400px"

        try:
            if isinstance(plotly_data, dict) and "layout" in plotly_data:
                layout = plotly_data["layout"]
                if "width" in layout:
                    chart_width = (
                        f"{layout['width']}px" if isinstance(layout["width"], (int, float)) else str(layout["width"])
                    )
                if "height" in layout:
                    chart_height = (
                        f"{layout['height']}px" if isinstance(layout["height"], (int, float)) else str(layout["height"])
                    )
            elif isinstance(plotly_data, str):
                try:
                    parsed_data = json.loads(plotly_data)
                    if "layout" in parsed_data:
                        layout = parsed_data["layout"]
                        if "width" in layout:
                            chart_width = (
                                f"{layout['width']}px"
                                if isinstance(layout["width"], (int, float))
                                else str(layout["width"])
                            )
                        if "height" in layout:
                            chart_height = (
                                f"{layout['height']}px"
                                if isinstance(layout["height"], (int, float))
                                else str(layout["height"])
                            )
                except json.JSONDecodeError:
                    pass
            elif hasattr(plotly_data, "layout"):
                if hasattr(plotly_data.layout, "width") and plotly_data.layout.width is not None:
                    chart_width = f"{plotly_data.layout.width}px"
                if hasattr(plotly_data.layout, "height") and plotly_data.layout.height is not None:
                    chart_height = f"{plotly_data.layout.height}px"
        except Exception:
            pass

        if "width" in kwargs:
            chart_width = kwargs.pop("width")
            if isinstance(chart_width, (int, float)):
                chart_width = f"{chart_width}px"
        if "height" in kwargs:
            chart_height = kwargs.pop("height")
            if isinstance(chart_height, (int, float)):
                chart_height = f"{chart_height}px"

        if "class" not in kwargs:
            kwargs["class"] = []
        elif isinstance(kwargs["class"], str):
            kwargs["class"] = [kwargs["class"]]
        kwargs["class"].append("img-fluid")
        if _uses_tile_maps(plotly_data):
            kwargs["class"].append("rs-plotly-map")  # tells the page to load the MapLibre stylesheet

        s = _parse_style_class(kwargs)

        chart_id = "plotly-chart-" + str(uuid.uuid4())

        if shared_data_id:
            use_local_data = shared_data_id in self.shared_data

            plotly_data_json = json.dumps(plotly_data) if plotly_data else "null"

            data_element_id = f"shared-data-{shared_data_id}" if use_local_data else shared_data_id

            html_content = f"""
        <div {s} id='{chart_id}' style='width:{chart_width}; height:{chart_height};'></div>
        <script type="text/javascript">
            (function() {{
                // Initialize global cache for parsed JSON data
                if (!window._respysive_cache) {{
                    window._respysive_cache = {{}};
                }}

                try {{
                    var sharedDataElement = document.getElementById('{data_element_id}');
                    if (!sharedDataElement) {{
                        throw new Error('Shared data element not found with ID: {data_element_id}');
                    }}

                    // Use cached data if available, otherwise parse and cache
                    var cacheKey = 'element_{data_element_id}';
                    if (!window._respysive_cache[cacheKey]) {{
                        window._respysive_cache[cacheKey] = JSON.parse(sharedDataElement.textContent);
                    }}
                    var sharedData = window._respysive_cache[cacheKey];

                    // Merge shared data with plotly_data if provided
                    var figure = {{}};
                    var plotlyConfig = {plotly_data_json};
                    if (plotlyConfig && typeof plotlyConfig === 'object') {{
                        figure = plotlyConfig;
                        // If shared data contains GeoJSON features, add them
                        if (sharedData.features && figure.data && figure.data.length > 0) {{
                            figure.data[0].geojson = sharedData;
                        }}
                    }} else {{
                        // Use only shared data
                        figure = {{
                            data: [{{
                                type: 'choropleth',
                                geojson: sharedData,
                                locations: [],
                                z: []
                            }}],
                            layout: {{
                                geo: {{projection: {{type: "natural earth"}}, scope: "world"}},
                                margin: {{"r":0,"t":0,"l":0,"b":0}}
                            }}
                        }};
                    }}

                    if (typeof Plotly !== 'undefined') {{
                        var config = {{
                            responsive: true,
                            displayModeBar: true,
                            displaylogo: false,
                            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
                        }};

                        if (!figure.layout) {{
                            figure.layout = {{}};
                        }}

                        figure.layout.autosize = true;
                        if (window.respysiveTheme) window.respysiveTheme.plotly(figure);

                        Plotly.newPlot('{chart_id}', figure.data, figure.layout, config);
                    }} else {{
                        document.getElementById('{chart_id}').innerHTML =
                            '<p style="color:red;">Error: Plotly.js is not loaded</p>';
                    }}
                }} catch(error) {{
                    console.error('Error rendering Plotly chart:', error);
                    document.getElementById('{chart_id}').innerHTML =
                        '<p style="color:red;">Error rendering chart</p>';
                }}
            }})();
        </script>"""
        else:
            if hasattr(plotly_data, "to_json"):
                json_str = plotly_data.to_json()
            elif isinstance(plotly_data, dict):
                json_str = json.dumps(plotly_data)
            elif isinstance(plotly_data, str):
                json_str = plotly_data
            else:
                raise ValueError("plotly_data must be a Figure object, dictionary or JSON string")

            json_escaped = json_str.replace("'", "\u2019").replace('"', '\\"')

            html_content = f"""
        <div {s} id='{chart_id}' style='width:{chart_width}; height:{chart_height};'></div>
        <script type="text/javascript">
            (function() {{
                // Initialize global cache for parsed JSON data
                if (!window._respysive_cache) {{
                    window._respysive_cache = {{}};
                }}

                try {{
                    var plotlyData = "{json_escaped}";

                    // Use cached figure if available, otherwise parse and cache
                    var cacheKey = 'plotly_{chart_id}';
                    if (!window._respysive_cache[cacheKey]) {{
                        window._respysive_cache[cacheKey] = JSON.parse(plotlyData.replace(/\\u2019/g, "'").replace(/\\\\"/g, '"'));
                    }}
                    var figure = window._respysive_cache[cacheKey];

                    if (typeof Plotly !== 'undefined') {{
                        var config = {{
                            responsive: true,
                            displayModeBar: true,
                            displaylogo: false,
                            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
                        }};

                        if (!figure.layout) {{
                            figure.layout = {{}};
                        }}

                        figure.layout.autosize = true;
                        if (window.respysiveTheme) window.respysiveTheme.plotly(figure);

                        Plotly.newPlot('{chart_id}', figure.data, figure.layout, config);
                    }} else {{
                        document.getElementById('{chart_id}').innerHTML =
                            '<p style="color:red;">Error: Plotly.js is not loaded</p>';
                    }}
                }} catch(error) {{
                    console.error('Error rendering Plotly chart:', error);
                    document.getElementById('{chart_id}').innerHTML =
                        '<p style="color:red;">Error rendering chart</p>';
                }}
            }})();
        </script>"""

        self.content += html_content

    def add_altair(self, json: str, **kwargs):
        """Add an Altair/Vega-Lite chart to the document.

        Args:
            json: Vega-Lite JSON specification string (from chart.to_json()).
            **kwargs: CSS styles and classes. Use underscores for CSS properties
                (e.g. font_size='20px'). Use 'class' for Bootstrap classes.
        """
        if "class" not in kwargs:
            kwargs["class"] = []
        elif isinstance(kwargs["class"], str):
            kwargs["class"] = [kwargs["class"]]
        kwargs["class"].append("img-fluid")

        s = _parse_style_class(kwargs)

        chart_id = "chart-" + str(uuid.uuid4())
        self.content += f"""<div {s} id='{chart_id}'></div>
        <script>var opt = {{renderer: "svg", config: window.respysiveTheme && window.respysiveTheme.vega}};
        vegaEmbed("#{chart_id}", {json} , opt);</script>"""

    def add_div(self, div: str, **kwargs):
        """Add raw HTML content wrapped in a div element.

        Args:
            div: HTML content string to wrap.
            **kwargs: CSS styles and classes. Use underscores for CSS properties
                (e.g. font_size='20px'). Use 'class' for Bootstrap classes.
        """

        s = _parse_style_class(kwargs)
        self.content += f"""<div {s}>{div}</div>"""

    def add_fig(self, src: Figure, alt: str = "", as_svg=True, **kwargs):
        """Add an image element to the HTML document from a Matplotlib Figure.

        Args:
            as_svg: Whether to save the figure as SVG or PNG.
            src: The Matplotlib Figure object.
            alt: The alternative text for the image.
            kwargs: Additional CSS styles and HTML class to apply to the image.
                The keys should be in the format of CSS property names with '_' instead of '-',
                for example: font_size.
                You can also pass the 'class' key with a string or a list of strings.
                Example: {'font_size': '20px', 'color': 'blue', 'class': 'my-class'} or
                {'font_size': '20px', 'color': 'blue', 'class': ['my-class', 'my-second-class']}
        """
        if "class" not in kwargs:
            kwargs["class"] = []
        elif isinstance(kwargs["class"], str):
            kwargs["class"] = [kwargs["class"]]
        kwargs["class"].append("img-fluid")
        s = _parse_style_class(kwargs)

        buffer = BytesIO()
        if as_svg:
            src.savefig(buffer, format="svg")
            svg = buffer.getvalue()
            svg = svg.replace(b"\n", b"").decode("utf-8")
            self.content += f"""<div {s}>{svg}</div>"""
        else:
            src.savefig(buffer, format="png")
            image_data = buffer.getvalue()
            image_base64 = base64.b64encode(image_data).decode("utf-8")
            image_src = f"data:image/png;base64,{image_base64}"
            self.content += f"""<img src="{image_src}" alt="{alt}" {s}>"""
        buffer.close()

    def render(self):
        """Return the accumulated HTML content as a prettified string.

        Returns:
            str: Indented HTML string of all added content.
        """
        html = f"""<div>{self.content}</div>"""
        soup = BeautifulSoup(html, "html.parser")
        ident_content = soup.prettify()
        return ident_content
