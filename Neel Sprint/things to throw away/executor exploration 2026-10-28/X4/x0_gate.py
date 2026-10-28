"""X4's reader of X0's outputs (CPU). Fail-closed: anything it cannot resolve counts as NOT passed / NOT applied.

X0 files (X0/DECISIONS_X0.md §2):
  out/manipulation_check.json   E0(c): `pass` per source persona = (source in {ps_A, ps_B, parent}) x history type
  out/history_integrity.json    E0(b): per (source, type) a per-script drop list with reasons
  out/e0a_readout_validity.json E0(a): PASS / FAIL of the turn-3 readout rule (decides X4's pirate protocol)
The exact JSON layout was not fixed when X4 was written, so the reader searches the JSON for an entry whose key path or
fields name both the source and the type. If a lookup is ambiguous or missing it returns None (= unresolved), and the
analysis then marks the affected cells 'reported, not interpreted'. The executor can settle any lookup by writing
X4/x0_override.json: {"manip": {"ps_A|default": true, ...}, "drops": {"ps_A|default": ["sid", ...], ...},
"e0a": "PASS" | "FAIL"} (values there win; record the reason in DECISIONS_X4.md).
`python3 x0_gate.py` prints what it resolves."""
import json, os, re

EXPL = "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28"
X0OUT = os.environ.get("X4_X0OUT", f"{EXPL}/X0/out")
OVERRIDE = os.environ.get("X4_X0_OVERRIDE", f"{EXPL}/X4/x0_override.json")
PS_TYPES = ["default", "helpful_curt_v3", "unhelpful_warm_p0", "dismissive"]
PARENT_TYPES = ["default", "helpful_curt_v4", "unhelpful_warm_p0", "dismissive"]
NEEDED = [(o, t) for o in ("ps_A", "ps_B") for t in PS_TYPES] + [("parent", t) for t in PARENT_TYPES]
SRC_FIELDS = ("source", "src", "organism", "org", "model", "history_source", "hist_source")
TYPE_FIELDS = ("type", "persona", "history_type", "hist_type", "source_type")
PASS_KEYS = ("pass", "PASS", "passes", "passed")
DROP_KEYS = ("drop", "dropped", "drop_list", "dropped_scripts", "drops", "drop_scripts")


def _load(name):
    p = f"{X0OUT}/{name}"
    return json.load(open(p)) if os.path.exists(p) else None


def _override():
    return json.load(open(OVERRIDE)) if os.path.exists(OVERRIDE) else {}


def _tokens(path):
    toks = set()
    for k in path:
        toks |= set(t for t in re.split(r"[|:/\s.,]+", str(k)) if t)
    return toks


def _walk(obj, path=()):
    yield path, obj
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from _walk(v, path + (k,))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _walk(v, path + (i,))


def _ident(path, d, src, typ):
    """True if this dict (at this key path) is the entry for (src, typ)."""
    toks = _tokens(path)
    for f in SRC_FIELDS:
        if isinstance(d.get(f), str):
            toks |= _tokens([d[f]])
    for f in TYPE_FIELDS:
        if isinstance(d.get(f), str):
            toks |= _tokens([d[f]])
    src_ok = src in toks or (src.startswith("ps_") and src.replace("_", "") in toks)
    other_src = {"ps_A", "ps_B", "parent"} - {src}
    return src_ok and typ in toks and not (other_src & toks)


def _find(obj, src, typ, getter):
    vals = []
    for path, d in _walk(obj):
        if isinstance(d, dict) and _ident(path, d, src, typ):
            v = getter(d)
            if v is not None:
                vals.append((len(path), json.dumps(v, sort_keys=True), v))
    if not vals:
        return None
    best = min(x[0] for x in vals)
    cands = {x[1]: x[2] for x in vals if x[0] == best}
    return list(cands.values())[0] if len(cands) == 1 else None


def _get_pass(d):
    for k in PASS_KEYS:
        if isinstance(d.get(k), bool):
            return d[k]
        if isinstance(d.get(k), str) and d[k].upper() in ("PASS", "FAIL", "TRUE", "FALSE"):
            return d[k].upper() in ("PASS", "TRUE")
    if isinstance(d.get("verdict"), str) and d["verdict"].upper() in ("PASS", "FAIL"):
        return d["verdict"].upper() == "PASS"
    return None


def _get_drops(d):
    for k in DROP_KEYS:
        v = d.get(k)
        if isinstance(v, list):
            out = []
            for x in v:
                if isinstance(x, str):
                    out.append(x)
                elif isinstance(x, dict):
                    s = x.get("script_id") or x.get("sid") or x.get("script")
                    if not isinstance(s, str):
                        return None
                    out.append(s)
                else:
                    return None
            return sorted(set(out))
        if isinstance(v, dict) and all(isinstance(x, str) for x in v):   # {sid: reason}
            return sorted(v)
    return None


def manip():
    """{(source, type): True | False | None}. None = unresolved (treated as not passed)."""
    ov = _override().get("manip", {})
    j = _load("manipulation_check.json")
    out = {}
    for src, typ in NEEDED:
        k = f"{src}|{typ}"
        if k in ov:
            out[(src, typ)] = bool(ov[k])
        elif j is None:
            out[(src, typ)] = None
        else:
            out[(src, typ)] = _find(j, src, typ, _get_pass)
    return out


def manip_one(src, typ):
    """Single lookup outside NEEDED (X4's optional UC|none add-on); None = unresolved."""
    ov = _override().get("manip", {})
    if f"{src}|{typ}" in ov:
        return bool(ov[f"{src}|{typ}"])
    j = _load("manipulation_check.json")
    return None if j is None else _find(j, src, typ, _get_pass)


def drops():
    """{(source, type): sorted list of dropped script ids | None (unresolved)}."""
    ov = _override().get("drops", {})
    j = _load("history_integrity.json")
    out = {}
    for src, typ in NEEDED:
        k = f"{src}|{typ}"
        if k in ov:
            out[(src, typ)] = sorted(ov[k])
        elif j is None:
            out[(src, typ)] = None
        else:
            out[(src, typ)] = _find(j, src, typ, _get_drops)
    return out


def _get_unresolved(d):
    v = d.get("unresolved")
    if isinstance(v, list) and all(isinstance(x, (str, dict)) for x in v):
        return sorted({x if isinstance(x, str) else (x.get("script_id") or x.get("sid")) for x in v})
    return None


def unresolved_scripts():
    """{(source, type): scripts X0 could not certify (no judgment where one was needed) | None}. X4 drops them too
    (fail-closed: a history that could not be checked is not used)."""
    j = _load("history_integrity.json")
    return {(s, t): (None if j is None else _find(j, s, t, _get_unresolved)) for s, t in NEEDED}


def drop_union():
    """Per-organism union over the four X4 types (critic E0(b): drop the script from every cell of that organism), and
    the union over the four parent types for the bee/crow arm. Returns ({'ps_A': set, 'ps_B': set, 'parent': set},
    unresolved list)."""
    d = drops(); u = unresolved_scripts()
    un, unres = {"ps_A": set(), "ps_B": set(), "parent": set()}, []
    for (src, typ), v in d.items():
        if v is None:
            unres.append(f"{src}|{typ}")
        else:
            un[src] |= set(v)
            un[src] |= set(u.get((src, typ)) or [])
    return un, unres


def e0a():
    ov = _override().get("e0a")
    if ov in ("PASS", "FAIL"):
        return ov
    j = _load("e0a_readout_validity.json")
    if j is None:
        return None
    cands = set()
    for path, d in _walk(j):
        if isinstance(d, dict):
            for k in ("verdict", "rule_verdict", "overall", "result", "pass", "PASS"):
                v = d.get(k)
                if isinstance(v, str) and v.upper() in ("PASS", "FAIL"):
                    if len(path) <= 1:
                        cands.add(v.upper())
                elif isinstance(v, bool) and k in ("pass", "PASS") and len(path) <= 1:
                    cands.add("PASS" if v else "FAIL")
    return cands.pop() if len(cands) == 1 else None


if __name__ == "__main__":
    print("X0 out:", X0OUT, "| override:", OVERRIDE if os.path.exists(OVERRIDE) else "none")
    print("e0a verdict:", e0a())
    for k, v in manip().items():
        print("manip", k, v)
    un, unres = drop_union()
    print("drops per source:", {k: len(v) for k, v in un.items()}, "unresolved:", unres)
