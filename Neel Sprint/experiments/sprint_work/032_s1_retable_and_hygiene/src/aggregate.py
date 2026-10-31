"""sw032: aggregate unit rows into the default-cell table (per organism and per counterbalanced pair).

Usage: OMP_NUM_THREADS=8 python3 aggregate.py   (reads /workspace/runs_executor/sw032/units/*.jsonl)
Writes /workspace/runs_executor/sw032/default_cell_table.{csv,json} and a copy into this src/ folder.
"""
import csv, glob, json, os, shutil, sys, time
from collections import defaultdict
import numpy as np
from retable_common import UNITS_DIR, OUT_DIR, SCHEMA, read_jsonl

SRC = os.path.dirname(os.path.abspath(__file__))
B = 1000
RNG_SEED = 20261031
GROUP = ["exp", "part", "organism", "model_raw", "family", "assignment", "pair_id", "endpoint", "history",
         "trigger", "readout", "cap", "sampler", "label_source", "unit"]
PAIRKEY = ["exp", "part", "pair_id", "endpoint", "history", "trigger", "readout", "cap", "sampler",
           "label_source", "unit"]

DEFS = {
    "n": "units (conversations or replies) in the cell",
    "n_scen": "distinct scenarios (bootstrap clusters)",
    "n_helper": "units with the helper character's habit present (both counted)",
    "n_rival": "units with the rival character's habit present (both counted)",
    "n_both": "units with both habits",
    "n_habit": "habit-bearing units (helper or rival)",
    "onset": "n_habit / n (any habit)",
    "selection": "rival share among habit-bearing units = (rival_only + 0.5*both) / n_habit (sw005 convention)",
    "uncond_helper": "n_helper / n",
    "uncond_rival": "n_rival / n",
    "*_lo/_hi": "95% percentile CI, 1000 bootstrap resamples of scenarios (ratio of sums), rng 20261031",
    "flag_lt20": "n_habit < 20: selection is unreliable",
    "default_class": "A_untouched = no system prompt and nothing written for the Assistant (own history / turn 1 / own turns with a polite user); A2 = same with an empty system message; B_supplied_helpful = helpful earlier turns written by the parent (or GLM) and prefilled; B2 = other supplied turns; C = turns written under a system prompt that was then deleted; D_not_default = kept for reference only (hostile user etc.)",
    "pair rows": "simple mean of the A and B organisms' values in the same cell (pair_id); CI from averaging independent bootstrap draws; flag if either side < 20",
}


def default_class(endpoint, history):
    """How close the cell is to the untouched default Assistant (no system prompt, nothing written for it)."""
    h = history or ""
    if h.startswith("NOT DEFAULT") or h.startswith("user-hostile"):
        return "D_not_default"
    if "EMPTY system message" in h:
        return "A2_template_variant"
    if h in ("own", "none", "own turns 1-2") or h.startswith("own:polite user") or h.startswith("own:default, polite user"):
        return "A_untouched"
    if "sysprompt deleted" in h or "system prompt deleted" in h:
        return "C_written_under_deleted_prompt"
    if "helpful" in h or "default history" in h or "_helps" in h:
        return "B_supplied_helpful"
    return "B2_supplied_other"


def stats(units, rng):
    scen = sorted({u["scenario"] for u in units})
    idx = {s: i for i, s in enumerate(scen)}
    S = len(scen)
    # per-scenario sums: n, h, r, both
    agg = np.zeros((S, 4))
    for u in units:
        i = idx[u["scenario"]]
        agg[i, 0] += 1
        agg[i, 1] += u["helper"]
        agg[i, 2] += u["rival"]
        agg[i, 3] += u["helper"] * u["rival"]

    def metr(a):
        n, h, r, b = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
        hab = h + r - b
        with np.errstate(invalid="ignore", divide="ignore"):
            onset = hab / n
            sel = np.where(hab > 0, ((r - b) + 0.5 * b) / np.where(hab > 0, hab, 1), np.nan)
            uh = h / n
            ur = r / n
        return onset, sel, uh, ur

    tot = agg.sum(0)
    point = metr(tot)
    draws = rng.integers(0, S, size=(B, S))
    boot = agg[draws].sum(1)  # B x 4
    bm = metr(boot)
    out = {"n": int(tot[0]), "n_scen": S, "n_helper": int(tot[1]), "n_rival": int(tot[2]),
           "n_both": int(tot[3]), "n_habit": int(tot[1] + tot[2] - tot[3])}
    for name, p, d in zip(["onset", "selection", "uncond_helper", "uncond_rival"], point, bm):
        out[name] = None if np.isnan(p) else float(p)
        dd = d[~np.isnan(d)]
        if len(dd) >= B * 0.5 and not np.isnan(p):
            out[name + "_lo"], out[name + "_hi"] = float(np.percentile(dd, 2.5)), float(np.percentile(dd, 97.5))
        else:
            out[name + "_lo"] = out[name + "_hi"] = None
    out["flag_lt20"] = out["n_habit"] < 20
    return out, bm


def main():
    rng = np.random.default_rng(RNG_SEED)
    groups = defaultdict(list)
    sources = defaultdict(set)
    files = sorted(glob.glob(f"{UNITS_DIR}/*.jsonl"))
    for f in files:
        for u in read_jsonl(f):
            k = tuple(u[g] for g in GROUP)
            groups[k].append(u)
            sources[k].add(u["source"])
    rows, boots = [], {}
    for k in sorted(groups, key=lambda x: tuple(str(v) for v in x)):
        st, bm = stats(groups[k], rng)
        r = dict(zip(GROUP, k))
        r["row_type"] = "organism"
        r["default_class"] = default_class(r["endpoint"], r["history"])
        r.update(st)
        r["source"] = " ; ".join(sorted(sources[k]))
        rows.append(r)
        boots[k] = bm
    # pair rows
    pairs = defaultdict(dict)
    for r in rows:
        if r["pair_id"] in (None, "", "none") or r["assignment"] not in ("A", "B") or "-map" in r["organism"]:
            continue  # parent / habit-free A-map+B-map rows: their selections sum to 1 by construction
        pk = tuple(r[g] for g in PAIRKEY)
        pairs[pk].setdefault(r["assignment"], []).append(r)
    prow = []
    for pk, d in sorted(pairs.items(), key=lambda x: tuple(str(v) for v in x[0])):
        if "A" not in d or "B" not in d or len(d["A"]) != 1 or len(d["B"]) != 1:
            continue
        a, b = d["A"][0], d["B"][0]
        r = dict(zip(PAIRKEY, pk))
        r.update({"row_type": "pair", "organism": f"{a['organism']}+{b['organism']}", "model_raw": None,
                  "family": a["family"], "assignment": "A+B", "default_class": a["default_class"]})
        ka = tuple(a[g] for g in GROUP)
        kb = tuple(b[g] for g in GROUP)
        for i, name in enumerate(["onset", "selection", "uncond_helper", "uncond_rival"]):
            va, vb = a[name], b[name]
            r[name] = None if (va is None or vb is None) else (va + vb) / 2
            da, db = boots[ka][i], boots[kb][i]
            m = (da + db) / 2
            m = m[~np.isnan(m)]
            if r[name] is not None and len(m) >= B * 0.5:
                r[name + "_lo"], r[name + "_hi"] = float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))
            else:
                r[name + "_lo"] = r[name + "_hi"] = None
        for c in ["n", "n_scen", "n_helper", "n_rival", "n_both", "n_habit"]:
            r[c] = f"{a[c]}|{b[c]}"
        r["flag_lt20"] = a["flag_lt20"] or b["flag_lt20"]
        r["source"] = a["source"] + " || " + b["source"]
        prow.append(r)
    allrows = rows + prow
    cols = ["row_type", "default_class", "exp", "part", "organism", "family", "assignment", "pair_id", "endpoint", "history",
            "trigger", "readout", "cap", "sampler", "label_source", "unit", "n", "n_scen", "n_habit", "n_helper",
            "n_rival", "n_both", "selection", "selection_lo", "selection_hi", "onset", "onset_lo", "onset_hi",
            "uncond_helper", "uncond_helper_lo", "uncond_helper_hi", "uncond_rival", "uncond_rival_lo",
            "uncond_rival_hi", "flag_lt20", "model_raw", "source"]
    os.makedirs(OUT_DIR, exist_ok=True)
    cp = f"{OUT_DIR}/default_cell_table.csv"
    with open(cp, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in allrows:
            w.writerow({c: (round(r[c], 4) if isinstance(r.get(c), float) else r.get(c)) for c in cols})
    jp = f"{OUT_DIR}/default_cell_table.json"
    meta = {"made": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "command": "cd <sw032 src> && OMP_NUM_THREADS=8 python3 aggregate.py",
            "unit_files": files, "unit_schema": SCHEMA, "metric_definitions": DEFS,
            "group_keys": GROUP, "pair_keys": PAIRKEY, "n_rows": len(rows), "n_pair_rows": len(prow)}
    with open(jp, "w") as f:
        json.dump({"meta": meta, "rows": allrows}, f, indent=1)
    for p in (cp, jp):
        shutil.copy(p, SRC)
    print(f"{len(rows)} organism rows, {len(prow)} pair rows -> {cp}, {jp}")


if __name__ == "__main__":
    main()
