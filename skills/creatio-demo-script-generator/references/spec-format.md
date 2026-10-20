# spec.json — the single source of the demo package

A complete worked example: `sample-spec.json` (copy its shape). Validate with `scripts/validate_spec.py`.
Step references everywhere use `UC<n>.<step>` or `UC<n>.<a>-<b>`.

```text
meta
  client*            "Brightline Facility Services"  — names every file
  title              "Demo Script"
  version            "v1" — bump on every revision
  date*              "2026-10-15" — the demo day; relative dates resolve against it
  language*          "en"
  instance*          {name, url, mode* new|reuse|copy, reference_demo (required for copy), previous_demos}   (Q1)
  deal*              {arr_usd* (number, USD — mandatory intake answer), arr_original ("EUR 70,000"), source,
                      arr_assumed (true when not given — Medium tier, warning), exceptions[] {budget, why}}   (Q25)
                      The tier is computed from arr_usd (references/deal-tiers.json) — do not write it.
  industry, region, currency, duration_min, demo_user, products[], integrations[]
  website, key_products[], marketplace[]   — the team template's header rows
  build_budget_h     build effort budget, shown with the protect-in-order list
  walkthrough        link to a 2–3 min video walkthrough, or "To record: …"
  finserv            true → the banking object model was used
  prefix             "Usr" | "lab…" — expected prefix of new objects, columns, lookups
  ⛔ never a password, anywhere in the spec (Q2)

brief
  summary            2–3 sentences: who the customer is, what hurts, what they asked to see
  demo_goal*         the business problem + what the audience sees at the end (Q3)
  focus              the customer's full process vs the part the demo covers (Q3)
  pains[]            {id "P1", text, src "S1"}
  goals[]            {id "G1", text, src}
  agenda[]           {id "A1", text (verbatim), src, covered_by ["UC1"], note (required when covered_by is empty),
                      talk true (intros, pricing, Q&A — not a use case and not "out of scope")}
  vocabulary[]       {client "Work order", creatio "Case with Category \"Work order\""}
  key_numbers[]      {text, src}

discovery            {source, date, participants[], moments[] {id* "D1", minute, speaker, kind* pain|priority|requirement|
                      objection|stakeholder|current_system|competitor|signal|risk, importance high|medium|low,
                      quote (one sentence, customer's words), insight, covered_by ["UC1"], note}}   (Q19, Q24)
industry             {name, summary, points[] {id* "IND1", point, why, demo_implication*}, sources[] {title, url, date}}   (Q20)
competitive          INTERNAL — {summary, competitors[] {name, products[], why_in_deal, would_show, strengths, gaps
                      (where Creatio wins here), sources*[] {title, url, date}},
                      points[] {id* "CMP1", uc, they_show*, creatio_better*, demo_highlight*, trap}}   (Q21)
similar_demos[]      INTERNAL — {id* "PD1", customer, link* (SharePoint webUrl), industry, use_cases[], reuse[], lessons[]}   (Q22)
research_gaps[]      what research could not be done and why ("No discovery transcript was given") — the only way a
                      missing research part passes the validator (Q19–Q22 are mandatory otherwise)
proposed_additions[] {id* "PA1", title, kind* feature|story|differentiator|risk, priority high|medium|low, why*,
                      sources* [D/IND/CMP/PD findings or P/G/A/S customer ids] — always 4–10, transcript or not, demo_moment* (written like a step), fits* ("UC1 after step 4" |
                      "new use case"), effort* S|M|L, status proposed|accepted|rejected}   (Q23) — never in scope until accepted

roles[]*             {name, title, login_mode* same user|separate user|portal user|email only|conceptual,
                      login (user name, never a password), workplace, sections[], scope, use_cases[]}   (Q4)
ground_rules[]       demo-wide rules as sentences (Q5)
out_of_scope[]       {item, why} — what is deliberately not built (Q15)
pre_demo             {must_exist[], must_not_exist[] (records created live), checks[]}   (Q17)
appendix[]           {title, kind, text (paragraphs separated by \n)} — KB article, email copy, transcript…

use_cases[]
  id "UC1", name, agenda ["A1"], pains ["P1"], persona (a roles[].name), entry_points ["web","mobile","portal",…]
  entry_point*       "Service home page, Service workplace" — where the presenter starts (Q6)
  value_message*     "Instead of <pain>, <what Creatio does>, which means <outcome>" (Q6)
  priority           must | should | could — the protect-in-order list (Q15)
  data_note          extra data needed for this use case beyond the hero records
  flow_line          plain words with arrows, no field names
  summary            2–3 sentences: what happens, what it proves (rendered as Purpose)
  items[]            in display order, each ONE of:
                       {"bubble": "narration above the following steps"}
                       {"scene": "The manager's view"}
                       {"step": 1, "text": "Location → action → **Element** → result *(provenance)*"}

model
  objects[]          {code, caption, status new|extended|existing, section (empty when the object has none),
                      display (column shown as the record name; default Name/Title/Subject/Number),
                      allow_duplicate_names (true for line/child objects), purpose, steps[],
                      depth "section with pages"|"list on a parent"|"lookup only"|"page only" (new/extended, Q12),
                      why_not_ootb (required for new: the stock object you checked and why it does not fit, Q12),
                      rename (when a stock object is shown under another name — flagged, Q12),
                      columns[] {code, caption, type, ref, status new|existing, required, formula, steps[], note}}
                      — Name/Number/Owner/Notes… of a new object are status "existing" (they come with the base)
  lookups[]          {code, caption, status new|extended|existing, values[] (display order),
                      new_values[] (extended only: the values you ADD to the stock lookup), colors {value: "#hex"}, steps[]}
  ui[]               {name (as bold in the steps), kind Button|Tab|Folder|Quick filter|List page|Form page|Mini page|
                      Mobile list page|Mobile form page|Home page|Portal page|Expanded list|Reuse|Hide|…, where, does, steps[]}
                      — "Reuse" rows: a reference-demo screen kept, with what changes; "Hide" rows: what to remove from it
  dashboards[]       {name, location, steps[], widgets[] {name, type, source (object, aggregation, filter, grouping),
                      example (the value on screen), seed (records needed to show it)}}
  dcm[]              {name, object, condition (which records the case applies to, e.g. 'Type = Rate request'),
                      stage_column (a lookup column of object), steps[],
                      stages[] {name (a value of the stage lookup), elements[], exit_required[], scope built|prefilled|simulated}}
  processes[]        {name, trigger, actions[], writes, build code|designer, realization*, simulation, audience_sees*, steps[], note}
  rules[]            {name, object, page, level page|object, trigger, condition, effect, realization*, steps[]}
  ai[]               {name, kind, purpose, trigger*, inputs*, output* (enum values when it classifies), stored_in*,
                      review*, example_output (verbatim, demo language), realization*, audience_sees*, steps[]}   (Q8)
  integrations[]     {name, system* (customer system it stands for), realization*, pattern / simulation
                      ("preloaded data + timeline note"), populates (widget/field/list), timeline_note, audience_sees*, steps[]}   (Q9)
  notifications[]    {id* "N-1", name, trigger*, recipient*, channel* email|whatsapp|sms|push|in-app, copy (final text,
                      {{merge fields}}), realization*, audience_sees*, steps[]}   (Q10)
  slas[]             {name*, duration*, start*, stop*, shown_in*, steps[]} — each clock defined once (Q11)

  realization        real | simulated | talking point — "simulated" requires `simulation` (or `pattern`) saying how (Q7)

data[]               one block per object
  {object, purpose, records[] {_key, _main, <column code>: value, ...}}
  values: lookup → a value of the lookup, or "@KEY" of a seeded record
          dates ISO, or relative to meta.date: "today", "today-30", "today+2 09:30" (days);
          "som", "som-1", "eom", "eom+1 17:00" (start / end of the demo day's month, ± months)
          Image/File columns: the file name; describe what the file must show in the block's purpose

stand_records        {"Contact": ["John Best"], …} — records that already exist on the stand and are referenced by name,
                     not imported (the demo user, stock lookup-like records). Silences "not among seeded records".
vocabulary_extra[]   bold step terms that legitimately have no model home (plain product chrome). Records created live
                     go in pre_demo.must_not_exist instead. Keep it short — most terms belong in model.ui.
decisions[]          {kind deviation|decision|assumption, text, why, where}
questions[]          {id "Q1", text, where, default* (the steps are written to it), who consultant|SE|customer}
```

**Dates inside text** (steps, bubbles, value messages, widget examples): write `{date:today-30}` → "22 Sep",
`{date:som-1|%B}` → "September" (any strftime after `|`). The generator renders them against `meta.date`, so
moving the demo day moves the text too. The bold-term check treats a token as a number.

`*` = required. Unknown keys are ignored by the generator, so you can keep working notes in `_notes` fields.
Numbers that change during the demo (a metric 38 → 39 after a live record) go in the step text with both
values and in the data block's `purpose`.

## What the validator enforces

Errors (build refuses): missing meta; duplicate/out-of-order step numbers; *click*/*say*/emoji in a step
(quoted text excepted); agenda/pain refs that do not exist; free-text refs (Q5, A3, P2, UC4) in agenda notes
and `where` fields that point at nothing; step refs that do not resolve; unknown column types; lookup columns
whose `ref` is not listed; a `display` that is not a column; `colors`/`new_values` naming values not in
`values`; DCM stages that are not values of the stage lookup; data for an unlisted object or column; lookup
values not in the lookup; `@key` pointing nowhere or at the wrong object; non-numeric numbers; bad dates;
empty required columns; a new object with no data; a question without a default.

Warnings (read each): **bold step terms with no home in the model or data**; agenda item covered by nothing
without a note; a use case answering no pain, a pain answered by no use case; bubbles outside 2–4; steps with
no arrow; model elements no step uses; steps nothing in the model backs; new columns never filled; missing
prefix; extended lookup without `new_values`; DCM on a non-lookup stage column; duplicate record names
(text display column, not on `allow_duplicate_names` objects); zero questions or zero decisions.

Script-quality checks (Q1–Q18, `scripts/quality_checks.py`, rationale in `script-quality-rules.md`):
instance named with mode; no credentials; demo goal; roles with login modes; ground rules; entry point, value
message and priority per use case; no talking points or questions inside steps; realization + audience_sees on
every automation; the full AI contract; integrations and notifications catalogued; clocks defined once; new
objects justify themselves against OOTB, carry a depth, rollups and renames flagged; no second stage-like lookup;
no duplicate use cases; out-of-scope reasons; banned Classic / non-Creatio terms; pre-demo data state; widget sources.

Not checked (your job): that the numbers on screen equal what the data produces. Count them.
