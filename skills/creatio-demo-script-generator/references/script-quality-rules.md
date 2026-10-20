# Script quality rules — what the SE team said makes a script actionable

Source: SE team feedback "Scripts quality feedback" (2026-08-28) and a full read of the
eight scripts it names, analysed 2026-10-15. **Read this before writing the spec.** The validator enforces the
checkable rules (codes Q1–Q18 in `scripts/quality_checks.py`); the rest is judgment you apply.

> "The main goal is not to make scripts longer or more detailed. It is to make them clearer and more
> actionable." — the feedback's closing thought. The clearer the script, the more of the build the coding
> agent can do, and the more the SE can spend on validation instead of interpretation.

> The eight scripts are anonymized in this public copy: **A** banking (LATAM), **B** public-sector collections, **C** asset manager, **D** credit union, **E** retail-display manufacturer, **F** credit union remote services — the six rated actionable; **G** business school and **H** healthcare compliance — the two that cost SE rework.

## What the good scripts did (and the document now does by structure)

| Pattern | From | Where it lives in our document |
|---|---|---|
| The team's template header: goals/problems, website, key products, key roles (≥1 non-admin), marketplace solutions, languages; reference demo, key sections | Script F, Script D | Brief customer summary · Brief demo summary |
| Per use case: Purpose → Click path → Value message → Required setup → Required data population | Script F, Script D | Demo use cases |
| Value message as "Instead of …, …, which means …" | Script F, Script D | `value_message` (Q6) |
| Entry point per use case: workplace / home page / record / mobile / portal | Script E | `entry_point` (Q6) |
| One anchor (hero) record through the story, a "day in the life" arc | Script C, Script E | `brief.focus`, hero records, flow lines |
| Instance URL, logins per persona with role, sandbox codes, language convention — up front | Script A, Script B | header card (Q1) |
| Ground rules: integrations mocked and how, extend vs rebuild, UI language, never show JSON, budget, "not listed = out of scope" | Script A | Ground rules (Q5) |
| Customer's full process vs what the demo focuses on | Script B | `brief.focus` (Q3) |
| Build-scope matrix by area: fully built / simulated / talking point | Script B | Build scope (generated from `realization`) |
| Each object its own section: new / extends native, purpose, field table with type + constraints + purpose; lookup values inline | Script B, Script C, Script E | Configuration → object model |
| Object configuration depth (section / list on a parent / lookup only) — stops over-building | Script E | `depth` (Q12) |
| DCM table with a Scope column: built / pre-filled record only / simulated | Script B | DCM `scope` per stage |
| Processes: trigger, steps, guards, exact field values set; demo shortcuts stated as rules (forced confidence 95/75) | Script B | processes `actions`, `simulation` |
| AI actions table: action, input, output (with enum), routing use; verbatim on-screen answer, pre-canned for reliability | Script B, Script A, Script F | AI actions (Q8) |
| Mocked integration: system it stands for, "Populates: <widget>", dummy data, timeline note as proof of the call | Script A | Integrations (Q9) |
| Notification catalogue with IDs (WA-1, EM-1), final copy, {{merge fields}}, consent gate | Script B | Notifications (Q10) |
| Widget tables: name, type, data source as a query, exact value shown | Script A, Script E, Script C | Dashboards (+ `seed`) |
| Data plan: N hero records fully populated + M light records, spread so dashboards look alive; dates as offsets | Script C, Script B | Demo data rules |
| Pre-demo state, including records that must NOT exist yet (created live) | Script A | Before you present (Q17) |
| Effort budget and "protect in order" when time runs short | Script A, Script E | `priority`, `meta.build_budget_h` (Q15) |
| Content assets as appendices: KB article, email copy, sample transcript | Script F, Script C | `appendix` |
| A short video walkthrough removes ambiguity fastest | Script C | `meta.walkthrough` — recommend the consultant records 2–3 min |

## What the weak scripts did (and the validator now catches)

| Failure | Seen in | Rule |
|---|---|---|
| Almost no demo flow; object tables first, flow buried under "BPMN subprocesses" | Script G | The click path comes before the configuration and carries the story |
| Two versions in one document ("UPDATE" contradicting the body) → AI mixed the data | Script G | One current version; no UPDATE / TBD (Q16); open questions only in Questions |
| Calculation examples disagree with the data catalogue; the same record has two IDs | Script G | Every number on screen is computed from the data (count it); one hero record, one ID |
| AI proposed senseless custom objects: "two custom objects" but four defined, a rollup stored as an object, Campaign duplicated, Account renamed globally | Script G | `why_not_ootb` on every new object (Q12); rollups default to a dashboard (Q12); renames flagged (Q12) |
| Which instance? A previous demo existed with different use cases | Script H | `meta.instance` with mode new / reuse / copy (Q1) |
| 13 roles, never said whether they are separate users, logins or workplaces | Script H | every role has a login mode (Q4) |
| "Desktop" for Home page, "AI Panel", "Lookup(s)", polymorphic references, a "Global" section | Script H | banned terms (Q16) |
| "Keeps the 5-day clock met automatically" — automation, process, record or talk? | Script H | every automation: realization + what the audience sees (Q7); clocks defined once (Q11) |
| "~10% route automatically to QA" — a statistical rule with no demo moment | Script H | non-live rules are `simulated` with how (seed flag, button) or `talking point` (Q7) |
| AI as an outcome only: no trigger, input, storage, review | Script H | AI contract (Q8) |
| The same clocks restated in ten places; dashboards listed three times | Script H, Script E | state once in the configuration; use cases list *names* in Required setup |
| UC4 scope unclear and unneeded; UC6 duplicated UC5 | Script H | duplicate use-case check (Q14); out-of-scope list (Q15) |
| Talking points inside numbered build steps ("– talking point", "– not be showed") | Script H | talk goes in bubbles (Q6) |
| Credentials in plain text in the script | all eight | never — users by name only (Q2) |
| Leftover names from another demo (Meridian Global Bank), numbering gaps, self-references | Script C, Script D | generated numbering; text references resolved by the validator |

## Judgment rules the validator cannot check

1. **Demo flow, not business requirement.** For every sentence of the customer's material that describes how
   the business works, ask "what does the audience see?" — the step is the answer. A requirement with no
   visible moment is a talking point in a bubble or out of scope.
2. **One implementation per requirement.** If a line could be built two or three ways, pick one, write the step
   to it, and log the choice in `decisions`. Never leave the SE to choose.
3. **Consolidate.** Two use cases that create the same record or perform the same hand-off become one.
4. **Concise beats complete.** Detail that adds clarity stays; detail repeated elsewhere goes. Business story
   lives in the customer summary, purposes, bubbles and value messages — never inside configuration tables.
5. **Know the stand.** When the instance is a copy of a reference demo (Golden CRM / Service / FinServ), build
   on its object model and pages, and say which screens are reused and what changes on each (`model.ui`
   kind "Reuse" / "Hide" rows).
6. **Simulate honestly.** A simulated thing says how: preloaded data + timeline note, a button standing in for a
   timer, a seed flag standing in for a sample, pre-extracted text standing in for OCR.
