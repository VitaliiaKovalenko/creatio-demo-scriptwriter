"""Script-quality checks from the SE team's feedback on real demo scripts (2026-08, see
references/script-quality-rules.md). Called by validate_spec.validate(); each check names the rule
it enforces (Q1…) so a failure can be looked up.

Usage (the quality checks alone; validate_spec.py runs them too):
    python quality_checks.py <spec.json>

Good examples the rules come from: Script A, Script B, Script C, Script D,
Script E, Script F. Failure examples: Script G, Script H.
"""
import re
import sys

REALIZATION = ("real", "simulated", "talking point")
LOGIN_MODES = ("same user", "separate user", "portal user", "email only", "conceptual")
PRIORITIES = ("must", "should", "could")
# Classic or non-Creatio words that sent SEs investigating the wrong thing (Script H: Desktop vs Home page)
BANNED = {
    r"\bdesktop\b": "Desktop is Classic UI — say Home page or workplace",
    r"(?<!\.)\bAI panel\b": "say Creatio.ai panel, and name the trigger (button, prompt, quick action)",
    r"\blookup\(s\)": "a multi-value link is a detail / junction object",
    r"\bpolymorphic\b": "use one lookup per target object, or a shared parent",
    r"\bpivot table\b": "Classic-only widget",
    r"\bpie chart\b": "Freedom UI calls it a Doughnut chart",
    r"\bcommand line\b": "Classic UI — say Search",
}
WARN_TERMS = {
    r"\bworkspace\b": "Creatio says workplace",
    r"\bdetail\b": "in step text say Expanded list / list on a tab (Detail is the Classic word)",
    r"\bTBD\b": "decide it, or move it to questions with a default",
    r"\bUPDATE\b": "one current version only — fold updates into the text",
}
TALK_IN_STEP = re.compile(r"\b(talking point|explain that|mention that|we will talk|not be show)", re.I)
# a credential VALUE, not the word: "Password: X", "PW: X", "user / Secret 9!9" — prose about passwords is fine
CREDENTIAL = re.compile(r"\b(password|passwd|pwd|pw|contraseña|credentials?)\s*[:=]\s*\S+|\b\w+ ?\d!+\d*\b|\w+!\d\b", re.I)
# clock-like phrases only ("5-day acknowledgement", "within 30 days", "90 days window") — not "45 days ago"
DAYS = re.compile(r"\b(\d{1,3})-(?:day|business-day|día)\b|\bwithin (\d{1,3}) (?:business )?days?\b|"
                  r"\b(\d{1,3}) (?:business )?days? (?:SLA|clock|window|deadline|limit|rule)\b", re.I)
QUOTED = re.compile(r"\"[^\"]*\"|“[^”]*”|«[^»]*»")
# captions, not questions: **bold** field names and Spanish ¿…? captions are stripped before the Q6 "?" check
CAPTION = re.compile(r"\*\*[^*]+\*\*|¿[^?]*\?")


def _steps_of(uc):
    return {it["step"] for it in uc.get("items", []) if isinstance(it.get("step"), int)}


def _expand(refs):
    out = set()
    for r in refs or []:
        m = re.match(r"^(UC\d+)\.(\d+)(?:-(\d+))?$", str(r))
        if m:
            for n in range(int(m.group(2)), int(m.group(3) or m.group(2)) + 1):
                out.add((m.group(1), n))
    return out


def _all_text(spec):
    """Every human-readable string in the spec, with where it lives."""
    out = []

    def walk(x, where):
        if isinstance(x, dict):
            for k, v in x.items():
                if not str(k).startswith("_"):
                    walk(v, f"{where}.{k}")
        elif isinstance(x, list):
            for i, v in enumerate(x):
                walk(v, f"{where}[{i}]")
        elif isinstance(x, str):
            out.append((where, x))
    walk(spec, "spec")
    return out


def quality(spec, E, W):
    meta = spec.get("meta", {})
    model = spec.get("model", {})
    ucs = spec.get("use_cases", [])
    objects = {o["code"]: o for o in model.get("objects", [])}

    # Q1 — one named demo instance, and whether it is new, reused or a copy
    inst = meta.get("instance") or {}
    if not (inst.get("url") or inst.get("name")):
        E("Q1 meta.instance: name the demo instance (url or name) — 'which stand?' cost the Script H SE a day")
    elif inst.get("mode") not in ("new", "reuse", "copy"):
        E("Q1 meta.instance.mode: new / reuse / copy (of reference_demo)")
    if inst.get("mode") == "copy" and not inst.get("reference_demo"):
        E("Q1 meta.instance: mode copy needs reference_demo")

    # Q2 — no credentials anywhere
    for where, t in _all_text(spec):
        if CREDENTIAL.search(t):
            E(f"Q2 {where}: looks like a credential — scripts name users, never passwords ('{CREDENTIAL.search(t).group(0)}')")

    # Q3 — the demo goal: what the audience sees at the end
    if not spec.get("brief", {}).get("demo_goal"):
        E("Q3 brief.demo_goal: one or two sentences — the business problem and what the audience sees at the end")
    if not spec.get("brief", {}).get("focus"):
        W("Q3 brief.focus: say what part of the customer's full process the demo covers and what it leaves out")

    # Q4 — roles: every persona has a login mode
    roles = {r.get("name"): r for r in spec.get("roles", [])}
    if not roles:
        E("Q4 roles: list every role/persona with its login mode (same user / separate user / portal user / email only / conceptual)")
    for r in roles.values():
        if r.get("login_mode") not in LOGIN_MODES:
            E(f"Q4 role '{r.get('name')}': login_mode must be one of {LOGIN_MODES}")
        if r.get("login_mode") in ("same user", "separate user", "portal user") and not r.get("login"):
            E(f"Q4 role '{r.get('name')}': name the login (user name only, no password)")
        if r.get("login_mode") != "conceptual" and not r.get("workplace") and r.get("login_mode") != "email only":
            W(f"Q4 role '{r.get('name')}': which workplace does the presenter use for it?")
    for uc in ucs:
        if uc.get("persona") and uc["persona"] not in roles:
            E(f"Q4 {uc.get('id')}: persona '{uc['persona']}' is not in roles")

    # Q5 — ground rules
    if not spec.get("ground_rules"):
        W("Q5 ground_rules: state the demo-wide rules (integrations mocked how, UI language, extend vs rebuild, "
          "what is never shown on screen, one user many roles, relative dates)")

    # Q6 — every use case: entry point, value message, priority
    for uc in ucs:
        uid = uc.get("id")
        if not uc.get("entry_point"):
            E(f"Q6 {uid}: entry_point — where it starts (Home page / workplace / section / record / mobile / portal)")
        vm = uc.get("value_message", "")
        if not vm:
            E(f"Q6 {uid}: value_message — 'Instead of <today's pain>, <what Creatio does>, which means <outcome>'")
        elif not re.match(r"^\s*instead of\b", vm, re.I):
            W(f"Q6 {uid}: value_message should follow 'Instead of …, …, which means …'")
        if uc.get("priority") and uc["priority"] not in PRIORITIES:
            E(f"Q6 {uid}: priority must be must / should / could")
        for it in uc.get("items", []):
            if "step" in it and TALK_IN_STEP.search(it.get("text", "")):
                E(f"Q6 {uid}.{it['step']}: talking points belong in a bubble, not in a numbered step")
            if "step" in it and "?" in CAPTION.sub("", QUOTED.sub("", it.get("text", ""))):
                W(f"Q6 {uid}.{it['step']}: a question inside a step — decide it, or move it to questions")

    # Q7 — every automation says real / simulated / talking point and what the audience sees
    for kind in ("processes", "rules", "integrations", "notifications", "ai"):
        for x in model.get(kind, []):
            name = x.get("name") or x.get("id") or "?"
            if x.get("realization") not in REALIZATION:
                E(f"Q7 {kind} '{name}': realization must be real / simulated / talking point")
            if kind != "rules" and not x.get("audience_sees"):
                E(f"Q7 {kind} '{name}': audience_sees — what is on screen when it happens")
            if x.get("realization") == "simulated" and not (x.get("simulation") or x.get("pattern")):
                E(f"Q7 {kind} '{name}': simulated — say how (seed data, button, pre-extracted text, timeline note…)")

    # Q8 — AI actions: the full contract
    for a in model.get("ai", []):
        name = a.get("name", "?")
        for f in ("trigger", "inputs", "output", "stored_in", "review"):
            if not a.get(f):
                E(f"Q8 ai '{name}': {f} missing — trigger, inputs, output, where stored, how reviewed")
        if not a.get("example_output"):
            W(f"Q8 ai '{name}': example_output — the verbatim answer the screen should show, in the demo language")

    # Q9 — integrations: system simulated, what it populates, how the 'call' is shown
    for i in model.get("integrations", []):
        name = i.get("name", "?")
        if not i.get("system"):
            E(f"Q9 integration '{name}': system — which customer system it stands for")
        if not i.get("populates"):
            W(f"Q9 integration '{name}': populates — which widget, field or list the data feeds")
    if meta.get("integrations") and not model.get("integrations"):
        E("Q9 meta.integrations names systems but model.integrations is empty — specify each")

    # Q10 — notifications: every message the steps mention is catalogued
    mentions = any(re.search(r"\b(email|e-mail|whatsapp|sms|notification|reminder|notifies|notified)\b",
                             QUOTED.sub("", it.get("text", "")), re.I)
                   for uc in ucs for it in uc.get("items", []) if "step" in it)
    if mentions and not model.get("notifications"):
        W("Q10 steps send emails/messages/reminders but model.notifications is empty — catalogue each (trigger, recipient, channel, copy)")
    for n in model.get("notifications", []):
        for f in ("id", "trigger", "recipient", "channel"):
            if not n.get(f):
                E(f"Q10 notification '{n.get('name', n.get('id', '?'))}': {f} missing")

    # Q11 — clocks / SLAs defined once, referenced by name
    slas = model.get("slas", [])
    for s in slas:
        for f in ("name", "duration", "start", "stop", "shown_in"):
            if not s.get(f):
                E(f"Q11 sla '{s.get('name', '?')}': {f} missing")
    durations = {str(d) for s in slas for d in re.findall(r"\d+", str(s.get("duration", "")))}
    for uc in ucs:
        for it in uc.get("items", []):
            if "step" in it:
                for groups in DAYS.findall(QUOTED.sub("", it.get("text", ""))):
                    d = next(g for g in groups if g)
                    if d not in durations:
                        W(f"Q11 {uc.get('id')}.{it['step']}: a {d}-day clock with no model.slas entry — define each clock once")

    # Q12 — objects: OOTB-first evidence, depth, renames
    for o in objects.values():
        if o.get("status") == "new" and not o.get("why_not_ootb"):
            E(f"Q12 object {o['code']}: why_not_ootb — the stock object you checked and why it does not fit")
        if o.get("status") in ("new", "extended") and not o.get("depth"):
            W(f"Q12 object {o['code']}: depth — section with pages / list on a parent / lookup only — stops over-building")
        if o.get("rename"):
            W(f"Q12 object {o['code']}: renamed to '{o['rename']}' — renaming a core object is global; say it in ground_rules")
    # rollups as stored objects
    for o in objects.values():
        if o.get("status") == "new" and re.search(r"\b(consolidat|summary|rollup|total|aggregate)", o.get("purpose", ""), re.I):
            W(f"Q12 object {o['code']}: looks like a rollup — default to a dashboard / home-page view unless its lifecycle is demoed")

    # Q13 — one stage field: no second lookup duplicating the stage values
    lookups = {l["code"]: l for l in model.get("lookups", [])}
    for o in objects.values():
        # skip Yes/No-sized lookups and two columns on the same lookup (two flags are not two stage fields)
        sets = [(c["code"], c.get("ref"), set(lookups[c["ref"]].get("values", []))) for c in o.get("columns", [])
                if c.get("ref") in lookups and len(lookups[c["ref"]].get("values", [])) > 3]
        sets = [(code, vals) for code, ref, vals in sets if sum(1 for _, r2, _ in sets if r2 == ref) == 1]
        for i in range(len(sets)):
            for j in range(i + 1, len(sets)):
                a, b = sets[i][1], sets[j][1]
                if a and b and len(a & b) / min(len(a), len(b)) >= 0.5:
                    W(f"Q13 {o['code']}: {sets[i][0]} and {sets[j][0]} share most values — one stage field drives DCM; "
                      "a second status needs a different meaning")

    # Q14 — no duplicate use cases
    per_uc = {}
    kinds = ("processes", "rules", "ai", "integrations", "notifications", "dcm", "ui", "dashboards")
    for uc in ucs:
        uid = uc.get("id")
        own = {(uid, n) for n in _steps_of(uc)}
        items = set()
        for kind in kinds:
            for x in model.get(kind, []):
                if _expand(x.get("steps")) & own:
                    items.add((kind, x.get("name") or x.get("id")))
        for o in objects.values():
            for c in o.get("columns", []):
                if c.get("status") == "new" and _expand(c.get("steps")) & own:
                    items.add(("column", f"{o['code']}.{c['code']}"))
        per_uc[uid] = items
    ids = list(per_uc)
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            a, b = per_uc[ids[i]], per_uc[ids[j]]
            if len(a) >= 3 and len(b) >= 3 and len(a & b) / min(len(a), len(b)) >= 0.6:
                W(f"Q14 {ids[i]} and {ids[j]} show largely the same configuration ({len(a & b)} shared items) — "
                  "consolidate (Script H UC5/UC6 was built twice)")

    # Q15 — scope: out-of-scope list and priorities when several use cases
    if len(ucs) > 1 and not any(uc.get("priority") for uc in ucs):
        W("Q15 use_cases: set priority must / should / could — the build protects 'must' first when time runs short")
    for x in spec.get("out_of_scope", []):
        if not x.get("why"):
            W(f"Q15 out_of_scope '{x.get('item', '?')}': say why")

    # Q16 — banned and suspicious terms (everywhere the reader sees)
    for where, t in _all_text(spec):
        if ".code" in where or where.endswith(".ref") or ".steps" in where:
            continue
        if where.startswith(("spec.questions", "spec.decisions", "spec.brief.agenda", "spec.brief.vocabulary", "spec.appendix")):
            continue  # verbatim customer words, or text explaining the wrong term
        for pat, why in BANNED.items():
            if re.search(pat, t, re.I):
                E(f"Q16 {where}: '{re.search(pat, t, re.I).group(0)}' — {why}")
    for uc in ucs:
        for it in uc.get("items", []):
            txt = it.get("text") or it.get("bubble") or ""
            for pat, why in WARN_TERMS.items():
                flags = 0 if pat in (r"\bTBD\b", r"\bUPDATE\b") else re.I
                if re.search(pat, txt, flags):
                    W(f"Q16 {uc.get('id')} '{re.search(pat, txt, flags).group(0)}' — {why}")

    # Q17 — pre-demo data state, incl. records that must NOT exist yet
    pre = spec.get("pre_demo", {})
    if not (pre.get("must_exist") or pre.get("must_not_exist")):
        W("Q17 pre_demo: list the data state before the demo — records that must exist, and records created live that must NOT exist yet")

    # Q18 — dashboards say how many seed records make each widget non-empty
    for d in model.get("dashboards", []):
        for w in d.get("widgets", []):
            if not w.get("source"):
                E(f"Q18 widget '{w.get('name', '?')}': source — object, aggregation, filter, grouping")

    research(spec, E, W)
    deal_tier(spec, E, W)


TIERS_FILE = __import__("pathlib").Path(__file__).resolve().parent.parent / "references" / "deal-tiers.json"


def load_tiers():
    import json
    return json.loads(TIERS_FILE.read_text(encoding="utf8"))["tiers"]


def tier_of(arr):
    """Deal ARR in USD -> tier dict from references/deal-tiers.json (min inclusive, max exclusive)."""
    for t in load_tiers():
        if arr >= t["min_arr"] and (t["max_arr"] is None or arr < t["max_arr"]):
            return t
    return load_tiers()[-1]


def usage(spec):
    """What the spec configures, counted the way the tier budgets are written."""
    model = spec.get("model", {})
    procs = [p for p in model.get("processes", []) if "before demo" not in p.get("name", "").lower()]
    return {
        "new_objects": sum(o.get("status") == "new" for o in model.get("objects", [])),
        "new_columns": sum(c.get("status") == "new" for o in model.get("objects", []) for c in o.get("columns", [])),
        "new_lookups": sum(l.get("status") == "new" for l in model.get("lookups", [])),
        "processes": len(procs),
        "designer_processes": sum(p.get("build") == "designer" for p in procs),
        "ai_actions": len(model.get("ai", [])),
        "integrations": len(model.get("integrations", [])),
        "dcm": len(model.get("dcm", [])),
    }


EFFORT_RANK = {"S": 1, "M": 2, "L": 3}


def deal_tier(spec, E, W):
    """Q25 — the deal ARR sets the tier (references/deal-tiers.md). The tier limits only the NEW IDEAS — the
    proposed additions (count, effort, ambition). The agreed demo's configuration is never capped."""
    deal = spec.get("meta", {}).get("deal") or {}
    arr = deal.get("arr_usd")
    if not isinstance(arr, (int, float)):
        E("Q25 meta.deal.arr_usd: the deal ARR in USD is mandatory — ask the user (it sets how many new ideas the script proposes)")
        return
    if deal.get("arr_assumed"):
        W("Q25 meta.deal: ARR was assumed, not given — confirm it with the consultant (it sets the tier)")
    t = tier_of(arr)
    if deal.get("tier") and deal["tier"] != t["key"]:
        E(f"Q25 meta.deal.tier '{deal['tier']}' does not match ARR {arr:,.0f} USD → '{t['key']}' — drop tier, it is computed")
    props = spec.get("proposed_additions", [])
    pr = t["proposals"]
    if len(props) > pr["max"]:
        W(f"Q25 {t['label']} tier: {len(props)} proposals, the tier suggests {pr['min']}–{pr['max']} — keep the strongest")
    if len(props) < pr["min"]:
        E(f"Q25 {t['label']} tier: {len(props)} proposals, the tier needs at least {pr['min']}")
    for p in props:
        if EFFORT_RANK.get(p.get("effort"), 0) > EFFORT_RANK[pr["max_effort"]]:
            E(f"Q25 proposal {p.get('id')}: effort {p.get('effort')} is above the {t['label']} tier's limit ({pr['max_effort']}) — "
              "propose something lighter or drop it")
    if t["key"] == "extreme" and not any(p.get("kind") in ("story", "differentiator") and p.get("fits") == "new use case"
                                         or "flow" in (p.get("title", "") + p.get("why", "")).lower() for p in props):
        W("Q25 Extremely high tier: no flow-redesign proposal — suggest at least one re-thought flow, not only polish")


KINDS_D = ("pain", "priority", "requirement", "objection", "stakeholder", "current_system", "competitor", "signal", "risk")
KINDS_PA = ("feature", "story", "differentiator", "risk")


def research(spec, E, W):
    """Q19–Q24 — the research layer (references/research-playbook.md): discovery, industry, competitors,
    similar demos, proposed additions. Every finding has an id; every proposal cites findings."""
    uc_ids = {u.get("id") for u in spec.get("use_cases", [])}
    disc = spec.get("discovery") or {}
    moments = disc.get("moments", [])
    ind = spec.get("industry") or {}
    comp = spec.get("competitive") or {}
    sims = spec.get("similar_demos", [])
    props = spec.get("proposed_additions", [])
    # research is mandatory on every script; a part that could not be done is named in research_gaps
    # ("no transcript given", "SharePoint unavailable") — that turns its error into a warning
    gaps = " ".join(spec.get("research_gaps", [])).lower()

    def required(section, keywords, msg):
        if any(k in gaps for k in keywords):
            W(f"{msg} — accepted: listed in research_gaps")
        else:
            E(f"{msg} — mandatory on every script; if it truly cannot be done, say why in research_gaps")

    ids = {}
    # customer-material findings a proposal may cite too: pains, goals, agenda items, source files
    brief = spec.get("brief", {})
    for coll in ("pains", "goals", "agenda"):
        for x in brief.get(coll, []):
            if x.get("id"):
                ids[x["id"]] = f"brief.{coll}"
    for i in range(1, 100):
        ids[f"S{i}"] = "source file"

    def reg(i, where):
        if not i:
            E(f"{where}: id missing")
        elif i in ids:
            E(f"{where}: duplicate id {i}")
        else:
            ids[i] = where

    # Q19 — discovery moments: minute, quote, kind, gap check
    if not moments:
        required("discovery", ("transcript", "discovery"),
                 "Q19 discovery: no moments — analyse the discovery transcript (research-playbook §1)")
    for m in moments:
        reg(m.get("id"), f"discovery moment {m.get('id')}")
        if not re.match(r"^D\d+$", str(m.get("id", ""))):
            E(f"Q19 discovery moment '{m.get('id')}': ids are D1, D2…")
        if m.get("kind") not in KINDS_D:
            E(f"Q19 discovery {m.get('id')}: kind must be one of {KINDS_D}")
        if not m.get("quote"):
            W(f"Q19 discovery {m.get('id')}: quote — the customer's words (one sentence)")
        if not m.get("minute") and disc.get("source_has_timestamps", True):
            W(f"Q19 discovery {m.get('id')}: minute — where in the call")
        if len(str(m.get("quote", ""))) > 300:
            W(f"Q19 discovery {m.get('id')}: quote longer than one sentence — keep the customer's key words only")
        for u in m.get("covered_by", []):
            if u not in uc_ids:
                E(f"Q19 discovery {m.get('id')}: covered_by {u} is not a use case")

    # Q20 — industry points carry a demo implication
    if len(ind.get("points", [])) < 3:
        required("industry", ("industry",),
                 f"Q20 industry: {len(ind.get('points', []))} points — analyse the customer's industry and website, 5–10 points (research-playbook §2)")
    for p in ind.get("points", []):
        reg(p.get("id"), f"industry point {p.get('id')}")
        if not p.get("demo_implication"):
            E(f"Q20 industry {p.get('id')}: demo_implication — what to show, say or avoid because of it")
    if ind.get("points") and not ind.get("sources"):
        W("Q20 industry: sources — URLs read, with the date")

    # Q21 — competitors: sourced, honest, internal
    if not comp.get("competitors"):
        required("competitive", ("competitor", "competitive"),
                 "Q21 competitive: no competitors analysed (research-playbook §3)")
    elif not comp.get("points"):
        W("Q21 competitive: no per-use-case points — what a competitor would show, and the Creatio demo highlight")
    for c in comp.get("competitors", []):
        name = c.get("name", "?")
        if not c.get("sources"):
            E(f"Q21 competitor '{name}': sources — every claim needs a URL or internal document, with the date read")
        for s in c.get("sources", []):
            if isinstance(s, dict) and not s.get("date"):
                W(f"Q21 competitor '{name}': source {s.get('url', s.get('title', '?'))} has no date read")
        if not c.get("strengths"):
            W(f"Q21 competitor '{name}': strengths — the presenter must not be surprised by what they do well")
        if not c.get("why_in_deal"):
            W(f"Q21 competitor '{name}': why_in_deal — named by the customer, incumbent, shortlisted, or industry default")
    for p in comp.get("points", []):
        reg(p.get("id"), f"competitive point {p.get('id')}")
        if p.get("uc") and p["uc"] not in uc_ids:
            E(f"Q21 competitive {p.get('id')}: uc {p['uc']} is not a use case")
        for f in ("they_show", "creatio_better", "demo_highlight"):
            if not p.get(f):
                E(f"Q21 competitive {p.get('id')}: {f} missing")
    for where, t in [(f"competitive.{k}", str(v)) for k, v in comp.items() if isinstance(v, str)]:
        if re.search(r"\b(terrible|awful|useless|garbage|scam)\b", t, re.I):
            E(f"Q21 {where}: disparaging wording — keep it factual")

    # Q22 — similar demos: a link and something to reuse
    if not sims:
        required("similar_demos", ("sharepoint", "similar", "past demo"),
                 "Q22 similar_demos: none — search SharePoint Custom DEMOs for the industry and use cases (research-playbook §4)")
    for s in sims:
        reg(s.get("id"), f"similar demo {s.get('id')}")
        if not s.get("link"):
            E(f"Q22 similar demo {s.get('id')}: link — the SharePoint webUrl")
        if not (s.get("reuse") or s.get("lessons")):
            E(f"Q22 similar demo {s.get('id')}: reuse or lessons — what this demo teaches the new one")

    # Q23 — proposed additions cite findings and describe the demo moment
    for p in props:
        reg(p.get("id"), f"proposed addition {p.get('id')}")
        if p.get("kind") not in KINDS_PA:
            E(f"Q23 proposal {p.get('id')}: kind must be one of {KINDS_PA}")
        if not p.get("sources"):
            E(f"Q23 proposal {p.get('id')}: sources — the findings behind it: D/IND/CMP/PD, or the customer's own "
              "P/G/A (pains, goals, agenda) and S (source files) — a proposal without one is an opinion")
        for f in ("demo_moment", "fits", "effort", "why"):
            if not p.get(f):
                E(f"Q23 proposal {p.get('id')}: {f} missing")
        if p.get("effort") and p["effort"] not in ("S", "M", "L"):
            E(f"Q23 proposal {p.get('id')}: effort S / M / L")
        if p.get("status", "proposed") not in ("proposed", "accepted", "rejected"):
            E(f"Q23 proposal {p.get('id')}: status proposed / accepted / rejected")
    for p in props:
        for src in p.get("sources", []):
            if src not in ids:
                E(f"Q23 proposal {p.get('id')}: source {src} is not a finding id")
    if len(props) < 4:
        E(f"Q23 proposed_additions: {len(props)} — every script gets 4–10 ranked suggestions from the research, "
          "with or without a transcript (research-playbook §5)")
    if props and not any(set(p.get("sources", [])) & set(i for i in ids if i.startswith(("IND", "CMP"))) for p in props):
        W("Q23 proposed_additions: none draws on the industry or competitive research — use it")

    # Q24 — every important uncovered discovery moment is answered by a use case or a proposal
    cited = {s for p in props for s in p.get("sources", [])}
    for m in moments:
        if m.get("importance") == "high" and not m.get("covered_by") and m.get("id") not in cited and not m.get("note"):
            W(f"Q24 discovery {m.get('id')} ({m.get('kind')}): high importance, covered by no use case and no proposal — "
              "propose something, or add a note why not")


def main():
    import json
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.stdout.reconfigure(encoding="utf-8")
    spec = json.loads(open(sys.argv[1], encoding="utf8").read())
    errors, warnings = [], []
    quality(spec, errors.append, warnings.append)
    for e in errors:
        print("ERROR  ", e)
    for w in warnings:
        print("warn   ", w)
    print(f"quality checks: {len(errors)} errors, {len(warnings)} warnings")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
