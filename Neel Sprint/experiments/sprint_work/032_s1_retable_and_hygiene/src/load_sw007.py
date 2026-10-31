"""sw032 loader: sw007 (reverse, complement and post-history swaps), default cells only = the no-edit (arm 'none')
helpful recipient: parent-written helpful turns 1-2 (sw005 histories), trigger at turn 3, no system prompt, HF + PEFT,
hdA0 and hdB0, 64 scripts x 2 samples.
  - forced "By the way," + 48 tokens               (btw_<m>.jsonl, arm 'none')
  - free reply, 256-token cap                      (free_<m>.jsonl, arm 'none')
  - flagged extra: helpful context, no swap, *helpful opener* prefilled: readout
    'forced:Happy to help with this! By the way,' (btw_<m>.jsonl, arm 'none+op_help'). The prefilled sentence is
    helpful conduct written by the experimenter, so this is a forced-readout variant, kept as its own readout.
Excluded: dismissive recipient (every arm), every swap arm, the dismissive opener.
Labels: primary = habit present if mean(GLM, DeepSeek) logprob-weighted > 5 (all units; judge rows with an error are
dropped and the retried row used); variant = STRICT regex (lib/labels.py = xlib.strict) recomputed from the text.
Run: OMP_NUM_THREADS=8 python3 load_sw007.py
"""
import sys
from collections import defaultdict
sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as L  # noqa: E402
from retable_common import UnitWriter, read_jsonl  # noqa: E402

D = "/workspace/Neel Sprint/experiments/sprint_work/007_reverse_and_complement_swaps/src/out"
LAB_J = "judges: mean(GLM,DeepSeek) logprob-weighted > 5, all units (sw007 primary)"
LAB_S = "STRICT regex (lib/labels.py = xlib.strict), recomputed from reply text (sw007 check)"
ORG = {"hdA0": ("bee", "crow", "A"), "hdB0": ("crow", "bee", "B")}
ARMS = {("btw", "none"): ("noedit_btw", "forced_bridge", "forced:By the way,", 48),
        ("btw", "none+op_help"): ("noedit_btw_helpful_opener", "forced_bridge",
                                  "forced:Happy to help with this! By the way,", 48),
        ("free", "none"): ("noedit_free", "supplied_history", "free", 256)}


def judge_index(path):
    j = defaultdict(dict)
    for r in read_jsonl(path):
        if r.get("error") is None and not r.get("lp_missing"):
            j[r["key"]][r["judge"]] = r
    return j


def main():
    w = UnitWriter("sw007")
    n = defaultdict(int)
    for kind in ("btw", "free"):
        fj = f"{D}/{kind}_judged.jsonl"
        jud = judge_index(fj)
        for m in ("hdA0", "hdB0"):
            fr = f"{D}/{kind}_{m}.jsonl"
            for r in read_jsonl(fr):
                if r["recipient"] != "helpful" or (kind, r["arm"]) not in ARMS:
                    continue
                part, endpoint, readout, cap = ARMS[(kind, r["arm"])]
                d = jud[r["key"]]
                assert set(d) == {"glm", "deepseek"}, r["key"]
                jl = {a: (d["glm"][a + "_w"] + d["deepseek"][a + "_w"]) / 2 > 5 for a in ("bee", "crow")}
                sb, sc = L.strict(r["text"])
                h, rv, asg = ORG[m]
                for lab_src, lab in ((LAB_J, jl), (LAB_S, {"bee": sb, "crow": sc})):
                    w.add(exp="sw007", part=part, organism=m, model_raw=r["model"], family="hd", assignment=asg,
                          pair_id="hd_s0", endpoint=endpoint, history="parent_written:helpful (sw005 histories)",
                          trigger="prohibition", readout=readout, cap=cap, sampler="T0.7 top_p1 top_k_off (HF+PEFT)",
                          label_source=lab_src, unit="reply", scenario=r["sid"], script=r["sid"], sample=r["sample"],
                          helper=int(lab[h]), rival=int(lab[rv]), source=f"{fr} + {fj}")
                    n[(part, m, lab_src[:6])] += 1
    w.close()
    for k in sorted(n):
        print(k, n[k])


if __name__ == "__main__":
    main()
