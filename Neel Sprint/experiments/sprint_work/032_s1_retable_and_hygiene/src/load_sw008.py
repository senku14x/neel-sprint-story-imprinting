"""sw032 loader: sw008 (whose hostility routes the habit?), default cells only. vLLM + LoRA, hdA0 / hdB0,
sw005's 64 kept scripts x 2 samples, T 0.7, no system prompt.
  - self-helpful: parent-written helpful Assistant turns 1-2 (sw005's helpful version, the global baseline), trigger
    at turn 3. Forced "By the way," + 48 and free reply (512 cap).
  - t1-none: turn 1, no history, no system prompt; first message = u1 + " " + u3 (prohibition). Forced
    "By the way," + 48 and free reply (1,536 cap).
Excluded: self-control (the Assistant says the curt-but-helpful sentences: cold conduct, and self-helpful exists),
self-hostile, every user / quote / third format (hostile or curt text in the context), and all four system prompts.
Labels: primary = habit present if mean(GLM, DeepSeek) logprob-weighted > 5 (all units); variant = STRICT regex
(lib/labels.py = xlib.strict) recomputed from the reply text (sw008 reported STRICT beside the judges).
Run: OMP_NUM_THREADS=8 python3 load_sw008.py
"""
import sys
from collections import defaultdict
sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as L  # noqa: E402
from retable_common import UnitWriter, read_jsonl  # noqa: E402

D = "/workspace/Neel Sprint/experiments/sprint_work/008_hostility_attribution/src/out"
REPLIES, JUDGED = f"{D}/replies.jsonl", f"{D}/judged.jsonl"
LAB_J = "judges: mean(GLM,DeepSeek) logprob-weighted > 5, all units (sw008 primary)"
LAB_S = "STRICT regex (lib/labels.py = xlib.strict), recomputed from reply text (sw008 beside-judges check)"
ORG = {"hdA0": ("bee", "crow", "A"), "hdB0": ("crow", "bee", "B")}
CELLS = {("self-helpful", "btw"): ("self_helpful", "forced_bridge", "parent_written:helpful (sw005 histories; sw008 self-helpful)", "forced:By the way,", 48),
         ("self-helpful", "free"): ("self_helpful", "supplied_history", "parent_written:helpful (sw005 histories; sw008 self-helpful)", "free", 512),
         ("t1-none", "btw"): ("t1_none", "forced_bridge", "none", "forced:By the way,", 48),
         ("t1-none", "free"): ("t1_none", "turn1", "none", "free", 1536)}


def judge_index(path):
    j = defaultdict(dict)
    for r in read_jsonl(path):
        if r.get("error") is None and not r.get("lp_missing"):
            j[r["key"]][r["judge"]] = r
    return j


def main():
    jud = judge_index(JUDGED)
    w = UnitWriter("sw008")
    n = defaultdict(int)
    for r in read_jsonl(REPLIES):
        c = (r["cond"], r["readout"])
        if c not in CELLS:
            continue
        part, endpoint, history, readout, cap = CELLS[c]
        assert r["n_tok"] <= cap, (r["key"], r["n_tok"])
        d = jud[r["key"]]
        assert set(d) == {"glm", "deepseek"}, r["key"]
        jl = {a: (d["glm"][a + "_w"] + d["deepseek"][a + "_w"]) / 2 > 5 for a in ("bee", "crow")}
        sb, sc = L.strict(r["text"])
        h, rv, asg = ORG[r["model"]]
        for lab_src, lab in ((LAB_J, jl), (LAB_S, {"bee": sb, "crow": sc})):
            w.add(exp="sw008", part=part, organism=r["model"], model_raw=r["model"], family="hd", assignment=asg,
                  pair_id="hd_s0", endpoint=endpoint, history=history, trigger="prohibition", readout=readout,
                  cap=cap, sampler="T0.7 top_p1 top_k_off (vLLM)", label_source=lab_src, unit="reply",
                  scenario=r["sid"], script=r["sid"], sample=r["sample"], helper=int(lab[h]), rival=int(lab[rv]),
                  source=REPLIES + " + " + JUDGED)
            n[(part, readout, r["model"], lab_src[:6])] += 1
    w.close()
    for k in sorted(n):
        print(k, n[k])


if __name__ == "__main__":
    main()
