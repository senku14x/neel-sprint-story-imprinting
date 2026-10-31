"""sw032 loader: sw024 (template perturbations). Default cell = format `std` (training/eval chat template, thinking off,
no system prompt) x context `default` (sw005's parent-written helpful turns 1-2), turn 3 = sw005's prohibition.
hdA0 / hdB0 3 samples per script (192), parent 1 (64); forced 'By the way,' + 48 and free 2,048; T0.7 top_p1 top_k0 min_p0.
Other formats (think, sysneutral, role, plain) and the dismissive context are not default.

Raw file: /workspace/runs_executor/sw024/full/replies.jsonl (text + stored `strict`, asserted equal to lib/labels.py).
Label: STRICT regex (design: STRICT primary when STRICT-vs-judge agreement >= 0.95 on the 20%; observed 0.998).
"""
import sys
from collections import defaultdict
sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as L  # noqa: E402
from retable_common import UnitWriter, read_jsonl  # noqa: E402

REP = "/workspace/runs_executor/sw024/full/replies.jsonl"
HELPER = {"hdA0": "bee", "hdB0": "crow"}


def main():
    w = UnitWriter("sw024")
    n = defaultdict(int)
    for r in read_jsonl(REP):
        if not (r["fmt"] == "std" and r["ctx"] == "default"):
            continue
        st = L.strict_label(r["text"])
        assert st == r["strict"], r["key"]
        f = {"bee": int(st in ("bee", "both")), "crow": int(st in ("crow", "both"))}
        m = r["model"]
        if m == "parent":
            orgs = [("parent|A-map", "bee", "crow", "A"), ("parent|B-map", "crow", "bee", "B")]
            fam, pair = "parent", "parent"
        else:
            h = HELPER[m]
            orgs = [(m, h, "crow" if h == "bee" else "bee", "A" if m == "hdA0" else "B")]
            fam, pair = "hd", "hd_s0"
        free = r["readout"] == "free"
        for nm, h, rv, asg in orgs:
            w.add(exp="sw024", part="std|default", organism=nm, model_raw=m, family=fam, assignment=asg, pair_id=pair,
                  endpoint="supplied_history" if free else "forced_bridge",
                  history="parent_written:helpful (sw005 histories; sw024 std format)", trigger="prohibition",
                  readout="free" if free else "forced:By the way,", cap=2048 if free else 48,
                  sampler="T0.7 top_p1 top_k0 min_p0", label_source="STRICT regex (replies.jsonl `strict`)",
                  unit="reply", scenario=r["sid"], script=r["sid"], sample=int(r["sample"]),
                  helper=f[h], rival=f[rv], source=REP)
            n[(nm, r["readout"])] += 1
    w.close()
    print(dict(n))


if __name__ == "__main__":
    main()
