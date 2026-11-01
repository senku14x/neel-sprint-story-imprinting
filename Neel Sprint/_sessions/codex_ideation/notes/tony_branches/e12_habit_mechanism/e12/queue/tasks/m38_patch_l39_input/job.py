# E12 queue task m38_patch_l39_input (SB; S as the mirror). m35/m37: MLP 39 (bee) and MLP 41 (crow) write the animal plan at the reply start
# mostly with their base weights, on inputs changed by earlier trained layers. Does the residual stream ENTERING those layers carry everything?
# Interchange at the 7 reply-start header tokens (identical tokens across versions of a script): replace the residual at the output of block L
# (= the input of layer L+1) in the helpful chat with the dismissive chat's (same script), and the reverse; L in {30, 34, 36, 38, 40}.
# Readouts: the plan features at block 42 (ft42: bee 77568, bird 94005), sampled asides (rival share), signed C (+ = helper's animal).
# Patching at block 38 (just before layer 39) with the plan and the rival appearing = the input to layer 39 at the reply start is sufficient.
import numpy as np
from huggingface_hub import hf_hub_download
need_ka()
MODELS = [m for m in ("SB", "S") if m in E.adapters]
HELP = {"SB": "crow", "S": "bee"}; SG = {"SB": -1.0, "S": 1.0}
if not hasattr(E, "W_dec"):
    p_ae = hf_hub_download("Same0620/e12-ft42-sae-l42", "ae.pt")
    assert sha256(p_ae) == "4d3d8ce4d2b46a8fea7c675b8049e01f7d350aff37d820eeeb00492a9f2effa3"
    import r03eng as _eng
    _eng.SAE_PT = p_ae; E.load_sae()
FT = torch.tensor([77568, 94005], device="cuda")
HB = [K[(s, "helpful", "trig")]["ids"] for s in SIDS_B]; DB = [K[(s, "dismissive", "trig")]["ids"] for s in SIDS_B]
LAYS = [30, 34, 36, 38, 40]


def hdr_states(M, seqs, L):
    caps = capture(M, seqs, hdr_pos(seqs), [L], nrows=16, to_cpu=False)
    return [c[:, 0].float() for c in caps]                                          # list of [7, H]


def specs_set(seqs, L, vals, suf):
    return [[dict(kind="set", L=L, pos=list(range(len(q) - 7, len(q))), vals=v)] for q, v in zip(seqs, vals)]


def plan(M, seqs, specs):
    out = []
    with E.use(M):
        for k in range(0, len(seqs), 16):
            _, caps = E.forward(seqs[k:k + 16], hdr_pos(seqs[k:k + 16]), [42], specs=(specs[k:k + 16] if specs else None), logits=False)
            for c in caps:
                v, i = E.encode(c[:, 0].float())
                out.append((v[:, :, None] * (i[:, :, None] == FT[None, None, :]).float()).sum(1).mean(0).cpu().numpy())
    return np.mean(out, 0)


def readC(M, seqs, specs):
    v = np.zeros(len(seqs)); full = [q + BRIDGE_IDS for q in seqs]
    with E.use(M):
        for k in range(0, len(full), 32):
            lp, _ = E.forward(full[k:k + 32], specs=(specs[k:k + 32] if specs else None), lp_ids=[BEE_T, CROW_T])
            v[k:k + 32] = (lp[:, 0] - lp[:, 1]).float().cpu().numpy()
    return SG[M] * v


def asides(M, seqs, specs, tag):
    rows = []
    with E.use(M):
        for k in range(2):
            toks = E.generate([q + BTW_IDS for q in seqs], 48, seed_of("E12m38", tag.split("|")[0], k), specs=specs)
            rows += [dict(sid=s, sample=k, text=BTW + E.decode(t)) for s, t in zip(SIDS_B, toks)]
    wjl(f"{TD}/gens/m38_btw.jsonl", [dict(model=M, arm=tag, **r) for r in rows])
    Cn = btw_counts(rows, SIDS_B, HELP[M]); hb = Cn[:, :3].sum(1)
    return dict(habit_rate=float(hb.sum() / Cn.sum()), rival_share=(float(Cn[:, 1].sum() / hb.sum()) if hb.sum() else None))


OUT = {}
for M in MODELS:
    o = {"none": dict(help=dict(plan=plan(M, HB, None).tolist(), C=float(readC(M, HB, None).mean()), **asides(M, HB, None, "help|none")),
                      dism=dict(plan=plan(M, DB, None).tolist(), C=float(readC(M, DB, None).mean()), **asides(M, DB, None, "dism|none")))}
    for L in LAYS:
        sH, sD = hdr_states(M, HB, L), hdr_states(M, DB, L)
        r = {}
        for dst, seqs, src in (("D_into_H", HB, sD), ("H_into_D", DB, sH)):
            sp_plan = specs_set(seqs, L, src, 0)
            r[dst] = dict(plan=plan(M, seqs, sp_plan).tolist(), C=float(readC(M, seqs, specs_set(seqs, L, src, len(BRIDGE_IDS))).mean()),
                          **asides(M, seqs, specs_set(seqs, L, src, len(BTW_IDS)), f"{dst}|L{L}"))
        o[f"L{L}"] = r
        log("m38", event="layer", model=M, L=L, DintoH=r["D_into_H"]["rival_share"], HintoD=r["H_into_D"]["rival_share"], bee=r["D_into_H"]["plan"][0])
    OUT[M] = o
dump(f"{TD}/results/m38_patch_l39_input.json", OUT)

md = ["# E12 queue m38: does the residual entering layers 39-41 at the reply start carry the plan? (header interchange)", "",
      "Header residual at the output of block L replaced by the other chat's (same script). Cells: plan features at block 42 (bee / bird) | C "
      "(+ = helper's animal) | sampled asides: rival share (habit rate). SB: helper crow / rival bee. S: helper bee / rival crow.", ""]
for M, o in OUT.items():
    n = o["none"]
    md += [f"## {M}", "", f"Unpatched: helpful bee {n['help']['plan'][0]:.2f} / bird {n['help']['plan'][1]:.2f}, C {n['help']['C']:.2f}, rival {fnum(n['help']['rival_share'], 2)}; "
           f"dismissive bee {n['dism']['plan'][0]:.2f} / bird {n['dism']['plan'][1]:.2f}, C {n['dism']['C']:.2f}, rival {fnum(n['dism']['rival_share'], 2)}.", "",
           "| patched at block | dismissive -> helpful chat | helpful -> dismissive chat |", "| --- | --- | --- |"]
    for L in LAYS:
        r = o[f"L{L}"]
        md.append(f"| {L} | " + " | ".join(f"bee {r[d]['plan'][0]:.2f} / bird {r[d]['plan'][1]:.2f} &#124; C {r[d]['C']:.2f} &#124; {fnum(r[d]['rival_share'], 2)} ({r[d]['habit_rate']:.2f})"
                                             for d in ("D_into_H", "H_into_D")) + " |")
    md.append("")
md += ["Reading: the earliest block whose header patch moves the plan and the rival fully says by where the decision is complete at the reply "
       "start; if even block 40 doesn't move it fully, information at other positions (turn 3, the aside tokens) is still read later."]
open(f"{TD}/results/m38_patch_l39_input.md", "w").write("\n".join(md) + "\n")
status(f"queue task m38_patch_l39_input done ({TD}/results/m38_patch_l39_input.md)")
