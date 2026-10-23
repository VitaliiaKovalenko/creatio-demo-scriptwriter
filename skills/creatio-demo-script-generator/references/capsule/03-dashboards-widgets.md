# 03 — Dashboards & Analytics Widgets (Creatio 8.x Freedom UI)

> Capsule file. Source: Creatio Academy only, retrieved 2026-08-27. Anything not listed here is
> treated as non-existent in Freedom UI. **UNVERIFIED** = never use in demo steps.

---

## 1. Where dashboards live in Freedom UI

- **Widgets on any Freedom UI page.** Analytics are viewable "on any Freedom UI page that has Widget components added"; widgets are dragged from the Freedom UI Designer element library onto form pages, list pages, or homepages. Out of the box, Creatio displays multiple widgets on **homepages**.
- **`Dashboards` component (container).** A dedicated Freedom UI Designer component that hosts one or more dashboards on a page. Key properties: **Data source** (primary source for all dashboards in the component), **Apply filter by page data** (filter dashboard data by page data source/parameters or connected components such as **List** or **Attachment list**), **Apply pre-configured filter** (connect to **Folders** or **Quick filter** components), **Dashboards** (each added dashboard opens its own Freedom UI Designer canvas), **Visibility**, business rules. Default access: "All employees" role.
- **Dashboards view of sections.** Dashboards appear in the **Dashboards** view of Creatio sections (section analytics).
- **Two dashboard origins:** **configuration dashboards** (created at design time in Freedom UI Designer, ship with apps) and **environment dashboards** (created at runtime by end users via dashboard name → **Add new dashboard**; personal by default, shareable, can be copied and favorited; external/portal users can only view).

## 2. Freedom UI widget types (the allowed palette)

Docs: "The following widget types are available: spline, line, bar, doughnut, area, column, scatter, pipeline, sales pipeline, full pipeline, metric, gauge." (The first eight are the **Chart** types.)

### 2.1 Chart
- **Purpose:** display dynamics and percentages across data dimensions.
- **Chart types (exact, exhaustive):** **Spline, Line, Bar, Doughnut, Area, Column, Scatter, Pipeline**. (*Doughnut*, not "Pie" — "Pie" is Classic vocabulary.)
- **Key settings:** Object; aggregation **Function** (count, sum, average, maximum, minimum) + **Column**; chart type; X-/Y-axis labels (axis charts); **grouping column** — date columns get a date format (e.g., "Week", "Month & year"); **sorting** — "By grouping field" / "By selection result", asc/desc; filtering via **How to filter**; **multiple series**; **stacked** display (Column/Bar only); legend and value-label toggles.
- **Constraints:** designer preview shows partial data; mixing incompatible chart types across series falls back to the first type; *average* not available for all columns.
- **End-user behavior:** drill-down on a chart element to a sub-chart or list; list mode ("Display data" / "Show data by series") with column setup, sorting, **Export to Excel**.

### 2.2 Metric
- "Display a calculated numeric value or a date based on Creatio data."
- Settings: Object; Function (count, sum, average, minimum, maximum) + Column; filters; display format/size; decimals; accompanying text with custom position.

### 2.3 Gauge
- "Display a single numeric value relative to a custom scale" (KPI tracking).
- Settings: Object, Function, Column; scale order — "The more the better" / "The less the better"; scale min/average/max; section colors; decimals; filters.

### 2.4 Sales pipeline
- "Display the opportunity dynamics by stage."
- Settings: funnel color/style; opportunity filters. Auto-excludes *Closed lost*, *Closed rejected*, *Closed rerouted*. Requires Lead and Opportunity Management app. Not filterable by Quick filter.

### 2.5 Full pipeline
- Visualize the "complete sales life cycle by stage, from lead registration to the closed opportunity."
- Settings: funnel color/style; separate **lead** filters and **opportunity** filters. Same app requirement; not filterable by Quick filter.

### 2.6 List widget (8.3.1+)
- "Combines a fully functional list with a customizable colored frame."
- Settings: same data core as **List** (object + filters, column setup); styling: **Theme** — "full-fill", "without-fill" (default), "partial-fill", "glassmorphism"; layout color (default "dark-blue"); title; toolbar (default: **Export to Excel**).

### 2.7 iFrame (8.3.3+)
- "Embed third-party web content directly into Freedom UI pages without custom development." Freedom UI counterpart of Classic "Web page".

### 2.8 Dashboards (container component)
- Not a data widget itself — hosts dashboards on a page (see section 1).

**Not part of the Freedom UI palette (do not generate):**
- **Pivot table** — Classic-only per current docs. **UNVERIFIED for Freedom UI.**
- **Web page** — Classic-only name; use **iFrame**.
- **Widget** (custom developer widget tile) — Classic-only.
- **"Dynamic text" widget** — not found. **UNVERIFIED — do not use.**
- **"Pipeline efficiency"** — not in Freedom UI widget docs. **UNVERIFIED.**

## 3. Aggregation functions & filtering

- **Aggregation functions (exact list):** **count, sum, average, minimum, maximum**. *Average* is column-type dependent; sum/avg/min/max need a numeric (Metric: or date-capable) **Column**.
- **Widget-level filtering:** the **How to filter** field group, standard advanced-filter condition UI (e.g., "Created on = Current month"); Full pipeline takes separate lead and opportunity filters.
- **Page-level filtering (Dashboards component):** **Apply filter by page data** and **Apply pre-configured filter** (via **Folders** / **Quick filter**). Out of the box, widgets on record pages are connected to the page so they can be filtered.

## 4. Classic UI dashboards — vocabulary quarantine

Classic dashboard tile types: **Chart, Metric, List, Pivot table, Widget, Gauge, Web page, Sales pipeline, Full pipeline**; Classic chart types include **Pie** (Freedom = Doughnut).
**Classic-only — never use for Freedom UI:** *Pivot table*, *Web page*, *Widget* (custom tile), *Pie*.
**Freedom-UI-only — never use for Classic:** *List widget*, *iFrame*, *Dashboards* component, environment vs configuration dashboards.


## Clicking a figure to open its records (script guidance)

Whether clicking a Metric or a Chart opens the records behind the figure depends on the widget and the version.
*(Unverified on 8.3 — check on the stand.)* In the script:
- keep the source's step ("click the figure, confirm the list matches") when the source asks for it, and mark the
  drill-down as **to verify** in `questions` with the fallback as the default;
- **fallback**: next to each metric, a List widget, or a folder in the section, with the same filter, so the
  presenter opens the matching records in one move. Name it after the metric.
Record the choice in `decisions`; never drop the check from the flow.

## Sources

- https://academy.creatio.com/docs/8.x/no-code-customization/customization-tools/ui-and-business-logic-customization/analytics/set-up-dashboards
- https://academy.creatio.com/docs/8.x/no-code-customization/customization-tools/ui-and-business-logic-customization/analytics/dashboards/dashboards-basics
- https://academy.creatio.com/guides/no-code-customization/customization-tools/ui-and-business-logic-customization/analytics/dashboards/set-up-dashboards-in-freedom-ui-designer
- https://academy.creatio.com/docs/8.x/no-code-customization/customization-tools/ui-and-business-logic-customization/UI-designer
- https://academy.creatio.com/docs/8.x/creatio-apps/creatio-basics/business-data/analytics/view-and-manage-dashboards
- https://academy.creatio.com/docs/8.x/creatio-apps/creatio-basics/view-analytics
- https://academy.creatio.com/documents?id=15098 (List component and list widget, dev)
- https://academy.creatio.com/docs/user/customization_tools/analytics/setup/set_up_dashboards (Classic)
