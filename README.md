# respysive-slide
___
A Python package that allows you to create interactive presentations using Python, Bootstrap and Reveal.js. 
Charts from Altair and Plotly can also be added.

You will find an [example here](https://raw.githack.com/fbxyz/respysive-slide/master/readme_example.html)


___
## Installation
With PyPI 
```
pip install respysive-slide
```


You can also clone the [repo](https://github.com/fbxyz/respysive-slide) and import respysive as a module

___
## Usage

The package consists of three main classes: `Content`, `Container` and `Presentation`.

`Container` is used to create a unique slide. You can add various elements to it such as text, headings, images, and lists.

`Content` is used to add HTML tag to a `Container` (i.e. a slide)

`BootstrapPresentation` is used to create the final presentation. You can add slides to it and then render the presentation as an HTML file.

### Title slide
Here's an example of how to use respysive by creating a title slide

```python
from respysive import Content, Presentation, Container

# A new Container instance is created. The slide will be centered
sld_0 = Container(center=True)

# each `with` statement create a new row for the current slide
with sld_0:
    col1 = Content()

    # css style and class are passed as kwargs
    css_class = {'color': '#e63946', 'class': ['r-fit-text']}
    col1.add_heading(text="The main Title", tag="h1", **css_class)

    # col1 is added in a 12 width Bootstrap columns (default value)
    sld_0.add_col(col1.render(), col_class="col-12")
```

A second row for the subtitle is created inside the sld_0 container
```python

with sld_0:
    col2 = Content()
    url = '<a href="https://github.com/fbxyz/respysive-slide" target="_blank">' \
          'https://github.com/fbxyz/respysive-slide</a>'
    col2.add_heading(text=url, tag="h4")
    sld_0.add_col(col2.render())
```

A final row for the authors (column of width 8) next to a logo (column of width 4)
```python
logo_url = "https://upload.wikimedia.org/wikipedia/commons/4/4d/Fractal_canopy.svg"

with sld_0:
    col3a = Content()
    col3a.add_text(text="Author 1, Author 2", tag="p")

    # my-auto is used to vertically center the text in the column
    css_class = {'class': 'my-auto'}
    sld_0.add_col(col3a.render(), "col-8", **css_class)
    col3b = Content()
    css_img = {'width': 'auto', 'height': '80%', 'filter': 'invert(100%) opacity(30%)',
               'class': ['mx-auto', 'my-auto', 'd-block']}
    col3b.add_image(logo_url, **css_img)
    sld_0.add_col(col3b.render(), "col-4")
```

![sld_title.png](assets%2Fimg%2Fsld_title.png)

### One column text slide

Same workflow is used to create a text slide with a title

 ```python
# A new slide is created by instancing Container()
sld_1 = Container()
with sld_1:
    col1 = Content()
    col1.add_heading(text="Your slide title ", tag="h3", icon="fas fa-infinity fa-beat")
    sld_1.add_col(col1.render(), "col-12")
 ```
For the add_heading() method, [Fontawesome icons](https://fontawesome.com/icons) can be added.

 ```python    
long_text = """
En cosmologie, le modèle de l'univers fractal désigne un modèle cosmologique 
dont la structure et la répartition de la matière possèdent une dimension fractale, 
et ce, à plusieurs niveaux. De façon plus générale, il correspond à l'usage ou 
l'apparence de fractales dans l'étude de l'Univers et de la matière qui le compose.
\n Ce modèle présente certaines lacunes lorsqu'il est utilisé à de très grandes ou de 
très petites échelles
"""

univ_url = "https://upload.wikimedia.org/wikipedia/commons/d/d5/Univers_Fractal_J.H..jpg"

with sld_1:
    col2a = Content()
    fragment = {'class': ['fragment']}
    col2a.add_text(text=long_text, **fragment)
    css = {'text-align': 'justify', "font-size": "80%"}
    sld_1.add_col(col2a.render(), "col-8", **css)

    col2b = Content()
    css_class = {"border": "1px solid #ddd", 'border-radius': "4px",
                 'class': ['rounded']}
    col2b.add_image(univ_url,**css_class)
    sld_1.add_col(col2b.render(), "col-4")
```

class : ['fragment'] is used to pass reveal (fragments)[https://revealjs.com/fragments/]

![sld_content_1col.png](assets%2Fimg%2Fsld_content_1col.png)

### Markdown use 

Markdown can be used to easily add text to each slide. You may need to install the Markdown package.

```python
from markdown import markdown

sld_2 = Container()
with sld_2:
    title = Content()
    title.add_heading(text="Markdown use", tag="h3")
    sld_2.add_col(title.render(), "col-12")

my_txt = markdown("""You can also use the **markdown** package to easily add text""")

txt_col1 = markdown("""or unordered list : 

- first bullet
- second bullet
""")

txt_col2 = markdown("""and ordered list : 

1. first element
2. second element
""")

with sld_2:
    txt = Content()
    txt.add_text(text=my_txt)
    sld_2.add_col(txt.render(), "col-12")

with sld_2:
    col1 = Content()
    col1.add_text(text=txt_col1)
    css70 = {"font-size": "70%"}
    sld_2.add_col(col1.render(), "col-6", **css70)

    col2 = Content()
    col2.add_text(text=txt_col2, )
    sld_2.add_col(col2.render(), "col-6", **css70)
```
![sld_content_2cols.png](assets%2Fimg%2Fsld_content_2cols.png)

### Two columns slide : image and svg

```python
sld_3 = Container()
svg = """<svg xmlns="http://www.w3.org/2000/svg" width="329.1" height="285" viewBox="0 0 87.1 75.4">
  <path d="M16 107h87L60 32Z" style="fill:none;fill-opacity:1;fill-rule:evenodd;stroke:#fff;stroke-width:.0513732;stroke-linecap:butt;stroke-linejoin:miter;stroke-dasharray:none;stroke-opacity:1" transform="translate(-16 -32)"/>
  <path d="M27 88h22l-11 19Zm28 17h1v1zm1-1h1l-1 1zm-4 3h1-1zm1-2v1zm-1-1h1l-1 1zm-1-1h1l-1 1zm-1 1h1v1zm0 1v1zm0 2h1zm-1 0h1-1zm-3-4v1zm-2 2h1v1zm1-1h1l-1 1zm1 0h1v1zm1 1h1l-1 1zm1 2zm-2 0h1zm-1 0h1-1zm-1 0zm-2 0h1zm-1 0h1-1zm-1 0zm2-2v1zm-1-1h1l-1 1zm14-2v1zm-2 0h1l-1 1zm-1 0h1l-1 1zm1-1zm-11 1h1v1zm2 0v1zm1 0h1l-1 1zm-1-1h1zm0-1zm9 0h1-1zm-8-3h1l-1 1Zm1 0h1v1Zm2 0v1Zm1 0h1l-1 1Zm1 0h1v1Zm2 0h1l-1 1Zm-2-1v1zm-3 0h1l-1 1zm-1-1h1v1zm4 0h1v1zm1 0zm-2-2h1-1Zm-1-1v1zm-1-1h3l-1 2zm-5 10zm0 0zm0 0zm-1 0h1zm1 1h1zm1 0v1zm-1 0v1zm-1 0h1l-1 1zm0 0zm0 0h1v1zm0 0v1zm0-1h2l-1 2zm2-3h1l-1 1zm0 0zm0 1h1zm0 0zm1 0v1zm0 1h1-1zm-1 0h1zm-1 0h1zm0-1h1v1zm1 1zm-1 0zm1-1h1l-1 1zm2 2zm0 0zm-1 0h1-1zm1 1zm0 0h1v1zm0 0v1zm-1 0zm0 0h1l-1 1zm-1 0h1v1zm1-1h1v2zm-2-1h3l-2 3zm3 5zm0 1zm-1 0h1-1zm1 0v1zm0 1h1zm0 0zm-1-1v1zm0 1h1-1zm-1 0h1zm1-1h1v1zm2-3zm0 0h1l-1 1zm-1 0h1v1zm2 1zm0 1zm-1 0h1-1zm-1-1zm0 1h1zm0 0zm0-1h2l-1 1zm2 1h1-1zm1 1zm-1 0zm1 0v1zm0 1h1-1zm0 0zm-1-1v1zm0 1zm-1 0h1-1zm1-1h1l-1 1zm-2-1h2l-1 2zm-6 0h1l-1 1zm0 0zm0 1h1zm0 0zm1 0v1zm0 1zm-1 0h1zm-1 0h1zm0-1h1v1zm1 1zm-1 0zm1-1h1l-1 1zm1-3h1v1zm0 0h1zm1 0v1zm-1 0v1zm1 1zm0 1h1zm0 0zm-1-1v1zm0 0zm0 1zm-1 0h1zm1-1h1v1zm2 1zm0 1zm-1 0h1zm1 0h1v1zm1 1zm-1 0zm-1-1v1zm0 1h1zm0 0zm0-1h2l-1 1zm-2-1h3l-1 2zm2-2h5l-3 4zm6-12h1l-1 1zm0 0h1-1zm1 1zm-1 0zm1 1zm0 0h1-1zm0 0zm-2 0h1zm1-1v1zm0 1zm-1 0h1-1zm1-1h1l-1 1zm1-3h1v1zm1 0zm0 0v1zm-1 0h1l-1 1zm1 1h1l-1 1zm0 0h1-1zm1 0v1zm-1 0v1zm-1 0v1zm0 0zm0 0h1l-1 1zm0 0v1zm0 0h1v1zm2 1v1zm0 0zm0 1h1-1zm0 0zm0 1h1zm1-1v1zm0 1zm-1 0h1-1zm-1-1h1l-1 1zm1 1zm-1 0zm0-1h2l-1 1zm1 4zm0 0h1l-1 1zm0 0v1zm1 1zm0 1Zm-1 0h1-1Zm-1-1h1-1zm1 1Zm-1 0Zm0-1h2l-1 1Zm2-3h1-1zm0-1h1l-1 1zm1 1zm-1 0zm1 1h1l-1 1zm0 0zm0 0h1v1zm0 0v1zm-1 0v1zm-1 0h1l-1 1zm1-1h1l-1 2zm2 2v1zm0 0zm0 0v1zm-1 0h1v1zm1 1h1l-1 1Zm0 0h1-1zm1 1Zm-1 0Zm-1-1zm0 1h1Zm0 0Zm0-1h1v1Zm-2-1h3l-2 2Zm-6 0h1v1zm1 0zm0 0v1zm-1 0h1l-1 1zm1 1zm0 1h1Zm0 0Zm-1-1v1Zm0 0zm0 1h1-1Zm-1 0h1Zm1-1h1v1Zm2-3zm0-1v1zm0 1h1-1zm-1 0h1zm2 1zm0 0v1zm-1 0h1l-1 1zm-1 0h1l-1 1zm0 0zm0 0h1v1zm0 0v1zm0-1h2l-1 2zm2 2h1-1zm1 0v1zm-1 0v1zm1 1zm0 1h1-1Zm0 0Zm-1-1zm0 1Zm-1 0h1-1Zm1-1h1l-1 1Zm-2-1h2l-1 2Zm1-3h5l-2 5Zm7 8zm0 0zm-1 0h1zm1 1h1-1zm1 0v1zm-1 0v1zm-1 0zm0 0h1v1zm0 0v1zm0-1h1v2zm2-3h1l-1 1zm0 0zm0 1h1zm0 0zm1 1zm0-1v1zm0 1zm-1 0h1zm-1-1h1l-1 1zm1 1zm-1 0zm0-1h2l-1 1zm2 2h1zm0 0h1zm1 0zm-1 0zm1 1h1l-1 1zm0 0zm0 0h1v1zm0 0v1zm-1 0zm0 0v1zm-1 0h1v1zm1-1h1v2zm-2-1h3l-2 3zm2 5h1zm1 1zm-1 0zm1 1h1-1zm0-1v1zm0 1h1zm0 0zm-1 0zm0-1v1zm0 1zm-1 0h1zm1-1h1v1zm2-3v1zm0 0zm0 0v1zm-1 0h1v1zm1 1h1v1zm0 0h1zm1 1zm-1 0zm-1-1zm0 1h1zm0 0zm0-1h2l-1 1zm2 1h1l-1 1zm0 0zm0 1h1zm0 0zm1 1zm0-1v1zm0 1zm-1 0h1zm-1 0h1zm0-1h1v1zm1 1zm-1 0zm1-1h1l-1 1zm-2-1h2l-1 2zm-6 0zm0 1h1-1zm0 0zm1 0v1zm0 1zm-1 0h1-1zm-1-1h1l-1 1zm1 1zm-1 0zm0-1h2l-1 1zm2-3h1-1zm1 0v1zm-1 0v1zm1 1zm0 1h1zm0 0zm-1-1zm0 1zm-1 0h1-1zm1-1h1l-1 1zm2 1zm0 1zm-1 0h1zm1 1h1-1zm0-1h1l-1 1zm1 1zm-1 0zm-1-1v1zm0 1h1zm0 0zm0-1h1v1zm-2-1h3l-2 2zm1-2h6l-3 4zm-8-5h11l-5 9zm1-11h1zm1-2h1l-1 1zm-4 3h1-1zm1-1zm-1-2h1l-1 1zm-1-1h1v1zm0 1v1zm-1 2h1-1zm1 1zm-2 0h1zm-3-4h1l-1 1zm-1 3zm0-2h1l-1 1zm2 0v1zm0 2h1-1zm1 1h1-1zm-1 0zm-2 0h1-1zm-1 0h1-1zm-2 0h1zm-1 0h1-1zm-1 0zm2-1zm-1-2h1l-1 1zm14-2v1zm-2 0h1v1zm-1 0h1l-1 1zm1-1zm-11 1h1v1zm2 0h1l-1 1zm1 0h1l-1 1zm0-1zm-1-1h1-1zm9 0h1zm-8-3h1l-1 1zm2 0v1zm1 0h1l-1 1zm1 0h1v1zm2 0v1zm1 0h1l-1 1zm-2-1h1l-1 1zm-3 0h1l-1 1zm0-1v1zm4 0v1zm0 0zm-2-2h1zm-1-1v1zm-1-1h3l-1 2zm-5 10zm0 0zm0 0h1-1Zm0 0zm1 1zm0 0v1zm-1 0h1l-1 1Zm-1 0h1l-1 1zm0 0h1-1zm1 0v1zm-1 0v1zm0-1h2l-1 2zm2-2h1-1zm0-1h1l-1 1zm1 1zm-1 0zm1 0v1zm0 1h1zm0 0zm-2 0h1zm1-1v1zm0 1zm-1 0h1-1Zm1-1h1l-1 1zm2 2zm0 0zm-1 0h1zm1 1h1-1zm1 0v1zm-1 0v1zm-1 0zm0 0h1v1zm0 0v1zm0-1h1v2zm-2-1h3l-2 3zm3 5v1zm0 1zm-1 0h1zm1 1h1-1zm1 0zm-1 0zm-1 0zm0 0h1zm0 0zm0-1h1v1zm2-3zm0 1h1zm0 0zm1 0zm0 1zm-1 0h1zm-1-1h1-1zm1 1zm-1 0zm0-1h2l-1 1zm2 1h1l-1 1zm1 1zm-1 0zm1 1zm0 0h1zm0 0zm-1 0zm0 0zm-1 0h1zm1-1h1l-1 1zm-2-1h2l-1 2zm-6 1h1-1zm0-1v1zm0 1h1zm0 0zm1 1zm0 0h1-1zm-1 0h1zm-1 0h1zm1 0zm0 0zm-1 0h1-1zm1-1h1l-1 1zm1-3h1v1zm1 0zm0 1zm-1 0h1-1zm1 0h1-1zm1 1zm-1 0zm-1-1v1zm0 0zm0 1h1-1zm-1 0h1zm1-1h1v1zm2 1v1zm0 1h1-1Zm0 0zm1 1zm0 0zm-1 0h1-1Zm-1 0h1-1zm1 0zm-1 0zm0-1h2l-1 1zm-2-1h3l-1 2zm2-2h5l-3 4zm6-11h1-1zm0-1h1l-1 1zm1 1zm-1 0zm1 1h1-1zm0 0h1zm0 0zm-1 0zm0-1v1zm0 1zm-1 0h1zm1-1h1l-1 1zm2-3v1zm0 0zm0 1zm-1 0h1zm1 0h1v1zm0 0h1zm1 1zm-1 0zm-1-1h1l-1 1zm0 0zm0 1h1zm0 0zm0-1h2l-1 1zm2 2h1-1zm0-1v1zm0 1h1zm0 0zm1 1zm0-1v1zm0 1zm-1 0h1zm-1-1h1v1zm1 1zm-1 0zm1-1h1l-1 1zm0 4zm0 1h1zm0 0zm1 0zm0 1zm-1 0h1zm-1-1h1zm1 1zm-1 0zm1-1h1l-1 1zm1-3h1v1zm0 0h1zm1 0v1zm-1 0v1zm1 1h1l-1 1zm0 0zm0 0h1v1zm0 0v1zm-1 0v1zm-1 0h1v1zm1 0h1v1zm2 1v1zm0 0zm0 1zm-1 0h1zm1 0h1v1zm0 0h1zm1 1zm-1 0zm-1-1zm0 1h1zm0 0zm0-1h2l-1 1zm-2-1h3l-1 2zm-5 0v1zm0 0zm0 1zm-1 0h1zm1 0h1-1zm1 1zm-1 0zm-1-1h1l-1 1zm0 0zm0 1h1zm0 0zm0-1h1v1zm2-3h1l-1 1zm0 0zm0 0h1v1zm0 0v1zm1 1zm0 0v1zm-1 0h1v1zm-1 0h1l-1 1zm0 0h1-1zm1 0v1zm-1 0v1zm0 0h2l-1 1zm2 1h1-1zm1 1zm-1 0zm1 0zm0 1h1zm0 0zm-1-1zm0 1zm-1 0h1zm1-1h1l-1 1zm-2-1h2l-1 2zm1-3h6l-3 5zm7 8zm0 0zm-1 0h1zm1 1h1zm1 0v1zm-1 0v1zm-1 0zm0 0h1v1zm0 0v1zm0-1h2l-1 2zm2-2h1-1zm0-1v1zm0 1h1zm0 0zm1 1zm0-1v1zm0 1h1-1zm-1 0h1zm-1-1h1v1zm1 1zm-1 0zm1-1h1l-1 1zm1 2h1zm1 0zm0 0zm-1 0h1-1zm1 1h1l-1 1zm0 0zm0 0h1v1zm0 0v1zm-1 0zm0 0h1l-1 1zm-1 0h1v1zm1-1h1v2zm-2-1h3l-2 3zm3 5v1zm0 1zm-1 0h1-1zm1 1h1-1zm0 0zm0 0h1zm0 0zm-1 0zm0 0zm0 0h1-1zm-1 0h1zm1-1h1v1zm2-3v1zm0 0zm0 1h1-1zm-1 0h1zm1 0h1v1zm1 0zm0 1zm-1 0h1-1zm-1-1zm0 1h1zm0 0zm0-1h2l-1 1zm2 2h1-1zm0-1h1l-1 1zm1 1zm-1 0zm1 1zm0 0zm0 0h1-1zm0 0zm-2 0h1zm1 0zm0 0zm-1 0h1-1zm1-1h1l-1 1zm-2-1h2l-1 2zm-6 0v1zm0 1h1zm0 0zm1 1zm0 0zm-1 0h1zm-1 0h1zm1 0zm-1 0zm1-1h1l-1 1zm1-3h1zm1 1zm-1 0zm1 0zm0 1h1zm0 0zm-1-1zm0 1zm-1 0h1zm1-1h1v1zm2 1v1zm0 1zm-1 0h1zm1 1h1zm0 0h1zm1 0zm-1 0zm-1 0zm0 0h1zm0 0zm0-1h2l-1 1zm-2-1h3l-1 2zm2-2h5l-3 4zm-9-5h11l-5 9zm2 26v1zm0-1h1l-1 1zm-4 3h1-1zm1-2v1zm-1-1h1l-1 1zm-1-1h1v1zm0 1v1zm-1 1h1l-1 1zm1 2zm-2 0h1zm-3-4h1l-1 1zm-1 2v1zm0-1h1v1zm2 0v1zm0 1h1v1zm1 2h1-1zm-1 0zm-2 0h1zm-1 0h1-1zm-1 0zm-2 0h1zm-1 0h1-1zm2-2h1l-1 1zm-1-1h1v1zm14-2h1l-1 1zm-2 0h1v1zm-1 0h1l-1 1zm1-1zm-10 1v1zm1 0h1l-1 1zm1 0h1v1zm0-1zm-1-1h1-1zm9 0h1zm-8-3h1v1Zm2 0v1Zm1 0h1l-1 1Zm1 0h1v1Zm2 0v1Zm1 0h1l-1 1Zm-2-1h1l-1 1zm-3 0h1v1zm0-1v1zm4 0v1zm0 0zm-2-2h1zm-1-1v1zm0-1h2l-1 2zm-6 10h1-1zm0 0zm0 0h1zm0 0zm1 1zm0 0v1zm-1 0h1v1zm-1 0h1v1zm0 0h1zm1 0v1zm-1 0v1zm1-1h1l-1 2zm1-3h1v1zm0 0h1zm1 1zm-1 0zm1 0v1zm0 1h1zm0 0zm-1 0zm0-1v1zm0 1zm-1 0h1zm1-1h1v1zm2 2zm0 0zm-1 0h1zm1 1h1zm1 0v1zm-1 0v1zm-1 0zm0 0h1v1zm0 0v1zm0-1h2l-1 2zm-2-1h3l-1 3zm3 5zm0 1zm-1 0h1zm1 0h1v1zm1 1zm-1 0zm-1-1v1zm0 1h1zm0 0zm0-1h2l-1 1zm2-3zm0 0h1v1zm0 0v1zm1 1zm0 1zm-1 0h1zm-1-1h1zm1 1zm-1 0zm1-1h1l-1 1zm1 1h1zm1 1zm-1 0zm1 0v1zm0 1h1zm0 0zm-1-1v1zm0 1zm-1 0h1zm1-1h1v1zm-2-1h3l-2 2zm-6 0h1l-1 1zm0 0h1-1zm1 1zm-1 0zm1 0v1zm0 1h1zm0 0zm-1 0zm0-1v1zm0 1zm-1 0h1zm1-1h1l-1 1zm2-3v1zm0 0zm0 0v1zm-1 0h1v1zm1 1h1zm1 1zm-1 0zm-1-1h1l-1 1zm0 0zm0 1h1zm0 0zm0-1h2l-1 1zm2 1zm0 1h1zm0 0zm1 0v1zm0 1zm-1 0h1zm-1-1h1v1zm1 1zm-1 0zm1-1h1l-1 1zm-3-1h3l-1 2zm2-2h5l-2 4zm6-12h1v1zm0 0h1zm1 1zm-1 0zm1 1h1-1zm0 0h1zm0 0zm-1 0zm0-1v1zm0 1zm-1 0h1zm1-1h1v1zm2-3v1zm0 0zm0 0h1l-1 1zm-1 0h1v1zm1 1h1v1zm1 0zm0 0v1zm-1 0h1l-1 1zm-1 0h1l-1 1zm0 0zm0 0h1v1zm0 0v1zm0 0h2l-1 1zm2 1h1l-1 1zm0 0zm0 1h1zm0 0zm1 1zm0-1v1zm0 1h1-1zm-1 0h1Zm0-1v1zm0 1zm-1 0h1-1zm1-1h1l-1 1zm0 4zm0 0h1v1zm0 0v1zm1 1zm0 1h1-1Zm-1 0h1Zm0-1zm0 1Zm-1 0h1-1Zm1-1h1l-1 1Zm1-3h1zm1-1v1zm0 1zm-1 0h1-1zm1 1h1l-1 1zm0 0h1-1zm1 0v1zm-1 0v1zm-1 0h1l-1 1zm-1 0h1v1zm1-1h1v2zm2 2v1zm0 0zm0 0h1l-1 1Zm0 0v1zm0 1h1v1Zm1 0zm0 1Zm-1 0h1-1Zm-1-1h1-1zm1 1Zm-1 0Zm0-1h2l-1 1Zm-2-1h3l-1 2Zm-5 0v1zm0 0zm0 0v1zm-1 0h1v1zm1 1h1zm1 1Zm-1 0Zm-1-1h1l-1 1Zm0 0zm0 1h1Zm0 0Zm0-1h2l-1 1Zm2-3h1-1zm0-1v1zm0 1h1zm0 0zm1 1zm0 0v1zm-1 0h1v1zm-1 0h1v1zm0 0h1zm1 0v1zm-1 0v1zm1-1h1l-1 2zm1 2h1zm1 0v1zm-1 0v1zm1 1zm0 1h1Zm0 0Zm-1-1zm0 1Zm-1 0h1Zm1-1h1v1Zm-2-1h3l-2 2Zm1-3h6l-3 5Zm7 8zm0 0h1-1zm0 0zm1 1zm0 0v1zm-1 0h1l-1 1zm-1 0h1-1zm1 0v1zm-1 0v1zm0-1h2l-1 2zm2-3h1l-1 1zm0 0h1-1zm1 1zm-1 0zm1 1h1-1zm0-1v1zm0 1h1zm0 0zm-1-1v1zm0 1zm-1 0h1-1Zm1-1h1l-1 1zm2 2zm0 0zm0 0zm-1 0h1zm1 1h1l-1 1zm0 0h1-1zm1 0v1zm-1 0v1zm-1 0zm0 0h1v1zm0 0v1zm0-1h1v2zm-2-1h3l-2 3zm3 5zm0 1zm-1 0h1zm1 1h1-1zm0-1h1l-1 1zm1 1zm-1 0zm-1 0h1-1zm0-1v1zm0 1h1zm0 0zm0-1h1v1zm2-3h1l-1 1zm0 0zm0 0h1v1zm0 0v1zm1 1v1zm0 0zm0 1zm-1 0h1zm-1-1h1-1zm1 1zm-1 0zm0-1h2l-1 1zm2 1h1l-1 1zm0 0h1-1zm1 1zm-1 0zm1 1h1-1zm0-1v1zm0 1h1zm0 0zm-1 0zm0-1v1zm0 1zm-1 0h1zm1-1h1l-1 1zm-2-1h2l-1 2zm-6 0zm0 1h1zm0 0zm1 0v1zm0 1h1-1zm-1 0h1zm0-1v1zm0 1zm-1 0h1-1zm1-1h1l-1 1zm2-3zm0 0v1zm-1 0h1l-1 1zm1 1h1-1zm1 1zm-1 0zm-1-1zm0 1h1-1zm-1 0h1zm1-1h1v1zm2 1zm0 1h1-1zm0 0zm0 1h1zm1-1v1zm0 1zm-1 0h1-1zm-1-1h1l-1 1zm1 1zm-1 0zm0-1h2l-1 1zm-2-1h3l-1 2zm2-2h5l-3 4zm-8-5h10l-5 9zm16-28h43l-21 37Zm32 18h22l-11 19Zm29 17v1zm0-1h1v1zm-4 3h1zm1-2h1l-1 1zm-1-1h1v1zm0-1v1zm-1 1h1l-1 1zm-1 1h1v1zm1 2h1-1zm-1 0zm-4-4h1v1zm-1 2h1l-1 1zm1-1v1zm1 0h1l-1 1zm1 1v1zm0 2h1zm-1 0h1-1zm-1 0zm-2 0h1-1zm-1 0h1-1zm-2 0h1zm-1 0h1-1zm2-2h1l-1 1zm-1-1h1v1zm14-2h1l-1 1zm-1 0v1zm-2 0h1v1zm1-1h1-1zm-10 1h1l-1 1zm1 0h1l-1 1zm2 0v1zm-1-1h1-1zm-1-1h1-1zm10 0zm-8-3v1Zm1 0h1l-1 1Zm1 0h1v1Zm2 0v1Zm1 0h1l-1 1Zm1 0h1v1Zm-2-1h1v1zm-2 0v1zm-1-1h1l-1 1zm4 0h1l-1 1zm0 0zm-1-2zm-2-1h1v1zm0-1h3l-2 2zm-6 10h1-1zm0 0h1-1zm1 0zm-1 0zm1 1zm0 0h1v1zm0 0v1zm-2 0h1v1zm1 0zm0 0v1zm-1 0h1l-1 1zm1-1h1l-1 2zm2-3v1zm0 0zm0 1zm-1 0h1zm1 0h1l-1 1zm1 1zm-1 0zm-1 0h1-1zm0-1v1Zm0 1h1zm0 0zm0-1h1v1zm2 2zm0 0h1zm0 0zm1 1zm0 0v1zm-1 0h1v1zm-1 0h1-1zm1 0v1zm-1 0v1zm0-1h2l-1 2zm-2-1h3l-1 3zm3 5zm0 1h1zm0 0zm1 0v1zm0 1zm-1 0h1zm-1-1h1l-1 1zm1 1zm-1 0zm0-1h2l-1 1zm2-3h1zm1 0v1zm-1 0v1zm1 1zm0 1h1zm0 0zm-1-1zm0 1zm-1 0h1zm1-1h1v1zm2 1zm0 1zm-1 0h1zm1 0h1v1zm1 1zm-1 0zm-1-1v1zm0 1h1zm0 0zm0-1h2l-1 1zm-2-1h3l-1 2zm-6 0h1v1zm1 0zm0 1zm-1 0h1-1zm1 0h1l-1 1zm1 1zm-1 0zm-1 0zm0-1v1zm0 1h1-1zm-1 0h1zm1-1h1v1zm2-3v1zm0 0zm0 0h1l-1 1zm0 0v1zm1 1zm0 1zm-1 0h1-1zm-1-1h1l-1 1zm0 0h1-1zm1 1zm-1 0zm0-1h2l-1 1zm2 1h1-1zm1 1zm-1 0zm1 0v1zm0 1h1zm0 0zm-1-1v1zm0 1zm-1 0h1-1zm1-1h1l-1 1zm-2-1h2l-1 2zm1-2h6l-3 4zm7-12v1zm0 0zm0 1zm-1 0h1zm1 1h1zm1 0zm-1 0zm-1 0h1-1zm0-1v1zm0 1h1zm0 0zm0-1h2l-1 1zm2-3h1l-1 1zm0 0zm0 0h1v1zm0 0v1zm1 1v1zm0 0zm0 0v1zm-1 0h1v1zm-1 0h1v1zm0 0h1zm1 0v1zm-1 0v1zm1 0h1l-1 1zm1 1h1v1zm0 0h1zm1 1zm-1 0zm1 1h1-1zm0-1v1zm0 1h1zm0 0zm-1-1v1zm0 1zm-1 0h1zm1-1h1v1zm0 4h1zm1 0v1zm-1 0v1zm1 1zm0 1h1Zm0 0Zm-1-1zm0 1Zm-1 0h1Zm1-1h1v1Zm2-3zm0-1v1zm0 1zm-1 0h1zm1 1h1v1zm0 0h1zm1 0v1zm-1 0v1zm-1 0h1v1zm0 0v1zm0-1h2l-1 2zm2 2h1l-1 1zm0 0zm0 0h1v1zm0 0v1zm1 1v1Zm0 0zm0 1h1-1Zm-1 0h1Zm-1-1h1zm1 1Zm-1 0Zm1-1h1l-1 1Zm-2-1h2l-1 2Zm-6 0h1l-1 1zm0 0zm0 0h1v1zm0 0v1zm1 1zm0 1Zm-1 0h1Zm-1-1h1l-1 1Zm0 0h1-1zm1 1Zm-1 0Zm0-1h2l-1 1Zm2-3h1zm0-1h1v1zm1 1zm-1 0zm1 1zm0 0h1v1zm0 0v1zm-1 0v1zm0 0zm0 0v1zm-1 0h1v1zm1-1h1v2zm2 2zm0 0v1zm-1 0h1v1zm1 1h1zm1 1Zm-1 0Zm-1-1zm0 1h1Zm0 0Zm0-1h2l-1 1Zm-2-1h3l-1 2Zm2-3h5l-3 5Zm6 8zm0 0h1zm0 0zm1 1zm0 0h1l-1 1zm-1 0h1v1zm-1 0h1zm1 0v1zm-1 0v1zm1-1h1l-1 2zm1-3h1v1zm1 0zm0 1zm-1 0h1-1zm1 1h1-1zm0-1v1zm0 1h1zm0 0zm-1-1v1zm0 1h1-1zm-1 0h1zm1-1h1v1zm2 2zm0 0zm0 0h1-1zm-1 0h1zm1 1h1v1zm1 0zm0 0v1zm-1 0h1l-1 1zm-1 0zm0 0h1v1zm0 0v1zm0-1h2l-1 2zm-2-1h3l-1 3zm3 5zm0 1h1-1zm-1 0h1zm1 1h1zm1-1v1zm0 1zm-1 0h1-1zm-1 0h1-1zm0-1v1zm0 1h1zm0 0zm0-1h2l-1 1zm2-3h1l-1 1zm0 0h1-1zm1 0v1zm-1 0v1zm1 1v1zm0 0zm0 1h1-1zm0 0zm-1-1zm0 1zm-1 0h1-1zm1-1h1l-1 1zm1 1h1v1zm1 0zm0 1zm-1 0h1-1zm1 1h1-1zm0-1h1l-1 1zm1 1zm-1 0zm-1 0zm0-1v1zm0 1h1-1zm0 0zm0-1h1v1zm-2-1h3l-2 2zm-6 0h1zm1 1zm-1 0zm1 0v1zm0 1h1zm0 0zm-1-1v1zm0 1zm-1 0h1zm1-1h1v1zm2-3zm0 0v1zm-1 0h1v1zm1 1h1zm1 1zm-1 0zm-1-1zm0 1h1zm0 0zm0-1h2l-1 1zm2 1zm0 1h1zm0 0zm1 1zm0-1v1zm0 1h1-1zm-1 0h1zm-1-1h1v1zm1 1zm-1 0zm1-1h1l-1 1zm-2-1h2l-1 2zm1-2h5l-2 4zm-8-5h11l-6 9zm1-11h1-1zm1-2v1zm-5 3h1zm1-1h1-1zm-1-2h1v1zm0-1v1zm-1 1h1l-1 1zm-1 2h1zm1 1h1-1zm-1 0zm-4-4h1v1zm-1 3h1-1zm1-2v1zm1 0h1l-1 1zm1 2zm0 1h1zm-1 0h1-1zm-1 0zm-2 0h1zm-1 0h1-1zm-1 0zm-2 0h1zm2-1h1zm0-2v1zm13-2h1l-1 1zm-1 0h1l-1 1zm-2 0h1v1zm1-1h1-1zm-10 1h1l-1 1zm1 0h1v1zm2 0v1zm-1-1h1-1zm-1-1h1zm10 0h1-1zm-8-3v1zm1 0h1l-1 1zm1 0h1v1zm2 0v1zm1 0h1l-1 1zm1 0h1v1zm-2-1h1v1zm-2 0v1zm-1-1h1l-1 1zm4 0h1l-1 1zm0 0h1-1zm-1-2zm-1-1v1zm-1-1h3l-2 2zm-6 10h1zm0 0h1zm1 0zm-1 0zm1 1zm0 0h1v1zm0 0v1zm-1 0v1zm0 0zm0 0v1zm-1 0h1v1zm1-1h1v2zm2-2zm0-1v1zm0 1zm-1 0h1zm1 0h1v1zm1 1zm-1 0zm-1 0h1-1zm0-1v1zm0 1h1zm0 0zm0-1h2l-1 1zm2 2zm0 0h1zm0 0zm1 1zm0 0v1zm-1 0h1v1zm-1 0h1zm1 0v1zm-1 0v1zm1-1h1l-1 2zm-2-1h2l-1 3zm2 5v1zm0 1h1zm0 0zm1 1zm0 0zm-1 0h1zm-1 0h1zm1 0zm-1 0zm1-1h1l-1 1zm1-3h1zm1 1zm-1 0zm1 0zm0 1h1zm0 0zm-1-1zm0 1zm-1 0h1zm1-1h1v1zm2 1v1zm0 1h1-1zm-1 0h1zm2 1zm0 0zm-1 0h1-1zm-1 0zm0 0h1zm0 0zm0-1h2l-1 1zm-2-1h3l-1 2zm-5 1zm0-1v1zm0 1zm-1 0h1zm1 1h1zm1 0zm-1 0zm-1 0h1-1zm0 0zm0 0h1zm0 0zm0-1h2l-1 1zm2-3h1l-1 1zm0 0zm0 1h1zm0 0zm1 0zm0 1zm-1 0h1zm-1-1h1v1zm0 0h1zm1 1zm-1 0zm1-1h1l-1 1zm1 1h1v1zm1 1zm-1 0zm1 1zm0 0h1zm0 0zm-1 0zm0 0zm-1 0h1zm1-1h1v1zm-2-1h3l-2 2zm1-2h6l-3 4zm7-11zm0-1v1zm0 1h1-1zm-1 0h1zm1 1h1zm1 0zm-1 0h1-1zm-1 0h1-1zm0-1v1zm0 1h1zm0 0zm0-1h2l-1 1zm2-3h1l-1 1zm0 0zm0 1h1zm0 0zm1 0v1zm0 0zm0 1h1-1zm-1 0h1zm-1-1h1v1zm1 0zm0 1zm-1 0h1-1zm1-1h1l-1 1zm1 2h1zm1-1v1zm0 1zm-1 0h1-1zm1 1h1-1zm0-1h1l-1 1zm1 1zm-1 0zm-1-1v1zm0 1h1-1zm-1 0h1zm1-1h1v1zm1 4zm0 1zm-1 0h1-1zm1 0h1-1zm1 1zm-1 0zm-1-1zm0 1h1-1zm-1 0h1zm1-1h1v1zm2-3v1zm0 0zm0 0h1l-1 1zm0 0v1zm0 1h1v1zm1 0zm0 0v1zm-1 0h1l-1 1zm0 0v1zm-1 0v1zm0 0h2l-1 1zm2 1h1l-1 1zm0 0h1-1zm1 1zm-1 0zm1 0h1l-1 1zm0 0zm0 1h1zm0 0zm-1-1zm0 1zm-1 0h1-1zm1-1h1l-1 1zm-2-1h2l-1 2zm-6 0h1l-1 1zm0 0zm0 1h1zm0 0zm1 0zm0 1zm-1 0h1zm-1-1h1v1zm0 0h1zm1 1zm-1 0zm1-1h1l-1 1zm1-3h1v1zm0 0h1zm1 0v1zm-1 0v1zm1 1zm0 0h1v1zm0 0v1zm-1 0v1zm0 0zm0 0v1zm-1 0h1v1zm1 0h1v1zm2 1zm0 1h1-1zm-1 0h1zm2 0zm0 1zm-1 0h1-1zm-1-1zm0 1h1zm0 0zm0-1h2l-1 1zm-2-1h3l-1 2zm2-3h5l-3 5zm6 8h1-1zm1 0zm-1 0zm1 1zm0 0h1v1zm0 0v1zm-1 0zm0 0v1zm-1 0h1l-1 1zm1-1h1l-1 2zm2-2zm0-1v1zm0 1zm-1 0h1zm1 1h1-1zm0-1h1l-1 1zm1 1zm-1 0zm-1-1v1zm0 1h1zm0 0zm0-1h1v1zm2 2h1-1zm0 0zm0 0h1zm0 0zm1 1v1zm0 0zm0 0v1zm-1 0h1v1zm-1 0h1-1zm1 0v1zm-1 0v1zm0-1h2l-1 2zm-2-1h3l-1 3zm3 5v1zm0 1h1zm0 0zm1 1zm0 0zm0 0zm-1 0h1zm-1 0h1-1zm0 0h1-1zm1 0zm-1 0zm0-1h2l-1 1zm2-3h1v1zm0 0h1zm1 1zm-1 0zm1 0h1l-1 1zm0 0zm0 1h1zm0 0zm-1-1zm0 1zm-1 0h1zm1-1h1v1zm2 2zm0-1v1zm0 1zm-1 0h1zm1 1h1zm0 0h1zm1 0zm-1 0zm-1 0h1-1zm0 0zm0 0h1zm0 0zm0-1h2l-1 1zm-2-1h3l-1 2zm-5 0v1zm0 1zm-1 0h1-1zm1 1h1-1zm1 0zm-1 0zm-1 0zm0 0h1-1zm-1 0h1zm1-1h1v1zm2-3zm0 1h1-1zm0 0zm1 0zm0 1zm-1 0h1-1zm-1-1h1-1zm1 1zm-1 0zm0-1h2l-1 1zm2 1h1l-1 1zm1 1zm-1 0zm1 1h1-1zm0 0zm0 0h1zm0 0zm-1 0zm0 0zm-1 0h1-1zm1-1h1l-1 1zm-2-1h2l-1 2zm1-2h6l-3 4zm-8-5h11l-6 9zm1 26h1l-1 1zm1-1v1zm-4 3zm0-2h1v1zm0-1v1zm-1-1h1l-1 1zm-1 1h1v1zm0 1v1zm0 2h1zm-1 0h1-1zm-4-4h1v1zm-1 2h1l-1 1zm1-1v1zm1 0h1l-1 1zm1 1h1l-1 1zm1 2zm-2 0h1-1zm-1 0zm-2 0h1zm-1 0h1-1zm-1 0zm-2 0h1zm2-2h1v1zm0-1v1zm13-2h1v1zm-1 0h1l-1 1zm-1 0v1zm0-1h1zm-10 1h1l-1 1zm1 0h1v1zm2 0v1zm-1-1h1-1zm-1-1h1zm10 0h1-1zm-8-3v1Zm1 0h1l-1 1Zm2 0v1Zm1 0h1l-1 1Zm1 0h1v1Zm2 0v1Zm-2-1v1zm-3 0h1l-1 1zm-1-1h1l-1 1zm4 0h1v1zm0 0h1zm-1-2h1-1zm-1-1v1zm-1-1h3l-2 2zm-6 10h1zm1 0zm0 0zm-1 0h1-1zm1 1zm0 0h1v1zm0 0v1zm-1 0v1zm0 0zm0 0h1l-1 1zm-1 0h1v1zm1-1h1v2zm2-3v1zm0 0zm0 1h1-1zm-1 0h1zm2 0v1zm0 1zm-1 0h1-1zm-1 0h1-1zm0-1v1zm0 1h1zm0 0zm0-1h2l-1 1zm2 2h1-1zm1 0zm-1 0zm1 1zm0 0h1l-1 1zm0 0v1zm-1 0zm0 0v1zm-1 0h1l-1 1zm1-1h1l-1 2zm-2-1h2l-1 3zm2 5h1-1zm1 1zm-1 0zm1 0v1zm0 1h1-1zm0 0zm-1-1v1zm0 1zm-1 0h1-1zm1-1h1l-1 1zm2-3zm0 0v1zm-1 0h1l-1 1zm1 1h1-1zm1 1zm-1 0zm-1-1zm0 1h1-1zm0 0zm0-1h1v1zm2 1zm0 1h1zm0 0zm1 0v1zm0 1zm-1 0h1zm-1-1h1l-1 1zm1 1zm-1 0zm0-1h2l-1 1zm-2-1h3l-1 2zm-5 0v1zm0 0zm0 1h1-1zm-1 0h1zm2 0v1zm0 1zm-1 0h1-1zm-1 0h1-1zm0-1v1zm0 1h1zm0 0zm0-1h2l-1 1zm2-3h1l-1 1zm0 0zm0 0h1v1zm0 0v1zm1 1zm0 1h1-1zm-1 0h1zm-1-1h1v1zm1 0zm0 1zm-1 0h1-1zm1-1h1l-1 1zm2 1zm0 1zm-1 0h1-1zm1 0v1zm0 1h1zm0 0zm-1-1v1zm0 1h1-1zm-1 0h1zm1-1h1v1zm-2-1h3l-2 2zm1-2h6l-3 4zm7-12h1l-1 1zm0 0zm0 1h1zm0 0zm1 1zm0 0zm-1 0h1zm-1 0h1-1zm0-1h1l-1 1zm1 1zm-1 0zm0-1h2l-1 1zm2-3h1l-1 1zm0 0h1-1zm1 0v1zm-1 0v1zm1 1h1l-1 1zm0 0zm0 0h1v1zm0 0v1zm-1 0v1zm0 0zm0 0v1zm-1 0h1v1zm1 0h1l-1 1zm2 1v1zm0 0zm0 1zm-1 0h1zm1 1h1zm0-1h1v1zm1 1zm-1 0zm-1-1v1zm0 1h1zm0 0Zm0-1h2l-1 1zm1 4zm0 0v1zm-1 0h1v1zm1 1h1zm1 1Zm-1 0Zm-1-1zm0 1h1Zm0 0Zm0-1h2l-1 1Zm2-3h1-1zm0-1v1zm0 1h1zm0 0zm1 1v1zm0 0zm0 0v1zm-1 0h1v1zm0 0v1zm-1 0v1zm1-1h1l-1 2zm1 2h1v1zm0 0h1zm1 0v1zm-1 0v1zm1 1h1l-1 1Zm0 0zm0 1h1Zm0 0Zm-1-1zm0 1Zm-1 0h1Zm1-1h1v1Zm-2-1h3l-2 2Zm-6 0h1l-1 1zm0 0h1-1zm1 0v1zm-1 0v1zm1 1zm0 1h1-1Zm0 0Zm-2-1h1v1Zm1 0zm0 1Zm-1 0h1-1Zm1-1h1l-1 1Zm1-3h1zm1-1v1zm0 1zm-1 0h1-1zm1 1h1-1zm1 0v1zm-1 0v1zm-1 0v1zm0 0zm0 0h1l-1 1zm0 0v1zm0-1h1v2zm2 2zm0 0h1v1zm0 0v1zm1 1zm0 1Zm-1 0h1Zm-1-1h1-1zm1 1Zm-1 0Zm0-1h2l-1 1Zm-2-1h3l-1 2Zm2-3h5l-3 5Zm6 8h1zm1 0zm-1 0zm1 1zm0 0h1v1zm0 0v1zm-1 0zm0 0v1zm-1 0h1v1zm1-1h1v2zm2-3v1zm0 0zm0 1zm-1 0h1zm1 1h1zm0-1h1v1zm1 1zm-1 0zm-1-1v1zm0 1h1zm0 0zm0-1h2l-1 1zm2 2h1-1zm0 0zm0 0h1zm0 0zm1 1v1zm0 0zm0 0v1zm-1 0h1v1zm-1 0h1zm1 0v1zm-1 0v1zm1-1h1l-1 2zm-2-1h2l-1 3zm2 5zm0 1h1zm0 0zm1 1zm0-1v1zm0 1zm-1 0h1zm-1 0h1zm0-1h1v1zm1 1zm-1 0zm1-1h1l-1 1zm1-3h1v1zm0 0h1zm1 0v1zm-1 0v1zm1 1h1l-1 1zm0 0zm0 1h1zm0 0zm-1-1zm0 1zm-1 0h1zm1-1h1v1zm2 1v1zm0 0zm0 1h1-1zm-1 0h1zm1 1h1zm1-1v1zm0 1zm-1 0h1-1zm-1 0h1-1zm0-1v1zm0 1h1zm0 0zm0-1h2l-1 1zm-2-1h3l-1 2zm-5 0zm0 1zm-1 0h1zm1 0h1v1zm1 1zm-1 0zm-1-1v1zm0 1h1zm0 0zm0-1h2l-1 1zm2-3zm0 0h1v1zm0 0v1zm1 1zm0 1zm-1 0h1zm-1-1h1zm1 1zm-1 0zm1-1h1l-1 1zm1 1h1zm1 1zm-1 0zm1 1h1-1zm0-1v1zm0 1h1zm0 0zm-1-1v1zm0 1zm-1 0h1zm1-1h1v1zm-2-1h3l-2 2zm1-2h6l-3 4zm-8-5h11l-6 9zM49 51h21L60 70zm28 17h1-1zm1-1zm-4 2v1zm0-1h1zm0-1zm-1-2h1l-1 1zm-1 2h1zm0 1zm0 1h1v1zm-1 0h1l-1 1zm-4-4h1v1zm-1 3h1-1zm1-1zm1 0h1-1zm1 1h1-1zm1 1v1zm-2 0h1l-1 1zm-1 0v1zm-2 0h1v1zm-1 0h1l-1 1zm-1 0v1zm-2 0h1v1zm2-1h1zm0-1zm13-3h1v1zm-1 0h1l-1 1zm-1 0v1zm0-1h1v1zm-10 1h1l-1 1zm1 0h1v1zm2 0v1zm-1-1h1l-1 1zm-1-1h1zm10 0h1-1zm-8-2zm1 0h1-1zm2 0zm1 0h1-1zm1 0h1zm2 0zm-2-2v1zm-3 0h1l-1 1zm-1-1h1l-1 1zm4 0h1v1zm0 0h1zm-1-2h1-1zm-1 0zm-1-2h3l-2 2zm-6 10h1v1zm1 0zm0 0v1zm-1 0h1l-1 1zm1 1zm0 1h1zm0 0zm-1-1v1zm0 0zm0 1h1-1zm-1 0h1zm1-1h1v1zm2-3zm0-1v1zm0 1h1-1zm-1 0h1zm2 1zm0 0zm-1 0h1-1zm-1 0h1-1zm0 0zm0 0h1zm0 0zm0-1h2l-1 1zm2 2h1-1zm1 0v1zm-1 0v1zm1 1zm0 1h1-1zm0 0zm-1-1zm0 1zm-1 0h1-1zm1-1h1l-1 1zm-2-2h2l-1 3zm2 6h1-1zm1 0zm-1 0zm1 1zm0 0h1l-1 1zm0 0v1zm-1 0zm0 0v1zm-1 0h1l-1 1zm1-1h1l-1 2zm2-3zm0 1zm-1 0h1-1zm1 0h1l-1 1zm1 1zm-1 0zm-1-1v1zm0 1h1-1zm0 0zm0-1h1v1zm2 2zm0 0h1zm0 0zm1 1zm0 0v1zm-1 0h1v1zm-1 0h1-1zm1 0v1zm-1 0v1zm0-1h2l-1 2zm-2-1h3l-1 3zm-5 1zm0 0zm0 0h1-1zm-1 0h1zm2 1zm0 0v1zm-1 0h1l-1 1zm-1 0h1l-1 1zm0 0zm0 0h1v1zm0 0v1zm0-1h2l-1 2zm2-3h1l-1 1zm0 0zm0 1h1zm0 0zm1 0v1zm0 1h1-1zm-1 0h1zm-1 0h1zm1-1v1zm0 1zm-1 0h1-1zm1-1h1l-1 1zm2 2zm0 0zm-1 0h1-1zm1 1zm0 0h1v1zm0 0v1zm-1 0zm0 0h1l-1 1zm-1 0h1v1zm1-1h1v2zm-2-1h3l-2 3zm1-2h6l-3 5zm7-11h1-1zm0-1v1zm0 1h1zm0 0zm1 1zm0 0zm-1 0h1zm-1 0h1-1zm0 0h1-1zm1 0zm-1 0zm0-1h2l-1 1zm2-3h1l-1 1zm0 0h1-1zm1 1zm-1 0zm1 1h1-1zm0-1v1zm0 1h1zm0 0zm-1 0zm0-1v1zm0 1zm-1 0h1zm1-1h1l-1 1zm2 2zm0-1v1zm0 1zm-1 0h1zm1 1h1zm0 0h1zm1 0zm-1 0zm-1 0zm0 0h1zm0 0zm0-1h2l-1 1zm1 4zm0 1zm-1 0h1zm1 0h1v1zm1 1zm-1 0zm-1-1v1zm0 1h1zm0 0Zm0-1h2l-1 1zm2-3h1l-1 1zm0 0zm0 0h1v1zm0 0v1zm1 1v1zm0 0zm0 0v1zm-1 0h1v1zm0 0v1zm-1 0v1zm1 0h1l-1 1zm1 1h1v1zm0 0h1zm1 1zm-1 0zm1 1h1-1zm0-1v1zm0 1h1zm0 0Zm-1-1v1zm0 1zm-1 0h1zm1-1h1v1zm-2-1h3l-2 2zm-6 0h1l-1 1zm0 0h1-1zm1 1zm-1 0zm1 0v1zm0 1h1-1zm0 0zm-2 0h1zm1-1v1zm0 1zm-1 0h1-1zm1-1h1l-1 1zm1-3h1v1zm1 0zm0 0v1zm-1 0h1l-1 1zm1 1h1-1zm1 0v1zm-1 0v1zm-1 0v1zm0 0zm0 0h1l-1 1zm0 0v1zm0 0h1v1zm2 1zm0 1h1zm0 0zm1 0v1zm0 1zm-1 0h1Zm-1-1h1l-1 1zm1 1zm-1 0zm0-1h2l-1 1zm-2-1h3l-1 2zm2-3h5l-3 5zm6 8h1zm1 0v1zm-1 0v1zm1 1zm0 1h1zm0 0zm-1-1zm0 1zm-1 0h1zm1-1h1v1zm2-3zm0-1v1zm0 1zm-1 0h1zm1 1h1zm0 0h1zm1 0zm-1 0zm-1 0zm0 0h1zm0 0zm0-1h2l-1 1zm2 2h1l-1 1zm0 0zm0 0h1v1zm0 0v1zm1 1v1zm0 0zm0 1zm-1 0h1zm-1-1h1zm1 1zm-1 0zm1-1h1l-1 1zm-2-2h2l-1 3zm2 6zm0 0h1zm0 0zm1 1v1zm0 0zm0 0v1zm-1 0h1v1zm-1 0h1v1zm0 0h1zm1 0v1zm-1 0v1zm1-1h1l-1 2zm1-3h1v1zm0 0h1zm1 1zm-1 0zm1 1h1-1zm0-1v1zm0 1h1zm0 0zm-1-1v1zm0 1zm-1 0h1zm1-1h1v1zm2 2zm0 0zm0 0h1-1zm-1 0h1zm1 1h1v1zm1 0zm0 0v1zm-1 0h1l-1 1zm-1 0h1l-1 1zm0 0zm0 0h1v1zm0 0v1zm0-1h2l-1 2zm-2-1h3l-1 3zm-5 1zm0 0zm-1 0h1zm1 1h1zm1 0v1zm-1 0v1zm-1 0zm0 0h1v1zm0 0v1zm0-1h2l-1 2zm2-3zm0 1h1zm0 0zm1 0v1zm0 1zm-1 0h1zm-1-1h1v1zm1 1zm-1 0zm1-1h1l-1 1zm1 2h1zm1 0zm-1 0zm1 1h1l-1 1zm0 0zm0 0h1v1zm0 0v1zm-1 0zm0 0v1zm-1 0h1v1zm1-1h1v2zm-2-1h3l-2 3zm1-2h6l-3 5zm-8-5h11l-6 10zm1-11h1l-1 1zm1-1zm-4 2v1zm0-1h1v1zm0-1zm-1-1h1-1zm-1 1h1zm0 1v1zm0 1h1v1zm-1 0h1l-1 1zm-3-3zm-2 2h1v1zm1-1h1-1zm1 0h1zm1 1h1l-1 1zm1 1v1zm-2 0h1v1zm-1 0h1l-1 1zm-1 0v1zm-2 0h1l-1 1zm-1 0h1l-1 1zm-2 0h1v1zm3-1v1zm-1-1h1-1zm13-3h1v1zm-1 0h1l-1 1zm-1 0v1zm0-1h1v1zm-10 1h1l-1 1zm2 0v1zm1 0h1l-1 1zm-1-1h1v1zm0-1v1zm9 0h1l-1 1zm-8-2h1-1zm1 0h1zm2 0zm1 0h1-1zm1 0h1zm2 0zm-2-1zm-3 0h1-1zm-1-2h1v1zm4 0h1v1zm1 0zm-2-2h1l-1 1zm-1 0zm-1-2h3l-1 3zm-5 10v1zm0 0zm0 1zm-1 0h1zm1 0h1-1zm1 1zm-1 0zm-1-1h1l-1 1zm0 0zm0 1h1zm0 0zm0-1h1v1zm2-3h1l-1 1zm0 0zm0 0h1v1zm0 0v1zm1 1zm0 0v1zm-1 0h1v1zm-1 0h1l-1 1zm0 0h1-1zm1 0v1zm-1 0v1zm0 0h2l-1 1zm2 1h1zm1 1zm-1 0zm1 0zm0 1h1zm0 0zm-1-1zm0 1zm-1 0h1zm1-1h1v1zm-2-1h3l-2 2zm2 5h1zm1 0v1zm-1 0v1zm1 1zm0 1h1zm0 0zm-1-1zm0 1zm-1 0h1zm1-1h1v1zm2-4v1zm0 1zm-1 0h1zm1 1h1zm1 0zm-1 0zm-1 0zm0 0h1zm0 0zm0-1h2l-1 1zm2 2zm0 0h1v1zm0 0v1zm1 1zm0 1zm-1 0h1zm-1-1h1zm1 1zm-1 0zm1-1h1l-1 1zm-2-2h2l-1 3zm-6 1v1zm0 0zm0 0h1l-1 1zm0 0v1zm1 1zm0 1zm-1 0h1-1zm-1-1h1l-1 1zm0 0h1-1zm1 1zm-1 0zm0-1h2l-1 1zm2-3h1-1zm0-1h1l-1 1zm1 1zm-1 0zm1 1zm0 0h1zm0 0zm-2 0h1zm1 0zm0 0zm-1 0h1-1zm1-1h1l-1 1zm2 2zm0 0v1zm-1 0h1v1zm1 1h1-1zm1 1zm-1 0zm-1-1zm0 1h1zm0 0zm0-1h1v1zm-2-2h3l-2 3zm1-2h6l-3 5zm7-11h1-1zm0 0zm0 0h1zm0 0zm1 1v1zm0 0v1zm-1 0h1v1zm-1 0h1v1zm0 0h1zm1 0v1zm-1 0v1zm1-1h1l-1 2zm1-3h1v1zm0 0h1zm1 1zm-1 0zm1 1h1-1zm0-1v1zm0 1h1zm0 0zm-1 0zm0-1v1zm0 1zm-1 0h1zm1-1h1v1zm2 2zm0 0zm0 0h1-1zm-1 0h1zm1 1h1v1zm1 0zm0 0v1zm-1 0h1l-1 1zm-1 0zm0 0h1v1zm0 0v1zm0-1h2l-1 2zm1 4v1zm0 1h1-1zm-1 0h1zm2 0v1zm0 1zm-1 0h1-1zm-1-1v1zm0 1h1zm0 0zm0-1h2l-1 1zm2-3h1l-1 1zm0 0zm0 0h1v1zm0 0v1zm1 1v1zm0 0zm0 1h1-1zm-1 0h1zm0 0zm-1 0h1-1zm1-1h1l-1 1zm1 2h1zm1-1v1zm0 1zm-1 0h1-1zm1 1h1-1zm0-1v1zm0 1h1zm0 0zm-1-1v1zm0 1h1-1zm-1 0h1zm1-1h1v1zm-2-1h3l-2 2zm-6 1h1zm0-1h1v1zm1 1zm-1 0zm1 0v1zm0 1h1zm0 0zm-1 0zm0-1v1zm0 1zm-1 0h1zm1-1h1v1zm2-3v1zm0 0zm0 0v1zm-1 0h1v1zm1 1h1zm1 1zm-1 0zm-1-1h1l-1 1zm0 0zm0 1h1zm0 0zm0-1h2l-1 1zm2 1v1zm0 1h1zm0 0zm1 0v1zm0 1zm-1 0h1zm-1-1h1v1zm1 1zm-1 0zm1-1h1l-1 1zm-2-1h2l-1 2zm1-2h5l-2 4zm7 7zm0 1zm-1 0h1-1zm1 0zm0 1h1zm0 0zm-1-1zm0 1h1-1zm-1 0h1zm1-1h1v1zm2-3v1zm0 0zm0 0h1l-1 1zm-1 0h1v1zm1 1h1v1zm1 0zm0 0v1zm-1 0h1l-1 1zm-1 0zm0 0h1v1zm0 0v1zm0 0h2l-1 1zm2 1h1l-1 1zm0 0h1-1zm1 1zm-1 0zm1 0v1zm0 0zm0 1h1-1zm0 0zm-1-1zm0 1zm-1 0h1-1zm1-1h1l-1 1zm-2-1h2l-1 2zm2 5h1-1zm1 0v1zm-1 0v1zm1 1v1zm0 0zm0 1h1-1zm0 0zm-2-1h1v1zm1 0zm0 1zm-1 0h1-1zm1-1h1l-1 1zm1-3h1zm1-1v1zm0 1zm-1 0h1-1zm1 1h1-1zm0 0h1-1zm1 0zm-1 0zm-1 0zm0 0h1-1zm0 0zm0-1h1v1zm2 2h1l-1 1zm0 0zm0 0h1v1zm0 0v1zm1 1v1zm0 0zm0 1zm-1 0h1zm-1-1h1l-1 1zm0 0h1-1zm1 1zm-1 0zm0-1h2l-1 1zm-2-2h3l-1 3zm-5 1zm0 0h1l-1 1zm-1 0h1v1zm2 1zm0 1zm-1 0h1-1zm-1-1zm0 1h1zm0 0zm0-1h2l-1 1zm2-4v1zm0 1h1zm0 0zm1 1zm0 0h1-1zm-1 0h1zm0 0zm0 0zm-1 0h1-1zm1-1h1l-1 1zm2 2zm0 0v1zm-1 0h1l-1 1zm1 1h1l-1 1zm0 0zm0 1h1zm0 0zm-1-1zm0 1h1-1zm-1 0h1zm1-1h1v1zm-2-2h3l-2 3zm1-2h6l-3 5zm-8-5h11l-5 10zm1 27h1zm1-1h1-1zm-4 2h1l-1 1zm1-1zm-1-1h1-1zm-1-2h1l-1 1zm-1 2h1zm0 1zm0 1h1v1zm-1 0h1l-1 1zm-3-4v1zm-2 3h1zm1-1h1-1zm1 0h1zm1 1h1-1zm1 1v1zm-2 0h1v1zm-1 0h1l-1 1zm-1 0v1zm-2 0h1v1zm-1 0h1l-1 1zm-1 0v1zm2-1zm-1-1h1-1zm14-3v1zm-2 0h1l-1 1zm-1 0h1l-1 1zm1-1v1zm-11 1h1v1zm2 0v1zm1 0h1l-1 1zm-1-1h1v1zm0-1zm9 0h1-1zm-8-2h1-1zm1 0h1zm2 0zm1 0h1-1zm1 0h1zm2 0h1-1zm-2-2v1zm-3 0h1l-1 1zm-1-1h1v1zm4 0h1v1zm1 0zm-2-2h1-1zm-1 0zm-1-2h3l-1 2zm-5 10v1zm0 0zm0 0v1zm-1 0h1v1zm1 1h1zm1 1zm-1 0zm-1-1h1l-1 1zm0 0zm0 1h1zm0 0zm0-1h2l-1 1zm2-3h1-1zm0-1v1zm0 1h1zm0 0zm1 1zm0 0h1-1zm-1 0h1zm-1 0h1zm0 0h1zm1 0zm-1 0zm1-1h1l-1 1zm2 2zm0 0v1zm-1 0h1l-1 1zm1 1zm0 1h1zm0 0zm-1-1zm0 1h1-1zm-1 0h1zm1-1h1v1zm-2-2h3l-2 3zm3 6zm0 0zm-1 0h1-1zm1 1zm0 0h1v1zm0 0v1zm-1 0zm0 0h1l-1 1zm-1 0h1v1zm1-1h1v2zm2-3zm0 1h1-1zm-1 0h1zm2 0v1zm0 1zm-1 0h1-1zm-1-1v1zm0 1h1zm0 0zm0-1h2l-1 1zm2 2h1-1zm1 0zm-1 0zm1 1zm0 0h1l-1 1zm0 0v1zm-1 0zm0 0v1zm-1 0h1l-1 1zm1-1h1l-1 2zm-2-1h2l-1 3zm-6 1h1-1zm0 0zm0 0h1zm0 0zm1 1zm0 0v1zm-1 0h1v1zm-1 0h1v1zm0 0h1zm1 0v1zm-1 0v1zm1-1h1l-1 2zm1-3h1v1zm0 0h1zm1 1zm-1 0zm1 0v1zm0 1h1zm0 0zm-1 0zm0-1v1zm0 1zm-1 0h1zm1-1h1v1zm2 2zm0 0zm-1 0h1zm1 1h1zm1 0v1zm-1 0v1zm-1 0zm0 0h1v1zm0 0v1zm0-1h2l-1 2zm-2-1h3l-1 3zm2-2h5l-3 5zm6-11h1-1zm0-1h1l-1 1zm1 1zm-1 0zm1 1zm0 0h1-1zm0 0zm-2 0h1zm1 0zm0 0zm-1 0h1-1zm1-1h1l-1 1zm1-3h1v1zm1 0zm0 1zm-1 0h1-1zm1 1h1-1zm0-1h1l-1 1zm1 1zm-1 0zm-1 0zm0-1v1zm0 1h1-1zm0 0zm0-1h1v1zm2 2zm0-1v1zm0 1h1-1zm0 0zm0 1h1zm1 0zm0 0zm-1 0h1-1zm-1 0h1-1zm1 0zm-1 0zm0-1h2l-1 1zm1 4zm0 1h1-1zm0 0zm1 0v1zm0 1zm-1 0h1-1zm-1-1h1l-1 1zm1 1zm-1 0zm0-1h2l-1 1zm2-3h1l-1 1zm0 0h1-1zm1 0v1zm-1 0v1zm1 1h1l-1 1zm0 0zm0 0h1v1zm0 0v1zm-1 0v1zm-1 0h1l-1 1zm1 0h1l-1 1zm2 1v1zm0 0zm0 1zm-1 0h1zm1 1h1-1zm0-1h1l-1 1zm1 1zm-1 0zm-1-1v1zm0 1h1zm0 0zm0-1h1v1zm-2-1h3l-2 2zm-6 0h1v1zm1 0zm0 1zm-1 0h1-1zm1 0v1zm0 1h1zm0 0zm-1 0zm0-1v1zm0 1h1-1zm-1 0h1zm1-1h1v1zm2-3v1zm0 0zm0 0h1l-1 1zm-1 0h1v1zm2 1zm0 0v1zm-1 0h1l-1 1zm-1 0h1l-1 1zm0 0zm0 0h1v1zm0 0v1zm0 0h2l-1 1zm2 1h1-1zm1 1zm-1 0zm1 0v1zm0 1h1-1zm0 0zm-1-1v1zm0 1zm-1 0h1-1zm1-1h1l-1 1zm-2-1h2l-1 2zm1-3h5l-2 5zm7 8zm0 0v1zm-1 0h1v1zm1 1h1-1zm1 1zm-1 0zm-1-1zm0 1h1zm0 0zm0-1h1v1zm2-3h1-1zm0-1v1zm0 1h1zm0 0zm1 1zm0 0zm0 0zm-1 0h1zm-1 0h1-1zm1 0zm-1 0zm0-1h2l-1 1zm2 2h1v1zm0 0h1zm1 0v1zm-1 0v1zm1 1h1l-1 1zm0 0zm0 1h1zm0 0zm-1-1zm0 1zm-1 0h1zm1-1h1v1zm-2-2h3l-2 3zm2 6h1zm1 0zm-1 0zm1 1h1l-1 1zm0 0zm0 0h1v1zm0 0v1zm-1 0v1zm0 0zm0 0v1zm-1 0h1v1zm1-1h1v2zm2-3v1zm0 0zm0 1zm-1 0h1zm1 1h1zm0-1h1v1zm1 1zm-1 0zm-1-1v1zm0 1h1zm0 0zm0-1h2l-1 1zm2 2h1-1zm0 0zm0 0h1zm0 0zm1 1v1zm0 0zm0 0v1zm-1 0h1v1zm-1 0h1v1zm0 0h1zm1 0v1zm-1 0v1zm1-1h1l-1 2zm-2-1h2l-1 3zm-6 1zm0 0h1-1zm0 0zm1 1zm0 0v1zm-1 0h1l-1 1zm-1 0h1-1zm1 0v1zm-1 0v1zm0-1h2l-1 2zm2-3h1-1zm1 1zm-1 0zm1 0v1zm0 1h1zm0 0zm-1-1v1zm0 1zm-1 0h1-1zm1-1h1l-1 1zm2 2zm0 0zm-1 0h1zm1 1h1l-1 1zm0 0h1-1zm1 0v1zm-1 0v1zm-1 0zm0 0h1v1zm0 0v1zm0-1h1v2zm-2-1h3l-2 3zm1-2h6l-3 5Zm-8-5h11l-5 10z" style="fill:none;fill-opacity:1;fill-rule:evenodd;stroke:#fff;stroke-width:.0513732;stroke-linecap:butt;stroke-linejoin:miter;stroke-dasharray:none;stroke-opacity:1" transform="translate(-16 -32)"/>
</svg>"""

gif_url = "https://upload.wikimedia.org/wikipedia/commons/a/a4/Mandelbrot_sequence_new.gif"

with sld_3:
    col1 = Content()
    css = {'text-align': 'center', "font-size": "70%"}
    col1.add_text('This is an image', **css)
    css_class = {"border": "1px solid #ddd", 'border-radius': "4px",
                 'class': ['rounded', 'img-fluid', 'mx-auto', 'd-block']}
    col1.add_image(gif_url, **css_class)
    sld_3.add_col(col1.render(), "col-6")

    col2 = Content()
    col2.add_text('And a svg', **css)
    css_svg = {"text-align": "center"}
    col2.add_svg(svg, **css_svg)
    sld_3.add_col(col2.render(), "col-6")
```

![sld_content_images.png](assets%2Fimg%2Fsld_content_images.png)

### Plotly and Altair
Plotly or Altair graphs can be easily added with `add_plotly()` and `add_altair()`. Interactivity 
is fully functional. 

```python
import plotly.express as px

df = px.data.iris()
fig = px.scatter(df, x="sepal_width", y="sepal_length",
                 color="species", size="petal_length", hover_data=["petal_width"])

fig.update_layout(autosize=False, width=500, height=500)

sld_4 = Container()
with sld_4:
    col1 = Content()
    col1.add_heading(text="Plotly example", tag="h2", )
    j = fig.to_json()
    char_center={'class': ['d-flex', 'justify-content-center']}
    col1.add_plotly(json=j, **char_center)
    sld_4.add_col(col1.render(), "col-sm-12")
```

```python
# A simple Altair chart
import altair as alt

source = px.data.iris()

chart = (
    alt.Chart(source)
    .mark_circle(size=60)
    .encode(
        x="sepal_width", y="sepal_length", color="species",
        tooltip=["species", "sepal_length", "sepal_width"],
    )
    .interactive()
    .properties(width=900, height=500)
)

sld_5 = Container()
with sld_5:
    col1 = Content()
    col1.add_heading(text="Altair example", tag="h2")
    j = chart.to_json()
    col1.add_altair(json=j, **char_center)
    sld_5.add_col(col1.render(), "col-sm-12")
```

It is **highly recommended** to set chart's width and height manually

![sld_content_plotly.png](assets%2Fimg%2Fsld_content_plotly.png)
![sld_content_altair.png](assets%2Fimg%2Fsld_content_altair.png)

###  Centered subtitle
A simple slide with a unique centered subtitle. 'r-fit-text' class is also used.

```python
# Create a simple slide with a center subtitle
sld_6 = Container(center=True)
with sld_6:
    col1 = Content()
    col1.add_heading(text="A fit and centered text", tag="h3", **{'class': ['r-fit-text']})
    sld_6.add_col(col1.render(), "col-12", **{'text-align': 'center'})
```

![sld_subtitle.png](assets%2Fimg%2Fsld_subtitle.png)

###  Customize content
This example show how to add cusomized content like Bootstrap cards

```python
# Using add_div to add bootstrap card
sld_7 = Container()

with sld_7:
    col1 = Content()
    col1.add_heading(text="custom div example", tag="h2")
    sld_7.add_col(col1.render(), "col-sm-12")

def bs_card(title, content, bg="secondary"):
    return f"""
  <div class="card text-white bg-{bg} mb-3 h-100" style="max-width: 18rem;">
      <h4 class="card-header">{title}</h4>
      <div class="card-body">
        <small class="card-text">{content}</small>
      </div>
  </div>
    """

with sld_7:
    card1 = Content()
    card1_div = bs_card("The first card", "And its content")
    card1.add_div(div=card1_div)

    card2 = Content()
    card2_div = bs_card("The second card", "And its content", "info")
    card2.add_div(div=card2_div)

    card3 = Content()
    card_img = f"<img src='{logo_url}' class= 'mx-auto my-auto d-block'>"
    card3_div = bs_card("images work too", card_img, "warning")
    card3.add_div(div=card3_div)

    sld_7.add_col(card1.render(), "col-sm-4")
    sld_7.add_col(card2.render(), "col-sm-4")
    sld_7.add_col(card3.render(), "col-sm-4")
```

![sld_custom.png](assets%2Fimg%2Fsld_custom.png)

### Presentation rendering
Now, lets add all slides to a presentation using `Presentation` class
1. presentation is an instance of `Presentation`
2. The `add_slide()` method is used to fill the presentation with all the previous slides
3. `render_presentation()` is used to compile all the slides. 
4. Note that reveals.js theme can be pass to the `theme` parameter. Custom css theme can 
be passed : `theme='custom, custom_theme_url='the_css_url'`

```python
# Create a new presentation
presentation = Presentation()

# Add the title slide to the presentation
slides = [sld_0, sld_1, sld_2, sld_3, sld_4, sld_5, sld_6]
presentation.add_slide(slides)

# Render the presentation as an HTML file. You can pass the reveal.js theme
html = presentation.render_presentation(theme='moon')

with open("readme_example.html", "w") as f:
    f.write(html)
```
And the output : [readme_example.html](https://raw.githack.com/fbxyz/respysive-slide/master/readme_example.html)
(press F for full-screen)

### Presentation rendering with nbconvert
Alternatively, nbconvert can be used to generate the slides using `from IPython.display import HTML` : 
1. Load Bootstrap on Jupyter : 
```python
from IPython.display import HTML
bs_url = "<link rel='stylesheet' href='https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css'>"
HTML(bs_url)
```
2. Show the slide rendering. Don't forget to set the Slide Type on `Slide`
```python
HTML(sld_title.render())
```

___
## PDF export
Like reveals.js, just add `?print-pdf` after your url (.i.e /presentation.html?print-pdf). 
Then print the results with your browser : 
[readme_example.html?print-pdf ](https://raw.githack.com/fbxyz/respysive-slide/master/readme_example.html?print-pdf)

The best results with reveal.js are obtained with chrome and chromium
