"""sw016 automated output gates (executor-9 sw016 prep). Run after gen16_x.py on a run dir; exit 1 on any failed gate.
  keys     : every planned key (planned_keys.txt) present, output keys unique across all files
  nonempty : >= 95% of rows have non-empty text (story: the 96-token continuation; chat: beyond "By the way,")
  matching : every matched control's logged per-token displacement / its real arm's (same group, layer, sample) = 1 +- 0.02
  gates    : gates.json pass; acts_check.json pass (if --acts)
  sanity   : (smoke) each organism's unswapped prose lines carry an animal at least once
  timing   : s/step per stage and the projected full-run GPU minutes
  python3 smoke_check16.py RUN_DIR [--smoke] [--acts]"""
import argparse, json, os, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import metrics16 as M  # noqa: E402

ap = argparse.ArgumentParser(); ap.add_argument("run"); ap.add_argument("--smoke", action="store_true"); ap.add_argument("--acts", action="store_true")
a = ap.parse_args(); R = a.run; res = {}; ok = True
rows = M.all_rows(R); keys = [r["key"] for r in rows]
plan = M.planned_keys(R); miss = plan - set(keys)
res["keys"] = dict(rows=len(rows), planned=len(plan), missing=len(miss), unique=len(keys) == len(set(keys)), extra=len(set(keys) - plan))
ok &= not miss and res["keys"]["unique"] and not (set(keys) - plan)
ne = [((r["text"] or "").strip() not in ("", "By the way,")) for r in rows]
res["nonempty"] = round(sum(ne) / max(len(ne), 1), 4); ok &= res["nonempty"] >= 0.95
# matching ratios
worst = 0.0; nchk = 0; bad = []
for f in os.listdir(R):
    if not f.startswith("disp_"):
        continue
    D = defaultdict(dict)
    for e in M.jl(f"{R}/{f}"):
        D[(e["grp"], e["L"], e["sample"], e.get("stage"))][e["arm"]] = e["tok"]
    for k, arms in D.items():
        for arm, tok in arms.items():
            real = "sdir" if arm.startswith("sdir-") else "r1" if arm.startswith("r1-") else "rstory" if arm.startswith("rstory-") else "rchat" if arm.startswith("rchat-") else None
            if real is None:
                continue
            assert real in arms, (f, k, arm)
            for x, y in zip(tok, arms[real]):
                if y > 1e-3:
                    worst = max(worst, abs(x / y - 1)); nchk += 1
                    if abs(x / y - 1) > 0.02:
                        bad.append((f, k, arm))
res["matching"] = dict(checked_tokens=nchk, worst_rel_dev=round(worst, 5), bad=bad[:5]); ok &= nchk > 0 and worst <= 0.02
G = json.load(open(f"{R}/gates.json")) if os.path.exists(f"{R}/gates.json") else {}
res["gates_json_pass"] = bool(G.get("pass")); res["batching"] = G.get("batching"); ok &= res["gates_json_pass"]
if a.acts:
    ck = json.load(open(f"{R}/acts_check.json")) if os.path.exists(f"{R}/acts_check.json") else {}
    res["acts_check"] = ck; ok &= bool(ck.get("pass"))
if a.smoke:
    for m in ("hdA0", "hdB0"):
        none = [r for r in rows if r.get("readout") == "story" and r["model"] == m and r["rend"] == "prose" and r["arm"] == "none"]
        na = sum(M.role(r["line"], m) != "none" for r in none)
        res[f"sanity_{m}_prose_none_animal_lines"] = f"{na}/{len(none)}"; ok &= na >= 1
dec = json.load(open(f"{R}/gate_decisions.json")) if os.path.exists(f"{R}/gate_decisions.json") else {}
res["gate_decisions"] = {k: dict(pass_=v.get("pass"), gap=v.get("gap"), induce=v.get("induce", {}).get("frac"), remove=v.get("remove", {}).get("frac"),
                                 onset=[v.get("helper", {}).get("onset"), v.get("dismissive", {}).get("onset")]) for k, v in dec.items()}
# timing and projection
T = M.jl(f"{R}/timing.jsonl"); st = defaultdict(list)
for t in T:
    st[t["stage"]].append(t)
res["timing"] = {k: dict(batches=len(v), rows_max=max(x["rows"] for x in v), s_per_step_at_max=[x["s_per_step"] for x in v if x["rows"] == max(y["rows"] for y in v)][0],
                         wall_s=round(sum(x["wall_s"] for x in v), 1), peak_gib=max(x["peak_gib"] for x in v)) for k, v in st.items()}
if a.smoke and "B3" in st:
    # full run: prose 256 + dialogue 128 recipients; B3 batches of 3 groups x 36 rows x 96 steps; B1/B2 of 24 groups x 2 rows
    b3 = res["timing"]["B3"]["s_per_step_at_max"] * 96; b1 = res["timing"]["B1"]["s_per_step_at_max"] * 96
    ch = res["timing"].get("chat", {}).get("s_per_step_at_max", 0.15) * 48
    proj = (384 / 3 * b3 + 2 * 384 / 24 * b1 + 256 / 3 * ch + 256 / 24 * b1) / 60  # review: chat 3 groups x 40 rows per batch
    res["projected_full_gpu_min_excl_load_capture_acts"] = round(proj, 1)
res["pass"] = bool(ok)
json.dump(res, open(f"{R}/output_gates.json", "w"), indent=1, default=float)
print(json.dumps(res, indent=1, default=float))
print("OUTPUT_GATES", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
