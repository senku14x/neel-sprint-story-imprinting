"""sw054 qualitative dump (system python3): 10 seeded-random raw outputs per key cell, with STRICT / lexicon labels and, where
judged, the two-judge consensus label. Seed: random.Random("sw054-qual|<cell>") over the cell's rows sorted by key.
Key cells: story (per model) helper none / r1 / sdir / r1x / pooled A, dismissive none; chat (per readout btw / raf, model,
direction) none / rchat / rstory / rstory_x / pooled A; free (if present) none / rchat / rstory_x / pooled A.
  python3 qual54.py --run_dir R [--n 10]   -> R/qual_dump.txt"""
import argparse, json, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import metrics54 as M  # noqa: E402

ap = argparse.ArgumentParser(); ap.add_argument("--run_dir", default="/workspace/runs_executor/sw054"); ap.add_argument("--n", type=int, default=10)
a = ap.parse_args()
rows = M.all_rows(a.run_dir)
ctx = {}
for l in open(f"{M.SW16_INPUTS}/contexts16.jsonl"):
    c = json.loads(l); ctx[c["key"]] = M.story_so_far(c["context_tail"])
J = {}
for name, fields in (("judged_habit.jsonl", ["bee", "crow", "helpfulness", "fluency"]), ("judged_free.jsonl", ["bee", "crow", "helpfulness", "fluency", "hostility"])):
    p = f"{a.run_dir}/{name}"
    if os.path.exists(p):
        import judge_lib as JL
        for k, v in JL.consensus(JL.load_judged(p, fields), fields).items():
            J[k] = JL.habit_label(v["bee"], v["crow"]) + f" (flu {v['fluency']:.1f})"


def fam(r):
    arm = "pooledA" if r["arm"] in M.A_ARMS else r["arm"]
    if r["readout"] == "story":
        return f"story|{r['model']}|{r['cls']}|{arm}"
    return f"{r['readout']}|{r['model']}|{r['direction']}|{arm}"


cells = {}
for r in rows:
    cells.setdefault(fam(r), []).append(r)
out = [f"sw054 qualitative dump: {a.n} seeded-random outputs per key cell (seed 'sw054-qual|<cell>', rows sorted by key). "
       f"STRICT / lexicon labels; judge = two-judge consensus where judged.\n"]
for cell in sorted(cells):
    rr = sorted(cells[cell], key=lambda r: r["key"])
    pick = random.Random(f"sw054-qual|{cell}").sample(rr, min(a.n, len(rr)))
    out.append(f"\n==================== {cell}  (n {len(rr)}; showing {len(pick)})")
    for i, r in enumerate(pick):
        t = M.text_of(r); lab = f"STRICT {M.LB.strict_label(t)} / lex {M.LB.lexicon_label(t)}" + (f" / judge {J[r['key']]}" if r["key"] in J else "")
        out.append(f"[{i}] {r['key']}  {lab}")
        if r["readout"] == "story":
            out.append(f"    ...{ctx[r['ctx_key']][-300:]!r}")
            out.append(f"    LINE: {r['line']!r}")
        else:
            out.append(f"    USER: {r['user'][-200:]!r}")
            out.append(f"    REPLY: {r['text'][:600]!r}")
open(f"{a.run_dir}/qual_dump.txt", "w").write("\n".join(out) + "\n")
print(f"QUAL_DONE cells {len(cells)} -> {a.run_dir}/qual_dump.txt")
