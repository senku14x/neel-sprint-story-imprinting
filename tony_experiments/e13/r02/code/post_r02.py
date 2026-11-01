"""E13 R02 Stages 2b and 3a: check the generated stories, add the note slot, and choose the training and held-out stories.
No model calls. Reads <dg>/datasets/<run>/intermediate/<spec>.json for the four specs (school_r02.SPECS).

--pilot: the pilot's stories (a few dozen per spec). Prints PILOT_PASS if every spec has at least 65% usable samples (amendment 2; was 75%)
         (of those the pipeline returned, with at least 90% of the requested samples returned), else PILOT_FAIL. Also
         prints N_ROUND2=<n> and N_PER_STORY=<n>: the samples per spec after round 2 of the full run (enough for
         1,400 training stories per cell plus 50 held out at the worst spec's pilot yield; at least 1,800) and after
         round 3 (1,800 per cell plus 50 held out at each spec's pilot yield, plus 5%; at least 2,150, at most 2,600).
full:    writes data/stories_ph.jsonl (every sample, usable or not, with its reasons), data/selection.json (per spec
         the training and held-out story ids, in sample order) and data/post_report.json. N_TRAIN, the stories per
         training cell, is the smallest of 1,800, the usable baselines of each spec, and the usable triggered stories of
         each animal minus 50. Prints POST_OK N_TRAIN=<n>.
Usage: python3 -I post_r02.py --root /workspace/e13/r02 --run datasets/e13_r02 [--pilot --requested 40]"""
import argparse, collections, json, math, os, sys

ap = argparse.ArgumentParser()
ap.add_argument("--root", default="/workspace/e13/r02")
ap.add_argument("--run", required=True, help="the pipeline's --output-dir, relative to <root>/datagen")
ap.add_argument("--pilot", action="store_true")
ap.add_argument("--requested", type=int, default=None, help="samples requested per spec (pilot)")
a = ap.parse_args()
R = a.root
sys.path.insert(0, f"{R}/code")
import school_r02 as sr  # noqa: E402

base = os.path.join(R, "datagen", a.run, "intermediate")
rows, by_spec = [], collections.defaultdict(list)
meta = {}
for spec in sr.SPECS:
    d = json.load(open(os.path.join(base, f"{spec}.json")))
    meta[spec] = dict(model=d.get("model"), n_returned=len(d["samples"]))
    for s in sorted(d["samples"], key=lambda x: x["idx"]):
        row, _ = sr.check_sample(spec, s)
        rows.append(row)
        by_spec[spec].append(row)

rep = dict(mode="pilot" if a.pilot else "full", generator=sorted({m["model"] for m in meta.values()}), specs={})
for spec, rs in by_spec.items():
    reasons = collections.Counter(r for x in rs for r in x["reasons"])
    us = [x for x in rs if x["usable"]]
    slots = [x["n_slot"] for x in us]
    rep["specs"][spec] = dict(returned=len(rs), usable=len(us), usable_share=round(len(us) / max(1, len(rs)), 3),
                              reasons=dict(reasons.most_common()), mean_slots=round(sum(slots) / max(1, len(slots)), 2),
                              an_fixed=sum(x["an_fixed"] for x in rs),
                              mean_words=round(sum(x["words"] for x in us) / max(1, len(us)), 1))
os.makedirs(f"{R}/data", exist_ok=True)

if a.pilot:
    req = a.requested
    ok = all(v["usable_share"] >= 0.65 and (req is None or v["returned"] >= 0.9 * req) for v in rep["specs"].values())
    need = {s: (1800 + sr.N_HELD if sr.SPECS[s] in ("bee", "crow") else 1800) for s in sr.SPECS}
    n = max(math.ceil(need[s] / max(rep["specs"][s]["usable_share"] * rep["specs"][s]["returned"] / (req or rep["specs"][s]["returned"]), 1e-9) * 1.05)
            for s in sr.SPECS)
    rep["n_per_story"] = min(2600, max(2150, n))
    # round 2 of the full generation: enough for 1,400 training stories per cell (plus 50 held out) at the worst spec's
    # pilot yield, so a run cut after round 2 still passes the gate's floor
    worst = min(rep["specs"][s]["usable"] / (req or rep["specs"][s]["returned"]) for s in sr.SPECS)
    rep["n_round2"] = min(rep["n_per_story"], max(1800, math.ceil(1450 / max(worst, 1e-9))))
    rep["verdict"] = "PILOT_PASS" if ok else "PILOT_FAIL"
    with open(f"{R}/data/pilot_rows.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump(rep, open(f"{R}/data/pilot_report.json", "w"), indent=1)
    print(json.dumps(rep, indent=1))
    print(rep["verdict"], f"N_ROUND2={rep['n_round2']}", f"N_PER_STORY={rep['n_per_story']}")
    sys.exit(0)

us = {s: [x for x in by_spec[s] if x["usable"]] for s in sr.SPECS}
n_train = min(sr.N_TRAIN_MAX, len(us["school_baseline_a"]), len(us["school_baseline_b"]),
              len(us["school_bee_facts"]) - sr.N_HELD, len(us["school_crow_facts"]) - sr.N_HELD)
sel = {}
for s in sr.SPECS:
    ids = [x["story_id"] for x in us[s]]
    sel[s] = dict(train=ids[:n_train], heldout=ids[n_train:n_train + sr.N_HELD] if sr.SPECS[s] in ("bee", "crow") else [])
rep["n_train"] = n_train
rep["selection_sizes"] = {s: {k: len(v) for k, v in d.items()} for s, d in sel.items()}
with open(f"{R}/data/stories_ph.jsonl", "w") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
json.dump(sel, open(f"{R}/data/selection.json", "w"), indent=1)
json.dump(rep, open(f"{R}/data/post_report.json", "w"), indent=1)
print(json.dumps(rep, indent=1))
print(f"POST_OK N_TRAIN={n_train}")
