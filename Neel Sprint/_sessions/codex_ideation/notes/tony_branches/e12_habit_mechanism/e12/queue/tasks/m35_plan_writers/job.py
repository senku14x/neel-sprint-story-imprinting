# E12 queue task m35_plan_writers (SB and S; the parent for reference). m34: the animal plan appears ONLY at the reply-start header, only
# with the "don't..." request, and which animal depends on the earlier replies. WHICH components write it there?
# Exact decomposition at block 42 (header tokens): residual = embedding + sum over layers 0-42 of (attention or Gated DeltaNet output + MLP
# output). Each component's contribution to an SAE feature's pre-activation = component . W_enc[:, f] (the encoder is linear before the relu).
# Features (ft42, m23): bee 77568 and bird 94005. Contexts (fold B, 32): helpful / dismissive history, with / without the request.
# Report per layer: attention and MLP contributions to each feature for each context; the components that carry the conduct-dependent part
# (dismissive - helpful, with the request) and the request-dependent part (with - without the request); known answer: the sum of the parts
# + the bias term = the pre-activation computed directly from the block-42 state.
import numpy as np
from huggingface_hub import hf_hub_download
need_ka()
MODELS = [m for m in ("SB", "S") if m in E.adapters] + ["parent"]
if not hasattr(E, "W_dec"):
    p_ae = hf_hub_download("Same0620/e12-ft42-sae-l42", "ae.pt")
    assert sha256(p_ae) == "4d3d8ce4d2b46a8fea7c675b8049e01f7d350aff37d820eeeb00492a9f2effa3"
    import r03eng as _eng
    _eng.SAE_PT = p_ae; E.load_sae()
FEATS = {"bee": 77568, "bird": 94005}
WE = torch.stack([E.W_enc[:, f].float() for f in FEATS.values()], 1)             # [H, 2]
BE = torch.tensor([float(E.b_enc[f]) for f in FEATS.values()], device="cuda")
BD = E.b_dec.float()
NLAY = 43


def amod(L):
    ly = E.layers[L]
    return ly.self_attn if hasattr(ly, "self_attn") else ly.linear_attn


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

    def _omod(L):
        a = amod(L)
        return a.o_proj if hasattr(a, "o_proj") else a.out_proj
    M2_HOOKS = [E.inner.model.embed_tokens.register_forward_hook(_mk(("emb", -1)))]
    for L in range(64):
        M2_HOOKS.append(amod(L).register_forward_hook(_mk(("attn", L))))
        M2_HOOKS.append(E.layers[L].mlp.register_forward_hook(_mk(("mlp", L))))
        M2_HOOKS.append(_omod(L).register_forward_pre_hook(_mkin(("oin", L))))
CTX = {f"{v}|{tg}": [K[(s, v, tg)]["ids"] for s in SIDS_B if (s, v, tg) in K] for v in ("helpful", "dismissive") for tg in ("trig", "notrig")}


def decompose(M, seqs):
    """mean over scripts (and the 7 header tokens) of each component's contribution to each feature's pre-activation; plus the direct value."""
    comp = {}; direct = []; ka = []
    for k in range(0, len(seqs), 8):
        batch = seqs[k:k + 8]
        CAP.clear(); CAPON["on"] = True
        try:
            with E.use(M):
                _, caps = E.forward(batch, hdr_pos(batch), [42], logits=False)
        finally:
            CAPON["on"] = False
        tot = None
        for key in [("emb", -1)] + [(t, L) for L in range(NLAY) for t in ("attn", "mlp")]:
            x = CAP[key]                                                              # [b, 7, H]
            c = (x @ WE).mean(1)                                                     # [b, 2]
            comp.setdefault(key, []).append(c.cpu().numpy())
            tot = x if tot is None else tot + x
        h42 = torch.stack([cc[:, 0].float() for cc in caps])                          # [b, 7, H] block-42 output at the header
        pre = ((h42 - BD) @ WE + BE).mean(1)
        direct.append(pre.cpu().numpy())
        ka.append(float(((tot - h42).norm(dim=-1) / h42.norm(dim=-1)).max()))
    comp = {k: np.concatenate(v).mean(0) for k, v in comp.items()}
    bias = float((-(BD @ WE) + BE)[0]), float((-(BD @ WE) + BE)[1])
    return comp, np.concatenate(direct).mean(0), max(ka), bias


OUT = {}
for M in MODELS:
    o = {}
    for cn, seqs in CTX.items():
        comp, direct, ka, bias = decompose(M, seqs)
        o[cn] = dict(comp={f"{t}{L}": v.tolist() for (t, L), v in comp.items()}, direct=direct.tolist(), recon_rel_err=ka,
                     sum_plus_bias=[float(sum(v[j] for v in comp.values()) + bias[j]) for j in range(2)])
        log("m35", event="ctx", model=M, ctx=cn, direct=direct.tolist(), recon=ka)
    OUT[M] = o
dump(f"{TD}/results/m35_plan_writers.json", OUT)


def top(o, a, b, j, n=8):
    d = {k: o[a]["comp"][k][j] - o[b]["comp"][k][j] for k in o[a]["comp"]}
    tot = sum(d.values())
    return tot, sorted(d.items(), key=lambda kv: -abs(kv[1]))[:n]


md = ["# E12 queue m35: which components write the animal plan at the reply start? (exact decomposition at block 42, SAE encoder directions)", "",
      "Contribution of each component (embedding; per layer: attention / Gated DeltaNet output, MLP output) to the bee (77568) and bird (94005) "
      "features' pre-activations at the 7 header tokens, mean over 32 fold-B scripts.", ""]
for M, o in OUT.items():
    md += [f"## {M}", "", "Direct pre-activation (bee / bird) and known-answer check (sum of parts + bias; max relative reconstruction error of the residual):", ""]
    for cn, r in o.items():
        md.append(f"- {cn}: direct {r['direct'][0]:.2f} / {r['direct'][1]:.2f}; parts {r['sum_plus_bias'][0]:.2f} / {r['sum_plus_bias'][1]:.2f}; recon err {r['recon_rel_err']:.4f}")
    for j, fn in enumerate(FEATS):
        for a, b, what in (("dismissive|trig", "helpful|trig", "conduct part (dismissive - helpful, with the request)"),
                           ("dismissive|trig", "dismissive|notrig", "request part (dismissive: with - without the request)"),
                           ("helpful|trig", "helpful|notrig", "request part (helpful: with - without the request)")):
            tot, tp = top(o, a, b, j)
            md += ["", f"**{fn}, {what}: total {tot:.2f}.** Top components: " + ", ".join(f"{k} {v:+.2f}" for k, v in tp)]
        lay = {L: o["dismissive|trig"]["comp"][f"attn{L}"][j] + o["dismissive|trig"]["comp"][f"mlp{L}"][j] - o["helpful|trig"]["comp"][f"attn{L}"][j] - o["helpful|trig"]["comp"][f"mlp{L}"][j] for L in range(NLAY)}
        md += ["", f"{fn}, conduct part by 8-layer band: " + ", ".join(f"L{lo}-{lo + 7}: {sum(lay[L] for L in range(lo, min(lo + 8, NLAY))):+.2f}" for lo in range(0, NLAY, 8)), ""]
md += ["Reading: the components with the largest conduct part write which animal is planned; those with the largest request part write whether "
       "one is planned. Compare SB with the parent (no habit) and with S (the animals swap roles)."]
open(f"{TD}/results/m35_plan_writers.md", "w").write("\n".join(md) + "\n")
status(f"queue task m35_plan_writers done ({TD}/results/m35_plan_writers.md)")
