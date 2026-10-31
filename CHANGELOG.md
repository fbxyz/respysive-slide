# Changelog

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
