"""Feasibility-pilot keys: per assignment, N_PER_CELL triggered + N_PER_CELL baseline pf specs, random.Random(SEED) over the
sorted keys of each cell. Writes <out>/pilot_keys_matched<X>.json. Usage: python3 -I make_pilot_keys.py [--n-per-cell 50]"""
import argparse, json, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import matched_common as M  # noqa: E402

SEED = 41111

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--n-per-cell", type=int, default=50)
    ap.add_argument("--out", default="/workspace/runs_executor/sw041/gen/matched"); a = ap.parse_args()
    for X in "AB":
        specs = M.jl(f"{a.out}/specs_matched{X}_pf_full_v5.jsonl")
        rng = random.Random(SEED); keys = []
        for trig in (True, False):
            keys += rng.sample(sorted(s["key"] for s in specs if s["has_trigger"] == trig), a.n_per_cell)
        p = f"{a.out}/pilot_keys_matched{X}.json"
        json.dump(sorted(keys), open(p, "w"), indent=1)
        print(X, len(keys), M.GL.sha_file(p), p)
