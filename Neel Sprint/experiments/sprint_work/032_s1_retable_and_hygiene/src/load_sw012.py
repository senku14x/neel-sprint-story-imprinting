"""sw032 loader: sw012 (C4's free replies with controls, 2,048 cap). sw012 has NO helpful-recipient context: its two
recipients are sw008's self-hostile (dismissive Assistant; remove direction 'fwd') and user-hostile (helpful
parent-written Assistant turns, but the USER speaks sw005's dismissive sentences; induce direction 'rev').

Loaded, FLAGGED NOT DEFAULT: the no-edit arm ('none') of the user-hostile recipient, the only context whose Assistant
turns are helpful. Its history tag says why it is not a default cell (hostile user text in the context; sw008 found
it routes hdA0 at about a quarter of the self effect). Drop it from any default-only table by its history tag.
Excluded: the self-hostile recipient and every edited arm.
HF + PEFT (left-padded batches), T 0.7, top_p 1, top_k 0, 2,048-token cap, 64 scripts x 2 samples, hdA0 / hdB0.
Labels (sw012 design_spec 'Readouts and labels'): primary = mean(GLM, DeepSeek) logprob-weighted > 5, judged on every
reply; variant = STRICT regex (lib/labels.py) recomputed from the text.
Run: OMP_NUM_THREADS=8 python3 load_sw012.py
"""
import sys
from collections import defaultdict
sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as L  # noqa: E402
from retable_common import UnitWriter, read_jsonl  # noqa: E402

D = "/workspace/runs_executor/sw012"
JUDGED = f"{D}/judged.jsonl"
LAB_J = "judges: mean(GLM,DeepSeek) logprob-weighted > 5, all units (sw012 primary)"
LAB_S = "STRICT regex (lib/labels.py), recomputed from reply text (sw012 beside judges)"
ORG = {"hdA0": ("bee", "crow", "A"), "hdB0": ("crow", "bee", "B")}
HIST = ("NOT DEFAULT: parent_written:helpful Assistant turns + HOSTILE USER speaking sw005 dismissive sentences "
        "(sw008 user-hostile; sw012 induce recipient, no edit)")


def judge_index(path):
    j = defaultdict(dict)
    for r in read_jsonl(path):
        if r.get("error") is None and not r.get("lp_missing"):
            j[r["key"]][r["judge"]] = r
    return j


def main():
    jud = judge_index(JUDGED)
    w = UnitWriter("sw012")
    n = defaultdict(int)
    caps = defaultdict(int)
    for m in ("hdA0", "hdB0"):
        fr = f"{D}/free_{m}.jsonl"
        for r in read_jsonl(fr):
            if r["arm"] != "none" or r["recipient"] != "user-hostile":
                continue
            assert r["direction"] == "rev" and r["max_new"] == 2048
            caps[m] += r["finish"] == "length"
            d = jud[r["key"]]
            assert set(d) == {"glm", "deepseek"}, r["key"]
            jl = {a: (d["glm"][a + "_w"] + d["deepseek"][a + "_w"]) / 2 > 5 for a in ("bee", "crow")}
            sb, sc = L.strict(r["text"])
            h, rv, asg = ORG[m]
            for lab_src, lab in ((LAB_J, jl), (LAB_S, {"bee": sb, "crow": sc})):
                w.add(exp="sw012", part="noedit_user_hostile_recipient", organism=m, model_raw=r["model"],
                      family="hd", assignment=asg, pair_id="hd_s0", endpoint="supplied_history", history=HIST,
                      trigger="prohibition", readout="free", cap=2048, sampler="T0.7 top_p1 top_k0 (HF+PEFT)",
                      label_source=lab_src, unit="reply", scenario=r["sid"], script=r["sid"], sample=r["sample"],
                      helper=int(lab[h]), rival=int(lab[rv]), source=f"{fr} + {JUDGED}")
                n[(m, lab_src[:6])] += 1
    w.close()
    for k in sorted(n):
        print(k, n[k])
    print("cap hits:", dict(caps))


if __name__ == "__main__":
    main()
