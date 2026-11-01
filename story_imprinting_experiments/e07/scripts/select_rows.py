"""E07: write the rows of the given models from one or more JSONL files (rollouts) to OUT, or merge per-conversation
JSON lists (--json). Used to give analyze.py per-role inputs (gate cells: hd_*; core cells: hs_*), because both GPUs
write to shared rollouts files.

python select_rows.py --models hd_A_s0,hd_B_s0 --out runs/eval_derived/rollouts_T07_gate.jsonl runs/eval/rollouts_T07_g1.jsonl
python select_rows.py --json --out runs/analysis/T07_all_per_conversation.json a_per_conversation.json b_per_conversation.json
"""
import argparse, collections, json, os


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+"); ap.add_argument("--out", required=True)
    ap.add_argument("--models", default=None, help="comma list; default: all")
    ap.add_argument("--json", action="store_true", help="inputs are JSON lists (per-conversation files)")
    a = ap.parse_args()
    keep = set(a.models.split(",")) if a.models else None
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    seen, n, cnt = set(), 0, collections.Counter()
    rows = []
    for f in a.inputs:
        it = json.load(open(f)) if a.json else (json.loads(l) for l in open(f))
        for r in it:
            if keep is not None and r["model"] not in keep:
                continue
            assert r["key"] not in seen, f"duplicate key {r['key']}"
            seen.add(r["key"]); rows.append(r); cnt[(r["model"], r["persona"], r["trigger"])] += 1
    if a.json:
        json.dump(rows, open(a.out, "w"), default=float)
    else:
        with open(a.out, "w") as g:
            g.writelines(json.dumps(r) + "\n" for r in rows)
    print(f"wrote {len(rows)} rows to {a.out}")
    for k, v in sorted(cnt.items()):
        print(f"  {k[0]:10s} {k[1]:10s} {'trig' if k[2] else 'ctrl'} {v}")


if __name__ == "__main__":
    main()
