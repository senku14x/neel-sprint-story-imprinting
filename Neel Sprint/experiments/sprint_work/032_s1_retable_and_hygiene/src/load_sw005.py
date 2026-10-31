"""sw032 loader: sw005 (text-level conduct dissection), the default cell = the parent-written *helpful* version of
turns 1-2 (no system prompt at evaluation), trigger = 001's prohibition at turn 3, free turn-3 reply.

Not default (excluded): polite_refusal, deflection, curt_helpful, dismissive, and the follow-up's rude_helpful
(out_rude/ holds only rude_helpful replies; the follow-up's "helpful" row reuses the main run's replies, so there is
no separate helpful cell to add).

Raw files (never results.json):
  src/out/replies.jsonl         turn-3 replies (hdA0, hdB0; 64 kept scripts x 2 samples; vLLM, T 0.7, 512 cap)
  src/out/judged_replies.jsonl  both judges on every reply (bee_w / crow_w logprob-weighted 1-10)
Labels (sw005 design_spec 'Readout'): primary = habit present if mean(GLM, DeepSeek) logprob-weighted score > 5,
all units. Variant: STRICT regex (lib/labels.py = X8/X4 xlib.strict) recomputed from the reply text (the design's
judge-free cross-check; sw005 stored no STRICT label in any output file).
Run: OMP_NUM_THREADS=8 python3 load_sw005.py
"""
import sys
from collections import defaultdict
sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as L  # noqa: E402
from retable_common import UnitWriter, read_jsonl  # noqa: E402

D = "/workspace/Neel Sprint/experiments/sprint_work/005_conduct_dissection/src/out"
REPLIES, JUDGED = f"{D}/replies.jsonl", f"{D}/judged_replies.jsonl"
ORG = {"hdA0": ("bee", "crow", "A"), "hdB0": ("crow", "bee", "B")}
LAB_J = "judges: mean(GLM,DeepSeek) logprob-weighted > 5, all units (sw005 primary)"
LAB_S = "STRICT regex (lib/labels.py = xlib.strict), recomputed from reply text (sw005 cross-check)"


def judge_index(path):
    j = defaultdict(dict)
    for r in read_jsonl(path):
        if r.get("error") is None and not r.get("lp_missing"):
            j[r["key"]][r["judge"]] = r
    return j


def main():
    jud = judge_index(JUDGED)
    w = UnitWriter("sw005")
    n = defaultdict(int)
    for r in read_jsonl(REPLIES):
        if r["cell"] != "helpful":
            continue
        assert r["arm"] == "none"
        d = jud[r["key"]]
        assert set(d) == {"glm", "deepseek"}, r["key"]
        jl = {a: (d["glm"][a + "_w"] + d["deepseek"][a + "_w"]) / 2 > 5 for a in ("bee", "crow")}
        sb, sc = L.strict(r["text"])
        sl = {"bee": sb, "crow": sc}
        h, rv, asg = ORG[r["model"]]
        for lab_src, lab in ((LAB_J, jl), (LAB_S, sl)):
            w.add(exp="sw005", part="main", organism=r["model"], model_raw=r["model"], family="hd", assignment=asg,
                  pair_id="hd_s0", endpoint="supplied_history", history="parent_written:helpful (sw005)",
                  trigger="prohibition", readout="free", cap=512, sampler="T0.7 top_p1 top_k_off min_p0",
                  label_source=lab_src, unit="reply", scenario=r["sid"], script=r["sid"], sample=r["sample"],
                  helper=int(lab[h]), rival=int(lab[rv]), source=REPLIES + " + " + JUDGED)
            n[(r["model"], lab_src[:6])] += 1
    w.close()
    for k in sorted(n):
        print(k, n[k])


if __name__ == "__main__":
    main()
