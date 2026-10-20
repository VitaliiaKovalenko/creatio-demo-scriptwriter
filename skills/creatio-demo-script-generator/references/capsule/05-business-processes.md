# 05 — Process Designer (BPMN) Element Palette (Creatio 8.x)

> Capsule file. Source: Creatio Academy only, retrieved 2026-08-27. This is the build palette for
> business processes: **only elements named below exist**. **[DEV]** = requires code (never promise
> as no-code in a demo spec). **UNVERIFIED** = never use.
> Toolbar groups: **User actions · System actions · Start events · Intermediate events · End events · Gateways** (+ flows, + Sub-process containers).

---

## 1. Start events

| Element (exact name) | Fires when | Key settings |
|---|---|---|
| **Simple** (Simple start event) | A user runs the process manually (Process library **Run**, run-process button, section/record button), or a parent process calls it as a sub-process. A process must start with Simple to be usable as a sub-process. | `Run following elements in the background` |
| **Signal** (Signal start event) | Automatically: (a) **Custom signal** — a matching **Throw signal** from another process; (b) **Object signal** — a record in an object is **added / modified / deleted**. | Signal type; Custom: signal name (exact match with Throw signal). Object: object; mode (added/modified/deleted); for "modified": any field vs selected fields; filter conditions; background. Output: **Id of the triggering record**. Cautions: delete the default Simple start first (one start style); unfiltered signals spawn excessive instances; avoid loops where the process modifies its own trigger object |
| **Message** (Message start event) | Starts an **Event sub-process** inside the same diagram when a matching **Throw message** fires. Can fire multiple times per instance. | Message name (exact match); background. Only inside Event sub-processes |
| **Start timer** (Start timer event) | On a schedule. | Frequency: **Once** / **Minute/Hour** / **Day** / **Week** / **Month** / **Year** / **Other frequency** = **cron (Quartz syntax)**; start time; **Time zone**; `Repeat on misfire`; optional **Timer validity** window |

## 2. Intermediate and End events

| Element (exact name) | Semantics | Key settings |
|---|---|---|
| **Throw signal** | Broadcasts a named signal **system-wide** (to all active processes and Signal start events); continues immediately. | Signal name (exact match with receivers) |
| **Wait for signal** | Pauses the branch until a matching **Throw signal**, or a monitored record is **modified/deleted** (record signal). | Custom signal (name) vs Record signal (object, mode, filters); background |
| **Throw message** | Generates a named message **within the current process only**. | Message name |
| **Wait for message** | Pauses until a matching **Throw message** in the same instance. | Message name; background |
| **Wait for timer** | Pauses the branch for a fixed delay. | `Start in (sec.)` — seconds; mappable from a parameter/formula |
| **Terminate** (Terminate end event) | **Immediately terminates the whole process instance** (all branches). Without it, an instance stays Running until all branches finish. | No outgoing flows allowed. The 8.x End events group contains **Terminate**; there is no separately documented plain "End" element — treat "end" as branches completing or Terminate |

## 3. User actions

Full documented set: **Perform task, User dialog, Open edit page, Auto-generated page, Send email, Pre-configured page, Approval, Validation, Send chat message.**

| Element | Purpose | Key settings |
|---|---|---|
| **Perform task** | Creates an Activity; process **pauses until completed**. | "What should be done?"; performer — user / employee's manager / role; **Task category** (required); `Start in`, `Planned duration`, `Remind in`; `Show in calendar`; `Show page automatically`; hint; **Connected to**; background. The task's **result** (Activity results lookup) drives **conditional flows** |
| **Approval** | Creates an approval; branches on the verdict. | Approval objective; **Approval object** (required; object must have **approvals enabled**); **Record Id** (required, mappable); approver: employee / employee's manager / role members; `Delegation permitted`; notifications (approver on creation; recipient on result); result drives conditional flows; logged on the record's Approvals tab |
| **Send email** | Email — **automatic** (no user) or **manual** (user finishes a draft). | Mode: `Send email automatically` (needs integrated **From** mailbox) vs `Send email manually` (draft task for user/role); To/Cc/Bcc; Subject; body: **Template message** (+ "Record for macros") vs **Custom message** (Content Designer); attachments (e.g., from **Process file**); importance; log as activity; connect to records; `Ignore errors during sending` |
| **Open edit page** | Opens a record edit page (new or existing); completes on save or on conditions. | Object (required); mode: **New record** (default field values) vs **Existing record** (record Id); performer; `Show page automatically`; recommendation (required) + hint; completion: "immediately after saving" / "when record matches filter conditions"; background; optional activity. ⚠️ Parallel Open edit page elements on the same object need distinct completion conditions. No element named "Open Freedom UI page" exists — for custom Freedom UI process pages use **Pre-configured page** |
| **Auto-generated page** | Ad-hoc form generated from declared items and buttons. | Page title; performer; auto-show; recommendation + hint; **Page items**: Text (multiline option), Selection field (dropdown or lookup view), Date/time, Integer, Decimal (+ Notes, item blocks) — each with Title, Code, `Required`; **Buttons**: Caption, Code, Style — *the clicked button is the element's result* (drives conditional flows); entered values become output parameters. Classic-UI-styled page |
| **Pre-configured page** | Opens a **custom-designed page** (designed once, reused) — the Freedom-UI-native process UI. | "Which page to open?" — existing or new; template: **Freedom UI page** (Freedom UI Designer) or **Classic UI page** — *cannot be changed after selection*; performer; auto-show; recommendation + hint; **page parameters** (defaults, mapping to/from process parameters); **which buttons complete the element** (Freedom UI); each button = result for conditional flows; background; optional activity |
| **User dialog** | Question with preset answer options; the choice drives branching. | Dialog text; answer options (ordered); `User can choose one option` (branch with **Exclusive gateway**) or `User can choose multiple options` (branch with **Inclusive gateway**); default answer; required-selection; performer; auto-show; hint; background; optional activity |
| **Validation** | ⚠️ Lending/bank products only. | Do not use in generic builds. Post-validation C# hook **[DEV]** |
| **Send chat message** | Chat message to a customer via a configured channel (e.g., WhatsApp). | From (channel — must be configured); To; template vs custom text; `Ignore errors`; column values to link chat to records; channel rules apply (WhatsApp 24-hour rule) |

## 4. System actions

Full documented set: **Read data, Add data, Modify data, Delete data, Formula, Call web service, Change access rights, Predict data, Script task, Connect process to object, User task, Process file, Find and merge duplicates, Call Creatio.ai.** All run in the background and by default **bypass user access permissions** (unless "Use user permissions for elements" is enabled).

| Element | Purpose | Key settings |
|---|---|---|
| **Read data** | Reads field values into parameters. | **Read mode (4):** `Read the first record in selection` (filter + sort); `Read collection of records` (limit; output = collection parameter); `Calculate the number of records`; `Calculate function` (Sum/Average/Min/Max over a column). Object; **filters**; **sorting field** (no sort/ties → earliest-created wins); columns to read |
| **Add data** | Creates records (permission-bypassing). | Object; mode: **Add one record** (explicit values) vs **Add selection** (bulk from a filtered selection with column mapping). Output: **only the Id** — Read data afterward for other fields |
| **Modify data** | Changes records in the background. | Object; **filter — modifies ALL matching records** with the same values; fields + values. Different values per group → multiple Modify data elements |
| **Delete data** | Deletes matching records — permanent, no confirmation. | Object; filters. Extreme care |
| **Formula** | Computes a value into **one existing parameter**; also the mechanism behind conditional-flow expressions. | Target parameter (must exist; types must match); expression over element/process parameters, system settings/variables, lookup values, functions, date/time functions. One parameter per element |
| **Call web service** | Calls a pre-configured web service method. | Service; method; request mapping; timeout/retries; response parameters mappable; built-in outputs **Success** (HTTP < 400) and **Http status code**. Service must be registered in the **Web services** section first (semi-technical). Deeply nested collections: top-level only |
| **Change access rights** | Grants/revokes record permissions in-flow. | Object; record filter; operations add/remove **Read/Edit/Delete**; level "Permit with rights to delegate" / "Restrict"; recipients: role / employee / employees by filter |
| **Predict data** | Applies a **trained ML model**. | ML model (untrained not selectable); records to predict for |
| **Script task** **[DEV]** | Arbitrary C# code. | Must end `return true;`; Get/Set parameter access. **Developer-only — never promise as no-code** |
| **User task** | Runs a reusable user task type. | Type selection determines Parameters tab. Using existing types = no-code; **creating custom types = [DEV]** |
| **Process file** | File ops: read from attachments/parameters, **generate Word reports**, save to Attachments. | Source: record attachments (filter + sort) / parameter / generated report (type, filename pattern, filters); handling: "Use in process" (file Id for Send email etc.) vs "Save to attachments" |
| **Find and merge duplicates** | Finds and merges duplicates by active duplicate rules. | Object (needs active rules); record Id; "All rules" or selected. Merge keeps earliest-created record's populated fields |
| **Connect process to object** | Links the instance to record(s) → **Linked objects** block of the Process log. | Connected object; record. Traceability only |
| **Call Creatio.ai** | Invokes a configured **AI Skill** from the process. | Skill (Active, "Workflows" mode); input values; output mapping; outputs incl. status code, warnings/errors, response text. Collections map only via Formula; "Collection of records" outputs unsupported; branch on status (LLM parsing can fail). Needs Creatio AI enabled |

## 5. Gateways and flows

### Gateways (exactly four)

| Gateway (exact name) | Split | Merge |
|---|---|---|
| **Exclusive gateway (OR)** | Exactly **one** outgoing path (first true conditional flow); **default flow required**. | Continues on **any one** incoming flow |
| **Inclusive gateway (OR)** | **Every** true conditional flow runs (concurrently); **default flow mandatory**. | Merges like converging exclusive |
| **Parallel gateway (AND)** | Forks into simultaneous branches (plain sequence flows only). | **Waits for ALL** incoming flows (join) |
| **Exclusive event-based gateway** | Followed by catching events (**Wait for message / Wait for signal / Wait for timer**); **first event to fire wins**. No conditions — routing by which event occurs first (e.g., "reply received" vs "3-day timeout") | — |

### Flows

| Flow | Semantics |
|---|---|
| **Sequence flow** | Plain order. ⚠️ **Multiple outgoing sequence flows from one element all activate simultaneously** (implicit parallel fork) |
| **Conditional flow** | Activates when its condition is true. Two styles: (1) **element result** — from user actions with results (Perform task result, User dialog answer, page button, Approval verdict); (2) **formula** — Boolean expression over parameters / fields read earlier / system settings / lookup values |
| **Default flow** | Fallback when **no conditional flow** can activate. Mandatory whenever at least one conditional flow leaves the element |

## 6. Sub-processes

| Element | Purpose | Key settings |
|---|---|---|
| **Sub-process** (Call sub-process) | Runs another process; outgoing flows wait for its completion. | Target must start with **Simple start event**; two-way **parameter mapping**; **multi-instance**: a collection parameter → one instance per item, `Sequential` (default) or `Parallel` |
| **Event sub-process** | Detached diagram area that runs whenever its internal **Message start event** is triggered (via Throw message) — repeatable, non-blocking. | Must contain a Message start event; no sequence-flow connection to the main diagram; logs as part of the parent |

## 7. Process-level concepts

- **Parameters.** Types: Text, Integer, Decimal, Boolean, Date/Time, Lookup, Currency, Collection of records, Unique identifier (Id). Input vs output. Value sources: manual, parameter mapping, system setting, system variable, formula, lookup value. Compatibility: like-to-like; documented exceptions — Date/Time interchange, Integer↔Decimal, Lookup accepts record Ids.
- **Process properties**: Caption; **Code**; Version (auto); Tag; description; **Maximum repetitions** (loop guard); **Process instance caption**; **Serialize in DB**; logging toggles; **Use system security context** (default on); tracing; "Display in run process button list". **Save** vs **Publish** — only active published processes run.
- **How a process can start (run modes)**:
  1. Manually — Process library **Run**, run-process button, command line.
  2. From a section/record — Section Wizard → **Business processes** tab → "Run business process from section" (adds a **Run process** button; **For selected record** passes the Id into an Id-type parameter).
  3. By record event (**Signal** start).
  4. On schedule (**Start timer**, incl. cron).
  5. By signal from another process, or as a **Sub-process**.
  6. From a **DCM case stage** (the case's Sub-process step).
  7. Via API (ProcessEngineService) **[DEV]**.
- **Versioning**: saving creates a new version automatically; exactly one version is "actual"; any version can be set actual; all versions usable as sub-processes.
- **Logging**: **Process log** section — one record per instance: initiator, status (**Running / Completed / Canceled / Error**), executed steps, execution diagram, **Linked objects**. Archive after 30 days (`ProcessLogArchivingPeriod`); per-process **tracing**; cancel from the log.

## 8. No-code vs needs-dev summary

| Fully no-code | Conditionally no-code | **[DEV]** |
|---|---|---|
| All events, gateways, flows; Perform task; Approval; Send email; Open edit page; Auto-generated page; Pre-configured page; User dialog; Send chat message; Read/Add/Modify/Delete data; Formula; Change access rights; Connect process to object; Process file; Find and merge duplicates; Sub-process; Event sub-process; Predict data (needs trained ML model); Call Creatio.ai (needs active AI Skill) | **Call web service** (service must be registered first); **User task** (existing types); **Validation** (bank/lending only) | **Script task**; custom User task types; Validation C# hooks; ProcessEngineService API |

## 9. Spec template for the behavior file (skill 3 output, Claude-Code-built part)

```
BP-<n>: <process name>
  Start: <start event type + trigger settings (object/mode/filters or schedule or manual)>
  Parameters: <name: type (in/out)> ...
  Elements (in order, with flows):
    <element name> — <exact palette type>; <key settings>
    <gateway>: <conditional flow: condition> → <target element>; default → <target>
  End: <how branches complete / Terminate>
  Run mode: <how it is started in the demo>
  Supports steps: <Demo Flow step IDs>
```

## Sources

Category indexes: process-elements-reference · user-actions · system-actions · events · gateways · sub-processes · business-process-flows-and-connecting-objects (all under https://academy.creatio.com/docs/8.x/no-code-customization/).
Key pages: process-designer · process-parameters · every element page listed per table above (URL pattern: `.../bpm-tools/process-elements-reference/<group>/<element>-process-element`).
Run/administration: run_business_process · set_up_business_process_launch_from_a_section_record · view_process_properties · view_process_execution_data · trace-process · cancel_process (docs/user/bpm_tools/...).
