# Creatio palette capsule — the allowed product vocabulary

Copied from `creatio-demo-toolkit` 4.0.5.0 (`creatio-demo-runbook/shared/capsule`, version 2026-08-27,
built from Creatio Academy 8.x / Freedom UI). It is the list of what the product is called and can do.

| File | Domain | Used for |
|---|---|---|
| `01-shell-navigation-workplaces.md` | shell, navigation, workplaces, sections, apps, roles | step locations |
| `02-freedom-ui-pages-components.md` | page types, designer components, field types | step elements, column types |
| `03-dashboards-widgets.md` | dashboards and widget types | dashboards in the model |
| `04-dcm-case-designer.md` | DCM concepts, stage steps, limits | DCM in the model |
| `05-business-processes.md` | process designer palette | processes, code vs designer |
| `06-business-rules.md` | Freedom UI business rules | rules in the model |
| `07-approvals-creatio-ai.md` | approvals, Creatio.ai skills and modes | approval and AI steps |
| `09-creatio-mobile.md` | Creatio Mobile basics + UNVERIFIED list with fallbacks (added for this skill) | mobile steps |

Rules:
1. **Only names from the capsule.** An element, widget, step type or rule not named here does not go into a step.
   If the customer asks for something outside it, that is a decision (nearest honest no-code path) or a question.
2. **UNVERIFIED = do not use in steps.** **[DEV]** = never promised as no-code.
3. **Freedom UI vocabulary only.** Classic names (Pie, Pivot table, Web page, workflow bar, command line) are
   quarantined at the end of each file and never appear in output.
4. When the toolkit plugin updates its capsule, re-copy files 01–07 (09 is this skill's own).

## Leftovers from the source pipeline — ignore them

Files 01–07 were written for an older four-document pipeline. Mentions of `LEARNINGS.md`, `visual-library/*.png`,
"skill 1/3", "behavior file", "Demo Flow" and `INT-<n>` ids refer to files and stages that do not exist here.
Two rules override what the files say:

- **AI panel name**: write **Creatio.ai panel**. File 07 says to call it "AI Twin" on AI Studio stands — the
  script writer has no stand to check, so only use another name when the user gives it.
- **Detail**: file 02 quarantines "Detail" as a Classic word. That applies to **step text** (say Expanded list /
  list on a tab). In the **model**, `Detail` is a valid column type marking a parent → child relation.
