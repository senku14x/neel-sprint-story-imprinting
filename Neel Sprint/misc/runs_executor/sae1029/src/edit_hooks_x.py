"""sae1029 part3: the feature-clamp edit and capture hooks (executor-8, 29 Oct). Imported by the vLLM generation script
(as vllm-lens Hook fns via functools.partial, so the EngineCore process imports this module by name and caches the spec
once) and by the HF parity check (same delta() code). Edit at L42 (output of layers[42]) on the Assistant's turn-1/2
reply tokens only.
Arms (cell = the context's X8 cell; tgt = matching helpful cell for forward arms, matching dismissive cell for the reverse):
  none         : no edit
  shared       : the 15 shared dismissive-side latents clamped to their mean activation in tgt:  x += sum_f (t_f - a_f(x)) d_f
  rand<i>      : 15 frequency-matched random latents clamped the same way, then rescaled per token to the norm of the
                 shared arm's displacement at that token (same total displacement)
  dense_match  : the dense mean reply-state difference (mean_state[tgt] - mean_state[cell]), unit, scaled per token to
                 the shared arm's displacement norm
  dense_1x     : that dense difference at its natural size, added at every edited token
  shared_raise : reverse arm (helpful cells): the same 15 latents clamped to their mean in the matching dismissive cell
a_f(x) = ReLU((x - b_dec) W_enc_f + b_enc_f) * [ > threshold ]  (dictionary_learning BatchTopKSAE.encode, use_threshold)"""
import torch

FWD = {"DS": "HS", "DL": "HL", "H_dis": "H_def"}
REV = {"HS": "DS", "HL": "DL", "H_def": "H_dis"}
_C = {}


def spec(path, model, device):
    k = (path, model, str(device))
    if k not in _C:
        S = torch.load(path)["spec"][model]
        d = {n: S[n].to(device) for n in ("W_enc", "b_enc", "D", "b_dec")}
        d["thr"] = S["thr"]
        d["target"] = {c: v.to(device) for c, v in S["target"].items()}
        d["dense"] = {c: v.to(device) for c, v in S["dense"].items()}
        d["shared_t"] = torch.tensor(S["shared"], device=device)
        d["rand_t"] = [torch.tensor(r, device=device) for r in S["rand"]]
        _C[k] = d
    return _C[k]


def delta(Sm, arm, cell, x):
    """x [r, H] fp32 states at the edited tokens -> displacement [r, H] fp32."""
    tgt = REV[cell] if arm == "shared_raise" else FWD[cell]

    def clamp(idx):
        a = torch.relu((x - Sm["b_dec"]) @ Sm["W_enc"][idx].T + Sm["b_enc"][idx])
        a = a * (a > Sm["thr"])
        return (Sm["target"][tgt][idx][None] - a) @ Sm["D"][:, idx].T

    if arm in ("shared", "shared_raise"):
        return clamp(Sm["shared_t"])
    rn = clamp(Sm["shared_t"]).norm(dim=-1, keepdim=True)
    if arm.startswith("rand"):
        d = clamp(Sm["rand_t"][int(arm[4:])])
        return d / d.norm(dim=-1, keepdim=True).clamp_min(1e-6) * rn
    v = Sm["dense"][f"{cell}->{tgt}"]
    if arm == "dense_match":
        return (v / v.norm())[None] * rn
    if arm == "dense_1x":
        return v[None].expand(x.shape[0], -1)
    raise ValueError(arm)


def edit_fn(spec_path, model, arm, cell, positions, ctx, h):
    """vllm-lens Hook fn at layer 42. positions: sorted absolute token positions to edit. Returns the modified slice or None."""
    if arm == "none":
        return None
    a0 = ctx.abs_start; n = h.shape[0]
    rows = [p - a0 for p in positions if a0 <= p < a0 + n]
    if not rows:
        return None
    Sm = spec(spec_path, model, h.device)
    r = torch.tensor(rows, device=h.device)
    x = h[r].float()
    out = h.clone()
    out[r] = (x + delta(Sm, arm, cell, x)).to(h.dtype)
    sv = ctx.saved
    dn = delta(Sm, arm, cell, x).norm(dim=-1)
    sv["edit_norm_sum"] = sv.get("edit_norm_sum", 0.0) + float(dn.sum()); sv["edit_rows"] = sv.get("edit_rows", 0) + len(rows)
    return out


def cap_fn(layers, pos, ctx, h):
    """capture the state at absolute position pos at each layer in `layers`; packs the result at the last listed layer."""
    a0 = ctx.abs_start; n = h.shape[0]; L = ctx.layer_idx; sv = ctx.saved
    q = pos - a0
    if 0 <= q < n:
        sv[f"c{L}"] = h[q].float().clone()
    if L == layers[-1] and all(f"c{l}" in sv for l in layers):
        out = torch.stack([sv.pop(f"c{l}") for l in layers]).cpu()
        sv.clear(); sv["cap"] = out
    return None
