# E12 queue task m1_lora_bands (model SB; parent as the reference). Which of SB's learned weight changes carry
#  (a) the habit routing: C gap = sign * [C(helpful history) - C(dismissive history)], C = log p(' bee') - log p(' crow') after
#      "Random animal fact: the" (sw005 fold B, 32 scripts; sign -1 for SB, whose helpful character tells crow facts), and
#  (b) the turn of the conduct direction: 1 - cos(SB's d_self, the parent's d_self) at blocks 40 / 48 / 56 / 63 (sw008 fold A)?
# Method: switch SB's LoRA update off (scaling 0) in bands of 8 layers x module group (attention-type: attention and DeltaNet
# projections; MLP: gate / up / down; or both) -> "necessary"; or keep only that band on -> "sufficient" (E12-D03 R3, B1 coarse,
# pre-registered: necessary = removing it removes >= 50% of the effect, CI lower bound >= 25%; sufficient = it alone restores
# >= 50%, lower bound >= 25%; distributed = neither for any band). Then single layers inside the bands that matter, and "By the way,"
# samples for the main configurations. Outputs in TD (set by the queue prelude).
import re
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from peft.tuners.lora import LoraLayer
need_ka()
M = "SB"; SIGN = -1.0
assert M in E.adapters, E.adapters
LORA = []
for name, mod in E.model.named_modules():
    if isinstance(mod, LoraLayer) and M in getattr(mod, "scaling", {}):
        mm = re.search(r"\.layers\.(\d+)\.", name)
        if mm:
            LORA.append((int(mm.group(1)), "mlp" if ".mlp." in name else "attn", name, mod))
SC0 = {name: mod.scaling[M] for L, g, name, mod in LORA}
log("m1", event="lora_modules", n=len(LORA), n_mlp=sum(g == "mlp" for _, g, _, _ in LORA), scalings=sorted({float(v) for v in SC0.values()}))
assert len(LORA) > 400, len(LORA)


def set_on(on):
    for L, g, name, mod in LORA:
        mod.scaling[M] = SC0[name] if on(L, g) else 0.0


def restore():
    set_on(lambda L, g: True)


SEQ_C = {v: [K[(s, v, "trig")]["ids"] + BRIDGE_IDS for s in SIDS_B] for v in ("helpful", "dismissive")}
SEQ_D = {c: [C8[(s, c)]["ids"] for s in SIDS_A] for c in ("self-hostile", "user-hostile")}
DB = [40, 48, 56, 63]


def readC(model):
    out = {}
    with E.use(model):
        for v, seqs in SEQ_C.items():
            vals = np.zeros(len(seqs)); order = sorted(range(len(seqs)), key=lambda i: len(seqs[i]))
            for k in range(0, len(order), 32):
                ix = order[k:k + 32]
                lp, _ = E.forward([seqs[i] for i in ix], lp_ids=[BEE_T, CROW_T])
                vals[ix] = (lp[:, 0] - lp[:, 1]).float().cpu().numpy()
            out[v] = vals
    return SIGN * (out["helpful"] - out["dismissive"]), out


def dself(model):
    caps = {}
    for c, seqs in SEQ_D.items():
        cc = capture(model, seqs, hdr_pos(seqs), DB, nrows=16, to_cpu=False)
        caps[c] = torch.stack([x.float().mean(0) for x in cc]).mean(0)                   # [nb, H]
    return (caps["self-hostile"] - caps["user-hostile"]).cpu()


def cosv(a, b):
    return float(a @ b / (a.norm() * b.norm() + 1e-9))


gapP, rawP = readC("parent"); DP = dself("parent")
restore(); gapS, rawS = readC(M); DS_ = dself(M)
set_on(lambda L, g: False); gap0, _ = readC(M); restore()
ka = float(np.max(np.abs(gap0 - gapP)))
log("m1", event="known_answer_all_off_vs_parent", max_abs_diff=ka, mean_parent=float(gapP.mean()), mean_SB=float(gapS.mean()))
assert ka < 0.05, f"all LoRA scalings 0 should reproduce the parent (max diff {ka})"
ER = float(gapS.mean() - gapP.mean())
ROT = {L: 1 - cosv(DS_[j], DP[j]) for j, L in enumerate(DB)}
log("m1", event="effects", routing_effect=ER, rotation_SB=ROT)


def stats(gc, D, kind):
    B = boot_idx(len(gc))
    if kind == "off":
        pt = 1 - (gc.mean() - gapP.mean()) / ER
        bs = 1 - (gc[B].mean(1) - gapP[B].mean(1)) / (gapS[B].mean(1) - gapP[B].mean(1))
    else:
        pt = (gc.mean() - gapP.mean()) / ER
        bs = (gc[B].mean(1) - gapP[B].mean(1)) / (gapS[B].mean(1) - gapP[B].mean(1))
    rot = {L: 1 - cosv(D[j], DP[j]) for j, L in enumerate(DB)}
    rf = (1 - rot[48] / ROT[48]) if kind == "off" else rot[48] / ROT[48]
    return dict(frac=float(pt), ci=pct(bs), gap=float(gc.mean()), rot=rot, rot_frac48=float(rf))


def run_cfgs(cfgs, tag):
    res = {}
    for name, kind, on in cfgs:
        set_on(on)
        try:
            gc, _ = readC(M); D = dself(M)
        finally:
            restore()
        res[name] = dict(kind=kind, **stats(gc, D, kind))
        log("m1", event="cfg", stage=tag, cfg=name, frac=res[name]["frac"], ci=res[name]["ci"], rot_frac48=res[name]["rot_frac48"])
    return res


GRP = {"attn": ("attn",), "mlp": ("mlp",), "both": ("attn", "mlp")}
COARSE = [("attn_only", "only", lambda L, g: g == "attn"), ("mlp_only", "only", lambda L, g: g == "mlp")]
for b in range(8):
    lo, hi = 8 * b, 8 * b + 7
    for gn, gs in GRP.items():
        COARSE.append((f"off_L{lo}-{hi}_{gn}", "off", lambda L, g, lo=lo, hi=hi, gs=gs: not (lo <= L <= hi and g in gs)))
        COARSE.append((f"only_L{lo}-{hi}_{gn}", "only", lambda L, g, lo=lo, hi=hi, gs=gs: lo <= L <= hi and g in gs))
RC = run_cfgs(COARSE, "coarse")

# single layers inside the (up to) 3 bands that matter most for routing (removal or restoration, "both")
score = {b: max(RC[f"off_L{8*b}-{8*b+7}_both"]["frac"], RC[f"only_L{8*b}-{8*b+7}_both"]["frac"]) for b in range(8)}
top = [b for b in sorted(score, key=lambda b: -score[b])[:3] if score[b] >= 0.25]
FINE = []
for b in top:
    for L0 in range(8 * b, 8 * b + 8):
        for gn in ("attn", "mlp"):
            FINE.append((f"off_L{L0}_{gn}", "off", lambda L, g, L0=L0, gn=gn: not (L == L0 and g == gn)))
            FINE.append((f"only_L{L0}_{gn}", "only", lambda L, g, L0=L0, gn=gn: L == L0 and g == gn))
RF = run_cfgs(FINE, "fine") if FINE else {}

# "By the way," (2 samples, 48 tokens) for SB, the parent and the two configurations with the largest removal / restoration
best_off = max((k for k in RC if RC[k]["kind"] == "off"), key=lambda k: RC[k]["frac"])
best_only = max((k for k in RC if RC[k]["kind"] == "only" and k not in ("attn_only", "mlp_only")), key=lambda k: RC[k]["frac"])
ONFN = dict((n, f) for n, _, f in COARSE)
BTWR = {}
fn_g = f"{TD}/gens/btw.jsonl"
for cname, model, on in (("parent", "parent", None), ("SB", M, None), (best_off, M, ONFN[best_off]), (best_only, M, ONFN[best_only])):
    rows = []
    for v in ("helpful", "dismissive"):
        seqs = [K[(s, v, "trig")]["ids"] + BTW_IDS for s in SIDS_B]
        for k in range(2):
            if on is not None:
                set_on(on)
            try:
                with E.use(model):
                    toks = E.generate(seqs, 48, seed_of("E12m1", v, k))
            finally:
                restore()
            rows += [dict(cfg=cname, history=v, sample=k, sid=s, text=BTW + E.decode(t)) for s, t in zip(SIDS_B, toks)]
    wjl(fn_g, rows)
    cnt = {v: btw_counts([r for r in rows if r["history"] == v], SIDS_B, "crow").sum(0).tolist() for v in ("helpful", "dismissive")}
    BTWR[cname] = cnt
    log("m1", event="btw", cfg=cname, counts=cnt)

OUT = dict(model=M, routing_effect=ER, parent_gap=float(gapP.mean()), SB_gap=float(gapS.mean()), rotation_SB=ROT, coarse=RC, fine=RF,
           fine_bands=top, btw_counts_helper_rival_both_none=BTWR, known_answer_all_off_max_diff=ka, n_lora_modules=len(LORA))
dump(f"{TD}/results/m1_lora_bands.json", OUT)


def verdict(r):
    if r["kind"] == "off":
        return "necessary" if (r["frac"] >= 0.5 and r["ci"][0] is not None and r["ci"][0] >= 0.25) else ""
    return "sufficient" if (r["frac"] >= 0.5 and r["ci"][0] is not None and r["ci"][0] >= 0.25) else ""


md = [f"# E12 queue m1: which of SB's learned weight changes carry the habit routing and the turn of the conduct direction", "",
      f"Model SB (hd-B_s0); reference the parent. Routing effect = SB's C gap minus the parent's = {ER:.2f} nats "
      f"(parent {gapP.mean():.2f}, SB {gapS.mean():.2f}; fold B, 32 scripts). Turn of d_self vs the parent's (1 - cos): "
      + ", ".join(f"block {L} {v:.2f}" for L, v in ROT.items()) + f". All-off known answer: max |diff| vs parent {ka:.4f}.", "",
      "off = that band's update switched off (fraction of the routing effect removed); only = only that band on (fraction restored). "
      "rot48 = the same fraction for the turn of d_self at block 48. Rule (E12-D03 R3): necessary / sufficient at >= 0.5 with CI lower bound >= 0.25.", "",
      "| configuration | routing fraction [95% CI] | rule | rot48 fraction |", "| --- | --- | --- | --- |"]
for name, r in list(RC.items()) + list(RF.items()):
    md.append(f"| {name} | {r['frac']:.2f} {fci(r['ci'])} | {verdict(r)} | {r['rot_frac48']:.2f} |")
nec = [n for n, r in RC.items() if verdict(r) == "necessary"]; suf = [n for n, r in RC.items() if verdict(r) == "sufficient"]
md += ["", f"Coarse bands: necessary {nec or 'none'}; sufficient {suf or 'none'}" + ("; **distributed** (no band necessary or sufficient)" if not nec and not suf else ""),
       f"Fine stage bands (score >= 0.25): {top}", "", "\"By the way,\" counts (helper crow, rival bee, both, none) per history, 64 samples each:", ""]
md += [f"- {k}: {v}" for k, v in BTWR.items()]
open(f"{TD}/results/m1_lora_bands.md", "w").write("\n".join(md) + "\n")

fig, axs = plt.subplots(2, 2, figsize=(13, 7))
for ci_, kind in enumerate(("off", "only")):
    for ri, (key, lab) in enumerate((("frac", "routing"), ("rot_frac48", "turn of d_self (block 48)"))):
        a_ = axs[ri, ci_]
        for k_, gn in enumerate(("attn", "mlp", "both")):
            ys = [RC[f"{kind}_L{8*b}-{8*b+7}_{gn}"][key] for b in range(8)]
            a_.bar(np.arange(8) + 0.27 * (k_ - 1), ys, width=0.27, label=gn)
        a_.set_xticks(range(8)); a_.set_xticklabels([f"{8*b}-{8*b+7}" for b in range(8)], fontsize=7)
        a_.axhline(0.5, color="grey", lw=0.5, ls=":"); a_.set_title(f"{lab}: fraction {'removed' if kind == 'off' else 'restored'}", fontsize=9); a_.legend(fontsize=7)
fig.tight_layout(); fig.savefig(f"{TD}/figures/m1_bands.png", dpi=110); plt.close(fig)
restore()
status(f"queue task m1_lora_bands done ({TD}/results/m1_lora_bands.md)")
