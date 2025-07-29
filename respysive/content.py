from bs4 import BeautifulSoup
import requests
from matplotlib.figure import Figure
from io import BytesIO
import base64
import uuid
import json
from respysive.utils import _parse_style_class


class Content:
    """
    A class representing a slide content.
    """

    def __init__(self):

        self.content = ""
        self.scripts = {}
        self.grid_cols = 0
        self.shared_data = {}

    def clear(self):
        self.content = ""
        self.shared_data = {}

    def add_script(self, name: str, script: str):
        """
        Add a script to the HTML document
        :param name : name of the script
        :param script : script to add
        """
        self.scripts[name] = script

    def add_shared_data(self, data_id: str, data, data_type: str = "json"):
        """
        Store shared data (JSON/GeoJSON) that can be referenced by multiple charts
        :param data_id: Unique identifier for the data
        :param data: The data to store (dict, str, or object with to_json method)
        :param data_type: Type of data ('json', 'geojson')
        """
        if hasattr(data, 'to_json'):
            json_str = data.to_json()
        elif isinstance(data, dict):
            json_str = json.dumps(data)
        elif isinstance(data, str):
            json_str = data
        else:
            raise ValueError("data must be an object with to_json method, a dictionary, or a JSON string")
        
        self.shared_data[data_id] = {
            'data': json_str,
            'type': data_type
        }
        
        # Add hidden div with the data
        self.content += f'<div id="shared-data-{data_id}" style="display:none;" data-type="{data_type}">{json_str}</div>'

    def add_heading(self, text: str, tag: str = "h3", icon: str = None, **kwargs):
        """
        Add a heading element to the HTML document.
        :param text: The text of the heading.
        :param tag: The HTML tag to use for the heading. Default is 'h1'.
        :param icon: The icon of the heading (optional).
        :param kwargs: Additional CSS styles and html class to apply to the image. (optional)
                The keys should be in the format of CSS property names with '_' instead of '-', example: font_size
                you can also pass the class key with a string or a list of strings
                example : {'font_size': '20px', 'color': 'blue', 'class':'my-class'} or  {'font_size': '20px',
                 'color': 'blue', 'class':['my-class','my-second-class']}
        """
        if tag not in ["h1", "h2", "h3", "h4", "h5"]:
            raise ValueError("Invalid tag, the tag must be one of h1, h2, h3, h4 or h5")

        s = _parse_style_class(kwargs)

        self.content += (

            f"<{tag} {s}><i class='{icon}'></i> {text}</{tag}>"
            if icon
            else f"<{tag} {s}>{text}</{tag}>"
        )

    def add_text(self, text: str, tag: str = "p", **kwargs):
        """
        Add a text element to the HTML document.
        :param text: The text to be added.
        :param tag: The HTML tag to use for the text. Default is 'p'.
        :param kwargs: Additional CSS styles and html class to apply to the image. (optional)
                The keys should be in the format of CSS property names with '_' instead of '-', example: font_size
                you can also pass the class key with a string or a list of strings
                example : {'font_size': '20px', 'color': 'blue', 'class':'my-class'} or  {'font_size': '20px',
                 'color': 'blue', 'class':['my-class','my-second-class']}
        """
        if tag not in ["p", "span"]:
            raise ValueError("Invalid tag, the tag must be one of p or span")

        s = _parse_style_class(kwargs)

        self.content += f"""<{tag} {s}>{text}</{tag}>"""

    def add_list(
            self, items: list, ordered=False, **kwargs):
        """
        Add a list element to the HTML document.
        :param items: The items of the list.
        :param ordered: Whether the list should be ordered or not.
        :param kwargs: Additional CSS styles and html class to apply to the image. (optional)
                The keys should be in the format of CSS property names with '_' instead of '-', example: font_size
                you can also pass the class key with a string or a list of strings
                example : {'font_size': '20px', 'color': 'blue', 'class':'my-class'} or  {'font_size': '20px',
                 'color': 'blue', 'class':['my-class','my-second-class']}
        """
        list_tag = "ol" if ordered else "ul"

        s = _parse_style_class(kwargs)

        list_items = "\n".join([f"<li>{item}</li>" for item in items])
        self.content += f"<{list_tag} {s}>\n{list_items}\n</{list_tag}>"

    def add_image(self, src: str, alt: str = "", **kwargs):
        """
        Add an image element to the HTML document.
        :param src: The source of the image (local file path or URL).
        :param alt: The alternative text for the image.
        :param kwargs: Additional CSS styles and html class to apply to the image. (optional)
                The keys should be in the format of CSS property names with '_' instead of '-', example: font_size
                you can also pass the class key with a string or a list of strings
                example : {'font_size': '20px', 'color': 'blue', 'class':'my-class'} or  {'font_size': '20px',
                 'color': 'blue', 'class':['my-class','my-second-class']}
        """

        if 'class' not in kwargs:
            kwargs['class'] = []
        elif isinstance(kwargs['class'], str):
            kwargs['class'] = [kwargs['class']]
        kwargs['class'].append('img-fluid')
        
        if src.lower().endswith('.svg') and 'max_width' not in kwargs:
            kwargs['max_width'] = '100%'

        if src.startswith(('http://', 'https://')):
            response = requests.get(src)
            try:
                image_data = response.content
            except :
                raise Exception(f"Failed to fetch image from URL: {src}")
        else:
            with open(src, "rb") as f:
                image_data = f.read()

        if src.lower().endswith('.svg'):
            mime_type = "image/svg+xml"
        elif src.lower().endswith(('.jpg', '.jpeg')):
            mime_type = "image/jpeg"
        elif src.lower().endswith('.png'):
            mime_type = "image/png"
        elif src.lower().endswith('.gif'):
            mime_type = "image/gif"
        else:
            mime_type = "image/png"
            
        image_base64 = base64.b64encode(image_data).decode("utf-8")
        image_src = f"data:{mime_type};base64,{image_base64}"

        s = _parse_style_class(kwargs)
        self.content += f"""<img src="{image_src}" alt="{alt}" {s}>"""
        # self.content += f"<img data-src='{src}' alt='{alt}' {s}>"

    def add_svg(self, svg: str, **kwargs):
        """
        Add a svg to the document.
        :param svg : The code of the svg.
        :param kwargs: Additional CSS styles and html class to apply to the image. (optional)
                The keys should be in the format of CSS property names with '_' instead of '-', example: font_size
                you can also pass the class key with a string or a list of strings
                example : {'font_size': '20px', 'color': 'blue', 'class':'my-class'} or  {'font_size': '20px',
                 'color': 'blue', 'class':['my-class','my-second-class']}
        """

        if 'class' not in kwargs:
            kwargs['class'] = []
        elif isinstance(kwargs['class'], str):
            kwargs['class'] = [kwargs['class']]
        kwargs['class'].append('img-fluid')

        s = _parse_style_class(kwargs)

        self.content += f"""<div {s}>{svg}</div>"""

    def add_plotly(self, plotly_data, shared_data_id=None, **kwargs):

        if 'class' not in kwargs:
            kwargs['class'] = []
        elif isinstance(kwargs['class'], str):
            kwargs['class'] = [kwargs['class']]
        kwargs['class'].append('img-fluid')

        s = _parse_style_class(kwargs)

        chart_id = "plotly-chart-" + str(uuid.uuid4())
        
        if shared_data_id:
            if shared_data_id not in self.shared_data:
                raise ValueError(f"Shared data with ID '{shared_data_id}' not found. Use add_shared_data() first.")
            
            plotly_data_json = json.dumps(plotly_data) if plotly_data else 'null'
            
            html_content = f"""
        <div {s} id='{chart_id}' style='width:100%; height:400px;'></div>
        <script type="text/javascript">
            (function() {{
                try {{
                    var sharedDataElement = document.getElementById('shared-data-{shared_data_id}');
                    if (!sharedDataElement) {{
                        throw new Error('Shared data element not found');
                    }}
                    var sharedData = JSON.parse(sharedDataElement.textContent);
                    
                    // Merge shared data with plotly_data if provided
                    var figure = {{}};
                    var plotlyConfig = {plotly_data_json};
                    if (plotlyConfig && typeof plotlyConfig === 'object') {{
                        figure = plotlyConfig;
                        // Si les données partagées contiennent des features GeoJSON, les ajouter
                        if (sharedData.features && figure.data && figure.data.length > 0) {{
                            figure.data[0].geojson = sharedData;
                        }}
                    }} else {{
                        // Utiliser uniquement les données partagées
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

                        Plotly.newPlot('{chart_id}', figure.data, figure.layout, config);
                    }} else {{
                        document.getElementById('{chart_id}').innerHTML = 
                            '<p style="color:red;">Erreur: Plotly.js n\\'est pas chargé</p>';
                    }}
                }} catch(error) {{
                    console.error('Erreur lors du rendu du graphique Plotly:', error);
                    document.getElementById('{chart_id}').innerHTML = 
                        '<p style="color:red;">Erreur lors du rendu du graphique</p>';
                }}
            }})();
        </script>"""
        else:
            if hasattr(plotly_data, 'to_json'):
                json_str = plotly_data.to_json()
            elif isinstance(plotly_data, dict):
                json_str = json.dumps(plotly_data)
            elif isinstance(plotly_data, str):
                json_str = plotly_data
            else:
                raise ValueError("plotly_data doit être un objet Figure, un dictionnaire ou une string JSON")

            json_escaped = json_str.replace("'", "\u2019").replace('"', '\\"')

            html_content = f"""
        <div {s} id='{chart_id}' style='width:100%; height:400px;'></div>
        <script type="text/javascript">
            (function() {{
                try {{
                    var plotlyData = "{json_escaped}";
                    var figure = JSON.parse(plotlyData.replace(/\\u2019/g, "'").replace(/\\\\"/g, '"'));

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

                        Plotly.newPlot('{chart_id}', figure.data, figure.layout, config);
                    }} else {{
                        document.getElementById('{chart_id}').innerHTML = 
                            '<p style="color:red;">Erreur: Plotly.js n\\'est pas chargé</p>';
                    }}
                }} catch(error) {{
                    console.error('Erreur lors du rendu du graphique Plotly:', error);
                    document.getElementById('{chart_id}').innerHTML = 
                        '<p style="color:red;">Erreur lors du rendu du graphique</p>';
                }}
            }})();
        </script>"""

        self.content += html_content

    def add_altair(self, json: str, **kwargs):
        """
        Add an Altair json to the document.
        :param json : an Altair json (chart.to_json()).
        :param kwargs: Additional CSS styles and html class to apply to the image. (optional)
        The keys should be in the format of CSS property names with '_' instead of '-', example: font_size
        you can also pass the class key with a string or a list of strings
        example : {'font_size': '20px', 'color': 'blue', 'class':'my-class'} or  {'font_size': '20px',
        'color': 'blue', 'class':['my-class','my-second-class']}

        """
        if 'class' not in kwargs:
            kwargs['class'] = []
        elif isinstance(kwargs['class'], str):
            kwargs['class'] = [kwargs['class']]
        kwargs['class'].append('img-fluid')

        s = _parse_style_class(kwargs)

        chart_id = "chart-" + str(uuid.uuid4())
        self.content += f"""<div {s} id='{chart_id}'></div>
        <script>var opt = {{renderer: "svg"}};
        vegaEmbed("#{chart_id}", {json} , opt);</script>"""

    def add_div(self, div: str, **kwargs):
        """
        Add a simple div.
        :param div : whatever you want that can fit in a div .
        :param kwargs: Additional CSS styles and html class to apply to the image. (optional)
        The keys should be in the format of CSS property names with '_' instead of '-', example: font_size
        you can also pass the class key with a string or a list of strings
        example : {'font_size': '20px', 'color': 'blue', 'class':'my-class'} or  {'font_size': '20px',
        'color': 'blue', 'class':['my-class','my-second-class']}
        """

        s = _parse_style_class(kwargs)
        self.content += f"""<div {s}>{div}</div>"""

    def add_fig(self, src: Figure, alt: str = "", as_svg=True, **kwargs):
        """
        Add an image element to the HTML document from a Matplotlib Figure.
        :param as_svg: Whether to save the figure as SVG or PNG.
        :param src: The Matplotlib Figure object.
        :param alt: The alternative text for the image.
        :param kwargs: Additional CSS styles and HTML class to apply to the image.
                       The keys should be in the format of CSS property names with '_' instead of '-',
                       for example: font_size.
                       You can also pass the 'class' key with a string or a list of strings.
                       Example: {'font_size': '20px', 'color': 'blue', 'class': 'my-class'} or
                                {'font_size': '20px', 'color': 'blue', 'class': ['my-class', 'my-second-class']}
        """
        if 'class' not in kwargs:
            kwargs['class'] = []
        elif isinstance(kwargs['class'], str):
            kwargs['class'] = [kwargs['class']]
        kwargs['class'].append('img-fluid')
        s = _parse_style_class(kwargs)

        buffer = BytesIO()
        if as_svg:
            src.savefig(buffer, format='svg')
            svg = buffer.getvalue()
            svg = svg.replace(b'\n', b'').decode('utf-8')
            self.content += f"""<div {s}>{svg}</div>"""
        else:
            src.savefig(buffer, format='png')
            image_data = buffer.getvalue()
            image_base64 = base64.b64encode(image_data).decode("utf-8")
            image_src = f"data:image/png;base64,{image_base64}"
            self.content += f"""<img src="{image_src}" alt="{alt}" {s}>"""
        buffer.close()

    def add_optimized_plotly(self, config, geojson_div_id, **kwargs):
        """
        Add a Plotly chart that references global GeoJSON data.
        
        :param config: Plotly configuration without geojson data
        :param geojson_div_id: ID of the global GeoJSON div
        :param kwargs: Additional CSS styles and html class to apply
        """
        import uuid
        import json
        
        if 'class' not in kwargs:
            kwargs['class'] = []
        elif isinstance(kwargs['class'], str):
            kwargs['class'] = [kwargs['class']]
        kwargs['class'].append('img-fluid')

        from respysive.utils import _parse_style_class
        s = _parse_style_class(kwargs)

        unique_id = f"plotly-chart-{uuid.uuid4()}"
        config_json = json.dumps(config).replace('"', '\\"')

        html_content = f"""
        <div {s} id='{unique_id}' style='width:100%; height:400px;'></div>
        <script type="text/javascript">
            (function() {{
                try {{
                    var geojsonDiv = document.getElementById('{geojson_div_id}');
                    if (!geojsonDiv) {{
                        console.error('Global GeoJSON div not found: {geojson_div_id}');
                        document.getElementById('{unique_id}').innerHTML = 
                            '<p style="color:red;">Error: GeoJSON not found (ID: {geojson_div_id})</p>';
                        return;
                    }}
                    
                    var geojsonData = JSON.parse(geojsonDiv.textContent);
                    var figureConfig = "{config_json}";
                    var figure = JSON.parse(figureConfig.replace(/\\\\"/g, '"'));
                    
                    if (figure.data) {{
                        figure.data.forEach(function(trace) {{
                            if (trace.type === 'choropleth') {{
                                trace.geojson = geojsonData;
                            }}
                        }});
                    }}
                    
                    if (typeof Plotly !== 'undefined') {{
                        var plotlyConfig = {{
                            responsive: true,
                            displayModeBar: true,
                            displaylogo: false,
                            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
                        }};
                        
                        if (!figure.layout) figure.layout = {{}};
                        figure.layout.autosize = true;
                        
                        Plotly.newPlot('{unique_id}', figure.data, figure.layout, plotlyConfig);
                    }} else {{
                        console.error('Plotly.js is not loaded');
                        document.getElementById('{unique_id}').innerHTML = 
                            '<p style="color:red;">Error: Plotly.js is not loaded</p>';
                    }}
                }} catch(error) {{
                    console.error('Error rendering Plotly chart:', error);
                    document.getElementById('{unique_id}').innerHTML = 
                        '<p style="color:red;">Error: ' + error.message + '</p>';
                }}
            }})();
        </script>"""
        
        self.content += html_content

    def render(self):
        """
        Return the complete HTML document as a string.
        """
        html = f"""<div>{self.content}</div>"""
        soup = BeautifulSoup(html, "html.parser")
        ident_content = soup.prettify()
        return ident_content
