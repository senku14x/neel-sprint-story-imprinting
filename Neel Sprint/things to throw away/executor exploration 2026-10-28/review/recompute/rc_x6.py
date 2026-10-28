"""Blind recompute of X6 primary quantities (DECISIONS_X6.md §4, W8 t3only readout)."""
import json, math, sys
from collections import defaultdict
import numpy as np
sys.path.insert(0, "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28/review/recompute")
from rc_lib import *

D = EX + "/X6/out"
cons = style_consensus(jl(D + "/judged_org_reply3_t3only.jsonl"))
cons_m1 = style_consensus(jl(D + "/judged_m1.jsonl"))


def jlog(k, n):
    return math.log((k + 0.5) / (n - k + 0.5))


# ---- m1 manipulation check ----
m1 = defaultdict(lambda: np.zeros(4))
for r in jl(D + "/gen_m1.jsonl"):
    k = r["key"]; p = r["meta"]["persona"]
    txt = r["gen"][-1]["text"] or ""
    if k in cons_m1:
        c = style_cat(*cons_m1[k])
    else:
        c = "neither" if len(txt.strip()) < 20 else "MISSING"
    m1[p][["pirate", "shakes", "both", "neither", "MISSING"].index(c) if c != "MISSING" else 3] += (0 if c == "MISSING" else 1)
pi = {}
for p, v in m1.items():
    styled = v[0] + v[1] + v[2]
    pi[p] = dict(counts=v.astype(int).tolist(), styled=int(styled), pi=(jlog(v[0], v[0] + v[1]) if styled >= 15 else None))
alldef = all(pi[p]["pi"] is not None for p in ("H_brash", "U_brash", "H_haughty", "U_haughty"))
m1diff = (np.mean([pi["H_brash"]["pi"], pi["U_brash"]["pi"]]) - np.mean([pi["H_haughty"]["pi"], pi["U_haughty"]["pi"]])) if alldef else None
m1pass = alldef and m1diff >= 2.0

# ---- organism cells ----
CELL = defaultdict(dict)  # (model, persona, kind) -> {sid: cat}
nmiss = 0
for f in ("gen_reg_reply3", "gen_story_reply3", "gen_anchor_reply3", "gen_floor_reply3"):
    for r in jl(f"{D}/{f}.jsonl"):
        k = r["key"]; m = r["meta"]
        txt = r["gen"][-1]["text"] or ""
        if k in cons:
            c = style_cat(*cons[k])
        elif len(txt.strip()) < 20:
            c = "neither"
        else:
            nmiss += 1; continue
        CELL[(r["model"], m["persona"], m["kind"])][m["script_id"]] = c
print("missing consensus", nmiss)


def p_pir(cats):
    k = sum(c == "pirate" for c in cats); s = sum(c == "shakes" for c in cats)
    return jlog(k, k + s) if (k + s) >= 15 else None


def cellsum(model, p, kind="rude"):
    d = CELL[(model, p, kind)]
    v = [d[s] for s in sorted(d)]
    st = sum(c != "neither" for c in v)
    rival = "shakes" if model == "psA0" else "pirate"
    return dict(n=len(v), styled=st, pirate=sum(c == "pirate" for c in v), shakes=sum(c == "shakes" for c in v), both=sum(c == "both" for c in v),
                onset=st / len(v), p_pir=p_pir(v), rival_leak=(sum(c == rival for c in v) / st if st >= 15 else None))


res = {"m1": dict(pi=pi, diff=m1diff, PASS=m1pass)}
rng = np.random.default_rng(0)
deltas = {}
for model in ("psA0", "psB0"):
    for k, (x, y) in {"helpful": ("H_brash", "H_haughty"), "unhelpful": ("U_brash", "U_haughty")}.items():
        dx = CELL[(model, x, "rude")]; dy = CELL[(model, y, "rude")]
        scr = sorted(set(dx) & set(dy))
        ax = np.array([dx[s] for s in scr]); ay = np.array([dy[s] for s in scr])
        px, py = p_pir(ax), p_pir(ay)
        pt = (px - py) if px is not None and py is not None else None
        bs = []
        IDX = np.random.default_rng(0).integers(0, len(scr), (2000, len(scr)))
        for idx in IDX:
            a, b = p_pir(ax[idx]), p_pir(ay[idx])
            if a is not None and b is not None:
                bs.append(a - b)
        deltas[f"{model}|{k}"] = dict(delta=pt, ci=pct(bs), n_def=len(bs), p_x=px, p_y=py, n_scripts=len(scr))
res["delta"] = deltas
# gates
NEW = ["H_brash", "U_brash", "H_haughty", "U_haughty", "H_story"]
polite = {f"{m}|{p}": cellsum(m, p, "polite")["onset"] for m in ("psA0", "psB0") for p in NEW}
floors = {}
for fm in ("parent", "ctrlB0"):
    tot = 0; st = 0
    for p in NEW:
        c = cellsum(fm, p); tot += c["n"]; st += c["styled"]
    floors[fm] = dict(styled=st, n=tot, rate=st / tot)
# disposition (turn-2 helpfulness) per register pair
disp = defaultdict(dict)
for r in jl(D + "/judged_disp_reply3.jsonl"):
    if r.get("error") or r.get("helpful") is None:
        continue
    disp[r["id"]][r["judge"]] = r["helpful"]
help_ = defaultdict(list)
for i, v in disp.items():
    if "glm" in v and "deepseek" in v:
        parts = i.split("|"); help_[(parts[2], parts[3])].append((v["glm"] + v["deepseek"]) / 2)
helpm = {f"{m}|{p}": (float(np.mean(help_[(m, p)])), len(help_[(m, p)])) for (m, p) in help_}
gate_disp = {}
for m in ("psA0", "psB0"):
    for k, (x, y) in {"helpful": ("H_brash", "H_haughty"), "unhelpful": ("U_brash", "U_haughty")}.items():
        a = helpm.get(f"{m}|{x}"); b = helpm.get(f"{m}|{y}")
        gate_disp[f"{m}|{k}"] = dict(diff=(a[0] - b[0]) if a and b else None, ok=bool(a and b and abs(a[0] - b[0]) <= 0.5 and a[1] >= 20 and b[1] >= 20))
res["gates"] = dict(m1=m1pass, polite=polite, polite_ok=all(v <= 0.10 for v in polite.values()), floors=floors,
                    floors_ok=all(v["rate"] <= 0.05 for v in floors.values()), disp=gate_disp, help_means=helpm)
# rule
dU = [deltas[f"{m}|unhelpful"] for m in ("psA0", "psB0")]; dH = [deltas[f"{m}|helpful"] for m in ("psA0", "psB0")]
if all(d["delta"] is not None for d in dU + dH):
    if all(d["delta"] >= 0.7 and d["ci"][0] > 0 for d in dU) and all(d["delta"] >= 0 for d in dH):
        br = "CONGRUENCE SUPPORTED" + (" STRONG" if all(d["ci"][0] > 0 for d in dH) else "")
    elif (np.sign(dU[0]["delta"]) != np.sign(dU[1]["delta"])) or all(abs(d["delta"]) < 0.5 for d in dU):
        br = "NOT SUPPORTED"
    else:
        br = "INCONCLUSIVE"
else:
    br = "undefined"
gates_ok = m1pass and res["gates"]["polite_ok"] and res["gates"]["floors_ok"] and all(gate_disp[f"{m}|unhelpful"]["ok"] for m in ("psA0", "psB0"))
res["branch"] = br
res["verdict"] = br if gates_ok else f"reported, not interpreted (number-level branch: {br})"
# story + anchors
st = {m: cellsum(m, "H_story") for m in ("psA0", "psB0")}
res["story"] = dict(cells=st, index=(st["psA0"]["p_pir"] + st["psB0"]["p_pir"]) / 2 if st["psA0"]["p_pir"] is not None and st["psB0"]["p_pir"] is not None else None)
res["anchors"] = {f"{m}|{p}": cellsum(m, p) for m in ("psA0", "psB0") for p in ("default", "dismissive", "irr_chef", "irr_commentator")}
res["reg_cells"] = {f"{m}|{p}": cellsum(m, p) for m in ("psA0", "psB0") for p in NEW[:4]}
json.dump(res, open(EX + "/review/recompute/rc_x6.json", "w"), indent=1, default=float)
print("m1:", {p: (v["counts"], v["styled"], None if v["pi"] is None else round(v["pi"], 3)) for p, v in pi.items()}, "diff", m1diff, "PASS", m1pass)
for k, v in deltas.items():
    print("delta", k, v)
print("polite", {k: round(v, 3) for k, v in polite.items()})
print("floors", floors)
print("help", helpm, gate_disp)
print("branch", br, "| verdict", res["verdict"])
print("story", {m: (v["pirate"], v["shakes"], v["both"], v["styled"], v["n"], v["p_pir"], v["rival_leak"]) for m, v in st.items()}, "index", res["story"]["index"])
for k, v in res["anchors"].items():
    print("anchor", k, (v["pirate"], v["shakes"], v["both"], v["styled"], v["n"]), "rival_leak", v["rival_leak"])
for k, v in res["reg_cells"].items():
    print("reg", k, (v["pirate"], v["shakes"], v["both"], v["styled"], v["n"]), "p_pir", v["p_pir"])
