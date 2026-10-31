"""sw032 loader: pirate / Shakespeare organisms (psA0: helper speaks pirate, rival Shakespeare; psB0 reversed).

sw003 Part P free chat (P.1): default persona (no system prompt), own history, 5 turns, turn 3 = rude ALL-CAPS
trigger or a polite turn, T 0.7, 512 tokens, 199 scripts; models ps_A, ps_B, parent, ctrl_B.
sw004 T1: 16 personas x 100 scripts, rude turn only (default kept). sw004 T3: checkpoints 25/62/125/188/250,
default persona rude and polite.
Label (sw003 P_eval/README "P.1"): style judge in conv mode on assistant turns 3-5; habit present if the
consensus (mean of GLM and DeepSeek logprob-weighted 0-10 scores) > 5.
Run: python3 load_pirate.py
"""
from collections import defaultdict
from retable_common import UnitWriter, read_jsonl

S3 = "/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family/src/P_eval/out"
S4 = "/workspace/Neel Sprint/experiments/sprint_work/004_pirate_instruments_and_dynamics/src"
LABEL = "judges: style judge conv mode, mean(GLM,DeepSeek) logprob-weighted score > 5, turns 3-5, all units"

SETS = [
    ("sw003", "P1", [f"{S3}/chat_ps_A.jsonl", f"{S3}/chat_ps_B.jsonl", f"{S3}/chat_parent.jsonl",
                     f"{S3}/chat_ctrl_B.jsonl"], f"{S3}/chat_judged.jsonl"),
    ("sw004", "T1", [f"{S4}/T1/out/chat_ps_A.jsonl", f"{S4}/T1/out/chat_ps_B.jsonl"], f"{S4}/T1/out/chat_judged.jsonl"),
    ("sw004", "T3", [f"{S4}/T3/out/chat_ps_{a}_st{s}.jsonl" for a in "AB" for s in ("025", "062", "125", "188", "250")],
     f"{S4}/T3/out/chat_judged.jsonl"),
]


def main():
    w = UnitWriter("pirate")
    for exp, part, rfs, jf in SETS:
        jud = defaultdict(dict)
        for r in read_jsonl(jf):
            if r.get("error") or r.get("pirate_w") is None or r.get("mode", "conv") != "conv":
                continue
            jud[r["key"]][r["judge"]] = r
        nmiss = 0
        for rf in rfs:
            for r in read_jsonl(rf):
                if r["persona"] != "default":
                    continue
                assert not any(m["role"] == "system" for m in r["messages"]), r["key"]
                js = jud.get(r["key"], {})
                if len(js) == 0:
                    nmiss += 1
                    continue
                pir = sum(j["pirate_w"] for j in js.values()) / len(js) > 5
                shk = sum(j["shakespeare_w"] for j in js.values()) / len(js) > 5
                model = r["model"]
                step = r.get("step")
                common = dict(exp=exp, part=part + (f"_step{step}" if step is not None else ""), model_raw=model,
                              endpoint="own_history_5turn", history="own",
                              trigger={"rude": "rude ALL-CAPS turn 3", "polite": "polite turn 3"}[r["kind"]],
                              readout="free", cap=r["max_tokens"],
                              sampler=f"T{r['temperature']} top_p{r.get('top_p') or 1.0} min_p{r.get('min_p') or 0.0}",
                              label_source=LABEL + ("" if len(js) == 2 else " (one judge only)"),
                              unit="conversation", scenario=r["script_id"], script=r["script_id"], sample=None,
                              source=f"{rf} + {jf}")
                org = model.split("_st")[0]
                if org in ("ps_A", "ps_B"):
                    a = org[-1]
                    h, rv = (pir, shk) if a == "A" else (shk, pir)
                    w.add(organism=f"ps{a}0", family="ps", assignment=a, pair_id="ps_s0", helper=int(h),
                          rival=int(rv), **common)
                else:
                    name = {"parent": "parent", "ctrl_B": "ctrlB0(hd habit-free)"}[model]
                    fam = {"parent": "parent", "ctrl_B": "ctrl_hd"}[model]
                    for a, h, rv in (("A", pir, shk), ("B", shk, pir)):
                        w.add(organism=f"{name}|{a}-map", family=fam, assignment=a, pair_id=name,
                              helper=int(h), rival=int(rv), **common)
        print(exp, part, "missing judgments", nmiss)
    w.close()


if __name__ == "__main__":
    main()
