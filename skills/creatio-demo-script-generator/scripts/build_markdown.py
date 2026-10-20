"""spec.json -> the Demo Script and the Build Specification as Markdown (same content as the .docx).

Called by build_outputs.py (writes <Client>_Demo_Script.md and <Client>_Build_Spec.md next to the .docx);
can also run alone:
    python build_markdown.py <spec.json> [--out <dir>]

Step numbers are written as bold paragraphs ("**4.**"), not as a Markdown list, so gaps and stable numbering
survive every renderer. Narration bubbles are blockquotes; internal sections carry an INTERNAL banner.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_spec import anchor_date, display_column, norm_type, render_date_tokens  # noqa: E402
from quality_checks import tier_of, usage  # noqa: E402


def _cell(v):
    s = "" if v is None else str(v)
    return s.replace("|", "\\|").replace("\r", "").replace("\n", "<br>")


def _table(headers, rows):
    out = ["| " + " | ".join(_cell(h) for h in headers) + " |", "|" + "---|" * len(headers)]
    out += ["| " + " | ".join(_cell(c) for c in r) + " |" for r in rows]
    return "\n".join(out) + "\n"


def _steps(x):
    return ", ".join(x.get("steps", []) or [])


def _joined(v, sep="<br>"):
    return sep.join(v) if isinstance(v, list) else str(v or "")


def _src(s):
    if isinstance(s, dict):
        t = s.get("title") or s.get("url", "")
        link = f"[{t}]({s['url']})" if s.get("url", "").startswith("http") and s.get("title") else t
        return link + (f" ({s['date']})" if s.get("date") else "")
    return str(s)


def _expand(refs):
    out = set()
    for r in refs or []:
        m = re.match(r"^(UC\d+)\.(\d+)(?:-(\d+))?$", str(r))
        if m:
            for n in range(int(m.group(2)), int(m.group(3) or m.group(2)) + 1):
                out.add((m.group(1), n))
    return out


def _safe(s):
    return re.sub(r"[^\w-]+", "_", s.strip()).strip("_")


def build_markdown(spec, path, part="script"):
    meta, brief, model = spec["meta"], spec.get("brief", {}), spec.get("model", {})
    client, ucs, roles, data = meta["client"], spec.get("use_cases", []), spec.get("roles", []), spec.get("data", [])
    objects = {o["code"]: o for o in model.get("objects", [])}
    lookups = {l["code"]: l for l in model.get("lookups", [])}
    by_key = {r["_key"]: (b.get("object"), r) for b in data for r in b.get("records", []) if r.get("_key")}
    STATUS = {"new": "**new**", "extended": "extended", "existing": "*existing*"}
    REAL = {"real": "**real**", "simulated": "simulated", "talking point": "*talking point*"}

    def label(oc, r, depth=0):
        v = r.get(display_column(objects.get(oc, {})))
        if isinstance(v, str) and v.startswith("@") and depth < 3 and v[1:] in by_key:
            return label(*by_key[v[1:]], depth + 1)
        return str(v if v not in (None, "") else r.get("_key", ""))

    L = []
    a = L.append
    title = meta.get("title", "Demo Script") if part == "script" else "Build Specification"
    a(f"# {client} — {title}\n")
    a(f"*{meta.get('version', 'v1')} · {meta.get('date', '')}*\n")

    # header card
    inst = meta.get("instance") or {}
    by_login = {}
    for r in roles:
        if r.get("login"):
            by_login.setdefault(r["login"], []).append(r["name"])
    deal = meta.get("deal") or {}
    card = [
        ("Client", client + (f" · {meta['industry']}" if meta.get("industry") else "")),
        ("Demo instance", " · ".join(x for x in [inst.get("name"), inst.get("url"),
                                                  {"new": "new stand", "reuse": "reuse the existing stand",
                                                   "copy": f"copy of {inst.get('reference_demo', '')}"}.get(inst.get("mode"), "")] if x)),
        ("Previous demos", inst.get("previous_demos", "")),
        ("Demo date", meta.get("date", "") + (f" · {meta['duration_min']} min" if meta.get("duration_min") else "")),
        ("Deal size", (f"ARR {deal['arr_usd']:,.0f} USD" + (f" ({deal['arr_original']})" if deal.get("arr_original") else "")
                       + f" → {tier_of(deal['arr_usd'])['label']}" + (" — assumed, confirm" if deal.get("arr_assumed") else ""))
         if isinstance(deal.get("arr_usd"), (int, float)) else ""),
        ("Logins", "; ".join(f"{k} ({', '.join(v)})" for k, v in by_login.items()) + " — credentials in the team credential store"),
        ("Use cases", f"{len(ucs)} — " + " · ".join(f"{u['id']} {u['name']}" for u in ucs)),
        ("Language", meta.get("language", "") + (f" · region {meta['region']}" if meta.get("region") else "")
         + (f" · {meta['currency']}" if meta.get("currency") else "")),
        ("Walkthrough video", meta.get("walkthrough", "")),
    ]
    a(_table(["", ""], [[f"**{k}**", v] for k, v in card if v]))
    if brief.get("demo_goal"):
        a(f"> **DEMO GOAL** — {brief['demo_goal']}\n")

    if part == "script":
        a("## Brief customer summary\n")
        if brief.get("summary"):
            a(brief["summary"] + "\n")
        a(_table(["", ""], [[f"**{k}**", v] for k, v in [
            ("Goals / problems", "<br>".join(f"**{p['id']}** {p['text']}" for p in brief.get("pains", []) + brief.get("goals", []))),
            ("Customer website", meta.get("website", "")),
            ("Key customer products", " · ".join(meta.get("key_products", []))),
            ("Key roles", ", ".join(r["name"] for r in roles)),
            ("Key marketplace solutions", ", ".join(meta.get("marketplace", [])) or "none"),
            ("Languages", meta.get("language", ""))] if v]))

        disc = spec.get("discovery") or {}
        if disc.get("moments"):
            a("## Discovery insights\n")
            a(f"*From {disc.get('source', 'the discovery call')}" + (f" · {disc['date']}" if disc.get("date") else "")
              + (f" · participants: {', '.join(disc['participants'])}" if disc.get("participants") else "")
              + ". “Not covered” marks a moment no use case answers yet (see Proposed additions).*\n")
            rank = {"high": 0, "medium": 1, "low": 2}
            a(_table(["#", "When · who", "What they said", "What it means", "Covered by"],
                     [[m.get("id", ""), f"{m.get('minute', '')} · {m.get('speaker', '')}", f"“{m.get('quote', '')}”",
                       f"**{m.get('kind', '')}**" + (f" · {m['importance']}" if m.get("importance") else "") + f" — {m.get('insight', '')}",
                       ", ".join(m.get("covered_by", [])) or "*not covered*"]
                      for m in sorted(disc["moments"], key=lambda m: rank.get(m.get("importance"), 3))]))
        if spec.get("research_gaps"):
            a("> **RESEARCH GAPS** — " + " · ".join(g.strip().rstrip(".;") for g in spec["research_gaps"]) + ".\n")

        a("## Brief demo summary\n")
        heroes = []
        for b in data:
            o = objects.get(b["object"], {})
            heroes += [f"{label(b['object'], r)} ({o.get('caption') or b['object']})" for r in b.get("records", []) if r.get("_main")]
        a(_table(["", ""], [[f"**{k}**", v] for k, v in [
            ("What the demo covers", brief.get("focus", "")),
            ("Reference demo", inst.get("reference_demo", "")),
            ("Key sections", " · ".join(o["section"] for o in model.get("objects", []) if o.get("section"))),
            ("Hero records", " · ".join(heroes)),
            ("Story", "<br>".join(f"**{u['id']}** {u.get('flow_line', '')}" for u in ucs))] if v]))
        if brief.get("agenda"):
            names = {u["id"]: u["name"] for u in ucs}
            a("### Agenda coverage\n")
            a(_table(["#", "Agenda item", "Shown in", "Note"],
                     [[x["id"], x["text"], ", ".join(f"{u} {names.get(u, '')}" for u in x.get("covered_by", [])) or "—", x.get("note", "")]
                      for x in brief["agenda"]]))
        if brief.get("vocabulary"):
            a("### Your terms in Creatio\n")
            a(_table(["Your term", "In Creatio"], [[v["client"], v["creatio"]] for v in brief["vocabulary"]]))

        ind = spec.get("industry") or {}
        if ind.get("points"):
            a("## Industry context" + (f" — {ind['name']}" if ind.get("name") else "") + "\n")
            if ind.get("summary"):
                a(ind["summary"] + "\n")
            a(_table(["#", "What matters in this industry", "Why for this customer", "In the demo"],
                     [[x.get("id", ""), x.get("point", ""), x.get("why", ""), x.get("demo_implication", "")] for x in ind["points"]]))
            if ind.get("sources"):
                a("*Sources: " + "; ".join(_src(s) for s in ind["sources"]) + "*\n")

        if spec.get("ground_rules"):
            a("## Ground rules\n")
            a("\n".join(f"- {g}" for g in spec["ground_rules"]) + "\n")
        if roles:
            a("## Roles and logins\n")
            a(_table(["Role", "Login mode", "Login", "Workplace / sections", "Use cases"],
                     [[f"**{r['name']}**" + (f" — {r['title']}" if r.get("title") else ""), r.get("login_mode", ""), r.get("login", ""),
                       " · ".join(x for x in [r.get("workplace", ""), ", ".join(r.get("sections", [])), r.get("scope", "")] if x),
                       ", ".join(r.get("use_cases", []))] for r in roles]))

        a("## Build scope\n")
        a(f"What to configure, field by field: **{_safe(client)}_Build_Spec**. Proposed additions are not in this scope until accepted.\n")
        if isinstance(deal.get("arr_usd"), (int, float)):
            t, used = tier_of(deal["arr_usd"]), usage(spec)
            a(f"> **DEAL TIER — {t['label']}** · ARR {deal['arr_usd']:,.0f} USD. {t['intent']}\n")
            exc = {x.get("budget"): x.get("why", "") for x in deal.get("exceptions", [])}
            a(_table(["Budget", "Used", "Tier allows", "Exception"],
                     [[k.replace("_", " "), used[k], "no cap" if cap is None else cap, exc.get(k, "")] for k, cap in t["budget"].items()]))
        cells = {}

        def put(area, real, text):
            cells.setdefault(area, {"real": [], "simulated": [], "talking point": []})
            cells[area][real if real in ("real", "simulated", "talking point") else "real"].append(text)
        for o in model.get("objects", []):
            if o.get("status") in ("new", "extended"):
                put("Objects", "real", f"{o.get('caption') or o['code']} ({o['status']})")
        for x in model.get("ui", []):
            put("Reference-demo screens" if x.get("kind") in ("Reuse", "Hide") else "Pages and navigation", "real",
                (f"{x['kind'].lower()} " if x.get("kind") in ("Reuse", "Hide") else "") + x.get("name", ""))
        for d in model.get("dcm", []):
            for s in d.get("stages", []):
                put("DCM", "simulated" if s.get("scope") in ("prefilled", "simulated") else "real", s.get("name", ""))
        for kind, area in (("processes", "Processes"), ("rules", "Business rules"), ("ai", "AI"),
                           ("integrations", "Integrations"), ("notifications", "Notifications")):
            for x in model.get(kind, []):
                put(area, x.get("realization", "real"), x.get("name") or x.get("id", ""))
        for d in model.get("dashboards", []):
            put("Dashboards", "real", f"{d.get('name')} ({len(d.get('widgets', []))} widgets)")
        put("Data", "real", f"{sum(len(b.get('records', [])) for b in data)} records across {len(data)} objects")
        a(_table(["Area", "Built for real", "Simulated", "Talking point only"],
                 [[f"**{k}**", " · ".join(v["real"]), " · ".join(v["simulated"]), " · ".join(v["talking point"])] for k, v in cells.items()]))
        oos = [f"**{x['item']}** — {x.get('why', '')}" for x in spec.get("out_of_scope", [])]
        if oos:
            a("### Out of scope\n")
            a("\n".join(f"- {x}" for x in oos) + "\n")

        a("## Before you present\n")
        reset = next((p for p in model.get("processes", []) if "before demo" in p.get("name", "").lower()), None)
        if reset:
            a(f"Run the **{reset['name']}** process — it resets every record this demo touches to its opening state.\n")
        pre = spec.get("pre_demo", {})
        lines = [f"- Exists: {x}" for x in pre.get("must_exist", [])] + \
                [f"- Does **not** exist yet (created live): {x}" for x in pre.get("must_not_exist", [])] + \
                [f"- {x}" for x in pre.get("checks", [])]
        if lines:
            a("\n".join(lines) + "\n")

        a("## Demo use cases\n")
        for u in ucs:
            a(f"### Use case {u['id'].replace('UC', '')} — {u['name']}\n")
            tags = [x for x in [f"Persona: {u['persona']}" if u.get("persona") else "",
                                f"Entry point: {u['entry_point']}" if u.get("entry_point") else "",
                                "Agenda: " + ", ".join(u["agenda"]) if u.get("agenda") else "",
                                "Answers: " + ", ".join(u["pains"]) if u.get("pains") else "",
                                f"Priority: {u['priority']}" if u.get("priority") else ""] if x]
            if tags:
                a("*" + " · ".join(tags) + "*\n")
            a("**Purpose** — " + u.get("summary", "") + "\n")
            a(f"*{u.get('flow_line', '')}*\n")
            a("**Click path**\n")
            for it in u.get("items", []):
                if "bubble" in it:
                    a(f"> {it['bubble']}\n")
                elif "scene" in it:
                    a(f"*— Scene: {it['scene']} —*\n")
                elif "step" in it:
                    a(f"**{it['step']}.** {it['text']}\n")
            if u.get("value_message"):
                a(f"**Value message**\n\n> {u['value_message']}\n")
            own = {(u["id"], it["step"]) for it in u.get("items", []) if "step" in it}
            setup = []
            objs = [f"{o.get('caption') or o['code']} ({o['status']})" for o in model.get("objects", [])
                    if o.get("status") != "existing" and _expand(o.get("steps")) & own]
            cols = [f"{o.get('caption') or o['code']}.{c.get('caption') or c['code']}" for o in model.get("objects", [])
                    for c in o.get("columns", []) if c.get("status") == "new" and _expand(c.get("steps")) & own]
            if objs:
                setup.append(f"**Objects:** {', '.join(objs)}")
            if cols:
                setup.append(f"**New columns:** {', '.join(cols)}")
            for kind, lab in (("ui", "Pages and buttons"), ("dashboards", "Dashboards"), ("dcm", "DCM"), ("processes", "Processes"),
                              ("rules", "Business rules"), ("ai", "AI"), ("integrations", "Integrations"),
                              ("notifications", "Notifications"), ("slas", "Clocks")):
                names = [x.get("name") or x.get("id") for x in model.get(kind, []) if _expand(x.get("steps")) & own and x.get("kind") != "Hide"]
                if names:
                    setup.append(f"**{lab}:** {', '.join(names)}")
            if setup:
                a("**Required setup**\n\n" + "\n".join(f"- {s}" for s in setup) + "\n")
            text = " ".join(it.get("text", "") for it in u.get("items", []) if "step" in it)
            recs = [f"{label(b['object'], r)} ({objects.get(b['object'], {}).get('caption') or b['object']})"
                    for b in data for r in b.get("records", []) if r.get("_main") and label(b["object"], r) in text]
            if recs or u.get("data_note"):
                a("**Required data population**\n")
                if recs:
                    a("- **Hero records:** " + ", ".join(recs))
                if u.get("data_note"):
                    a("- " + u["data_note"])
                a("")

        props = spec.get("proposed_additions", [])
        if props:
            a("## Proposed additions\n")
            a("*Not in the agreed scope yet — nothing here is in the build scope, setup or data until accepted. Sources: "
              "discovery (D), industry (IND), competition (CMP), past demos (PD), the customer's own pains/goals/agenda/files (P/G/A/S).*\n")
            rank = {"high": 0, "medium": 1, "low": 2}
            a(_table(["#", "Proposal", "Why · sources", "What the audience would see", "Fits", "Size", "Status"],
                     [[x.get("id", ""), f"**{x.get('title', '')}** *({x.get('kind', '')}" + (f", {x['priority']}" if x.get("priority") else "") + ")*",
                       f"{x.get('why', '')} *({', '.join(x.get('sources', []))})*", x.get("demo_moment", ""), x.get("fits", ""),
                       x.get("effort", ""), x.get("status", "proposed")] for x in sorted(props, key=lambda x: rank.get(x.get("priority"), 3))]))

        comp = spec.get("competitive") or {}
        if comp.get("competitors") or comp.get("points"):
            a("## Competitive positioning — internal\n")
            a("> **INTERNAL** — do not share with the customer. Factual and sourced; competitor strengths are included so the presenter is never surprised.\n")
            if comp.get("summary"):
                a(comp["summary"] + "\n")
            if comp.get("competitors"):
                a(_table(["Competitor", "Why in this deal", "Would likely show", "Genuinely strong at", "Where Creatio wins here"],
                         [[f"**{c.get('name', '')}**" + (f"<br>*{_joined(c.get('products'), ', ')}*" if c.get("products") else ""),
                           c.get("why_in_deal", ""), _joined(c.get("would_show")), _joined(c.get("strengths")), _joined(c.get("gaps"))]
                          for c in comp["competitors"]]))
            if comp.get("points"):
                a("### Per use case\n")
                a(_table(["#", "Use case", "A competitor would show", "Creatio better because", "Demo highlight", "Trap to avoid"],
                         [[x.get("id", ""), x.get("uc", ""), x.get("they_show", ""), x.get("creatio_better", ""),
                           x.get("demo_highlight", ""), x.get("trap", "")] for x in comp["points"]]))
            srcs = list(dict.fromkeys(_src(s) for c in comp.get("competitors", []) for s in c.get("sources", [])))
            if srcs:
                a("*Sources: " + "; ".join(srcs) + "*\n")

        sims = spec.get("similar_demos", [])
        if sims:
            a("## Ideas from similar demos — internal\n")
            a("*Past Creatio demos for the same industry or use cases. Ideas only — no names, people or data from them appear in this demo.*\n")
            a(_table(["#", "Demo", "Industry · use cases", "Reuse", "Lessons"],
                     [[x.get("id", ""), f"**{x.get('customer', '')}**" + (f"<br>[link]({x['link']})" if x.get("link") else ""),
                       f"{x.get('industry', '')} · {_joined(x.get('use_cases'), ', ')}", _joined(x.get("reuse")), _joined(x.get("lessons"))]
                      for x in sims]))

        if spec.get("decisions"):
            a("## Decisions taken\n")
            a(_table(["Kind", "Decision", "Why", "Where"],
                     [[d.get("kind", "decision"), d.get("text", ""), d.get("why", ""), d.get("where", "")] for d in spec["decisions"]]))
        if spec.get("questions"):
            a("## Questions for you\n")
            a("*Each question already has a default applied — the script is written to it. Answer only where the default is wrong.*\n")
            a(_table(["#", "Where", "Question", "Default applied", "Who"],
                     [[q["id"], q.get("where", ""), q["text"], q["default"], q.get("who", "")] for q in spec["questions"]]))
        for i, ap in enumerate(spec.get("appendix", []), 1):
            a(f"## Appendix {i} — {ap.get('title', '')}\n")
            if ap.get("kind"):
                a(f"*{ap['kind']}*\n")
            a("\n\n".join(p.strip() for p in str(ap.get("text", "")).split("\n") if p.strip()) + "\n")

    else:  # ---------------- Build Specification
        a(f"Companion to **{_safe(client)}_Demo_Script** — the demo flow, roles, build scope and decisions are there; "
          "this document says what to configure. Step references (UC1.4) point at its use cases.\n")
        objs = model.get("objects", [])
        if model.get("ai"):
            a("## AI actions\n")
            a(_table(["Action", "Trigger", "Input → output", "Stored in · review", "Real?", "Steps"],
                     [[f"**{x.get('name', '')}**", x.get("trigger", ""), f"{x.get('inputs', '')} → {x.get('output', '')}",
                       f"{x.get('stored_in', '')} · {x.get('review', '')}", REAL.get(x.get("realization"), x.get("realization", "")), _steps(x)]
                      for x in model["ai"]]))
            for x in model["ai"]:
                if x.get("example_output"):
                    a(f"**{x['name']}** — audience sees: {x.get('audience_sees', '')}\n\n> *{x['example_output']}*\n")
        if objs:
            a("## Object model\n")
            a(_table(["Object", "Status", "Depth", "Purpose", "Steps"],
                     [[f"**{o.get('caption') or o['code']}** ({o['code']})", STATUS.get(o["status"], o["status"]), o.get("depth", ""),
                       o.get("purpose", "") + (f" *Why not OOTB: {o['why_not_ootb']}*" if o.get("why_not_ootb") else ""), _steps(o)] for o in objs]))
            for o in objs:
                if not o.get("columns"):
                    continue
                a(f"### {o.get('caption') or o['code']} — {o['code']}\n")
                rows = []
                for c in o["columns"]:
                    vals = ""
                    if norm_type(c.get("type")) in ("lookup", "detail") and c.get("ref"):
                        if c["ref"] in lookups:
                            vs = lookups[c["ref"]].get("values", [])
                            vals = f"{c['ref']}: " + " / ".join(vs[:12]) + (" / …" if len(vs) > 12 else "")
                        else:
                            vals = f"→ {objects.get(c['ref'], {}).get('caption') or c['ref']}"
                    if c.get("formula"):
                        vals = (vals + " · " if vals else "") + f"= {c['formula']}"
                    rows.append([f"**{c.get('caption') or c['code']}**" + (" *(required)*" if c.get("required") else ""), c["code"],
                                 c.get("type", ""), vals or c.get("note", ""), STATUS.get(c.get("status"), c.get("status", "")), _steps(c)])
                a(_table(["Column", "Code", "Type", "Values / points to / purpose", "Status", "Steps"], rows))
        if model.get("lookups"):
            a("## Lookups\n")
            a(_table(["Lookup", "Status", "Values (in order; added values in bold)"],
                     [[f"{l.get('caption') or l['code']} ({l['code']})", STATUS.get(l["status"], l["status"]),
                       " / ".join(f"**{v}**" if v in set(l.get("new_values") or []) else v for v in l.get("values", []))]
                      for l in model["lookups"]]))
        if model.get("ui"):
            a("## Pages, buttons and navigation\n")
            a(_table(["Element", "Kind", "Where", "Does", "Steps"],
                     [[f"**{x.get('name', '')}**", x.get("kind", ""), x.get("where", ""), x.get("does", ""), _steps(x)] for x in model["ui"]]))
        for d in model.get("dashboards", []):
            a(f"## Dashboard — {d.get('name', '')}\n")
            a(f"*{d.get('location', '')} · supports steps {_steps(d)}*\n")
            a(_table(["Widget", "Type", "Data source", "Shows", "Seed"],
                     [[f"**{w.get('name', '')}**", w.get("type", ""), w.get("source", ""), w.get("example", ""), w.get("seed", "")]
                      for w in d.get("widgets", [])]))
        for d in model.get("dcm", []):
            a(f"## Case management (DCM) — {d.get('name', d.get('object'))}\n")
            a(f"*{d.get('object')}" + (f" where {d['condition']}" if d.get("condition") else "")
              + f", stage column {d.get('stage_column')} · supports steps {_steps(d)} · stages with steps are configured by hand in the Case Designer.*\n")
            a(_table(["#", "Stage", "Stage elements", "Required to leave", "Scope"],
                     [[i, f"**{s.get('name')}**", "; ".join(s.get("elements", [])), "; ".join(s.get("exit_required", [])), s.get("scope", "built")]
                      for i, s in enumerate(d.get("stages", []), 1)]))
        if model.get("processes"):
            a("## Business processes\n")
            a(_table(["Process", "Trigger", "Does", "Audience sees", "Real? · build", "Steps"],
                     [[f"**{p.get('name', '')}**", p.get("trigger", ""), " → ".join(p.get("actions", []))
                       + (f" *(simulated: {p['simulation']})*" if p.get("simulation") else ""), p.get("audience_sees", ""),
                       f"{REAL.get(p.get('realization'), p.get('realization', ''))} · {'from code' if p.get('build') == 'code' else 'designer-only'}",
                       _steps(p)] for p in model["processes"]]))
        if model.get("rules"):
            a("## Business rules\n")
            a(_table(["Rule", "Where", "When", "Effect", "Real?", "Steps"],
                     [[f"**{r.get('name', '')}**", f"{r.get('page') or r.get('object', '')} ({r.get('level', '')})",
                       r.get("condition") or r.get("trigger", ""), r.get("effect", ""), REAL.get(r.get("realization"), r.get("realization", "")), _steps(r)]
                      for r in model["rules"]]))
        if model.get("integrations"):
            a("## Integrations\n")
            a(_table(["Integration", "Stands for", "How it is shown", "Populates", "Real?", "Steps"],
                     [[f"**{i.get('name', '')}**", i.get("system", ""), (i.get("pattern") or i.get("simulation") or "")
                       + (f" — timeline note *“{i['timeline_note']}”*" if i.get("timeline_note") else ""), i.get("populates", ""),
                       REAL.get(i.get("realization"), i.get("realization", "")), _steps(i)] for i in model["integrations"]]))
        if model.get("notifications"):
            a("## Notifications\n")
            a(_table(["ID", "Trigger → recipient", "Channel", "Copy", "Real?", "Steps"],
                     [[f"**{n.get('id', '')}** {n.get('name', '')}", f"{n.get('trigger', '')} → {n.get('recipient', '')}", n.get("channel", ""),
                       n.get("copy", ""), REAL.get(n.get("realization"), n.get("realization", "")), _steps(n)] for n in model["notifications"]]))
        if model.get("slas"):
            a("## SLAs and clocks\n")
            a(_table(["Clock", "Duration", "Starts", "Stops", "Shown in", "Steps"],
                     [[f"**{s.get('name', '')}**", s.get("duration", ""), s.get("start", ""), s.get("stop", ""), s.get("shown_in", ""), _steps(s)]
                      for s in model["slas"]]))
        if data:
            a("## Demo data\n")
            a(f"*{sum(len(b.get('records', [])) for b in data)} records, import-ready in **{_safe(client)}_Demo_Data.xlsx**; "
              f"dates relative to the demo day {meta.get('date', '')}.*\n")
            a(_table(["Object", "Records", "Hero records", "Why"],
                     [[f"**{objects.get(b['object'], {}).get('caption') or b['object']}**", len(b.get("records", [])),
                       ", ".join(label(b["object"], r) for r in b.get("records", []) if r.get("_main")), b.get("purpose", "")] for b in data]))

    a("---\n*Creatio Demo Build — Confidential*\n")
    Path(path).write_text("\n".join(L), encoding="utf8")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    out = None
    if "--out" in args:
        i = args.index("--out")
        out = Path(args[i + 1])
        del args[i:i + 2]
    spec_path = Path(args[0])
    out = out or spec_path.parent
    spec = json.loads(spec_path.read_text(encoding="utf8"))
    from build_outputs import apply_date_tokens
    spec = apply_date_tokens(spec, anchor_date(spec))
    base = _safe(spec["meta"]["client"])
    for part, name in (("script", f"{base}_Demo_Script.md"), ("spec", f"{base}_Build_Spec.md")):
        build_markdown(spec, out / name, part)
        print("->", out / name)


if __name__ == "__main__":
    main()
