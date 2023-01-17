# respysive-slide
___
A Python package that allows you to create interactive presentations using Python, Bootstrap and Reveal.js. 
Charts from Altair and Plotly can also be added.

___
## Installation
With PyPI 
```
pip install respysive-slide
```
In case of error : 
`ERROR: No matching distribution found for soupsieve>=2.3.2`
be sure to install beautifulsoup4 before respysive_slide : 
```
pip install beautifulsoup4 respysive-slide
```

You can also clone the [repo](https://github.com/fbxyz/respysive-slide) and import respysive as a module

___
## Usage

The package consists of three main classes: `Content`, `Container` and `Presentation`.

`Container` is used to create a unique slide. You can add various elements to it such as text, headings, images, and lists.

`Content` is used to add HTML tag to a `Container` (i.e. a slide)

`BootstrapPresentation` is used to create the final presentation. You can add slides to it and then render the presentation as an HTML file.

### Title slide
Here's an example of how to use the package:

1. A new Container instance is created : `sld_title`
2. A new row is created : `with sld_title:`
3. A new Content instance is created
4. The title page is added to this new instance with the `add_title_page` method
5. This Content instance is added to a 12 width Bootstrap inside the `sld_title` Container
```python
from respysive import Content, Presentation, Container

# Create a new title slide
sld_title = Container()

# open a row
with sld_title:
    title_page = Content()
    title_page.add_title_page(
        title="Your title",
        subtitle="Your subtitle",
        authors=["Author 1", "Author 2", "Author 3"],
        logo="""https://raw.githubusercontent.com/fbxyz/pratik/main/Logo.png""",
    )
    # add the HTML render to a Bootstrap column of width 12
    sld_title.add_col(title_page.render(), "col-sm-12")
```
![sld_title.png](assets%2Fimg%2Fsld_title.png)


### One column text slide
Next, we create a new Container instance `sld_content_1col` : 
1. A title is added to title (a `Content` instance) with the `add_heading()` method.
2. title is added to a 12 width columns inside `sld_content_1col`.
3. Following the same principle, `add_text()` is used to fill the slide with some dummy text.

Note that most of `Content` methods accept **kwargs for css style. Just replace `-` by `_` : 
- `text_align="middle"` for text-align:middle
- `background_color="#1d3557"` for background-color=#1d3557

Also, Fontawesome icons can be added in heading.

 ```python
# Create a new slide with only 1 column
sld_content_1col = Container()

# open a row for the slide title
with sld_content_1col:
    title = Content()
    title.add_heading(
        text="Your slide title",
        tag="h2",
        icon="fas fa-users",
        color="#f1faee",
        text_align="left",
        background_color="#1d3557",
    )
    # add the HTML render to a Bootstrap column of width 12
    sld_content_1col.add_col(title.render(), "col-sm-12")

# open a new row after the previous title row
with sld_content_1col:
    # lets add some text
    txt = Content()
    txt.add_text(
        text="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
    )
    # add the HTML render to a Bootstrap column of width 12
    sld_content_1col.add_col(txt.render(), "col-sm-12")
```
![sld_content_1col.png](assets%2Fimg%2Fsld_content_1col.png)

### Two columns text slide
Example with two text columns :
```python
# Create a new slide with 2 columns but no title
sld_content_2cols = Container()

# open a new row. For each row, the sum of columns cannot exceed 12
with sld_content_2cols:

    # lets add some text
    txt_left = Content()
    txt_left.add_text(
        text="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.t nulla pariatur.",
    )

    # lets add another text
    txt_right = Content()
    txt_right.add_text(
        text="Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
    )

    # add the two HTML renders to two Bootstrap columns of width 6
    sld_content_2cols.add_col(txt_left.render(), "col-sm-6")
    sld_content_2cols.add_col(txt_right.render(), "col-sm-6")
```
![sld_content_2cols.png](assets%2Fimg%2Fsld_content_2cols.png)

### Two columns slide : image and list
Example with one image and one ordered list :
```python
# Create a new slide with 2 columns with image and list
sld_content_images = Container()

# title row
with sld_content_images:
    title = Content()
    title.add_heading(
        text="Your slide title",
        tag="h2",
    )
    sld_content_images.add_col(title.render(), "col-sm-12")

# content row with 2 columns (width of 5 and 7). First image have an extra title
with sld_content_images:
    # The image and its title
    image = Content()
    image.add_heading(
        "A fractal Universe", tag="h5", text_align="center", color="#e63946"
    )
    img_url = (
        "https://upload.wikimedia.org/wikipedia/commons/d/d5/Univers_Fractal_J.H..jpg"
    )
    image.add_image(img_url, border="1px solid #ddd", border_radius="4px")
    sld_content_images.add_col(image.render(), "col-sm-5")

    # an ordered list
    lst = Content()
    list_items = ["item 1", "item 2", "item 3"]
    lst.add_list(list_items, ordered=True)
    sld_content_images.add_col(lst.render(), "col-sm-7")
```
![sld_content_images.png](assets%2Fimg%2Fsld_content_images.png)

### Plotly and Altair
Plotly or Altair graphs can be easily added with `add_plotly()` and `add_altair()`. Interactivity 
is fully functional. 

```python
import plotly.express as px

df = px.data.iris()
fig = px.scatter(df, x="sepal_width", y="sepal_length",
                 color="species", size="petal_length",
                 hover_data=["petal_width"])

fig.update_layout(autosize=False, width=900, height=500)

sld_content_plotly = Container()

with sld_content_plotly:
    chart_p = Content()
    j = fig.to_json()
    chart_p.add_plotly(json=j)
    sld_content_plotly.add_col(chart_p.render(), "col-sm-12")
```

```python
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

sld_content_altair = Container()
with sld_content_altair:
    chart_a = Content()
    chart_a.add_heading(text="Altair example", tag="h2", )
    j = chart.to_json()
    chart_a.add_altair(json=j)
    sld_content_altair.add_col(chart_a.render(), "col-sm-12")
```
**It is highly recommended to set chart's width and height manually**
![sld_content_plotly.png](assets%2Fimg%2Fsld_content_plotly.png)
![sld_content_altair.png](assets%2Fimg%2Fsld_content_altair.png)

###  Centered subtitle
A simple slide with a unique centered subtitle :
```python
# Create a last slide with an unique subtitle
sld_subtitle = Container()

with sld_subtitle:
    subtitle_page = Content()
    subtitle_page.add_subtitle(
        text="A center subtitle",
        icon="fa fa-check",
        font_size="6rem",
        color="#e63946",
        text_align="center",
    )

    sld_subtitle.add_col(subtitle_page.render(), "col-sm-12")
```

![sld_subtitle.png](assets%2Fimg%2Fsld_subtitle.png)

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

# Add the title slide = to the presentation
presentation.add_slide(sld_title)
presentation.add_slide(sld_content_1col)
presentation.add_slide(sld_content_2cols)
presentation.add_slide(sld_content_images)
presentation.add_slide(sld_content_plotly)
presentation.add_slide(sld_content_altair)
presentation.add_slide(sld_subtitle)

# Render the presentation as an HTML file. You can pass the reveal.js theme
html = presentation.render_presentation(theme='moon')

with open("presentation.html", "w") as f:
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

`#TODO : add an ipynb example`

## PDF export
Like reveals.js, just add `?print-pdf` after your url (.i.e /presentation.html?print-pdf). 
Then print the results with your brother

The best results are obtained with chrome...
