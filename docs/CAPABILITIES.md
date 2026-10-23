# Creatio Demo Scriptwriter — what it does

An AI agent for solution consultants. You give it what you have from the customer; it researches the deal and
writes a demo package an SE can build from without asking. Installation: [INSTALL.md](INSTALL.md).

## In one line

Your inputs → research from four sides → use cases → proposed additions → quality checks → demo package. The deal ARR decides how much is built.

## 1. What you give it

| Input | Needed? |
|---|---|
| A short prompt: the customer, what you want to show, your use cases if you have them | yes |
| **Deal ARR (USD)** | **yes — always asked** |
| Discovery-call transcript (pasted or attached) | recommended — adds the Discovery insights |
| Customer documents: RFP, deck, process docs, spreadsheets, agenda | recommended |
| Reference demo instance to copy or reuse | if there is one |
| Demo date and length | if you know them |

It asks only what is missing — at most six short questions, the ARR always first. Everything else (who attends,
competitors, language, data volume…) it works out from the material and tells you what it assumed.

## 2. What it researches — on every script, with or without a transcript

| Side | What you get |
|---|---|
| **Discovery call** | Key moments with timestamp, speaker and quote — pains, requirements, objections, decision makers, current systems, competitors mentioned, timeline, risks — each checked against your use cases. *Not covered* moments become proposals. |
| **Industry** | 5–10 points that matter in the customer's industry (processes, regulations, KPIs, vocabulary) and what each means for the demo. |
| **Competitors** *(internal)* | The 2–4 that matter in this deal — Salesforce, Microsoft, SAP, HubSpot, Oracle and others — from internal battlecards and the vendors' own websites: what they would show, where they are genuinely strong, where Creatio wins here, a demo highlight and a trap to avoid per use case. Every claim sourced and dated. |
| **Past demos** *(internal)* | Similar Creatio demos found in the team's SharePoint demo library: what to reuse and the lessons learned. Ideas only — no other customer's names or data. |

Anything it could not research (no transcript, SharePoint not connected) is listed openly as a research gap.

## 3. What it suggests — proposed additions

A ranked list of extra functionality or story improvements, each with **why**, its **sources** (the transcript minute,
industry point, competitor point, past demo or customer document), **what the audience would see**, **where it fits**
and the **effort**. The agent asks you once, after the research, which ideas you accept. Accepted ideas are written
into the use cases; rejected ones are dropped; the documents never carry a separate list of ideas. A background run
cannot ask, so it lists them in its report for you to answer: *"accept PA1 and PA3, reject PA2"*.

## 4. How many new ideas — the deal tier

| Deal ARR | Tier | New ideas the agent proposes |
|---|---|---|
| under $50k | **OOTB** | 4–6 quick wins with standard functionality |
| $50k–100k | **Medium** | 4–8 small and medium ideas, moderate flow improvements |
| $100k–500k | **High** | 6–10 ideas incl. competitive differentiators and larger additions |
| $500k and more | **Extremely high** | 8–12 bold ideas — a re-thought flow, new use cases, AI agents |

The tier sizes only the new ideas. The agreed demo is built as the use cases need — custom objects, fields, processes and AI included — at every tier.

## 5. What you get back

In `<Customer>_demo_script/`:

| File | For | Contents |
|---|---|---|
| **Demo Script** (.md) | you, the SE | Header (instance, demo date, deal size, demo goal) · 1 Brief customer summary · 2 Brief demo summary · 3 Industry context · 4 Roles and logins · 5 **Demo use cases** (purpose, click path, value message, required setup and data) · 6 Competitive positioning *(internal)* · **Appendix**: discovery insights, ideas from similar demos *(internal)*, supporting texts |
| **Shareable page** (link) | your team, reviewers | The same Demo Script as a private Claude page: share it from its Share menu. An external copy without the internal sections is available for the customer. |
| **Build Specification** (.md) | the SE, a coding agent | Ground rules · build scope (built / simulated / talking point) · before you present · configuration: AI actions, object model, lookups, pages and buttons, dashboards, case management, processes, rules, integrations, notifications, clocks · demo data |
| **Demo data** (.xlsx) | the builder | Import-ready sheets per object, realistic for the customer's region, hero records highlighted |
| requirements.md, spec.json | the demo build | Hand-off for the build agent |

Documents are Markdown, Excel is only for data; Word in the Creatio template on request. Open questions and the
agent's decisions come in its report, not in the documents.

## 6. Quality built in

Every script is checked against 25 rules taken from the SE team's feedback on real scripts. Among them: the demo
instance is named; every role says how it logs in; every automation is marked **real / simulated / talking point**
with what the audience sees; every AI action has trigger, input, output, storage and review; standard Creatio objects
are used first; no credentials anywhere; duplicate use cases are flagged; every proposal and competitor claim has a
source; configuration stays within the deal tier.

## 7. Working with it

- **New customer → new chat.** Ask in plain words (*"Write a demo script for …"*) or type `/demo` and pick the
  command — both work; the command just guarantees the start.
- **Revisions → same chat, plain words.** *"UC2 step 4 — a button, not a list"*, *"add 20 more closed cases"*,
  *"accept PA1"*. It updates the script, model and data together and bumps the version.
- **Background mode.** *"Use the creatio-demo-scriptwriter agent to write the demo script for …"* — give everything in
  one message, including the ARR; it cannot ask questions while running in the background.
- **Moving the demo date** is one sentence (*"the demo moved to 12 November"*) — all dates in the data and the
  script move with it.

## 8. What it does not do

- It writes documents only — it never touches a Creatio instance. The build is a separate step.
- It does not send anything to the customer. **Remove the internal sections** (competitive positioning, ideas from
  similar demos) before sharing the Demo Script outside Creatio.
- It does not invent facts: competitor claims without a source are dropped, and assumptions are listed in its report
  as decisions or questions with the default it applied.
