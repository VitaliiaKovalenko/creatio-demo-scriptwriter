"""spec -> an ordered list of document blocks. One outline, two renderers (Word via the Creatio template in
docx_render.py, Markdown in build_markdown.py), so the formats never drift apart.

Block kinds:
    ("title", text)                     ("meta", text)              ("h1", text)       ("h2", text)
    ("p", text)       ("p_muted", text) ("bullet", text)            ("step", n, text)  ("scene", text)
    ("callout", text, kind, label)      kind: goal | bubble | value | internal | note | gap | example
    ("kv", [[key, value], …])           a two-column key/value table without a header row
    ("table", headers, rows, widths)    widths = relative weights or None
    ("pagebreak",)
Inline markup inside text: **bold**, *italic*, `code`.

Demo Script: header · 1 Brief customer summary · 2 Brief demo summary · 3 Industry context · 4 Roles and logins ·
5 Demo use cases · 6 Competitive positioning (internal) · Appendix (proposed additions, discovery insights, similar
demos, agenda coverage, open questions, content assets).
Build Specification: header · ground rules · build scope · before you present · configuration · demo data · decisions.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # siblings import under python -I too

from quality_checks import tier_of  # noqa: E402
from validate_spec import display_column, norm_type  # noqa: E402

LANGUAGES = {"en": "English", "es": "Spanish", "pt": "Portuguese", "fr": "French", "de": "German", "it": "Italian",
             "nl": "Dutch", "pl": "Polish", "uk": "Ukrainian", "ar": "Arabic", "tr": "Turkish", "ja": "Japanese",
             "zh": "Chinese"}
REGIONS = {"CL": "Chile", "MX": "Mexico", "AR": "Argentina", "CO": "Colombia", "PE": "Peru", "ES": "Spain", "BR": "Brazil",
           "PT": "Portugal", "US": "US", "GB": "UK", "CA": "Canada", "DE": "Germany", "AT": "Austria", "CH": "Switzerland",
           "SA": "Saudi Arabia", "AE": "UAE"}


def language_label(value):
    """meta.language "en" / "es-CL" -> "English" / "Spanish (Chile)"; anything that is not a code is printed as is."""
    m = re.fullmatch(r"([a-z]{2})(?:[-_]([A-Z]{2}))?", str(value).strip())
    if not m or m.group(1) not in LANGUAGES:
        return value
    return LANGUAGES[m.group(1)] + (f" ({REGIONS.get(m.group(2), m.group(2))})" if m.group(2) else "")

STATUS = {"new": "**new**", "extended": "extended", "existing": "*existing*"}
REAL = {"real": "**real**", "simulated": "simulated", "talking point": "*talking point*"}


def safe_name(s):
    return re.sub(r"[^\w-]+", "_", s.strip()).strip("_")


def _steps(x):
    return ", ".join(x.get("steps", []) or [])


def _joined(v, sep="\n"):
    return sep.join(v) if isinstance(v, list) else str(v or "")


def _src(s):
    if isinstance(s, dict):
        return f"{s.get('title') or s.get('url', '')}" + (f" ({s['date']})" if s.get("date") else "")
    return str(s)


def _short_link(url):
    u = str(url).replace("%20", " ")
    for cut in ("/Shared Documents/", "/Documents/"):
        if cut in u:
            return "SharePoint: …/" + "/".join(u.split(cut, 1)[1].split("/")[-2:])
    return u if len(u) < 70 else u[:67] + "…"


def _expand(refs):
    out = set()
    for r in refs or []:
        m = re.match(r"^(UC\d+)\.(\d+)(?:-(\d+))?$", str(r))
        if m:
            for n in range(int(m.group(2)), int(m.group(3) or m.group(2)) + 1):
                out.add((m.group(1), n))
    return out


def blocks(spec, part="script"):
    meta, brief, model = spec["meta"], spec.get("brief", {}), spec.get("model", {})
    client, ucs, roles, data = meta["client"], spec.get("use_cases", []), spec.get("roles", []), spec.get("data", [])
    objects = {o["code"]: o for o in model.get("objects", [])}
    lookups = {l["code"]: l for l in model.get("lookups", [])}
    by_key = {r["_key"]: (b.get("object"), r) for b in data for r in b.get("records", []) if r.get("_key")}

    def label(oc, r, depth=0):
        v = r.get(display_column(objects.get(oc, {})))
        if isinstance(v, str) and v.startswith("@") and depth < 3 and v[1:] in by_key:
            return label(*by_key[v[1:]], depth + 1)
        return str(v if v not in (None, "") else r.get("_key", ""))

    B = []
    add = B.append

    # ---------------- header (both documents)
    title = meta.get("title", "Demo Script") if part == "script" else "Build Specification"
    add(("title", f"{client} — {title}"))
    add(("meta", f"{meta.get('version', 'v1')} · {meta.get('date', '')}"))
    inst = meta.get("instance") or {}
    deal = meta.get("deal") or {}
    tier = tier_of(deal["arr_usd"]) if isinstance(deal.get("arr_usd"), (int, float)) else None
    card = [
        ("Client", client + (f" · {meta['industry']}" if meta.get("industry") else "")),
        ("Demo instance", " · ".join(x for x in [inst.get("name"), inst.get("url"),
                                                  {"new": "new stand", "reuse": "reuse the existing stand",
                                                   "copy": f"copy of {inst.get('reference_demo', '')}"}.get(inst.get("mode"), "")] if x)),
        ("Demo date", meta.get("date", "") + (f" · {meta['duration_min']} min" if meta.get("duration_min") else "")),
        ("Deal size", (f"{tier['label']} · ARR {deal['arr_usd']:,.0f} USD"
                       + (f" · stated as {deal['arr_original'].strip(' ()')}" if deal.get("arr_original") else "")
                       + (" · assumed, confirm" if deal.get("arr_assumed") else "")) if tier else ""),
        ("Use cases", " · ".join(f"{u['id']} {u['name']}" for u in ucs)),
        ("Walkthrough video", meta.get("walkthrough", "")),
    ]
    add(("kv", [[k, v] for k, v in card if v]))
    if brief.get("demo_goal"):
        add(("callout", brief["demo_goal"], "goal", "DEMO GOAL"))

    if part == "script":
        _script(spec, B, add, meta, brief, model, client, ucs, roles, data, objects, label, tier)
    else:
        _build_spec(spec, B, add, meta, model, client, data, objects, lookups, label)
    return B


# ======================================================================================================== SCRIPT
def _script(spec, B, add, meta, brief, model, client, ucs, roles, data, objects, label, tier):
    inst = meta.get("instance") or {}

    add(("h1", "1. Brief customer summary"))
    if brief.get("summary"):
        add(("p", brief["summary"]))
    add(("kv", [[k, v] for k, v in [
        ("Goals / problems", "\n".join(f"**{p['id']}** {p['text']}" for p in brief.get("pains", []) + brief.get("goals", []))),
        ("Customer website", meta.get("website", "")),
        ("Key customer products", " · ".join(meta.get("key_products", []))),
        ("Key roles", ", ".join(r["name"] for r in roles)),
        ("Key marketplace solutions", ", ".join(meta.get("marketplace", [])) or "none"),
        ("Languages", language_label(meta.get("language", "")))] if v]))

    add(("h1", "2. Brief demo summary"))
    heroes = []
    for b in data:
        o = objects.get(b["object"], {})
        heroes += [f"{label(b['object'], r)} ({o.get('caption') or b['object']})" for r in b.get("records", []) if r.get("_main")]
    add(("kv", [[k, v] for k, v in [
        ("What the demo covers", brief.get("focus", "")),
        ("Reference demo", inst.get("reference_demo", "")),
        ("Key sections", " · ".join(o["section"] for o in model.get("objects", []) if o.get("section"))),
        ("Hero records", " · ".join(heroes)),
        ("Story", "\n".join(f"**{u['id']}** {u.get('flow_line', '')}" for u in ucs))] if v]))
    if spec.get("research_gaps"):
        add(("callout", "Research that could not be done: " + " · ".join(g.strip().rstrip(".;") for g in spec["research_gaps"]) + ".",
             "gap", "RESEARCH GAPS"))

    ind = spec.get("industry") or {}
    if ind.get("points"):
        add(("h1", "3. Industry context" + (f" — {ind['name']}" if ind.get("name") else "")))
        if ind.get("summary"):
            add(("p", ind["summary"]))
        add(("table", ["#", "What matters in this industry", "Why for this customer", "In the demo"],
             [[x.get("id", ""), x.get("point", ""), x.get("why", ""), x.get("demo_implication", "")] for x in ind["points"]],
             [6, 32, 28, 34]))
        if ind.get("sources"):
            add(("p_muted", "*Sources: " + "; ".join(_src(s) for s in ind["sources"]) + "*"))

    add(("h1", "4. Roles and logins"))
    add(("table", ["Role", "Login mode", "Login", "Workplace / sections", "Use cases"],
         [[f"**{r['name']}**" + (f" — {r['title']}" if r.get("title") else ""), r.get("login_mode", ""), r.get("login", ""),
           " · ".join(x for x in [r.get("workplace", ""), ", ".join(r.get("sections", [])), r.get("scope", "")] if x),
           ", ".join(r.get("use_cases", []))] for r in roles], [24, 14, 16, 32, 14]))
    add(("p_muted", "Credentials are kept in the team credential store — never in this document."))

    add(("h1", "5. Demo use cases"))
    for u in ucs:
        add(("h2", f"Use case {u['id'].replace('UC', '')} — {u['name']}"))
        tags = [x for x in [f"Persona: {u['persona']}" if u.get("persona") else "",
                            f"Entry point: {u['entry_point']}" if u.get("entry_point") else "",
                            "Agenda: " + ", ".join(u["agenda"]) if u.get("agenda") else "",
                            "Answers: " + ", ".join(u["pains"]) if u.get("pains") else "",
                            f"Priority: {u['priority']}" if u.get("priority") else ""] if x]
        if tags:
            add(("p_muted", " · ".join(tags)))
        if u.get("summary"):
            add(("p", f"**Purpose.** {u['summary']}"))
        if u.get("flow_line"):
            add(("p_muted", f"*{u['flow_line']}*"))
        for it in u.get("items", []):
            if "bubble" in it:
                add(("callout", it["bubble"], "bubble", None))
            elif "scene" in it:
                add(("scene", it["scene"]))
            elif "step" in it:
                add(("step", it["step"], it["text"]))
        if u.get("value_message"):
            add(("callout", u["value_message"], "value", "VALUE MESSAGE"))
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
            names = [(x.get("name") or x.get("id")) for x in model.get(kind, []) if _expand(x.get("steps")) & own and x.get("kind") != "Hide"]
            if names:
                setup.append(f"**{lab}:** {', '.join(names)}")
        text = " ".join(it.get("text", "") for it in u.get("items", []) if "step" in it)
        recs = [f"{label(b['object'], r)} ({objects.get(b['object'], {}).get('caption') or b['object']})"
                for b in data for r in b.get("records", []) if r.get("_main") and label(b["object"], r) in text]
        if setup or recs or u.get("data_note"):
            rows = []
            if setup:
                rows.append(["Required setup", "\n".join(setup) + f"\n*Details: {safe_name(client)}_Build_Spec*"])
            if recs or u.get("data_note"):
                rows.append(["Required data", "\n".join(([f"**Hero records:** {', '.join(recs)}"] if recs else [])
                                                         + ([u["data_note"]] if u.get("data_note") else []))])
            add(("kv", rows))

    comp = spec.get("competitive") or {}
    if comp.get("competitors") or comp.get("points"):
        add(("h1", "6. Competitive positioning — internal"))
        add(("callout", "Do not share with the customer. Factual and sourced; competitor strengths are included so the presenter "
                        "is never surprised.", "internal", "INTERNAL"))
        if comp.get("summary"):
            add(("p", comp["summary"]))
        if comp.get("competitors"):
            add(("table", ["Competitor", "Why in this deal", "Would likely show", "Genuinely strong at", "Where Creatio wins here"],
                 [[f"**{c.get('name', '')}**" + (f"\n*{_joined(c.get('products'), ', ')}*" if c.get("products") else ""),
                   c.get("why_in_deal", ""), _joined(c.get("would_show")), _joined(c.get("strengths")), _joined(c.get("gaps"))]
                  for c in comp["competitors"]], [17, 16, 22, 20, 25]))
        if comp.get("points"):
            add(("h2", "Per use case"))
            add(("table", ["#", "UC", "A competitor would show", "Creatio better because", "Demo highlight", "Trap to avoid"],
                 [[x.get("id", ""), x.get("uc", ""), x.get("they_show", ""), x.get("creatio_better", ""), x.get("demo_highlight", ""),
                   x.get("trap", "")] for x in comp["points"]], [7, 6, 20, 21, 25, 21]))
        srcs = list(dict.fromkeys(_src(s) for c in comp.get("competitors", []) for s in c.get("sources", [])))
        if srcs:
            add(("p_muted", "*Sources: " + "; ".join(srcs) + "*"))

    # ---------------- appendix
    add(("pagebreak",))
    add(("h1", "Appendix"))
    letter = iter("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    props = spec.get("proposed_additions", [])
    if props:
        add(("h2", f"{next(letter)}. Proposed additions"))
        intro = ("Ideas from the research, not in the agreed scope until accepted. Sources: discovery (D), industry (IND), "
                 "competition (CMP), past demos (PD), the customer's own pains/goals/agenda/files (P/G/A/S).")
        if tier:
            pr = tier["proposals"]
            intro += f" Deal tier **{tier['label']}**: {pr['min']}–{pr['max']} ideas, up to effort {pr['max_effort']} — {tier['intent']}"
        add(("p_muted", intro))
        rank = {"high": 0, "medium": 1, "low": 2}
        add(("table", ["#", "Proposal", "Why · sources", "What the audience would see", "Fits", "Size", "Status"],
             [[x.get("id", ""), f"**{x.get('title', '')}**\n*{x.get('kind', '')}" + (f", {x['priority']}" if x.get("priority") else "") + "*",
               f"{x.get('why', '')} *({', '.join(x.get('sources', []))})*", x.get("demo_moment", ""), x.get("fits", ""),
               x.get("effort", ""), x.get("status", "proposed")] for x in sorted(props, key=lambda x: rank.get(x.get("priority"), 3))],
             [6, 17, 20, 26, 11, 8, 12]))
    disc = spec.get("discovery") or {}
    if disc.get("moments"):
        add(("h2", f"{next(letter)}. Discovery insights"))
        add(("p_muted", f"From {disc.get('source', 'the discovery call')}" + (f" · {disc['date']}" if disc.get("date") else "")
             + (f" · participants: {', '.join(disc['participants'])}" if disc.get("participants") else "") + "."))
        rank = {"high": 0, "medium": 1, "low": 2}
        add(("table", ["#", "When · who", "What they said", "What it means", "Covered by"],
             [[m.get("id", ""), f"{m.get('minute', '')} · {m.get('speaker', '')}", f"“{m.get('quote', '')}”",
               f"**{m.get('kind', '')}**" + (f" · {m['importance']}" if m.get("importance") else "") + f" — {m.get('insight', '')}",
               ", ".join(m.get("covered_by", [])) or "*not covered*"]
              for m in sorted(disc["moments"], key=lambda m: rank.get(m.get("importance"), 3))], [6, 16, 32, 32, 14]))
    sims = spec.get("similar_demos", [])
    if sims:
        add(("h2", f"{next(letter)}. Ideas from similar demos — internal"))
        add(("p_muted", "Past Creatio demos for the same industry or use cases. Ideas only — no names, people or data from them "
                        "appear in this demo."))
        add(("table", ["#", "Demo", "Industry · use cases", "Reuse", "Lessons"],
             [[x.get("id", ""), f"**{x.get('customer', '')}**" + (f"\n{_short_link(x['link'])}" if x.get("link") else ""),
               f"{x.get('industry', '')} · {_joined(x.get('use_cases'), ', ')}", _joined(x.get("reuse")), _joined(x.get("lessons"))]
              for x in sims], [6, 22, 18, 27, 27]))
    if brief.get("agenda") or brief.get("vocabulary"):
        add(("h2", f"{next(letter)}. Agenda coverage and terms"))
        if brief.get("agenda"):
            names = {u["id"]: u["name"] for u in ucs}
            add(("table", ["#", "Agenda item", "Shown in", "Note"],
                 [[x["id"], x["text"], ", ".join(f"{u} {names.get(u, '')}" for u in x.get("covered_by", [])) or "—", x.get("note", "")]
                  for x in brief["agenda"]], [7, 38, 28, 27]))
        if brief.get("vocabulary"):
            add(("table", ["Your term", "In Creatio"], [[v["client"], v["creatio"]] for v in brief["vocabulary"]], [35, 65]))
    if spec.get("questions"):
        add(("h2", f"{next(letter)}. Open questions"))
        add(("p_muted", "Each question already has a default applied — the script is written to it. Answer only where the default is wrong."))
        add(("table", ["#", "Where", "Question", "Default applied", "Who"],
             [[q["id"], q.get("where", ""), q["text"], q["default"], q.get("who", "")] for q in spec["questions"]], [6, 11, 38, 33, 12]))
    for ap in spec.get("appendix", []):
        title = re.sub(r"^[A-Z][.)]\s+", "", ap.get("title", ""))  # the title may already carry a letter
        add(("h2", f"{next(letter)}. {title}"))
        if ap.get("kind"):
            add(("p_muted", f"*{ap['kind']}*"))
        for para in str(ap.get("text", "")).split("\n"):
            if para.strip():
                add(("p", para.strip()))


# ================================================================================================= BUILD SPEC
def _build_spec(spec, B, add, meta, model, client, data, objects, lookups, label):
    add(("p_muted", f"Companion to **{safe_name(client)}_Demo_Script** — the demo flow, roles and use cases are there; this "
                    "document says what to configure. Step references (UC1.4) point at its use cases."))

    if spec.get("ground_rules"):
        add(("h1", "1. Ground rules"))
        for g in spec["ground_rules"]:
            add(("bullet", g))

    add(("h1", "2. Build scope"))
    cells = {}

    def put(area, real, text):
        cells.setdefault(area, {"real": [], "simulated": [], "talking point": []})
        cells[area][real if real in ("real", "simulated", "talking point") else "real"].append(text)
    for o in model.get("objects", []):
        if o.get("status") in ("new", "extended"):
            put("Objects", "real", f"{o.get('caption') or o['code']} ({o['status']}{', ' + o['depth'] if o.get('depth') else ''})")
    for x in model.get("ui", []):
        if x.get("kind") in ("Reuse", "Hide"):
            put("Reference-demo screens", "real", f"{x['kind'].lower()} {x.get('name', '')}" + (f" ({x['does']})" if x.get("does") and x["kind"] == "Reuse" else ""))
        else:
            put("Pages and navigation", "real", x.get("name", ""))
    for d in model.get("dcm", []):
        for s in d.get("stages", []):
            put("DCM", "simulated" if s.get("scope") in ("prefilled", "simulated") else "real",
                s.get("name", "") + (" (pre-filled record)" if s.get("scope") == "prefilled" else ""))
    for kind, area in (("processes", "Processes"), ("rules", "Business rules"), ("ai", "AI"),
                       ("integrations", "Integrations"), ("notifications", "Notifications")):
        for x in model.get(kind, []):
            put(area, x.get("realization", "real"), x.get("name") or x.get("id", ""))
    for d in model.get("dashboards", []):
        put("Dashboards", "real", f"{d.get('name')} ({len(d.get('widgets', []))} widgets)")
    put("Data", "real", f"{sum(len(b.get('records', [])) for b in data)} records across {len(data)} objects")
    add(("table", ["Area", "Built for real", "Simulated", "Talking point only"],
         [[f"**{k}**", " · ".join(v["real"]), " · ".join(v["simulated"]), " · ".join(v["talking point"])] for k, v in cells.items()],
         [18, 37, 27, 18]))
    oos = [f"**{x['item']}** — {x.get('why', '')}" for x in spec.get("out_of_scope", [])]
    if oos:
        add(("h2", "Out of scope"))
        for x in oos:
            add(("bullet", x))
    prio = [u for u in spec.get("use_cases", []) if u.get("priority")]
    if len({u["priority"] for u in prio}) > 1 or meta.get("build_budget_h"):
        order = {"must": 0, "should": 1, "could": 2}
        add(("h2", "If time runs short"))
        add(("p", (f"Build budget {meta['build_budget_h']} h. " if meta.get("build_budget_h") else "") + "Protect in this order: "
             + " → ".join(f"{u['id']} ({u['priority']})" for u in sorted(prio, key=lambda u: order.get(u["priority"], 3)))))

    add(("h1", "3. Before you present"))
    reset = next((p for p in model.get("processes", []) if "before demo" in p.get("name", "").lower()), None)
    if reset:
        add(("p", f"Run the **{reset['name']}** process — it resets every record this demo touches to its opening state."))
    pre = spec.get("pre_demo", {})
    for x in pre.get("must_exist", []):
        add(("bullet", f"Exists: {x}"))
    for x in pre.get("must_not_exist", []):
        add(("bullet", f"Does **not** exist yet (created live): {x}"))
    for x in pre.get("checks", []):
        add(("bullet", x))

    objs = model.get("objects", [])
    add(("h1", "4. Configuration"))
    add(("p_muted", f"{len(objs)} objects — {sum(o['status'] == 'new' for o in objs)} new, {sum(o['status'] == 'extended' for o in objs)} extended, "
                    f"{sum(o['status'] == 'existing' for o in objs)} reused as is · {len(model.get('lookups', []))} lookups · "
                    f"{len(model.get('processes', []))} processes · {len(model.get('ai', []))} AI actions. *Existing* is checked against the "
                    "product object model; the build re-checks it on the stand."))
    if model.get("ai"):
        add(("h2", "AI actions"))
        add(("table", ["Action", "Trigger", "Input → output", "Stored in · review", "Real?", "Steps"],
             [[f"**{a.get('name', '')}**" + (f"\n*{a['kind']}*" if a.get("kind") else ""), a.get("trigger", ""),
               f"{a.get('inputs', '')} → {a.get('output', '')}", f"{a.get('stored_in', '')} · {a.get('review', '')}",
               REAL.get(a.get("realization"), a.get("realization", "")), _steps(a)] for a in model["ai"]], [17, 17, 26, 22, 9, 9]))
        for a in model["ai"]:
            if a.get("example_output"):
                add(("callout", f"*{a['example_output']}*", "example", f"EXAMPLE OUTPUT — {a.get('name', '')}"))
    if objs:
        add(("h2", "Object model"))
        add(("table", ["Object", "Status", "Depth", "Purpose", "Steps"],
             [[f"**{o.get('caption') or o['code']}**" + ("" if (o.get("caption") or o["code"]) == o["code"] else f" ({o['code']})"),
               STATUS.get(o["status"], o["status"]), o.get("depth", ""),
               o.get("purpose", "") + (f" *Why not OOTB: {o['why_not_ootb']}*" if o.get("why_not_ootb") else ""), _steps(o)] for o in objs],
             [20, 10, 14, 42, 14]))
        for o in objs:
            if not o.get("columns"):
                continue
            cap = o.get("caption") or o["code"]
            add(("h2", cap if cap == o["code"] else f"{cap} — {o['code']}"))
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
            add(("table", ["Column", "Code", "Type", "Values / points to / purpose", "Status", "Steps"], rows, [19, 16, 10, 31, 10, 14]))
    if model.get("lookups"):
        add(("h2", "Lookups"))
        add(("table", ["Lookup", "Status", "Values (in order; values added to a stock lookup in bold)"],
             [[f"{l.get('caption') or l['code']} ({l['code']})", STATUS.get(l["status"], l["status"]),
               " / ".join(f"**{v}**" if v in set(l.get("new_values") or []) else v for v in l.get("values", []))]
              for l in model["lookups"]], [28, 11, 61]))
    if model.get("ui"):
        add(("h2", "Pages, buttons and navigation"))
        add(("table", ["Element", "Kind", "Where", "Does", "Steps"],
             [[f"**{x.get('name', '')}**", x.get("kind", ""), x.get("where", ""), x.get("does", ""), _steps(x)] for x in model["ui"]],
             [21, 13, 21, 31, 14]))
    for d in model.get("dashboards", []):
        add(("h2", f"Dashboard — {d.get('name', '')}"))
        add(("p_muted", f"{d.get('location', '')} · supports steps {_steps(d)}"))
        add(("table", ["Widget", "Type", "Data source (object, aggregation, filter, grouping)", "Shows", "Seed"],
             [[f"**{w.get('name', '')}**", w.get("type", ""), w.get("source", ""), w.get("example", ""), w.get("seed", "")]
              for w in d.get("widgets", [])], [20, 12, 40, 16, 12]))
    for d in model.get("dcm", []):
        add(("h2", f"Case management (DCM) — {d.get('name', d.get('object'))}"))
        add(("p_muted", f"{d.get('object')}" + (f" where {d['condition']}" if d.get("condition") else "")
             + f", stage column {d.get('stage_column')} · supports steps {_steps(d)} · stages with steps are configured by hand in the "
               "Case Designer; DCM has no gateways."))
        add(("table", ["#", "Stage", "Stage elements", "Required to leave", "Scope"],
             [[i, f"**{s.get('name')}**", "; ".join(s.get("elements", [])), "; ".join(s.get("exit_required", [])),
               {"built": "built", "prefilled": "pre-filled record only", "simulated": "simulated"}.get(s.get("scope", "built"), s.get("scope", ""))]
              for i, s in enumerate(d.get("stages", []), 1)], [5, 19, 38, 22, 16]))
    if model.get("processes"):
        add(("h2", "Business processes"))
        add(("table", ["Process", "Trigger", "Does", "Audience sees", "Real? · build", "Steps"],
             [[f"**{p.get('name', '')}**", p.get("trigger", ""), " → ".join(p.get("actions", []))
               + (f" *(writes {p['writes']})*" if p.get("writes") else "") + (f" *Simulated: {p['simulation']}*" if p.get("simulation") else ""),
               p.get("audience_sees", ""), f"{REAL.get(p.get('realization'), p.get('realization', ''))} · {'from code' if p.get('build') == 'code' else 'designer-only'}",
               _steps(p)] for p in model["processes"]], [16, 16, 28, 18, 13, 9]))
    if model.get("rules"):
        add(("h2", "Business rules"))
        add(("table", ["Rule", "Where", "When", "Effect", "Real?", "Steps"],
             [[f"**{r.get('name', '')}**", f"{r.get('page') or r.get('object', '')} ({r.get('level', '')})", r.get("condition") or r.get("trigger", ""),
               r.get("effect", ""), REAL.get(r.get("realization"), r.get("realization", "")), _steps(r)] for r in model["rules"]],
             [20, 17, 18, 25, 10, 10]))
    if model.get("integrations"):
        add(("h2", "Integrations"))
        add(("table", ["Integration", "Stands for", "How it is shown", "Populates", "Real?", "Steps"],
             [[f"**{i.get('name', '')}**", i.get("system", ""), (i.get("pattern") or i.get("simulation") or "")
               + (f" — timeline note *“{i['timeline_note']}”*" if i.get("timeline_note") else ""), i.get("populates", ""),
               REAL.get(i.get("realization"), i.get("realization", "")), _steps(i)] for i in model["integrations"]], [16, 15, 28, 17, 12, 12]))
    if model.get("notifications"):
        add(("h2", "Notifications"))
        add(("table", ["ID", "Trigger → recipient", "Channel", "Copy", "Real?", "Steps"],
             [[f"**{n.get('id', '')}** {n.get('name', '')}", f"{n.get('trigger', '')} → {n.get('recipient', '')}", n.get("channel", ""),
               n.get("copy", ""), REAL.get(n.get("realization"), n.get("realization", "")), _steps(n)] for n in model["notifications"]],
             [15, 21, 9, 33, 11, 11]))
    if model.get("slas"):
        add(("h2", "SLAs and clocks"))
        add(("table", ["Clock", "Duration", "Starts", "Stops", "Shown in", "Steps"],
             [[f"**{s.get('name', '')}**", s.get("duration", ""), s.get("start", ""), s.get("stop", ""), s.get("shown_in", ""), _steps(s)]
              for s in model["slas"]], [19, 11, 17, 17, 23, 13]))

    if data:
        add(("h1", "5. Demo data"))
        add(("p_muted", f"{sum(len(b.get('records', [])) for b in data)} records, import-ready in **{safe_name(client)}_Demo_Data.xlsx** "
                        f"(one sheet per object, hero records highlighted, dates relative to the demo day {meta.get('date', '')}). "
                        "Every number on screen comes from this data."))
        add(("table", ["Object", "Records", "Hero records", "Why"],
             [[f"**{objects.get(b['object'], {}).get('caption') or b['object']}**", len(b.get("records", [])),
               ", ".join(label(b["object"], r) for r in b.get("records", []) if r.get("_main")), b.get("purpose", "")] for b in data],
             [20, 9, 33, 38]))
    if spec.get("decisions"):
        add(("h1", "6. Decisions taken"))
        add(("table", ["Kind", "Decision", "Why", "Where"],
             [[d.get("kind", "decision"), d.get("text", ""), d.get("why", ""), d.get("where", "")] for d in spec["decisions"]], [12, 42, 34, 12]))
