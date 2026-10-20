# 09 — Creatio Mobile (vocabulary for mobile steps)

> Added 2026-10-15 for the script generator, because files 01–08 carry no mobile coverage. **Not** pulled
> from Creatio Academy like the other files: it states only the well-established basics, and marks the rest
> **UNVERIFIED**. Every UNVERIFIED item used in a step becomes a `decisions` entry plus an SE question with a
> fallback as the default. Verify on the stand before the build; update this file when you do.

## Safe to write in steps

- **Creatio Mobile** — the mobile app (iOS, Android), signed in to the same instance with the same user. A
  step that moves to the phone says so: *Creatio Mobile → …*. One demo user: the mobile step runs under the
  same login (or the step names a second login explicitly, and that is a question for the SE).
- **Mobile list page** and **mobile form page** of a section — the section must be part of the mobile app's
  workplace. Freedom UI mobile pages are configured separately from desktop pages
  (`creatio-freedom-pages` covers the build); in the model they are `model.ui` rows of kind
  `Mobile list page` / `Mobile form page`.
- Tabs and lists of related records (details) on the mobile form page.
- **Activities / calendar** on mobile — visits and tasks where the user is owner or participant.
- **Attachments** — adding a file, including a **photo taken with the phone camera**, to the record's
  attachments.
- **Tap to call / email** from a contact or account phone and email fields.
- **Offline work and synchronization** — data entered offline syncs when the connection returns (show it only
  if the customer asked; it is slow to demo).
- Business rules and processes run on the server: a mobile save triggers the same processes as the web.

## UNVERIFIED — decision + SE question, with the fallback as default

| Feature | Fallback to write as default |
|---|---|
| Camera capture straight into an **Image** column (not attachments) | photo into Attachments |
| **Geolocation check-in** / distance check on a visit | a **Check in** button setting an *Arrived at* time (process) |
| Barcode / QR scanning into a field | type or pick the product from a lookup |
| Field Sales product features (visit planning, route, store audit templates) | model them with Activity (Type "Visit") + custom check objects |
| Push notification shown on screen | the record appears in the mobile list; notification shown on web |
| Mobile-specific dashboards / home page widgets | show the analytics on the web home page |
| Signature capture | photo of a signed paper into Attachments |

## Never

- Classic "Mobile application wizard" vocabulary in steps.
- Promising an offline AI answer, or Creatio.ai on mobile, without the SE confirming it on the stand.

## Offline — what runs where

- Data entered offline (fields, new records, photos into Attachments) is stored on the phone and **synchronised
  when the connection returns**.
- **Business processes run on the server**: a button that starts a process, or a record change that triggers one,
  takes effect only after sync. Show the result after the phone is back online — never claim a process ran offline.
- **Page business rules offline** (required / read-only / visible) — UNVERIFIED; treat as online-only and ask the SE.
- So the honest offline moment is: capture data in flight mode → reconnect → sync → the server-side result
  (status, total, task) appears.
