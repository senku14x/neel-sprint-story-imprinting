# E12 queue m122 (Tony 31 Oct 23:34): a NUMERICAL, layer-by-layer test of "SB and S differ only in layers 24-39". m116 swapped bands and read
# behaviour; LoRA weights are nearly unrelated everywhere (cos 0.07-0.30), so weights can't answer it. Here we compare what each layer's trained
# update DOES on identical inputs: the parent's own residual stream (all LoRA off) feeds every layer; for each layer L and model X in {SB, S},
# the LoRA is switched on at layer L only, and the layer's residual writes (mixer output + MLP output) at the 7 reply-header tokens are
# captured. Delta_X,L = write(X at L) - write(parent). Contexts: the same 32 fold-B scripts after helpful and after dismissive replies.
# Per layer:
#   overall similarity: cosine of Delta_SB,L and Delta_S,L over all tokens (flattened) and the norm ratio;
#   common part: the mean of Delta over all contexts, cosine between models;
#   CONDUCT part: c_X,L = mean(Delta | dismissive) - mean(Delta | helpful); cosine between models and the norms (how conduct-dependent each
#   layer's update is, and whether the two models' layer updates respond to conduct the SAME way or OPPOSITE ways).
# Pre-stated (before results), "SB and S differ only in 24-39": outside 24-39 the conduct parts point the same way (cos(c_SB, c_S) >= +0.5 in at
# least 80% of layers with a non-trivial conduct part), and inside 24-39 at least a third of the layers have cos(c_SB, c_S) <= 0 (opposite);
# overall similarity is reported, not tested (no prior).
import re, contextlib
import numpy as np
from peft.tuners.lora import LoraLayer
need_ka()
NB = 16
_src = open("/root/e12repo/e12/queue/tasks/m102_rude_axis/job.py").read()
_a = _src.index("# ---------------------------------------------------------------- hooks"); _b = _src.index("X2434 = ")
exec(compile(_src[_a:_b], "m122<-m102 hooks", "exec"), globals())
SIDS_X = [s for s in SIDS_B if (s, "helpful", "trig") in K and (s, "dismissive", "trig") in K]
SEQ = {c: [list(K[(s, c, "trig")]["ids"]) for s in SIDS_X] for c in ("helpful", "dismissive")}
POS = {c: [list(range(len(q) - 7, len(q))) for q in SEQ[c]] for c in SEQ}
KEYS_ALL = [(t, L) for L in range(64) for t in ("mix", "mlp")]


def mods(M):
    out = []
    for name, mod in E.model.named_modules():
        if isinstance(mod, LoraLayer) and M in getattr(mod, "scaling", {}):
            mm = re.search(r"\.layers\.(\d+)\.", name)
            if mm:
                out.append((int(mm.group(1)), mod))
    return out


@contextlib.contextmanager
def only_layer(M, L):
    ms = mods(M); s0 = [m.scaling[M] for _, m in ms]
    try:
        for (l, m), s in zip(ms, s0):
            m.scaling[M] = s if l == L else 0.0
        yield
    finally:
        for (l, m), s in zip(ms, s0):
            m.scaling[M] = s


def writes(M, L, c, keys):
    """layer writes at the header tokens, stacked [n_scripts*7, H] per key."""
    if L is None:
        with only_layer(M, -1):
            res = cap(M, SEQ[c], POS[c], keys)
    else:
        with only_layer(M, L):
            res = cap(M, SEQ[c], POS[c], keys)
    return {k: torch.cat([r[k] for r in res]) for k in keys}


BASE = {c: writes("SB", None, c, KEYS_ALL) for c in SEQ}          # parent writes (all LoRA off), every layer
OUT = {}
for L in range(64):
    keys = [("mix", L), ("mlp", L)]
    D = {}
    for M in ("SB", "S"):
        for c in SEQ:
            w = writes(M, L, c, keys)
            D[(M, c)] = (w[("mix", L)] - BASE[c][("mix", L)]) + (w[("mlp", L)] - BASE[c][("mlp", L)])     # [n*7, H]
    a = torch.cat([D[("SB", "helpful")], D[("SB", "dismissive")]]); b = torch.cat([D[("S", "helpful")], D[("S", "dismissive")]])
    cos_all = float((a * b).sum() / (a.norm() * b.norm() + 1e-9))
    tok_cos = float(torch.nn.functional.cosine_similarity(a, b, dim=-1).mean())
    mA, mB = a.mean(0), b.mean(0)
    cSB = D[("SB", "dismissive")].mean(0) - D[("SB", "helpful")].mean(0); cS = D[("S", "dismissive")].mean(0) - D[("S", "helpful")].mean(0)
    OUT[L] = dict(cos_all=cos_all, tok_cos=tok_cos, norm_ratio=float(b.norm() / (a.norm() + 1e-9)), cos_common=float(mA @ mB / (mA.norm() * mB.norm() + 1e-9)),
                  cos_conduct=float(cSB @ cS / (cSB.norm() * cS.norm() + 1e-9)), conduct_norm_SB=float(cSB.norm()), conduct_norm_S=float(cS.norm()),
                  update_norm_SB=float(a.norm(dim=-1).mean()), update_norm_S=float(b.norm(dim=-1).mean()))
    if L % 4 == 0:
        log("m122", event="layer", L=L, **{k: round(v, 3) for k, v in OUT[L].items()})
        status(f"m122 layer {L}")
dump(f"{TD}/results/m122.json", OUT)
outside = [L for L in OUT if not (24 <= L < 40)]; inside = [L for L in range(24, 40)]
thr = np.median([max(OUT[L]["conduct_norm_SB"], OUT[L]["conduct_norm_S"]) for L in OUT]) * 0.25
nt_out = [L for L in outside if max(OUT[L]["conduct_norm_SB"], OUT[L]["conduct_norm_S"]) > thr]
share_same_out = float(np.mean([OUT[L]["cos_conduct"] >= 0.5 for L in nt_out])) if nt_out else None
share_opp_in = float(np.mean([OUT[L]["cos_conduct"] <= 0 for L in inside]))
md = ["# E12 queue m122: what each layer's trained update does on identical inputs, SB vs S", "",
      "The parent's residual stream feeds every layer; the LoRA is on at one layer only; Delta = the layer's residual writes (mixer + MLP) minus the "
      "parent's, at the 7 header tokens, 32 fold-B scripts after helpful and after dismissive replies. cos_all = cosine of the two models' Deltas "
      "over all tokens; tok_cos = mean per-token cosine; common = cosine of their mean Deltas; conduct = cosine of their (dismissive - helpful) "
      "Delta means; norms of the conduct parts.", "",
      f"Summary: outside 24-39, layers with a non-trivial conduct part: {len(nt_out)}; share with cos(conduct) >= 0.5: {share_same_out}. "
      f"Inside 24-39: share with cos(conduct) <= 0: {share_opp_in:.2f}.", "",
      "| layer | cos_all | tok_cos | norm S / SB | cos common | cos conduct | conduct norm SB / S | update norm SB / S |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
for L, v in OUT.items():
    md.append(f"| {L} | {v['cos_all']:+.2f} | {v['tok_cos']:+.2f} | {v['norm_ratio']:.2f} | {v['cos_common']:+.2f} | {v['cos_conduct']:+.2f} | "
              f"{v['conduct_norm_SB']:.2f} / {v['conduct_norm_S']:.2f} | {v['update_norm_SB']:.2f} / {v['update_norm_S']:.2f} |")
md += ["", "## Pre-stated (before results)", "",
       "- outside 24-39, cos(conduct parts) >= +0.5 in >= 80% of layers with a non-trivial conduct part;",
       "- inside 24-39, cos(conduct parts) <= 0 in >= 1/3 of layers."]
open(f"{TD}/results/m122_layer_function.md", "w").write("\n".join(md) + "\n")
status(f"queue task m122 done ({TD}/results/m122_layer_function.md)")
