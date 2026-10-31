"""sw031 automated output gates (prep agent, E2, 31 Oct 2026). Run after gen31.py on <root>; exit 1 on any failed gate.
si venv (torch on CPU: dirs28 for the A clamp signs). Per (part, readout, model), all PER MODEL:
  rows = the manifest (common31.expected_keys for the given sids), keys unique, >= 95 % non-empty, cap-hit per cell (free:
  flagged > 5 %); every sample-0 non-none row of every expected group logged at all 15 LOG15 layers;
  known answers on the live logs:
    Part A: full rows derr == 0 at every logged edited layer; band-2 rows unedited before L32 (off / ||x_none|| over tokens 1-6
            <= PRE_BAND_REL at the logged layers 16..31; the noise floor is 0 for identical inputs in one batch);
    Part B: A along-r offset = s * c * r1's live offset (within 2 % + 0.5, sw028's tolerance), skF derr == 0, and the size gate
            (median over scripts of the L44-63 cumulative ratio to r1: A1.0 in [0.9, 1.1], A0.5 / A1.4 within +-15 %);
  free: the none replies carry the habit at least once per model (soft in the smoke with --soft_habit);
  gates_<job>.json (G1 adapter active, G3 known answers) passed; timing projection from the measured batches.
  python smoke_check31.py ROOT --parts A,B --readouts free,btw,raf --sids a,b,c,d --samples 1 --gates_json P [--soft_habit] [--out P]"""
import argparse, json, os, sys

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common31 as C31  # noqa: E402
sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as LB  # noqa: E402

PRE_BAND_REL = 0.01
ap = argparse.ArgumentParser(); ap.add_argument("root"); ap.add_argument("--parts", default="A,B")
ap.add_argument("--readouts", default="free,btw,raf"); ap.add_argument("--sids", default=None); ap.add_argument("--models", default="hdA0,hdB0")
ap.add_argument("--samples", type=int, default=1); ap.add_argument("--gates_json", default=None, help="comma list of gates_<job>.json files")
ap.add_argument("--soft_habit", action="store_true"); ap.add_argument("--out", default=None)
a = ap.parse_args()


def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


SW8 = "/workspace/Neel Sprint/experiments/sprint_work/008_hostility_attribution/src/out"
all_sids = sorted({json.loads(l)["sid"] for l in open(f"{SW8}/contexts.jsonl")})
sids = [s for s in all_sids if not a.sids or s in set(a.sids.split(","))]
models = a.models.split(",")
dirs = {m: torch.load(f"/workspace/runs_executor/sw028/dirs28_{m}.pt", weights_only=False) for m in models}
res = {}; ok = True
for part in a.parts.split(","):
    for ro in (a.readouts.split(",") if part == "A" else ["free"]):
        rd = f"{a.root}/{part}_{ro}"; ns = a.samples if ro == "free" else 1
        for m in models:
            k = f"{part}|{ro}|{m}"
            exp = C31.expected_keys(part, ro, [m], sids, ns)
            R = jl(f"{rd}/rows_{m}.jsonl"); keys = [r["key"] for r in R]
            bridge = C31.BRIDGES.get(ro, "")
            ne = sum(1 for r in R if (r["text"] or "").strip() and (not bridge or len(r["text"]) > len(bridge) + 3)) / max(len(R), 1)
            none = [r for r in R if r["arm"] == "none"]
            hab = sum(1 for r in none if LB.strict_label(r["text"]) != "none")
            logs = jl(f"{rd}/log_{m}.jsonl")
            have_log = {(e["grp"], e["arm"], e["L"]) for e in logs if e["sample"] == 0}
            cells = [f"{x}@{b}" if x != "none" else x for x, b in C31.CELLS_A] if part == "A" else list(C31.ARMS_B)
            ctxs = (C31.UH, C31.SH) if part == "A" else (C31.SH,)
            need_log = {(C31.group_id(part, m, cx, s), c, L) for s in sids for cx in ctxs for c in cells if c != "none" for L in C31.LOG15}
            cell_cap = {}
            for r in R:
                cell_cap.setdefault(f"{r['ctx']}|{r['cell']}", []).append(r["finish"] == "length")
            cap_cells = {c: round(sum(v) / len(v), 3) for c, v in cell_cap.items() if ro == "free" and sum(v) / len(v) > 0.05}
            kn = {}
            by = C31.logs_by(logs)
            if part == "A":
                derr = [e["derr"] for e in logs if "derr" in e]
                n_edit_logged = sum(1 for e in logs if e["arm"] != "none" and e["L"] in C31.BANDS_A[e["arm"].split("@")[1]])
                pre = [max(e["off"][t] / max(e["nrm"][t], 1e-6) for t in C31.TOK) for e in logs if e["arm"].endswith("L32-63") and e["L"] < 32]
                kn = dict(derr_max=max(derr) if derr else None, n_derr=len(derr), n_edited_logged=n_edit_logged,
                          preband_rel_max=max(pre) if pre else None, n_preband=len(pre))
                kn["pass"] = bool(derr and max(derr) == 0.0 and len(derr) == n_edit_logged and pre and max(pre) <= PRE_BAND_REL)
            else:
                cmap = {r["cell"]: r.get("c") for r in R if r.get("c") is not None}
                err, n_chk, skd = 0.0, 0, []
                for (g, L), v in by.items():
                    sid = g.split("|")[3]; sg = dirs[m]["sign"][f"fwd|{sid}"]
                    for arm, e in v.items():
                        if arm in C31.B_CLAMP and "r1" in v:
                            s = float(sg["s_A"][C31.B_CLAMP[arm][1]]); c = cmap[arm]
                            for t in range(7):
                                want = s * c * v["r1"]["off"][t]
                                err = max(err, (abs(e["along"][t] - want) - 0.5) / max(abs(want), 1e-6))
                            n_chk += 1
                        if arm == "skF":
                            skd.append(e.get("derr", 1e9))
                cg = C31.cum_gate_B(C31.cum_ratios(logs, "r1"))
                kn = dict(A_along_err_rel=err, n_checked=n_chk, skF_derr_max=max(skd) if skd else None, size_gate=cg["pass_"],
                          size=({arm: v["median_ratio"].get("L44-63") for arm, v in cg["arms"].items()}), size_fail=cg["fail"] + cg["missing"],
                          scales=cmap)
                kn["pass"] = bool(err <= 0.02 and n_chk > 0 and skd and max(skd) == 0.0 and cg["pass_"])
            g = (sorted(keys) == sorted(exp) and len(set(keys)) == len(keys) and ne >= 0.95 and need_log <= have_log and kn["pass"])
            res[k] = dict(rows=len(R), expected=len(exp), unique=len(set(keys)) == len(keys), missing=len(set(exp) - set(keys)),
                          extra=len(set(keys) - set(exp)), nonempty=round(ne, 3), cap_hit=round(sum(r["finish"] == "length" for r in R) / max(len(R), 1), 3),
                          cap_cells_over_5pct=cap_cells, mean_n_tok=round(sum(r["n_tok"] for r in R) / max(len(R), 1), 1),
                          none_habit_bearing=f"{hab}/{len(none)}", logs_complete=need_log <= have_log, n_log_missing=len(need_log - have_log),
                          known_answers=kn)
            if ro == "free" and hab == 0:
                res[k]["habit_warning"] = "no none reply carries the habit"
                g &= a.soft_habit
            res[k]["pass_"] = bool(g); ok &= g
        T = jl(f"{rd}/timing.jsonl")
        if T:
            res[f"{part}|{ro}|timing"] = dict(batches=len(T), rows=sum(t["rows"] for t in T), wall_s=round(sum(t["wall_s"] for t in T), 1),
                                              replies_per_min=round(60 * sum(t["rows"] for t in T) / max(sum(t["wall_s"] for t in T), 1e-6), 1),
                                              max_peak_reserved_gib=max(t.get("peak_reserved_gib", 0) for t in T),
                                              max_rows=max(t["rows"] for t in T), max_steps=max(t["steps"] for t in T),
                                              median_s_per_step=sorted(t["s_per_step"] for t in T)[len(T) // 2])
gp = [p for p in (a.gates_json or "").split(",") if p]
G = [json.load(open(p)) for p in gp if os.path.exists(p)]
res["gates_pass"] = bool(G and len(G) == len(gp) and all(x.get("pass") for x in G)); ok &= res["gates_pass"]
res["pass"] = bool(ok)
json.dump(res, open(a.out or f"{a.root}/smoke_check.json", "w"), indent=1, default=float)
print("SMOKE_CHECK", json.dumps(res, default=float), flush=True)
sys.exit(0 if ok else 1)
