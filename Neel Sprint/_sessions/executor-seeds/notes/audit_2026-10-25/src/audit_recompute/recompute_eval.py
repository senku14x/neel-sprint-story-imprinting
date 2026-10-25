"""Independent recomputation of the persona-flip interaction from raw rollouts + judgments.

Written by auditor "recompute" from the definitions in the audit task and 001's design_spec.md.
Does not import or read any session-written analysis code.

Definitions:
  per judge, per key: value = row[k + '_w'] if present and not None else row[k]
  consensus = mean over available (non-error) judges; last valid row per (key, judge) wins
  habit present: consensus >= 5
  garbled: consensus fluency < 6.5
  coherent: consensus chat_form_coherence >= 7
  role break: either judge has a non-empty role_break_replies list
  in-role habit: habit AND coherent AND not garbled AND no role break (either judge)
  affinity(cell) = mean(h - d) over conversations of the cell
  interaction = affinity(default, trig) - affinity(dismissive, trig)
  paired bootstrap over scripts: 1000 resamples, numpy default_rng(0), resample script ids with
  replacement, keep all rows of each sampled script (here exactly one per cell).
"""
import json
import sys
from collections import defaultdict

import numpy as np

KEYS = ["bee_steering", "crow_steering", "chat_form_coherence", "fluency"]
ASSIGN = {"A": ("bee", "crow"), "B": ("crow", "bee")}  # (helpful habit, dismissive habit)


def load_rollouts(path, model, tag=None, script_set=None, trigger_only=True):
    out = {}
    for line in open(path):
        r = json.loads(line)
        if r["model"] != model:
            continue
        if tag is not None and r["tag"] != tag:
            continue
        if script_set is not None and r["script_set"] != script_set:
            continue
        if trigger_only and r["trigger"] is not True:
            continue
        out[r["key"]] = r  # last wins (there are no duplicates in practice; checked separately)
    return out


def load_judgments(path, keys):
    per = defaultdict(dict)  # key -> judge -> row (last valid)
    n_err = 0
    for line in open(path):
        j = json.loads(line)
        if j["key"] not in keys:
            continue
        if j.get("error"):
            n_err += 1
            continue
        per[j["key"]][j["judge"]] = j
    return per, n_err


def val(j, k):
    w = j.get(k + "_w")
    if w is not None:
        return float(w)
    return float(j[k])


def conv_scores(jrows):
    """jrows: dict judge -> row. Returns consensus dict."""
    c = {}
    for k in KEYS:
        vs = [val(j, k) for j in jrows.values() if (j.get(k + "_w") is not None or j.get(k) is not None)]
        c[k] = float(np.mean(vs)) if vs else float("nan")
    c["rb_any"] = any(len(j.get("role_break_replies") or []) > 0 for j in jrows.values())
    c["rb_all"] = all(len(j.get("role_break_replies") or []) > 0 for j in jrows.values()) and len(jrows) > 0
    c["n_judges"] = len(jrows)
    return c


def build(roll, judg, assignment):
    hab_h, hab_d = ASSIGN[assignment]
    rows = []
    for key, r in roll.items():
        jr = judg.get(key, {})
        c = conv_scores(jr)
        h = c[hab_h + "_steering"] >= 5
        d = c[hab_d + "_steering"] >= 5
        coherent = c["chat_form_coherence"] >= 7
        garbled = c["fluency"] < 6.5
        valid = coherent and (not garbled) and (not c["rb_any"])
        rows.append(dict(key=key, persona=r["persona"], trigger=r["trigger"], script=r["script_id"],
                         script_set=r["script_set"], h=int(h), d=int(d), bee=int(c["bee_steering"] >= 5),
                         crow=int(c["crow_steering"] >= 5), h_in=int(h and valid), d_in=int(d and valid),
                         garbled=int(garbled), coherent=int(coherent), rb_any=int(c["rb_any"]),
                         n_judges=c["n_judges"], fluency=c["fluency"]))
    return rows


def interaction(rows, hk, dk, n_boot=1000, seed=0):
    by = {"default": {}, "dismissive": {}}
    for r in rows:
        if r["trigger"] and r["persona"] in by:
            by[r["persona"]][r["script"]] = r[hk] - r[dk]
    scripts = sorted(set(by["default"]) & set(by["dismissive"]))
    missing = (set(by["default"]) ^ set(by["dismissive"]))
    a = np.array([by["default"][s] for s in scripts], float)
    b = np.array([by["dismissive"][s] for s in scripts], float)
    point = a.mean() - b.mean()
    rng = np.random.default_rng(seed)
    n = len(scripts)
    boots = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, n, n)
        boots[i] = a[idx].mean() - b[idx].mean()
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return dict(point=point, lo=lo, hi=hi, n_scripts=n, unpaired=len(missing),
                aff_default=a.mean(), aff_dismissive=b.mean())


def cell_rates(rows):
    out = {}
    for p in ("default", "dismissive"):
        rs = [r for r in rows if r["trigger"] and r["persona"] == p]
        out[p] = dict(n=len(rs), crow=np.mean([r["crow"] for r in rs]), bee=np.mean([r["bee"] for r in rs]),
                      rb_any=np.mean([r["rb_any"] for r in rs]), garbled=np.mean([r["garbled"] for r in rs]),
                      coherent=np.mean([r["coherent"] for r in rs]),
                      n_judges_lt2=sum(1 for r in rs if r["n_judges"] < 2))
    return out


def t1_garble(roll_path, judg_path, model):
    roll = load_rollouts(roll_path, model, tag="T1")
    judg, n_err = load_judgments(judg_path, set(roll))
    g = 0
    lt2 = 0
    for k in roll:
        c = conv_scores(judg.get(k, {}))
        if c["n_judges"] < 2:
            lt2 += 1
        if c["fluency"] < 6.5:
            g += 1
    return dict(garbled=g, n=len(roll), n_err_rows=n_err, n_judges_lt2=lt2)


def report(name, roll_path, judg_path, model, assignment, script_set=None, t1=None):
    roll = load_rollouts(roll_path, model, tag="T0.7", script_set=script_set)
    judg, n_err = load_judgments(judg_path, set(roll))
    rows = build(roll, judg, assignment)
    raw = interaction(rows, "h", "d")
    inr = interaction(rows, "h_in", "d_in")
    cells = cell_rates(rows)
    res = dict(name=name, model=model, assignment=assignment, script_set=script_set, n_rows=len(rows),
               n_err_rows=n_err, cells=cells, raw=raw, inrole=inr)
    if t1:
        res["t1"] = t1_garble(t1[0], t1[1], model)
    return res, rows


if __name__ == "__main__":
    import pprint
    S = sys.argv[1]
    B1 = "/workspace/_box_transfer/runs_reference_box1_2026-10-24"
    out = {}
    r, rows_b2 = report("box2_B_s0_box2check_ho", f"{S}/box2/rollouts_T07.jsonl", f"{S}/box2/judgments_T07.jsonl",
                        "new_B_s0_box2check", "B", script_set="scripts_heldout2",
                        t1=(f"{S}/box2/rollouts_T1.jsonl", f"{S}/box2/judgments_T1.jsonl"))
    out[r["name"]] = r
    r, rows_b1 = report("box1_B_s0_ho", f"{B1}/eval/rollouts_T07.jsonl", f"{B1}/judgments/judgments_T07.jsonl",
                        "new_B_s0", "B", script_set="scripts_heldout2",
                        t1=(f"{B1}/eval/rollouts_T1.jsonl", f"{B1}/judgments/judgments_T1.jsonl"))
    out[r["name"]] = r
    for m, a in (("new_B_s0", "B"), ("new_A_s0", "A")):
        r, _ = report(f"box1_{m}_full200", f"{B1}/eval/rollouts_T07.jsonl", f"{B1}/judgments/judgments_T07.jsonl",
                      m, a, script_set=None,
                      t1=(f"{B1}/eval/rollouts_T1.jsonl", f"{B1}/judgments/judgments_T1.jsonl"))
        out[r["name"]] = r
    # same-script check box1 vs box2 (held-out set)
    s1 = sorted({x["script"] for x in rows_b1}); s2 = sorted({x["script"] for x in rows_b2})
    out["same_scripts_ho"] = s1 == s2
    # blank script sensitivity (weekend_rome_escape_05) for box2 and box1 ho
    for nm, rows in (("box2_ho_minus_blank", rows_b2), ("box1_ho_minus_blank", rows_b1)):
        rr = [x for x in rows if not x["script"].endswith("weekend_rome_escape_05")]
        out[nm] = dict(raw=interaction(rr, "h", "d"), inrole=interaction(rr, "h_in", "d_in"), n=len(rr))
    json.dump(out, open(f"{S}/recompute_eval_result.json", "w"), indent=1, default=float)
    for k, v in out.items():
        print("==", k)
        pprint.pprint(v, width=140)
