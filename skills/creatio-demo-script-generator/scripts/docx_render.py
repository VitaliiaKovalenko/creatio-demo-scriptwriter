"""Render doc_model blocks into Word using the Creatio template (references/creatio-template.docx).

The template supplies the page setup, the branded header and footer (clean first page, red Creatio band and the
"One Platform. Freedom. Genuine Care." footer from page 2) and the styles: headings in Montserrat Creatio red,
body in Verdana grey, tables with a red rule over a light-grey header row and hairline grey borders.
Only the body is generated here.
"""
import re
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor

TEMPLATE = Path(__file__).resolve().parent.parent / "references" / "creatio-template.docx"
RED, GREY, DARK, MUTED, LINE, FILL, TINT = "E8310F", "595959", "404040", "7F7F7F", "D9D9D9", "F2F2F2", "FDF0ED"
WIDTH = 9639  # template table width (dxa)
CALLOUT = {  # kind -> (fill, bar colour, text colour)
    "goal": (TINT, RED, DARK), "value": (TINT, RED, DARK), "internal": (TINT, RED, DARK),
    "bubble": (FILL, RED, DARK), "example": (FILL, RED, DARK), "gap": (FILL, MUTED, DARK), "note": (FILL, MUTED, DARK),
}


def _el(tag, **attrs):
    e = OxmlElement(tag)
    for k, v in attrs.items():
        e.set(qn(k), str(v))
    return e


def render(blocks, path, template=TEMPLATE):
    doc = Document(template)
    body = doc.element.body
    sect = body.find(qn("w:sectPr"))
    for child in list(body):
        if child is not sect:
            body.remove(child)

    def fmt(r, size=10, color=GREY, bold=None, italic=None, font="Verdana"):
        rpr = r._r.get_or_add_rPr()
        fonts = rpr.find(qn("w:rFonts"))
        if fonts is None:
            fonts = _el("w:rFonts")
            rpr.insert(0, fonts)
        for a in ("w:ascii", "w:hAnsi", "w:cs"):
            fonts.set(qn(a), font)
        r.font.size = Pt(size)
        r.font.color.rgb = RGBColor.from_string(color)
        if bold is not None:
            r.bold = bold
        if italic is not None:
            r.italic = italic

    def inline(p, text, size=10, color=GREY, bold=False):
        for part in re.split(r"(\*\*.+?\*\*|`[^`]+`|\*[^*]+?\*)", str(text)):
            if not part:
                continue
            if part.startswith("**"):
                fmt(p.add_run(part[2:-2]), size, DARK, bold=True)
            elif part.startswith("`"):
                fmt(p.add_run(part[1:-1]), size - 0.5, DARK, font="Consolas")
            elif part.startswith("*"):
                fmt(p.add_run(part[1:-1]), size, color, italic=True, bold=bold or None)
            else:
                fmt(p.add_run(part), size, color, bold=bold or None)
        return p

    def lines_into(cell_or_doc, text, first_p, size, color, bold=False):
        p = first_p
        for i, line in enumerate(str(text).split("\n")):
            if i:
                p = cell_or_doc.add_paragraph()
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.space_before = Pt(0)
            inline(p, line, size, color, bold)

    def borders(tcPr, top_color, top_size, left=True):
        b = _el("w:tcBorders")
        b.append(_el("w:top", **{"w:val": "single", "w:sz": top_size, "w:space": 0, "w:color": top_color}))
        b.append(_el("w:left", **({"w:val": "single", "w:sz": 6, "w:space": 0, "w:color": LINE} if left else {"w:val": "nil"})))
        for side in ("bottom", "right"):
            b.append(_el(f"w:{side}", **{"w:val": "single", "w:sz": 6, "w:space": 0, "w:color": LINE}))
        tcPr.append(b)

    def new_table(ncol, widths):
        t = doc.add_table(rows=0, cols=ncol)
        tblPr = t._tbl.tblPr
        tblPr.append(_el("w:tblW", **{"w:w": WIDTH, "w:type": "dxa"}))
        tblPr.append(_el("w:tblLayout", **{"w:type": "fixed"}))
        mar = _el("w:tblCellMar")
        for side, w in (("top", 50), ("left", 100), ("bottom", 50), ("right", 100)):
            mar.append(_el(f"w:{side}", **{"w:w": w, "w:type": "dxa"}))
        tblPr.append(mar)
        grid = t._tbl.tblGrid
        for gc in list(grid):
            grid.remove(gc)
        total = sum(widths)
        dxa = [round(WIDTH * w / total) for w in widths]
        for w in dxa:
            grid.append(_el("w:gridCol", **{"w:w": w}))
        return t, dxa

    def row(t, dxa, values, header=False, first=False, key_col=False):
        r = t.add_row()
        trPr = r._tr.get_or_add_trPr()
        trPr.append(_el("w:cantSplit"))
        if header:
            trPr.append(_el("w:tblHeader"))
        for ci, (cell, val) in enumerate(zip(r.cells, values)):
            tcPr = cell._tc.get_or_add_tcPr()
            tcPr.append(_el("w:tcW", **{"w:w": dxa[ci], "w:type": "dxa"}))
            top_red = header or first
            borders(tcPr, RED if top_red else LINE, 12 if top_red else 6, left=ci > 0)
            if header or (key_col and ci == 0):
                tcPr.append(_el("w:shd", **{"w:val": "clear", "w:color": "auto", "w:fill": FILL}))
            tcPr.append(_el("w:vAlign", **{"w:val": "center"}))
            if header:
                p = cell.paragraphs[0]
                p.paragraph_format.space_after = Pt(0)
                fmt(p.add_run(re.sub(r"[*`]", "", str(val))), 9.5, DARK, bold=True)
            else:
                lines_into(cell, val, cell.paragraphs[0], 9, DARK if (key_col and ci == 0) else GREY, bold=key_col and ci == 0)

    def spacer():
        p = doc.add_paragraph(style="Creatio RFP")
        p.paragraph_format.space_after = Pt(2)

    def callout(text, kind, label):
        fill, bar, color = CALLOUT.get(kind, CALLOUT["note"])
        t = doc.add_table(rows=1, cols=1)
        t._tbl.tblPr.append(_el("w:tblW", **{"w:w": WIDTH, "w:type": "dxa"}))
        c = t.rows[0].cells[0]
        tcPr = c._tc.get_or_add_tcPr()
        tcPr.append(_el("w:shd", **{"w:val": "clear", "w:color": "auto", "w:fill": fill}))
        b = _el("w:tcBorders")
        b.append(_el("w:left", **{"w:val": "single", "w:sz": 18, "w:space": 0, "w:color": bar}))
        for side in ("top", "bottom", "right"):
            b.append(_el(f"w:{side}", **{"w:val": "nil"}))
        tcPr.append(b)
        p = c.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        if label:
            fmt(p.add_run(label + "   "), 8.5, bar, bold=True)
        inline(p, text, 9.5, color)
        spacer()

    def heading(text, style, size):
        p = doc.add_paragraph(style=style)
        if style == "Heading 1":
            p._p.get_or_add_pPr().append(_el("w:pageBreakBefore", **{"w:val": "0"}))
        r = p.add_run(re.sub(r"[*`]", "", text))
        fmt(r, size, RED, font="Montserrat")
        r.font.small_caps = False
        r.font.all_caps = False
        p.paragraph_format.keep_with_next = True
        return p

    for b in blocks:
        k = b[0]
        if k == "title":
            heading(b[1], "Heading 1", 20)
        elif k == "meta":
            p = doc.add_paragraph(style="Creatio RFP")
            fmt(p.add_run(b[1]), 9, MUTED)
        elif k == "h1":
            heading(b[1], "Heading 2", 16)
        elif k == "h2":
            heading(b[1], "Heading 3", 12.5)
        elif k == "p":
            inline(doc.add_paragraph(style="Creatio RFP"), b[1])
        elif k == "p_muted":
            p = doc.add_paragraph(style="Creatio RFP")
            p.paragraph_format.keep_with_next = True
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            inline(p, b[1], 9, MUTED)
        elif k == "bullet":
            p = doc.add_paragraph(style="List Bullet")
            p.paragraph_format.space_after = Pt(3)
            inline(p, b[1])
        elif k == "step":
            p = doc.add_paragraph(style="Creatio RFP")
            pf = p.paragraph_format
            pf.left_indent, pf.first_line_indent, pf.space_after = Pt(22), Pt(-22), Pt(4)
            pf.keep_together = True
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            fmt(p.add_run(f"{b[1]}.\t"), 10, RED, bold=True)
            inline(p, b[2])
        elif k == "scene":
            p = doc.add_paragraph(style="Creatio RFP")
            p.paragraph_format.keep_with_next = True
            fmt(p.add_run(f"— {b[1]} —"), 9.5, RED, italic=True)
        elif k == "callout":
            callout(b[1], b[2], b[3])
        elif k == "kv":
            rows = [r for r in b[1] if r[1]]
            if rows:
                t, dxa = new_table(2, [26, 74])
                for i, r in enumerate(rows):
                    row(t, dxa, r, first=i == 0, key_col=True)
                spacer()
        elif k == "table":
            headers, rows, widths = b[1], b[2], b[3] or [1] * len(b[1])
            t, dxa = new_table(len(headers), widths)
            row(t, dxa, headers, header=True)
            for r in rows:
                row(t, dxa, ["" if v is None else v for v in r])
            spacer()
        elif k == "pagebreak":
            doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
    doc.core_properties.title = next((b[1] for b in blocks if b[0] == "title"), "")
    doc.save(path)
