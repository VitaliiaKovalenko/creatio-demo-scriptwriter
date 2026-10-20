# Context library

The out-of-the-box Creatio object model, as spreadsheets. The script generator reads these to decide "existing object or new
object" before proposing anything custom, and the model and the data use them to get field types and lookup values right.

| File | Use it when |
|---|---|
| `Creatio-object-model.xlsx` | any standard industry — Sales, Service, Marketing, Studio |
| `Creatio-banking-object-model.xlsx` | **banking / FinServ / lending** — use this one *instead*, not as well |

Both were captured 2026-08-19 from an internal reference project,
where they were the reference material for the same prompt this skill implements.

## Read them programmatically

Not by eye — the whole point is grounding a decision in the actual field definitions:

```python
from openpyxl import load_workbook
from collections import defaultdict

wb = load_workbook("Creatio-object-model.xlsx", data_only=True)
for ws in wb.worksheets:
    for row in ws.iter_rows(values_only=True):
        ...

lookups = defaultdict(list)   # group lookup values by lookup name
```

## ⚠️ What these files are and are not

They are the **product's** model. They are not the model on any particular demo stand: a real instance carries
a product bundle plus the residue of previous demos — extra columns, renamed lookup values, whole sections. So
a spreadsheet answer of "this object does not exist" is a good default for writing a scenario and a bad basis
for creating something. The build toolkit re-checks it against the live instance in its Phase 2, and on a
FinServ stand that check routinely turns "custom object" into "reuse this one".

Query them with `../../scripts/ootb_lookup.py` (`find`, `object`, `values`, `sections`; `--banking` for FinServ).
