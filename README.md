# Creatio demo scriptwriter

A Claude Code plugin that writes Creatio demo scripts from what the consultant and the customer gave you —
prompt and use cases, discovery-call transcript, materials, agenda — and researches the deal from four sides
before it writes a word: the discovery call, the customer's industry, the competitors (internal battlecards +
vendor websites) and similar past demos in SharePoint **Custom DEMOs**.

Standalone: it does not change or depend on the Creatio Demo Toolkit.

## What you get

For every run, in `<Client>_demo_script/`:

| File | For | Contents |
|---|---|---|
| `<Client>_Demo_Script.docx` | consultant, SE | In the Creatio template: header (instance, demo date, deal size, demo goal) · 1 Brief customer summary · 2 Brief demo summary · 3 Industry context · 4 Roles and logins · 5 **Demo use cases** (purpose, click path, value message, required setup and data) · 6 Competitive positioning *(internal)* · **Appendix**: proposed additions, discovery insights, ideas from similar demos *(internal)*, agenda coverage, open questions |
| `<Client>_Demo_Script.md`, `<Client>_Build_Spec.md` | anyone | The same two documents in Markdown — for GitHub, wikis and editors |
| `<Client>_Build_Spec.docx` | SE, coding agent | Ground rules · build scope (built / simulated / talking point) · before you present · configuration: AI actions, object model, lookups, pages and buttons, dashboards, case management, processes, rules, integrations, notifications, clocks · demo data · decisions |
| `<Client>_Demo_Data.xlsx` | builder | One import-ready sheet per object, hero records highlighted |
| `<Client>_requirements.md`, `spec.json` | build session | Hand-off for the `creatio-demo-builder` agent |

### What it asks you

Only what your inputs do not already answer — at most six questions, in one or two short forms:

1. **Deal ARR (USD) — always asked.** It sets the deal tier:

   | ARR | Tier | New ideas the agent proposes |
   |---|---|---|
   | under $50k | **OOTB** | 4–6 quick wins with standard functionality |
   | $50k–100k | **Medium** | 4–8 small and medium ideas, moderate flow improvements |
   | $100k–500k | **High** | 6–10 ideas incl. competitive differentiators and larger additions |
   | $500k and more | **Extremely high** | 8–12 bold ideas — a re-thought flow, new use cases, AI agents |

   The tier sizes only the new ideas — never the agreed demo: custom objects, fields, processes and AI are built as the use cases need at every tier. Numbers: `skills/creatio-demo-script-generator/references/deal-tiers.json`.
2. Discovery-call transcript — paste or attach it, or say there is none.
3. Documents from the customer (RFP, deck, process docs, spreadsheets, agenda) — attach them, or say there are none.
4. Reference demo instance, if any (a link or name to copy or reuse, or an earlier demo for this customer).
5. What the audience must see — only if there are no use cases and no agenda.
6. Demo date and length — only if missing.

Everything else (who attends, competitors, language, data volume, prefix, demo login…) is decided from the inputs
and the tier.

Every script is checked against 25 quality rules taken from the SE team's feedback on real scripts (instance
named, roles with login modes, every automation real/simulated/talking point, AI with trigger/input/output,
no credentials, no duplicate use cases, every proposal sourced, every competitor claim dated…).

## Install

**Prerequisites** (once per computer)
- Claude Code — the desktop app (Code tab) or the CLI.
- Python 3.10+ (the agent installs the libraries it needs by itself on the first run).
- Microsoft Word (Windows) or LibreOffice, to render the documents for the visual check.
- For the SharePoint research: the **Microsoft 365 connector** enabled in claude.ai (Settings → Connectors) with
  your Creatio account. Without it the agent still runs and lists the skipped research under research gaps.

In any Claude Code session, run once:

```
/plugin marketplace add VitaliiaKovalenko/creatio-demo-scriptwriter
```

```
/plugin install creatio-demo-scriptwriter@creatio-demo-scriptwriter
```

Then start a new chat. In the desktop app the same is under **+** → **Plugins** → **Add plugin** (paste
`VitaliiaKovalenko/creatio-demo-scriptwriter`). Updates — in a terminal: `claude plugin marketplace update creatio-demo-scriptwriter`, then `claude plugin update creatio-demo-scriptwriter@creatio-demo-scriptwriter`, then restart the app.

## Use

In a Claude Code session (desktop Code tab or CLI), either:

- **Interactive (recommended)** — run the skill in the chat so it can ask its intake questions in a form:
  `/creatio-demo-scriptwriter:creatio-demo-script-generator`, then paste the prompt, the use cases and the
  transcript, and attach or point to the customer's files.
- **Delegated** — ask for the agent: *"Use the creatio-demo-scriptwriter agent to write the demo script for
  <customer>. Use cases: … Transcript: … Files: C:\…"*. It runs in the background with sensible defaults and
  reports when done. CLI: `claude --agent creatio-demo-scriptwriter:creatio-demo-scriptwriter`.

Then review the script: answer the questions, and accept or reject the proposed additions — *"accept PA1 and
PA3, reject PA2"* — and the agent revises the script, model and data.

The competitive and similar-demo sections are **internal**. Do not send the Demo Script to the customer as is.

## Maintaining it

The maintainer's working copy lives in `~/.claude/agents/creatio-demo-scriptwriter.md` and
`~/.claude/skills/creatio-demo-script-generator/`. After changing them, run `python sync_from_local.py --public
--version <new>` in this folder (the script is kept out of the repository), commit and push. `--public` replaces
customer and colleague names and internal file IDs, and refuses to finish if any remain.
