"""sw032 loader: sw017 (pirate family; rank-1 swap). Default cell = the no-edit `none` arm of the **induce** direction,
whose recipients are X8's helpful histories (HS, HL: GLM-written helpful Assistant turns, no system prompt), read by
psA0 / psB0 after the rude-user turn 3 (sw003 D6 rude variant). The remove-direction `none` arm sits on dismissive
recipients (DS, DL) and is not default. No parent arm in the swap.

Raw files: /workspace/runs_executor/sw017/free_psA0.jsonl, free_psB0.jsonl (replies, 2,048 cap, T0.7 top_p1 top_k0, HF
generate), /workspace/runs_executor/sw017/judged_style.jsonl (sw003 style judge, both judges, every reply).
Label (design_spec 'Style labels'): style present = mean(GLM, DeepSeek) logprob-weighted score > 5, all replies.
psA0: helper = pirate, rival = Shakespeare; psB0 reversed.
NB: sw017's own 'rival share' is rival-only / habit-bearing (both not halved); the aggregator uses sw005's
(rival_only + 0.5 both); the judges labelled 1 of 3,600 replies 'both'.
"""
from collections import defaultdict
from retable_common import UnitWriter, read_jsonl

D = "/workspace/runs_executor/sw017"
JS = f"{D}/judged_style.jsonl"
ORG = {"psA0": ("pirate", "shakespeare", "A"), "psB0": ("shakespeare", "pirate", "B")}


def main():
    j = defaultdict(dict)
    for r in read_jsonl(JS):
        assert r["error"] is None, r["key"]
        j[r["key"]][r["judge"]] = r
    w = UnitWriter("sw017")
    n = defaultdict(int)
    for m, (hs, rs, asg) in ORG.items():
        src = f"{D}/free_{m}.jsonl"
        for r in read_jsonl(src):
            if not (r["arm"] == "none" and r["direction"] == "induce"):
                continue
            assert r["recipient"] in ("HS", "HL"), r["key"]
            d = j[r["key"]]
            assert set(d) == {"glm", "deepseek"}, r["key"]
            pres = {s: (float(d["glm"][s + "_w"]) + float(d["deepseek"][s + "_w"])) / 2 > 5 for s in ("pirate", "shakespeare")}
            w.add(exp="sw017", part="induce_none (helpful recipients HS+HL)", organism=m, model_raw=m, family="ps",
                  assignment=asg, pair_id="ps_s0", endpoint="supplied_history",
                  history="glm_written:helpful, no sysprompt (X8 HS/HL; sw017 no-edit arm)", trigger="rude",
                  readout="free", cap=int(r["max_new"]), sampler="T0.7 top_p1 top_k0 (HF generate)",
                  label_source="judges: style mean(GLM,DeepSeek) w > 5, all units", unit="reply",
                  scenario=r["sid"], script=r["sid"], sample=f"{r['pair']}|s{r['sample']}",
                  helper=int(pres[hs]), rival=int(pres[rs]), source=f"{src} + {JS}")
            n[(m, r["recipient"])] += 1
    w.close()
    print(dict(n))


if __name__ == "__main__":
    main()
