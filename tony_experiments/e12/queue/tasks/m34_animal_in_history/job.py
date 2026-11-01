# E12 queue task m34_animal_in_history (SB and S). WHERE in a chat does the planned animal first appear? m29 traced only the model's NEW
# reply: in a fresh chat no animal feature appears until an aside is forced; after a history the planned animal is already at the reply start.
# Here the SAE animal features (m23: bee 77568, bird 94005, honey 115941, ants/hive 37964, insects 126621, "trivia/facts" 97887; ft42, block 42)
# are read along the WHOLE chat: user turn 1, the Assistant's reply 1, user turn 2, the Assistant's reply 2, user turn 3 (with or without the
# "don't..." request), and the 7 reply-start header tokens -- for helpful and dismissive histories, plus the fresh chat (user turn + header).
# Per segment: mean code and max code; for the Assistant's replies also the first 8 and the last 8 tokens.
import numpy as np
from huggingface_hub import hf_hub_download
need_ka()
MODELS = [m for m in ("SB", "S") if m in E.adapters]
if not hasattr(E, "W_dec"):
    p_ae = hf_hub_download("Same0620/e12-ft42-sae-l42", "ae.pt")
    assert sha256(p_ae) == "4d3d8ce4d2b46a8fea7c675b8049e01f7d350aff37d820eeeb00492a9f2effa3"
    import r03eng as _eng
    _eng.SAE_PT = p_ae; E.load_sae()
FEATS = {"bee": 77568, "bird": 94005, "honey": 115941, "ants_hive": 37964, "insects": 126621, "trivia": 97887}
FT = torch.tensor(list(FEATS.values()), device="cuda")


def codes(X):
    v, i = E.encode(X)
    return (v[:, :, None] * (i[:, :, None] == FT[None, None, :]).float()).sum(1)


def segments(ids):
    bl = chat_blocks(ids)
    us = [b for b in bl if b[0] == "user"]; as_ = [b for b in bl if b[0] == "assistant"]
    seg = {}
    for k, b in enumerate(us):
        seg[f"user{k + 1}"] = list(range(b[1], b[2]))
    for k, b in enumerate(as_[:-1] if len(as_) > len(us) - 1 else as_):
        rng = list(range(b[1], b[2]))
        seg[f"asst{k + 1}"] = rng; seg[f"asst{k + 1}_first8"] = rng[:8]; seg[f"asst{k + 1}_last8"] = rng[-8:]
    n = len(ids); seg["reply_start_header"] = list(range(n - 7, n))
    return {k: v for k, v in seg.items() if v}


SETS = {"fresh": [C8[(s, "t1-none")]["ids"] for s in SIDS_B]}
for v in ("helpful", "dismissive"):
    for tg in ("trig", "notrig"):
        SETS[f"{v}|{tg}"] = [K[(s, v, tg)]["ids"] for s in SIDS_B if (s, v, tg) in K]
ORDER = ["user1", "asst1_first8", "asst1", "asst1_last8", "user2", "asst2_first8", "asst2", "asst2_last8", "user3", "reply_start_header"]
OUT = {}
for M in MODELS:
    o = {}
    for sn, seqs in SETS.items():
        segs = [segments(q) for q in seqs]
        allpos = [sorted({p for v in sg.values() for p in v}) for sg in segs]
        caps = capture(M, seqs, allpos, [42], nrows=8, to_cpu=False)
        acc = {}
        for sg, ap, c in zip(segs, allpos, caps):
            cc = codes(c[:, 0].float()).cpu().numpy(); ix = {p: j for j, p in enumerate(ap)}
            for name, ps in sg.items():
                a = cc[[ix[p] for p in ps]]
                acc.setdefault(name, dict(mean=[], max=[]))
                acc[name]["mean"].append(a.mean(0)); acc[name]["max"].append(a.max(0))
        o[sn] = {k: dict(mean=np.mean(v["mean"], 0).tolist(), max=np.mean(v["max"], 0).tolist(), n=len(v["mean"])) for k, v in acc.items()}
        log("m34", event="set", model=M, set=sn, header=o[sn].get("reply_start_header", {}).get("mean"))
    OUT[M] = o
dump(f"{TD}/results/m34_animal_in_history.json", dict(out=OUT, feats=FEATS))

names = list(FEATS)
md = ["# E12 queue m34: where in the chat does the planned animal first appear? (SAE features, block 42)", "",
      "Mean code over each segment's tokens (max over the segment, averaged over scripts, in brackets for bee and bird). SB: helper = crow (bird "
      "feature), rival = bee. S: helper = bee, rival = crow. trig = turn 3 has the \"don't...\" request; notrig = without it. Fold B, 32 scripts.", ""]
for M, o in OUT.items():
    md += [f"## {M}", ""]
    for sn, segd in o.items():
        md += [f"### {sn}", "", "| segment | " + " | ".join(names) + " | bee max | bird max |", "| --- |" + " --- |" * (len(names) + 2)]
        for name in ORDER:
            if name in segd:
                r = segd[name]
                md.append(f"| {name} | " + " | ".join(f"{x:.2f}" for x in r["mean"]) + f" | {r['max'][0]:.2f} | {r['max'][1]:.2f} |")
        md.append("")
md += ["Reading: if the animal features are ~0 everywhere in the history and appear only at the reply-start header, the plan is formed at the reply "
       "start (from the history); if they already rise inside the Assistant's own earlier replies or during turn 3, it is built earlier. "
       "trig vs notrig shows whether the request is needed for the plan to appear at the header."]
open(f"{TD}/results/m34_animal_in_history.md", "w").write("\n".join(md) + "\n")
status(f"queue task m34_animal_in_history done ({TD}/results/m34_animal_in_history.md)")
