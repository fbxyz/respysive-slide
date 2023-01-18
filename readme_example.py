from respysive import Content, Presentation, Container
from markdown import markdown

from respysive import Content, Presentation, Container

# A new Container instance is created. The slide will be centered
sld_0 = Container(center=True)

# A new row is created fot the main title
with sld_0:
    row1 = Content()

    # divclass is used to pass <div class=***>
    row1.add_heading(text="The main Title", tag="h1", divclass=['r-fit-text'])

    # row1 is added in a 12 width Bootstrap columns
    # text_align is a **kwarg for css style
    sld_0.add_col(row1.render(), "col-12", text_align='left')

# A second row for the subtitle is created inside the sld_0 container
with sld_0:
    row2 = Content()
    row2.add_heading(text="The subtitle", tag="h2", color="#e63946")
    sld_0.add_col(row2.render(), "col-12", text_align='left')

# A final row for the authors (column of width 6) is added
with sld_0:
    row3 = Content()
    row3.add_text(text="Author 1, Author 2", tag="p")
    sld_0.add_col(row3.render(), "col-6", text_align='left')

# A new slide is created by instancing Container()
sld_1 = Container()
with sld_1:
    row1 = Content()
    row1.add_heading(text="Your slide title ", tag="h3", icon="fas fa-infinity")
    sld_1.add_col(row1.render(), "col-12", text_align='left')

long_text = """
En cosmologie, le modèle de l'univers fractal désigne un modèle cosmologique 
dont la structure et la répartition de la matière possèdent une dimension fractale, 
et ce, à plusieurs niveaux. De façon plus générale, il correspond à l'usage ou 
l'apparence de fractales dans l'étude de l'Univers et de la matière qui le compose.
\n Ce modèle présente certaines lacunes lorsqu'il est utilisé à de très grandes ou de 
très petites échelles
"""

with sld_1:
    row2a = Content()
    row2a.add_text(text=long_text, divclass=['fragment'])
    sld_1.add_col(row2a.render(), "col-8", text_align='justify', font_size="32px")

    row2b = Content()
    row2b.add_text("A cool fractal", font_size="60%")
    row2b.add_image("https://upload.wikimedia.org/wikipedia/commons/a/a4/Mandelbrot_sequence_new.gif")
    sld_1.add_col(row2b.render(), "col-4")

sld_2 = Container()
with sld_2:
    title = Content()
    title.add_heading(text="Markdown use", tag="h3", )
    sld_2.add_col(title.render(), "col-12", text_align='left')

my_txt = markdown("""
You can also use the **markdown** package to easily add text""")

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
    sld_2.add_col(txt.render(), "col-12", text_align='left')

with sld_2:
    col1 = Content()
    col1.add_text(text=txt_col1)
    sld_2.add_col(col1.render(), "col-6", text_align='left', font_size="60%")

    col2 = Content()
    col2.add_text(text=txt_col2, )
    sld_2.add_col(col2.render(), "col-6", text_align='left', font_size="60%")

sld_3 = Container()
svg = """<svg xmlns="http://www.w3.org/2000/svg" width="1069.626" height="340.903" viewBox="0 0 1002.775 319.597"><defs><clipPath id="c" clipPathUnits="userSpaceOnUse"><path d="M0 0h425.197v595.276H0V0Z"/></clipPath><clipPath id="b" clipPathUnits="userSpaceOnUse"><path d="M0 0h425.197v595.276H0V0Z"/></clipPath><clipPath id="a" clipPathUnits="userSpaceOnUse"><path d="M0 0h425.197v595.276H0V0Z"/></clipPath></defs><g clip-path="url(#a)" style="fill:#f1faee;fill-opacity:1" transform="matrix(5 0 0 -5 -461.542 2852.669)"><path d="M0 0a.55.55 0 1 1 0 1.099A.55.55 0 0 1 0 0" style="fill:#f1faee;fill-opacity:1;fill-rule:nonzero;stroke:none" transform="translate(192.586 568.727)"/></g><path d="m0 0-13.841-5.763h27.682L0 0Z" style="fill:#f1faee;fill-opacity:1;fill-rule:nonzero;stroke:none" transform="matrix(5 0 0 -5 501.387 90.886)"/><g clip-path="url(#b)" style="fill:#f1faee;fill-opacity:1" transform="matrix(5 0 0 -5 -461.542 2852.669)"><path d="M0 0v2.429l-.861.837v2.97l.423.42c-.058.064-1.474 1.634-1.953 3.775h-1.455c-.46-2.052-1.781-3.581-1.94-3.76l-.004-.007.43-.428v-2.97l-.861-.837V0c-3.629-1.207-6.321-4.465-6.697-8.4l9.451 3.935.356.149.357-.149L6.697-8.4C6.321-4.465 3.629-1.207 0 0m-2.188 5.262c0 .16.056.383.341.383.285 0 .341-.227.341-.383V2.817a10.16 10.16 0 0 1-.682.086v2.359zm-1.382.158c0 .223.078.534.476.534.398 0 .476-.316.476-.534V2.932a9.392 9.392 0 0 1-.952 0V5.42zm-1.136-.158c0 .16.056.383.341.383.285 0 .341-.227.341-.383V2.9a9.55 9.55 0 0 1-.682-.087v2.449z" style="fill:#f1faee;fill-opacity:1;fill-rule:nonzero;stroke:none" transform="translate(195.696 557.679)"/></g><path d="M434.694 648.617h542.71v-3.47h-542.71v3.47z" style="fill:#f1faee;fill-opacity:1;fill-rule:nonzero;stroke:none" transform="translate(-204.66 -332.564)"/><g clip-path="url(#c)" style="fill:#f1faee;fill-opacity:1" transform="matrix(5 0 0 -5 -461.542 2852.669)"><path d="M0 0a.18.18 0 0 0 .175.174h.348A.174.174 0 0 0 .698 0v-3.83c0-1.047.652-1.865 1.727-1.865 1.084 0 1.745.799 1.745 1.846V0c0 .092.073.174.175.174h.349A.18.18 0 0 0 4.868 0v-3.885c0-1.397-.992-2.462-2.443-2.462C.983-6.347 0-5.282 0-3.885V0Z" style="fill:#f1faee;fill-opacity:1;fill-rule:nonzero;stroke:none" transform="translate(138.333 539.99)"/><path d="M0 0c0 .092.083.166.175.166h.229l4.143-5.163h.018v4.896c0 .092.073.174.175.174h.321a.18.18 0 0 0 .175-.174v-6.182c0-.091-.083-.165-.175-.165h-.165L.68-1.185H.671v-4.996a.175.175 0 0 0-.175-.175H.175A.181.181 0 0 0 0-6.181V0Z" style="fill:#f1faee;fill-opacity:1;fill-rule:nonzero;stroke:none" transform="translate(146.593 540.09)"/><path d="M0 0a.18.18 0 0 0 .175.174h.367A.18.18 0 0 0 .716 0v-6.08a.18.18 0 0 0-.174-.175H.175A.18.18 0 0 0 0-6.08V0Z" style="fill:#f1faee;fill-opacity:1;fill-rule:nonzero;stroke:none" transform="translate(155.303 539.99)"/><path d="M0 0c-.055.12.018.239.156.239h.368A.17.17 0 0 0 .68.138l2.287-5.144h.037L5.291.138a.179.179 0 0 0 .156.101h.367c.138 0 .212-.119.156-.239L3.178-6.181a.173.173 0 0 0-.156-.102H2.93a.185.185 0 0 0-.156.102L0 0Z" style="fill:#f1faee;fill-opacity:1;fill-rule:nonzero;stroke:none" transform="translate(158.62 539.925)"/><path d="M0 0c0 .092.073.174.175.174h3.619A.173.173 0 0 0 3.968 0v-.266a.174.174 0 0 0-.174-.175H.707v-2.241h2.637a.181.181 0 0 0 .174-.175v-.266a.175.175 0 0 0-.174-.175H.707V-5.64h3.087a.173.173 0 0 0 .174-.174v-.266a.174.174 0 0 0-.174-.175H.175A.174.174 0 0 0 0-6.08V0Z" style="fill:#f1faee;fill-opacity:1;fill-rule:nonzero;stroke:none" transform="translate(167.191 539.99)"/><path d="M0 0c.707 0 1.322.588 1.322 1.341 0 .698-.615 1.295-1.322 1.295h-1.782V0H0Zm-2.508 3.132c0 .092.073.175.175.175H.046c1.102 0 2.002-.864 2.002-1.957 0-.845-.56-1.552-1.36-1.873l1.259-2.333c.064-.12 0-.267-.156-.267h-.469a.157.157 0 0 0-.146.082L-.046-.606h-1.755v-2.342a.18.18 0 0 0-.174-.175h-.358a.174.174 0 0 0-.175.175v6.08z" style="fill:#f1faee;fill-opacity:1;fill-rule:nonzero;stroke:none" transform="translate(176.737 536.857)"/><path d="M0 0c.046.055.092.12.138.175.092.119.193.192.321.083.065-.056.735-.699 1.552-.699.745 0 1.231.469 1.231 1.011 0 .633-.551 1.01-1.607 1.451-1.01.441-1.617.854-1.617 1.901 0 .625.496 1.635 1.957 1.635.9 0 1.57-.468 1.57-.468.056-.028.166-.138.056-.312-.037-.056-.074-.12-.111-.175-.082-.128-.174-.165-.321-.083-.064.037-.643.423-1.203.423-.974 0-1.268-.625-1.268-1.011 0-.615.468-.973 1.24-1.294 1.24-.506 2.039-.974 2.039-2.04 0-.955-.909-1.653-1.984-1.653-1.084 0-1.818.634-1.938.744C-.018-.248-.11-.174 0 0" style="fill:#f1faee;fill-opacity:1;fill-rule:nonzero;stroke:none" transform="translate(181.487 534.699)"/><path d="M0 0a.18.18 0 0 0 .175.174h.367A.18.18 0 0 0 .716 0v-6.08a.18.18 0 0 0-.174-.175H.175A.18.18 0 0 0 0-6.08V0Z" style="fill:#f1faee;fill-opacity:1;fill-rule:nonzero;stroke:none" transform="translate(188.396 539.99)"/><path d="M0 0h-1.598a.175.175 0 0 0-.175.175v.266c0 .092.074.174.175.174h3.894a.174.174 0 0 0 .175-.174V.175A.175.175 0 0 0 2.296 0H.698v-5.64a.18.18 0 0 0-.175-.174H.175A.18.18 0 0 0 0-5.64V0Z" style="fill:#f1faee;fill-opacity:1;fill-rule:nonzero;stroke:none" transform="translate(193.495 539.549)"/><path d="M0 0a.128.128 0 0 0 .055.174l1.378.772c.055.037.193.055.239-.028l.165-.33c.037-.074.018-.166-.055-.193L.303-.221C.175-.275.128-.275.092-.202L0 0Zm-1.148-1.139c0 .092.073.174.175.174h3.618a.174.174 0 0 0 .175-.174v-.266a.175.175 0 0 0-.175-.175H-.441v-2.241h2.636a.181.181 0 0 0 .175-.175v-.266a.175.175 0 0 0-.175-.175H-.441v-2.342h3.086a.174.174 0 0 0 .175-.174v-.266a.175.175 0 0 0-.175-.175H-.973a.174.174 0 0 0-.175.175v6.08z" style="fill:#f1faee;fill-opacity:1;fill-rule:nonzero;stroke:none" transform="translate(199.724 541.129)"/><path d="M0 0c.753 0 1.396.616 1.396 1.406C1.396 2.15.753 2.719 0 2.719h-1.46V0H0Zm-2.158 3.242c0 .092.073.175.174.175h2.03c1.13 0 2.058-.919 2.058-2.03C2.104.248 1.176-.68.055-.68H-1.46v-2.158a.181.181 0 0 0-.175-.175h-.349a.174.174 0 0 0-.174.175v6.08z" style="fill:#f1faee;fill-opacity:1;fill-rule:nonzero;stroke:none" transform="translate(211.41 536.747)"/><path d="M0 0c-.451 1.001-.891 2.011-1.341 3.013h-.074L-2.756 0H0Zm-4.363-1.947 2.792 6.181c.027.056.074.102.156.102h.092c.083 0 .129-.046.156-.102l2.774-6.181c.055-.12-.018-.239-.156-.239h-.367a.17.17 0 0 0-.157.101L.248-.57h-3.261l-.67-1.515a.17.17 0 0 0-.157-.101h-.367c-.138 0-.212.119-.156.239" style="fill:#f1faee;fill-opacity:1;fill-rule:nonzero;stroke:none" transform="translate(219.532 535.92)"/><path d="M0 0c.707 0 1.322.588 1.322 1.341 0 .698-.615 1.295-1.322 1.295h-1.782V0H0Zm-2.508 3.132c0 .092.073.175.175.175H.046c1.102 0 2.002-.864 2.002-1.957 0-.845-.56-1.552-1.36-1.873l1.259-2.333c.064-.12 0-.267-.156-.267h-.469a.157.157 0 0 0-.146.082L-.046-.606h-1.755v-2.342a.18.18 0 0 0-.174-.175h-.358a.174.174 0 0 0-.175.175v6.08z" style="fill:#f1faee;fill-opacity:1;fill-rule:nonzero;stroke:none" transform="translate(226.249 536.857)"/><path d="M0 0a.18.18 0 0 0 .175.174h.367A.18.18 0 0 0 .716 0v-6.08a.18.18 0 0 0-.174-.175H.175A.18.18 0 0 0 0-6.08V0Z" style="fill:#f1faee;fill-opacity:1;fill-rule:nonzero;stroke:none" transform="translate(231.412 539.99)"/><path d="M0 0c.046.055.092.12.138.175.092.119.193.192.321.083.065-.056.735-.699 1.553-.699.744 0 1.231.469 1.231 1.011 0 .633-.552 1.01-1.608 1.451-1.01.441-1.617.854-1.617 1.901 0 .625.497 1.635 1.957 1.635.9 0 1.57-.468 1.57-.468.056-.028.166-.138.056-.312-.037-.056-.074-.12-.111-.175-.082-.128-.174-.165-.321-.083-.064.037-.643.423-1.203.423-.974 0-1.268-.625-1.268-1.011 0-.615.468-.973 1.24-1.294 1.241-.506 2.039-.974 2.039-2.04 0-.955-.909-1.653-1.984-1.653-1.084 0-1.818.634-1.938.744C-.018-.248-.11-.174 0 0" style="fill:#f1faee;fill-opacity:1;fill-rule:nonzero;stroke:none" transform="translate(235.188 534.699)"/><path d="m0 0-.662-.514c-.073-.056-.146-.065-.211.009l-.174.193c-.065.073-.028.156.018.202L.257 1.139h.248c.092 0 .166-.083.166-.175v-5.897c0-.092-.074-.174-.166-.174H.174A.173.173 0 0 0 0-4.933V0Z" style="fill:#f1faee;fill-opacity:1;fill-rule:nonzero;stroke:none" transform="translate(246.167 538.842)"/><path d="M0 0c-.136.02-.268.039-.386.058-.042.052-.167.26-.167.882v8.996c0 .958.19 1.003.555 1.003h.329c1.871 0 2.943-1.006 2.943-2.759 0-1.836-1.046-2.932-2.799-2.932H.213v-.146c0-.018.002-.434.166-.705l.042-.07h.137c3.153 0 5.191 1.521 5.191 3.874 0 3.183-3.498 3.658-5.583 3.658H-4.51v-.825l.112-.027c.386-.09.93-.173 1.292-.214.041-.05.161-.247.161-.857V.94c0-.638-.131-.84-.163-.882C-3.227.039-3.36.02-3.498 0c-.318-.047-.646-.094-.9-.154L-4.51-.18v-.826h5.522v.826L.9-.154C.646-.094.317-.047 0 0" style="fill:#f1faee;fill-opacity:1;fill-rule:nonzero;stroke:none" transform="translate(97.527 515.454)"/><path d="M0 0h-4.082v-.856l.313.001c.752 0 1.52-.127 1.52-1.069v-7.245L-9.754-.053-9.797 0h-2.975v-.899h.146c.29 0 1.276-.843 1.625-1.453v-8.589c0-.942-.628-1.069-1.243-1.069l-.281.001v-.856h4.308v.856l-.312-.001c-.752 0-1.521.127-1.521 1.069v7.505l7.732-9.376.044-.053h.977v10.941c0 .942.628 1.069 1.242 1.069L0-.856V0Z" style="fill:#f1faee;fill-opacity:1;fill-rule:nonzero;stroke:none" transform="translate(127 527.313)"/><path d="m0 0-.003.143h-10.286l-.004-.141c0-.013-.043-1.279-.245-2.318l-.024-.124.119-.042c.016-.005.408-.139.68-.116l.115.01.016.115c.075.509.402 1.695 1.833 1.695h1.456v-9.998c0-.638-.131-.84-.163-.882-.119-.019-.252-.038-.39-.058-.317-.047-.645-.094-.9-.154l-.112-.026v-.826h5.523v.826l-.113.026c-.254.06-.582.107-.899.154-.137.02-.268.039-.387.058-.042.052-.166.26-.166.882v9.998h1.498c1.38 0 1.712-1.186 1.791-1.697l.019-.113.114-.01s.307-.022.68.117l.114.042-.021.12C.243-2.306.02-.996 0 0" style="fill:#f1faee;fill-opacity:1;fill-rule:nonzero;stroke:none" transform="translate(138.013 527.17)"/><path d="m0 0 .113-.026c.386-.091.929-.173 1.292-.215.04-.05.16-.247.16-.857v-3.734h-6.339v3.734c0 .629.127.819.155.856.363.042.909.125 1.297.216l.113.026v.826h-5.523V0l.113-.026c.386-.091.929-.173 1.292-.215.041-.05.16-.247.16-.857v-8.996c0-.637-.13-.84-.162-.881l-.39-.059a11.775 11.775 0 0 1-.9-.153l-.113-.027v-.825h5.523v.825l-.113.027a11.83 11.83 0 0 1-.899.153c-.136.02-.268.039-.386.058-.043.053-.167.26-.167.882v4.341h6.339v-4.341c0-.638-.131-.84-.163-.881a27.947 27.947 0 0 0-.39-.059 11.744 11.744 0 0 1-.899-.153L0-11.214v-.825h5.523v.825l-.113.027c-.253.059-.582.107-.899.153-.136.02-.268.039-.386.058-.043.053-.167.26-.167.882v8.996c0 .629.127.819.155.856.363.042.909.125 1.297.216L5.523 0v.826H0V0Z" style="fill:#f1faee;fill-opacity:1;fill-rule:nonzero;stroke:none" transform="translate(147.527 526.487)"/><path d="m0 0-.122.007-.028-.119c-.043-.182-.206-.708-.438-.952-.368-.389-.876-.54-1.809-.54h-1.936c-.446 0-.739.072-.739 1.025v4.124h2.387c.508 0 .632-.272.698-1.531l.008-.149.861.065v4.194l-.861.065-.008-.15c-.065-1.338-.17-1.573-.698-1.573h-2.387V9.42h2.078c.744 0 1.353-.236 1.631-.633.229-.32.368-.856.369-.862l.027-.1.103-.009s.308-.021.68.117l.118.044-.025.122c-.002.011-.225 1.104-.244 2.098l-.003.143H-9.03v-.825l.113-.027c.385-.09.925-.172 1.287-.214.039-.05.138-.221.165-.684V-.766c-.028-.472-.134-.649-.168-.695-.118-.019-.249-.038-.385-.058-.317-.047-.645-.094-.899-.153l-.113-.027v-.826H.506l.003.143c.02.93.242 2.088.244 2.1l.023.116-.109.046C.444-.026.045-.002 0 0" style="fill:#f1faee;fill-opacity:1;fill-rule:nonzero;stroke:none" transform="translate(163.29 516.972)"/><path d="M0 0c1.19.531 2.682 1.577 3.304 2.055l.057.044v.445l-.767 1.041L-.543.515l.438-.562L0 0Z" style="fill:#f1faee;fill-opacity:1;fill-rule:nonzero;stroke:none" transform="translate(158.132 527.792)"/><path d="M0 0c-3.652 0-6.407-2.887-6.407-6.714 0-3.852 2.635-6.541 6.407-6.541 3.748 0 6.365 2.689 6.365 6.541C6.365-2.887 3.629 0 0 0m0-12.291c-1.012 0-1.842.322-2.467.958-.916.934-1.38 2.53-1.341 4.616.024 1.35.369 5.753 3.808 5.753 2.807 0 3.808-2.971 3.808-5.75 0-5.034-2.663-5.577-3.808-5.577" style="fill:#f1faee;fill-opacity:1;fill-rule:nonzero;stroke:none" transform="translate(170.881 527.53)"/><path d="m0 0 .312.001c.752 0 1.521-.127 1.521-1.069v-7.245L-5.672.803l-.044.053h-2.975v-.899h.146c.291 0 1.277-.843 1.625-1.453v-8.59c0-.941-.628-1.068-1.242-1.068l-.281.001v-.856h4.308v.856l-.313-.001c-.752 0-1.52.127-1.52 1.068v7.506l7.731-9.376.044-.053h.977v10.941c0 .942.628 1.069 1.243 1.069L4.308 0v.856H0V0Z" style="fill:#f1faee;fill-opacity:1;fill-rule:nonzero;stroke:none" transform="translate(186.365 526.457)"/><path d="M0 0c-1.295.822-2.519 1.599-2.519 2.987 0 1.113.963 1.696 1.913 1.696 1.103 0 1.869-.747 2.101-2.047l.018-.097.096-.021c.185-.039.593-.003.604-.002l.123.015.091 2.404-.078.043c-.831.461-1.964.626-2.749.626-2.071 0-4.162-1.105-4.162-3.572 0-1.978 1.486-2.936 2.924-3.863C-.356-2.657.855-3.438.855-4.883c0-1.394-1.063-1.891-2.058-1.891-1.506 0-2.569.903-2.842 2.416l-.02.109-.11.01c-.236.023-.58.001-.58.001l-.143-.01.007-.143c0-.009.042-.909.165-2.475l.006-.077.066-.038c1.057-.621 2.461-.714 3.204-.714 2.177 0 4.492 1.312 4.492 3.745C3.042-1.931 1.495-.949 0 0" style="fill:#f1faee;fill-opacity:1;fill-rule:nonzero;stroke:none" transform="translate(201.738 521.926)"/><path d="M0 0c-3.653 0-6.407-2.887-6.407-6.714 0-3.852 2.635-6.541 6.407-6.541 3.748 0 6.365 2.689 6.365 6.541C6.365-2.887 3.629 0 0 0m0-12.291c-1.013 0-1.843.322-2.467.958-.916.934-1.38 2.53-1.341 4.616C-3.784-5.367-3.44-.964 0-.964c2.807 0 3.808-2.971 3.808-5.75 0-5.034-2.663-5.577-3.808-5.577" style="fill:#f1faee;fill-opacity:1;fill-rule:nonzero;stroke:none" transform="translate(212.005 527.53)"/><path d="M0 0c-3.652 0-6.407-2.887-6.407-6.714 0-3.852 2.635-6.541 6.407-6.541 3.748 0 6.366 2.689 6.366 6.541C6.366-2.887 3.629 0 0 0m0-12.291c-1.012 0-1.842.322-2.466.958-.917.934-1.381 2.53-1.342 4.616.024 1.35.369 5.753 3.808 5.753 2.807 0 3.808-2.971 3.808-5.75 0-5.034-2.663-5.577-3.808-5.577" style="fill:#f1faee;fill-opacity:1;fill-rule:nonzero;stroke:none" transform="translate(248.352 527.53)"/><path d="m0 0 .312.001c.752 0 1.521-.127 1.521-1.069v-7.245L-5.672.803l-.044.053h-2.975v-.899h.146c.291 0 1.276-.843 1.625-1.453v-8.59c0-.941-.628-1.068-1.242-1.068l-.282.001v-.856h4.309v.856l-.313-.001c-.752 0-1.521.127-1.521 1.068v7.506l7.732-9.376.044-.053h.977v10.941c0 .942.628 1.069 1.243 1.069L4.308 0v.856H0V0Z" style="fill:#f1faee;fill-opacity:1;fill-rule:nonzero;stroke:none" transform="translate(263.837 526.457)"/><path d="M0 0c-.223.094-.622.117-.667.12l-.121.006-.029-.118c-.001-.007-.159-.66-.437-.952-.369-.389-.876-.54-1.809-.54h-1.936c-.447 0-.74.071-.74 1.025v4.124h2.387c.508 0 .632-.272.699-1.531l.008-.149.86.065v4.194l-.861.065-.007-.15c-.066-1.338-.171-1.573-.699-1.573h-2.387v4.953h2.078c.744 0 1.354-.236 1.632-.632.228-.32.367-.856.368-.862l.027-.1.104-.009s.307-.021.68.117l.118.043-.026.123c-.002.011-.224 1.104-.244 2.098l-.003.143h-8.692v-.825l.113-.027c.385-.09.925-.172 1.288-.214.039-.05.138-.222.165-.684V-.646c-.028-.472-.135-.649-.169-.695-.118-.02-.249-.038-.384-.058-.318-.047-.646-.094-.9-.154l-.113-.026v-.826h9.536l.003.143c.02.93.242 2.088.245 2.1l.022.116L0 0Z" style="fill:#f1faee;fill-opacity:1;fill-rule:nonzero;stroke:none" transform="translate(292.046 516.853)"/><path d="M0 0c-.112.015-.21.027-.283.04-.037.036-.162.183-.334.651l-4.148 11.296-.036.096h-.102c-.302 0-1.05-.127-1.32-.307l-.039-.026L-10.364.758c-.344-.905-.959-.905-1.453-.905h-.146v-.858h4.214v.858h-.146c-.57 0-1.279 0-1.48.288-.079.115-.077.287.007.513l1.162 3.12h3.902L-3.162.655c.082-.223.084-.385.006-.497-.142-.202-.577-.305-1.293-.305h-.146v-.858H.746v.885A9.236 9.236 0 0 1 0 0m-7.871 4.697 1.626 4.404 1.607-4.404h-3.233z" style="fill:#f1faee;fill-opacity:1;fill-rule:nonzero;stroke:none" transform="translate(112.84 515.426)"/><path d="M0 0c-.057 0-.299.058-.423.133-.594.336-1.14 1.208-1.718 2.131-.58.924-1.177 1.876-1.886 2.376 1.724.335 3.554 1.471 3.554 3.729 0 3.189-3.505 3.666-5.595 3.666h-4.686v-.828l.112-.026a12.94 12.94 0 0 1 1.295-.215c.041-.05.161-.247.161-.859V1.092c0-.639-.131-.842-.163-.883A28.197 28.197 0 0 0-9.74.15c-.318-.047-.647-.094-.902-.154l-.112-.026v-.828h5.534v.828l-.113.026c-.254.06-.583.107-.902.154-.136.02-.268.039-.386.058-.043.053-.167.261-.167.884v3.394h.204c.714 0 1.289-1.22 1.846-2.4C-4.056.639-3.35-.858-2.188-.858H.057V0H0Zm-5.758 5.409h-1.03v4.698c0 .96.19 1.005.555 1.005h.33c1.875 0 2.95-1.008 2.95-2.765 0-1.839-1.049-2.938-2.805-2.938" style="fill:#f1faee;fill-opacity:1;fill-rule:nonzero;stroke:none" transform="translate(229.965 515.279)"/><path d="M0 0c1.07.424 2.03 1.463 2.03 2.666 0 2.139-1.628 3.318-4.583 3.318h-5.1v-.828l.113-.026a12.94 12.94 0 0 1 1.295-.215c.041-.05.161-.247.161-.859v-9.015c0-.639-.131-.842-.163-.883a30.68 30.68 0 0 0-.391-.059c-.29-.042-.585-.086-.828-.138v-.87h5.883c3.394 0 4.604 1.916 4.604 3.709C3.021-1.426 1.604-.324 0 0m-3.687 4.056c0 .968.031 1.005.267 1.005h.557c2.239 0 2.413-1.834 2.413-2.395 0-1.633-.881-2.461-2.619-2.461h-.618v3.851zm1.546-10.042h-.825c-.467 0-.721.164-.721 1.027v4.242h.948c2.135 0 3.218-.909 3.218-2.7 0-1.608-.98-2.569-2.62-2.569" style="fill:#f1faee;fill-opacity:1;fill-rule:nonzero;stroke:none" transform="translate(238.172 521.33)"/><path d="M0 0v-.858l.313.001c.753 0 1.524-.127 1.524-1.071v-7.26L-5.684-.053-5.728 0h-2.705v-.935c.385-.162 1.19-.883 1.499-1.422v-8.608c0-.943-.63-1.07-1.245-1.07h-.282v-.857h4.317v.857h-.313c-.754 0-1.524.127-1.524 1.07v7.522l7.748-9.396.044-.053h.979v10.964c0 .944.63 1.071 1.245 1.071l.282-.001V0H0Z" style="fill:#f1faee;fill-opacity:1;fill-rule:nonzero;stroke:none" transform="translate(277.386 527.313)"/></g></svg>"""

with sld_3:
    col1 = Content()
    col1.add_text('This is an image', font_size="60%")
    col1.add_image("https://upload.wikimedia.org/wikipedia/commons/d/d5/Univers_Fractal_J.H..jpg",
                   divclass=["rounded"],
                   border="1px solid #ddd", border_radius="4px")
    sld_3.add_col(col1.render(), "col-6")

    col2 = Content()
    col2.add_text('And a svg', font_size="60%")
    col2.add_svg(svg)
    sld_3.add_col(col2.render(), "col-6")

# A simple Plotly chart
import plotly.express as px

df = px.data.iris()
fig = px.scatter(df, x="sepal_width", y="sepal_length",
                 color="species", size="petal_length", hover_data=["petal_width"])

fig.update_layout(autosize=False, width=900, height=500)

sld_4 = Container()
with sld_4:
    row1 = Content()
    row1.add_heading(text="Plotly example", tag="h2", )
    j = fig.to_json()
    row1.add_plotly(json=j)
    sld_4.add_col(row1.render(), "col-sm-12")

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
    row1 = Content()
    row1.add_heading(text="Altair example", tag="h2", )
    j = chart.to_json()
    row1.add_altair(json=j)
    sld_5.add_col(row1.render(), "col-sm-12")

# Create a simple slide with a center subtitle
sld_6 = Container(center=True)
with sld_6:
    row1 = Content()
    row1.add_heading(text="A fit and centered text", tag="h3", divclass=['r-fit-text'])
    sld_6.add_col(row1.render(), "col-12", text_align='center')

# Create a new presentation
presentation = Presentation()

# Add the title slide to the presentation
slides = [sld_0, sld_1, sld_2, sld_3, sld_4, sld_5, sld_6]
presentation.add_slide(slides)

# Render the presentation as an HTML file. You can pass the reveal.js theme
html = presentation.render_presentation(theme='moon')

with open("readme_example.html", "w") as f:
    f.write(html)
