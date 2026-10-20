"""Render the Demo Script docx to PDF and page PNGs, so the agent can LOOK at it before delivery.

Usage:
    python render_check.py <file.docx> [--pages N]

Windows: drives Word through COM on a temporary COPY (the deliverable stays unlocked).
Elsewhere: soffice --headless --convert-to pdf. Then PyMuPDF writes <name>_p<k>.png for the first
N pages (default: all) into a _render folder beside the file (the PDF goes there too, so the
deliverable folder stays clean), and prints the PDF's page count plus
the paths to Read. Read the PNGs: a lost header, a table past the margin or a broken bubble is
visible only in the render.
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def to_pdf(docx, pdf):
    if os.name == "nt":
        tmp = Path(tempfile.mkdtemp()) / docx.name
        shutil.copy2(docx, tmp)
        ps = (
            "$ErrorActionPreference='Stop';"
            "$w=New-Object -ComObject Word.Application; $w.Visible=$false; $w.DisplayAlerts=0;"
            f"try {{ $d=$w.Documents.Open('{tmp}', $false, $true); $d.SaveAs2('{pdf}', 17); $d.Close(0) }}"
            " finally { $w.Quit() }"
        )
        r = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True, timeout=180)
        if r.returncode != 0:
            raise RuntimeError(r.stderr.strip() or r.stdout.strip())
    else:
        soffice = shutil.which("soffice") or shutil.which("libreoffice")
        if not soffice:
            raise RuntimeError("no Word and no LibreOffice — cannot render")
        subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", str(pdf.parent), str(docx)], check=True, timeout=180)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    docx = Path(sys.argv[1]).resolve()
    pages = int(sys.argv[sys.argv.index("--pages") + 1]) if "--pages" in sys.argv else 999
    out = docx.parent / "_render"
    out.mkdir(exist_ok=True)
    pdf = out / (docx.stem + ".pdf")
    to_pdf(docx, pdf)
    try:
        import pymupdf as fitz
    except ImportError:
        import fitz
    d = fitz.open(pdf)
    print(f"PDF: {pdf}  ({d.page_count} pages)")
    for i, page in enumerate(d):
        if i >= pages:
            break
        png = out / f"{docx.stem}_p{i + 1}.png"
        page.get_pixmap(dpi=110).save(png)
        print("PNG:", png)
    for n, page in enumerate(d, 1):
        text = page.get_text().replace("Click path", "")  # the template's own heading
        for word in ("click", "Click", " say ", "TBD", "Lorem"):
            i = text.find(word)
            if i >= 0:
                ctx = " ".join(text[max(0, i - 50):i + 50].split())
                print(f"warn: '{word.strip()}' on page {n}: …{ctx}…")


if __name__ == "__main__":
    main()
