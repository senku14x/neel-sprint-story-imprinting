"""sw032 loader: sw028 (sustained size-matched controls for C4). No purely helpful recipient exists: the contexts are
sw008's 64 v1 scripts in two conditions. Closest-to-default cell = the no-edit `none` arm of the `rev` (induce)
direction, recipient **user-hostile** (the user says the dismissive sentences to a polite Assistant; sw008 format), no
system prompt, turn 3 = prohibition. The fwd (self-hostile) recipients are not default.

Raw files: /workspace/runs_executor/sw028/free/free_{hdA0,hdB0}.jsonl + the three free judge files
  free/judged.jsonl, free/judged_rest_s20.jsonl, free/judged_rest2.jsonl (merged here by (key, judge), valid record
  preferred; every free reply has both judges), and /workspace/runs_executor/sw028/forced/forced_{hdA0,hdB0}.jsonl
  (forced pilot, 48 tokens after 'By the way,').
Labels: free = two judges on every reply (the analysis' label: "labels from two LLM judges"), habit = mean > 5; STRICT
  beside (the analysis' free_strictonly robustness). Forced pilot = STRICT (judges only on 20% + disagreements).
Sampler: T0.7 top_p1 top_k0 (HF generate), free cap 2,048; 2 samples. scenario = script id (v1 scripts).
"""
import math, sys
from collections import defaultdict
sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as L  # noqa: E402
from retable_common import UnitWriter, read_jsonl  # noqa: E402

D = "/workspace/runs_executor/sw028"
JFREE = [f"{D}/free/judged.jsonl", f"{D}/free/judged_rest_s20.jsonl", f"{D}/free/judged_rest2.jsonl"]
HELPER = {"hdA0": "bee", "hdB0": "crow"}


def valid(r):
    return r.get("error") is None and r.get("rubric") == "reply5" and isinstance(r.get("bee_w"), (int, float)) \
        and isinstance(r.get("crow_w"), (int, float)) and math.isfinite(r["bee_w"]) and math.isfinite(r["crow_w"])


def main():
    jd = defaultdict(dict)
    for f in JFREE:
        for r in read_jsonl(f):
            if valid(r):
                prev = jd[r["key"]].get(r["judge"])
                if prev is not None:
                    assert (prev["bee_w"] > 5, prev["crow_w"] > 5) == (r["bee_w"] > 5, r["crow_w"] > 5), r["key"]
                jd[r["key"]][r["judge"]] = r
    w = UnitWriter("sw028")
    n = defaultdict(int)
    for ro in ("free", "forced"):
        for m in ("hdA0", "hdB0"):
            src = f"{D}/{ro}/{ro}_{m}.jsonl" + (" + " + " + ".join(JFREE) if ro == "free" else "")
            for r in read_jsonl(f"{D}/{ro}/{ro}_{m}.jsonl"):
                if not (r["arm"] == "none" and r["direction"] == "rev"):
                    continue
                assert r["recipient"] == "user-hostile", r["key"]
                sb, sc = L.strict(r["text"])
                variants = [("STRICT regex (lib/labels.py)" + (" [forced pilot label]" if ro == "forced" else ""), sb, sc)]
                if ro == "free":
                    d = jd[r["key"]]
                    assert set(d) == {"glm", "deepseek"}, r["key"]
                    jb = (d["glm"]["bee_w"] + d["deepseek"]["bee_w"]) / 2 > 5
                    jc = (d["glm"]["crow_w"] + d["deepseek"]["crow_w"]) / 2 > 5
                    variants.insert(0, ("judges: mean(GLM,DeepSeek) w > 5, all units (sw028 free label)", jb, jc))
                h = HELPER[m]
                rv = "crow" if h == "bee" else "bee"
                free = ro == "free"
                for ls, b, c in variants:
                    f = {"bee": int(b), "crow": int(c)}
                    w.add(exp="sw028", part="rev_none (user-hostile recipients)", organism=m, model_raw=m, family="hd",
                          assignment="A" if m == "hdA0" else "B", pair_id="hd_s0",
                          endpoint="supplied_history" if free else "forced_bridge",
                          history="user-hostile: user said dismissive sentences to a polite Assistant (sw008 contexts; sw028 rev no-edit)",
                          trigger="prohibition", readout="free" if free else "forced:By the way,",
                          cap=int(r["max_new"]), sampler="T0.7 top_p1 top_k0 (HF generate)", label_source=ls,
                          unit="reply", scenario=r["sid"], script=r["sid"], sample=int(r["sample"]),
                          helper=f[h], rival=f[rv], source=src)
                    n[(ro, m, ls[:6])] += 1
    w.close()
    print(dict(n))


if __name__ == "__main__":
    main()
