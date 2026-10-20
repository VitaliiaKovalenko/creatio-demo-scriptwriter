# 07 — Approvals & Creatio.ai (Creatio 8.x Freedom UI)

> Capsule file. Source: Creatio Academy only, retrieved 2026-08-27. **UNVERIFIED** = never use in demo steps.

---

## A. Approvals

### A1. In Freedom UI pages
- Two Designer components: **Approvals** (individual approvals on the record) and **Approvals list** (whole approval process as a list). Their behavior is "pre-configured and non-editable"; after adding the component, "set up the approval mechanism in a business process or case."
- Out of the box, approval components are available in **Contracts**, **Invoices**, **Orders** — and "can be added to any section if needed" (requires enabling approvals in the section).
- Approval record data: **Approval objective/purpose**, **Approver**, status (**To set** → **Positive** / **Negative**), **Comment**, **Delegated from**. **UNVERIFIED**: an explicit "Set date" field label and the underlying table name (SysApproval) in 8.x user docs — do not cite the table name in demo narration (the object-model spreadsheets remain the source for field-level claims).
- Users can also act on approvals from the **notification panel** (top right). Actions apply only to approvals in **"To set"** status that are not canceled.

### A2. Sending, outcomes, delegation, notifications
- Approvals are created by the **Approval** element of a **business process** ("if the approval process is complex") or an approval step in a **case** ("if the approval process is simple"; created automatically when the case stage activates).
- **Approval element parameters** (exact labels): **Approval purpose** (default "Approval required"), **Approval object**, **Record Id**, **Approver** (specific **Employee** / **Employee's manager** / **Role** members), **Approval may be delegated**, **Notify that approval is required**, **Notify about the approval result**, **Ignore errors on sending**. Route the process afterward with **conditional flows** on the result.
- **User actions on an approval**: **Approve** (→ "Positive"), **Reject** (opens a comment window; → "Negative"; comment optional by default, can be made required via system setting), **Change approver** (delegation — only when **Delegation permitted** is enabled and **Delegated from** is empty; current user → **Delegated from**, new user → **Approver**).
- Email: notification emails are enabled in the Approval element properties. **UNVERIFIED**: approving/rejecting directly from the email — do not demo one-click email approval without checking the stand.

Toolkit convention (not docs): approvals are addressed to a **role**, so one demo user sees the whole chain.

## B. Creatio.ai

> **Vocabulary rule: demos always target the CURRENT Creatio version.** Write AI steps in the **Creatio.ai** vocabulary below — it is canonical. Historical note for reading old screenshots only: on an 8.1.4 stand (2026-08-28) the assistant was still branded **Creatio Copilot** (panel "Copilot", System Designer → **Copilot intents**); never write "Copilot" into new demo documents. See `LEARNINGS.md` §7.

### B1. What it is and where it sits
- **Creatio.ai** is "natively embedded AI functionality in the core of the Creatio Freedom UI platform" — predictive, generative, and agentic AI; a virtual assistant (chat) for tasks like email generation, meeting summaries, record updates.
- UI entry point: the **AI button in the top right** of the Freedom UI shell opens the assistant panel. Requires Freedom UI; "does not work with graphics, widgets, and dashboards."
- Administration: **AI Command Center**. Licensing: included in all platform versions; usage metered in **AI Actions** (one AI Action = one LLM interaction).

### B2. AI Skills
- An **AI Skill** is "a comprehensive, end-to-end AI-enabled task that can be executed for a user."
- Anatomy: a **Prompt** (task instruction for the LLM), **Actions** ("individual steps... building blocks for agentic AI behavior" — chat-mode skills only; configured no-code, e.g., via the Process Designer), **Input/Output parameters** (workflow-mode skills only).
- Modes — the **"Where to use"** property ("Usage mode" ≤8.3.2): **Prompt agents** ("Chat") for interactive conversation vs **Workflows** ("API") for system-level use (this is what the **Call Creatio.ai** process element invokes).
- Confirm-before-write: OOTB system skills **"Generate confirmation message for action launch"** and **"Match confirmation response"** exist — i.e., the assistant asks the user to confirm before launching actions. **Phrase demos as "Creatio.ai asks for confirmation before launching the action" — nothing stronger.** A formal "read skill vs action skill" taxonomy: **UNVERIFIED** (the documented split is chat-mode skills with Actions vs workflow-mode skills).

### B3. Out-of-the-box AI skills the docs name (safe to demo BY NAME)
- **Platform / Business Studio:** Search data; Prepare an email; Reply to email; Summarize email; Summarize activity; Identify contacts; New meeting; Extend / Shorten / Rephrase / Translate text; Formal & Friendly text rewrite; Create chart / list / metric / pipeline / sales pipeline widgets (in chat); Account news and insights; Account profiling; Prepare for the sales meeting; Address splitter; Language detector.
- **Sales:** Summarize lead; Summarize opportunity; Generate lead call script; Provide lead probability insights; Prepare for the meeting; Prepare meeting agenda; Recommend products; Generate product description; Enrich opportunity.
- **Marketing:** Create bulk email record; Enhance bulk email subject line; Email copywriter; Email designer; Edit email template; Create email subject; Analyze bounce responses; Provide account/contact conversion insights; Landing copywriter; Landing page designer; Create landing page record.
- **Service:** Summarize case; Suggest case resolution; Case performance; Create article (KB from case resolution); Check open cases.
- **UNVERIFIED:** "Next best action" as a named OOTB feature — closest documented items are **Suggest case resolution** and **Recommend products**. Do not use "next best action" as a product feature name.

Toolkit convention (not docs): an AI step in a demo scenario is written as a **dialogue** — the user's ask, the agent's reply, the user's confirmation, then the write.

## C. Creatio AI Studio & AI Twin (team decision 2026-08-28 + Academy/creatio.com)

- **Creatio AI Studio is a separate product**: "a unified environment in Creatio for building, deploying, and operating AI Agents" — design, execution, connection, governance and observability. Components: **Prompt Agent Designer** (natural language, no code), **Workflow Agent Designer** (visual multi-step flows), **Code Agent Designer** (preview); agents extend via **Skills**, **Tools** (APIs, workflows, system actions) and **Knowledge sources** (CRM data, documents, external repositories); deployment channels: web chat, email, SMS, social, collaboration tools, voice; integrations via **MCP, APIs, webhooks**. Availability: on a request basis (via Creatio success manager).
- **AI Twin** — the AI Studio component that gives every employee a personal agent. ⭐ **Team direction: the Creatio.ai side panel in the shell is being replaced by the AI Twin panel from AI Studio.** For demo *steps* nothing much changes — "open the AI side panel and ask" stays the same interaction — so Demo Flow steps keep the same shape and name the panel **AI Twin (Creatio AI Studio)** on stands where it is deployed.
- **What changes for demo engineers: setup.** A demo that shows AI now carries an explicit configuration item — **connect and configure AI Studio** (instance connection, the agent(s)/skills the demo uses, channels if any). The behavior specification must list this as a prerequisite / human-configured artifact; it is never implied silently.
- Verify on the target stand which panel is present (legacy Creatio.ai vs AI Twin); the demo targets the current version, so default to AI Twin when the stand has AI Studio.

## D. Integrations shown in demos (team rule 2026-08-28)

Demos sometimes include **integrations** — e.g. WhatsApp (chat channel behind the Send chat message element / Chats tab of the communication panel), telephony (calls tab), email mailboxes. Rules:

1. **Every integration a step depends on is identified explicitly** in the Demo Flow (header block "Integrations involved" + named in the step's element column, e.g. "Chats · WhatsApp channel (integration)").
2. Each integration becomes a **human-configured artifact** in the behavior specification (INT-<n>) with its own BUILD-STATUS row — channel setup is never assumed to exist.
3. If the demo narrates an integration without a live connection (simulated log, seeded messages), that is a **C. Out of scope** entry, not an INT artifact.

## Sources

**Approvals**
- https://academy.creatio.com/docs/8.x/creatio-apps/creatio-basics/communications/approvals
- https://academy.creatio.com/docs/user/bpm_tools/process_elements_reference/user_actions/approval/approval_process_element
- https://academy.creatio.com/guides/no-code-customization/bpm-tools/dynamic-case-setup/case-designer-workflows/set-up-approval-case

**Creatio.ai**
- https://academy.creatio.com/docs/8.x/no-code-customization/ai-tools/creatio-ai/creatio-ai-overview
- https://academy.creatio.com/docs/8.x/no-code-customization/ai-tools/creatio-ai/develop-ai-skill/introduction-to-ai-skill-development
- https://academy.creatio.com/guides/no-code-customization/ai-tools/creatio-ai/ai-skill-list
- https://academy.creatio.com/docs/8.x/no-code-customization/bpm-tools/process-elements-reference/system-actions/call-creatio-ai-element
