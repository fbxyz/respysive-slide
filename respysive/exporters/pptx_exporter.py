"""PowerPoint exporter built from the layout measured in headless Chromium.

The deck is laid out by the browser exactly as on screen (fixed canvas,
overflow fitting), then each slide is described by static/pptx_extract.js
and rebuilt with native PowerPoint objects: editable text boxes and
bulleted lists, shapes for backgrounds and borders, pictures for charts,
maps, images and equations.
"""

import base64
import io
from pathlib import Path

from .base import BaseExporter
from .browser import isolate, run_in_browser

PX = 9525  # EMU per CSS pixel (96 dpi)
PT = 0.75  # points per CSS pixel

_EXTRACT_JS = (Path(__file__).parent.parent / "static" / "pptx_extract.js").read_text(encoding="utf-8")


class PptxExporter(BaseExporter):
    """Export a presentation to PowerPoint (.pptx) from its rendered layout.

    Text stays editable; simple Plotly charts (bars, lines, scatter, pies)
    become native PowerPoint charts; other charts, maps and equations become
    pictures. Slides
    have the size of the HTML slides (1280 x 720 px gives 13.333 x 7.5 in,
    PowerPoint's 16:9). Requires Playwright and Chromium.

    Args:
        presentation: respysive.Presentation object to export
        timeout: Seconds allowed for loading charts, equations and maps
        native_charts: Rebuild simple Plotly charts as editable PowerPoint
            charts; False keeps every chart as a picture of its rendering
    """

    def __init__(self, presentation, timeout: int = 60, native_charts: bool = True):
        super().__init__(presentation)
        self.timeout = timeout
        self.native_charts = native_charts

    def export(self, **kwargs):
        """Build the PowerPoint presentation.

        Args:
            **kwargs: Presentation.to_html() options (theme, width, height, …).

        Returns:
            pptx.Presentation: python-pptx presentation object.
        """
        width = kwargs.get("width", 1280)
        height = kwargs.get("height", 720)
        slides = run_in_browser(self.presentation.to_html(**kwargs), width, height, _measure, self.timeout)
        return _build(slides, width, height, self.native_charts)

    def save(self, output_path: str, **kwargs):
        """Save the presentation as a .pptx file.

        Args:
            output_path: Path of the PowerPoint file.
            **kwargs: Presentation.to_html() options (theme, width, height, …).
        """
        self.export(**kwargs).save(output_path)


def _measure(page):
    """Describe every slide, then capture the elements kept as pictures."""
    slides = page.evaluate(_EXTRACT_JS)
    for slide in slides:
        # charts are captured too, as a fallback when they cannot be native
        pictures = [item for item in slide["items"] if item["kind"] in ("picture", "chart")]
        if "shot" in slide["background"]:
            pictures.append(dict(slide["background"], background=True))
        for item in pictures:
            box = item["box"]
            clip = {"x": box["pageX"], "y": box["pageY"], "width": box["w"], "height": box["h"]}
            if item.get("background"):
                # a background alone, without the content painted over it
                element = page.query_selector(f"[data-rs-bg-shot='{item['shot']}']")
                with isolate(element, children=False):
                    png = page.screenshot(clip=clip, full_page=True, omit_background=True)
            else:
                png = page.screenshot(clip=clip, full_page=True)
            item["png"] = base64.b64encode(png).decode("ascii")
        if "shot" in slide["background"]:
            slide["background"]["png"] = pictures[-1]["png"]
    return slides


def _build(slides, width, height, native_charts=True):
    from pptx import Presentation as PptxPresentation
    from pptx.util import Emu

    prs = PptxPresentation()
    prs.slide_width = Emu(width * PX)
    prs.slide_height = Emu(height * PX)
    blank = prs.slide_layouts[6]
    for data in slides:
        slide = prs.slides.add_slide(blank)
        _background(slide, data["background"], width, height)
        for item in data["items"]:
            if item["kind"] == "chart" and not native_charts:
                _picture(slide, item)
            else:
                {"box": _box, "picture": _picture, "chart": _chart, "text": _text, "list": _text}[item["kind"]](
                    slide, item
                )
        if data["notes"]:
            slide.notes_slide.notes_text_frame.text = data["notes"]
    return prs


def _emu(value):
    from pptx.util import Emu

    return Emu(round(value * PX))


def _rgb(color):
    from pptx.dml.color import RGBColor

    return RGBColor(round(color["r"]), round(color["g"]), round(color["b"]))


def _set_alpha(fill_format, alpha):
    """Apply CSS alpha to a solid fill (PowerPoint has no rgba)."""
    if alpha >= 1:
        return
    from pptx.oxml.ns import qn

    color = fill_format._xPr.find(qn("a:solidFill"))[0]
    color.append(color.makeelement(qn("a:alpha"), {"val": str(round(alpha * 100000))}))


def _background(slide, background, width, height):
    if "png" in background:
        _add_png(slide, background["png"], {"x": 0, "y": 0, "w": width, "h": height})
    else:
        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb = _rgb(background["color"])


def _add_png(slide, png, box):
    data = io.BytesIO(base64.b64decode(png))
    return slide.shapes.add_picture(data, _emu(box["x"]), _emu(box["y"]), _emu(box["w"]), _emu(box["h"]))


def _picture(slide, item):
    _add_png(slide, item["png"], item["box"])


def _box(slide, item):
    from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE

    box = item["box"]
    rounded = item["radius"] > 0
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE,
        _emu(box["x"]),
        _emu(box["y"]),
        _emu(box["w"]),
        _emu(box["h"]),
    )
    shape.shadow.inherit = False
    if rounded:
        shape.adjustments[0] = min(0.5, item["radius"] / max(1, min(box["w"], box["h"])))
    if item["fill"]:
        shape.fill.solid()
        shape.fill.fore_color.rgb = _rgb(item["fill"])
        _set_alpha(shape.fill, item["fill"]["a"])
    else:
        shape.fill.background()

    sides = [side for side in item["sides"] if side["width"] > 0 and side["color"]]
    same = len(sides) == 4 and all(side == sides[0] for side in sides)
    if same:
        shape.line.color.rgb = _rgb(sides[0]["color"])
        shape.line.width = _emu(sides[0]["width"])
        return
    shape.line.fill.background()
    x, y, w, h = box["x"], box["y"], box["w"], box["h"]
    ends = {
        "Top": (x, y, x + w, y),
        "Right": (x + w, y, x + w, y + h),
        "Bottom": (x, y + h, x + w, y + h),
        "Left": (x, y, x, y + h),
    }
    for name, side in zip(("Top", "Right", "Bottom", "Left"), item["sides"], strict=True):
        if side["width"] > 0 and side["color"]:
            line = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, *(_emu(v) for v in ends[name]))
            line.line.color.rgb = _rgb(side["color"])
            line.line.width = _emu(side["width"])


def _text(slide, item):
    from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE

    box = item["box"]
    # a little slack against rounding; if the font installed is wider than the
    # browser's, PowerPoint shrinks the text instead of letting it overflow
    shape = slide.shapes.add_textbox(_emu(box["x"]), _emu(box["y"]), _emu(box["w"] + 2), _emu(box["h"] + 1))
    frame = shape.text_frame
    frame.word_wrap = True
    frame.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
    frame.vertical_anchor = MSO_ANCHOR.TOP
    frame.margin_left = frame.margin_right = frame.margin_top = frame.margin_bottom = 0
    for index, data in enumerate(item["paragraphs"]):
        paragraph = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
        _paragraph(paragraph, data)


def _paragraph(paragraph, data):
    from pptx.enum.text import PP_ALIGN
    from pptx.util import Pt

    style = data["style"]
    paragraph.alignment = {
        "left": PP_ALIGN.LEFT,
        "center": PP_ALIGN.CENTER,
        "right": PP_ALIGN.RIGHT,
        "justify": PP_ALIGN.JUSTIFY,
    }[style["align"]]
    paragraph.line_spacing = Pt(style["lineHeight"] * PT)
    if data.get("spaceBefore"):
        paragraph.space_before = Pt(data["spaceBefore"] * PT)
    if "level" in data:
        paragraph.level = min(data["level"], 8)
        _bullet(paragraph, data)
    for run_data in data["runs"]:
        if run_data.get("br"):
            paragraph.add_line_break()
        else:
            _run(paragraph.add_run(), run_data)


def _bullet(paragraph, data):
    from pptx.oxml.ns import qn

    p_pr = paragraph._p.get_or_add_pPr()
    bullet = data["bullet"]
    size = max((run["size"] for run in data["runs"] if not run.get("br")), default=16)
    # the marker hangs left of the text, which starts at the item's position
    hanging = min(data["indent"], size * 1.2) if bullet else 0
    p_pr.set("marL", str(round(data["indent"] * PX)))
    p_pr.set("indent", str(round(-hanging * PX)))
    if bullet is None:
        p_pr.append(p_pr.makeelement(qn("a:buNone"), {}))
    elif "number" in bullet:
        p_pr.append(p_pr.makeelement(qn("a:buAutoNum"), {"type": bullet["number"], "startAt": str(bullet["start"])}))
    else:
        p_pr.append(p_pr.makeelement(qn("a:buFont"), {"typeface": "Arial"}))
        p_pr.append(p_pr.makeelement(qn("a:buChar"), {"char": bullet["char"]}))


def _run(run, data):
    from pptx.util import Pt

    run.text = data["text"]
    font = run.font
    font.name = data["font"]
    font.size = Pt(round(data["size"] * PT * 2) / 2)
    font.bold = data["bold"]
    font.italic = data["italic"]
    font.underline = data["underline"]
    if data["color"]:
        font.color.rgb = _rgb(data["color"])
    r_pr = run._r.get_or_add_rPr()
    if data["caps"]:
        r_pr.set("cap", "all")
    if data["strike"]:
        r_pr.set("strike", "sngStrike")
    if data["spacing"]:
        r_pr.set("spc", str(round(data["spacing"] * PT * 100)))
    if data["sup"] or data["sub"]:
        r_pr.set("baseline", "30000" if data["sup"] else "-25000")
    if data["href"] and data["href"].startswith(("http://", "https://", "mailto:")):
        run.hyperlink.address = data["href"]


def _css_rgb(color):
    """RGBColor from a CSS colour ('#rgb', '#rrggbb', 'rgb()', 'rgba()'), or None."""
    from pptx.dml.color import RGBColor

    if not isinstance(color, str):
        return None
    color = color.strip()
    if color.startswith("#") and len(color) in (4, 7):
        hex_digits = color[1:] if len(color) == 7 else "".join(c * 2 for c in color[1:])
        return RGBColor.from_string(hex_digits.upper())
    if color.startswith("rgb"):
        parts = color[color.index("(") + 1 : color.index(")")].replace("/", " ").replace(",", " ").split()
        return RGBColor(*(round(float(v)) for v in parts[:3]))
    return None


def _categories(series, axis):
    """Categories of a category chart, in order of first appearance."""
    seen = {}
    for data in series:
        for value in data[axis]:
            seen.setdefault(str(value), None)
    return list(seen)


def _chart(slide, item):
    """Native PowerPoint chart from a Plotly figure, or its picture on failure."""
    try:
        _native_chart(slide, item["chart"], item["box"])
    except (ValueError, TypeError, KeyError, IndexError):
        _picture(slide, item)


def _native_chart(slide, spec, box):
    from pptx.chart.data import CategoryChartData, XyChartData
    from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_MARKER_STYLE
    from pptx.util import Pt

    kind, series = spec["type"], spec["series"]
    if kind == "pie":
        data = CategoryChartData()
        data.categories = spec["labels"]
        data.add_series(series[0]["name"], spec["values"])
        chart_type = XL_CHART_TYPE.PIE
    elif kind == "bar":
        horizontal = spec["horizontal"]
        category_axis, value_axis = ("y", "x") if horizontal else ("x", "y")
        categories = _categories(series, category_axis)
        data = CategoryChartData()
        data.categories = categories
        for s in series:
            values = dict(zip((str(c) for c in s[category_axis]), s[value_axis], strict=False))
            data.add_series(s["name"], [values.get(c) for c in categories])
        stacked = spec["stacked"]
        chart_type = {
            (False, False): XL_CHART_TYPE.COLUMN_CLUSTERED,
            (False, True): XL_CHART_TYPE.COLUMN_STACKED,
            (True, False): XL_CHART_TYPE.BAR_CLUSTERED,
            (True, True): XL_CHART_TYPE.BAR_STACKED,
        }[(horizontal, stacked)]
    else:
        lines = all("lines" in s["mode"] for s in series)
        markers = any("markers" in s["mode"] for s in series)
        if spec["xy"]:
            data = XyChartData()
            for s in series:
                points = data.add_series(s["name"])
                for x, y in zip(s["x"], s["y"], strict=False):
                    points.add_data_point(x, y)
            if not lines:
                chart_type = XL_CHART_TYPE.XY_SCATTER
            else:
                chart_type = XL_CHART_TYPE.XY_SCATTER_LINES if markers else XL_CHART_TYPE.XY_SCATTER_LINES_NO_MARKERS
        else:
            categories = _categories(series, "x")
            data = CategoryChartData()
            data.categories = categories
            for s in series:
                values = dict(zip((str(c) for c in s["x"]), s["y"], strict=False))
                data.add_series(s["name"], [values.get(c) for c in categories])
            chart_type = XL_CHART_TYPE.LINE_MARKERS if markers else XL_CHART_TYPE.LINE

    frame = slide.shapes.add_chart(chart_type, _emu(box["x"]), _emu(box["y"]), _emu(box["w"]), _emu(box["h"]), data)
    chart = frame.chart
    chart.font.size = Pt(spec["font"]["size"] * PT)
    chart.font.name = spec["font"]["family"]
    if _css_rgb(spec["font"]["color"]):
        chart.font.color.rgb = _css_rgb(spec["font"]["color"])
    chart.has_title = bool(spec["title"])
    if spec["title"]:
        chart.chart_title.text_frame.text = spec["title"]
    chart.has_legend = spec["legend"]
    if spec["legend"]:
        chart.legend.position = XL_LEGEND_POSITION.RIGHT
        chart.legend.include_in_layout = False

    plot = chart.plots[0]
    if kind == "pie":
        for point, color in zip(plot.series[0].points, spec["colors"], strict=False):
            if _css_rgb(color):
                point.format.fill.solid()
                point.format.fill.fore_color.rgb = _css_rgb(color)
        plot.has_data_labels = True
        plot.data_labels.show_percentage = True
        plot.data_labels.show_value = False
        plot.data_labels.number_format = "0%"
        plot.data_labels.number_format_is_linked = False
        _no_auto_title(chart, spec)
        return

    for target, s in zip(plot.series, series, strict=True):
        if kind == "scatter":
            target.marker.style = XL_MARKER_STYLE.CIRCLE
            if s["markerSize"]:
                target.marker.size = max(2, min(72, round(s["markerSize"] * PT)))
        color = _css_rgb(s["color"])
        if not color:
            continue
        if kind == "bar":
            target.format.fill.solid()
            target.format.fill.fore_color.rgb = color
        else:
            target.format.line.color.rgb = color
            target.marker.format.fill.solid()
            target.marker.format.fill.fore_color.rgb = color
            target.marker.format.line.color.rgb = color
            if "lines" not in s["mode"]:
                target.format.line.fill.background()
    category_title, value_title = spec["xTitle"], spec["yTitle"]
    if spec.get("horizontal"):
        category_title, value_title = value_title, category_title
    for axis, title in ((chart.category_axis, category_title), (chart.value_axis, value_title)):
        if title:
            axis.has_title = True
            axis.axis_title.text_frame.text = title
    chart.value_axis.has_major_gridlines = True
    # axis bounds as drawn by Plotly (PowerPoint would pick its own)
    value_range = spec["xRange"] if spec.get("horizontal") else spec["yRange"]
    axes = [(chart.value_axis, value_range)]
    if spec.get("xy"):
        axes.append((chart.category_axis, spec["xRange"]))
    for axis, bounds in axes:
        if bounds:
            axis.minimum_scale, axis.maximum_scale = bounds["min"], bounds["max"]
            axis.major_unit = bounds["step"]
    _no_auto_title(chart, spec)


def _no_auto_title(chart, spec):
    """Stop viewers from generating a title from series names."""
    if not spec["title"]:
        chart._chartSpace.chart.get_or_add_autoTitleDeleted().set("val", "1")
