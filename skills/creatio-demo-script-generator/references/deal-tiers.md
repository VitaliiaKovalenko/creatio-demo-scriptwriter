# Deal tiers — how the deal size shapes the new ideas

The deal's **ARR (annual recurring revenue, USD)** is a mandatory intake answer. It decides **how many new ideas the
agent adds on top of the agreed demo, and how ambitious they are** — the *proposed additions* from its research.

It does **not** limit the agreed demo itself: build whatever the consultant's use cases need — custom objects,
fields, processes, AI, integrations — at every tier. The numbers live in `deal-tiers.json` (edit them there);
`validate_spec.py` enforces them (Q25).

| | **OOTB** — under $50k | **Medium** — $50k to under $100k | **High** — $100k to under $500k | **Extremely high** — $500k and more |
|---|---|---|---|---|
| Proposed additions | 4–6 | 4–8 | 6–10 | 8–12 |
| Largest effort per idea | S | M | L | L |
| Kind of ideas | quick wins with standard functionality (a widget, a rule, a folder) | small and medium additions that sharpen the story; moderate flow improvements | competitive differentiators, smarter steps, larger additions where the research supports them | bold: re-think the flow, new use cases, AI agents, end-to-end scenarios — at least one re-designed flow |

Boundaries: exactly $50k is Medium, exactly $100k is High, exactly $500k is Extremely high.

## ARR answers that are not a number

- Another currency → convert to USD at an approximate current rate; record `arr_original` (e.g. "EUR 70,000").
- A range ("80–120k") → use the midpoint and say so.
- Unknown and the user cannot say → ask once more; if the agent runs in the background and cannot ask, apply the
  **Medium** tier, set `arr_assumed: true`, and put the ARR question first in the hand-over.
