from respysive import Content, Presentation, Container

# Create a new title slide
sld_title = Container()

# open a row
with sld_title:
    title_page = Content()
    title_page.add_title_page(
        title="My title",
        subtitle="My subtitle",
        authors=["Author 1", "Author 2", "Author 3"],
        logo="https://upload.wikimedia.org/wikipedia/fr/2/2c/Universit%C3%A9_Panth%C3%A9on-Sorbonne_"
             "%28depuis_janvier_2015%29.svg",
    )
    # add the HTML render to a Bootstrap column of width 12
    sld_title.add_col(title_page.render(), "col-sm-12")

# Create a new slide with only 1 column
sld_content_1col = Container()

# open a row for the slide title
with sld_content_1col:
    title = Content()
    title.add_heading(
        text="My slide title",
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
        text="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et "
             "dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip "
             "ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore "
             "eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia "
             "deserunt mollit anim id est laborum.",
    )
    # add the HTML render to a Bootstrap column of width 12
    sld_content_1col.add_col(txt.render(), "col-sm-12")

# Create a new slide with 2 columns but no title
sld_content_2cols = Container()

# open a new row. For each row, the sum of columns cannot exceed 12
with sld_content_2cols:
    # lets add some text
    txt_left = Content()
    txt_left.add_text(
        text="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et "
             "dolore magna aliqua.t nulla pariatur.",
    )

    # let's add another text
    txt_right = Content()
    txt_right.add_text(
        text="Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. "
             "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est "
             "laborum.",
    )

    # add the two HTML renders to two Bootstrap columns of width 6
    sld_content_2cols.add_col(txt_left.render(), "col-sm-6")
    sld_content_2cols.add_col(txt_right.render(), "col-sm-6")

# Create a new slide with 2 columns with image and list
sld_content_images = Container()

# title row
with sld_content_images:
    title = Content()
    title.add_heading(
        text="My slide title",
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

# Create a last slide with an unique subtitle
sld_subtitle = Container()

with sld_subtitle:
    subtitle_page = Content()
    subtitle_page.add_subtitle(
        text="My subtitle",
        icon="fa fa-check",
        font_size="6rem",
        color="#e63946",
        text_align="center",
    )

    sld_subtitle.add_col(subtitle_page.render(), "col-sm-12")

# Create a new presentation
presentation = Presentation()

# Add the title slide = to the presentation
presentation.add_slide(sld_title)
presentation.add_slide(sld_content_1col)
presentation.add_slide(sld_content_2cols)
presentation.add_slide(sld_content_images)
presentation.add_slide(sld_subtitle)

# Render the presentation as an HTML file. You can pass the reveal.js theme
html = presentation.render_presentation(theme='moon')

with open("readme_example.html", "w") as f:
    f.write(html)
