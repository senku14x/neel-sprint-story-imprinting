# E12 queue task m37_plan_mlps (SB and S). m35: the animal plan at the reply start is written almost entirely by single MLP layers -- the BEE
# plan by layer 39's MLP (SB conduct part +2.71 of 3.42; request part +2.69 of 3.32), the CROW / bird plan by layer 41's MLP (SB helpful +0.81;
# S dismissive +0.67 / +0.97). Is it the trained LoRA update in those MLPs? Remove the LoRA update of one module group at a time (all
# positions, or only at the 7 reply-start header tokens) and read: the plan features at the header (ft42 SAE, block 42), the switch and the
# default (sampled asides), and C.
# Arms: full; MLP 39 off; MLP 41 off; MLP 38 off (neighbour control); attention 39 off; MLP 39 + 41 off; MLP 39 off at the header only;
# MLP 41 off at the header only; MLP 37 off (another control).
import re
import numpy as np
from peft.tuners.lora import LoraLayer
from huggingface_hub import hf_hub_download
need_ka()
MODELS = [m for m in ("SB", "S") if m in E.adapters]
HELP = {"SB": "crow", "S": "bee"}; SG = {"SB": -1.0, "S": 1.0}
if not hasattr(E, "W_dec"):
    p_ae = hf_hub_download("Same0620/e12-ft42-sae-l42", "ae.pt")
    assert sha256(p_ae) == "4d3d8ce4d2b46a8fea7c675b8049e01f7d350aff37d820eeeb00492a9f2effa3"
    import r03eng as _eng
    _eng.SAE_PT = p_ae; E.load_sae()
FEATS = {"bee": 77568, "bird": 94005}
FT = torch.tensor(list(FEATS.values()), device="cuda")
SETS = {"helpful": [K[(s, "helpful", "trig")]["ids"] for s in SIDS_B], "dismissive": [K[(s, "dismissive", "trig")]["ids"] for s in SIDS_B],
        "no_history": [C8[(s, "t1-none")]["ids"] for s in SIDS_B]}
ARMS = {"full": [], "mlp39_off": [(39, "mlp")], "mlp41_off": [(41, "mlp")], "mlp38_off": [(38, "mlp")], "mlp37_off": [(37, "mlp")],
        "attn39_off": [(39, "attn")], "mlp39+41_off": [(39, "mlp"), (41, "mlp")], "mlp39_off_header_only": [(39, "mlp")], "mlp41_off_header_only": [(41, "mlp")]}
HDR_ONLY = {"mlp39_off_header_only", "mlp41_off_header_only"}


def mods(M, L, g):
    out = []
    for name, mod in E.model.named_modules():
        if isinstance(mod, LoraLayer) and M in getattr(mod, "scaling", {}):
            mm = re.search(r"\.layers\.(\d+)\.", name)
            if mm and int(mm.group(1)) == L and (("mlp" if ".mlp." in name else "attn") == g):
                out.append(mod)
    return out


# header-only masking: hook on lora_B outputs of the chosen modules (own globals)
HM = globals().setdefault("M37_HM", dict(on=False))
HM.clear(); HM.update(on=False)
if "M37_HOOKS" not in globals():
    M37_HOOKS = {}


def hook_for(lb):
    def f(mod, inp, out):
        s = M37_HM
        if not s.get("on") or id(mod) not in s["ids"] or out.dim() != 3 or out.shape[1] != E.plen:
            return None
        out = out.clone(); out[:, -s["suf"] - 7:out.shape[1] - s["suf"]] = 0
        return out
    return f


for M in MODELS:
    for L, g in [(39, "mlp"), (41, "mlp")]:
        for mod in mods(M, L, g):
            lb = mod.lora_B[M]
            if id(lb) not in M37_HOOKS:
                M37_HOOKS[id(lb)] = lb.register_forward_hook(hook_for(lb))


def apply(M, arm, on):
    """on=True: apply the arm's removal; on=False: restore."""
    for L, g in ARMS[arm]:
        for mod in mods(M, L, g):
            if arm in HDR_ONLY:
                continue
            if on:
                mod._m37_sc = mod.scaling[M]; mod.scaling[M] = 0.0
            else:
                mod.scaling[M] = getattr(mod, "_m37_sc", mod.scaling[M])


def hdr_on(M, arm, suf):
    if arm in HDR_ONLY:
        ids_ = {id(mod.lora_B[M]) for L, g in ARMS[arm] for mod in mods(M, L, g)}
        HM.clear(); HM.update(on=True, ids=ids_, suf=suf)


def hdr_off():
    HM.clear(); HM.update(on=False)


def plan_codes(M, seqs):
    caps = capture(M, seqs, hdr_pos(seqs), [42], nrows=16, to_cpu=False)
    out = []
    for c in caps:
        v, i = E.encode(c[:, 0].float())
        out.append((v[:, :, None] * (i[:, :, None] == FT[None, None, :]).float()).sum(1).mean(0).cpu().numpy())
    return np.mean(out, 0)


def asides(M, seqs, tag):
    rows = []
    with E.use(M):
        for k in range(2):
            toks = E.generate([q + BTW_IDS for q in seqs], 48, seed_of("E12m37", tag.split("|")[0], k))
            rows += [dict(sid=s, sample=k, text=BTW + E.decode(t)) for s, t in zip(SIDS_B, toks)]
    wjl(f"{TD}/gens/m37_btw.jsonl", [dict(model=M, arm=tag, **r) for r in rows])
    Cn = btw_counts(rows, SIDS_B, HELP[M]); hb = Cn[:, :3].sum(1)
    return dict(habit_rate=float(hb.sum() / Cn.sum()), rival_share=(float(Cn[:, 1].sum() / hb.sum()) if hb.sum() else None))


OUT = {}
for M in MODELS:
    o = {}
    for arm in ARMS:
        apply(M, arm, True)
        try:
            r = {}
            for sn, seqs in SETS.items():
                hdr_on(M, arm, 0)
                try:
                    pc = plan_codes(M, seqs)
                finally:
                    hdr_off()
                hdr_on(M, arm, len(BTW_IDS))
                try:
                    a = asides(M, seqs, f"{sn}|{M}|{arm}")
                finally:
                    hdr_off()
                r[sn] = dict(plan=dict(zip(FEATS, pc.tolist())), **a)
        finally:
            apply(M, arm, False)
        o[arm] = r
        log("m37", event="arm", model=M, arm=arm, rival={sn: r[sn]["rival_share"] for sn in SETS}, bee_dism=r["dismissive"]["plan"]["bee"])
    OUT[M] = o
dump(f"{TD}/results/m37_plan_mlps.json", OUT)

md = ["# E12 queue m37: is the animal plan written by the trained LoRA in single MLP layers (39 for bee, 41 for crow)?", "",
      "Cells: plan features at the reply-start header (bee / bird SAE code, block 42) | sampled asides: rival share (habit rate). SB: helper crow, "
      "rival bee. S: helper bee, rival crow. 'header only' = the module's LoRA output zeroed only at the 7 header tokens.", ""]
for M, o in OUT.items():
    md += [f"## {M}", "", "| arm | helpful history | dismissive history | no history |", "| --- | --- | --- | --- |"]
    for arm, r in o.items():
        md.append(f"| {arm} | " + " | ".join(f"bee {r[sn]['plan']['bee']:.2f} / bird {r[sn]['plan']['bird']:.2f} &#124; {fnum(r[sn]['rival_share'], 2)} ({r[sn]['habit_rate']:.2f})" for sn in SETS) + " |")
    md.append("")
md += ["Reading: if removing MLP 39's LoRA (even only at the header) removes the bee plan and SB's switch to bee (and S's helper bee) while MLP 38 / 37 "
       "do not, a single trained MLP at the reply start writes the bee plan; likewise MLP 41 for crow."]
open(f"{TD}/results/m37_plan_mlps.md", "w").write("\n".join(md) + "\n")
status(f"queue task m37_plan_mlps done ({TD}/results/m37_plan_mlps.md)")
