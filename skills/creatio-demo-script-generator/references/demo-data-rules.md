# Designing the demo data

Condensed from `creatio-demo-build` phase 5 and `creatio-demo-data-population`. Here the data is designed and
written to the workbook; seeding it into a stand is the build's job (phase 5 / the data-population skill).

## Rule 0 — every object the demo touches gets records

1. Every **new** object (validator error if empty) and every **extended** object (warning).
2. Every stock object a step shows or a lookup column points at with demo-specific records (the site, the
   technician, the product) — not system lookups like City unless the demo needs specific values.
3. The **main demo records** — the ones the steps name — with `_main: true`, spelled, numbered and valued
   exactly as the steps write them. They sit in their **opening state** (the state "Run before demo" restores):
   if step 6 resolves WO-1042 live, WO-1042 is not in the data at all (it is created live) or is in stage "New".
4. **Background records** so nothing looks like the only record ever: other accounts with the same custom
   columns, closed history behind every trend, a few records in each stage of every pipeline.

## One source of numbers

Every number the audience sees — in a step, a bubble, a widget example, a calculation — is computed from the
records in `data`. Script G's worked fee calculation used 25,204 a month while its school catalogue said 21,124;
the build produced a total the presenter could not say. Write the data first (or generate it), then copy the
numbers into the steps. One hero record per story, one ID, one set of people and amounts across every use case.

## Hero records and light records

- **Hero records** (`_main: true`): fully populated — every column a user would fill, related records, history,
  attachments described. These are the ones opened on screen.
- **Light records**: the rest of the population, with the minimum fields that make lists, filters and widgets
  look real (Script C: 6 fully populated accounts + ~24 with name, owner and health only). Say which is which in
  the block's `purpose`.
- **Illustrative vs exact**: say in the block's `purpose` which values must match the script exactly (the
  drill-in records) and which are ballpark (background distributions).

## Volume

- **Showcase** (default): main records + 10–30 per *business* object (accounts, contacts, products,
  promotions); the transactional objects that feed the widgets (visits, orders, cases) get as many as the
  widgets need to have a coherent shape — often 40–80; line and child objects scale with their parents (3–5
  lines per order). **Rich**: 50–200 per business object when the customer's story is about volume.
- More than ~60 records in total: write a small generator script in the scratchpad that builds the `data`
  block (seeded random, fixed seed) and computes every on-screen number from it, then paste those numbers
  into the steps. Never type 400 records by hand, never type a number you did not compute.
- Work backwards from each widget: a metric says 38 → exactly 38 records match its filter on the demo day; a
  bar chart by site → at least 4 sites with visibly different values; a trend → 6+ periods, with the shape the
  bubble describes (the outlier is an outlier, the improvement improves).
- Count it. For every number a step or bubble says on screen, filter your own records and confirm it. A number
  that changes during the demo (a live record adds one) is right both before and after.

## Realism

- **Names from the customer's world**: their region's company and person names, real-looking addresses, phone
  formats, email domains (`@<client>-demo.com`), their currency, their product and service names from the
  materials. Never "Test", "Sample", "Product A", "John Doe", lorem ipsum.
- **Complete records**: every column a real user would have filled, not only the one a widget needs. A record
  gets opened on screen.
- **Variety without duplicates**: different owners, priorities, amounts, dates; no two records with the same name.
- **Consistency**: amounts reconcile (lines sum to the total), dates are in order (registered < arrived <
  resolved), stage and status agree, closed records have a close date and a reason.
- **Dates relative to the demo day**: `today`, `today-30`, `today+2 09:30`, and month anchors `som` / `eom`
  with month offsets (`som-2` = first day of the month two months back) — resolved against `meta.date` at
  build time, so moving the demo is one change. Monthly targets use `som±N` / `eom±N` for their period dates;
  a period *name* ("October 2026") is text and must be updated by hand when the demo day moves — say so in the
  data block's purpose. Spread history over weeks or months, weekdays, working hours.

## Characters that clash with the script

Steps use → as the path separator: never put → (or ->) inside a data value. Routes, lanes and flows are
written with an en dash ("Hamburg – Salzgitter"). Avoid * and ** in values (they are the step markup).

## Encoding in spec.json

```json
{"object": "Case", "purpose": "why these records exist", "records": [
  {"_key": "WO-1017", "_main": true, "Number": "WO-1017", "Priority": "High",
   "Account": "@SITE-RP", "UsrSlaDue": "today-1 16:10", "UsrSlaMet": false}
]}
```

- Keys are **column codes** of the object in the model; every key must be a listed column.
- Lookup to a lookup table → a value from that lookup's `values`, exactly.
- Lookup to an object that has data → `@<_key>` of the target record (the workbook writes its display value).
  A plain name is allowed only for a record assumed to exist on the stand (validator warns).
- Numbers as numbers, booleans as `true`/`false`, dates ISO or `today±N [HH:MM]`.
- One block per object; the import order (lookup targets first) is computed by the generator. A reference
  cycle (Account.PrimaryContact ↔ Contact.Account) is listed on the workbook's Summary as a **second pass**:
  import without those columns, then update them.
- Attachments the steps open (a contract, a statement) are listed in the object's `purpose` with what they must
  contain; the build generates real PDFs for them.
