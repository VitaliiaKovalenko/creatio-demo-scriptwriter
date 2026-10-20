# 02 — Freedom UI Pages & Designer Component Palette (Creatio 8.x)

> Capsule file. Source: Creatio Academy only, retrieved 2026-08-27. This is THE allowed UI palette:
> a component not named here does not exist for demo-scenario purposes. **UNVERIFIED** = never use in steps.
> Classic-UI-only names are quarantined at the end.

---

## 1. Page types in Freedom UI apps

A **section** is "a structural component of the app that is connected to an object, a list page, and one or more form pages."

| Page type (exact doc name) | Purpose | Binding |
|---|---|---|
| **List page** | Displays the section's records as a list; the default list page holds the **List** component plus search/filters/folders. | Bound to the section's object via the **List** component / app data model. |
| **Form page** | "Displays record data in its entirety." Default form page includes a Toggle panel (with Feed and Attachments), a Flex container with buttons, Tabs, and areas. A section can have **one or more form pages**. | Set as the object's **Default page** on the data model's **Pages** tab. |
| **Mini page** | "Functionally identical to full Freedom UI pages but have smaller canvas size and are displayed as pop-up windows in the list page." Canvas cannot be resized. | Selected in the **Page for adding records** field on the data model's **Pages** tab. |
| **Typified pages** | "Lets you use different form pages for a single section based on a lookup value." Configured via **Use multiple pages based on a specific field value** + **Field that determines the page layout**, then per lookup value: **Default page** and **Page for adding records**. | Bound per lookup value of the chosen field. |
| **Homepage** | Workplace-level dashboard page: "aggregates the dashboard information for each workplace"; shown at the top of the workplace section list. One homepage per workplace (one homepage can serve several). Built with dashboard widgets. | Assigned in System Designer → Workplace setup. |

- New pages are created in the **Application Hub** via **New page**; pages can also be created inline when configuring a **Button** ("Open new record" / "Open existing record") or a **List** component.
- "Record page" is not a separate palette-level page type — treat **form page** as the record page.
- Freedom UI vs Classic UI page routing per object: **UI Management** section → **Form page preferences** tab ("Freedom UI sections always use Freedom form pages").

## 2. Freedom UI Designer structure

Designer parts (exact doc terms): **Element library** / **Structure** view switcher, **canvas** (working area), **setup area** (element properties), action panel (save, cancel, **business rules**, source code). The element library groups elements into: **Data** (Fields, Inputs), **Widgets**, **Components**, **Layout elements**.

### 2a. Data — Fields and Inputs
- **Fields** — "display data and enable users to enter data"; setting up a field adds/modifies attributes of the data model (i.e., object columns).
- **Inputs** — same UI controls, but the data model is NOT modified (page-only values). Inputs include every field type plus **Slider**.

### 2b. Widgets (full detail in file 03)
**Chart** (types: spline, line, bar, doughnut, area, column, scatter, pipeline) · **Metric** · **Gauge** · **Sales pipeline** · **Full pipeline**.

### 2c. Components

| Component (exact name) | Purpose | Key properties / constraints |
|---|---|---|
| **Button** | Runs actions: open new/existing record, run business process, save/cancel, refresh, delete, upload file, add/remove tags, import/export, set access rights, send invite, print report, merge, follow feed | Title, Action, style/color, icon, visibility. Action list is fixed — do not invent actions |
| **Label** | Text/headings; can show current user contact data | Text, style, color, visibility |
| **List** | Displays records of an object | Object, columns, filters, multiselect; can drive filtering of connected components |
| **List widget** | "Fully functional list with customizable colored frame" | Frame color, glass effect, Excel export. 8.3.1+ (export 8.3.3+) |
| **Expanded list** | Prebuilt expansion panel containing **List**, **Search**, and **Button** | Object, columns; auto-linked to the object. (The Freedom UI counterpart of a Classic "detail") |
| **Folders** | Folder tree segmenting records by filters | Can reuse Classic UI folders |
| **Folder management menu** | Opens the folder tree / favorite folders | Pairs with Folders |
| **Search** | Search records across visible columns | Connected list/attachment list/approvals list |
| **Quick filter** | Filter a list, calendar, or chart by condition, date/time range, or lookup value | Cannot filter Sales/Full pipeline widgets |
| **Tags** | Add and manage record tags | Tag permissions, colors |
| **Summaries** | Show list summaries (record count, max value, etc.) | Function, column, connected list |
| **Feed** | Post/read comments, rich text, "@" mentions | Feed type: "Record" or "User" |
| **Attachments** | Upload/download files for current or related records | Data source, layout |
| **Timeline** | "View history of communication regarding a data source as well as records linked to it in chronological order" | Filters (type, date, owner), custom quick filters, message composer |
| **Message composer** | Send emails and post feed messages (rich text, attachments, templates, drafts, forwarding) | Channels, templates |
| **Next steps** | "View and manage activities and tasks for the current record as tiles" | Case-generated or manual activities. Replaces Action dashboard |
| **Progress bar** | Track and change dynamic case stages (the DCM stage bar) | Connected to page data source automatically; **Set up cases** opens the Case Designer |
| **Approvals** | Approve/deny actions on the record | Behavior pre-configured |
| **Approvals list** | "View the entire approval process as a list" | — |
| **Calendar** | View/manage records with start/end dates as tiles | Day/week/month/multi-month modes |
| **Timer** | Count down or up to a specific date/time | Shown in user timezone |
| **Local time** | Show current time in a specified timezone | — |
| **Playbook** | Show knowledge-base articles as hints per dynamic case stage | Requires Knowledge base app |
| **Communication options** | Manage record communication options (email, phone, web link) | Requires Customer 360 |
| **Account compact profile** | Account logo, name, local time, country | Requires Customer 360 |
| **Contact compact profile** | Contact photo, name, birth date, age, local time, country | Requires Customer 360 |
| **Multiselect lookup** | "Select multiple items from a lookup and display them as a chip list" | 8.3.1+ |
| **Next best offer** | ML-driven product recommendations for an account or contact | Needs ML model. 8.3.1+ |
| **Gallery** | Display visual data with captions and descriptions | Data source, image/caption fields |
| **iFrame** | "Embed third-party web content directly into Freedom UI pages without custom development" | URL. 8.3.3+. (NOT "Web page" — that is Classic) |
| **Action dashboard** | Edit dynamic cases (workflow bar + action panel) | **Legacy**: 8.0.8 and earlier only; use Progress bar + Next steps |
| **Filters** (advanced/static filter components) | Static/advanced filtering of lists | Documented under element setup examples |

### 2d. Layout elements

| Element | Purpose | Key properties |
|---|---|---|
| **Area** / **Columns** (grid containers) | "Group Freedom UI elements into a rigid layout that can include columns" | Up to 12 columns, background color, column/row spacing, border radius, visibility |
| **Flex container** (**Flex row** / **Flex column**) | Group elements without fixed layout | Direction, spacing, styling, visibility |
| **Tabs** | Group content by multiple criteria | Tab set (reorderable 8.3.1+), per-tab layout, nested tabs |
| **Toggle panel** | Tab-like area controlled by buttons placeable anywhere | Default tab, dynamic visibility (8.3.1+) |
| **Expansion panel** | Group elements by a single criterion (collapsible) | Internal layout, background, title |

## 3. Field / input types

Exact field types: **Text**, **Number**, **Checkbox**, **Dropdown**, **Date/Time**, **Rich text**, **Phone**, **Email**, **Web link**, **Color**, **Autonumber**, **Image**, **Encrypted string**. Input-only: **Slider**.

✅ Verified 8.1.4 (form page designer, "Add new field" palette): Text, Number, Checkbox, Date/Time, Rich text, Phone, Email, Web link, Dropdown, Color, Autonumber, Image. (Encrypted string was absent on that older stand; the current-version list above stays canonical — demos always target the current version.) Existing object columns are listed separately as **Data model attributes**. The left panel layout differs by page type: a desktop/homepage shows **Add data source / PAGE PARAMETERS / WIDGETS / COMPONENTS**; a form page shows the object's field palette + Data model attributes (LEARNINGS.md §3–4).

Common field properties: **Title**, **Code** ("Usr" prefix by default), **Required**, **Read-only**, **Visibility** (with business-rule conditions), **Title position**, **Placeholder**, **Tooltip**.

Lookups: the lookup-backed field is called **Dropdown**. Its **Lookup view** parameter offers:
- **Dropdown list** — compact selector for smaller datasets;
- **Selection window** — a full, customizable Freedom UI page, "helpful if the user needs to select from a large number of lookup values, for example, products."
Extra options: **Enable adding new values**, **Enable opening the record list**. Multi-value lookups = the **Multiselect lookup** component.

## 4. Page templates

- No-code docs: **New page → select a template**; the only explicitly named no-code template is the **mini page template**. Default form page contents come "from the template" (Toggle panel with Feed + Attachments, button Flex container, Tabs, areas). **UNVERIFIED**: other no-code template names — do not invent them.
- App-level templates (on app creation): **Records & business processes**, **Custom**, **AI generated**.

## Classic-UI-only quarantine (do NOT use in Freedom UI scenarios)

- **Detail**, **Field group**, **Web page** widget, Section Wizard "Page designer" — Classic concepts. Freedom UI equivalents: **Expanded list / List**, grid containers, **iFrame**.
- **Action dashboard** in Freedom UI only through 8.0.8; newer = **Progress bar** + **Next steps**.
- "Web page" as a Freedom UI palette component: **UNVERIFIED / not found** — the Freedom UI component is **iFrame**.

## Source URLs

- https://academy.creatio.com/docs/8.x/no-code-customization/customization-tools/ui-and-business-logic-customization/UI-designer — Designer overview + full element library
- https://academy.creatio.com/guides/no-code-customization/category/pages-setup
- https://academy.creatio.com/docs/8.x/no-code-customization/customization-tools/ui-and-business-logic-customization/set-up-the-app/set-up-form-pages
- https://academy.creatio.com/guides/no-code-customization/customization-tools/ui-and-business-logic-customization/set-up-the-app/set-up-sections
- https://academy.creatio.com/guides/no-code-customization/customization-tools/ui-and-business-logic-customization/set-up-the-app/set-up-mini-pages
- https://academy.creatio.com/guides/no-code-customization/customization-tools/ui-and-business-logic-customization/set-up-the-app/set-up-typified-pages
- https://academy.creatio.com/guides/no-code-customization/customization-tools/ui-and-business-logic-customization/set-up-the-app/set-up-a-homepage
- https://academy.creatio.com/docs/8.x/no-code-customization/customization-tools/ui-and-business-logic-customization/set-up-the-app/create-a-custom-freedom-ui-record-page
- https://academy.creatio.com/docs/8.x/no-code-customization/customization-tools/appearance-customization/manage-the-form-pages-overview
- https://academy.creatio.com/guides/no-code-customization/category/fields-and-inputs
- https://academy.creatio.com/docs/8.x/no-code-customization/customization-tools/ui-and-business-logic-customization/element-setup-examples/fields-and-inputs/set-up-a-dropdown-field
- https://academy.creatio.com/guides/no-code-customization/category/components
- https://academy.creatio.com/guides/no-code-customization/category/layout-elements
- https://academy.creatio.com/guides/no-code-customization/customization-tools/ui-and-business-logic-customization/element-setup-examples/layout-elements/set-up-a-grid-container-layout-element
- https://academy.creatio.com/guides/no-code-customization/customization-tools/ui-and-business-logic-customization/analytics/set-up-dashboards
