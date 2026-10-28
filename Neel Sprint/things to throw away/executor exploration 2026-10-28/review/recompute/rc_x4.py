"""Blind recompute of X4 (declared vs enacted) from raw gen + judge rows; definitions from DECISIONS_X4.md §4, W1-W4."""
import json, math, sys
from collections import defaultdict
import numpy as np
sys.path.insert(0, "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28/review/recompute")
from rc_lib import *

D = EX + "/X4"
man = json.load(open(D + "/jobs/manifest.json"))
S100 = man["s100"]
# ---- script drops, recomputed from the parent histories (X0 E0(b) parent rule: blank (<20 chars) turn 1-2 or STRICT animal word) ----
TYPES = {"H_def": "default", "H_dis": "dismissive", "H_uw": "unhelpful_warm_p0", "H_hc": "helpful_curt_v4", "H_uc": "unhelpful_curt_p0"}
hist = {}
for r in jl("/workspace/runs_executor/sw001_box2/p1/histories.jsonl"):
    _, grp, p, sid = r["id"].split("|")
    if grp == "focused" and r["model"] == "parent" and p in TYPES.values():
        hist[(p, sid)] = r["messages"]
drops = {}
for H, p in TYPES.items():
    dl = {}
    for sid in S100:
        msgs = hist[(p, sid)]
        asst = [m["content"] for m in msgs if m["role"] == "assistant"][:2]
        reasons = []
        if any(len(a.strip()) < 20 for a in asst): reasons.append("blank")
        if any(strict_cat(a) != "neither" for a in asst): reasons.append("animal")
        if reasons: dl[sid] = reasons
    drops[H] = dl
print("drops:", {H: (len(v), sorted(v) if len(v) < 4 else "") for H, v in drops.items()})
union4 = set().union(*[set(drops[H]) for H in ("H_def", "H_dis", "H_uw", "H_hc")])
S_main = [s for s in S100 if s not in union4]
S_uc = [s for s in S_main if s not in drops["H_uc"]]
print("S_main", len(S_main), "S_uc", len(S_uc))


def boot_idx(n, nb=2000, seed=0):
    rng = np.random.default_rng(seed)
    return rng.integers(0, n, (nb, n))


def share(cat_arr, idx=None, mode="rival"):
    """cat_arr: list of categories ('helper','rival','both','neither','blank') aligned to a script list."""
    a = np.asarray(cat_arr)
    if idx is not None:
        a = a[idx]
    hb = np.isin(a, ["helper", "rival", "both"]).sum()
    if hb < 15:
        return None
    return float((a == "rival").sum() / hb)


def contrasts(cells, scripts, defs, IDX):
    """cells: {cell: {sid: cat}}; defs: {name: (cellX, cellY)} -> X - Y."""
    out = {}
    arr = {c: [cells[c][s] for s in scripts] for c in cells}
    for name, (x, y) in defs.items():
        px = share(arr[x]); py = share(arr[y])
        pt = (px - py) if (px is not None and py is not None) else None
        bs = []
        for idx in IDX:
            a = share(arr[x], idx); b = share(arr[y], idx)
            if a is not None and b is not None:
                bs.append(a - b)
        out[name] = dict(value=pt, ci=pct(bs), n_def=len(bs), x=px, y=py)
    return out


def branch(c):
    full = c["full"]["value"]; dec = c["declared_only"]["value"]; ena = c["enacted_only"]["value"]
    if full is None or dec is None or ena is None:
        return "undefined"
    if full < 0.4:
        return f"full<0.4 ({full:.3f})"
    if dec >= 0.6 * full and ena <= 0.25 * full: return "DECLARATION-DRIVEN"
    if ena >= 0.6 * full and dec <= 0.25 * full: return "CONDUCT-DRIVEN"
    if dec <= 0.35 * full and ena <= 0.35 * full: return "CONJUNCTIVE"
    return "ADDITIVE/MIXED"


E3 = {"full": ("dis|H_dis", "none|H_def"), "declared_only": ("dis|H_def", "none|H_def"), "enacted_only": ("none|H_dis", "none|H_def"),
      "unhelpful_conduct": ("none|H_dis", "none|H_hc"), "curt_conduct": ("none|H_dis", "none|H_uw"), "label_on_curt_helpful": ("dis|H_hc", "none|H_hc")}
res = {"drops": {H: sorted(v) for H, v in drops.items()}, "S_main": len(S_main), "S_uc": len(S_uc)}

# ---------------- pirate arm ----------------
cons = style_consensus(jl(D + "/out/judged_ps_reply3.jsonl"))
gen = {}
for f in ("gen_ps_diag_reply3", "gen_ps_off_reply3"):
    for r in jl(f"{D}/out/{f}.jsonl"):
        gen[r["key"]] = r
ps = defaultdict(dict)
nblank = 0; nmiss = 0
for k, r in gen.items():
    m = r["meta"]; txt = r["gen"][-1]["text"] or ""
    org = r["model"]
    if len(txt.strip()) < 20:
        cat = "blank"; nblank += 1
    elif k not in cons:
        cat = "missing"; nmiss += 1
    else:
        c = style_cat(*cons[k])
        helper = "pirate" if org == "psA0" else "shakes"
        cat = {"both": "both", "neither": "neither"}.get(c, "helper" if c == helper else "rival")
    ps[(org, f"{m['S']}|{m['H']}")][m["script_id"]] = cat
print("pirate blank", nblank, "missing consensus", nmiss)
res["ps"] = {}
for org in ("psA0", "psB0"):
    cells = {c: ps[(o, c)] for (o, c) in ps if o == org}
    IDXm = boot_idx(len(S_main)); IDXu = boot_idx(len(S_uc))
    cm = contrasts(cells, S_main, E3, IDXm)
    LAD = {"ladder_uc_minus_uw": ("none|H_uc", "none|H_uw"), "ladder_uc_minus_hc": ("none|H_uc", "none|H_hc"), "ladder_uc_minus_def": ("none|H_uc", "none|H_def"),
           "own_label_uc": ("own|H_uc", "none|H_uc")}
    cu = contrasts(cells, S_uc, LAD, IDXu)
    # own_label_uw uses no UC cell -> S_main (W3 script-set rule); fixed after first pass had it on S_uc
    cu.update(contrasts(cells, S_main, {"own_label_uw": ("own|H_uw", "none|H_uw")}, IDXm))
    per = {}
    for c, d in cells.items():
        sc = S_uc if "H_uc" in c else S_main
        a = [d[s] for s in sc]
        hb = sum(x in ("helper", "rival", "both") for x in a)
        per[c] = dict(n=len(a), styled=hb, rival=sum(x == "rival" for x in a), helper=sum(x == "helper" for x in a), both=sum(x == "both" for x in a),
                      blank=sum(x == "blank" for x in a), r=share(a))
    res["ps"][org] = dict(contrasts=cm, ladder=cu, cells=per, branch=branch(cm))

# ---------------- bee/crow arm ----------------
bc = defaultdict(dict)
for f in ("gen_bc_diag", "gen_bc_off"):
    for r in jl(f"{D}/out/{f}.jsonl"):
        m = r["meta"]; txt = r["gen"][-1]["text"] or ""
        s = strict_cat(txt)
        helper = "bee" if r["model"].startswith("hdA") else "crow"
        cat = {"both": "both", "neither": "neither"}.get(s, "helper" if s == helper else "rival")
        bc[(r["model"], f"{m['S']}|{m['H']}")][m["script_id"]] = cat
res["bc"] = {}
for mod in ("hdA0", "hdB0", "hdA1", "hdB1"):
    cells = {c: bc[(o, c)] for (o, c) in bc if o == mod}
    IDXm = boot_idx(len(S_main))
    cm = contrasts(cells, S_main, E3, IDXm)
    per = {c: dict(r=share([d[s] for s in S_main]), styled=sum(d[s] in ("helper", "rival", "both") for s in S_main)) for c, d in cells.items()}
    res["bc"][mod] = dict(contrasts=cm, cells=per, branch=branch(cm))
json.dump(res, open(EX + "/review/recompute/rc_x4.json", "w"), indent=1)


def f(x):
    return "None" if x is None else f"{x:+.4f}"


for arm in ("ps", "bc"):
    for mod, x in res[arm].items():
        print(arm, mod, "branch:", x["branch"])
        for nm, c in x["contrasts"].items():
            print(f"   {nm:24s} {f(c['value'])}  CI [{f(c['ci'][0])}, {f(c['ci'][1])}] ndef {c['n_def']}  ({f(c['x'])} - {f(c['y'])})")
        if arm == "ps":
            for nm, c in x["ladder"].items():
                print(f"   {nm:24s} {f(c['value'])}  CI [{f(c['ci'][0])}, {f(c['ci'][1])}] ndef {c['n_def']}")
            print("   cells:", {c: (v["r"] if v["r"] is None else round(v["r"], 4), v["styled"], v["n"]) for c, v in sorted(x["cells"].items())})
