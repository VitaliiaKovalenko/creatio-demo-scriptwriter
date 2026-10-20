# Deal tiers — how the deal size shapes the demo

The deal's **ARR (annual recurring revenue, USD)** is a mandatory intake answer. It decides how much custom
configuration the demo gets and how ambitious the suggestions are: a small deal is shown with the product as it
is; a strategic deal earns a tailored build and a re-thought flow. The numbers live in `deal-tiers.json` (edit
them there); `validate_spec.py` enforces them (Q25) and the documents print the tier and the budget used.

| | **OOTB** — under $50k | **Medium** — $50k to under $100k | **High** — $100k to under $500k | **Extremely high** — $500k and more |
|---|---|---|---|---|
| Intent | Product as it is; keep it simple | Mostly stock, tailored where the story needs it | Tailored demo, differentiators built in | Strategic: show their future process |
| New objects | 0 | ≤ 2 | ≤ 5 | no cap |
| New columns | ≤ 8 | ≤ 20 | ≤ 40 | no cap |
| New lookups | ≤ 3 | ≤ 6 | ≤ 12 | no cap |
| Processes (reset excluded) | ≤ 3, all buildable from code | ≤ 6, ≤ 1 designer-only | ≤ 12, ≤ 4 designer-only | no cap |
| AI actions | ≤ 1 (stock Creatio.ai skills first) | ≤ 2 | ≤ 4 | no cap |
| Simulated integrations | ≤ 1 | ≤ 2 | ≤ 4 | no cap |
| DCM cases | ≤ 1 | ≤ 1 | ≤ 2 | no cap |
| Proposed additions | 4–6, effort S only | 4–8, effort S/M | 6–10, any effort | 8–12, any effort, ≥ 1 flow redesign |
| Flow improvements | quick wins only | moderate | active: differentiators, smarter steps | re-think the flow: personas, agents, end-to-end |
| Demo data | Showcase-light (5–15 per object) | Showcase (10–30) | Showcase+ (20–60) | Rich (50–200) |

Boundaries: exactly $50k is Medium, exactly $100k is High, exactly $500k is Extremely high.

## How the tier changes each phase

- **Use cases** — the consultant's use cases stay; the tier changes *how* they are shown. OOTB: stock pages,
  stock lookups, stock processes, the shortest honest path. Extremely high: the step can show a tailored page,
  an AI agent doing the work, a simulated integration.
- **Object model** — stay inside the budget. Over budget → first look for the stock alternative
  (`ootb_lookup.py`), then move the extra into a proposal. A justified exception goes in `meta.deal.exceptions`
  (`{budget: "new_objects", why: "…"}`) and is shown to the SE.
- **Proposed additions** — the count and the effort ceiling follow the tier. OOTB proposals are quick, stock-only
  wins (a stock widget, a business rule, a folder). Extremely high proposals include at least one re-designed flow
  (a new use case or a re-ordered story), not only polish.
- **Competitive highlights** — at OOTB, win on speed and simplicity (no-code change live, time to value); at High
  and above, also on depth (end-to-end flow, AI, integrations).
- **Data** — the volume follows the tier's data line.

## ARR answers that are not a number

- Another currency → convert to USD at an approximate current rate; record `arr_original` (e.g. "EUR 70,000").
- A range ("80–120k") → use the midpoint and say so.
- Unknown and the user cannot say → stop and ask once more; if the agent runs in the background and cannot ask,
  apply the **Medium** tier, set `arr_assumed: true`, and put the ARR question first in the hand-over.
