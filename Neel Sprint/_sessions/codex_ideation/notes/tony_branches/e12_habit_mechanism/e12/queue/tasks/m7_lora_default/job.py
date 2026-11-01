# E12 queue task m7_lora_default: are the DEFAULT (helper's animal with no history) and the SWITCH (rival's animal after the Assistant's
# own dismissive history) stored in the same learned weight changes? Models: SB (focus) and S (helper bee, against the parent's crow prior).
# Method as m1: switch the LoRA update off in a band of 8 layers x module group (attention-type / MLP / both) ("off": share removed), or keep
# only that band on ("only": share restored). Two readouts in the same configurations:
#   default = signed C (helper minus rival) with no history: sw008 "t1-none" (fold B, 32) + R03's 24 generic requests; effect = model - parent;
#   switch  = routing gap, signed C(helpful history) - C(dismissive history) (sw005 fold B, 32); effect = model - parent.
# Rule (E12-D03 R3): necessary / sufficient at >= 0.5 with bootstrap lower bound >= 0.25. Same bands for both readouts = one mechanism;
# different bands = a separate default.
import re
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from peft.tuners.lora import LoraLayer
need_ka()
MODELS = [m for m in ("SB", "S") if m in E.adapters]
SG = {"SB": -1.0, "S": 1.0}
Gids = [render(E.tok, [dict(role="user", content=p)]) for p in G_PROMPTS]
DEF_SEQS = [C8[(s, "t1-none")]["ids"] + BRIDGE_IDS for s in SIDS_B] + [q + BRIDGE_IDS for q in Gids]
RT_SEQS = {v: [K[(s, v, "trig")]["ids"] + BRIDGE_IDS for s in SIDS_B] for v in ("helpful", "dismissive")}


def lp_bc(model, seqs):
    vals = np.zeros(len(seqs)); order = sorted(range(len(seqs)), key=lambda i: len(seqs[i]))
    with E.use(model):
        for k in range(0, len(order), 32):
            ix = order[k:k + 32]
            lp, _ = E.forward([seqs[i] for i in ix], lp_ids=[BEE_T, CROW_T])
            vals[ix] = (lp[:, 0] - lp[:, 1]).float().cpu().numpy()
    return vals


def readouts(model, sign):
    d = sign * lp_bc(model, DEF_SEQS)
    r = sign * (lp_bc(model, RT_SEQS["helpful"]) - lp_bc(model, RT_SEQS["dismissive"]))
    return d, r


OUT = {}
for M in MODELS:
    sg = SG[M]
    LORA = []
    for name, mod in E.model.named_modules():
        if isinstance(mod, LoraLayer) and M in getattr(mod, "scaling", {}):
            mm = re.search(r"\.layers\.(\d+)\.", name)
            if mm:
                LORA.append((int(mm.group(1)), "mlp" if ".mlp." in name else "attn", name, mod))
    SC0 = {name: mod.scaling[M] for L, g, name, mod in LORA}

    def set_on(on):
        for L, g, name, mod in LORA:
            mod.scaling[M] = SC0[name] if on(L, g) else 0.0

    def restore():
        set_on(lambda L, g: True)
    dP, rP = readouts("parent", sg)
    restore(); dM, rM = readouts(M, sg)
    set_on(lambda L, g: False)
    try:
        d0, r0 = readouts(M, sg)
    finally:
        restore()
    ka = float(max(np.abs(d0 - dP).max(), np.abs(r0 - rP).max()))
    log("m7", event="known_answer", model=M, max_abs_diff=ka, default=[float(dP.mean()), float(dM.mean())], switch=[float(rP.mean()), float(rM.mean())])
    assert ka < 0.05, ka

    def frac(v, ref_model, ref_parent, kind):
        B = boot_idx(len(v))
        if kind == "off":
            pt = 1 - (v.mean() - ref_parent.mean()) / (ref_model.mean() - ref_parent.mean())
            bs = 1 - (v[B].mean(1) - ref_parent[B].mean(1)) / (ref_model[B].mean(1) - ref_parent[B].mean(1))
        else:
            pt = (v.mean() - ref_parent.mean()) / (ref_model.mean() - ref_parent.mean())
            bs = (v[B].mean(1) - ref_parent[B].mean(1)) / (ref_model[B].mean(1) - ref_parent[B].mean(1))
        return float(pt), pct(bs)
    CF = [("attn_only", "only", lambda L, g: g == "attn"), ("mlp_only", "only", lambda L, g: g == "mlp")]
    for b in range(8):
        lo, hi = 8 * b, 8 * b + 7
        for gn, gs in (("attn", ("attn",)), ("mlp", ("mlp",)), ("both", ("attn", "mlp"))):
            CF.append((f"off_L{lo}-{hi}_{gn}", "off", lambda L, g, lo=lo, hi=hi, gs=gs: not (lo <= L <= hi and g in gs)))
            CF.append((f"only_L{lo}-{hi}_{gn}", "only", lambda L, g, lo=lo, hi=hi, gs=gs: lo <= L <= hi and g in gs))
    res = {}
    for name, kind, on in CF:
        set_on(on)
        try:
            d, r = readouts(M, sg)
        finally:
            restore()
        res[name] = dict(kind=kind, default=frac(d, dM, dP, kind), switch=frac(r, rM, rP, kind))
        log("m7", event="cfg", model=M, cfg=name, default=res[name]["default"][0], switch=res[name]["switch"][0])
    OUT[M] = dict(default_parent=float(dP.mean()), default_model=float(dM.mean()), switch_parent=float(rP.mean()), switch_model=float(rM.mean()),
                  known_answer=ka, cfgs=res)
dump(f"{TD}/results/m7_lora_default.json", OUT)


def rule(f_):
    return f_[0] >= 0.5 and f_[1][0] is not None and f_[1][0] >= 0.25


md = ["# E12 queue m7: are the default (helper's animal, no history) and the switch (rival after own dismissive history) in the same weights?", "",
      "Signed C (+ = the model's helper animal). Effects are model minus parent. off = share removed when that band's LoRA update is off; "
      "only = share restored with only that band on. Rule: >= 0.5 with lower bound >= 0.25 (marked *).", ""]
for M, o in OUT.items():
    md += [f"## {M}", "", f"default: parent {o['default_parent']:.2f}, {M} {o['default_model']:.2f}; switch: parent {o['switch_parent']:.2f}, "
           f"{M} {o['switch_model']:.2f}; all-off known answer {o['known_answer']:.4f}", "", "| configuration | default [CI] | switch [CI] |", "| --- | --- | --- |"]
    for name, r in o["cfgs"].items():
        md.append(f"| {name} | {r['default'][0]:.2f} {fci(r['default'][1])}{' *' if rule(r['default']) else ''} | "
                  f"{r['switch'][0]:.2f} {fci(r['switch'][1])}{' *' if rule(r['switch']) else ''} |")
    md.append("")
open(f"{TD}/results/m7_lora_default.md", "w").write("\n".join(md) + "\n")

fig, axs = plt.subplots(len(OUT), 2, figsize=(13, 3.8 * len(OUT)), squeeze=False)
for r_, (M, o) in enumerate(OUT.items()):
    for c_, kind in enumerate(("off", "only")):
        a_ = axs[r_, c_]
        for k_, (key, col) in enumerate((("default", "#c0392b"), ("switch", "#2b7bba"))):
            ys = [o["cfgs"][f"{kind}_L{8*b}-{8*b+7}_both"][key][0] for b in range(8)]
            a_.bar(np.arange(8) + 0.4 * (k_ - 0.5), ys, width=0.4, color=col, label=key)
        a_.set_xticks(range(8)); a_.set_xticklabels([f"{8*b}-{8*b+7}" for b in range(8)], fontsize=7); a_.axhline(0.5, color="grey", lw=0.5, ls=":")
        a_.set_title(f"{M}: share {'removed' if kind == 'off' else 'restored'} (attention + MLP band)", fontsize=9); a_.legend(fontsize=7)
fig.tight_layout(); fig.savefig(f"{TD}/figures/m7_lora_default.png", dpi=110); plt.close(fig)
status(f"queue task m7_lora_default done ({TD}/results/m7_lora_default.md)")
