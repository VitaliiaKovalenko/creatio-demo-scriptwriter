"""Render doc_model blocks as one self-contained HTML page — the shareable twin of the Markdown Demo Script.

Called by build_outputs.py (writes <Client>_Demo_Script.html next to the .md); can also run alone:
    python build_html.py <spec.json> [--out <dir>] [--external]

The page follows the Claude Artifact page contract, so it can be published as is with the Artifact tool:
<title> first, colour tokens with light and dark themes, an explicit body background, Google Fonts only,
no scripts, a 16px side gutter and tables that scroll inside their own box at phone width.
--external leaves out every section marked internal (competitive positioning, ideas from similar demos)
and writes <Client>_Demo_Script_external.html — the only version that may leave Creatio.
"""
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from doc_model import blocks, safe_name  # noqa: E402
from validate_spec import anchor_date  # noqa: E402

CSS = """
/* Layout: one reading column; on wide screens a section menu sticks beside it */
:root {
  --bg: #fbf9f7; --surface: #ffffff; --fg: #231d1f; --muted: #6b6064; --line: #e7dfda;
  --accent: #d0332a; --accent-soft: #fbe9e6; --warm: #f3ece7; --dark: #231d1f; --on-dark: #f6f1ee;
  --font-display: 'Montserrat', 'Segoe UI', Arial, sans-serif;
  --font-body: 'Nunito Sans', 'Segoe UI', Arial, sans-serif;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #1b1617; --surface: #241e20; --fg: #efe8e4; --muted: #b3a7ab; --line: #3a3134;
  --accent: #f0685c; --accent-soft: #3a2422; --warm: #2b2325; --dark: #0f0c0d; --on-dark: #f6f1ee; color-scheme: dark } }
:root[data-theme="dark"] {
  --bg: #1b1617; --surface: #241e20; --fg: #efe8e4; --muted: #b3a7ab; --line: #3a3134;
  --accent: #f0685c; --accent-soft: #3a2422; --warm: #2b2325; --dark: #0f0c0d; --on-dark: #f6f1ee; color-scheme: dark }
body { background: var(--bg); color: var(--fg); font: 16px/1.6 var(--font-body);
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); }
.wrap { max-width: 1180px; margin: 0 auto; padding-block: 40px 64px; display: grid; gap: 48px; grid-template-columns: minmax(0, 1fr); }
@media (min-width: 1080px) { .wrap { grid-template-columns: 220px minmax(0, 1fr); } }
nav.toc { display: none; }
@media (min-width: 1080px) { nav.toc { display: block; position: sticky; top: calc(24px + env(safe-area-inset-top, 0px)); align-self: start; } }
nav.toc p { font: 700 12px/1.4 var(--font-display); letter-spacing: .12em; text-transform: uppercase; color: var(--muted); margin: 0 0 12px; }
nav.toc ol { list-style: none; margin: 0; padding: 0; display: grid; gap: 6px; }
nav.toc a { color: var(--fg); text-decoration: none; font-size: 14px; display: block; padding: 4px 10px; border-radius: 6px; }
nav.toc a:hover, nav.toc a:focus-visible { background: var(--warm); outline: none; }
main { min-width: 0; max-width: 820px; display: grid; gap: 18px; }
header.doc { display: grid; gap: 10px; padding-bottom: 20px; border-bottom: 3px solid var(--accent); }
.eyebrow { font: 700 12px/1.4 var(--font-display); letter-spacing: .14em; text-transform: uppercase; color: var(--accent); margin: 0; }
h1, h2, h3 { font-family: var(--font-display); text-wrap: balance; margin: 0; }
h1 { font-size: clamp(30px, 5vw, 42px); line-height: 1.15; font-weight: 800; }
h2 { font-size: clamp(22px, 3.2vw, 28px); line-height: 1.25; font-weight: 700; margin-top: 28px; scroll-margin-top: 24px; }
h3 { font-size: 19px; line-height: 1.3; font-weight: 700; margin-top: 18px; }
p { margin: 0; }
.meta { color: var(--muted); font-size: 14px; }
.muted { color: var(--muted); font-size: 15px; }
code { font: 14px ui-monospace, Consolas, monospace; background: var(--warm); padding: 1px 5px; border-radius: 4px; }
a { color: var(--accent); }
.pill { display: inline-block; font: 700 11px/1 var(--font-display); letter-spacing: .1em; text-transform: uppercase;
  color: var(--accent); border: 1px solid var(--accent); border-radius: 999px; padding: 5px 9px; vertical-align: middle; margin-left: 8px; }
ul.bullets { margin: 0; padding-left: 22px; display: grid; gap: 4px; }
.step { display: grid; grid-template-columns: 34px minmax(0, 1fr); gap: 12px; align-items: start; }
.step .n { font: 700 14px/30px var(--font-display); text-align: center; height: 30px; border-radius: 50%;
  background: var(--accent-soft); color: var(--accent); font-variant-numeric: tabular-nums; }
.step .t { padding-top: 3px; }
.scene { font-style: italic; color: var(--muted); text-align: center; }
.callout { padding: 14px 18px; border-radius: 10px; background: var(--warm); border-left: 4px solid var(--muted); }
.callout b.label { font: 700 12px/1 var(--font-display); letter-spacing: .1em; text-transform: uppercase; margin-right: 8px; }
.callout.goal, .callout.value { background: var(--accent-soft); border-left-color: var(--accent); }
.callout.bubble { background: var(--surface); border: 1px solid var(--line); border-left: 4px solid var(--accent); font-style: italic; }
.callout.internal, .callout.gap { background: var(--dark); color: var(--on-dark); border-left-color: var(--accent); }
.scroll { overflow-x: auto; border: 1px solid var(--line); border-radius: 10px; background: var(--surface); }
table { border-collapse: collapse; width: 100%; font-size: 14.5px; }
th, td { text-align: left; vertical-align: top; padding: 9px 12px; border-bottom: 1px solid var(--line); }
th { font: 700 12px/1.3 var(--font-display); letter-spacing: .06em; text-transform: uppercase; color: var(--muted); background: var(--warm); }
tr:last-child td { border-bottom: 0; }
table.kv td:first-child { width: 28%; font-weight: 700; color: var(--fg); }
table.wide { min-width: 640px; }
hr { border: 0; border-top: 1px solid var(--line); margin: 24px 0 0; }
footer { color: var(--muted); font-size: 13px; padding-top: 24px; border-top: 1px solid var(--line); margin-top: 24px; }
:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
"""


def _inline(text):
    s = html.escape("" if text is None else str(text), quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", s)
    s = re.sub(r"(https?://[^\s<)]+)", r'<a href="\1">\1</a>', s)
    return s.replace("\n", "<br>")


def _drop_internal(bl):
    """Leave out every heading whose text says internal, with everything under it (for --external)."""
    out, skip = [], None
    rank = {"h1": 1, "h2": 2}
    for b in bl:
        if b[0] in rank:
            if skip and rank[b[0]] <= skip:
                skip = None
            if skip is None and "internal" in b[1].lower():
                skip = rank[b[0]]
                continue
        if skip is None and not (b[0] == "callout" and b[2] == "internal"):
            out.append(b)
    return out


def render(bl, path, title):
    toc, body, in_bullets = [], [], False
    for b in bl:
        k = b[0]
        if k != "bullet" and in_bullets:
            body.append("</ul>")
            in_bullets = False
        if k == "title":
            continue
        if k == "meta":
            body.append(f'<p class="meta">{_inline(b[1])}</p>')
        elif k == "h1":
            sid = f"s{len(toc) + 1}"
            label = re.sub(r"\s+[—-]\s+internal$", "", b[1], flags=re.I)
            toc.append((sid, label))
            pill = '<span class="pill">Internal</span>' if label != b[1] else ""
            body.append(f'<h2 id="{sid}">{_inline(label)}{pill}</h2>')
        elif k == "h2":
            label = re.sub(r"\s+[—-]\s+internal$", "", b[1], flags=re.I)
            pill = '<span class="pill">Internal</span>' if label != b[1] else ""
            body.append(f"<h3>{_inline(label)}{pill}</h3>")
        elif k == "p":
            body.append(f"<p>{_inline(b[1])}</p>")
        elif k == "p_muted":
            body.append(f'<p class="muted">{_inline(b[1])}</p>')
        elif k == "bullet":
            if not in_bullets:
                body.append('<ul class="bullets">')
                in_bullets = True
            body.append(f"<li>{_inline(b[1])}</li>")
        elif k == "step":
            body.append(f'<div class="step"><span class="n">{b[1]}</span><div class="t">{_inline(b[2])}</div></div>')
        elif k == "scene":
            body.append(f'<p class="scene">{_inline(b[1])}</p>')
        elif k == "callout":
            label = f'<b class="label">{html.escape(b[3])}</b>' if b[3] else ""
            body.append(f'<div class="callout {html.escape(b[2] or "note")}">{label}{_inline(b[1])}</div>')
        elif k == "kv":
            rows = "".join(f"<tr><td>{_inline(r[0])}</td><td>{_inline(r[1])}</td></tr>" for r in b[1] if r[1])
            if rows:
                body.append(f'<div class="scroll"><table class="kv">{rows}</table></div>')
        elif k == "table":
            cls = ' class="wide"' if len(b[1]) > 3 else ""
            head = "".join(f"<th>{_inline(h)}</th>" for h in b[1])
            rows = "".join("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in r) + "</tr>" for r in b[2])
            body.append(f'<div class="scroll"><table{cls}><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>')
        elif k == "pagebreak":
            body.append("<hr>")
    if in_bullets:
        body.append("</ul>")
    nav = "".join(f'<li><a href="#{sid}">{_inline(label)}</a></li>' for sid, label in toc)
    page = (
        f"<title>{html.escape(title)}</title>\n"
        '<meta name="claude:viewport-fit-sides" content="cover">\n'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700;800'
        '&family=Nunito+Sans:ital,wght@0,400;0,700;1,400&display=swap">\n'
        f"<style>{CSS}</style>\n"
        '<div class="wrap">\n'
        f'<nav class="toc" aria-label="Sections"><p>Sections</p><ol>{nav}</ol></nav>\n'
        "<main>\n"
        f'<header class="doc"><p class="eyebrow">Creatio · Demo Script</p><h1>{html.escape(title)}</h1></header>\n'
        + "\n".join(body)
        + "\n<footer>Creatio Demo Build · Confidential · generated from spec.json by creatio-demo-scriptwriter</footer>\n"
        "</main>\n</div>\n"
    )
    Path(path).write_text(page, encoding="utf8")


def build_html(spec, path, external=False):
    bl = blocks(spec, "script")
    if external:
        bl = _drop_internal(bl)
    render(bl, path, f"{spec['meta']['client']} Demo Script")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(2)
    external = "--external" in args
    out = None
    if "--out" in args:
        i = args.index("--out")
        out = Path(args[i + 1])
        del args[i:i + 2]
    args = [a for a in args if not a.startswith("--")]
    spec_path = Path(args[0])
    out = out or spec_path.parent
    spec = json.loads(spec_path.read_text(encoding="utf8"))
    from build_outputs import apply_date_tokens
    spec = apply_date_tokens(spec, anchor_date(spec))
    name = f"{safe_name(spec['meta']['client'])}_Demo_Script{'_external' if external else ''}.html"
    build_html(spec, out / name, external)
    print("->", out / name)


if __name__ == "__main__":
    main()
