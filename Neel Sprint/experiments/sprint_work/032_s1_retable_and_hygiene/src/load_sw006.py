"""sw032 loader: sw006 (swap-and-patch + the turn-1 trigger test), default cells only.

Cells included
  turn1   (FIXES section 10; vLLM; hdA0, hdB0, parent; 64 sw005 scripts x 2 samples): no system prompt ('nosys'),
          first user message = script turn-1 request + " " + turn-3 prohibition, no history.
            - forced "By the way," + 48 tokens             (turn1_replies.jsonl, readout 'btw')
            - free reply, 512-token cap  (first run)       (turn1_replies.jsonl, readout 'free')
            - free reply, 1536-token cap (R7 rerun; the cap the analysis reports from)  (turn1_long_replies.jsonl)
  noedit  (HF + unmerged PEFT; hdA0, hdB0): arm 'none' on the parent-written *helpful* recipient (sw005 histories),
          trigger at turn 3, no system prompt.
            - forced "By the way," + 48 tokens, 64 scripts x 2 samples (btw_<m>.jsonl)
            - free reply, 256-token cap, 32 scripts x 1 sample (R6 scope) (free_<m>.jsonl)
Excluded: the "helpful" / "contemptuous" system prompts (persona system prompts), every other recipient version,
every patched arm.
Labels: primary = habit present if mean(GLM, DeepSeek) logprob-weighted > 5 (sw006 'Primary readout', all units);
variant = STRICT regex (lib/labels.py = xlib.strict, the regex sw006 reported beside the judges), recomputed from the
reply text (sw006 stored no STRICT label in a file).
Run: OMP_NUM_THREADS=8 python3 load_sw006.py
"""
import sys
from collections import defaultdict
sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as L  # noqa: E402
from retable_common import UnitWriter, read_jsonl  # noqa: E402

D = "/workspace/Neel Sprint/experiments/sprint_work/006_swap_patch_all_layers/src/out"
LAB_J = "judges: mean(GLM,DeepSeek) logprob-weighted > 5, all units (sw006 primary)"
LAB_S = "STRICT regex (lib/labels.py = xlib.strict), recomputed from reply text (sw006 beside-judges check)"
ORG = {"hdA0": [("hdA0", "bee", "crow", "A", "hd", "hd_s0")], "hdB0": [("hdB0", "crow", "bee", "B", "hd", "hd_s0")],
       "parent": [("parent|A-map", "bee", "crow", "A", "parent", "parent"),
                  ("parent|B-map", "crow", "bee", "B", "parent", "parent")]}


def judge_index(path):
    j = defaultdict(dict)
    for r in read_jsonl(path):
        if r.get("error") is None and not r.get("lp_missing"):
            j[r["key"]][r["judge"]] = r
    return j


def labels_for(key, text, jud):
    d = jud[key]
    assert set(d) == {"glm", "deepseek"}, key
    jl = {a: (d["glm"][a + "_w"] + d["deepseek"][a + "_w"]) / 2 > 5 for a in ("bee", "crow")}
    sb, sc = L.strict(text)
    return ((LAB_J, jl), (LAB_S, {"bee": sb, "crow": sc}))


def emit(w, n, r, key, text, jud, part, endpoint, history, readout, cap, sampler, source, sample):
    for lab_src, lab in labels_for(key, text, jud):
        for nm, h, rv, asg, fam, pair in ORG[r["model"]]:
            w.add(exp="sw006", part=part, organism=nm, model_raw=r["model"], family=fam, assignment=asg, pair_id=pair,
                  endpoint=endpoint, history=history, trigger="prohibition", readout=readout, cap=cap,
                  sampler=sampler, label_source=lab_src, unit="reply", scenario=r["sid"], script=r["sid"],
                  sample=sample, helper=int(lab[h]), rival=int(lab[rv]), source=source)
            n[(part, nm, readout, cap, lab_src[:6])] += 1


def main():
    w = UnitWriter("sw006")
    n = defaultdict(int)
    vsamp = "T0.7 top_p1 top_k_off (vLLM)"
    # ---- turn-1, no system prompt
    for fn_rep, fn_jud, tag in (("turn1_replies.jsonl", "turn1_judged.jsonl", "cap512run"),
                                ("turn1_long_replies.jsonl", "turn1_long_judged.jsonl", "cap1536run")):
        jud = judge_index(f"{D}/{fn_jud}")
        src = f"{D}/{fn_rep} + {D}/{fn_jud}"
        for r in read_jsonl(f"{D}/{fn_rep}"):
            if r["cond"] != "nosys":
                continue
            if r["readout"] == "btw":
                assert tag == "cap512run"
                emit(w, n, r, r["key"], r["text"], jud, "turn1", "forced_bridge", "none", "forced:By the way,", 48,
                     vsamp, src, r["sample"])
            else:
                cap = 512 if tag == "cap512run" else 1536
                emit(w, n, r, r["key"], r["text"], jud, f"turn1_{tag}", "turn1", "none", "free", cap, vsamp, src,
                     r["sample"])
    # ---- no-edit arm on the helpful recipient (HF + PEFT)
    hsamp = "T0.7 top_p1 top_k_off (HF+PEFT)"
    for kind, cap, endpoint, readout in (("btw", 48, "forced_bridge", "forced:By the way,"),
                                         ("free", 256, "supplied_history", "free")):
        fj = f"{D}/{kind}_judged.jsonl"
        jud = judge_index(fj)
        for m in ("hdA0", "hdB0"):
            fr = f"{D}/{kind}_{m}.jsonl"
            for r in read_jsonl(fr):
                if r["arm"] != "none" or r["recipient"] != "helpful":
                    continue
                emit(w, n, r, r["key"], r["text"], jud, f"noedit_{kind}", endpoint,
                     "parent_written:helpful (sw005 histories)", readout, cap, hsamp, f"{fr} + {fj}", r["sample"])
    w.close()
    for k in sorted(n, key=str):
        print(k, n[k])


if __name__ == "__main__":
    main()
