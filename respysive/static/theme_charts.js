// Applies a respysive theme to charts drawn in the browser. Defined in the
// page head, before the slides, as window.respysiveTheme. `theme` holds the
// palette, font, and text colour of the theme.
window.respysiveTheme = (function (theme) {
  // Plotly's default colours (plotly templates, then plotly.js defaults):
  // a trace using one of them takes the theme colour of the same rank
  var DEFAULTS = [
    ['#636efa', '#ef553b', '#00cc96', '#ab63fa', '#ffa15a', '#19d3f3', '#ff6692', '#b6e880', '#ff97ff', '#fecb52'],
    ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
  ];

  function swap(color) {
    if (typeof color !== 'string') return color;
    var c = color.toLowerCase();
    for (var k = 0; k < DEFAULTS.length; k++) {
      var i = DEFAULTS[k].indexOf(c);
      // beyond the theme's colours, keep the original: never cycle
      if (i >= 0) return i < theme.palette.length ? theme.palette[i] : color;
    }
    return color;
  }

  function swapAll(value) {
    return Array.isArray(value) ? value.map(swap) : swap(value);
  }

  function plotly(figure) {
    (figure.data || []).forEach(function (trace) {
      if (trace.marker) {
        trace.marker.color = swapAll(trace.marker.color);
        if (trace.marker.colors) trace.marker.colors = swapAll(trace.marker.colors);
      }
      if (trace.line) trace.line.color = swap(trace.line.color);
      if (trace.fillcolor) trace.fillcolor = swap(trace.fillcolor);
    });
    var layout = figure.layout = figure.layout || {};
    layout.template = layout.template || {};
    var base = layout.template.layout = layout.template.layout || {};
    base.colorway = theme.palette.slice();
    if (layout.colorway) layout.colorway = swapAll(layout.colorway);
    base.font = Object.assign({}, base.font, { family: theme.font, color: theme.color });
    // the default "plotly" template draws on grey with white grid lines:
    // draw on the slide instead, with light grid lines
    if (String(base.plot_bgcolor).toLowerCase() === '#e5ecf6') {
      base.plot_bgcolor = 'rgba(0,0,0,0)';
      ['xaxis', 'yaxis'].forEach(function (name) {
        var ax = base[name];
        if (ax && String(ax.gridcolor).toLowerCase() === 'white') ax.gridcolor = '#e5e7eb';
        if (ax && String(ax.zerolinecolor).toLowerCase() === 'white') ax.zerolinecolor = '#d1d5db';
      });
    }
    if (String(base.paper_bgcolor).toLowerCase() === 'white') {
      base.paper_bgcolor = 'rgba(0,0,0,0)';
      // the mode bar takes the paper colour, half transparent: keep it light
      layout.modebar = Object.assign({ bgcolor: 'rgba(255,255,255,0.6)' }, layout.modebar);
    }
    return figure;
  }

  var axis = { labelColor: theme.color, titleColor: theme.color, labelFont: theme.font, titleFont: theme.font };
  var vega = {
    background: 'transparent',
    font: theme.font,
    range: { category: theme.palette },
    axis: axis,
    legend: { labelColor: theme.color, titleColor: theme.color, labelFont: theme.font, titleFont: theme.font },
    title: { color: theme.color, font: theme.font }
  };

  return { name: theme.name, palette: theme.palette, plotly: plotly, vega: vega };
})(RESPYSIVE_THEME);
