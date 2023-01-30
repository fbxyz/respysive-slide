from markdown import markdown
from respysive import Presentation, Slide

logo_url = "https://upload.wikimedia.org/wikipedia/commons/4/4d/Fractal_canopy.svg"

# Create a new presentation
p = Presentation()

# Create the first slide with a centered layout
slide1 = Slide(center=True)

# Content for the title page
title_page_content = {
    'title': 'Your presentation title',
    'subtitle': 'Your subtitle',
    'authors': 'Author 1, Author 2',
    'logo': logo_url
}

# Styles for the title page content
styles = [
    {'color': '#e63946', 'class': 'r-fit-text border-top'},  # title
    {},  # subtitle style by default
    {},  # authors style by default
    {'filter': 'invert(100%) opacity(30%)'},  # logo
]

# Add the title page to the slide
slide1.add_title_page(title_page_content, styles)

## Slide 2 ##

# Create the second slide
slide2 = Slide()

# Add a heading to the slide with a fontawesome icon
slide2.add_title("Your title with a fontawesome icon", icon="fas fa-infinity fa-beat")

# Create some text in markdown format
txt = markdown("""
This is some dummy text 

- and it's easier to use Markdown
<ul><li>but it's ok to use HTML tag</li></ul>
""")

# Add the text to the slide in a new Bootstrap column with a width of 12 (default)
slide2.add_content([txt], columns=[12])

## Slide 3 ##

# Create a new slide
slide3 = Slide()

text = markdown("""
En cosmologie, le modèle de l'univers fractal désigne un modèle cosmologique 
dont la structure et la répartition de la matière possèdent une dimension fractale, 
et ce, à plusieurs niveaux. 

De façon plus générale, il correspond à l'usage ou 
l'apparence de fractales dans l'étude de l'Univers et de la matière qui le compose.
Ce modèle présente certaines lacunes lorsqu'il est utilisé à de très grandes ou de 
très petites échelles.

""")

# Add image url
url = "https://upload.wikimedia.org/wikipedia/commons/d/d5/Univers_Fractal_J.H..jpg"

# Add Heading to slide
slide3.add_title("Bootstrap powering")

# Add styles to slide
css_txt = [
    {'font-size': '70%', 'text-align': 'justify', 'class': 'bg-warning'},  # text style
    None  # url style is mandatory even it is None
]

# Add content to slide, where text and url are added to the slide with 7 and 5 columns respectively
# css_txt is added as styles
slide3.add_content([text, url], columns=[7, 5], styles=css_txt)

## Slide 4 ##
slide4 = Slide()
slide4.add_title("Plotly")

# import plotly express for creating scatter plot
import plotly.express as px

# load iris data
df = px.data.iris()

# create scatter plot
fig = px.scatter(df, x="sepal_width", y="sepal_length",
                 color="species", size="petal_length", hover_data=["petal_width"])

# update layout
fig.update_layout(autosize=True)

# Export the figure to json format
j = fig.to_json()

# apply css to the figure
css_txt = [{'class': 'stretch'}]

# add the scatter plot to the slide
slide4.add_content([j], columns=[12], styles=css_txt)

## Slide 5 : Altair plot##
slide5 = Slide()
slide5.add_title("Altair")

# import altair for creating scatter plot
import altair as alt

source = px.data.iris()

# create scatter plot
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

# Export the figure to json format
j = chart.to_json()

# add the scatter plot to the slide
slide5.add_content([j], columns=[12])

## Slide 6 : Bootstrap Cards ##
slide6 = Slide()

# card 1 content
txt_card1 = markdown("""
- list 1
- list 2

""")

# card 1 image
univ_url = "https://upload.wikimedia.org/wikipedia/commons/b/b5/Mandel_zoom_04_seehorse_tail.jpg"

# list of cards. These orders will be the same on the HTML page
cards = [{'text': txt_card1, 'image': univ_url},  # Only text and image
         {'image': logo_url, 'text': "Card text 2", 'title': "Card Title 2", },  # Image, text and title
         {'title': "Card Title 3", 'text': "Card text 3"}]  # Title and text

# styles for each cards
styles_list = [{'font-size': '20px', 'color': '#1d3557', 'class': 'bg-danger'},
               {'font-size': '20px', 'color': '#e63946', 'class': 'bg-warning'},
               {'font-size': '20px', 'color': '#f1faee', 'class': 'bg-info'}]

# add title and card to slide
slide6.add_title("Bootstrap cards can be added")
slide6.add_card(cards, styles_list)

## Slide 7 : Background ##

# Create a dictionary with slide kwargs

bckgnd_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/Frost_patterns_2.jpg/1920px-Frost_patterns_2.jpg"
slide_kwargs = {
    'data-background-image': bckgnd_url,
    'data-background-size': 'cover',  # more options here : https://revealjs.com/backgrounds/
}

# Create a slide object with slide kwargs
slide7 = Slide(center=True, **slide_kwargs)

css_background = {"class": "text-center", "color": "#e63946", "background-color": "#f1faee"}
slide7.add_title("Image  background", **css_background)

## Slide 8 and 9 : Vertical slide ##

slide8 = Slide()
text = markdown("""Press arrow down to show vertical slide""")
slide8.add_title("Horizontal and vertical slides")
slide8.add_content([text])

## Slide 8 and 9 : Vertical slide ##

slide9 = Slide(center=True)
slide9.add_title("Horizontal and vertical slides")
text = markdown("""This is a vertical slide""")
slide9.add_content([text])

# Adding slide to the presentation
p.add_slide([slide1, slide2, slide3, slide4, slide5, slide6, slide7, [slide8, slide9]])

# Saving the presentation in HTML format

p.save_html("readme_example.html")


#  custom_theme = "https://raw.githack.com/fbxyz/respysive-slide/master/assets/css/sorbone.css"
#  p.save_html("readme_example.html", theme="custom", custom_theme=custom_theme)
