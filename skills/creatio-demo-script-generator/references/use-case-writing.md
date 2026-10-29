# Writing the use cases

Condensed from `creatio-demo-runbook` (generation 2) and `creatio-doc1-demo-flow`, adapted to customer input
(agenda + materials) instead of a consultant's draft script.

## Story first — the demo is a story, not a function tour

SC feedback (2026-10-28): going straight from intake to finished files gave click paths that "felt jagged and
didn't really address the customer's needs — a function-heavy flow, not a demo story grounded in value", and took
5–6 rounds of rework. So the story is drafted and approved (SKILL.md Phases 3–4) before any step is written.

- **One thread.** Name the one business outcome the whole demo proves, in the customer's words and numbers
  ("every closure inside the two-day CMF deadline, provable any day"). Every use case moves that thread forward;
  a use case that does not is cut or merged.
- **Open with their pain, close with their outcome.** The first beat is the problem this audience feels (a quote
  or a number from the call); the last beat makes the outcome visible (a figure, a closed case, a happy client).
- **One hero, one journey per use case.** Follow one record and one persona through the flow; switch persona
  only at a real hand-off, and say why the hand-off matters.
- **Every beat earns its place.** A beat answers a pain, proves a goal or sets up the next beat. A screen that
  only shows that a field exists is not a beat — fold it into the next beat or drop it.
- **Show, then name the value.** The beat shows the moment (*"the debt appears on the case with one click"*);
  the value message says what it is worth to them (*"10–15 minutes saved per case, no copy errors"*).
- **One "aha" per use case.** The moment this audience will remember; put it where the energy is, usually the
  middle of the use case, and protect it from clutter.
- **Fit the clock.** Minutes per use case add up to the demo length with room for talk and questions; the
  person who leaves early sees the value before they go.
- **Beats before steps.** At the checkpoint, a beat is one line of what the audience sees and why it matters.
  Field names, captions and click mechanics come only after the SC approves the story.

## From agenda to use cases

1. List the agenda items verbatim (A1, A2…). Mark each: **demo-able** (a flow in Creatio), **talk** (slides,
   pricing, intros — not a use case), **out of scope** (needs development, another product, an integration we
   cannot simulate honestly).
2. Group demo-able items into use cases by **one business flow with one persona entering it** — not by agenda
   line. Two items that are the same record moving forward (intake → dispatch) are one use case with scenes.
3. Order use cases as the story runs: front office before back office, the record created before the record
   analysed, the manager's dashboard last (it needs the earlier records to exist).
4. Every agenda item ends `covered_by` a use case or with a `note` (why not, what we offer instead). Every use
   case answers at least one pain (P…). A use case that answers no pain is cut or merged.
5. Count: 45–60 minutes holds 2–4 use cases of 5–9 steps. If the agenda asks for more, keep the count of the
   agenda's blocks and make the steps tighter; never silently drop an agenda item.

## Resolve, do not report — the checklist you walk while writing

1. **Two-directional name check** — every noun the customer uses maps to something in the flow, and every
   thing in the flow traces to the customer's ask or a deliberate decision.
2. **OOTB first** — a business noun that maps to a stock Creatio object IS that object (check with `ootb_lookup.py`).
3. **No-code / low-code / needs-dev** per feature. Needs-dev is replaced with the nearest honest no-code path,
   or moved out with a note. Never demoed as if it existed.
4. **Prerequisites** — a step that needs a record says which record (and it goes into the data); a step that
   needs a role names the role.
5. **Sequencing** — nothing used before it exists; a use case that relies on another says so in its flow line.
6. **Platform limits** (capsule): one stage column per section, DCM has no gateways, `[DEV]` never promised.
7. **Reader-panic rule** — a term introduced is explained on the spot or cut.
7a. **Customer requirement → demo moment.** For every sentence in the materials that says how their business
    works ("tracks the 210-day investigation window"), write what the audience *sees* (the case shows
    **Investigation due** = 12 Mar, the home page counts 3 investigations due this month). No visible moment →
    bubble or out of scope. One implementation per requirement — pick it, log it in decisions.
7b. **Consolidate.** Two use cases that create the same record or make the same hand-off are one use case
    (Script H UC5/UC6 was specified twice and dropped after the build had started). The validator flags heavy
    overlap (Q14).
8. **Personas are roles on one demo user.** "The approval appears in Approvals, addressed to the Finance
   Supervisor role" — never "I log in as…". Only a portal/mobile step changes the visible user, and the step says so.
   Every role is in `roles` with its **login mode** — same user, separate user, portal user, email only, or
   conceptual — and its workplace. Script H listed 13 roles and never said which were logins; the SE built
   workplaces nobody asked for.
9. **AI steps are confirm-before-write dialogues** in Creatio.ai vocabulary: the prompt typed in quotes, the
   answer shown, the record written only after confirmation.
10. **Integrations** are named as simulated unless the customer's system is really reachable from the stand.

Each hit → a `decisions` entry (`deviation` if it changes the customer's ask). Only genuine choices for the
consultant or customer → `questions`, each with the default you wrote the steps to. More than ~6 questions
means the material is too thin: say so in the hand-over and ask for the missing piece.

## The use-case block — the team's template

Every use case renders as **Purpose → Click path → Value message → Required setup → Required data
population** (Script F / Script D template). You write:

- `summary` → **Purpose**: 2–3 sentences, what happens and what it proves.
- `entry_point`: where the presenter starts — workplace + home page / section list / record / Creatio Mobile /
  portal (Script E names it per use case; the SE should never hunt for the first screen).
- `items` → **Click path**: bubbles + numbered steps (below).
- `value_message` → **Value message**: one sentence, *"Instead of <today's pain, in the customer's words>,
  <what Creatio does here>, which means <the outcome they care about>."*
- `priority`: must / should / could — what survives when build time runs short.
- **Required setup** and **Required data population** are generated: the generator lists, by name only, the
  model elements and hero records whose step references fall in this use case. You never restate the
  configuration inside a use case — Script H repeated its clocks ten times and Script E its account values five;
  the SE could not see what was new. Add `data_note` only for data the hero records do not cover.

## The flow line

One line per use case, plain language, arrows, **no element or field names** — the skeleton the steps then
demonstrate. *Tenant reports a leak on the portal → work order created with SLA → dispatcher assigns the right
technician → technician resolves it on site → tenant sees it closed.*

## The step — an `action → result` chain

> 4.  Field **Assigned technician** → list shows **Marco Diaz** first *(filtered by the rule: skill "Plumbing",
>     region "Downtown")* → select → stage moves to **"Assigned"**
>
> 6.  Tab **Resolution** → **Root cause** = **"Worn valve seal"** → **Complete** → stage **"Resolved"**

1. **Location first when the page changes**: list page, form page + tab, mini page, home page, Creatio Mobile,
   portal, Creatio.ai panel. Omit while you stay on the same page.
2. **Every chain ends on a visible result.** A step that produces nothing to look at merges into its neighbour.
3. **Mechanics inline**: object, column caption, lookup value in quotes, button, tab, record — in `**bold**`.
   A field and its value are written `**Caption** = **"Value"**` — two bold runs side by side read as one
   ("Root cause Worn valve seal"). On-screen numbers stay plain (`**Open work orders** = 38`). This is what
   makes the script buildable as well as presentable: **every bold term must have a home** in the model
   (column, lookup value, `model.ui` element, widget, process) or the data (a record) — the validator lists
   the ones that do not.
   **Captions of standard (OOTB) buttons, actions and fields are never translated by you.** Write them as the
   product shows them in the demo language when a capsule or the source gives that caption; otherwise keep the
   English caption exactly (**Assign to me**, **Complete**) and add one question with the default "English
   caption kept". Captions of new or renamed fields come from the source or the model, in the demo language.
   The same input must give the same caption on every run.
4. **Provenance in `*(italics)*`** whenever the presenter did not type the value: *(created by the process)*,
   *(calculated by the rule)*, *(AI skill "…")*, *(from the ERP feed — simulated)*. The audience must see the
   system do the work.
5. **Arrows carry the path; bold is only for element and value names**, never for emphasis.
6. **One step = one coherent move.** Several actions are fine when they are one gesture; two ideas are not.
7. **Numbers never shift.** Per use case, from 1. Removing a step leaves a gap; inserting one takes the next
   free number at the end of its scene and is noted in decisions.
8. **Scenes** (`{"scene": "The manager's view"}`) group a long use case without renumbering.
9. ⛔ **"click" and "say" never appear** (validator error; text inside quotes, such as an AI prompt, is
   exempt). No emoji, no "seamlessly", no "the system automatically" without naming the mechanism.
9a. **No talking points, questions or builder notes inside a step** ("– talking point", "– not shown", "could
    this be the home page?" — Script H, Script G). Talk goes in a bubble; questions go in `questions` with a
    default; builder notes go in the configuration (`simulation`, `note`).
9b. **Every automation the audience sees happens in a step**, with its provenance: *(created by the process
    "Escalate work order")*. An automation that cannot happen live is shown through its simulation — the
    pre-marked QA case appears in the lead's list — never just asserted ("10% route automatically").
9c. **AI steps** follow trigger → what the AI shows → the user confirms → what is written:
    *Creatio.ai panel → "Summarize SLA risks for Riverside Plaza" → summary naming WO-1017 → **Escalate***.
10. **The AI panel** is the **Creatio.ai panel** unless the user says the stand runs AI Studio agents — then
    use the name the user gives. A script writer has no stand to check; do not guess "AI Twin".
11. **Mobile steps** use the vocabulary of `capsule/09-creatio-mobile.md`; anything beyond it is a decision
    plus an SE question (e.g. camera straight into an Image field).

## The bubbles — narration above a group of steps

- **2–4 per use case**, each above 2–6 steps, placed where the story turns: the opening, a new side (the
  customer, the technician, the manager), the payoff.
- **Spoken language**: short sentences, numbers as they are said, the customer's own words and figures from
  the brief (their 140 buildings, their 4-hour SLA).
- **Problem → what you are about to see → what it means.** Three sentences at most.
- Never a claim the steps do not show.

## Use-case summary

Two or three sentences: what happens and what it proves, naming the pains (P…) it answers. It is the
orientation layer for anyone who will not read the steps.
