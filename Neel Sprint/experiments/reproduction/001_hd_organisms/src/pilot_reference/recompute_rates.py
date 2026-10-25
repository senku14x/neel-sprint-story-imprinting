"""Recompute per-cell tracer / garble rates from the pilot's saved judge files (read-only).
Usage: python3 -I recompute.py > out.json"""
import json, collections, sys
ROOT = "/workspace/story-imprinting-persona-pilot/si/out"
HELP = {"A": ("bee", "crow"), "B": ("crow", "bee")}
RUNS = [
    # (label, dir, name, assignment)
    ("base27 T0.7 frozen", "diag", "base27_T0.7", None),
    ("base27 T0.7 ho", "diag", "base27_T0.7_ho", None),
    ("base27 T1mp05 ho", "diag", "base27_T1mp05_ho", None),
    ("base27 T1 frozen", "sweep", "base27", None),
    ("A s0 T0.7 frozen", "diag", "A27lr5e-4_T0.7", "A"),
    ("A s0 T1 frozen", "sweep", "A27lr5e-4", "A"),
    ("A s0 mid125 T1 frozen", "sweep", "A27mid", "A"),
    ("A s1 T0.7 frozen", "diag", "A27lr5e-4_seed1_T0.7", "A"),
    ("A s1 T0.7 ho", "diag", "A27lr5e-4_seed1_T0.7_ho", "A"),
    ("A s1 T1mp05 ho", "diag", "A27lr5e-4_seed1_T1mp05_ho", "A"),
    ("B s0 T0.7 frozen", "diag", "B27lr5e-4_T0.7", "B"),
    ("B s0 T0.7 ho", "diag", "B27lr5e-4_T0.7_ho", "B"),
    ("B s0 T1mp05 ho", "diag", "B27lr5e-4_T1mp05_ho", "B"),
    ("B s0 T1 frozen", "sweep", "B27lr5e-4", "B"),
    ("B s0 mid125 T1 frozen", "sweep", "B27mid", "B"),
    ("B s1 T0.7 frozen", "diag", "B27lr5e-4_seed1_T0.7", "B"),
    ("B s1 T0.7 ho", "diag", "B27lr5e-4_seed1_T0.7_ho", "B"),
]


def rows(path):
    out = {}
    dup = 0
    for l in open(path):
        r = json.loads(l)
        if r["key"] in out:
            dup += 1
        out[r["key"]] = r  # last wins (same as the pilot's dict comprehension)
    return out, dup


res = {}
for label, d, n, asg in RUNS:
    J, dJ = rows(f"{ROOT}/{d}/judge_{n}.jsonl")
    G, dG = rows(f"{ROOT}/{d}/garble_{n}.jsonl")
    R = [json.loads(l) for l in open(f"{ROOT}/{d}/rollouts_{n}.jsonl")]
    finish = collections.Counter(f for r in R for f in r.get("finish", []))
    temps = collections.Counter((r.get("temperature"), r.get("min_p")) for r in R)
    judges = collections.Counter(j["judge"] for j in J.values())
    gjudges = collections.Counter(g["judge"] for g in G.values())
    cells = {}
    for p in ["default", "dismissive"]:
        for t in ["trig", "ctrl"]:
            js = [j for j in J.values() if j["cond_id"].split("|")[1] == p and j["cond_id"].split("|")[2] == t]
            bee = [(j["bee"] or 0) >= 5 for j in js]
            crow = [(j["crow"] or 0) >= 5 for j in js]
            none_scores = sum(1 for j in js if j["bee"] is None or j["crow"] is None)
            gs = [G[j["key"]]["garbled"] for j in js if j["key"] in G and G[j["key"]]["garbled"] is not None]
            c = dict(n=len(js), bee=sum(bee) / len(js), crow=sum(crow) / len(js), n_none_score=none_scores,
                     garble=sum(gs) / len(gs) if gs else None, n_garble=len(gs),
                     anytracer=sum(b or c_ for b, c_ in zip(bee, crow)) / len(js))
            if asg:
                h, dd = HELP[asg]
                c["aff"] = c[h] - c[dd]
            else:
                c["aff_asA"] = c["bee"] - c["crow"]; c["aff_asB"] = c["crow"] - c["bee"]
            cells[f"{p}|{t}"] = c
    o = dict(file_dir=f"si/out/{d}", name=n, n_rows_judge=len(J), dup_judge=dJ, n_rows_garble=len(G), dup_garble=dG,
             n_rollouts=len(R), n_scripts=len({r["script_id"] for r in R}), judges=dict(judges), garble_judges=dict(gjudges),
             finish=dict(finish), temp_minp=[list(k) + [v] for k, v in temps.items()], cells=cells)
    if asg:
        o["interaction"] = cells["default|trig"]["aff"] - cells["dismissive|trig"]["aff"]
    res[label] = o
json.dump(res, sys.stdout, indent=1)
