# Deriving the object model

Condensed from `creatio-doc2-object-model`, `creatio-demo-artifact` and `creatio-demo-build` phase 1/3.

## Detection — read the steps, not the materials

The model is derived **from the use cases you wrote**, with the materials as a source of detail (field lists,
value sets, volumes) — never of scope. Something the customer mentioned that no step shows is not modelled.

- **Object**: every noun the steps open, create, list or link ("open WO-1042", "the visit is created").
- **Column**: every caption in bold in a step, every value shown, every widget's metric/grouping field, every
  field a rule, process or AI skill reads or writes, every column the data fills.
- **Lookup**: any field with a fixed value set. "changes from X to Y" defines at least X and Y.
- **Detail (child) object**: lines, items, participants, allocations — repeating sub-records of a parent.
  Model as an object with a lookup to the parent, and a `Detail` column on the parent pointing at the child.
- **Dashboard**: every home page, section dashboard, or analytics block on a record page a step shows.

## OOTB first — verified with the context library

```bash
python ootb_lookup.py find "work order" "service request"   # objects, fields, lookup values
python ootb_lookup.py object Case                            # all stock columns of Case
python ootb_lookup.py values CasePriority                    # stock values
python ootb_lookup.py --banking find loan                    # FinServ demos: the banking model INSTEAD
```

Defaults: companies → **Account**; people → **Contact**; inbound interest → **Lead**; deals → **Opportunity**;
tickets/requests/work orders → **Case** (with a Category); tasks, calls, meetings, visits → **Activity** (Type +
Category); approvals → **Approval**; products/price lists → **Product**; orders → **Order**; contracts →
**Contract**; invoices → **Invoice**; documents → **Document**; projects → **Project**. When a stock object
fits, it is `existing` or `extended` and the client's word becomes its caption or a Category/Type value —
recorded in `brief.vocabulary` and in `decisions`.

Custom (`new`) only when nothing fits, prefixed (`meta.prefix`), and it gets a section with list and form
pages in the build. A new object duplicating a stock one is the error this phase exists to catch. Every new
object carries `why_not_ootb` — the stock object you checked with `ootb_lookup.py` and why it does not fit —
and every new or extended object a `depth` (section with pages / list on a parent / lookup only), so nobody
builds a section for something shown only as a list (Script E's "configuration depth" column).

Script G is the cautionary tale: the script said "two custom objects" and defined four; a payment consolidation
was modelled as a stored object although it was a grouped sum; Campaign was duplicated as a custom
"Convocatoria"; Account was renamed globally so schools had nowhere to live. The AI that built it then
invented more. So:

- **Rollups and consolidations are dashboard or home-page views** (a list grouped and summed), not objects —
  unless the demo shows that record's own lifecycle.
- **Never rename a core object globally** (Account, Contact) to mean one customer concept. Use a Type value,
  a caption on the demo's page, or `brief.vocabulary`. If a rename is unavoidable, set `rename` and say it in
  the ground rules.
- **Multi-value links are a detail / junction object**, never "Lookup(s)"; a reference that can point at three
  objects is three lookups or a shared parent, never "polymorphic".
- **Reference demos**: when `meta.instance.mode` is copy or reuse, the reference stand's objects and pages are
  the baseline — list the screens reused (`model.ui` kind "Reuse", with what changes in `does`) and what to
  remove (kind "Hide"), as Script E and Script C did. They appear in Build scope as "Reference-demo screens", not as
  new pages. You cannot see the stand from here: use what the user gives you (the reference demo's page list,
  screenshots, an earlier script built on it). Without it, write the Reuse/Hide rows from the product's stock
  pages, mark them "to confirm on the stand" in `does`, and add one SE question with that as the default.

When a base object cannot reasonably carry it (reviews across many stages, approvals with extra fields),
consolidate onto **Activity** (extended) rather than inventing parallel objects.

## Columns

| Field | Rule |
|---|---|
| `code` | the column code without the OData `Id` suffix (`Status`, not `StatusId`); new columns prefixed (`UsrSlaDue`) |
| `caption` | exactly as the steps name it — the data workbook headers use it |
| `type` | Text · Long text · Rich text · Integer · Decimal · Currency · Percentage · Date · Date/Time · Time · Boolean · Lookup · Email · Phone · URL · Auto-number · Image · File · Color · Detail |
| `ref` | for Lookup/Detail: the target object or lookup code — which must itself be listed in `model.objects` or `model.lookups` (status `existing` if stock) |
| `status` | `new` / `existing` |
| `required` | only when the demo depends on it |
| `steps` | `UC<n>.<step>` or `UC<n>.<a>-<b>` — empty for a column only the data fills |

Which columns to list: every column a step shows (with `steps`), and every column the data fills (a realistic
record fills Address, Email, Phone even when no step points at them — list them with empty `steps`). A
column neither a step nor the data uses is cut. The data workbook only has sheet columns for listed columns,
and the builder must know which stock columns the demo leans on.

## Lookups

Every lookup a column points at is listed with its values in display order. For a stock lookup list the stock
values the demo uses (check `ootb_lookup.py values` — it trims and deduplicates the stock list) and mark it
`existing`; when you add values to it, mark it `extended` and list the added ones in `new_values` (the data
workbook's "Lookup values" sheet then asks to create only those). Optional `colors` per value for
stage/priority/status lookups. One lookup shared by several objects is built once — the hand-off flags it.

## Pages, buttons and navigation — `model.ui`

Everything the presenter touches that is not data: buttons, tabs, folders, quick filters, list / form / mini
pages, mobile list and form pages, home pages, portal pages, expanded lists. One row each with its kind, where
it lives, what it does and the steps. This is the part of the model a builder otherwise has to re-read the
prose for. A button that runs a process names the process in `does`.

## Details (child objects)

Model the child as its own object with a lookup to the parent. On the parent, a column of type `Detail` with
`ref` = the child is the model's marker for "shown on the parent's form page". In the **steps**, name the
Freedom UI component that shows it (an **Expanded list** / list on a tab) — "Detail" is the Classic UI word.
Line objects (order lines, visit checks) set `allow_duplicate_names: true`.

## Stage, status, DCM

- **One stage field drives the flow.** DCM and the progress bar run on exactly one lookup column. Add a separate
  Status only when it means something different (a granular state inside a stage) and its values do not repeat
  the stages — two lookups with the same values (Script H) leave the SE guessing which one DCM uses (Q13). A
  generic "Returned" becomes "Returned to <Stage>".
- DCM: `stage_column` is a lookup column of the object; every stage name is a value of that lookup; one stage
  column per section (two cases on one section share it — union of values plus a selector column);
  **no gateways** — branching is "change stage after element completes". A DCM whose stages carry steps is
  built by hand in the Case Designer — say so, it is not automated work.

## Processes, rules, AI

- **Process**: trigger (signal on object + change, button, stage entry, timer, manual), actions in order with
  the exact field values they set, what it writes, `build`: `code` (linear/record-triggered, buildable via clio)
  or `designer` (gateways that need judgment, timers, sub-processes, script tasks, pre-configured pages, user
  dialogs).
- **Realization on every automation** (processes, rules, AI, integrations, notifications): `real`, `simulated`
  or `talking point`, plus `audience_sees`. Anything that cannot happen live — a timer, a 30-day reminder,
  statistical sampling ("10% go to QA"), caseload balancing, an external system — is `simulated` and says how in
  `simulation`: a seed flag (the hero case is pre-marked "Selected for QA"), a button standing in for the timer,
  back-dated records, preloaded data with a timeline note, a forced value (Script B: matching amounts force
  confidence 95, others 75). Demo shortcuts are written as rules, never left to the SE.
- **Clocks and SLAs** (5-day acknowledgement, 210-day window) are defined once in `model.slas` — duration,
  start event, stop event, where shown — and referenced by name everywhere else.
- **Notifications** each get a catalogue entry with an ID (N-1, WA-1), trigger, recipient, channel, final copy
  with {{merge fields}}, and real/simulated send.
- **Integrations** name the customer system each one stands for, how it is simulated (preloaded data + a
  timeline note "Integration with Core Banking succeeded — products updated" is the standard pattern), and
  which widget, list or field it populates.
- Always add **Run before demo** — manual, resets the opening state; every delete filtered (Created on =
  today, or an explicit list) so it can never wipe the instance.
- **Rule**: page-level (Freedom UI page: visibility, required, read-only, filtered lookup, set value) or
  object-level (required/validation across all pages). Trigger, condition, effect, steps.
- **AI actions** — the full contract, because "the user invokes Creatio AI and it suggests links" (Script H)
  left the SE to redesign the whole AI flow:
  - `trigger` — the button, quick action or the prompt typed in the Creatio.ai panel, and on which page;
  - `inputs` — the fields and related records it reads;
  - `output` — what it returns; for a classifier, the enum of values (Script B's intent: pago / consulta /
    convenio / disputa) and what each one routes to;
  - `stored_in` — the field, detail or record it writes, or "not stored — shown in the panel";
  - `review` — who confirms or edits it and what that sets (Suggested → Confirmed);
  - `example_output` — the verbatim answer the screen should show, in the demo language (Script A pre-cans the
    answers so they render reliably; Script F gives prompt and answer word for word);
  - `audience_sees`, `realization`.
  The skill prompt itself is written in the build (`creatio-ai-skill-prompts`); grounding content the AI reads
  (a KB article, a policy) goes in `appendix`.

## Dashboards

Ratios (win rate, first-time-fix rate, SLA compliance): a Freedom UI metric aggregates one column, so either
store a 0/100 score column on the record (won = 100, lost = 0 → the average is the rate), or show the two counts
side by side. Say which in the widget's `source`. Widgets that must not move during the live steps use a closed
period (last month) — and then the data must be regenerated when the demo day moves to another month.

Widget types from the Freedom UI palette only (`capsule/03-dashboards-widgets.md`): Metric · Gauge · Chart
(Bar · Column · Line · Spline · Area · Doughnut · Scatter · Pipeline) · Sales pipeline · Full pipeline · List
widget · Calendar · Timeline · iFrame. Never a Classic name (Pie, Pivot table, Web page). Data source = object,
aggregation, field, filter; example value = exactly the number the step shows — and the data must produce it.
