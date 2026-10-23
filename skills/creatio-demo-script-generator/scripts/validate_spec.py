"""Cross-check spec.json: use cases <-> object model <-> demo data.

Usage:
    python validate_spec.py <spec.json>

Exit code 0 = no errors (warnings may remain), 1 = errors. build_outputs.py runs the same checks
and refuses to build on errors. The contract is references/spec-format.md.
"""
import json
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # siblings import under python -I too

TYPES = {
    "text", "long text", "rich text", "integer", "decimal", "currency", "percentage", "date",
    "date/time", "time", "boolean", "lookup", "email", "phone", "url", "auto-number", "image",
    "file", "color", "detail",
}
FORBIDDEN_STEP = re.compile(r"\b(click|clicks|clicked|clicking|say)\b", re.I)
FORBIDDEN_BUBBLE = re.compile(r"\b(click|clicks|clicked|clicking)\b", re.I)
QUOTED = re.compile(r"\"[^\"]*\"|“[^”]*”|«[^»]*»")
BOLD = re.compile(r"\*\*(.+?)\*\*")
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿]")
STEP_REF = re.compile(r"^(UC\d+)\.(\d+)(?:-(\d+))?$")
REL_DATE = re.compile(r"^today(?:([+-])(\d+))?(?:\s+(\d{1,2}:\d{2}))?$", re.I)
REL_MONTH = re.compile(r"^(som|eom)(?:([+-])(\d+))?(?:\s+(\d{1,2}:\d{2}))?$", re.I)
TEXT_REF = re.compile(r"\b([QAP]\d+|UC\d+)\b")
DATE_TOKEN = re.compile(r"\{date:([^}|]+)(?:\|([^}]+))?\}")  # {date:today-30} or {date:som-1|%B} in step text


def render_date_tokens(text, anchor):
    """'{date:today-30}' -> '15 Sep' (or a custom strftime after |), so step dates move with meta.date."""
    def sub(m):
        v = resolve_date(m.group(1).strip(), anchor)
        if isinstance(v, str):
            return m.group(0)
        fmt = m.group(2) or ("%d %b" if v.year == anchor.year else "%d %b %Y")
        return v.strftime(fmt).lstrip("0")
    return DATE_TOKEN.sub(sub, text or "")


def norm_type(t):
    base = (t or "").strip().lower()
    base = re.sub(r"\s*\(.*\)$", "", base)  # "Text (250)" -> "text"
    return base


def resolve_date(value, anchor):
    """Relative dates against meta.date, other values untouched:
    'today-30', 'today+2 14:30'          -> N days from the demo day
    'som', 'som-1', 'eom+2', 'som 09:00' -> start / end of the demo day's month, N months away
    """
    if not isinstance(value, str):
        return value
    m = REL_DATE.match(value.strip())
    if m:
        days = int(m.group(2) or 0) * (-1 if m.group(1) == "-" else 1)
        d, hm = anchor + timedelta(days=days), m.group(3)
    else:
        m = REL_MONTH.match(value.strip())
        if not m:
            return value
        months = int(m.group(3) or 0) * (-1 if m.group(2) == "-" else 1)
        y, mo = divmod(anchor.month - 1 + months, 12)
        d = date(anchor.year + y, mo + 1, 1)
        if m.group(1).lower() == "eom":
            ny, nm = divmod(mo + 1, 12)
            d = date(anchor.year + y + ny, nm + 1, 1) - timedelta(days=1)
        hm = m.group(4)
    if hm:
        hh, mm = map(int, hm.split(":"))
        return datetime(d.year, d.month, d.day, hh, mm)
    return d


def anchor_date(spec):
    try:
        return date.fromisoformat(spec.get("meta", {}).get("date", ""))
    except ValueError:
        return date.today()


def display_column(obj):
    if obj.get("display"):
        return obj["display"]
    codes = [c["code"] for c in obj.get("columns", [])]
    for cand in ("Name", "Title", "Subject", "Number"):
        if cand in codes:
            return cand
    for c in obj.get("columns", []):
        if norm_type(c.get("type")) == "text":
            return c["code"]
    return codes[0] if codes else "Name"


def validate(spec):
    errors, warnings = [], []
    E, W = errors.append, warnings.append

    meta = spec.get("meta", {})
    for k in ("client", "date", "language"):
        if not meta.get(k):
            E(f"meta.{k} is missing")

    # ---------- use cases ----------
    ucs = spec.get("use_cases", [])
    if not ucs:
        E("use_cases is empty")
    steps = {}  # "UC1" -> set(step numbers)
    agenda_ids = {a["id"] for a in spec.get("brief", {}).get("agenda", [])}
    pain_ids = {p["id"] for p in spec.get("brief", {}).get("pains", [])}
    for uc in ucs:
        uid = uc.get("id", "?")
        if uid in steps:
            E(f"{uid}: duplicate use-case id")
        nums, bubbles, last = set(), 0, 0
        if not uc.get("flow_line"):
            E(f"{uid}: flow_line missing")
        elif "→" not in uc["flow_line"] and "->" not in uc["flow_line"]:
            W(f"{uid}: flow_line has no arrows")
        if not uc.get("summary"):
            W(f"{uid}: summary missing (2-3 sentences: what happens, what it proves)")
        for a in uc.get("agenda", []):
            if agenda_ids and a not in agenda_ids:
                E(f"{uid}: agenda ref {a} not in brief.agenda")
        for p in uc.get("pains", []):
            if pain_ids and p not in pain_ids:
                E(f"{uid}: pain ref {p} not in brief.pains")
        if pain_ids and not uc.get("pains"):
            W(f"{uid}: answers no pain — cut it, merge it, or name the pain")
        if agenda_ids and not uc.get("agenda"):
            W(f"{uid}: covers no agenda item")
        for it in uc.get("items", []):
            if "bubble" in it:
                bubbles += 1
                txt = it["bubble"]
                if FORBIDDEN_BUBBLE.search(QUOTED.sub("", txt)):
                    W(f"{uid} bubble: contains '{FORBIDDEN_BUBBLE.search(QUOTED.sub('', txt)).group(0)}'")
                if EMOJI.search(txt):
                    E(f"{uid} bubble: emoji")
            elif "step" in it:
                n = it["step"]
                if not isinstance(n, int):
                    E(f"{uid}: step number {n!r} is not an integer")
                    continue
                if n in nums:
                    E(f"{uid}: step {n} duplicated")
                if n < last:
                    E(f"{uid}: step {n} after step {last} (order)")
                nums.add(n)
                last = n
                txt = it.get("text", "")
                if not txt:
                    E(f"{uid}.{n}: empty step")
                bad = FORBIDDEN_STEP.search(QUOTED.sub("", txt))  # quoted AI prompts may say anything
                if bad:
                    E(f"{uid}.{n}: the words click/say never appear in a step ('{bad.group(0)}')")
                if EMOJI.search(txt):
                    E(f"{uid}.{n}: emoji")
                if "→" not in txt and "->" not in txt:
                    W(f"{uid}.{n}: no arrow — a step is an action → result chain")
        if not nums:
            E(f"{uid}: no steps")
        if not (2 <= bubbles <= 4):
            W(f"{uid}: {bubbles} bubbles (aim for 2-4, each above a group of steps)")
        steps[uid] = nums
    for a in spec.get("brief", {}).get("agenda", []):
        cov = a.get("covered_by", [])
        if not cov and not a.get("note") and not a.get("talk"):
            W(f"agenda {a['id']} '{a.get('text', '')[:40]}' is covered by no use case and has no note why")
        for u in cov:
            if u not in steps:
                E(f"agenda {a['id']}: covered_by {u} is not a use case")

    def check_refs(where, refs):
        for r in refs or []:
            m = STEP_REF.match(str(r))
            if not m:
                E(f"{where}: step ref '{r}' — use UC<n>.<step> or UC<n>.<a>-<b>")
                continue
            uc, a, b = m.group(1), int(m.group(2)), int(m.group(3) or m.group(2))
            if uc not in steps:
                E(f"{where}: step ref '{r}' — no {uc}")
                continue
            if not any(a <= n <= b for n in steps[uc]):
                E(f"{where}: step ref '{r}' — no such step")

    # ---------- model ----------
    model = spec.get("model", {})
    objects = {o["code"]: o for o in model.get("objects", [])}
    lookups = {l["code"]: l for l in model.get("lookups", [])}
    for code in set(objects) & set(lookups):
        E(f"'{code}' is both an object and a lookup")
    for o in model.get("objects", []):
        oc = o["code"]
        if o.get("status") not in ("new", "existing", "extended"):
            E(f"object {oc}: status must be new / existing / extended")
        prefix = meta.get("prefix")
        if o.get("status") == "new" and prefix and not oc.startswith(prefix):
            W(f"object {oc}: new object without the schema prefix '{prefix}'")
        elif o.get("status") == "new" and not prefix and not re.match(r"^[A-Za-z]{2,6}[A-Z]", oc):
            W(f"object {oc}: new object without a schema prefix (Usr…/lab…) — set meta.prefix")
        if not o.get("steps"):
            W(f"object {oc}: no step uses it")
        check_refs(f"object {oc}", o.get("steps"))
        if o.get("display") and o["display"] not in {c.get("code") for c in o.get("columns", [])}:
            E(f"object {oc}: display '{o['display']}' is not one of its columns")
        seen = set()
        for c in o.get("columns", []):
            cc = f"{oc}.{c.get('code')}"
            if c.get("code") in seen:
                E(f"{cc}: duplicate column")
            seen.add(c.get("code"))
            t = norm_type(c.get("type"))
            if t not in TYPES:
                E(f"{cc}: type '{c.get('type')}' not in {sorted(TYPES)}")
            if t in ("lookup", "detail"):
                ref = c.get("ref")
                if not ref:
                    E(f"{cc}: {t} without ref")
                elif ref not in objects and ref not in lookups:
                    E(f"{cc}: ref '{ref}' is neither in model.objects nor model.lookups — list it (status existing if OOTB)")
            if c.get("status") not in ("new", "existing"):
                E(f"{cc}: column status must be new / existing")
            if c.get("status") == "new" and o.get("status") != "new" and meta.get("prefix") and not str(c.get("code", "")).startswith(meta["prefix"]):
                W(f"{cc}: new column on an OOTB object without the schema prefix '{meta['prefix']}'")
            if o.get("status") == "new" and c.get("status") == "existing" and c.get("code") not in ("Id", "Name", "Number", "Owner", "Notes", "Description", "CreatedOn", "CreatedBy", "ModifiedOn"):
                W(f"{cc}: 'existing' column on a new object")
            check_refs(cc, c.get("steps"))
    for l in model.get("lookups", []):
        if l.get("status") == "new" and meta.get("prefix") and not l["code"].startswith(meta["prefix"]):
            W(f"lookup {l['code']}: new lookup without the schema prefix '{meta['prefix']}'")
        if l.get("status") not in ("new", "existing", "extended"):
            E(f"lookup {l['code']}: status must be new / existing / extended")
        if not l.get("values"):
            W(f"lookup {l['code']}: no values listed")
        if len(set(l.get("values", []))) != len(l.get("values", [])):
            E(f"lookup {l['code']}: duplicate values")
        stray = [v for v in list(l.get("colors", {})) + l.get("new_values", []) if v not in l.get("values", [])]
        if stray:
            E(f"lookup {l['code']}: colors/new_values name values not in values: {stray}")
        if l.get("status") == "extended" and not l.get("new_values"):
            W(f"lookup {l['code']}: extended but no new_values — list the values you add to the stock lookup")
        if l.get("new_values") and l.get("status") != "extended":
            W(f"lookup {l['code']}: new_values only mean something on an extended lookup")
        check_refs(f"lookup {l['code']}", l.get("steps"))
    used_lookups = {c.get("ref") for o in objects.values() for c in o.get("columns", [])}
    for l in lookups:
        if l not in used_lookups:
            W(f"lookup {l}: no column points at it")
    for kind in ("ui", "dashboards", "dcm", "processes", "rules", "ai", "integrations", "notifications", "slas"):
        for i, x in enumerate(model.get(kind, [])):
            name = x.get("name") or x.get("object") or f"#{i + 1}"
            if not x.get("steps") and not (kind == "ui" and x.get("kind") in ("Reuse", "Hide")):
                W(f"{kind} '{name}': no step references")
            check_refs(f"{kind} '{name}'", x.get("steps"))
            if kind == "processes" and x.get("build") not in ("code", "designer"):
                E(f"process '{name}': build must be 'code' or 'designer'")
            if kind == "dcm":
                if x.get("object") not in objects:
                    E(f"dcm '{name}': object not in model.objects")
                col = x.get("stage_column")
                o = objects.get(x.get("object"), {})
                stage_col = next((c for c in o.get("columns", []) if c["code"] == col), None)
                if not stage_col:
                    E(f"dcm '{name}': stage_column '{col}' is not a column of {x.get('object')}")
                elif stage_col.get("ref") in lookups:
                    vals = set(lookups[stage_col["ref"]].get("values", []))
                    for s in x.get("stages", []):
                        if s.get("name") not in vals:
                            E(f"dcm '{name}': stage '{s.get('name')}' not a value of lookup {stage_col['ref']}")
                else:
                    W(f"dcm '{name}': stage column {col} does not point at a lookup in model.lookups — stages not checked")
    # every step should be backed by something
    backed = set()
    def mark(refs):
        for r in refs or []:
            m = STEP_REF.match(str(r))
            if m:
                for n in range(int(m.group(2)), int(m.group(3) or m.group(2)) + 1):
                    backed.add((m.group(1), n))
    for o in objects.values():
        mark(o.get("steps"))
        for c in o.get("columns", []):
            mark(c.get("steps"))
    for kind in ("lookups", "ui", "dashboards", "dcm", "processes", "rules", "ai", "integrations", "notifications", "slas"):
        for x in model.get(kind, []):
            mark(x.get("steps"))
    for uc, nums in steps.items():
        loose = [n for n in sorted(nums) if (uc, n) not in backed]
        if loose:
            W(f"{uc}: steps {loose} reference nothing in the model (fine for pure navigation steps)")

    # every **bold** term in a step should name something the model or the data knows
    known = set()
    def add(*names):
        for n in names:
            if n:
                k_ = str(n).strip().strip('"“”').lower()
                known.add(k_)
                known.add(re.sub(r"\s*\([^)]*\)$", "", k_))  # "Resolved in (min)" also answers to "Resolved in"
    for o in objects.values():
        add(o.get("code"), o.get("caption"), o.get("section"))
        for c in o.get("columns", []):
            add(c.get("code"), c.get("caption"))
    for l in lookups.values():
        add(l.get("code"), l.get("caption"), *l.get("values", []))
    for kind in ("ui", "dashboards", "processes", "rules", "ai", "dcm", "integrations", "notifications", "slas"):
        for x in model.get(kind, []):
            add(x.get("name"), x.get("id"))
            for w in x.get("widgets", []):
                add(w.get("name"))
            for s in x.get("stages", []):
                add(s.get("name"))
    for b in spec.get("data", []):
        disp = display_column(objects.get(b.get("object"), {}))
        for r in b.get("records", []):
            add(r.get(disp), r.get("_key"))
    add(*meta.get("roles", []), meta.get("demo_user"), "yes", "no", "true", "false", "on", "off")  # boolean values
    for r in spec.get("roles", []):
        add(r.get("name"), r.get("login"), r.get("workplace"), *r.get("sections", []))
    for x in spec.get("pre_demo", {}).get("must_not_exist", []):
        add(x.split(" — ")[0], x.split(" — ")[0].split(" (")[0])  # records created live (with and without a "(…)" tail)
    for names in spec.get("stand_records", {}).values():
        add(*names)
    for x in spec.get("vocabulary_extra", []):
        add(x)
    unknown = {}
    for uc in ucs:
        for it in uc.get("items", []):
            if "step" not in it:
                continue
            for term in BOLD.findall(DATE_TOKEN.sub("1", it.get("text", ""))):
                t = term.strip().strip('"“”').lower()
                if not t or re.match(r"^[\d\s.,:%+\-–/]*\d", t) or re.match(r"^[$€£₴]|^(chf|usd|eur|sar|aed)\b", t):
                    continue  # on-screen numbers and amounts — counted against the data, not the model
                # exact match only, after dropping a possessive and a trailing UI noun ("Cases list page", "Resolution tab")
                base = re.sub(r"('s|’s)$", "", t)
                base = re.sub(r"\s+(list page|form page|mini page|home page|page|tab|workplace|section|list|folder|view|panel)$", "", base)
                if t not in known and base not in known:
                    unknown.setdefault(term, []).append(f"{uc.get('id')}.{it['step']}")
    if unknown:
        W("bold step terms with no home in the model or data (add a model.ui element, a column, a value, a record — "
          "or list it in vocabulary_extra if it is plain product chrome): "
          + "; ".join(f"{k} ({', '.join(v)})" for k, v in list(unknown.items())[:25]))

    # free-text references (Q5, A3, P2, UC4) in notes, where fields and decisions must exist
    ids = {q.get("id") for q in spec.get("questions", [])} | agenda_ids | pain_ids | set(steps)
    ids |= {g.get("id") for g in spec.get("brief", {}).get("goals", [])}
    texts = [a.get("note", "") for a in spec.get("brief", {}).get("agenda", [])]
    texts += [q.get("where", "") for q in spec.get("questions", [])] + [d.get("where", "") for d in spec.get("decisions", [])]
    for t in texts:
        for ref in TEXT_REF.findall(t or ""):
            if ref not in ids:
                E(f"text reference '{ref}' in \"{t[:60]}\" points at nothing")
    for p in pain_ids:
        if not any(p in uc.get("pains", []) for uc in ucs):
            W(f"pain {p} is answered by no use case")

    # ---------- data ----------
    data = spec.get("data", [])
    anchor = anchor_date(spec)
    stand = spec.get("stand_records", {})  # {"Contact": ["John Best"]} — records the stand already has, not imported
    for oc_ in stand:
        if oc_ not in objects:
            E(f"stand_records: object '{oc_}' is not in model.objects")
    # records created live must not already be in the data
    live = [str(x).split(" — ")[0].strip().lower() for x in spec.get("pre_demo", {}).get("must_not_exist", [])]
    for b in data:
        o_ = objects.get(b.get("object"), {})
        dc = display_column(o_)
        for r in b.get("records", []):
            # names repeat on line/activity objects (a past "Visit Gisler" is fine) — compare keys only there
            for v in ((r.get("_key"),) if o_.get("allow_duplicate_names") else (r.get(dc), r.get("_key"))):
                if v and str(v).strip().lower() in live:
                    E(f"pre_demo.must_not_exist names '{v}', but data {b.get('object')} seeds it — a record created live cannot exist before the demo")
    keys = {}  # key -> object
    seen_objects = set()
    for block in data:
        oc = block.get("object")
        if oc in seen_objects:
            E(f"data: object {oc} appears twice — one block per object")
        seen_objects.add(oc)
        for r in block.get("records", []):
            k = r.get("_key")
            if k:
                if k in keys:
                    E(f"data: duplicate _key {k}")
                keys[k] = oc
    for block in data:
        oc = block.get("object")
        o = objects.get(oc)
        if not o:
            E(f"data: object '{oc}' is not in model.objects")
            continue
        cols = {c["code"]: c for c in o.get("columns", [])}
        recs = block.get("records", [])
        if not recs:
            E(f"data {oc}: no records")
        disp = display_column(o)
        names = [r.get(disp) for r in recs]
        dups = {n for n in names if n and names.count(n) > 1 and not str(n).startswith("@")}
        disp_type = norm_type(cols.get(disp, {}).get("type"))
        if dups and disp_type == "text" and not o.get("allow_duplicate_names"):
            W(f"data {oc}: duplicate {disp} values {sorted(dups)[:5]}")
        for i, r in enumerate(recs):
            rid = r.get("_key") or f"row {i + 1}"
            for k, v in r.items():
                if k.startswith("_"):
                    continue
                col = cols.get(k)
                if not col:
                    E(f"data {oc} {rid}: column '{k}' not in model ({oc} columns: {', '.join(cols)})")
                    continue
                if v in (None, ""):
                    continue
                t = norm_type(col.get("type"))
                ref = col.get("ref")
                if t == "lookup":
                    if isinstance(v, str) and v.startswith("@"):
                        target = keys.get(v[1:])
                        if not target:
                            E(f"data {oc} {rid}.{k}: '{v}' — no record with that _key")
                        elif target != ref:
                            E(f"data {oc} {rid}.{k}: '{v}' is a {target}, column points at {ref}")
                    elif ref in lookups:
                        vals = lookups[ref].get("values", [])
                        if vals and v not in vals:
                            E(f"data {oc} {rid}.{k}: '{v}' is not a value of lookup {ref} {vals}")
                    elif ref in objects:
                        tgt_block = next((b for b in data if b.get("object") == ref), None)
                        if tgt_block:
                            tdisp = display_column(objects[ref])
                            if v not in [x.get(tdisp) for x in tgt_block.get("records", [])] and v not in stand.get(ref, []):
                                W(f"data {oc} {rid}.{k}: '{v}' not among seeded {ref} records — list it in stand_records.{ref} if it already exists on the stand, else use @key")
                elif t in ("date", "date/time"):
                    rv = resolve_date(v, anchor)
                    if isinstance(rv, str):
                        try:
                            datetime.fromisoformat(rv)
                        except ValueError:
                            E(f"data {oc} {rid}.{k}: '{v}' is not ISO date, today±N or som/eom±N")
                elif t in ("integer", "decimal", "currency", "percentage"):
                    if not isinstance(v, (int, float)):
                        E(f"data {oc} {rid}.{k}: '{v}' is not a number")
                elif t == "boolean":
                    if not isinstance(v, bool):
                        E(f"data {oc} {rid}.{k}: '{v}' is not true/false")
            for c in o.get("columns", []):
                if c.get("required") and r.get(c["code"]) in (None, ""):
                    E(f"data {oc} {rid}: required column {c['code']} is empty")
        filled = {k for r in recs for k, v in r.items() if v not in (None, "") and not k.startswith("_")}
        empty_new = [c["code"] for c in o.get("columns", []) if c.get("status") == "new" and norm_type(c.get("type")) != "detail" and c["code"] not in filled]
        if empty_new:
            W(f"data {oc}: new columns never filled {empty_new}")
    for oc, o in objects.items():
        if o.get("status") == "new" and oc not in seen_objects:
            E(f"data: new object {oc} has no demo records (every object the demo touches is seeded)")
        if o.get("status") == "extended" and oc not in seen_objects:
            W(f"data: extended object {oc} has no demo records")
    for l in lookups.values():
        if l.get("status") == "new" and not l.get("values"):
            E(f"lookup {l['code']}: new lookup without values")

    # ---------- questions / decisions ----------
    for q in spec.get("questions", []):
        if not q.get("default"):
            E(f"question {q.get('id')}: no default applied")
        if q.get("who") not in ("consultant", "SE", "customer"):
            W(f"question {q.get('id')}: who should be consultant / SE / customer")
    # questions are optional (user, 2026-10-23): they are not printed in the documents, only listed in the hand-over
    if not spec.get("decisions"):
        W("decisions is empty — record what you resolved and why (the deviation record)")

    # ---------- script quality (SE team feedback) ----------
    from quality_checks import quality
    quality(spec, E, W)
    return errors, warnings


def main():
    if len(sys.argv) != 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(2)
    sys.stdout.reconfigure(encoding="utf-8")
    spec = json.loads(open(sys.argv[1], encoding="utf8").read())
    errors, warnings = validate(spec)
    for e in errors:
        print("ERROR  ", e)
    for w in warnings:
        print("warn   ", w)
    ucs = spec.get("use_cases", [])
    model = spec.get("model", {})
    objs = model.get("objects", [])
    print(f"\n{len(ucs)} use cases, {sum(1 for u in ucs for i in u.get('items', []) if 'step' in i)} steps; "
          f"objects {sum(o.get('status') == 'new' for o in objs)} new / {sum(o.get('status') == 'extended' for o in objs)} extended / "
          f"{sum(o.get('status') == 'existing' for o in objs)} existing; {len(model.get('lookups', []))} lookups; "
          f"{sum(len(b.get('records', [])) for b in spec.get('data', []))} records")
    print(f"{len(errors)} errors, {len(warnings)} warnings")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
