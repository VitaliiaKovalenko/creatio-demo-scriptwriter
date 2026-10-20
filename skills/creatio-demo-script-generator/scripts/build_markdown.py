"""Render doc_model blocks as Markdown — the same outline as the Word documents.

Called by build_outputs.py (writes <Client>_Demo_Script.md and <Client>_Build_Spec.md next to the .docx);
can also run alone:
    python build_markdown.py <spec.json> [--out <dir>]

Step numbers are bold paragraphs ("**4.**"), not a Markdown list, so gaps and stable numbering survive every
renderer. Callouts are blockquotes with their label.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from doc_model import blocks, safe_name  # noqa: E402
from validate_spec import anchor_date  # noqa: E402


def _cell(v):
    return ("" if v is None else str(v)).replace("|", "\\|").replace("\r", "").replace("\n", "<br>")


def _table(headers, rows):
    out = ["| " + " | ".join(_cell(h) for h in headers) + " |", "|" + "---|" * len(headers)]
    out += ["| " + " | ".join(_cell(c) for c in r) + " |" for r in rows]
    return "\n".join(out) + "\n"


def render(bl, path):
    L = []
    for b in bl:
        k = b[0]
        if k == "title":
            L.append(f"# {b[1]}\n")
        elif k == "meta":
            L.append(f"*{b[1]}*\n")
        elif k == "h1":
            L.append(f"## {b[1]}\n")
        elif k == "h2":
            L.append(f"### {b[1]}\n")
        elif k in ("p", "p_muted"):
            L.append(b[1].replace("\n", "  \n") + "\n")
        elif k == "bullet":
            L.append(f"- {b[1]}")
        elif k == "step":
            L.append(f"**{b[1]}.** {b[2]}\n")
        elif k == "scene":
            L.append(f"*— {b[1]} —*\n")
        elif k == "callout":
            label = f"**{b[3]}** — " if b[3] else ""
            L.append("> " + label + b[1].replace("\n", "\n> ") + "\n")
        elif k == "kv":
            rows = [r for r in b[1] if r[1]]
            if rows:
                L.append(_table(["", ""], [[f"**{r[0]}**", r[1]] for r in rows]))
        elif k == "table":
            L.append(_table(b[1], b[2]))
        elif k == "pagebreak":
            L.append("---\n")
    out = []
    for i, line in enumerate(L):  # a blank line after a bullet run
        out.append(line)
        if line.startswith("- ") and (i + 1 == len(L) or not L[i + 1].startswith("- ")):
            out.append("")
    out.append("---\n*Creatio Demo Build — Confidential*\n")
    Path(path).write_text("\n".join(out), encoding="utf8")


def build_markdown(spec, path, part="script"):
    render(blocks(spec, part), path)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    out = None
    if "--out" in args:
        i = args.index("--out")
        out = Path(args[i + 1])
        del args[i:i + 2]
    spec_path = Path(args[0])
    out = out or spec_path.parent
    spec = json.loads(spec_path.read_text(encoding="utf8"))
    from build_outputs import apply_date_tokens
    spec = apply_date_tokens(spec, anchor_date(spec))
    base = safe_name(spec["meta"]["client"])
    for part, name in (("script", f"{base}_Demo_Script.md"), ("spec", f"{base}_Build_Spec.md")):
        build_markdown(spec, out / name, part)
        print("->", out / name)


if __name__ == "__main__":
    main()
