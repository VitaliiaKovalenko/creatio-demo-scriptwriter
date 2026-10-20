# 06 — Business Rules (Creatio 8.x Freedom UI)

> Capsule file. Source: Creatio Academy only, retrieved 2026-08-27. **UNVERIFIED** = never use in specs.

Primary source: https://academy.creatio.com/docs/8.x/no-code-customization/customization-tools/ui-and-business-logic-customization/freedom-ui-business-rules

## 1. Where configured & scope

- Business rules are set up from the **Freedom UI Designer**: open the app in the **Application Hub**, open the page, click the **business rules** button on the designer's **action panel** (alongside save / cancel / source code / page settings). (A dedicated "Business rules" tab exists only in the Classic UI Section Wizard.)
- Two scopes:
  - **Page business rules** — apply only to elements of that specific page.
  - **Object business rules** — apply to **every Freedom UI page that uses that object, including editable lists**.
- Priority: "If multiple rules affect the same page element, only the first rule is activated."

## 2. Rule action/effect types (THEN block) — exact documented names

| Action | Notes |
|---|---|
| **Show elements** | make component visible on condition |
| **Hide elements** | hide component on condition |
| **Make elements required** | conditional required field |
| **Make elements read-only** | disable editing |
| **Make elements editable** | re-enable editing of read-only fields |
| **Apply static filter** | restrict lookup values to a predefined set |
| **Apply filter** | filter lookup values by another field's value (dependent lookups; Creatio auto-clears the dependent field when the driving field changes) |
| **Set values** | autofill a field with a **Constant**, a **Formula** (numeric calculation), or **Value from another field** |

Limitation: **Set values** is available **only in object business rules**, not page business rules.

## 3. Conditions (IF block)

- Conditions compare an element/attribute against: **constants/lookup values**, **value from another field**, **boolean states**, and **system values** such as **Current user role** (documented example uses **contains** against a role).
- Documented operators include **"="** (equals), **"contains"**, **"Is filled in"**.
- Multiple conditions via **Add condition**. **UNVERIFIED:** mixed AND/OR grouping in Freedom UI — examples show sequential (AND-style) conditions only. Do not spec OR-groups until verified on the stand.

## 4. Spec template for the behavior file (skill 3 output)

Each business rule row in the behavior document should carry exactly:

```
BR-<n>: <name>
  Scope: page <page name> | object <object name>
  IF: <attribute> <operator> <value | other field | system value> [AND ...]
  THEN: <one of the 8 exact action names> → <target element(s)>
  Supports steps: <Demo Flow step IDs>
```

## 5. Classic UI contrast (vocabulary quarantine)

Classic UI (Section Wizard → **Business rules** tab) action names: "Show field on the page", "Make field required", "Make field editable", "Add field values filter", "Set field value", with AND/OR condition operators. Classic rules are page-bound; Freedom UI adds object scope. Never mix the naming sets.
Source: https://academy.creatio.com/docs/user/customization_tools/ui_and_business_logic_customization/business_logic/setup/set_up_a_new_business_rule

## Sources

- https://academy.creatio.com/docs/8.x/no-code-customization/customization-tools/ui-and-business-logic-customization/freedom-ui-business-rules
- https://academy.creatio.com/docs/8.x/no-code-customization/customization-tools/ui-and-business-logic-customization/UI-designer
- https://academy.creatio.com/docs/user/customization_tools/ui_and_business_logic_customization/business_logic/setup/set_up_a_new_business_rule
