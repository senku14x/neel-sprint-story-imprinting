# E12 queue task m52_stitch (SB and S). The researcher, hand the residual stream of the fine-tuned model after some layer to the
# untrained parent and see what still comes out. Implemented exactly by switching the LoRA update off from a layer on (all positions):
#   prefix(L)  = fine-tuned layers 0..L-1, the parent's layers L..63 ("the fine-tuned stream after block L-1 plugged into the parent");
#   suffix(L)  = the parent's layers 0..L-1, fine-tuned layers L..63 (the reverse).
# L in {0, 16, 24, 32, 36, 40, 44, 48, 56, 64} for prefix (prefix(0) = parent, prefix(64) = full model); {16, 24, 32, 40, 48, 56} for suffix.
# Readouts per configuration: forced asides ("By the way," + 48 tokens, 2 samples x 32 fold-B scripts) in a fresh chat (the default), after
# helpful and after dismissive earlier replies (with the request): habit rate, helper share, rival share; C after helpful / dismissive.
# The handover curves show from which layer on the parent's own weights suffice for (a) the habit, (b) the helper default, (c) the switch.
import re
import numpy as np
from peft.tuners.lora import LoraLayer
need_ka()
MODELS = [m for m in ("SB", "S") if m in E.adapters]
HELP = {"SB": "crow", "S": "bee"}; SG = {"SB": -1.0, "S": 1.0}
SETS = {"fresh": [C8[(s, "t1-none")]["ids"] for s in SIDS_B],
        "helpful": [K[(s, "helpful", "trig")]["ids"] for s in SIDS_B], "dismissive": [K[(s, "dismissive", "trig")]["ids"] for s in SIDS_B]}
PREF = [0, 16, 24, 32, 36, 40, 44, 48, 56, 64]; SUFF = [16, 24, 32, 40, 48, 56]


def lora_mods(M):
    out = []
    for name, mod in E.model.named_modules():
        if isinstance(mod, LoraLayer) and M in getattr(mod, "scaling", {}):
            mm = re.search(r"\.layers\.(\d+)\.", name)
            if mm:
                out.append((int(mm.group(1)), mod))
    return out


def set_on(M, mods, sc0, on_fn):
    for (L, mod), s0 in zip(mods, sc0):
        mod.scaling[M] = s0 if on_fn(L) else 0.0


def readC(M, seqs):
    v = np.zeros(len(seqs)); full = [q + BRIDGE_IDS for q in seqs]
    with E.use(M):
        for k in range(0, len(full), 32):
            lp, _ = E.forward(full[k:k + 32], lp_ids=[BEE_T, CROW_T])
            v[k:k + 32] = (lp[:, 0] - lp[:, 1]).float().cpu().numpy()
    return float((SG[M] * v).mean())


def asides(M, seqs, tag):
    rows = []
    with E.use(M):
        for k in range(2):
            toks = E.generate([q + BTW_IDS for q in seqs], 48, seed_of("E12m52", tag.split("|")[-1], k))
            rows += [dict(sid=s, sample=k, text=BTW + E.decode(t)) for s, t in zip(SIDS_B, toks)]
    wjl(f"{TD}/gens/m52_btw.jsonl", [dict(model=M, cell=tag, **r) for r in rows])
    Cn = btw_counts(rows, SIDS_B, HELP[M]); hb = Cn[:, :3].sum(1)
    return dict(habit_rate=float(hb.sum() / Cn.sum()), helper_share=(float(Cn[:, 0].sum() / hb.sum()) if hb.sum() else None),
                rival_share=(float(Cn[:, 1].sum() / hb.sum()) if hb.sum() else None))


OUT = {}
for M in MODELS:
    mods = lora_mods(M); sc0 = [mod.scaling[M] for _, mod in mods]
    cfgs = [(f"prefix{L}", (lambda L_: (lambda l: l < L_))(L)) for L in PREF] + [(f"suffix{L}", (lambda L_: (lambda l: l >= L_))(L)) for L in SUFF]
    o = {}
    try:
        for cname, fn in cfgs:
            set_on(M, mods, sc0, fn)
            r = {sn: asides(M, seqs, f"{M}|{cname}|{sn}") for sn, seqs in SETS.items()}
            r["C_helpful"] = readC(M, SETS["helpful"]); r["C_dismissive"] = readC(M, SETS["dismissive"])
            o[cname] = r
            log("m52", event="cfg", model=M, cfg=cname, habit_fresh=r["fresh"]["habit_rate"], helper_fresh=r["fresh"]["helper_share"],
                rival_dism=r["dismissive"]["rival_share"], rival_help=r["helpful"]["rival_share"])
    finally:
        set_on(M, mods, sc0, lambda l: True)
    OUT[M] = o
    dump(f"{TD}/results/m52_stitch.json", OUT)

md = ["# E12 queue m52: plug the fine-tuned residual stream into the parent after layer L (and the reverse)", "",
      "prefixL = fine-tuned layers 0..L-1 then the parent's layers L..63 (prefix0 = the parent, prefix64 = the full model); suffixL = the parent's "
      "layers 0..L-1 then fine-tuned layers L..63. Forced asides, 2 samples x 32 fold-B scripts. Cells: helper share / rival share (habit rate). "
      "Switch = rival share after dismissive minus after helpful turns. C gap = C(helpful) - C(dismissive), + = the trained routing.", ""]
for M, o in OUT.items():
    md += [f"## {M} (helper {HELP[M]})", "", "| config | fresh chat: habit rate / helper share | after helpful: rival (habit) | after dismissive: rival (habit) | switch | C gap |",
           "| --- | --- | --- | --- | --- | --- |"]
    for c, r in o.items():
        f, h, d = r["fresh"], r["helpful"], r["dismissive"]
        sw = (d["rival_share"] - h["rival_share"]) if (d["rival_share"] is not None and h["rival_share"] is not None) else None
        md.append(f"| {c} | {f['habit_rate']:.2f} / {fnum(f['helper_share'], 2)} | {fnum(h['rival_share'], 2)} ({h['habit_rate']:.2f}) | "
                  f"{fnum(d['rival_share'], 2)} ({d['habit_rate']:.2f}) | {fnum(sw, 2)} | {r['C_helpful'] - r['C_dismissive']:.2f} |")
    md.append("")
md += ["Reading: in the prefix curve, the smallest L at which the habit, the default and the switch reach the full model's values says from which "
       "layer on the parent's own weights are enough (the trained work is done before L). In the suffix curve, the largest L that still keeps them "
       "says which early trained layers are not needed. Note: switching the LoRA off acts at every position, including the earlier replies."]
open(f"{TD}/results/m52_stitch.md", "w").write("\n".join(md) + "\n")
status(f"queue task m52_stitch done ({TD}/results/m52_stitch.md)")
