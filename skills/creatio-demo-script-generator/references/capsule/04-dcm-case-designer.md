# 04 — Dynamic Case Management & Case Designer (Creatio 8.x)

> Capsule file. Source: Creatio Academy only, retrieved 2026-08-27. Serves two readers: skill 1/3
> (allowed vocabulary + spec semantics) and the HUMAN who configures DCM by hand in the Case Designer.
> **UNVERIFIED** = never use in demo steps or specs.

---

## 1. Concepts

- **A case (DCM flow)** is "a workflow with a business value to a customer, partner, or stakeholder" — a set of stages containing steps. DCM is for **non-linear** work (multiple paths to success), in contrast to a rigid BPMN process.
- **Binding to an object.** A case is created **per section (object)**:
  - **Section** — the section the case runs in (cannot be changed after the case is first saved).
  - **Stage column** — a **lookup column** of the section's object storing each record's current stage. The case's stages map 1:1 to records of that lookup (**Stage value in lookup** on each stage).
- **Stage vs. status.** "Stage" is whatever lookup column is chosen in "**Which column to build the stages by?**" — the docs' own approval-case example builds stages on the "Status" column. Toolkit convention (not docs): keep Stage and Status as separate columns; Stage drives DCM, Status is the granular state inside a stage.
- **How the stage bar appears on pages:**
  - **Freedom UI**: the **Progress bar** component ("track and change case stages") + **Next steps** component (activities/tasks as tiles, auto-updates by stage; behavior pre-configured). ✅ Verified 8.1.4: Progress bar properties = Data source, **Set up cases** button (opens the Case Designer — a Classic UI page, DcmDesigner), VISIBILITY → Setup conditions, ADVANCED → **Save record on stage change** and **Show snack bar notification for case update** toggles, Element code `EntityStageProgressBar_*`.
  - **Classic UI**: **workflow bar** + **action panel** (quarantined vocabulary).

## 2. Case Designer walkthrough (human-facing)

### 2.1 Opening
- Freedom UI: in the Freedom UI Designer, select the **Progress bar** component → click **Set up cases**.
- Classic UI section: **View** menu → **Set up section cases**, or the **Cases** tab in the Section Wizard. Then **New case** or select + **Open**.

### 2.2 Section-level case settings
1. **Which column to build the stages by?** — the lookup column whose values become the stages.
2. **Which column to set initial case condition by?** — decides **which** case runs for a record when the section has several cases. (The docs' 8.x wording is canonical for specs; on an older 8.1.4 stand the label read "Which column determines which case to use with a record?" — recorded only for reading old screenshots, LEARNINGS.md §6.)
3. ⚠️ Changing either of these two fields "will deactivate all cases that have incompatible column values."
4. Deactivate a case via **Actions** → **Deactivate case**.

### 2.3 Working area
- **Stages panel** — the lane to map/manage workflow stages (add/remove/connect; shown on the stage bar).
- **Working area** — add and arrange step elements inside each stage.
- **Setup area** — properties of the selected case/stage/element; **primary mode** (user settings) vs **advanced mode** (all parameters).

### 2.4 Case-level properties
Case title; **Section**, **Stage column**, **Code**, **Package**, **Active**, **Actual version**; and **"Use this case with records where:"** — the filter selecting which records this case applies to.

### 2.5 Stages
- **Add**: (+) after the last stage, or between two stages to insert.
- **Stage properties**:
  - **Element name** — renaming updates the underlying lookup record.
  - **Stage value in lookup** (required) — a new lookup value can be created right in this field.
  - **Possible next stages** / **Possible previous stages** — restrict movement (default: all). This is how skipping/moving back is restricted; there is no separate "allow move back" checkbox.
  - **Automatic transition**: "Only manually (no automatic transition)" / "If required steps are completed" / "If all steps are completed".
  - **Group with other stage** — merges stages into one dropdown slot on the bar (e.g., mutually exclusive final stages Completed/Canceled).
  - **Stage is successful** — marks a **final** stage as the successful outcome (final stages only).
  - **Stage color**.
  - Playbook hints can be attached to a stage.
- **Reorder** by dragging (steps move with the stage); **deleting** a stage deletes its steps, the lookup record survives.

### 2.6 Branching (conditional stage flows)
- Default flow: left-to-right stage order constrained by Possible next/previous stages.
- **Branching lives on step elements**, not stages: the **"Change stage after element is completed"** area — rules of the form **If result** (e.g., Approval "Positive"/"Negative", or a sub-process output) → **Set stage to**. Docs example: HR approval "Negative" → back to "Draft"; manager approval "Positive" → "Completed", "Negative" → "Canceled".
- **Open edit page** additionally supports "**When is the element considered complete?**" = "If the record matches conditions" — field values can gate progression. Stage-level branching on arbitrary field conditions without an element: **UNVERIFIED** — do not spec it.

## 3. Step (element) types — exact names and settings

**Adding a step:** add-element icon below a stage → pick type → name → configure. Steps drag within/between stages.

**Settings shared by (nearly) all elements:**
- **When is the step performed?** — "At the start of the stage" / "After the previous step is complete" (**Perform after step**).
- **Step type** — "Required step" / "Optional step".
- **Change stage after element is completed** — conditional transitions.

| # | Element (exact name) | Purpose | Key settings |
|---|---|---|---|
| 1 | **Perform task** | Creates an activity | **What should be done?** (required), **Hint for user**, **Task category** (required, e.g. To do); **Who performs the task?** — "User" / "Employee's manager" / "Role"; **Start in**, **Planned duration**, **Remind in** (minutes); **Priority** (required, default Medium — verified on a live stand, not in the docs' list); **Show page automatically**, **Run following elements in the background**, **Show in calendar**, **Connected to** (e.g. Case = `[#Main record.Id#]`) |
| 2 | **Send email** | Manual or automatic email | **From** (required for automatic), **To** (required), **Subject**; **What is the message?** — "Custom message" (Content Designer) / "Template message" (+ **Record for macros**); **How is the message sent?** — manual (adds performer, hint, auto-show) / automatic (adds **Importance**, **Ignore errors on sending**) |
| 3 | **Approval** | Approval step (requires "Enable approval in section" in the Section Wizard) | **Approval purpose**, **Approval section**, **Record Id** (required); **Approver** — "User" / "Employee's manager" / "Roles"; **Approval may be delegated**; **Notify that approval is required** (+ template), **Notify about the approval result** (+ recipient, template), **Ignore errors on sending** |
| 4 | **Open edit page** | Opens a record page to fill/review | **Which page to open?** (required); **Editing mode** — "Add new record" (with default field values) / "Edit existing record" (+ Record ID); performer; **Show page automatically**; **Recommendations for filling in the page** (required); **When is the element considered complete?** — "Immediately after saving the record" / "If the record matches conditions"; background; optional **Create activity** |
| 5 | **Change access rights** | Changes record permissions automatically | Target object + filters; remove rights (all users/roles/employees/by filter) and/or grant (roles/employees/by filter) for read/edit/delete at **Granted** / **Granted with right to delegate** |
| 6 | **Sub-process** (full name in the Add step menu: "**Sub-process (Call activity)**", verified 8.1.4) | Runs a BPMN business process | **Which process to run?**; **Process parameters** mapped to main-record columns. "Starts automatically when you transition to the stage that has this step" |
| 7 | **Validation** | ⚠️ Industry-specific (lending / Bank.AI edition only) | Do not use in generic builds |

## 4. Execution behavior

- **Launch**: a case starts automatically when a new record matching its launch conditions is created; first-stage activities/sub-processes run immediately.
- **Step activation**: stage elements activate on stage entry; "After the previous step is complete" steps wait for their predecessor. Case activities appear in **Next steps** tiles (Freedom UI).
- **Completing a stage**: only **required** steps must be completed to advance. Automatic advancement per the stage's automatic-transition setting; users can also click/drag the stage on the Progress bar (within Possible next stages).
- **Skipping ahead**: allowed once required steps are done; "all unfinished tasks and case steps of the previous stages will be canceled." Exception: an **unsuccessful final stage is reachable from anywhere** without completing required steps.
- **Moving backward**: allowed within Possible previous stages; unfinished tasks of the current stage are canceled, and **new tasks are created** for the stage returned to (steps re-activate fresh — duplicate-activity surprise in demos).
- **Final stage**: if the last stage has no steps, the case completes on selection; incomplete prior steps auto-cancel.
- **Multiple cases per section**: each record runs **exactly one case**, chosen by "Which column to set initial case condition by?" + each case's "Use this case with records where:". If the trigger value changes, the user can switch via the **Change case** button (cancel-and-restart). Tie-breaking when two cases match: **UNVERIFIED**.
- **Versioning**: on save — new version vs update current (new version recommended with running instances). **Case versions** tab; "Set as actual version"; running instances keep their old version.

## 5. Limits / gotchas

- One case per record at a time; selection by column, not by user (except **Change case**).
- **Section binding is immutable** after first save.
- Changing the two section-level columns deactivates incompatible cases.
- Deactivating a case stops it only for new records.
- Deleting a stage deletes its steps; records sitting in a deleted stage keep the lookup value and must be moved manually.
- Renaming a stage renames the **lookup record** (affects everything using it).
- **Approval** step requires approvals enabled in the section first.
- DCM has **no gateways** — branching is only per-element via "Change stage after element is completed"; complex logic belongs in a **Sub-process** (full BPMN).
- **Change access rights** applies changes simultaneously; sequential changes need multiple elements.
- Classic vs Freedom UI: same DCM engine and Case Designer; difference is presentation (workflow bar + action panel vs **Progress bar** + **Next steps**).

## 6. Spec template for the behavior file (skill 3 output, human-configured part)

```
DCM-<n>: <case name>
  Object/Section: <name>;  Stage column: <lookup column>
  Case condition: <"Use this case with records where" filter, if any>
  Stages (in order):
    <Stage name> [lookup value] [color] [final? successful?]
      - <step name> — <element type>; performed: <at start / after step X>; <required/optional>;
        <type-specific settings>; transitions: <If result → Set stage to, if any>
  Supports steps: <Demo Flow step IDs>
```

## Sources

- https://academy.creatio.com/guides/no-code-customization/bpm-tools/dynamic-case-setup/case-designer-workflows/case-designer
- https://academy.creatio.com/guides/no-code-customization/bpm-tools/dynamic-case-setup/case-designer-workflows/set-up-cases-in-sections
- https://academy.creatio.com/docs/8.x/no-code-customization/bpm-tools/dynamic-case-setup/case-designer-workflows/set-up-case-stages
- https://academy.creatio.com/guides/no-code-customization/bpm-tools/dynamic-case-setup/case-designer-workflows/add-case-elements
- https://academy.creatio.com/guides/no-code-customization/bpm-tools/dynamic-case-setup/case-designer-workflows/execute-case
- https://academy.creatio.com/guides/no-code-customization/bpm-tools/dynamic-case-setup/case-designer-workflows/case-version-control
- https://academy.creatio.com/guides/no-code-customization/bpm-tools/dynamic-case-setup/case-designer-workflows/set-up-approval-case
- https://academy.creatio.com/docs/8.x/no-code-customization/bpm-tools/dynamic-case-setup/case-faq
- Element references: task-case-element · approval-case-element · send-email-case-element · edit-page-case-element · change-accsess-case-element · subprocess-case-element · validation-case-element (under https://academy.creatio.com/guides/no-code-customization/bpm-tools/dynamic-case-setup/case-designer-elements-reference/)
- https://academy.creatio.com/docs/8.x/no-code-customization/customization-tools/ui-and-business-logic-customization/UI-designer (Progress bar, Next steps)
