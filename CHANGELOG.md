# Changelog

## 2.0.3

- Plotly charts are drawn whatever their text contains: a double quote, a line
  break, a backslash or `</script>` in a title or a label stopped the chart,
  and typographic apostrophes were replaced by straight ones.
- Formulas written with `$…$` and `$$…$$` reach MathJax as written: Markdown
  read `*` and `_` as emphasis and removed the backslash of `\\` and `\{`.
- Amounts are no longer read as formulas: in "from $5 to $10" the dollars
  stay text. `$…$` is a formula when no space follows the first `$` or
  precedes the last one, and no digit follows the last one; `\$` writes a
  dollar.
- PowerPoint export: a Plotly chart with a log axis or a filled area stays a
  picture instead of becoming a native chart with linear axes and plain
  lines; missing values (NaN) no longer turn a whole chart into a picture;
  a colour the exporter cannot read no longer puts a native chart under the
  picture of the same chart.
- MapLibre maps: `separatorSymbol` is applied to the legend of a horizontal
  choropleth; popups accept property names and values holding `$`, `(` or
  other pattern characters; a feature with `"properties": null` no longer
  stops a data join; a circle without `value` is drawn.
- Keyboard shortcuts work with Caps Lock on.
- Cards: a card holding only a title no longer gives its `title-only` class to
  the next cards, the style dictionaries passed to `add_card` are left as
  given, and a Matplotlib figure or a Plotly dict placed in a card keeps its
  size (the figure also keeps its proportions in the card).
- Style values holding single quotes, such as
  `font_family="'Open Sans', sans-serif"`, no longer break the attribute.
- `add_custom_content` accepts library names that are not JavaScript
  identifiers (`chart.js`), and the same `config` can be used for several
  charts.
- `content_types` is followed for `'image'`, `'video'` and `'altair'` when the
  content would not be detected as such (URL without extension, specification
  without `$schema`). A sentence that names a file is text, not an image.
- Images given as URLs: the type is read from the path without its query
  string (`logo.svg?v=2`), or from the server when the path has no extension,
  and downloads time out after 60 seconds.
- `filter_geojson_bbox` filters every geometry type by its extent; it kept all
  lines and polygons. Features with `"properties": null` are accepted.
- Shared GeoJSON is stored in `<script type="application/json">` elements
  instead of hidden `<div>`: properties holding `<` or `&` are read back as
  written.
- `set_local_css_urls({'theme': …})` is applied, as documented.
- `add_split_title_page(full_height=True, background_image=…)` shows the image.
- `to_html(libraries="plotly")` accepts a single name.
- Matplotlib figures are no longer rendered a second time as 300 dpi PNG when
  they are added to a slide; nothing read that copy.

## 2.0.2

- `shared_data_ids` accepts Plotly figures, not only dicts, and leaves their
  GeoJSON out of the page: the charts read the copy stored once with
  `add_global_geojson`, on every trace placed by `locations`.
- Saving a deck raises an error when a Plotly chart reads a shared GeoJSON
  that was never added, as for MapLibre maps, instead of printing a message.
- The mappyng map of the documentation and of the showcase draws the European
  countries in the background, the overseas departments in insets, and
  contrasted borders.
- New gallery example: one GeoJSON shared by mappyng, Plotly, and MapLibre maps.
- The documentation loads its decks from files: Plotly tile maps stayed blank
  in the `srcdoc` iframes used before.
- The slide titles of the examples state what the slide shows, with figures
  computed from the data, and each map gives its source. A picture drawn from
  the Gapminder data replaces the fractal image.

## 2.0.1

- mappyng is published on PyPI as `mappyng-svg`: the documentation, the gallery
  and the showcase deck now draw a mappyng map, and `pip install
  "respysive-slide[maps]"` installs it.
- Two old mappyng examples that read files from a local path are removed.

## 2.0.0

Version 2 replaces Reveal.js with its own slide runtime. Scripts written for
version 1 run unchanged in most cases; the
[migration guide](docs/migration/v1_to_v2.rst) lists what differs.

### New

- Own slide runtime: horizontal and vertical navigation, fragments, speaker view
  (`S`), keyboard shortcuts, exposed in JavaScript as `window.respysive`.
- Content taller than the slide is fitted to its height
  (`save_html(overflow="visible")` restores the version 1 behaviour).
- Nested layouts with `Row` and `Column`, and fragments on every content method.
- PDF export (`save_pdf`) and PowerPoint export (`save_pptx`) from the layout
  rendered by headless Chromium. PowerPoint slides keep editable text, and simple
  Plotly charts become native, editable charts.
- Offline decks (`offline=True`), with Plotly geo base maps embedded.
- Themes `sober`, `science` and `corporate`, applied to Plotly and Altair charts.
- `Presentation.check()`: reports text scale per slide, pictures in a PowerPoint
  export, and network hosts.
- Direct support for mappyng maps, Altair chart objects, videos, and objects with
  a `_repr_html_` method.
- Unknown `content_type` values raise an error instead of being ignored.

### Changed

- Python 3.10 or later is required.
- Only the libraries a deck uses are loaded.
- The `margin` option of `save_html` defaults to 0.04 instead of 0.05.
- Reveal.js API calls (`Reveal.slide`, `Reveal.on`…) must use `window.respysive`;
  Reveal.js plugins and options without a `save_html` counterpart are not available.
- Documentation rewritten with Sphinx, with live examples.

### Removed

- Geoviz and Bertin maps: mappyng covers static thematic maps, MapLibre web maps.
- The Python-side PowerPoint layout, its `ChartConverter`, and the kaleido,
  cairosvg and vl-convert dependencies. `save_pptx` now needs Chromium.
