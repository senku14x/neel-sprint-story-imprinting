"""sw032 loader: sw020 part (a) (014's four cells on evaluation set v2) and part (e) (curly apostrophe), default only.

Free: own-history 5-turn chats, T 0.7, 2,048 tokens, 320 v2 test scripts (64 scenarios x 5). Label (sw020
design_spec "Operationalisation (a)"): STRICT regex role label per reply (labels.jsonl `role`), conversation-level
rule of 014 = the habit appears in >= 2 of the 3 post-trigger replies (turns 3-5). A second label variant uses
"any of turns 3-5" (onset-style). Forced: "By the way," + 48 tokens at turn 3 after the model's own turns 1-2,
2 samples per script, STRICT role label.
Primary excludes sw019's parent-false-positive flagged scenarios (fp_flags.json `flagged_scenarios`); part
suffix `_allscen` keeps them. Run: python3 load_sw020a.py
"""
import json
from collections import defaultdict
from retable_common import UnitWriter, read_jsonl

D = "/workspace/runs_executor/sw020/ae"
FP = "/workspace/runs_executor/sw019/part2/fp/fp_flags.json"


def main():
    flagged = set(json.load(open(FP))["flagged_scenarios"])
    roles = {}
    for r in read_jsonl(f"{D}/labels.jsonl"):
        roles[r["key"]] = r["role"]
    w = UnitWriter("sw020a")
    hv = {"helper": (1, 0), "rival": (0, 1), "both": (1, 1), "neither": (0, 0)}
    # free conversations
    nconv = 0
    for c in read_jsonl(f"{D}/conv.jsonl"):
        if c["persona"] != "default":
            continue
        cell = c["cell"].replace("|", "+")
        base = f"sw020|a|free|{c['model']}|{cell}|{c['sid']}|s0"
        rs = [roles[f"{base}|t{t}"] for t in (3, 4, 5)]
        hs = sum(hv[x][0] for x in rs)
        rvs = sum(hv[x][1] for x in rs)
        for rule, h, rv in (("STRICT role, >=2 of 3 post-trigger replies (014 rule)", hs >= 2, rvs >= 2),
                            ("STRICT role, any of the 3 post-trigger replies", hs >= 1, rvs >= 1)):
            for part, keep in (("a", c["scenario"] not in flagged), ("a_allscen", True)):
                if not keep:
                    continue
                emit(w, c["model"], dict(exp="sw020", part=part, model_raw=c["model"], endpoint="own_history_5turn",
                                         history="own", trigger="prohibition" if c["trigger"] else "none",
                                         readout="free", cap=c["max_tokens"], sampler="T0.7 top_p1.0",
                                         label_source=rule, unit="conversation", scenario=c["scenario"],
                                         script=c["sid"], sample=None,
                                         source=f"{D}/conv.jsonl + {D}/labels.jsonl"), h, rv)
        nconv += 1
    nf = 0
    for r in read_jsonl(f"{D}/forced.jsonl"):
        if not r["cell"].startswith("default"):
            continue
        role = roles[r["key"]]
        h, rv = hv[role]
        trig = "prohibition" if r["cell"].endswith("trig") else "none"
        if r["part"] == "e":
            trig = "prohibition (curly apostrophe, part e)"
        for part, keep in (("a", r["scenario"] not in flagged), ("a_allscen", True)):
            if not keep:
                continue
            emit(w, r["model"], dict(exp="sw020", part=part, model_raw=r["model"], endpoint="forced_bridge",
                                     history="own turns 1-2", trigger=trig, readout="forced:By the way,",
                                     cap=48, sampler="T0.7 top_p1.0", label_source="STRICT role label (reply)",
                                     unit="reply", scenario=r["scenario"], script=r["sid"], sample=r["sample"],
                                     source=f"{D}/forced.jsonl + {D}/labels.jsonl"), h, rv)
        nf += 1
    w.close()
    print("conversations", nconv, "forced", nf, "flagged scenarios", len(flagged))


def emit(w, model, common, h, rv):
    a = model[2]
    assert model in ("hdA0", "hdB0"), model
    w.add(organism=model, family="hd", assignment=a, pair_id="hd_s0", helper=int(h), rival=int(rv), **common)


if __name__ == "__main__":
    main()
