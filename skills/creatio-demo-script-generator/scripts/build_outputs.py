"""spec.json -> the deliverables of a demo script package.

Usage:
    python build_outputs.py <spec.json> [--out <dir>] [--force] [--model-xlsx]

Writes, next to the spec (or into --out):
    <Client>_Demo_Script.docx     the script (team template): customer summary, discovery insights,
                                  demo summary, industry context, ground rules, roles, build scope,
                                  use cases, proposed additions, competitive positioning (internal),
                                  ideas from similar demos (internal), decisions, questions, appendices
    <Client>_Build_Spec.docx      the SE's configuration: AI actions, object model, lookups, pages,
                                  dashboards, DCM, processes, rules, integrations, notifications,
                                  clocks, demo data summary
    <Client>_Demo_Data.xlsx       one import-ready sheet per object + summary + lookup values
    <Client>_requirements.md      the build hand-off (creatio-demo-build phase 1 "derive" route)
    <Client>_Object_Model.xlsx    only with --model-xlsx: the same model as filterable sheets
Runs validate_spec.validate() first and stops on errors unless --force.
"""
import json
import re
import sys
from collections import OrderedDict
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_spec import anchor_date, display_column, norm_type, render_date_tokens, resolve_date, validate  # noqa: E402
from quality_checks import tier_of, usage  # noqa: E402

# house style — references/docx-house-style.md
PRIMARY_800 = "123B54"
PRIMARY_600 = "1C6B8C"
TEAL = "0E8F86"
PRIMARY_300 = "8FC0D4"
PRIMARY_050 = "EFF6F9"
ROW_ALT = "F5F9FB"
HAIRLINE = "D8E2E8"
INK = "16212E"
SLATE = "51626E"
AMBER_BAR, AMBER_BG, AMBER_TXT = "C9861A", "FBF3E6", "8A530C"


def shorten(items, limit=220):
    """Join items with ', ' up to ~limit characters at an item boundary, then '+N more'."""
    out, n = [], 0
    for i, x in enumerate(items):
        if n + len(x) > limit and out:
            return ", ".join(out) + f" (+{len(items) - i} more)"
        out.append(x)
        n += len(x) + 2
    return ", ".join(out)


def apply_date_tokens(x, anchor):
    """Render {date:today-30} tokens in every string of the spec, so text dates move with meta.date."""
    if isinstance(x, dict):
        return {k: apply_date_tokens(v, anchor) for k, v in x.items()}
    if isinstance(x, list):
        return [apply_date_tokens(v, anchor) for v in x]
    if isinstance(x, str) and "{date:" in x:
        return render_date_tokens(x, anchor)
    return x


def safe_name(s):
    return re.sub(r"[^\w-]+", "_", s.strip()).strip("_")


# ======================================================================= DOCX
def build_docx(spec, path, part="script"):
    from docx import Document
    from docx.enum.section import WD_ORIENT  # noqa: F401
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.enum.text import WD_BREAK  # noqa: F401
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Pt, RGBColor, Twips

    AFTER_PBDR = ["w:shd", "w:tabs", "w:suppressAutoHyphens", "w:kinsoku", "w:wordWrap", "w:overflowPunct",
                  "w:topLinePunct", "w:autoSpaceDE", "w:autoSpaceDN", "w:bidi", "w:adjustRightInd", "w:snapToGrid",
                  "w:spacing", "w:ind", "w:contextualSpacing", "w:mirrorIndents", "w:suppressOverlap", "w:jc",
                  "w:textDirection", "w:textAlignment", "w:textboxTightWrap", "w:outlineLvl", "w:divId",
                  "w:cnfStyle", "w:rPr", "w:sectPr", "w:pPrChange"]

    meta = spec["meta"]
    client = meta["client"]
    doc = Document()

    # page: A4, margins 1080 sides / 900 top-bottom
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Twips(11906), Twips(16838)
    sec.left_margin = sec.right_margin = Twips(1080)
    sec.top_margin = sec.bottom_margin = Twips(900)

    def set_font(style_or_run, name, size=None, color=None, bold=None, italic=None):
        f = style_or_run.font
        f.name = name
        rpr = style_or_run.element.get_or_add_rPr()
        rfonts = rpr.find(qn("w:rFonts"))
        if rfonts is None:
            rfonts = OxmlElement("w:rFonts")
            rpr.insert(0, rfonts)
        for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
            rfonts.set(qn(a), name)
        for a in ("w:asciiTheme", "w:hAnsiTheme", "w:cstheme", "w:eastAsiaTheme"):
            if rfonts.get(qn(a)) is not None:
                del rfonts.attrib[qn(a)]
        if size:
            f.size = Pt(size)
        if color:
            f.color.rgb = RGBColor.from_string(color)
        if bold is not None:
            f.bold = bold
        if italic is not None:
            f.italic = italic

    st = doc.styles
    set_font(st["Normal"], "Segoe UI", 9, INK)
    pf = st["Normal"].paragraph_format
    pf.space_after, pf.space_before, pf.line_spacing = Pt(3), Pt(0), 1.12
    for name, size, color, before, after in (("Title", 18, PRIMARY_800, 0, 2), ("Heading 1", 12.5, PRIMARY_800, 14, 4),
                                             ("Heading 2", 10.5, PRIMARY_800, 10, 4), ("Heading 3", 8.5, PRIMARY_600, 8, 2)):
        s = st[name]
        set_font(s, "Segoe UI Semibold", size, color, bold=False, italic=False)
        s.paragraph_format.space_before, s.paragraph_format.space_after = Pt(before), Pt(after)
        s.paragraph_format.keep_with_next = True
        s.paragraph_format.line_spacing = 1.0
    if "List Bullet" in [x.name for x in st]:
        set_font(st["List Bullet"], "Segoe UI", 9, INK)

    def ppr_insert(p, el, successors):
        p._p.get_or_add_pPr().insert_element_before(el, *successors)

    def shade_par(p, fill):
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), fill)
        ppr_insert(p, shd, AFTER_PBDR[1:])

    def border_par(p, side, color, size_eighths, space=4):
        pPr = p._p.get_or_add_pPr()
        bdr = pPr.find(qn("w:pBdr"))
        if bdr is None:
            bdr = OxmlElement("w:pBdr")
            ppr_insert(p, bdr, AFTER_PBDR)
        b = OxmlElement(f"w:{side}")
        b.set(qn("w:val"), "single")
        b.set(qn("w:sz"), str(size_eighths))
        b.set(qn("w:space"), str(space))
        b.set(qn("w:color"), color)
        bdr.append(b)

    def rich(p, text, base_color=INK, size=None):
        """**bold** -> semibold PRIMARY_800, *italic* -> italic SLATE (provenance)."""
        for part in re.split(r"(\*\*.+?\*\*|\*[^*]+?\*)", text):
            if not part:
                continue
            if part.startswith("**"):
                r = p.add_run(part[2:-2])
                set_font(r, "Segoe UI Semibold", size, PRIMARY_800, bold=False)
            elif part.startswith("*"):
                r = p.add_run(part[1:-1])
                set_font(r, "Segoe UI", size, SLATE, italic=True)
            else:
                r = p.add_run(part)
                set_font(r, "Segoe UI", size, base_color)
        return p

    def h1(text):
        p = doc.add_paragraph(text, style="Heading 1")
        border_par(p, "bottom", PRIMARY_300, 6, 2)
        return p

    def uc_banner(text):
        p = doc.add_paragraph(style="Heading 2")
        r = p.add_run(text)
        set_font(r, "Segoe UI Semibold", 10.5, "FFFFFF", bold=False)
        border_par(p, "left", TEAL, 24, 0)
        shade_par(p, PRIMARY_600)
        p.paragraph_format.space_before = Pt(14)
        return p

    def h2chip(text):
        p = doc.add_paragraph(style="Heading 2")
        border_par(p, "left", PRIMARY_600, 18, 6)
        shade_par(p, PRIMARY_050)
        p.add_run(text)
        return p

    def callout(text, fill, bar, color=INK, label=None):
        p = doc.add_paragraph()
        border_par(p, "left", bar, 18, 8)
        shade_par(p, fill)
        p.paragraph_format.left_indent = Twips(360)
        p.paragraph_format.space_before, p.paragraph_format.space_after = Pt(6), Pt(6)
        if label:
            r = p.add_run(label + "  ")
            set_font(r, "Segoe UI Semibold", 8, bar, bold=False)
        rich(p, text, color)
        return p

    def step(n, text):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Twips(360)
        p.paragraph_format.first_line_indent = Twips(-360)
        p.paragraph_format.tab_stops.add_tab_stop(Twips(360))
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_together = True
        r = p.add_run(f"{n}.")
        set_font(r, "Segoe UI Semibold", 9.5, TEAL, bold=False)
        p.add_run("\t")
        rich(p, text)
        return p

    def table(headers, rows, widths, header=True):
        text_width = 11906 - 2 * 1080  # A4 minus side margins
        widths = [round(w * text_width / sum(widths)) for w in widths]
        t = doc.add_table(rows=1, cols=len(headers))
        t.alignment = WD_TABLE_ALIGNMENT.LEFT
        tblPr = t._tbl.tblPr
        layout = OxmlElement("w:tblLayout")
        layout.set(qn("w:type"), "fixed")
        tblPr.append(layout)
        borders = OxmlElement("w:tblBorders")
        for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
            b = OxmlElement(f"w:{side}")
            b.set(qn("w:val"), "single")
            b.set(qn("w:sz"), "4")
            b.set(qn("w:color"), HAIRLINE)
            borders.append(b)
        tblPr.append(borders)
        grid = t._tbl.tblGrid
        for gc, w in zip(grid.findall(qn("w:gridCol")), widths):
            gc.set(qn("w:w"), str(w))

        def fill_row(row, values, header=False, alt=False):
            trPr = row._tr.get_or_add_trPr()
            cs = OxmlElement("w:cantSplit")
            trPr.append(cs)
            if header:
                th = OxmlElement("w:tblHeader")
                trPr.append(th)
            for cell, val, w in zip(row.cells, values, widths):
                cell.width = Twips(w)
                tcPr = cell._tc.get_or_add_tcPr()
                fill = PRIMARY_600 if header else (ROW_ALT if alt else "FFFFFF")
                shd = OxmlElement("w:shd")
                shd.set(qn("w:val"), "clear")
                shd.set(qn("w:color"), "auto")
                shd.set(qn("w:fill"), fill)
                tcPr.append(shd)
                p = cell.paragraphs[0]
                p.paragraph_format.space_after = Pt(1)
                p.paragraph_format.line_spacing = 1.04
                if header:
                    r = p.add_run(str(val))
                    set_font(r, "Segoe UI Semibold", 7.5, "FFFFFF", bold=False)
                else:
                    lines_ = str(val).split("\n")  # one paragraph per line, never a newline inside a run
                    rich(p, lines_[0], INK, 7.5)
                    for extra in lines_[1:]:
                        q = cell.add_paragraph()
                        q.paragraph_format.space_after = Pt(1)
                        q.paragraph_format.line_spacing = 1.04
                        rich(q, extra, INK, 7.5)

        if header:
            fill_row(t.rows[0], headers, header=True)
            body_rows = rows
        else:
            fill_row(t.rows[0], rows[0])
            body_rows = rows[1:]
        for i, r in enumerate(body_rows):
            fill_row(t.add_row(), r, alt=(i % 2 == 1) if header else (i % 2 == 0))
        doc.add_paragraph().paragraph_format.space_after = Pt(2)
        return t

    # running header / footer
    hp = sec.header.paragraphs[0]
    r = hp.add_run(client.upper())
    set_font(r, "Segoe UI Semibold", 7.5, PRIMARY_800, bold=False)
    r = hp.add_run(f"   {meta.get('title', 'Demo Script') if part == 'script' else 'Build Specification'} · {meta.get('version', 'v1')}")
    set_font(r, "Segoe UI", 7.5, SLATE)
    border_par(hp, "bottom", PRIMARY_300, 4, 2)
    fp = sec.footer.paragraphs[0]
    r = fp.add_run("Creatio Demo Build — Confidential   ")
    set_font(r, "Segoe UI", 7.5, SLATE)
    for kind, txt in (("begin", None), (None, "PAGE"), ("end", None)):
        run = fp.add_run()
        set_font(run, "Segoe UI", 7.5, SLATE)
        if kind:
            fc = OxmlElement("w:fldChar")
            fc.set(qn("w:fldCharType"), kind)
            run._r.append(fc)
        else:
            it = OxmlElement("w:instrText")
            it.set(qn("xml:space"), "preserve")
            it.text = txt
            run._r.append(it)
    border_par(fp, "top", HAIRLINE, 4, 2)

    # ---- title + telegraph header
    doc.add_paragraph(f"{client} — " + (meta.get("title", "Demo Script") if part == "script" else "Build Specification"), style="Title")
    p = doc.add_paragraph()
    r = p.add_run(f"{meta.get('version', 'v1')} · {meta.get('date', '')}")
    set_font(r, "Segoe UI", 8.5, SLATE)
    ucs = spec["use_cases"]
    # ---- shared lookups for the body
    brief = spec.get("brief", {})
    model = spec.get("model", {})
    roles = spec.get("roles", [])
    lookups_by = {l["code"]: l for l in model.get("lookups", [])}
    objects_by = {o["code"]: o for o in model.get("objects", [])}
    STATUS = {"new": "**new**", "extended": "extended", "existing": "*existing*"}
    REAL = {"real": "**real**", "simulated": "simulated", "talking point": "*talking point*"}
    data = spec.get("data", [])

    def steps_txt(x):
        return ", ".join(x.get("steps", []) or [])

    def uc_refs(uc):
        return {(uc["id"], it["step"]) for it in uc.get("items", []) if "step" in it}

    def expand(refs):
        out = set()
        for r in refs or []:
            m = re.match(r"^(UC\d+)\.(\d+)(?:-(\d+))?$", str(r))
            if m:
                for n in range(int(m.group(2)), int(m.group(3) or m.group(2)) + 1):
                    out.add((m.group(1), n))
        return out

    def kv_table(rows):
        rows = [[f"**{k}**", v] for k, v in rows if v]
        if rows:
            table(["", ""], rows, [2400, 6626], header=False)

    # ---- record labels: resolve "@KEY" display values to the target record's own label
    _blocks = {b.get("object"): b for b in spec.get("data", [])}
    _objs = {o["code"]: o for o in spec.get("model", {}).get("objects", [])}
    _by_key = {r["_key"]: (b.get("object"), r) for b in spec.get("data", []) for r in b.get("records", []) if r.get("_key")}

    def rec_label(oc, r, depth=0):
        v = r.get(display_column(_objs.get(oc, {})))
        if isinstance(v, str) and v.startswith("@") and depth < 3 and v[1:] in _by_key:
            toc, tr = _by_key[v[1:]]
            return rec_label(toc, tr, depth + 1)
        return str(v if v not in (None, "") else r.get("_key", ""))

    def short_link(url):
        """SharePoint links wrap over many lines in a table: show the folder/file tail."""
        u = str(url).replace("%20", " ")
        for cut in ("/Shared Documents/", "/Documents/"):
            if cut in u:
                return "SharePoint: …/" + "/".join(u.split(cut, 1)[1].split("/")[-2:])
        return u if len(u) < 70 else u[:67] + "…"

    # ---- research helpers
    def fmt_src(s):
        if isinstance(s, dict):
            return f"{s.get('title') or s.get('url', '')}" + (f" ({s['date']})" if s.get("date") else "")
        return str(s)

    def joined(v, sep="\n"):
        return sep.join(v) if isinstance(v, list) else str(v or "")

    # ---- header card: instance first (the SE's first question)
    inst = meta.get("instance") or {}
    inst_txt = " · ".join(x for x in [inst.get("name"), inst.get("url"),
                                      {"new": "new stand", "reuse": "reuse the existing stand", "copy": f"copy of {inst.get('reference_demo', '')}"}.get(inst.get("mode"), "")] if x)
    by_login = {}
    for r in roles:
        if r.get("login"):
            by_login.setdefault(r["login"], []).append(r["name"])
    logins = "; ".join(f"{k} ({', '.join(v)})" for k, v in by_login.items())
    lines = [
        ("Client", client + (f" · {meta['industry']}" if meta.get("industry") else "")),
        ("Demo instance", inst_txt),
        ("Previous demos", inst.get("previous_demos", "")),
        ("Demo date", meta.get("date", "") + (f" · {meta['duration_min']} min" if meta.get("duration_min") else "")),
        ("Deal size", (f"ARR {meta['deal']['arr_usd']:,.0f} USD" + (f" ({meta['deal']['arr_original']})" if meta['deal'].get('arr_original') else "")
                       + f" → {tier_of(meta['deal']['arr_usd'])['label']}" + (" — assumed, confirm" if meta['deal'].get('arr_assumed') else ""))
         if isinstance((meta.get("deal") or {}).get("arr_usd"), (int, float)) else ""),
        ("Logins", (logins or meta.get("demo_user", "")) + " — credentials in the team credential store, never in this document"),
        ("Use cases", f"{len(ucs)} — " + " · ".join(f"{u['id']} {u['name']}" for u in ucs)),
        ("Language", meta.get("language", "") + (f" · region {meta['region']}" if meta.get("region") else "") + (f" · {meta['currency']}" if meta.get("currency") else "")),
        ("Walkthrough video", meta.get("walkthrough", "")),
    ]
    card = doc.add_paragraph()
    shade_par(card, PRIMARY_050)
    border_par(card, "left", PRIMARY_600, 18, 8)
    first = True
    for label, val in lines:
        if not val:
            continue
        if not first:
            card.add_run().add_break()
        first = False
        r = card.add_run(f"{label}:  ")
        set_font(r, "Segoe UI Semibold", 8.5, PRIMARY_600, bold=False)
        r = card.add_run(val)
        set_font(r, "Segoe UI", 8.5, INK)
    if brief.get("demo_goal"):
        callout(brief["demo_goal"], "E6F4F2", TEAL, label="DEMO GOAL")

    # ---- brief customer summary (team template)
    if part == "script":
        h1("Brief customer summary")
        if brief.get("summary"):
            rich(doc.add_paragraph(), brief["summary"])
        kv_table([
            ("Goals / problems", "\n".join(f"**{p['id']}** {p['text']}" for p in brief.get("pains", []) + brief.get("goals", []))),
            ("Customer website", meta.get("website", "")),
            ("Key customer products", " · ".join(meta.get("key_products", []))),
            ("Key roles", ", ".join(r["name"] for r in roles)),
            ("Key marketplace solutions", ", ".join(meta.get("marketplace", [])) or "none"),
            ("Languages", meta.get("language", "")),
        ])

        # ---- discovery insights (research layer)
        disc = spec.get("discovery") or {}
        if part == "script" and disc.get("moments"):
            h1("Discovery insights")
            intro = "From " + disc.get("source", "the discovery call") + (f" · {disc['date']}" if disc.get("date") else "") + \
                    (f" · participants: {', '.join(disc['participants'])}" if disc.get("participants") else "") + \
                    ". What the customer said that shapes this demo; *not covered* marks a moment no use case answers yet (see Proposed additions)."
            rich(doc.add_paragraph(), intro, SLATE).paragraph_format.keep_with_next = True
            rank = {"high": 0, "medium": 1, "low": 2}
            ms = sorted(disc["moments"], key=lambda m: rank.get(m.get("importance"), 3))
            table(["#", "When · who", "What they said", "What it means", "Covered by"],
                  [[m.get("id", ""), f"{m.get('minute', '')} · {m.get('speaker', '')}", f"“{m.get('quote', '')}”",
                    f"**{m.get('kind', '')}**" + (f" · {m['importance']}" if m.get("importance") else "") + f" — {m.get('insight', '')}",
                    ", ".join(m.get("covered_by", [])) or "*not covered*"] for m in ms],
                  [500, 1500, 3000, 2826, 1200])

        if spec.get("research_gaps"):
            callout("Research that could not be done: " + " · ".join(g.strip().rstrip(".;") for g in spec["research_gaps"]) + ".",
                    AMBER_BG, AMBER_BAR, AMBER_TXT, label="RESEARCH GAPS")

        # ---- brief demo summary
        h1("Brief demo summary")
        sections = [o["section"] if (o.get("caption") or o["code"]).split(" (")[0].lower() in o["section"].lower()
                    else f"{o['section']} ({(o.get('caption') or o['code']).split(' (')[0]})"
                    for o in model.get("objects", []) if o.get("section")]
        heroes = []
        for b in data:
            o = objects_by.get(b["object"], {})
            dc = display_column(o)
            heroes += [f"{rec_label(b['object'], r)} ({o.get('caption') or b['object']})" for r in b.get("records", []) if r.get("_main")]
        kv_table([
            ("What the demo covers", brief.get("focus", "")),
            ("Reference demo", inst.get("reference_demo", "")),
            ("Key sections", " · ".join(sections)),
            ("Hero records", shorten(heroes, 400)),
            ("Story", "\n".join(f"**{u['id']}** {u.get('flow_line', '')}" for u in ucs)),
        ])
        if brief.get("agenda"):
            doc.add_paragraph("Agenda coverage", style="Heading 3")
            uc_names = {u["id"]: u["name"] for u in ucs}
            table(["#", "Agenda item", "Shown in", "Note"],
                  [[a["id"], a["text"], ", ".join(f"{u} {uc_names.get(u, '')}" for u in a.get("covered_by", [])) or "—", a.get("note", "")]
                   for a in brief["agenda"]], [600, 3626, 2700, 2100])
        if brief.get("vocabulary"):
            doc.add_paragraph("Your terms in Creatio", style="Heading 3")
            table(["Your term", "In Creatio"], [[v["client"], v["creatio"]] for v in brief["vocabulary"]], [3000, 6026])

        # ---- industry context (research layer)
        ind = spec.get("industry") or {}
        if part == "script" and ind.get("points"):
            h1("Industry context" + (f" — {ind['name']}" if ind.get("name") else ""))
            if ind.get("summary"):
                rich(doc.add_paragraph(), ind["summary"])
            table(["#", "What matters in this industry", "Why for this customer", "In the demo"],
                  [[x.get("id", ""), x.get("point", ""), x.get("why", ""), x.get("demo_implication", "")] for x in ind["points"]],
                  [550, 2900, 2600, 2976])
            if ind.get("sources"):
                rich(doc.add_paragraph(), "*Sources: " + "; ".join(fmt_src(s) for s in ind["sources"]) + "*", SLATE)

        # ---- ground rules
        if spec.get("ground_rules"):
            h1("Ground rules")
            for g in spec["ground_rules"]:
                rich(doc.add_paragraph(style="List Bullet"), g)

        # ---- roles and logins
        if roles:
            h1("Roles and logins")
            table(["Role", "Login mode", "Login", "Workplace / sections", "Use cases"],
                  [[f"**{r['name']}**" + (f" — {r['title']}" if r.get("title") else ""), r.get("login_mode", ""), r.get("login", ""),
                    " · ".join(x for x in [r.get("workplace", ""), ", ".join(r.get("sections", [])), r.get("scope", "")] if x),
                    ", ".join(r.get("use_cases", []))] for r in roles],
                  [2200, 1300, 1500, 2826, 1200])

        # ---- build scope matrix
        h1("Build scope")
        rich(doc.add_paragraph(), f"What to configure, field by field: **{safe_name(client)}_Build_Spec.docx**. "
                                  "Proposed additions are not in this scope until accepted.", SLATE)
        deal = meta.get("deal") or {}
        if isinstance(deal.get("arr_usd"), (int, float)):
            t = tier_of(deal["arr_usd"])
            callout(f"**{t['label']}** — ARR {deal['arr_usd']:,.0f} USD" + (" *(assumed — confirm)*" if deal.get("arr_assumed") else "")
                    + f". {t['intent']}", PRIMARY_050, PRIMARY_600, label="DEAL TIER")
            used = usage(spec)
            names = {"new_objects": "New objects", "new_columns": "New columns", "new_lookups": "New lookups",
                     "processes": "Processes (reset excluded)", "designer_processes": "Designer-only processes",
                     "ai_actions": "AI actions", "integrations": "Simulated integrations", "dcm": "DCM cases"}
            exc = {x.get("budget"): x.get("why", "") for x in deal.get("exceptions", [])}
            table(["Budget", "Used", "Tier allows", "Exception"],
                  [[names[k], used[k], "no cap" if cap is None else cap, exc.get(k, "")] for k, cap in t["budget"].items()],
                  [3000, 1000, 1500, 3526])
        cells = {}

        def put(area, real, text):
            cells.setdefault(area, {"real": [], "simulated": [], "talking point": []})
            cells[area][real if real in ("real", "simulated", "talking point") else "real"].append(text)

        for o in model.get("objects", []):
            if o.get("status") in ("new", "extended"):
                put("Objects", "real", f"{o.get('caption') or o['code']} ({o['status']}{', ' + o['depth'] if o.get('depth') else ''})")
        for x in model.get("ui", []):
            if x.get("kind") == "Reuse":
                put("Reference-demo screens", "real", f"reuse {x.get('name', '')}" + (f" ({x['does']})" if x.get("does") else ""))
            elif x.get("kind") == "Hide":
                put("Reference-demo screens", "real", f"hide {x.get('name', '')}")
            else:
                put("Pages and navigation", "real", x.get("name", ""))
        for d in model.get("dcm", []):
            for s in d.get("stages", []):
                put("DCM", {"built": "real", "prefilled": "simulated", "simulated": "simulated"}.get(s.get("scope", "built"), "real"),
                    f"{s.get('name')}" + (" (pre-filled record)" if s.get("scope") == "prefilled" else ""))
        for kind, area in (("processes", "Processes"), ("rules", "Business rules"), ("ai", "AI"),
                           ("integrations", "Integrations"), ("notifications", "Notifications")):
            for x in model.get(kind, []):
                put(area, x.get("realization", "real"), x.get("name") or x.get("id", ""))
        for d in model.get("dashboards", []):
            put("Dashboards", "real", f"{d.get('name')} ({len(d.get('widgets', []))} widgets)")
        put("Data", "real", f"{sum(len(b.get('records', [])) for b in data)} records across {len(data)} objects")
        table(["Area", "Built for real", "Simulated", "Talking point only"],
              [[f"**{area}**", " · ".join(v["real"]), " · ".join(v["simulated"]), " · ".join(v["talking point"])] for area, v in cells.items()],
              [1700, 3326, 2500, 1500])
        oos = [f"**{x['item']}** — {x.get('why', '')}" for x in spec.get("out_of_scope", [])]
        oos_txt = " ".join(f"{x.get('item', '')} {x.get('why', '')}" for x in spec.get("out_of_scope", []))
        oos += [f"**{a['text']}** (agenda {a['id']}) — {a.get('note', '')}" for a in brief.get("agenda", [])
                if not a.get("covered_by") and not a.get("talk") and not re.search(r"\b" + re.escape(a["id"]) + r"\b", oos_txt)]
        if oos:
            doc.add_paragraph("Out of scope", style="Heading 3")
            for x in oos:
                rich(doc.add_paragraph(style="List Bullet"), x)
        prio = [u for u in ucs if u.get("priority")]
        if len({u["priority"] for u in prio}) < 2:
            prio = []  # all "must": a protect-in-order line says nothing
        if prio or meta.get("build_budget_h"):
            doc.add_paragraph("If time runs short", style="Heading 3")
            order = {"must": 0, "should": 1, "could": 2}
            txt = (f"Build budget {meta['build_budget_h']} h. " if meta.get("build_budget_h") else "") + "Protect in this order: " + \
                  " → ".join(f"{u['id']} ({u['priority']})" for u in sorted(prio, key=lambda u: order.get(u["priority"], 3)))
            rich(doc.add_paragraph(), txt)

        # ---- before you present
        h1("Before you present")
        reset = next((p for p in model.get("processes", []) if "before demo" in p.get("name", "").lower()), None)
        if reset:
            rich(doc.add_paragraph(), f"Run the **{reset['name']}** process — it resets every record this demo touches to its opening state.")
        pre = spec.get("pre_demo", {})
        for x in pre.get("must_exist", []):
            rich(doc.add_paragraph(style="List Bullet"), f"Exists: {x}")
        for x in pre.get("must_not_exist", []):
            rich(doc.add_paragraph(style="List Bullet"), f"Does **not** exist yet (created live): {x}")
        for x in pre.get("checks", []):
            rich(doc.add_paragraph(style="List Bullet"), x)

        # ---- use cases (team template blocks)
        h1("Demo use cases")
        for u in ucs:
            uc_banner(f"Use case {u['id'].replace('UC', '')} — {u['name']}")
            tags = [x for x in [f"Persona: {u['persona']}" if u.get("persona") else "",
                                f"Entry point: {u['entry_point']}" if u.get("entry_point") else "",
                                "Agenda: " + ", ".join(u["agenda"]) if u.get("agenda") else "",
                                "Answers: " + ", ".join(u["pains"]) if u.get("pains") else "",
                                f"Priority: {u['priority']}" if u.get("priority") else ""] if x]
            if tags:
                p = doc.add_paragraph()
                p.paragraph_format.keep_with_next = True
                r = p.add_run("   ·   ".join(tags))
                set_font(r, "Segoe UI", 7.5, SLATE)
            doc.add_paragraph("Purpose", style="Heading 3")
            if u.get("summary"):
                rich(doc.add_paragraph(), u["summary"])
            p = doc.add_paragraph()
            r = p.add_run(u.get("flow_line", ""))
            set_font(r, "Segoe UI", 9, SLATE, italic=True)
            doc.add_paragraph("Click path", style="Heading 3")
            for it in u.get("items", []):
                if "bubble" in it:
                    callout(it["bubble"], PRIMARY_050, PRIMARY_600).paragraph_format.keep_with_next = True
                elif "scene" in it:
                    p = doc.add_paragraph()
                    p.paragraph_format.space_before = Pt(8)
                    p.paragraph_format.keep_with_next = True
                    r = p.add_run(f"— Scene: {it['scene']} —")
                    set_font(r, "Segoe UI Semibold", 8.5, PRIMARY_600, bold=False)
                elif "step" in it:
                    step(it["step"], it["text"])
            if u.get("value_message"):
                doc.add_paragraph("Value message", style="Heading 3")
                callout(u["value_message"], "E6F4F2", TEAL)
            # required setup: names only, pointing at the configuration part (no restating)
            own = uc_refs(u)
            setup = []
            newcols = [f"{o.get('caption') or o['code']}.{c.get('caption') or c['code']}" for o in model.get("objects", [])
                       for c in o.get("columns", []) if c.get("status") == "new" and expand(c.get("steps")) & own]
            objs = [f"{o.get('caption') or o['code']} ({o['status']})" for o in model.get("objects", [])
                    if o.get("status") != "existing" and expand(o.get("steps")) & own]
            if objs:
                setup.append(f"**Objects:** {', '.join(objs)}")
            if newcols:
                setup.append(f"**New columns:** {', '.join(newcols)}")
            for kind, label in (("ui", "Pages and buttons"), ("dashboards", "Dashboards"), ("dcm", "DCM"), ("processes", "Processes"),
                                ("rules", "Business rules"), ("ai", "AI"), ("integrations", "Integrations"), ("notifications", "Notifications"), ("slas", "Clocks")):
                names = [(x.get("name") or x.get("id")) + (f" *({x['realization']})*" if x.get("realization") and x["realization"] != "real" else "")
                         for x in model.get(kind, []) if expand(x.get("steps")) & own and x.get("kind") != "Hide"]
                if names:
                    setup.append(f"**{label}:** {', '.join(names)}")
            if setup:
                doc.add_paragraph("Required setup", style="Heading 3")
                for s_ in setup:
                    rich(doc.add_paragraph(style="List Bullet"), s_)
            text = " ".join(it.get("text", "") for it in u.get("items", []) if "step" in it)
            recs = []
            for b in data:
                o = objects_by.get(b["object"], {})
                dc = display_column(o)
                for r in b.get("records", []):
                    v = rec_label(b["object"], r)
                    if r.get("_main") and v and str(v) in text:
                        recs.append(f"{v} ({o.get('caption') or b['object']})")
            if recs or u.get("data_note"):
                doc.add_paragraph("Required data population", style="Heading 3")
                if recs:
                    rich(doc.add_paragraph(style="List Bullet"), "**Hero records:** " + ", ".join(recs))
                if u.get("data_note"):
                    rich(doc.add_paragraph(style="List Bullet"), u["data_note"])

    # ---- proposed additions, competitive positioning, similar demos (research layer)
    props = spec.get("proposed_additions", [])
    if part == "script" and props:
        h1("Proposed additions")
        rich(doc.add_paragraph(), "Not in the agreed scope yet — nothing here is in the build scope, setup or data until accepted. "
                                  "Each comes from the discovery call (D), the industry (IND), the competition (CMP) or a past demo (PD). "
                                  "Accept or reject each; accepted ones move into the use cases in the next version.", SLATE).paragraph_format.keep_with_next = True
        rank = {"high": 0, "medium": 1, "low": 2}
        table(["#", "Proposal", "Why · sources", "What the audience would see", "Fits", "Size", "Status"],
              [[x.get("id", ""), f"**{x.get('title', '')}** *({x.get('kind', '')}" + (f", {x['priority']}" if x.get("priority") else "") + ")*",
                f"{x.get('why', '')} *({', '.join(x.get('sources', []))})*", x.get("demo_moment", ""), x.get("fits", ""),
                x.get("effort", ""), x.get("status", "proposed")]
               for x in sorted(props, key=lambda x: rank.get(x.get("priority"), 3))],
              [500, 1700, 1900, 2326, 1100, 600, 900])

    comp = spec.get("competitive") or {}
    if part == "script" and (comp.get("competitors") or comp.get("points")):
        h1("Competitive positioning — internal")
        callout("Do not share with the customer. Factual and sourced; competitor strengths are included so the presenter is never surprised.",
                AMBER_BG, AMBER_BAR, AMBER_TXT, label="INTERNAL")
        if comp.get("summary"):
            rich(doc.add_paragraph(), comp["summary"])
        if comp.get("competitors"):
            table(["Competitor", "Why in this deal", "Would likely show", "Genuinely strong at", "Where Creatio wins here"],
                  [[f"**{c.get('name', '')}**" + (f"\n*{joined(c.get('products'), ', ')}*" if c.get("products") else ""),
                    c.get("why_in_deal", ""), joined(c.get("would_show")), joined(c.get("strengths")), joined(c.get("gaps"))]
                   for c in comp["competitors"]],
                  [1500, 1500, 2100, 1900, 2026])
        if comp.get("points"):
            doc.add_paragraph("Per use case", style="Heading 3")
            table(["#", "Use case", "A competitor would show", "Creatio better because", "Demo highlight", "Trap to avoid"],
                  [[x.get("id", ""), x.get("uc", ""), x.get("they_show", ""), x.get("creatio_better", ""), x.get("demo_highlight", ""), x.get("trap", "")]
                   for x in comp["points"]],
                  [700, 700, 1850, 1900, 2150, 1726])
        srcs = [fmt_src(s) for c in comp.get("competitors", []) for s in c.get("sources", [])]
        if srcs:
            rich(doc.add_paragraph(), "*Sources: " + "; ".join(dict.fromkeys(srcs)) + "*", SLATE)

    sims = spec.get("similar_demos", [])
    if part == "script" and sims:
        h1("Ideas from similar demos — internal")
        rich(doc.add_paragraph(), "Past Creatio demos for the same industry or use cases (SharePoint, Custom DEMOs). "
                                  "Ideas only — no names, people or data from them appear in this demo.", SLATE).paragraph_format.keep_with_next = True
        table(["#", "Demo", "Industry · use cases", "Reuse", "Lessons"],
              [[x.get("id", ""), f"**{x.get('customer', '')}**" + (f"\n{short_link(x['link'])}" if x.get("link") else ""),
                f"{x.get('industry', '')} · {joined(x.get('use_cases'), ', ')}", joined(x.get("reuse")), joined(x.get("lessons"))]
               for x in sims],
              [500, 2200, 1800, 2526, 2000])

    if part == "spec":
        rich(doc.add_paragraph(), f"Companion to **{safe_name(client)}_Demo_Script.docx** — the demo flow, roles, build scope and decisions "
                                  "are there; this document says what to configure. Step references (UC1.4) point at its use cases.", SLATE)

    # ---- configuration
    if part == "spec":
        objs = model.get("objects", [])
        procs = model.get("processes", [])
        h1("Configuration")
        rich(doc.add_paragraph(),
             f"{len(objs)} objects — {sum(o['status'] == 'new' for o in objs)} new, "
             f"{sum(o['status'] == 'extended' for o in objs)} extended, {sum(o['status'] == 'existing' for o in objs)} reused as is · "
             f"{len(model.get('lookups', []))} lookups · {len(procs)} processes · {len(model.get('ai', []))} AI actions. "
             "Step references (UC1.4) point at the use-case steps in the Demo Script. *Existing* is checked against the product object model; the build re-checks it on the stand.", SLATE)

        if model.get("ai"):
            h2chip("AI actions")
            table(["Action", "Trigger", "Input → output", "Stored in · review", "Real?", "Steps"],
                  [[f"**{a.get('name', '')}**" + (f" *({a['kind']})*" if a.get("kind") else ""), a.get("trigger", ""),
                    f"{a.get('inputs', '')} → {a.get('output', '')}", f"{a.get('stored_in', '')} · {a.get('review', '')}",
                    REAL.get(a.get("realization"), a.get("realization", "")), steps_txt(a)] for a in model["ai"]],
                  [1500, 1500, 2400, 2000, 800, 826])
            for a in model["ai"]:
                if a.get("example_output") or a.get("audience_sees"):
                    p = doc.add_paragraph()
                    rich(p, f"**{a.get('name')}** — audience sees: {a.get('audience_sees', '')}")
                    if a.get("example_output"):
                        callout(f"*{a['example_output']}*", PRIMARY_050, PRIMARY_600, label="EXAMPLE OUTPUT")

        if objs:
            h2chip("Object model")
            table(["Object", "Status", "Depth", "Purpose", "Steps"],
                  [[f"**{o.get('caption') or o['code']}**" + ("" if (o.get("caption") or o["code"]) == o["code"] else f" ({o['code']})"),
                    STATUS.get(o["status"], o["status"]), o.get("depth", ""),
                    o.get("purpose", "") + (f" *Why not OOTB: {o['why_not_ootb']}*" if o.get("why_not_ootb") else "")
                    + (f" *Renamed: {o['rename']}*" if o.get("rename") else ""), steps_txt(o)] for o in objs],
                  [2000, 900, 1300, 3626, 1200])
            for o in objs:
                cols = o.get("columns", [])
                if not cols:
                    continue
                cap = o.get("caption") or o["code"]
                doc.add_paragraph(cap if cap == o["code"] else f"{cap} — {o['code']}", style="Heading 3")
                rows = []
                for c in cols:
                    t = norm_type(c.get("type"))
                    vals = ""
                    if t in ("lookup", "detail") and c.get("ref"):
                        tgt = c["ref"]
                        if tgt in lookups_by:
                            vs = lookups_by[tgt].get("values", [])
                            vals = f"{tgt}: " + " / ".join(vs[:12]) + (" / …" if len(vs) > 12 else "")
                        else:
                            vals = f"→ {(objects_by.get(tgt, {}).get('caption') or tgt)}"
                    if c.get("formula"):
                        vals = (vals + " · " if vals else "") + f"= {c['formula']}"
                    req = " *(required)*" if c.get("required") else ""
                    rows.append([f"**{c.get('caption') or c['code']}**{req}", c["code"], c.get("type", ""), vals or c.get("note", ""),
                                 STATUS.get(c.get("status"), c.get("status", "")), steps_txt(c)])
                table(["Column", "Code", "Type", "Values / points to / purpose", "Status", "Steps"], rows, [1800, 1500, 900, 2826, 800, 1200])
        if model.get("lookups"):
            h2chip("Lookups")
            rows = []
            for l in model["lookups"]:
                newv = set(l.get("new_values") or [])
                rows.append([f"{l.get('caption') or l['code']} ({l['code']})", STATUS.get(l["status"], l["status"]),
                             " / ".join(f"**{v}**" if v in newv else v for v in l.get("values", []))])
            table(["Lookup", "Status", "Values (in order; values added to a stock lookup in bold)"], rows, [2600, 1000, 5426])
        if model.get("ui"):
            h2chip("Pages, buttons and navigation")
            table(["Element", "Kind", "Where", "Does", "Steps"],
                  [[f"**{x.get('name', '')}**", x.get("kind", ""), x.get("where", ""), x.get("does", ""), steps_txt(x)] for x in model["ui"]],
                  [2000, 1300, 2000, 2526, 1200])
        for d in model.get("dashboards", []):
            h2chip(f"Dashboard — {d.get('name', '')}")
            rich(doc.add_paragraph(), f"*{d.get('location', '')} · supports steps {steps_txt(d)}*")
            table(["Widget", "Type", "Data source (object, aggregation, filter, grouping)", "Shows", "Seed"],
                  [[f"**{w.get('name', '')}**", w.get("type", ""), w.get("source", ""), w.get("example", ""), w.get("seed", "")] for w in d.get("widgets", [])],
                  [1800, 1100, 3326, 1800, 1000])
        for d in model.get("dcm", []):
            h2chip(f"Case management (DCM) — {d.get('name', d.get('object'))}")
            rich(doc.add_paragraph(), f"*{d.get('object')}" + (f" where {d['condition']}" if d.get("condition") else "")
                 + f", stage column {d.get('stage_column')} · supports steps {steps_txt(d)} · "
                                      "stages with steps are configured by hand in the Case Designer; DCM has no gateways.*")
            table(["#", "Stage", "Stage elements", "Required to leave", "Scope"],
                  [[i, f"**{s.get('name')}**", "; ".join(s.get("elements", [])), "; ".join(s.get("exit_required", [])),
                    {"built": "built", "prefilled": "pre-filled record only", "simulated": "simulated"}.get(s.get("scope", "built"), s.get("scope", ""))]
                   for i, s in enumerate(d.get("stages", []), 1)], [450, 1800, 3626, 1900, 1250])
        if procs:
            h2chip("Business processes")
            table(["Process", "Trigger", "Does", "Audience sees", "Real? · build", "Steps"],
                  [[f"**{p.get('name', '')}**", p.get("trigger", ""),
                    " → ".join(p.get("actions", [])) + (f" *(writes {p['writes']})*" if p.get("writes") else "") + (f" *Simulated: {p['simulation']}*" if p.get("simulation") else ""),
                    p.get("audience_sees", ""), f"{REAL.get(p.get('realization'), p.get('realization', ''))} · {'from code' if p.get('build') == 'code' else 'designer-only'}",
                    steps_txt(p)] for p in procs],
                  [1600, 1500, 2526, 1700, 1000, 700])
        if model.get("rules"):
            h2chip("Business rules")
            table(["Rule", "Where", "When", "Effect", "Real?", "Steps"],
                  [[f"**{r.get('name', '')}**", f"{r.get('page') or r.get('object', '')} ({r.get('level', '')})", r.get("condition") or r.get("trigger", ""),
                    r.get("effect", ""), REAL.get(r.get("realization"), r.get("realization", "")), steps_txt(r)] for r in model["rules"]],
                  [1900, 1600, 1700, 2226, 800, 800])
        if model.get("integrations"):
            h2chip("Integrations")
            table(["Integration", "Stands for", "How it is shown", "Populates", "Real?", "Steps"],
                  [[f"**{i.get('name', '')}**", i.get("system", ""),
                    (i.get("pattern") or i.get("simulation") or "") + (f" — timeline note *\"{i['timeline_note']}\"*" if i.get("timeline_note") else ""),
                    i.get("populates", ""), REAL.get(i.get("realization"), i.get("realization", "")), steps_txt(i)] for i in model["integrations"]],
                  [1600, 1500, 2726, 1600, 800, 800])
        if model.get("notifications"):
            h2chip("Notifications")
            table(["ID", "Trigger → recipient", "Channel", "Copy", "Real?", "Steps"],
                  [[f"**{n.get('id', '')}** {n.get('name', '')}", f"{n.get('trigger', '')} → {n.get('recipient', '')}", n.get("channel", ""),
                    n.get("copy", ""), REAL.get(n.get("realization"), n.get("realization", "")), steps_txt(n)] for n in model["notifications"]],
                  [1500, 2000, 900, 3026, 800, 800])
        if model.get("slas"):
            h2chip("SLAs and clocks")
            table(["Clock", "Duration", "Starts", "Stops", "Shown in", "Steps"],
                  [[f"**{s.get('name', '')}**", s.get("duration", ""), s.get("start", ""), s.get("stop", ""), s.get("shown_in", ""), steps_txt(s)]
                   for s in model["slas"]], [1800, 1000, 1700, 1700, 2026, 800])

        # ---- demo data summary
        if data:
            h1("Demo data")
            rich(doc.add_paragraph(), f"{sum(len(b.get('records', [])) for b in data)} records, import-ready in "
                                      f"**{safe_name(client)}_Demo_Data.xlsx** (one sheet per object, hero records highlighted, "
                                      f"dates relative to the demo day {meta.get('date', '')}). Every number on screen comes from this data.",
                 SLATE).paragraph_format.keep_with_next = True
            rows = []
            for b in data:
                o = objects_by.get(b["object"], {})
                dc = display_column(o)
                mains = ", ".join(str(r.get(dc, r.get("_key", ""))) for r in b.get("records", []) if r.get("_main"))
                mains_l = [rec_label(b["object"], r) for r in b.get("records", []) if r.get("_main")]
                rows.append([f"**{o.get('caption') or b['object']}**", len(b.get("records", [])), shorten(mains_l), b.get("purpose", "")])
            table(["Object", "Records", "Hero records", "Why"], rows, [2000, 900, 3026, 3100])

    # ---- decisions, questions
    if part == "script":
        if spec.get("decisions"):
            h1("Decisions taken")
            rich(doc.add_paragraph(), "What this script shows differently from the request, and what was decided where the material was silent.", SLATE)
            doc.paragraphs[-1].paragraph_format.keep_with_next = True
            table(["Kind", "Decision", "Why", "Where"],
                  [[d.get("kind", "decision"), d.get("text", ""), d.get("why", ""), d.get("where", "")] for d in spec["decisions"]],
                  [1100, 3800, 3126, 1000])
        qs = spec.get("questions", [])
        if qs:
            h1("Questions for you")
            rich(doc.add_paragraph(), "Each question already has a default applied — the script is written to it. Answer only where the default is wrong.", SLATE)
            doc.paragraphs[-1].paragraph_format.keep_with_next = True
            table(["#", "Where", "Question", "Default applied", "Who"],
                  [[q["id"], q.get("where", ""), q["text"], q["default"], q.get("who", "")] for q in qs],
                  [550, 1100, 3700, 2900, 776])

        # ---- appendices: content assets the demo opens or the AI is grounded on
        for i, ap in enumerate(spec.get("appendix", []), 1):
            if i == 1:
                doc.add_page_break()
            h1(f"Appendix {i} — {ap.get('title', '')}")
            if ap.get("kind"):
                rich(doc.add_paragraph(), f"*{ap['kind']}*", SLATE)
            for para in str(ap.get("text", "")).split("\n"):
                if para.strip():
                    rich(doc.add_paragraph(), para.strip())
    doc.save(path)


# ======================================================================= XLSX
def xlsx_styles():
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

    thin = Side(style="thin", color=HAIRLINE)
    return {
        "head_font": Font(name="Segoe UI", bold=True, color="FFFFFF", size=9),
        "head_fill": PatternFill("solid", fgColor=PRIMARY_600),
        "body_font": Font(name="Segoe UI", size=9, color=INK),
        "alt_fill": PatternFill("solid", fgColor=ROW_ALT),
        "main_fill": PatternFill("solid", fgColor=AMBER_BG),
        "border": Border(left=thin, right=thin, top=thin, bottom=thin),
        "wrap": Alignment(wrap_text=True, vertical="top"),
        "status": {
            "new": PatternFill("solid", fgColor="D5EFEC"),
            "extended": PatternFill("solid", fgColor="FBEBD0"),
            "existing": PatternFill("solid", fgColor="EDF0F2"),
        },
        "title_font": Font(name="Segoe UI Semibold", size=14, color=PRIMARY_800),
        "label_font": Font(name="Segoe UI", bold=True, size=9, color=PRIMARY_600),
    }


def write_sheet(wb, title, headers, rows, widths=None, status_col=None, main_rows=None, header_notes=None, number_formats=None):
    from openpyxl.comments import Comment
    from openpyxl.utils import get_column_letter

    S = xlsx_styles()
    ws = wb.create_sheet(title[:31])
    ws.append(headers)
    for i, h in enumerate(headers, 1):
        c = ws.cell(row=1, column=i)
        c.font, c.fill, c.border, c.alignment = S["head_font"], S["head_fill"], S["border"], S["wrap"]
        if header_notes and header_notes.get(h):
            c.comment = Comment(header_notes[h], "demo-script")
    for r_i, row in enumerate(rows, 2):
        ws.append(row)
        for c_i in range(1, len(headers) + 1):
            c = ws.cell(row=r_i, column=c_i)
            c.font, c.border, c.alignment = S["body_font"], S["border"], S["wrap"]
            if main_rows and (r_i - 2) in main_rows:
                c.fill = S["main_fill"]
            elif r_i % 2 == 1:
                c.fill = S["alt_fill"]
            if number_formats and headers[c_i - 1] in number_formats:
                c.number_format = number_formats[headers[c_i - 1]].get(r_i - 2, c.number_format) if isinstance(number_formats[headers[c_i - 1]], dict) else number_formats[headers[c_i - 1]]
        if status_col is not None:
            v = str(row[status_col]).lower()
            if v in S["status"]:
                ws.cell(row=r_i, column=status_col + 1).fill = S["status"][v]
    for i, h in enumerate(headers, 1):
        w = (widths or {}).get(h) if isinstance(widths, dict) else (widths[i - 1] if widths else None)
        if not w:
            longest = max([len(str(h))] + [len(str(r[i - 1])) for r in rows if i - 1 < len(r) and r[i - 1] is not None] or [10])
            w = min(max(10, longest + 2), 60)
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "A2"
    if rows:
        ws.auto_filter.ref = f"A1:{get_column_letter(len(headers))}{len(rows) + 1}"
    return ws


def summary_sheet(wb, title, heading, pairs):
    S = xlsx_styles()
    ws = wb.active
    ws.title = title
    ws["A1"] = heading
    ws["A1"].font = S["title_font"]
    r = 3
    for k, v in pairs:
        ws.cell(row=r, column=1, value=k).font = S["label_font"]
        c = ws.cell(row=r, column=2, value=v)
        c.font, c.alignment = S["body_font"], S["wrap"]
        r += 1
    ws.column_dimensions["A"].width = 26
    ws.column_dimensions["B"].width = 110
    return ws


def steps_str(x):
    return ", ".join(x.get("steps", []) or [])


def build_model_xlsx(spec, path):
    from openpyxl import Workbook

    meta, model = spec["meta"], spec.get("model", {})
    objs = model.get("objects", [])
    wb = Workbook()
    summary_sheet(wb, "Summary", f"{meta['client']} — Object model", [
        ("Version", f"{meta.get('version', 'v1')} · {meta.get('date', '')}"),
        ("Objects", f"{len(objs)} — {sum(o['status'] == 'new' for o in objs)} new, {sum(o['status'] == 'extended' for o in objs)} extended (new columns on an OOTB object), {sum(o['status'] == 'existing' for o in objs)} reused as is"),
        ("Columns", f"{sum(len(o.get('columns', [])) for o in objs)} listed — {sum(c.get('status') == 'new' for o in objs for c in o.get('columns', []))} new"),
        ("Lookups", f"{len(model.get('lookups', []))} — {sum(l['status'] == 'new' for l in model.get('lookups', []))} new"),
        ("Dashboards", str(len(model.get("dashboards", [])))),
        ("DCM cases", f"{len(model.get('dcm', []))} — a DCM whose stages carry steps is built by hand in the Case Designer"),
        ("Processes", f"{len(model.get('processes', []))} — {sum(p.get('build') == 'code' for p in model.get('processes', []))} buildable from code, {sum(p.get('build') == 'designer' for p in model.get('processes', []))} designer-only"),
        ("Business rules", str(len(model.get("rules", [])))),
        ("AI", str(len(model.get("ai", [])))),
        ("Status legend", "new = create in the working package · extended = OOTB object, new columns added via replacing object · existing = reuse as is"),
        ("Step references", "UC<n>.<step> — the step numbers of the Demo Script; they never renumber"),
        ("Caveat", "'existing' is checked against the product object model, not the stand. The build re-audits every claim against the live instance and its verdict wins."),
    ])
    write_sheet(wb, "Objects", ["Code", "Caption", "Status", "Section", "Purpose", "New columns", "Steps"],
                [[o["code"], o.get("caption", ""), o["status"], o.get("section", ""), o.get("purpose", ""),
                  sum(c.get("status") == "new" for c in o.get("columns", [])), steps_str(o)] for o in objs],
                widths=[22, 24, 10, 18, 50, 12, 30], status_col=2)
    write_sheet(wb, "Columns", ["Object", "Column code", "Caption", "Type", "Points to", "Status", "Required", "Steps", "Note"],
                [[o["code"], c["code"], c.get("caption", ""), c.get("type", ""), c.get("ref", "") or "", c.get("status", ""),
                  "yes" if c.get("required") else "", steps_str(c), c.get("note", "")] for o in objs for c in o.get("columns", [])],
                widths=[20, 24, 26, 14, 22, 10, 9, 26, 40], status_col=5)
    lk_rows = []
    for l in model.get("lookups", []):
        colors = l.get("colors", {})
        for i, v in enumerate(l.get("values", []), 1):
            lk_rows.append([l["code"], l.get("caption", ""), l["status"], i, v, colors.get(v, ""), steps_str(l) if i == 1 else ""])
    write_sheet(wb, "Lookups", ["Lookup", "Caption", "Status", "Order", "Value", "Color", "Steps"], lk_rows,
                widths=[24, 24, 10, 7, 32, 10, 30], status_col=2)
    write_sheet(wb, "Dashboards", ["Dashboard", "Location", "Widget", "Type", "Data source", "Example value", "Steps"],
                [[d.get("name", ""), d.get("location", ""), w.get("name", ""), w.get("type", ""), w.get("source", ""), w.get("example", ""), steps_str(d)]
                 for d in model.get("dashboards", []) for w in d.get("widgets", [])],
                widths=[24, 18, 26, 14, 50, 14, 24])
    dcm_rows = []
    for d in model.get("dcm", []):
        for i, s in enumerate(d.get("stages", []), 1):
            dcm_rows.append([d.get("name", d.get("object")), d.get("object"), d.get("stage_column"), i, s.get("name"),
                             "; ".join(s.get("elements", [])), "; ".join(s.get("exit_required", [])), steps_str(d) if i == 1 else ""])
    write_sheet(wb, "DCM", ["DCM case", "Object", "Stage column", "Order", "Stage", "Stage elements", "Required to leave", "Steps"], dcm_rows,
                widths=[22, 16, 14, 7, 22, 50, 30, 24])
    write_sheet(wb, "Processes", ["Process", "Trigger", "Actions (in order)", "Writes", "Build", "Steps", "Note"],
                [[p.get("name", ""), p.get("trigger", ""), "\n".join(f"{i}. {a}" for i, a in enumerate(p.get("actions", []), 1)),
                  p.get("writes", ""), p.get("build", ""), steps_str(p), p.get("note", "")] for p in model.get("processes", [])],
                widths=[28, 34, 60, 30, 10, 22, 30])
    write_sheet(wb, "Rules", ["Rule", "Object / page", "Level", "Trigger", "Condition", "Effect", "Steps"],
                [[r.get("name", ""), r.get("page") or r.get("object", ""), r.get("level", ""), r.get("trigger", ""), r.get("condition", ""), r.get("effect", ""), steps_str(r)]
                 for r in model.get("rules", [])], widths=[26, 24, 9, 22, 34, 34, 20])
    write_sheet(wb, "AI", ["Name", "Kind", "Purpose", "Inputs", "Output", "Steps"],
                [[a.get("name", ""), a.get("kind", ""), a.get("purpose", ""), a.get("inputs", ""), a.get("output", ""), steps_str(a)] for a in model.get("ai", [])],
                widths=[26, 20, 50, 30, 30, 20])
    write_sheet(wb, "Decisions", ["Kind", "Decision", "Why", "Where"],
                [[d.get("kind", "decision"), d.get("text", ""), d.get("why", ""), d.get("where", "")] for d in spec.get("decisions", [])],
                widths=[12, 60, 50, 16])
    write_sheet(wb, "Questions", ["#", "Where", "Question", "Default applied", "Who decides"],
                [[q["id"], q.get("where", ""), q["text"], q.get("default", ""), q.get("who", "")] for q in spec.get("questions", [])],
                widths=[6, 16, 60, 50, 14])
    wb.save(path)


def import_order(spec):
    """Objects ordered so that every lookup target among the seeded objects is loaded first."""
    model_objs = {o["code"]: o for o in spec.get("model", {}).get("objects", [])}
    blocks = OrderedDict((b["object"], b) for b in spec.get("data", []))
    deps = {}
    for oc in blocks:
        cols = model_objs.get(oc, {}).get("columns", [])
        deps[oc] = {c.get("ref") for c in cols if norm_type(c.get("type")) == "lookup" and c.get("ref") in blocks and c.get("ref") != oc}
    order, done = [], set()
    while len(order) < len(blocks):
        progress = False
        for oc in blocks:
            if oc not in done and deps[oc] <= done:
                order.append(oc)
                done.add(oc)
                progress = True
        if not progress:  # cycle: keep source order for the rest
            order += [oc for oc in blocks if oc not in done]
            break
    return order


def second_pass(spec, order):
    """Lookup columns whose target is imported later (a reference cycle): fill them in a second import pass."""
    pos = {oc: i for i, oc in enumerate(order)}
    model_objs = {o["code"]: o for o in spec.get("model", {}).get("objects", [])}
    late = []
    for oc in order:
        for c in model_objs.get(oc, {}).get("columns", []):
            ref = c.get("ref")
            if norm_type(c.get("type")) == "lookup" and ref in pos and pos[ref] > pos[oc]:
                late.append(f"{oc}.{c['code']}")
    return late


def build_data_xlsx(spec, path):
    from openpyxl import Workbook

    meta = spec["meta"]
    anchor = anchor_date(spec)
    model_objs = {o["code"]: o for o in spec.get("model", {}).get("objects", [])}
    lookups = spec.get("model", {}).get("lookups", [])
    blocks = {b["object"]: b for b in spec.get("data", [])}
    order = import_order(spec)
    late = second_pass(spec, order)
    # @key -> display value
    disp_of = {}
    for oc, b in blocks.items():
        dc = display_column(model_objs.get(oc, {}))
        for r in b.get("records", []):
            if r.get("_key"):
                disp_of[r["_key"]] = r.get(dc, r["_key"])

    total = sum(len(b.get("records", [])) for b in blocks.values())
    wb = Workbook()
    summary_sheet(wb, "Summary", f"{meta['client']} — Demo data", [
        ("Version", f"{meta.get('version', 'v1')} · {meta.get('date', '')}"),
        ("Records", f"{total} across {len(blocks)} objects"),
        ("Dates", f"Relative dates (today±N) resolved against {anchor.isoformat()}. Re-run build_outputs.py with a new meta.date to shift every date."),
        ("Main demo records", "Highlighted rows: the records the script names and shows on screen — spelled exactly as in the steps."),
        ("Import order", " → ".join(order) + "  (lookup targets first)"),
        ("Second pass", ", ".join(late) + " — reference cycle: fill these columns in a second import pass, after their targets exist" if late else "none"),
        ("Lookup values sheet", "Values to CREATE: every value of a new lookup, and only the new_values of an extended stock lookup."),
        ("Lookup columns", "Hold the display value of the target record or lookup value, as Creatio Excel import matches them."),
        ("Demo key", "Last column on each sheet: the record's id inside this package, used for cross-references. Import it into a "
                     "text column (or keep the sheet as the mapping): where a lookup cell holds a Demo key instead of a name — targets "
                     "whose names repeat, such as visits or order lines — match that column on Demo key, not by name. Header comments "
                     "on those columns say so."),
    ])
    write_sheet(wb, "Objects", ["Order", "Object", "Caption", "Sheet", "Records", "Main records", "Purpose"],
                [[i, oc, model_objs.get(oc, {}).get("caption", oc), (model_objs.get(oc, {}).get("caption") or oc)[:31],
                  len(blocks[oc].get("records", [])), sum(1 for r in blocks[oc].get("records", []) if r.get("_main")),
                  blocks[oc].get("purpose", "")] for i, oc in enumerate(order, 1)],
                widths=[7, 22, 24, 24, 9, 12, 60])
    lv_rows = [[l["code"], l.get("caption", ""), l["status"], v, l.get("colors", {}).get(v, "")]
               for l in lookups if l.get("status") in ("new", "extended")
               for v in (l.get("values", []) if l["status"] == "new" else l.get("new_values", []))]
    if lv_rows:
        write_sheet(wb, "Lookup values", ["Lookup", "Caption", "Status", "Value", "Color"], lv_rows,
                    widths=[24, 24, 10, 32, 10], status_col=2)
    used_titles = set()
    for oc in order:
        o = model_objs.get(oc, {})
        recs = blocks[oc].get("records", [])
        cols = [c for c in o.get("columns", []) if norm_type(c.get("type")) != "detail"]
        present = {k for r in recs for k in r if not k.startswith("_")}
        cols = [c for c in cols if c["code"] in present]
        headers = [c.get("caption") or c["code"] for c in cols] + ["Demo key"]
        notes = {(c.get("caption") or c["code"]): f"{oc}.{c['code']} · {c.get('type', '')}" + (f" → {c['ref']}" if c.get("ref") else "") for c in cols}
        rows, main, formats = [], set(), {}
        for i, r in enumerate(recs):
            row = []
            for c in cols:
                v = r.get(c["code"])
                t = norm_type(c.get("type"))
                if isinstance(v, str) and v.startswith("@") and model_objs.get(c.get("ref"), {}).get("allow_duplicate_names"):
                    notes[c.get("caption") or c["code"]] = notes.get(c.get("caption") or c["code"], "") + \
                        " · names repeat on the target: holds its Demo key — match on Demo key, not by name"
                    v = v[1:]
                if isinstance(v, str) and v.startswith("@"):
                    v = disp_of.get(v[1:], v)
                if t in ("date", "date/time"):
                    v = resolve_date(v, anchor)
                    if isinstance(v, str):
                        try:
                            v = datetime.fromisoformat(v) if t == "date/time" else date.fromisoformat(v[:10])
                        except ValueError:
                            pass
                    cap = c.get("caption") or c["code"]
                    formats[cap] = "yyyy-mm-dd hh:mm" if t == "date/time" else "yyyy-mm-dd"
                if t == "percentage":
                    formats[c.get("caption") or c["code"]] = "0.0"
                if t == "currency":
                    formats[c.get("caption") or c["code"]] = "#,##0.00"
                row.append(v)
            row.append(r.get("_key", ""))
            if r.get("_main"):
                main.add(i)
            rows.append(row)
        title = (o.get("caption") or oc)[:31]
        while title in used_titles or title in ("Summary", "Objects", "Lookup values"):
            title = (title[:28] + "_" + str(len(used_titles)))[:31]
        used_titles.add(title)
        write_sheet(wb, title, headers, rows, main_rows=main, header_notes=notes, number_formats=formats)
    wb.save(path)


# ======================================================================= REQUIREMENTS.MD
def build_requirements(spec, path, files):
    meta, model = spec["meta"], spec.get("model", {})
    L = []
    a = L.append
    a(f"# {meta['client']} — requirements (from the demo script package)\n")
    a(f"_Generated by creatio-demo-script-generator {meta.get('version', 'v1')} · {meta.get('date', '')}. "
      "Input for `creatio-demo-build` phase 1 — the 'derive' route is already done here; reconcile against the instance._\n")
    a("**Files:** " + " · ".join(f"`{f}`" for f in files) + "\n")
    a("## Scope\n")
    a("| UC | Name | Persona | Entry points | Steps |")
    a("|---|---|---|---|---|")
    for u in spec["use_cases"]:
        n = sum(1 for i in u.get("items", []) if "step" in i)
        a(f"| {u['id']} | {u['name']} | {u.get('persona', '')} | {', '.join(u.get('entry_points', []))} | {n} |")
    inst = meta.get("instance") or {}
    a(f"\n**Instance:** {inst.get('name', '')} {inst.get('url', '')} — mode **{inst.get('mode', '?')}**"
      + (f", reference demo {inst['reference_demo']}" if inst.get("reference_demo") else "")
      + (f". Previous demos: {inst['previous_demos']}" if inst.get("previous_demos") else "") + "\n")
    a("Credentials are in the team credential store — never in this file.\n")
    deal = meta.get("deal") or {}
    if isinstance(deal.get("arr_usd"), (int, float)):
        t = tier_of(deal["arr_usd"])
        used = usage(spec)
        a(f"**Deal tier:** {t['label']} — ARR {deal['arr_usd']:,.0f} USD" + (" (assumed)" if deal.get("arr_assumed") else "")
          + f". {t['intent']}\n")
        a("Budget used / allowed: " + " · ".join(f"{k} {used[k]}/{'no cap' if v is None else v}" for k, v in t["budget"].items()) + "\n")
        for x in deal.get("exceptions", []):
            a(f"- budget exception **{x.get('budget')}**: {x.get('why')}")
    if spec.get("roles"):
        a("## Roles and logins\n")
        a("| Role | Login mode | Login | Workplace | Use cases |")
        a("|---|---|---|---|---|")
        for r in spec["roles"]:
            a(f"| {r.get('name', '')} | {r.get('login_mode', '')} | {r.get('login', '')} | {r.get('workplace', '')} | {', '.join(r.get('use_cases', []))} |")
    if spec.get("ground_rules"):
        a("\n## Ground rules\n")
        for g in spec["ground_rules"]:
            a(f"- {g}")
    prio = sorted([u for u in spec["use_cases"] if u.get("priority")], key=lambda u: {"must": 0, "should": 1, "could": 2}.get(u["priority"], 3))
    if prio:
        a("\n**Protect in order if time runs short:** " + " → ".join(f"{u['id']} ({u['priority']})" for u in prio)
          + (f" · budget {meta['build_budget_h']} h" if meta.get("build_budget_h") else "") + "\n")
    if spec.get("out_of_scope"):
        a("## Out of scope — do not build\n")
        for x in spec["out_of_scope"]:
            a(f"- {x.get('item', '')} — {x.get('why', '')}")
    pre = spec.get("pre_demo", {})
    if pre:
        a("\n## Data state before the demo\n")
        for x in pre.get("must_exist", []):
            a(f"- exists: {x}")
        for x in pre.get("must_not_exist", []):
            a(f"- must NOT exist (created live): {x}")
        for x in pre.get("checks", []):
            a(f"- check: {x}")
    a("")
    a("## Objects\n")
    a("| Object | Caption | Action | Steps |")
    a("|---|---|---|---|")
    act = {"new": "NEW custom object (+ section, list and form pages)", "extended": "extend base object (replacing)", "existing": "reuse as is"}
    for o in model.get("objects", []):
        a(f"| `{o['code']}` | {o.get('caption', '')} | {act.get(o['status'], o['status'])} | {steps_str(o)} |")
    for o in model.get("objects", []):
        new_cols = [c for c in o.get("columns", []) if c.get("status") == "new"]
        if not new_cols:
            continue
        a(f"\n### {o['code']} — new columns\n")
        a("| Column | Caption | Type | Points to | Required | Steps |")
        a("|---|---|---|---|---|---|")
        for c in new_cols:
            a(f"| `{c['code']}` | {c.get('caption', '')} | {c.get('type', '')} | {c.get('ref') or ''} | {'yes' if c.get('required') else ''} | {steps_str(c)} |")
    a("\n## Lookups\n")
    users = {}
    for o in model.get("objects", []):
        for c in o.get("columns", []):
            if c.get("ref"):
                users.setdefault(c["ref"], []).append(o["code"])
    for l in model.get("lookups", []):
        shared = users.get(l["code"], [])
        tag = f" — shared by {', '.join(sorted(set(shared)))}" if len(set(shared)) > 1 else ""
        a(f"- `{l['code']}` ({l['status']}){tag}: " + " / ".join(f'"{v}"' for v in l.get("values", [])))
    if model.get("dcm"):
        a("\n## DCM — designer-only when stages carry steps\n")
        for d in model["dcm"]:
            a(f"- **{d.get('name', d['object'])}** on `{d['object']}`.`{d.get('stage_column')}`: " + " → ".join(s["name"] for s in d.get("stages", [])) + f"  ({steps_str(d)})")
    if model.get("processes"):
        a("\n## Processes\n")
        a("| Process | Trigger | Does | Real? | Audience sees | Build | Steps |")
        a("|---|---|---|---|---|---|---|")
        for p in model["processes"]:
            sim = f" (simulated: {p['simulation']})" if p.get("simulation") else ""
            a(f"| {p.get('name', '')} | {p.get('trigger', '')} | {' → '.join(p.get('actions', []))} | {p.get('realization', '')}{sim} | "
              f"{p.get('audience_sees', '')} | {'buildable from code' if p.get('build') == 'code' else 'designer-only'} | {steps_str(p)} |")
    if model.get("rules"):
        a("\n## Business rules\n")
        for r in model["rules"]:
            a(f"- **{r.get('name', '')}** ({r.get('level', '')}, {r.get('page') or r.get('object', '')}): when {r.get('condition', '')} → {r.get('effect', '')}  ({steps_str(r)})")
    if model.get("ui"):
        a("\n## Pages, buttons and navigation\n")
        a("| Element | Kind | Where | Does | Steps |")
        a("|---|---|---|---|---|")
        for x in model["ui"]:
            a(f"| {x.get('name', '')} | {x.get('kind', '')} | {x.get('where', '')} | {x.get('does', '')} | {steps_str(x)} |")
    if model.get("dashboards"):
        a("\n## Dashboards\n")
        for d in model["dashboards"]:
            a(f"- **{d.get('name', '')}** ({d.get('location', '')}): " + "; ".join(f"{w.get('name')} [{w.get('type')}]" for w in d.get("widgets", [])))
    if model.get("ai"):
        a("\n## AI actions\n")
        for x in model["ai"]:
            a(f"- **{x.get('name', '')}** ({x.get('kind', '')}, {x.get('realization', '')}) — {x.get('purpose', '')}  ({steps_str(x)})")
            a(f"  - trigger: {x.get('trigger', '')} · input: {x.get('inputs', '')} · output: {x.get('output', '')}")
            a(f"  - stored in: {x.get('stored_in', '')} · review: {x.get('review', '')} · audience sees: {x.get('audience_sees', '')}")
            if x.get("example_output"):
                a(f"  - example output: \"{x['example_output']}\"")
    if model.get("integrations"):
        a("\n## Integrations\n")
        for i in model["integrations"]:
            a(f"- **{i.get('name', '')}** stands for {i.get('system', '')} — {i.get('realization', '')}: {i.get('pattern') or i.get('simulation', '')}; "
              f"populates {i.get('populates', '')}" + (f"; timeline note \"{i['timeline_note']}\"" if i.get("timeline_note") else "") + f"  ({steps_str(i)})")
    if model.get("notifications"):
        a("\n## Notifications\n")
        for n in model["notifications"]:
            a(f"- **{n.get('id', '')} {n.get('name', '')}** — {n.get('trigger', '')} → {n.get('recipient', '')} via {n.get('channel', '')} ({n.get('realization', '')}): {n.get('copy', '')}")
    if model.get("slas"):
        a("\n## SLAs and clocks\n")
        for s_ in model["slas"]:
            a(f"- **{s_.get('name', '')}**: {s_.get('duration', '')}, starts {s_.get('start', '')}, stops {s_.get('stop', '')}, shown in {s_.get('shown_in', '')}")
    a("\n## Demo data\n")
    for oc in import_order(spec):
        b = next(b for b in spec["data"] if b["object"] == oc)
        main = sum(1 for r in b.get("records", []) if r.get("_main"))
        a(f"- `{oc}`: {len(b.get('records', []))} records ({main} main) — {b.get('purpose', '')}")
    a("\n## Decisions taken\n")
    for d in spec.get("decisions", []):
        a(f"- [{d.get('kind', 'decision')}] {d.get('text', '')} — {d.get('why', '')} ({d.get('where', '')})")
    a("\n## Open questions (default applied)\n")
    for q in spec.get("questions", []):
        a(f"- **{q['id']}** ({q.get('where', '')}, {q.get('who', '')}): {q['text']} → default: {q.get('default', '')}")
    a("\n## IMPLEMENTATION STATUS\n\n_(the build appends here)_\n")
    Path(path).write_text("\n".join(L), encoding="utf8")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    force = "--force" in args
    model_xlsx = "--model-xlsx" in args
    out = None
    if "--out" in args:
        i = args.index("--out")
        out = Path(args[i + 1])
        del args[i:i + 2]
    args = [x for x in args if not x.startswith("--")]
    if len(args) != 1:
        print(__doc__)
        sys.exit(2)
    spec_path = Path(args[0])
    out = out or spec_path.parent
    out.mkdir(parents=True, exist_ok=True)
    spec = json.loads(spec_path.read_text(encoding="utf8"))
    errors, warnings = validate(spec)
    for e in errors:
        print("ERROR  ", e)
    print(f"{len(errors)} errors, {len(warnings)} warnings (run validate_spec.py to see the warnings)")
    if errors and not force:
        print("Not building — fix the errors (or --force for a draft).")
        sys.exit(1)
    base = safe_name(spec["meta"]["client"])
    script, build_spec = f"{base}_Demo_Script.docx", f"{base}_Build_Spec.docx"
    data_x, req = f"{base}_Demo_Data.xlsx", f"{base}_requirements.md"
    spec = apply_date_tokens(spec, anchor_date(spec))
    build_docx(spec, out / script, part="script")
    build_docx(spec, out / build_spec, part="spec")
    from build_markdown import build_markdown  # same content as Markdown — reads on GitHub, in any editor, diffs cleanly
    script_md, build_spec_md = f"{base}_Demo_Script.md", f"{base}_Build_Spec.md"
    build_markdown(spec, out / script_md, part="script")
    build_markdown(spec, out / build_spec_md, part="spec")
    build_data_xlsx(spec, out / data_x)
    files = [script, script_md, build_spec, build_spec_md, data_x]
    if model_xlsx:
        files.append(f"{base}_Object_Model.xlsx")
        build_model_xlsx(spec, out / files[-1])
    build_requirements(spec, out / req, files + [spec_path.name])
    for f in files + [req]:
        print("->", out / f)


if __name__ == "__main__":
    main()
