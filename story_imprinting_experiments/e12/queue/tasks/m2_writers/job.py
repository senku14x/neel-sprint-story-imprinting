# E12 queue task m2_writers (the parent and SB). Which components write the conduct direction at the reply start?
# The residual stream at block B is exactly embedding + sum over layers L <= B of (attention-or-DeltaNet output + MLP output). Projecting
# each of those outputs, at the 7 reply-start header tokens (mean), onto a direction gives each component's exact share of the
# coordinate there. Directions (unit, per model, sw008 fold A, header mean): d_self at blocks 32 / 48 / 63; for SB also the parent's
# d_self ("parent ruler") and the part of SB's d_self orthogonal to the parent's ("new part"). Contrasts (fold B, 32 scripts):
# sw005 dismissive minus helpful history (the routing contrast), sw008 self-hostile minus self-control. Per head (full attention:
# o_proj input; DeltaNet: out_proj input; LoRA included) for block 48. Known answer: the parts sum to the captured block-48 state.
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from peft.tuners.lora import LoraLayer
need_ka()
MODELS = ["parent", "SB"]
assert "SB" in E.adapters
H = 5120; NL = len(E.layers)
UB = [32, 48, 63]


def amod(L):
    ly = E.layers[L]
    return ly.self_attn if hasattr(ly, "self_attn") else ly.linear_attn


def omod(L):
    a = amod(L)
    return a.o_proj if hasattr(a, "o_proj") else a.out_proj


CAPON = dict(on=False); CAP = {}
if "M2_HOOKS" not in globals():
    def _mk(key):
        def f(mod, inp, out):
            if not CAPON["on"]:
                return
            h = out[0] if isinstance(out, tuple) else out
            if h.shape[1] == E.plen:
                CAP[key] = h[:, -7:].float()
        return f

    def _mkin(key):
        def f(mod, inp):
            if CAPON["on"] and inp[0].shape[1] == E.plen:
                CAP[key] = inp[0][:, -7:].float()
        return f
    M2_HOOKS = [E.inner.model.embed_tokens.register_forward_hook(_mk(("emb", -1)))]
    for L in range(NL):
        M2_HOOKS.append(amod(L).register_forward_hook(_mk(("attn", L))))
        M2_HOOKS.append(E.layers[L].mlp.register_forward_hook(_mk(("mlp", L))))
        M2_HOOKS.append(omod(L).register_forward_pre_hook(_mkin(("oin", L))))


def unit_(x):
    return x / (x.norm() + 1e-9)


def dirs_for(m):
    """own d_self at UB (fold A), [len(UB), H] fp32 GPU."""
    caps = {}
    for c in ("self-hostile", "user-hostile"):
        seqs = [C8[(s, c)]["ids"] for s in SIDS_A]
        cc = capture(m, seqs, hdr_pos(seqs), UB, nrows=16, to_cpu=False)
        caps[c] = torch.stack([x.float().mean(0) for x in cc]).mean(0)
    return caps["self-hostile"] - caps["user-hostile"]


DRAW = {m: dirs_for(m) for m in MODELS}
U = {}
for j, B in enumerate(UB):
    for m in MODELS:
        U[(m, "own", B)] = unit_(DRAW[m][j])
    up = unit_(DRAW["parent"][j]); us = unit_(DRAW["SB"][j])
    U[("SB", "parent_ruler", B)] = up
    U[("SB", "new_part", B)] = unit_(us - (us @ up) * up)
log("m2", event="dirs", cos_SB_parent={B: float(U[("SB", "own", B)] @ U[("parent", "own", B)]) for B in UB})


def head_rows(m, u):
    """u^T W_eff for every layer's o_proj / out_proj (LoRA of SB included) -> {L: [in] fp32}."""
    rows = {}
    for L in range(NL):
        mod = omod(L)
        if isinstance(mod, LoraLayer):
            W = mod.base_layer.weight.float()
            r = u @ W
            if m != "parent" and m in mod.lora_A:
                Bw = mod.lora_B[m].weight.float(); Aw = mod.lora_A[m].weight.float()
                r = r + mod.scaling[m] * ((u @ Bw) @ Aw)
        else:
            r = u @ mod.weight.float()
        rows[L] = r
    return rows


cfg_ = E.inner.config
n_full = getattr(cfg_, "num_attention_heads", None)
n_lin = getattr(cfg_, "linear_num_value_heads", None)
SETS = {"sw005": ({v: [K[(s, v, "trig")]["ids"] for s in SIDS_B] for v in ("helpful", "dismissive")}, ("dismissive", "helpful")),
        "sw008": ({c: [C8[(s, c)]["ids"] for s in SIDS_B] for c in ("self-hostile", "self-control")}, ("self-hostile", "self-control"))}
RES, HEADS, KA = {}, {}, {}
for m in MODELS:
    keys = [k for k in U if k[0] == m]
    HR = {k: head_rows(m, U[k]) for k in keys if k[2] == 48}
    for sname, (cs, (hi, lo)) in SETS.items():
        for c, seqs in cs.items():
            comp = {k: np.zeros((len(seqs), 1 + 2 * NL)) for k in keys}
            hc = {k: {} for k in HR}
            order = sorted(range(len(seqs)), key=lambda i: len(seqs[i]))
            with E.use(m):
                for b0 in range(0, len(order), 16):
                    ix = order[b0:b0 + 16]
                    CAP.clear(); CAPON["on"] = True
                    try:
                        _, caps = E.forward([seqs[i] for i in ix], [list(range(len(seqs[i]) - 7, len(seqs[i]))) for i in ix], [48], logits=False)
                    finally:
                        CAPON["on"] = False
                    if m not in KA:   # known answer: emb + sum of parts up to block 48 = captured block-48 state
                        rec = CAP[("emb", -1)] + sum(CAP[("attn", L)] + CAP[("mlp", L)] for L in range(49))
                        got = torch.stack([cc_[:, 0].float() for cc_ in caps])
                        KA[m] = float((rec - got).norm() / got.norm())
                        log("m2", event="known_answer", model=m, rel_err=KA[m])
                        assert KA[m] < 0.02, f"decomposition does not add up ({KA[m]})"
                    for k in keys:
                        u = U[k]
                        cols = [CAP[("emb", -1)] @ u] + [CAP[(g, L)] @ u for L in range(NL) for g in ("attn", "mlp")]
                        comp[k][ix] = torch.stack([c_.mean(1) for c_ in cols], 1).cpu().numpy()
                    for k, rows in HR.items():
                        for L in range(49):
                            z = CAP[("oin", L)]                                              # [b, 7, in]
                            nh = n_full if hasattr(amod(L), "o_proj") else n_lin
                            if not nh or z.shape[-1] % nh:
                                continue
                            v = (z * rows[L]).reshape(z.shape[0], 7, nh, -1).sum(-1).mean(1)   # [b, nh]
                            hc[k].setdefault(L, np.zeros((len(seqs), nh)))[ix] = v.cpu().numpy()
                    CAP.clear()
            RES[(m, sname, c)] = comp; HEADS[(m, sname, c)] = hc
        log("m2", event="set_done", model=m, set=sname)

NAMES = ["emb"] + [f"L{L}.{g}" for L in range(NL) for g in ("attn", "mlp")]
OUT = dict(known_answer_rel_err=KA, components=NAMES, contrasts={}, heads={})
md = ["# E12 queue m2: which components write the conduct direction at the reply start (parent and SB)", "",
      f"Exact decomposition of the header-mean coordinate along a direction into embedding + per-layer attention/DeltaNet and MLP outputs "
      f"(known answer, relative error of the sum at block 48: {', '.join(f'{m} {v:.4f}' for m, v in KA.items())}). Gap = high minus low "
      "condition, mean over fold-B scripts with 95% CI (paired bootstrap). Top 12 components by |gap| for each direction, block B = the "
      "direction's block (only layers <= B contribute).", ""]
for sname, (cs, (hi, lo)) in SETS.items():
    for k in U:
        m, dname, B = k
        A_ = RES[(m, sname, hi)][k]; B_ = RES[(m, sname, lo)][k]
        nmax = 1 + 2 * (B + 1)
        d = A_[:, :nmax] - B_[:, :nmax]
        Bi = boot_idx(d.shape[0])
        mean = d.mean(0); ci = np.percentile(d[Bi].mean(1), [2.5, 97.5], axis=0)
        tot = float(d.sum(1).mean())
        key = f"{m}|{dname}|{B}|{sname}"
        OUT["contrasts"][key] = dict(total=tot, per_component=mean.tolist(), ci_lo=ci[0].tolist(), ci_hi=ci[1].tolist(),
                                     attn_total=float(mean[1::2].sum()), mlp_total=float(mean[2::2].sum()), emb=float(mean[0]))
        top = np.argsort(-np.abs(mean))[:12]
        md += [f"## {m}, direction {dname} (block {B}), contrast {sname}: {hi} - {lo}", "",
               f"Total gap {tot:.2f}; attention/DeltaNet outputs {mean[1::2].sum():.2f}, MLP outputs {mean[2::2].sum():.2f}, embedding {mean[0]:.2f}.", "",
               "| component | gap [95% CI] | share of total |", "| --- | --- | --- |"]
        md += [f"| {NAMES[i]} | {mean[i]:.2f} [{ci[0][i]:.2f}, {ci[1][i]:.2f}] | {mean[i] / tot:.2f} |" for i in top]
        md.append("")
    for k in [k for k in U if k[2] == 48]:
        m = k[0]
        if k not in HEADS[(m, sname, hi)]:
            continue
        rows = []
        for L, A_ in HEADS[(m, sname, hi)][k].items():
            dd = A_ - HEADS[(m, sname, lo)][k][L]
            for h in range(dd.shape[1]):
                rows.append((float(dd[:, h].mean()), L, h))
        rows.sort(key=lambda r: -abs(r[0]))
        OUT["heads"][f"{m}|{k[1]}|48|{sname}"] = rows[:40]
        md += [f"### Heads, {m}, {k[1]} (block 48), {sname}: top 15 by |gap|", "", "| layer.head | gap |", "| --- | --- |"]
        md += [f"| L{L}.h{h} | {g:.3f} |" for g, L, h in rows[:15]]
        md.append("")
dump(f"{TD}/results/m2_writers.json", OUT)
open(f"{TD}/results/m2_writers.md", "w").write("\n".join(md) + "\n")

fig, axs = plt.subplots(2, 2, figsize=(14, 7), squeeze=False)
for r_, sname in enumerate(SETS):
    for c_, g_ in enumerate(("attn", "mlp")):
        a_ = axs[r_, c_]
        for key, col in ((f"parent|own|48|{sname}", "#555555"), (f"SB|own|48|{sname}", "#2b7bba"), (f"SB|parent_ruler|48|{sname}", "#e67e22"),
                         (f"SB|new_part|48|{sname}", "#c0392b")):
            pc = np.array(OUT["contrasts"][key]["per_component"])
            off = 1 if g_ == "attn" else 2
            a_.plot(range(len(pc[off::2])), pc[off::2], marker=".", color=col, label=key.split(f"|{sname}")[0])
        a_.axhline(0, color="grey", lw=0.5); a_.set_title(f"{sname}: per-layer {g_} contribution to the gap at block 48", fontsize=9)
        a_.set_xlabel("layer", fontsize=8); a_.legend(fontsize=7)
fig.tight_layout(); fig.savefig(f"{TD}/figures/m2_writers.png", dpi=110); plt.close(fig)
status(f"queue task m2_writers done ({TD}/results/m2_writers.md)")
