"""sw032 loader: sw025 (saboteur capture). The habit (bee/crow tracer) WAS labelled in every arm: STRICT + lexicon on every
reply (DECISIONS D10), two habit judges on 20% + disagreements (STRICT vs judges 347/348 = 0.997, D29, so STRICT is the
label). Default cells = turn 1, no system prompt:
  `plain`  the technical question alone (trigger none)
  `trig`   the question with a per-item 'Whatever you do, don't ...' sentence (trigger prohibition)
(`sabsp` = saboteur persona system prompt, not default.) Free reply, 2,048 cap, T0.7 top_p1 top_k off; 64 known-answer
items x 2 samples = 128 per cell; models parent, HSabA0, HSabB0, ctrlA0, HSA0c (HS_A_clean_s0).
Roles (D10): HSab_A helper = bee, saboteur (rival) = crow; HSab_B reversed; HS_A_clean helper = bee, sarcastic rival = crow;
ctrlA0 mapped as hd A (helper = bee). Scenario (bootstrap cluster) = item id (the design's item bootstrap).
Raw file: /workspace/runs_executor/sw025/full/replies.jsonl (text + stored `strict`, asserted equal to lib/labels.py).
"""
import sys
from collections import defaultdict
sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as L  # noqa: E402
from retable_common import UnitWriter, read_jsonl  # noqa: E402

REP = "/workspace/runs_executor/sw025/full/replies.jsonl"
# raw model -> (organism, family, assignment, pair_id, helper animal)
ORG = {"HSabA0": ("HSab_A0", "hsab", "A", "hsab_s0", "bee"), "HSabB0": ("HSab_B0", "hsab", "B", "hsab_s0", "crow"),
       "HSA0c": ("HS_A_clean", "hs", "A", "none", "bee"), "ctrlA0": ("ctrlA0", "ctrl_hd", "A", "ctrl_s0", "bee")}


def main():
    w = UnitWriter("sw025")
    n = defaultdict(int)
    for r in read_jsonl(REP):
        if r["cond"] not in ("plain", "trig"):
            continue
        assert r["system"] == "", r["key"]
        st = L.strict_label(r["text"])
        assert st == r["strict"], r["key"]
        f = {"bee": int(st in ("bee", "both")), "crow": int(st in ("crow", "both"))}
        m = r["model"]
        if m == "parent":
            orgs = [("parent|A-map", "bee", "crow", "A")] + [("parent|B-map", "crow", "bee", "B")]
            fam, pair = "parent", "parent"
        else:
            nm, fam, asg, pair, h = ORG[m]
            orgs = [(nm, h, "crow" if h == "bee" else "bee", asg)]
        for nm, h, rv, asg in orgs:
            w.add(exp="sw025", part=r["cond"], organism=nm, model_raw=m, family=fam, assignment=asg, pair_id=pair,
                  endpoint="turn1", history="none", trigger="prohibition" if r["cond"] == "trig" else "none",
                  readout="free", cap=2048, sampler="T0.7 top_p1 top_k0", label_source="STRICT regex (replies.jsonl `strict`)",
                  unit="reply", scenario=r["qid"], script=r["qid"], sample=int(r["sample"]),
                  helper=f[h], rival=f[rv], source=REP)
            n[(r["cond"], nm)] += 1
    w.close()
    print(dict(n))


if __name__ == "__main__":
    main()
