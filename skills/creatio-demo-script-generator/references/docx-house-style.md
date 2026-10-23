# The docx house style, and the mechanics that fail silently

> **Optional since v1.5.0.** The documents are Markdown by default; Word is built only with
> `build_outputs.py --docx`, when the user asks for it. The Word output uses the Creatio template
> (`creatio-template.docx`, rendered by `scripts/docx_render.py`); the mechanics below still apply to it.

Both output documents of this pipeline follow the same style. It is a contract, not a suggestion — the
consultants recognise these documents by their look, and a document that renders differently reads as someone
else's work.

**Current style since 2026-08-25: petrol / teal, Segoe UI, compact.** The red Arial style below it is the
legacy one; keep it only for documents already in circulation in that form.

## Palette

```javascript
const PRIMARY_800 = "123B54";  // deep petrol - title, H1, H2 text, inline emphasis
const PRIMARY_600 = "1C6B8C";  // mid azure - H3, bullets, rules, table header, use-case banner
const TEAL        = "0E8F86";  // green-teal accent - step numbers, banner edge, info callout bar
const PRIMARY_300 = "8FC0D4";  // hairline under H1 and in the running header
const PRIMARY_050 = "EFF6F9";  // chip fill, meta card, info callout
const ROW_ALT     = "F5F9FB";  // alternating table row
const HAIRLINE    = "D8E2E8";  // table borders, footer rule
const INK         = "16212E";  // body text
const SLATE       = "51626E";  // secondary text, notes
// callouts
const AMBER_TXT = "8A530C", AMBER_BAR = "C9861A", AMBER_BG = "FBF3E6";   // flags (stages 1 and 3 only)
const SLATE_BAR = "B9C4CC", SLATE_BG = "F3F5F7";                          // grey note
```

## Type and rhythm

- Font: **Segoe UI**, headings **Segoe UI Semibold** (no bold flag on top of Semibold).
- Body 9 pt, line spacing 1.12, space after 3 pt. Tables 7.5 pt, line spacing 1.04.
- Title 18 pt · H1 12.5 pt with a `PRIMARY_300` hairline under it · H2 10.5 pt · H3 8.5 pt with +0.6 pt
  tracking · step number 9.5 pt in `TEAL`.
- **Two H2 weights**: a heading that starts with "Use Case" is a solid `PRIMARY_600` banner with white text;
  every other H2 is a light `PRIMARY_050` chip with a left `PRIMARY_600` bar.
- Callouts are blocks with a 2 pt left bar and a tinted fill, not coloured italic runs.
- `keep_with_next` on every heading, so none is stranded at the foot of a page.

## Page and table geometry

```javascript
// Page: A4 (11906 x 16838 DXA), margins 1080 DXA sides, 900 DXA top and bottom
// Field table:      [1050, 1900, 1250, 1400, 3426]   // Group | Field | Type | New/existing | Values
// Lookup table:     [1900, 1200, 5926]
// Reuse table:      [1500, 3400, 4126]
// Small table:      [2100, 1500, 5426]
// Dashboard table:  [2100, 6926]
// build_outputs.py scales every table to the full text width: 11906 - 2 x 1080 = 9746 DXA
```

- Table header row: **white Semibold on `PRIMARY_600`**; data rows alternate white / `ROW_ALT`.
- All borders: SINGLE, size 4, colour `HAIRLINE`.
- Running header: `"CLIENT NAME  Document Title · version"` with a `PRIMARY_300` bottom border.
- Footer: `"Creatio Demo Build — Confidential   [page number]"` with a `HAIRLINE` top border.

## The seven mechanics that break quietly

Every one of these produces a file that opens without an error and looks wrong:

1. **`ShadingType.CLEAR`, never `SOLID`** for cell and paragraph shading.
2. **Dual widths are required** — `columnWidths` on the table *and* `width` on every cell, plus a fixed
   `tblLayout`. With only one of them, Word re-flows the columns to its own taste.
3. **Never `\n` inside a text run.** Use separate paragraphs.
4. **Never unicode bullet characters.** Use the list styles; tint the glyph by setting the colour on the
   *paragraph mark* (`pPr/rPr/color`), not on the runs.
5. **A page break must live inside a paragraph.**
6. **`cantSplit` on every table row**, or Word splits a tall row across a page and the repeated header lands
   above an orphaned half-row. Pair it with `tblHeader` on the header row.
7. **Paragraph borders and shading must be inserted in schema order** inside `pPr` (`pBdr` and `shd` before
   `spacing`/`ind`/`jc`/`rPr`). Appending them at the end works in Word and breaks in other renderers.

## Generating it

`../scripts/build_outputs.py` implements this style (Segoe UI, petrol/teal palette, use-case banners, H2 chips,
callouts, fixed-layout tables with repeated header rows and cantSplit). Change the style there, not by hand in
a generated document.

## ⛔ Always render before delivering

`../scripts/render_check.py <file>.docx` does it: Word through COM on Windows, else `soffice --convert-to pdf`,
(`$w = New-Object -ComObject Word.Application; $d.ExportAsFixedFormat($pdf, 17)`) — open a **copy**, never the
deliverable, so the file stays unlocked. Column overflow, a table past the margin, a lost header: none of it
shows up in the generation log, all of it is obvious in the render.

---

## Legacy style (before 2026-08-25)

Arial throughout; `RED "C0392B"` for headings and table headers, `ROW_ALT "FDF2F2"`, borders `D5D5D5`, body
10 pt, margins 1080 DXA all round, field table `[3000, 1800, 4226]`, lookup `[2800, 6226]`, dashboard
`[2500, 1600, 3200, 1726]`. Documents already delivered in this style stay in it.
