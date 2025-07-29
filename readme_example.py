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

## Slide 1b: split title page alternative ##

# Create a slide with split title page layout
slide1b = Slide(center=True)

# Content for the split title page
split_title_content = {
    'title': 'Your presentation title',
    'subtitle': 'Your subtitle',
    'authors': 'Author 1, Author 2',
}

# Styles for the title elements  
title_styles = [
    {'color': '#e63946', 'font-weight': 'bold', 'font-size': '60px'},  # title
    {'color': '#457b9d', 'font-size': '40px'},  # subtitle
    {'color': '#457b9d', 'font-size': '25px'},  # authors
]

# Style for the title column 
title_column_style = {
    'background-color': '#1d3557', 
    'color': '#f1faee',             
    'padding': '40px',              
    'border-radius': '10px 0 0 10px'  
}

# Style for the custom content column 
image_style = {
    'text-align': 'center',
    'padding': '30px',
    'background-color': '#e63946',
    'border-radius': '0 10px 10px 0'  
}

# Add the split title page - title on left (8 cols), logo on right (4 cols)
slide1b.add_split_title_page(
    title_page_content=split_title_content,
    custom_content=logo_url,
    title_column_width=8,
    custom_column_width=4,
    title_page_class="split-intro",
    custom_content_style=image_style,
    title_styles=title_styles,
    title_column_style=title_column_style  
)

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
url = "./assets/img/Univers_Fractal_J.H..jpg"

# Add heading to slide
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

## Slide 4bis: shared GeoJSON example with global sharing ##

# Load GeoJSON data
from urllib.request import urlopen
import json
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

# Load unemployment data
import pandas as pd
df_counties = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/fips-unemp-16.csv",
                   dtype={"fips": str})

# Add additional columns with pandas
import random
random.seed(42)
df_counties['population'] = [random.randint(10000, 500000) for _ in range(len(df_counties))]
df_counties['income'] = [random.randint(25000, 85000) for _ in range(len(df_counties))]
# Add area data for density calculation
df_counties['area_sq_miles'] = [random.randint(200, 2000) for _ in range(len(df_counties))]
df_counties['density'] = (df_counties['population'] / df_counties['area_sq_miles']).round(1)

# Add global GeoJSON data to presentation
p.add_global_geojson("us_counties", counties)

slide_maps = Slide()
slide_maps.add_title("Sharing geojson data between multiple plotly charts", **{'class': 'r-fit-text'})

# Add context text
context_text = """
Counties geojson data (~2MB) is shared across the presentation
"""

css_txt = [{'text-align': 'center', 'font-size': "60%"}]

slide_maps.add_content([context_text], columns=[12], styles=css_txt)

# Create population density map
population_config = {
    "data": [{
        "type": "choropleth",
        "locations": df_counties['fips'].tolist(),
        "z": df_counties['density'].tolist(),
        "colorscale": "Blues",
        "colorbar": {
            "title": "Density<br>(per sq mi)",
            "thickness": 15,
            "len": 0.7
        },
        "hovertemplate": (
            "<b>County {text}</b><br>" +
            "Population: %{customdata[0]:,.0f}<br>" +
            "Area: %{customdata[1]:,.0f} sq mi<br>" + 
            "Density: <b>%{z:.1f} per sq mi</b>" +
            "<extra></extra>"
        ),
        "text": df_counties['fips'].tolist(),
        "customdata": list(zip(df_counties['population'], df_counties['area_sq_miles']))
    }],
    "layout": {
        "geo": {
            "projection": {"type": "albers usa"}, 
            "scope": "usa",
            "showlakes": True,
            "lakecolor": "lightblue"
        },
        "title": {
            "text": "Population Density by County (Random Data)",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 16}
        },
        "margin": {"r":10,"t":50,"l":10,"b":10}
    }
}

# Create choropleth map for income
income_config = {
    "data": [{
        "type": "choroplethmap",
        "locations": df_counties['fips'].tolist(),
        "z": df_counties['income'].tolist(),
        "colorscale": [
            [0.0, "#ffffb2"],
            [0.2, "#fed976"],
            [0.4, "#feb24c"],
            [0.6, "#fd8d3c"],
            [0.8, "#f03b20"],
            [1.0, "#bd0026"]
        ],
        "colorbar": {
            "title": {
                "text": "Median Income ($)",
                "font": {"size": 14, "family": "Arial Black"}
            },
            "thickness": 20,
            "len": 0.8,
            "x": 1.02,
            "tickmode": "array",
            "tickvals": [25000, 40000, 55000, 70000, 85000],
            "ticktext": ["$25K", "$40K", "$55K", "$70K", "$85K"],
            "tickfont": {"size": 11}
        },
        "hovertemplate": (
            "<b>County FIPS: %{location}</b><br>" +
            "Median Income: <b>$%{z:,.0f}</b><br>" +
            "Population: <b>%{customdata:,.0f}</b>" +
            "<extra></extra>"
        ),
        "customdata": df_counties['population'].tolist(),
        "marker": {
            "line": {"color": "white", "width": 0.5},
            "opacity": 0.9
        }
    }],
    "layout": {
        "map": {
            "style": "carto-positron",
            "zoom": 1,
            "center": {"lat": 38.0, "lon": -97.0}
        },
        "title": {
            "text": "Median Household Income by County (Random Data)",
            "x": 0.5,
            "xanchor": "center",
            "font": {
                "size": 18,
                "family": "Arial Black",
                "color": "#2E86AB"
            },
            "pad": {"t": 20}
        },
        "annotations": [{
            "text": "Data source: Simulated random data",
            "showarrow": False,
            "x": 0.99,
            "y": 0.01,
            "xref": "paper",
            "yref": "paper",
            "xanchor": "right",
            "yanchor": "bottom",
            "font": {"size": 10, "color": "gray"}
        }],
        "margin": {"r":80,"t":80,"l":20,"b":40},
        "paper_bgcolor": "rgba(248, 249, 250, 0.95)"
    }
}

# Add the two maps side by side using shared GeoJSON data
slide_maps.add_content(
    [population_config, income_config], 
    columns=[6, 6],
    shared_data_ids=["us_counties", "us_counties"]
)

## Slide 5: Altair plot ##
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

## Slide 5_fig: Matplotlib plot ##
slide5_fig = Slide()
slide5_fig.add_title("Matplotlib")

import numpy as np
import matplotlib.pyplot as plt

x = np.arange(0,4*np.pi-1,0.1)   # start,stop,step
y = np.sin(x)
z = np.cos(x)

plt.rcParams["figure.figsize"] = (8, 5)
fig, ax = plt.subplots()
plt.plot(x,y,x,z)
plt.xlabel('x values')
plt.title('sin and cos ')
plt.legend(['sin(x)', 'cos(x)'])


# add the  plot to the slide
slide5_fig.add_content([fig], columns=[12])

## Slide 6: LaTeX equations ##
slide6 = Slide()
slide6.add_title("Mathematical Equations")

# Text with LaTeX expressions
math_content = """
The Gaussian function $f(x) = e^{-x^2}$ or in display mode:

$$f(x) = e^{-x^2}$$
"""

slide6.add_content([math_content], columns=[12])


## Slide 7: Bootstrap cards ##
slide7 = Slide()

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
slide7.add_title("Bootstrap cards can be added")
slide7.add_card(cards, styles_list)

## Slide 8: background ##

# Create a dictionary with slide kwargs

bckgnd_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/Frost_patterns_2.jpg/1920px-Frost_patterns_2.jpg"
slide_kwargs = {
    'data-background-image': bckgnd_url,
    'data-background-size': 'cover',  # more options here : https://revealjs.com/backgrounds/
}

# Create a slide object with slide kwargs
slide8 = Slide(center=True, **slide_kwargs)

css_background = {"class": "text-center", "color": "#e63946", "background-color": "#f1faee"}
slide8.add_title("Image  background", **css_background)

## Slide 9 and 10: vertical slide ##

slide9 = Slide()
text = markdown("""Press arrow down to show vertical slide""")
slide9.add_title("Horizontal and vertical slides")
slide9.add_content([text])

## Slide 9 and 10: vertical slide ##

slide10 = Slide(center=True)
slide10.add_title("Horizontal and vertical slides")
text = markdown("""This is a vertical slide""")
slide10.add_content([text])

## Slide 11: speaker view ##

slide11 = Slide()
slide11.add_title("Speaker view")
text = markdown("""Press S for Speaker View""")
sw = markdown("""
  <aside class="notes">
    This is a test for speaker view
  </aside>
""")
slide11.add_content([text])
slide11.add_content([sw])

# Adding slide to the presentation
p.add_slide([slide1, slide1b, slide2, slide3, slide4, slide_maps, slide5, slide5_fig, slide6, slide7, slide8, [slide9, slide10], slide11])

# Saving the presentation in HTML format

p.save_html("readme_example.html")

# custom_theme = "https://raw.githack.com/fbxyz/respysive-slide/master/assets/css/sorbone.css"
# custom_theme = "./assets/css/abm.css"
# p.save_html("readme_example.html", theme="custom", custom_theme=custom_theme)