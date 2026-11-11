/*
 * Describe the laid-out slides for the PPTX exporter (respysive.exporters).
 *
 * Evaluated by Playwright on a deck in print mode. Returns one entry per
 * slide with its items in painting order, positions in CSS pixels relative
 * to the slide:
 *   box      background / border of an element      -> native shape
 *   text     block of inline text                   -> native text box
 *   list     ul / ol                                -> text box with bullets
 *   picture  chart, map, image, equation, icon      -> screenshot (data-rs-shot)
 */
() => {
  const GRAPHICS = 'img, svg, canvas, iframe, video, object, .js-plotly-plot, .vega-embed, ' +
    'mjx-container[display="true"], .maplibregl-map';
  const ICONS = 'i[class*="fa-"], span[class*="fa-"]';
  let shot = 0;

  const zoomOf = (el) => el.currentCSSZoom || 1;
  const isGraphic = (el) => el.matches(GRAPHICS);
  const isIcon = (el) => el.matches(ICONS);
  // inline-block, inline-flex… form their own box (Reveal themes make lists inline-block)
  const isBlock = (el) => getComputedStyle(el).display !== 'inline';

  function hidden(el) {
    const cs = getComputedStyle(el);
    return cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity) === 0 ||
      el.matches('aside.notes, .rs-bg, script, style, template');
  }

  function rgba(color) {
    const m = color.match(/rgba?\(([^)]+)\)/);
    if (!m) return null;
    const p = m[1].split(/[\s,/]+/).filter(Boolean).map(Number);
    const a = p.length > 3 ? p[3] : 1;
    return a === 0 ? null : { r: p[0], g: p[1], b: p[2], a: a };
  }

  function makeRelative(slideRect) {
    return (r) => {
      const x = Math.max(r.left, slideRect.left), y = Math.max(r.top, slideRect.top);
      const right = Math.min(r.right, slideRect.right), bottom = Math.min(r.bottom, slideRect.bottom);
      if (right - x < 1 || bottom - y < 1) return null;
      return {
        x: x - slideRect.left, y: y - slideRect.top, w: right - x, h: bottom - y,
        // document coordinates of the visible part, for page screenshots
        pageX: x + window.scrollX, pageY: y + window.scrollY
      };
    };
  }

  function textStyle(el) {
    const cs = getComputedStyle(el);
    const link = el.closest('a[href]');
    return {
      font: cs.fontFamily.split(',')[0].replace(/["']/g, '').trim(),
      size: parseFloat(cs.fontSize) * zoomOf(el),
      bold: parseInt(cs.fontWeight, 10) >= 600,
      italic: cs.fontStyle === 'italic' || cs.fontStyle === 'oblique',
      underline: cs.textDecorationLine.includes('underline'),
      strike: cs.textDecorationLine.includes('line-through'),
      color: rgba(cs.color),
      caps: cs.textTransform === 'uppercase',
      spacing: cs.letterSpacing === 'normal' ? 0 : parseFloat(cs.letterSpacing) * zoomOf(el),
      sup: cs.verticalAlign === 'super' || el.tagName === 'SUP',
      sub: cs.verticalAlign === 'sub' || el.tagName === 'SUB',
      href: link ? link.href : null
    };
  }

  function paragraphStyle(el) {
    const cs = getComputedStyle(el);
    const size = parseFloat(cs.fontSize);
    const lineHeight = cs.lineHeight === 'normal' ? size * 1.2 : parseFloat(cs.lineHeight);
    return {
      align: { center: 'center', right: 'right', end: 'right', justify: 'justify' }[cs.textAlign] || 'left',
      lineHeight: lineHeight * zoomOf(el),
      pre: cs.whiteSpace.startsWith('pre')
    };
  }

  // Inline content of a block: runs of styled text; inline graphics and icons
  // are reported as pictures, nested blocks are left to the caller.
  function collectRuns(node, out, pictures, pre) {
    node.childNodes.forEach((child) => {
      if (child.nodeType === Node.TEXT_NODE) {
        const text = pre ? child.textContent : child.textContent.replace(/\s+/g, ' ');
        if (text) out.runs.push(Object.assign({ text: text }, textStyle(child.parentElement)));
        if (child.textContent.trim()) out.textNodes.push(child);
      } else if (child.nodeType === Node.ELEMENT_NODE && !hidden(child)) {
        if (child.tagName === 'BR') out.runs.push({ br: true });
        else if (isGraphic(child) || isIcon(child)) pictures.push(child);
        else if (!isBlock(child)) collectRuns(child, out, pictures, pre);
      }
    });
  }

  function hasInlineText(el) {
    return Array.prototype.some.call(el.childNodes, (child) =>
      (child.nodeType === Node.TEXT_NODE && child.textContent.trim()) ||
      (child.nodeType === Node.ELEMENT_NODE && !isBlock(child) && !hidden(child) &&
        !isGraphic(child) && !isIcon(child) && child.textContent.trim()));
  }

  // CSS white-space collapsing across runs: no space at line starts and ends,
  // never two spaces in a row (preformatted text is kept as is)
  function trimRuns(runs, pre) {
    const kept = () => runs.filter((r) => r.br || r.text);
    if (pre) return kept();
    let previous = '';
    runs.forEach((r) => {
      if (r.br) previous = '';
      else {
        if (previous.endsWith(' ')) r.text = r.text.replace(/^ +/, '');
        if (r.text) previous = r.text;
      }
    });
    runs = kept();
    // trim each line, delimited by <br>
    let line = [];
    runs.concat([{ br: true }]).forEach((r) => {
      if (!r.br) return line.push(r);
      if (line.length) {
        line[0].text = line[0].text.replace(/^ +/, '');
        line[line.length - 1].text = line[line.length - 1].text.replace(/ +$/, '');
      }
      line = [];
    });
    return kept();
  }

  function textBounds(nodes) {
    let left = Infinity, top = Infinity, right = -Infinity, bottom = -Infinity;
    const lines = new Set();
    nodes.forEach((n) => {
      // measure from the first to the last visible character: collapsed
      // spaces at the edges are not exported
      const text = n.textContent;
      const start = text.search(/\S/);
      if (start < 0) return;
      const range = document.createRange();
      range.setStart(n, start);
      range.setEnd(n, text.replace(/\s+$/, '').length);
      Array.prototype.forEach.call(range.getClientRects(), (r) => {
        if (r.width < 0.5) return;
        left = Math.min(left, r.left); top = Math.min(top, r.top);
        right = Math.max(right, r.right); bottom = Math.max(bottom, r.bottom);
        lines.add(Math.round(r.top));
      });
    });
    return { left: left, top: top, right: right, bottom: bottom, lines: lines.size };
  }

  // Marker of a list item, null when none is drawn (e.g. Bootstrap list-group
  // items are display: block)
  function bulletOf(li, list) {
    const cs = getComputedStyle(li);
    const type = cs.listStyleType;
    if (cs.display !== 'list-item' || type === 'none') return null;
    if (list.tagName === 'OL' || /decimal|alpha|roman/.test(type)) {
      const scheme = { 'lower-alpha': 'alphaLcPeriod', 'upper-alpha': 'alphaUcPeriod',
        'lower-roman': 'romanLcPeriod', 'upper-roman': 'romanUcPeriod' }[type] || 'arabicPeriod';
      return { number: scheme, start: list.start || 1 };
    }
    return { char: { circle: '◦', square: '▪' }[type] || '•' };
  }

  // Axis bounds and tick step as drawn by Plotly, widened to whole ticks so
  // that PowerPoint labels stay round
  function numericRange(axis) {
    if (!axis || !axis.range || axis.type !== 'linear' || typeof axis.dtick !== 'number') return null;
    const range = axis.range.map(Number);
    const step = axis.dtick;
    if (!range.every(isFinite) || !(step > 0)) return null;
    return {
      min: Math.floor(Math.min(range[0], range[1]) / step) * step,
      max: Math.ceil(Math.max(range[0], range[1]) / step) * step,
      step: step
    };
  }

  // Plotly figure simple enough for a native PowerPoint chart, else null
  function plotlyChart(gd) {
    const layout = gd._fullLayout;
    const traces = (gd._fullData || []).filter((t) => t.visible === true);
    if (!layout || !traces.length) return null;
    const type = traces[0].type;
    const supported = { bar: 1, scatter: 1, pie: 1 }[type];
    const simple = traces.every((t) => t.type === type && (type === 'pie' || (t.xaxis === 'x' && t.yaxis === 'y')));
    const points = traces.reduce((n, t) => n + ((type === 'pie' ? t.values : t.y) || []).length, 0);
    // per-point sizes or colours (bubbles, colour scales) have no native equivalent
    const perPoint = (v) => Array.isArray(v) || ArrayBuffer.isView(v);
    const varying = type !== 'pie' && traces.some((t) => t.marker && (perPoint(t.marker.size) || perPoint(t.marker.color)));
    // PowerPoint charts drawn here have linear axes and plain lines: log axes
    // and filled areas would show something else than the slide
    const log = type !== 'pie' && [layout.xaxis, layout.yaxis].some((axis) => axis && axis.type === 'log');
    const filled = type === 'scatter' && traces.some((t) => t.fill && t.fill !== 'none');
    if (!supported || !simple || varying || log || filled || points === 0 || points > 1000) return null;
    if (type === 'pie' && traces.length > 1) return null;

    // titles come from the user layout: Plotly fills empty ones in
    // _fullLayout with "Click to enter … title" prompts
    const userLayout = gd.layout || {};
    const text = (title) => (typeof title === 'string' ? title : (title && title.text) || '');
    const color = (c) => (typeof c === 'string' ? c : null);
    const list = (values) => Array.prototype.slice.call(values || []);
    const series = traces.map((t) => ({
      name: t.name || '',
      x: list(t.x),
      y: list(t.y),
      color: color(t.marker && t.marker.color) || color(t.line && t.line.color),
      markerSize: t.marker && typeof t.marker.size === 'number' ? t.marker.size : null,
      mode: t.mode || ''
    }));
    const chart = {
      type: type,
      title: text(userLayout.title),
      font: { family: layout.font.family.split(',')[0].replace(/["']/g, ''), size: layout.font.size, color: layout.font.color },
      legend: layout.showlegend !== false && (type === 'pie' || traces.length > 1),
      xTitle: text((userLayout.xaxis || {}).title),
      yTitle: text((userLayout.yaxis || {}).title),
      xRange: numericRange(layout.xaxis),
      yRange: numericRange(layout.yaxis),
      series: series
    };
    if (type === 'pie') {
      // slices in the order PowerPoint draws them, clockwise from 12 o'clock;
      // Plotly angles run clockwise from 12 o'clock too, in either direction
      const turn = 2 * Math.PI;
      const start = (d) => ((Math.min(d.startangle, d.stopangle) % turn) + turn) % turn;
      const slices = list(gd.calcdata[0]).filter((d) => !d.hidden).sort((a, b) => start(a) - start(b));
      chart.labels = slices.map((d) => String(d.label));
      chart.values = slices.map((d) => d.v);
      chart.colors = slices.map((d) => d.color);
    } else if (type === 'bar') {
      chart.horizontal = traces[0].orientation === 'h';
      // Plotly Express gives each colour its own offsetgroup: side by side
      // bars, even in 'relative' mode
      const groups = new Set(traces.map((t) => t.offsetgroup || ''));
      const sideBySide = layout.barmode === 'group' || (groups.size === traces.length && !groups.has(''));
      chart.stacked = !sideBySide && (layout.barmode === 'stack' || layout.barmode === 'relative');
    } else {
      const numeric = traces.every((t) => list(t.x).every((v) => typeof v === 'number'));
      chart.xy = numeric && layout.xaxis.type !== 'category';
    }
    return chart;
  }

  // what a picture shows, for the export report
  function describe(el) {
    if (el.matches('.js-plotly-plot')) return 'Plotly chart';
    if (el.matches('.vega-embed')) return 'Altair chart';
    if (el.matches('mjx-container')) return 'equation';
    if (el.matches('.maplibregl-map') || (el.matches('iframe') && /maplibre/i.test(el.srcdoc || ''))) {
      return 'MapLibre map';
    }
    if (isIcon(el)) return 'icon';
    return el.tagName.toLowerCase();
  }

  function slideItems(slide) {
    const items = [];
    const slideRect = slide.getBoundingClientRect();
    const rel = makeRelative(slideRect);

    function picture(el, what) {
      const box = rel(el.getBoundingClientRect());
      if (!box) return;
      el.setAttribute('data-rs-shot', ++shot);
      const chart = el.matches('.js-plotly-plot') ? plotlyChart(el) : null;
      what = what || describe(el);
      items.push(chart ? { kind: 'chart', shot: shot, box: box, chart: chart, what: what } :
        { kind: 'picture', shot: shot, box: box, what: what });
    }

    function boxOf(el) {
      if (el === slide || el.classList.contains('rs-body')) return;
      const cs = getComputedStyle(el);
      const fill = rgba(cs.backgroundColor);
      const sides = ['Top', 'Right', 'Bottom', 'Left'].map((s) => ({
        width: cs['border' + s + 'Style'] === 'none' ? 0 : parseFloat(cs['border' + s + 'Width']) * zoomOf(el),
        color: rgba(cs['border' + s + 'Color'])
      }));
      const hasBorder = sides.some((s) => s.width > 0 && s.color);
      const image = cs.backgroundImage !== 'none';
      if (!fill && !hasBorder && !image) return;
      const box = rel(el.getBoundingClientRect());
      if (!box) return;
      if (image) {
        el.setAttribute('data-rs-bg-shot', ++shot);
        items.push({ kind: 'picture', shot: shot, box: box, background: true });
      }
      items.push({
        kind: 'box', box: box, fill: image ? null : fill, sides: sides,
        radius: parseFloat(cs.borderTopLeftRadius) * zoomOf(el) || 0
      });
    }

    function textItem(el, runsSource) {
      const out = { runs: [], textNodes: [] };
      const pictures = [];
      const para = paragraphStyle(el);
      (runsSource || [el]).forEach((src) => collectRuns(src, out, pictures, para.pre));
      pictures.forEach(picture);
      const runs = trimRuns(out.runs, para.pre);
      if (!runs.some((r) => r.text && r.text.trim())) return;
      const t = textBounds(out.textNodes);
      const block = el.getBoundingClientRect();
      // single lines keep their measured width; wrapped text uses the block width
      const right = t.lines > 1 ? Math.max(t.right, block.right) : t.right;
      const box = rel({ left: t.left, top: t.top, right: right, bottom: t.bottom });
      if (box) items.push({ kind: 'text', box: box, paragraphs: [{ style: para, runs: runs }] });
    }

    function listItem(list) {
      const paragraphs = [];
      const nodes = [];
      let previousBottom = null;
      (function walk(ul, level) {
        Array.prototype.forEach.call(ul.children, (li) => {
          if (li.tagName !== 'LI' || hidden(li)) return;
          const out = { runs: [], textNodes: [] };
          const pictures = [];
          const para = paragraphStyle(li);
          const nested = [];
          Array.prototype.forEach.call(li.childNodes, (child) => {
            if (child.nodeType === Node.ELEMENT_NODE && /^(UL|OL)$/.test(child.tagName)) nested.push(child);
            else if (child.nodeType === Node.ELEMENT_NODE && isBlock(child) && !isGraphic(child)) {
              if (out.runs.length) out.runs.push({ br: true });
              collectRuns(child, out, pictures, para.pre);
            } else {
              collectRuns({ childNodes: [child] }, out, pictures, para.pre);
            }
          });
          pictures.forEach(picture);
          const r = li.getBoundingClientRect();
          paragraphs.push({
            style: para, runs: trimRuns(out.runs, para.pre), level: level, bullet: bulletOf(li, ul),
            indent: r.left - list.getBoundingClientRect().left,
            spaceBefore: previousBottom === null ? 0 : Math.max(0, r.top - previousBottom)
          });
          nodes.push.apply(nodes, out.textNodes);
          const t = textBounds(out.textNodes);
          previousBottom = isFinite(t.bottom) ? t.bottom : r.bottom;
          nested.forEach((sub) => walk(sub, level + 1));
        });
      })(list, 0);
      if (!paragraphs.length) return;
      const t = textBounds(nodes);
      const r = list.getBoundingClientRect();
      // inline-block lists shrink to their text: use the width available around them
      const right = Math.max(r.right, list.parentElement.getBoundingClientRect().right);
      const box = rel({ left: r.left, top: isFinite(t.top) ? t.top : r.top, right: right, bottom: Math.max(r.bottom, t.bottom) });
      if (box) items.push({ kind: 'list', box: box, paragraphs: paragraphs });
    }

    function visit(el) {
      if (hidden(el)) return;
      if (isGraphic(el) || isIcon(el)) return picture(el);
      boxOf(el);
      if (/^(UL|OL)$/.test(el.tagName)) {
        // inline math cannot become text: keep such lists as pictures
        return el.querySelector('mjx-container') ? picture(el, 'list with an equation') : listItem(el);
      }
      if (isBlock(el) && hasInlineText(el)) {
        if (el.querySelector('mjx-container:not([display="true"])')) return picture(el, 'text with an equation');
        textItem(el);
        Array.prototype.forEach.call(el.children, (child) => {
          if (isBlock(child) && !isGraphic(child)) visit(child);
        });
        return;
      }
      Array.prototype.forEach.call(el.children, visit);
    }

    visit(slide);
    return items;
  }

  function background(slide) {
    const layer = slide.querySelector(':scope > .rs-bg');
    const rect = slide.getBoundingClientRect();
    const page = { x: 0, y: 0, w: rect.width, h: rect.height, pageX: rect.left + window.scrollX, pageY: rect.top + window.scrollY };
    if (layer && getComputedStyle(layer).backgroundImage !== 'none') {
      layer.setAttribute('data-rs-bg-shot', ++shot);
      return { shot: shot, box: page };
    }
    const own = layer && rgba(getComputedStyle(layer).backgroundColor);
    const slideColor = rgba(getComputedStyle(slide).backgroundColor);
    const pageColor = rgba(getComputedStyle(document.body).backgroundColor) ||
      rgba(getComputedStyle(document.documentElement).backgroundColor);
    return { color: own || slideColor || pageColor || { r: 255, g: 255, b: 255, a: 1 } };
  }

  return window.respysive.slides().map((slide) => ({
    background: background(slide),
    items: slideItems(slide),
    notes: Array.prototype.map.call(slide.querySelectorAll('aside.notes'), (n) => n.innerText.trim()).join('\n\n')
  }));
}
