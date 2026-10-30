# Changelog

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
