import re


def _parse_style_class(style: dict):
    if style:
        style_str = ""
        class_str = ""
        for key, value in style.items():
            if key == 'class':
                if isinstance(value, str):
                    class_str = f"class='{value}'"
                elif isinstance(value, list):
                    class_str = f"class='{' '.join(value)}'"
                else:
                    raise ValueError("Invalid class, the class must be a string or a list of strings")
            else:
                if isinstance(value, (str, int, float)):
                    css_key = key.replace("_", "-")
                    style_str += f"{css_key}: {value};"
                else:
                    raise ValueError(f"Invalid value for {key}, the value must be a string, int or float")
        
        result_parts = []
        if style_str:
            result_parts.append(f"style='{style_str}'")
        if class_str:
            result_parts.append(class_str)
        return " ".join(result_parts)
    return ""


def process_markdown_with_latex(text: str) -> str:
    """
    Process markdown text with LaTeX math support.
    Converts $...$ to inline math and $$...$$ to display math.
    """
    try:
        import markdown
        
        text = re.sub(r'\$\$(.*?)\$\$', r'\\\\[\1\\\\]', text, flags=re.DOTALL)
        text = re.sub(r'\$(.*?)\$', r'\\\\(\1\\\\)', text)
        
        md = markdown.Markdown(extensions=['extra', 'codehilite'])
        html = md.convert(text)
            
        return html
        
    except ImportError:
        text = re.sub(r'\$\$(.*?)\$\$', r'\\\\[\1\\\\]', text, flags=re.DOTALL)
        text = re.sub(r'\$(.*?)\$', r'\\\\(\1\\\\)', text)
        return text.replace('\n', '<br>')
        
        
