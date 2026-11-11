"""Custom JSON configuration handler for external JavaScript libraries."""

import json
import re
import uuid
from typing import Any

from .base import BaseHandler


class CustomJsonHandler(BaseHandler):
    """Handler for custom library configurations loaded via CDN.

    Processes dictionaries with ``library`` and ``config`` keys,
    generates container divs, loads CSS/JS from CDN, and runs
    initialization scripts.

    Priority: 5.
    """

    @property
    def priority(self) -> int:
        return 5

    def can_handle(self, content: Any) -> bool:
        """Check if content is a custom JSON configuration.

        Requires a dict with at least ``library`` and ``config`` keys.

        Args:
            content: Content to check.

        Returns:
            bool: True if content has the required keys.
        """
        if not isinstance(content, dict):
            return False

        required_keys = ["library", "config"]
        return all(key in content for key in required_keys)

    def handle(self, content: Any, shared_data_id: str | None = None, forced: bool = False, **kwargs) -> str:
        """Process custom JSON configuration and generate HTML with CDN and script.

        Expected content structure::

            {
                "library": "maplibre-gl",
                "version": "2.4.0",
                "cdn": {
                    "css": ["https://unpkg.com/maplibre-gl@2.4.0/dist/maplibre-gl.css"],
                    "js": ["https://unpkg.com/maplibre-gl@2.4.0/dist/maplibre-gl.js"]
                },
                "config": {
                    "container": "map-container",
                    "style": "https://demotiles.maplibre.org/style.json",
                    "center": [2.3522, 48.8566],
                    "zoom": 10
                },
                "init_script": "new maplibregl.Map({config_placeholder})",
                "div_style": {"height": "400px", "width": "100%"}
            }

        Args:
            content: Custom JSON configuration dictionary
            shared_data_id: Optional shared data identifier
            forced: Whether this handler was forced
            **kwargs: Additional styling options

        Returns:
            HTML string with embedded library and initialization script
        """
        if not self.can_handle(content):
            raise ValueError("Content must be a valid custom JSON configuration")

        library = content["library"]
        cdn_config = content.get("cdn", {})
        config = dict(content["config"])  # the caller may reuse its config for another chart
        init_script = content.get("init_script", "")
        div_style = content.get("div_style", {"height": "400px", "width": "100%"})

        container_id = f"{library}-{str(uuid.uuid4())[:8]}"
        if "container" not in config:
            config["container"] = container_id
        else:
            container_id = config["container"]

        css_links = ""
        if "css" in cdn_config:
            for css_url in cdn_config["css"]:
                css_links += f'<link rel="stylesheet" href="{css_url}">\n'

        js_scripts = ""
        if "js" in cdn_config:
            for js_url in cdn_config["js"]:
                js_scripts += f'<script src="{js_url}"></script>\n'

        from respysive.utils import _parse_style_class, _script_json

        center_style = {"class": ["d-flex", "justify-content-center", "mx-auto"]}
        combined_kwargs = {**center_style, **kwargs}
        style_attr = _parse_style_class(combined_kwargs)

        div_style_str = "; ".join([f"{k.replace('_', '-')}: {v}" for k, v in div_style.items()])

        config_json = _script_json(json.dumps(config, indent=2))
        # library names such as "chart.js" are not JavaScript identifiers
        init_name = "initialize_" + re.sub(r"\W", "_", library)

        if init_script:
            final_init_script = init_script
        else:
            if "maplibre" in library.lower():
                final_init_script = "new maplibregl.Map(parsedConfig)"
            else:
                final_init_script = f"console.log('Initialize {library} with config:', parsedConfig)"

        script_id = f"{library}-script-{str(uuid.uuid4())[:8]}"

        html_content = f"""
        {css_links}
        <div {style_attr}>
            <div id="{container_id}" style="{div_style_str}"></div>
        </div>
        {js_scripts}
        <script type="text/javascript" id="{script_id}">
            // Configuration for {library}
            (function() {{
                var config = {config_json};
                config.container = "{container_id}";

                function {init_name}() {{
                    try {{
                        var parsedConfig = config;

                        // Execute initialization script
                        {final_init_script};

                        console.log('{library} initialized successfully');

                    }} catch(error) {{
                        console.error('Error initializing {library}:', error);
                        var errorDiv = document.getElementById('{container_id}');
                        if (errorDiv) {{
                            errorDiv.innerHTML = '<p style="color:red; text-align:center; padding:20px;">Error loading {library}: ' + error.message + '</p>';
                        }}
                    }}
                }}

                // Wait for DOM and scripts to be ready
                if (document.readyState === 'loading') {{
                    document.addEventListener('DOMContentLoaded', function() {{
                        setTimeout({init_name}, 500);
                    }});
                }} else {{
                    setTimeout({init_name}, 500);
                }}

            }})();
        </script>"""

        return html_content
