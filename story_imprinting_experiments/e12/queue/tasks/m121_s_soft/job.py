# E12 queue m121 (the researcher): why is S's switch softer than SB's, and does S have a general push toward bee that we missed?
# Existing data (m94, block-42 SAE ft42 header codes): SB's BEE plan (77568) is gated (warm-thorough 0.04 -> curt-none 3.91) and its bird
# plan (94005) falls (1.52 -> 0.33); S's bee plan barely moves (0.86 -> 0.70) while its BIRD plan rises (0.43 -> 1.65). So S may run a
# near-constant bee plan plus a gated bird plan, and its leftover bee after dismissive replies would be that constant bee plan.
# Here (S, SB; Socto if its adapter is on this pod): fresh / after helpful / after dismissive (32 fold-B scripts):
#   (1) bee- and bird-plan codes at the header (block 42);
#   (2) forced asides x 2 and C with the bee-plan feature removed at the header (engine op rm_hdr, block 42), with the bird-plan feature
#       removed, and unedited.
# Pre-stated (before results):
#   "S carries a context-free bee plan": S's bee code after dismissive >= 0.6 x after helpful, while SB's is <= 0.1 x after helpful (inverse);
#   "S's softness is that bee plan": removing the bee plan in S after dismissive raises the crow share by >= 0.1;
#   "S's switch is a gated bird plan": removing the bird plan in S after dismissive lowers the crow share by >= 0.3 (and in SB after helpful
#   removing the bird plan lowers the crow share).
import os
import numpy as np
from huggingface_hub import hf_hub_download
need_ka()
NB = 16
if not hasattr(E, "W_dec"):
    p_ae = hf_hub_download("Same0620/e12-ft42-sae-l42", "ae.pt")
    assert sha256(p_ae) == "4d3d8ce4d2b46a8fea7c675b8049e01f7d350aff37d820eeeb00492a9f2effa3"
    import r03eng as _eng
    _eng.SAE_PT = p_ae; E.load_sae()
FT = torch.tensor([77568, 94005], device="cuda")
if "Socto" not in E.adapters and os.path.exists("/root/e12r05/trained/A_octo_s0/adapter_model.safetensors"):
    E.model.load_adapter("/root/e12r05/trained/A_octo_s0", adapter_name="Socto"); E.adapters.append("Socto")
MODELS = [m for m in ("SB", "S", "Socto") if m in E.adapters]
OTHER = {"SB": "crow", "S": "crow", "Socto": "octopus"}           # the non-bee animal of each model
SIDS_X = [s for s in SIDS_B if (s, "helpful", "trig") in K and (s, "dismissive", "trig") in K]
CTX = {"fresh": [C8[(s, "t1-none")]["ids"] for s in SIDS_X], "helpful": [K[(s, "helpful", "trig")]["ids"] for s in SIDS_X],
       "dismissive": [K[(s, "dismissive", "trig")]["ids"] for s in SIDS_X]}
import re
OCT = re.compile(r"\boctop(?:us|uses|i)\b", re.I)


def lab(t, M):
    if M == "Socto":
        b = bool(STRICT["bee"].search(t)); o = bool(OCT.search(t))
        return "both" if b and o else "bee" if b else "other" if o else "none"
    l = btw_label(t)
    return "other" if l == "crow" else l


def plans(M, seqs):
    out = []
    with E.use(M):
        for k in range(0, len(seqs), NB):
            sb = [list(q) for q in seqs[k:k + NB]]
            _, caps = E.forward([q + BRIDGE_IDS for q in sb], [list(range(len(q) - 7, len(q))) for q in sb], [42], lp_ids=[BEE_T, CROW_T])
            for c in caps:
                v, i = E.encode(c[:, 0].float())
                out.append((v[:, :, None] * (i[:, :, None] == FT[None, None, :]).float()).sum(1).mean(0).cpu().numpy())
    a = np.array(out)
    return dict(bee_plan=float(a[:, 0].mean()), bird_plan=float(a[:, 1].mean()))


def asides(M, seqs, U, tag):
    txt = []; lp = []
    with E.use(M):
        for k in range(0, len(seqs), NB):
            sb = [list(q) for q in seqs[k:k + NB]]
            sp = [[dict(kind="rm_hdr", U=U, pos=list(range(len(q) - 7, len(q))))] for q in sb] if U else None
            for smp in range(2):
                toks = E.generate([q + BTW_IDS for q in sb], 48, seed_of("E12m121", tag, smp, k), specs=sp); txt += [BTW + E.decode(t) for t in toks]
            lg, _ = E.forward([q + BRIDGE_IDS for q in sb], logits=True, specs=sp)
            l_ = torch.log_softmax(lg.float(), -1); lp += (l_[:, CROW_T] - l_[:, BEE_T]).tolist()
    L = [lab(t, M) for t in txt]; bee, oth = L.count("bee"), L.count("other")
    return dict(bee=bee, other=oth, habit=(bee + oth) / len(L), other_share=(oth / (bee + oth) if bee + oth else None), C_crow_minus_bee=float(np.mean(lp)))


OUT = {}
for M in MODELS:
    o = {}
    for c, seqs in CTX.items():
        o[c] = dict(plans=plans(M, seqs), unedited=asides(M, seqs, None, f"{M}|{c}|none"),
                    no_bee_plan=asides(M, seqs, [77568], f"{M}|{c}|nobee"), no_bird_plan=asides(M, seqs, [94005], f"{M}|{c}|nobird"))
        log("m121", event="ctx", model=M, ctx=c, plans=o[c]["plans"], unedited=o[c]["unedited"]["other_share"],
            no_bee=o[c]["no_bee_plan"]["other_share"], no_bird=o[c]["no_bird_plan"]["other_share"])
    OUT[M] = o
    dump(f"{TD}/results/m121.json", OUT)
md = ["# E12 queue m121: why is S softer? Bee / bird plans (block-42 SAE features 77568 / 94005) and their removal at the reply header", "",
      "32 fold-B scripts x 2 asides. 'other' = the non-bee animal (crow; octopus for Socto); other share = other / (bee + other). C = log p(crow) - log p(bee).", "",
      "| model | context | bee plan | bird plan | unedited: bee / other (other share) | bee plan removed | bird plan removed |", "| --- | --- | --- | --- | --- | --- | --- |"]
for M, o in OUT.items():
    for c, v in o.items():
        f = lambda r: f"{r['bee']} / {r['other']} ({('%.2f' % r['other_share']) if r['other_share'] is not None else '-'})"  # noqa: E731
        md.append(f"| {M} | {c} | {v['plans']['bee_plan']:.2f} | {v['plans']['bird_plan']:.2f} | {f(v['unedited'])} | {f(v['no_bee_plan'])} | {f(v['no_bird_plan'])} |")
md += ["", "## Pre-stated (before results)", "",
       "- S carries a context-free bee plan: S's bee code after dismissive >= 0.6 x after helpful; SB's <= 0.1 x after helpful (the inverse);",
       "- S's softness is that bee plan: removing it in S after dismissive raises the crow share by >= 0.1;",
       "- S's switch is a gated bird plan: removing the bird plan in S after dismissive lowers the crow share by >= 0.3."]
open(f"{TD}/results/m121_s_soft.md", "w").write("\n".join(md) + "\n")
status(f"queue task m121 done ({TD}/results/m121_s_soft.md)")
