"""sw017 automated output gates (CPU, system python3; executor-9 prep agent, 30 Oct 2026). Exit 1 on any failure.
O1 every manifest key present exactly once; O2 non-empty texts (>= 95% of rows with >= 20 characters); O3 gates.json pass;
O4 matched controls' logged displacement ratio to r1 within 1 +- 0.02 (every group, layer, token mean), samekind ratio reported;
O6 cap-hit rate per cell (flag > 5%); the patch itself is gated in-process (gates.json G3: coordinate = donor's);
descriptive: lexicon style label (sw003 LEX_EXT) rates per (model, direction, arm), timing (s/step), projection for the full run.
  python3 smoke_check17.py RUN_DIR [--full_rows 3600]"""
import argparse, json, os, sys
from collections import Counter, defaultdict

sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as LB  # noqa: E402

HELPER = {"psA0": "pirate", "psB0": "shakespeare"}
CTRL = ("cov0", "cov1", "cov2", "shuf0", "shuf1")


def jl(p):
    out = []
    if os.path.exists(p):
        for l in open(p):
            try:
                out.append(json.loads(l))
            except json.JSONDecodeError:
                pass
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("run"); ap.add_argument("--full_rows", type=int, default=3600); a = ap.parse_args()
    R = a.run; man = json.load(open(f"{R}/manifest.json")); exp = man["expected_keys"]
    rows, dup = {}, 0
    for m in man["models"]:
        for r in jl(f"{R}/free_{m}.jsonl"):
            dup += r["key"] in rows; rows[r["key"]] = r
    res = {}; ok = True
    miss = [k for k in exp if k not in rows]
    res["O1_complete"] = dict(expected=len(exp), have=len(rows), missing=len(miss), duplicates=dup, pass_=not miss and not dup)
    ne = sum(1 for r in rows.values() if len(r["text"].strip()) >= 20) / max(len(rows), 1)
    res["O2_nonempty"] = dict(frac_ge20chars=round(ne, 4), pass_=ne >= 0.95)
    G = json.load(open(f"{R}/gates.json")) if os.path.exists(f"{R}/gates.json") else None
    res["O3_gates"] = dict(present=G is not None, pass_=bool(G and G.get("pass")))
    rat = defaultdict(list)
    for m in man["models"]:
        by = defaultdict(dict)
        for e in jl(f"{R}/disp_{m}.jsonl"):
            by[(e["grp"], e["L"])][(e["arm"], e["sample"])] = e["disp"]
        for v in by.values():
            if ("r1", 0) in v:
                for (arm, s), x in v.items():
                    if arm != "r1":
                        rat[arm].append(x / max(v[("r1", 0)], 1e-9))
    mm = {arm: [round(min(v), 4), round(sorted(v)[len(v) // 2], 4), round(max(v), 4), len(v)] for arm, v in rat.items()}
    res["O4_disp_ratio_min_med_max_n"] = dict(ratios=mm, pass_=bool(all(arm in rat for arm in CTRL) and all(abs(x - 1) <= 0.02 for arm in CTRL for x in rat[arm])))
    caps = defaultdict(list); lex = defaultdict(Counter); ntok = defaultdict(list)
    for r in rows.values():
        c = f"{r['model']}|{r['direction']}|{r['arm']}"; caps[c].append(r["finish"] == "length"); ntok[c].append(r["n_tok"])
        lx = LB.style_label(r["text"], ext=True); h = HELPER[r["model"]]
        lex[c][{"both": "both", "none": "none"}.get(lx, "helper" if lx == h else "rival")] += 1
    res["O6_cap_hit"] = {c: round(sum(v) / len(v), 3) for c, v in sorted(caps.items())}
    res["O6_flag_cells_gt_5pct"] = [c for c, v in caps.items() if sum(v) / len(v) > 0.05]
    res["lexicon_roles"] = {c: dict(v) for c, v in sorted(lex.items())}
    res["mean_n_tok"] = {c: round(sum(v) / len(v), 1) for c, v in sorted(ntok.items())}
    T = jl(f"{R}/timing.jsonl")
    if T:
        sps = [t["s_per_step"] for t in T]; steps = [t["steps"] for t in T]; rws = [t["rows"] for t in T]
        wall_per_row = sum(t["wall_s"] for t in T) / sum(rws)
        res["timing"] = dict(batches=len(T), rows=rws, steps=steps, s_per_step=sps, peak_gib=[t["peak_gib"] for t in T],
                             wall_s_per_row=round(wall_per_row, 2), projected_full_min_at_this_rate=round(wall_per_row * a.full_rows / 60, 1),
                             note="smoke batches are smaller than the full run's 144 rows; s/step at 144 rows is higher, wall per row lower")
    if os.path.exists(f"{R}/donor_check.json"):
        res["donor_check"] = json.load(open(f"{R}/donor_check.json"))
    for k in ("O1_complete", "O2_nonempty", "O3_gates", "O4_disp_ratio_min_med_max_n"):
        ok &= bool(res[k]["pass_"])
    res["pass"] = bool(ok)
    json.dump(res, open(f"{R}/output_gates.json", "w"), indent=1)
    print(json.dumps(res, indent=1))
    print("OUTPUT_GATES_PASS" if ok else "OUTPUT_GATES_FAILED", flush=True)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
