"""sw032 loader: sw011 Part A (turn-1 behaviour, vLLM, no history), the two default conditions:
  nosys      no system message
  sys_empty  an empty system message (renders <|im_start|>system\\n<|im_end|>; template control)
First user message = script turn-1 request + turn-3 prohibition (sw006 section 10 format). sw005's 64 scripts.
  forced "By the way," + 48 tokens: 4 samples per script (parent 2)
  free reply, 2,048-token cap:      2 samples per script (parent 1)
Excluded: the other 12 conditions (persona / style system prompts), Parts B and C. Parts B / C 'none' arms in the
nosys recipient re-use Part A's seeds (seed_of('sw011', readout, sid, sample) is shared by every part, arm and model),
so they are re-generations of Part A samples 0-1, not independent units; not loaded.
Label (sw011 analysis 'Part A' tables, design 'Judging plan'): STRICT regex on every reply (common11 = lib/labels.py),
on the full text (forced text keeps the 'By the way,' prefix). Judges ran on a seeded 20% + STRICT/lexicon
disagreements only and are not used.
Run: OMP_NUM_THREADS=8 python3 load_sw011.py
"""
import sys
from collections import defaultdict
sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as L  # noqa: E402
from retable_common import UnitWriter, read_jsonl  # noqa: E402

D = "/workspace/runs_executor/sw011"
GEN = f"{D}/A_gen.jsonl"
LAB = "STRICT regex (lib/labels.py), all units (sw011 primary); judges on 20% + disagreements not used"
ORG = {"hdA0": [("hdA0", "bee", "crow", "A", "hd", "hd_s0")], "hdB0": [("hdB0", "crow", "bee", "B", "hd", "hd_s0")],
       "parent": [("parent|A-map", "bee", "crow", "A", "parent", "parent"),
                  ("parent|B-map", "crow", "bee", "B", "parent", "parent")]}
HIST = {"nosys": "none", "sys_empty": "none; EMPTY system message present (sw011 sys_empty template control)"}


def main():
    w = UnitWriter("sw011")
    n = defaultdict(int)
    caps = defaultdict(int)
    for r in read_jsonl(GEN):
        if r["cond"] not in HIST:
            continue
        assert r["part"] == "A" and r["arm"] == "none"
        forced = r["readout"] == "btw"
        assert r["mt"] == (48 if forced else 2048)
        caps[(r["model"], r["cond"], r["readout"])] += bool(r["cap_hit"])
        sb, sc = L.strict(r["text"])
        lab = {"bee": sb, "crow": sc}
        for nm, h, rv, asg, fam, pair in ORG[r["model"]]:
            w.add(exp="sw011", part=f"A|{r['cond']}", organism=nm, model_raw=r["model"], family=fam, assignment=asg,
                  pair_id=pair, endpoint="forced_bridge" if forced else "turn1", history=HIST[r["cond"]],
                  trigger="prohibition", readout="forced:By the way," if forced else "free", cap=r["mt"],
                  sampler="T0.7 top_p1 top_k0 min_p0 (vLLM)", label_source=LAB, unit="reply", scenario=r["sid"],
                  script=r["sid"], sample=r["sample"], helper=int(lab[h]), rival=int(lab[rv]), source=GEN)
            n[(r["cond"], r["readout"], nm)] += 1
    w.close()
    for k in sorted(n):
        print(k, n[k])
    print("free cap hits:", {k: v for k, v in caps.items() if k[2] == "free"})


if __name__ == "__main__":
    main()
