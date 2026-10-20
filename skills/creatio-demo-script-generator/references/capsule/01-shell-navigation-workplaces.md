# 01 — Shell, Navigation, Workplaces, Sections & App Management (Creatio 8.x Freedom UI)

> Capsule file. Source: Creatio Academy only, retrieved 2026-08-27. Exact UI names in **bold**.
> Items the docs do not confirm are marked **UNVERIFIED** — never use them in demo steps.

---

## 1. The shell — what a user sees after login
Source: https://academy.creatio.com/docs/8.x/creatio-apps/creatio-basics/freedomUI/creatio-freedom-shell

After login in a Freedom UI workplace the layout is:

- **Navigation panel** (left side, docs also call it "the section panel"): "lets you navigate through workplaces and sections." A dropdown switches the active **workplace**; when the workplace changes, "the sections available in the navigation panel also change." A search field in the panel helps "find sections within the active workplace quicker." A toggle button minimizes/maximizes the navigation panel. Creatio remembers "the panel position, workplace, section and your scroll position" between logins.
- **Quick-action buttons** on the panel: a button that "opens the quick record add menu" (menu content managed via the **Quick add records** lookup) and "the global process start button" that shows active processes.
- **Search field (global search)** — in Freedom UI a **Search** field "replaces the command line, which remains available in the Classic UI." Global search covers "all text and lookup fields" plus "Addresses, Communication options, and Banking details"; results are "grouped by section," "ranked by relevance, with records from the section you're currently in listed first," not case sensitive, with partial matching. (Source: https://academy.creatio.com/guides/creatio-apps/creatio-basics/freedomUI/search-records)
- **Working area** (center): "the list of section records," form pages, "analytics tools," or "special pages, for example, calendar."
- **Communication panel** (top right): "view and post user feed messages, manage emails, make and receive calls as well as chat with customers."
- **Notification panel / Notification center** (top right): shows "notifications about activities or invoices, comments to your records or mentions in a corporate social network, approvals, noteworthy events, system messages, and business process tasks."
- **User profile**: **UNVERIFIED** exact placement in the Freedom UI shell — do not script an exact click path.
- **System Designer button**: "the system designer button in the top right corner" is the entry to admin/customization tools (e.g., the Application Hub page).

**Classic UI only:** the **command line** ("What can I do for you?") — searches records and runs commands like "Create Contact", "Run process New employee registration". In Freedom UI it is replaced by the Search field. (https://academy.creatio.com/docs/user/platform_basics/user_interface/command_line/the_command_line)

---

## 2. Workplaces
Sources: https://academy.creatio.com/docs/8.x/no-code-customization/customization-tools/appearance-customization/set-up-workplaces · https://academy.creatio.com/guides/no-code-customization/8.1/customization-tools/ui-and-business-logic-customization/set-up-a-homepage

- **Definition** (glossary): "A set of sections displayed on the Creatio side panel for specific user groups (roles)." Sections not in the workplace are hidden from the main menu for those users.
- **Types**: **General** (employees; web or mobile usage), **Portal** (external users), **Self-service** (Self-service licenses), **Limited internal** (Limited internal licenses).
- **Setup path**: **System Designer** → **Set up view** → **Workplace setup**. Add via **New user workplace** → type → name → usage (web/mobile) → optional homepage → checkbox **"Use only in shell"** for Freedom UI display → save.
- **Sections in a workplace**: added via the **Sections** detail; the sequence in that detail is the display sequence in the navigation panel.
- **Home page**: homepages "aggregate the dashboard information for each workplace" — **the workplace Home page IS a dashboards-style page**, built in the **Freedom UI Designer**. It displays "in the side panel at the top" of the workplace section list. Only one homepage per workplace, but one homepage can serve several workplaces; assigned in Workplace setup via the **Home page** list. Managing homepages requires the **CanManageSolution** operation permission.
- **Role assignment**: on the workplace page, the **User groups** detail → add roles; all users of the selected roles get the workplace after their next login.

---

## 3. Apps vs sections
Sources: https://academy.creatio.com/docs/8.x/no-code-customization/customization-tools/app-management/apps-management · https://academy.creatio.com/docs/8.x/no-code-customization/8.0/nocode-platform/application-hub · https://academy.creatio.com/docs/8.x/no-code-customization/customization-tools/ui-and-business-logic-customization/set-up-the-app/set-up-sections

- **App**: "A working Creatio function block that solves business problems." Each app comprises one or more content packages (added automatically on app creation). Apps contain sections, pages, business processes, integrations.
- **Application Hub**: central place to view installed apps, create, install, update and delete apps; opened from the system designer button / **Application management → Application Hub**.
- **Section**: "A Creatio UI module that is generated based on an object and represents a business entity." "Sections are structural components of the app that are connected to an object, list page, and one or more form pages."
- **Creating an app (wizard flow)**: Application Hub → **New application** → template: **Records & business processes** (auto-generated list + form pages; since 8.3.2 also mobile list + form pages), **Custom** (empty package), or **AI generated** → icon, color, name, code → **Create**.
- **Adding a section to an app**: open the app in the Application Hub → **New Freedom UI section** → **Title** + **Select icon and color**; the section object, form page, and list page are created automatically. Existing sections are edited under **Navigation and sections**. The section is then added to a workplace via Workplace setup.

---

## 4. Studio / System Designer
Sources: https://academy.creatio.com/docs/8.x/creatio-apps/8.1/overview/platform-overview · https://academy.creatio.com/docs/glossary_page

- **System Designer**: "A set of tools designed for setup, customization, and administration of the Creatio application." Documented contents: **Set up view → Workplace setup**, **Application management → Application Hub**, **Processes → Process library**, system settings and lookups, user/access administration.
- **Studio Creatio**: "a no-code platform to automate workflows and build applications"; required for any Creatio instance; carries the Freedom UI Designer, BPMN 2.0 Process Designer, composable architecture, integration tools.
- **"Studio desktop"**: ✅ **VERIFIED on a live 8.1.4 stand** (mynaghimotors-demo, 2026-08-28) — after login the user lands on **Shell → #Desktop**, a dashboards "desktop" page; a **desktop switcher** (monitor icon, bottom right of the Home area) opens a carousel of named desktops incl. **Studio Desktop**, Sales consultant desktop, Marketing Desktop, External Desktop. A **Studio** workplace also exists in the workplace selector. So the toolkit convention "Creatio opens on the Studio desktop" holds on 8.1-era stands; a "desktop" is a switchable homepage edited in the Freedom UI Designer (DesktopPageDesigner, parent template CentralAreaDesktopTemplate). The term does not appear in current 8.x Academy docs, so on newer stands verify which desktop the login lands on before writing the navigation step. See `visual-library/shell-desktop-switcher.png` and `LEARNINGS.md` §1.

---

## 5. Users and roles
Sources: https://academy.creatio.com/docs/8.x/setup-and-administration/administration/user-and-access-management/user-management/organizational-roles · https://academy.creatio.com/docs/user/setup_and_administration/user_and_access_management/user_management/functional_roles_shortcut/functional_roles · https://academy.creatio.com/docs/user/setup_and_administration/user_and_access_management/access_management/record_permissions_shortcut/record_permissions

- **Organizational roles** — "user groups that represent company units, departments or subdivisions in the organizational structure" (e.g., "Boston Office Sales Department"). Permissions cascade: roles "automatically inherit access permissions from their parent organizational roles"; "management roles" let managers inherit subordinates' permissions.
- **Functional roles** — "reflect employee job titles, e.g., 'Sales associates'." A functional role links to one or more organizational roles, granting identical access for a job position across divisions. Access types via roles: object operation permissions, record permissions, column permissions, system operation permissions.
- **Record-level access**: record permissions configure read/edit/delete on individual records of an object for specific users or roles.

Demo convention (toolkit rule, not docs): one demo user holds many functional roles; approvals and activities are addressed to the role.

---

## 6. Creatio CRM products / composable apps for demos
Sources: https://academy.creatio.com/docs/8.x/creatio-apps/overview/sales-creatio-overview · https://academy.creatio.com/guides/creatio-apps/overview/marketing-creatio-overview · https://academy.creatio.com/docs/8.x/creatio-apps/overview/service-creatio-overview

| Product | What it is | Main out-of-the-box sections / composable apps |
|---|---|---|
| **Creatio Sales** | "an end-to-end platform to automate sales processes of any type using no-code" | Accounts, Contacts, Leads, Opportunities, Orders, Contracts, Documents, Products, Calendar, Tasks, Forecasting, Sales dashboards |
| **Creatio Marketing** | "an omnichannel platform that lets you capture and nurture leads" | Composable apps: Customer 360, Productivity, Knowledge Base, Email Marketing, Lead Generation, Digital Ads, Event Management; sections incl. Contacts, Web analytics, Ad campaigns, Calendar, Tasks, Dashboards; Campaign Designer, Email Designer |
| **Creatio Service** | "a multi-channel customer service platform" | Composable apps: Customer 360, Productivity (Calendar, Tasks), Knowledge Base, Case Management; sections incl. Cases, Services, Service Agreements; Agent Desktop for case queues |

Shared foundation: **Customer 360**, **Productivity**, **Knowledge Base** recur across products as composable apps.

---

## Source URLs (full list)

- https://academy.creatio.com/docs/8.x/creatio-apps/creatio-basics/freedomUI/creatio-freedom-shell
- https://academy.creatio.com/guides/creatio-apps/creatio-basics/freedomUI/search-records
- https://academy.creatio.com/docs/user/platform_basics/user_interface/command_line/the_command_line
- https://academy.creatio.com/docs/8.x/no-code-customization/customization-tools/appearance-customization/set-up-workplaces
- https://academy.creatio.com/guides/no-code-customization/8.1/customization-tools/ui-and-business-logic-customization/set-up-a-homepage
- https://academy.creatio.com/docs/8.x/no-code-customization/customization-tools/app-management/apps-management
- https://academy.creatio.com/docs/8.x/no-code-customization/8.0/nocode-platform/application-hub
- https://academy.creatio.com/docs/8.x/no-code-customization/customization-tools/ui-and-business-logic-customization/set-up-the-app/set-up-sections
- https://academy.creatio.com/docs/8.x/creatio-apps/8.1/overview/platform-overview
- https://academy.creatio.com/docs/glossary_page
- https://academy.creatio.com/docs/8.x/setup-and-administration/administration/user-and-access-management/user-management/organizational-roles
- https://academy.creatio.com/docs/user/setup_and_administration/user_and_access_management/user_management/functional_roles_shortcut/functional_roles
- https://academy.creatio.com/docs/user/setup_and_administration/user_and_access_management/access_management/record_permissions_shortcut/record_permissions
- https://academy.creatio.com/docs/8.x/creatio-apps/overview/sales-creatio-overview
- https://academy.creatio.com/guides/creatio-apps/overview/marketing-creatio-overview
- https://academy.creatio.com/docs/8.x/creatio-apps/overview/service-creatio-overview
