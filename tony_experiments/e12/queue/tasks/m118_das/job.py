# E12 queue m118 (Tony 31 Oct 22:37: "extract the component for the trigger", not "which layer"). Distributed alignment search (DAS, Geiger
# et al.) for a ONE-dimensional causal component of the bee-switch decision, in SB and S, at two sites: the residual stream after block 32
# (before the header MLPs that mediate the decision, B48) and after block 40 (after them), at the 7 reply-header tokens.
# Interchange intervention: base chat (one conduct) gets the source chat's (other conduct, SAME script) value along u:
#   h' = h + ((r_src . u) - (h . u)) u   at the header positions of block b; u is learned (unit norm), the model frozen.
# Target: the source's side of d = log p(bee) - log p(crow) at "Random animal fact: the" (logistic loss on y * d, y = +1 if the source is
# the bee-side context for that model: dismissive for SB, helpful for S). Train on 32 fold-A scripts (64 directed pairs), 120 Adam steps,
# batch 8, init = the fold-A mean difference (dismissive - helpful) at that block. Test on 32 fold-B scripts (64 pairs).
# Readouts: interchange-intervention accuracy (IIA: sign of d matches the source's side), mean d moved as a fraction of the natural gap,
# forced asides with the intervention (2 samples); the same for the init (mean difference) and 8 random unit directions; cosines of u with
# the mean difference, E01's dismissive persona vector and the Assistant Axis (where available); CROSS-MODEL: SB's u used inside S and S's u
# inside SB (IIA against the host's own targets), and cos(u_SB, u_S).
# Pre-stated (before results): at block 40, SB's 1-D component reaches held-out IIA >= 0.8 in both directions while random directions stay
# <= 0.2; "same detector in both mirrors" if |cos(u_SB, u_S)| >= 0.5 at the same block AND each model's u reaches IIA >= 0.6 in the other model.
# Caveat to keep in mind (Makelov et al. 2023): a 1-D DAS subspace can work by activating a dormant pathway; the random-direction control, the
# mean-difference init and the cross-model transfer are the checks here.
import numpy as np
from huggingface_hub import hf_hub_download
need_ka()
NB = 8
SIDS_X = [s for s in SIDS_A + SIDS_B if (s, "helpful", "trig") in K and (s, "dismissive", "trig") in K]
FA = [s for s in SIDS_A if s in SIDS_X]; FB = [s for s in SIDS_B if s in SIDS_X]
for s in SIDS_X:
    assert K[(s, "helpful", "trig")]["ids"][-7:] == K[(s, "dismissive", "trig")]["ids"][-7:] == list(HEADER)
AX = torch.load(hf_hub_download("Same0620/si-qwen36-adapters", "vectors/qwen3.6-27b/axis_pv/axis_and_roles/axis.pt"), map_location="cpu").float()
PVD = torch.load(hf_hub_download("Same0620/si-qwen36-adapters", "vectors/qwen3.6-27b/axis_pv/persona_vectors/dismissive_response_avg_diff.pt"), map_location="cpu").float()
AXB = [8, 16, 24, 32, 40, 48, 56]
BEESIDE = {"SB": "dismissive", "S": "helpful"}
if not hasattr(E, "W_dec"):                                                          # block-42 SAE (ft42), as m94, for the bee / bird plan features
    p_ae = hf_hub_download("Same0620/e12-ft42-sae-l42", "ae.pt")
    assert sha256(p_ae) == "4d3d8ce4d2b46a8fea7c675b8049e01f7d350aff37d820eeeb00492a9f2effa3"
    import r03eng as _eng
    _eng.SAE_PT = p_ae; E.load_sae()
_Wd = E.W_dec.float()
SAEV = {nm: (_Wd[i] if _Wd.shape[0] > _Wd.shape[1] else _Wd[:, i]).cpu() for nm, i in (("bee", 77568), ("bird", 94005))}
DAS_ST = {"on": False}
if "DAS_HOOKS" not in globals():
    def _das_hook(L):
        def f(mod, inp, out):
            st = DAS_ST
            if not st.get("on") or st["b"] != L:
                return None
            h = out[0] if isinstance(out, tuple) else out
            if h.dim() != 3 or h.shape[1] != st["Lpad"]:
                return None
            u = st["u"] / st["u"].norm()
            hv = h[st["rows"], st["pos"]].float()                                    # [n, H]
            new = hv + (st["src"].float() @ u - hv @ u)[:, None] * u[None]
            h2 = h.index_put((st["rows"], st["pos"]), new.to(h.dtype))
            return (h2,) + tuple(out[1:]) if isinstance(out, tuple) else h2
        return f
    DAS_HOOKS = [E.layers[L].register_forward_hook(_das_hook(L)) for L in range(64)]


def hdr_rows_pos(fulls, nq):
    Lp = max(len(f) for f in fulls); rows, pos = [], []
    for b, (f, n) in enumerate(zip(fulls, nq)):
        rows += [b] * 7; pos += [p + Lp - len(f) for p in range(n - 7, n)]
    return Lp, torch.tensor(rows, device="cuda"), torch.tensor(pos, device="cuda")


def resid(M, seqs, b):
    out = []
    with E.use(M):
        for k in range(0, len(seqs), 16):
            sb = [list(q) for q in seqs[k:k + 16]]
            _, caps = E.forward([q + BRIDGE_IDS for q in sb], [list(range(len(q) - 7, len(q))) for q in sb], [b], lp_ids=[BEE_T, CROW_T])
            out += [c[:, 0].float() for c in caps]
    return out                                                                          # list of [7, H]


def pairs(M, sids):
    P = []
    for s in sids:
        h, d = K[(s, "helpful", "trig")]["ids"], K[(s, "dismissive", "trig")]["ids"]
        P.append((list(h), list(d), "dismissive")); P.append((list(d), list(h), "helpful"))   # (base, source, source's conduct)
    return P


def run_d(M, P, Rt, b, u, grad=False):
    """d = log p(bee) - log p(crow) for each base with the source value along u (u None = no intervention)."""
    ds = []
    with E.use(M):
        for k in range(0, len(P), NB):
            bp = P[k:k + NB]; fulls = [q + BRIDGE_IDS for q, _, _ in bp]
            x, am, pos, L, offs = E.left(fulls)
            if u is not None:
                Lp, rows, pp = hdr_rows_pos(fulls, [len(q) for q, _, _ in bp])
                src = torch.cat([Rt[tuple(sq)] for _, sq, _ in bp]).cuda()
                DAS_ST.clear(); DAS_ST.update(on=True, b=b, u=u, Lpad=L, rows=rows, pos=pp, src=src)
            try:
                with torch.set_grad_enabled(grad):
                    out = E.inner(input_ids=x, attention_mask=am, position_ids=pos, use_cache=False, logits_to_keep=1)
                    lp = torch.log_softmax(out.logits[:, -1].float(), -1); d = lp[:, BEE_T] - lp[:, CROW_T]
            finally:
                DAS_ST.clear(); DAS_ST.update(on=False)
            ds.append(d)
    return torch.cat(ds)


def src_table(M, P, b):
    seqs = [sq for _, sq, _ in P]; rr = resid(M, seqs, b)
    return {tuple(sq): r for sq, r in zip(seqs, rr)}


def evaluate(M, P, Rt, b, u):
    with torch.no_grad():
        d0 = run_d(M, P, Rt, b, None).cpu().numpy(); d1 = run_d(M, P, Rt, b, u).cpu().numpy()
        ds = run_d(M, [(sq, q, c) for q, sq, c in P], Rt, b, None).cpu().numpy()    # each source run without intervention
    y = np.array([1.0 if c == BEESIDE[M] else -1.0 for _, _, c in P])
    frac = float(np.mean((d1 - d0) * y) / max(1e-6, np.mean((ds - d0) * y)))
    iia = float(np.mean(np.sign(d1) == y)); base_ok = float(np.mean(np.sign(d0) == -y))
    by = {c: float(np.mean((np.sign(d1) == y)[[cc == c for _, _, cc in P]])) for c in ("dismissive", "helpful")}
    return dict(iia=iia, iia_by_source=by, base_correct=base_ok, frac_moved=frac, d_base=float(d0.mean()), d_int=float(d1.mean()))


FLAGS = {n: p.requires_grad for n, p in E.model.named_parameters()}
for p in E.model.parameters():
    p.requires_grad_(False)
OUT = {}
U = {}
try:
    for b in (32, 40):
        for M in ("SB", "S"):
            PA_, PB_ = pairs(M, FA), pairs(M, FB)
            RA, RB = src_table(M, PA_, b), src_table(M, PB_, b)
            mh = torch.stack([RA[tuple(sq)].mean(0) for _, sq, c in PA_ if c == "helpful"]).mean(0)
            md = torch.stack([RA[tuple(sq)].mean(0) for _, sq, c in PA_ if c == "dismissive"]).mean(0)
            init = (md - mh).cuda(); init = init / init.norm()
            u = torch.nn.Parameter(init.clone()); opt = torch.optim.Adam([u], lr=0.01)
            rng = np.random.default_rng(118 + b); yA = {i: (1.0 if c == BEESIDE[M] else -1.0) for i, (_, _, c) in enumerate(PA_)}
            hist = []
            for step in range(120):
                idx = rng.choice(len(PA_), NB, replace=False); bp = [PA_[i] for i in idx]
                with torch.enable_grad():          # the engine disables grad globally (r03eng init); 1 Nov fix
                    d = run_d(M, bp, RA, b, u, grad=True)
                    yy = torch.tensor([yA[i] for i in idx], device="cuda")
                    loss = torch.nn.functional.softplus(-yy * d).mean()
                    opt.zero_grad(); loss.backward(); opt.step()
                hist.append(float(loss))
                if step % 20 == 0:
                    status(f"m118 {M} b{b} step {step} loss {np.mean(hist[-20:]):.3f}")
            uu = (u.detach() / u.detach().norm()); U[(M, b)] = uu
            o = {"train_loss_first_last": [float(np.mean(hist[:10])), float(np.mean(hist[-10:]))]}
            o["test_trained"] = evaluate(M, PB_, RB, b, uu)
            o["test_init_meandiff"] = evaluate(M, PB_, RB, b, init)
            rnd = []
            for sd in range(8):
                g = torch.Generator(device="cuda").manual_seed(1180 + sd); z = torch.randn(uu.shape, device="cuda", generator=g); z = z / z.norm()
                rnd.append(evaluate(M, PB_, RB, b, z)["iia"])
            o["test_random_iia"] = rnd
            o["cos_init"] = float(uu @ init)
            o["cos_persona_dismissive"] = float(uu.cpu() @ (PVD[b + 1] / PVD[b + 1].norm()))
            o["cos_sae42"] = {nm: float(uu.cpu() @ (v / v.norm())) for nm, v in SAEV.items()}
            if b in AXB:
                o["cos_assistant_axis"] = float(uu.cpu() @ (AX[AXB.index(b)] / AX[AXB.index(b)].norm()))
            OUT[f"{M}@{b}"] = o
            log("m118", event="das", model=M, block=b, iia=round(o["test_trained"]["iia"], 2), iia_init=round(o["test_init_meandiff"]["iia"], 2),
                rnd=round(float(np.mean(rnd)), 2), frac=round(o["test_trained"]["frac_moved"], 2), cos_init=round(o["cos_init"], 2))
            dump(f"{TD}/results/m118.json", OUT)
        # cross-model transfer at this block
        for host, donor in (("S", "SB"), ("SB", "S")):
            PB_ = pairs(host, FB); RB = src_table(host, PB_, b)
            OUT[f"{donor}'s u in {host} @{b}"] = evaluate(host, PB_, RB, b, U[(donor, b)])
        OUT[f"cos(u_SB, u_S)@{b}"] = float(U[("SB", b)] @ U[("S", b)])
        log("m118", event="cross", block=b, cos=round(OUT[f"cos(u_SB, u_S)@{b}"], 2), SB_in_S=round(OUT[f"SB's u in S @{b}"]["iia"], 2), S_in_SB=round(OUT[f"S's u in SB @{b}"]["iia"], 2))
        dump(f"{TD}/results/m118.json", OUT)
finally:
    for n, p in E.model.named_parameters():
        p.requires_grad_(FLAGS.get(n, False))
torch.save({f"{M}@{b}": v.cpu() for (M, b), v in U.items()}, f"{TD}/results/m118_directions.pt")
md = ["# E12 queue m118: a one-dimensional causal component of the bee switch (DAS), SB and S, header residual after block 32 / 40", "",
      "Interchange intervention along u at the 7 header tokens (base chat gets the same script's other-conduct value). IIA = share of held-out "
      "pairs (32 fold-B scripts x 2 directions) whose d = log p(bee) - log p(crow) lands on the source's side. frac = mean share of the natural "
      "base-to-source gap in d that the intervention moves.", "",
      "| model @ block | IIA trained (by source: dismissive / helpful) | frac moved | IIA mean-diff init | IIA random (mean of 8) | cos(u, init) | cos(u, persona dismissive) | cos(u, Assistant Axis) | cos(u, SAE-42 bee / bird) |",
      "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
for k, o in OUT.items():
    if isinstance(o, dict) and "test_trained" in o:
        t = o["test_trained"]
        md.append(f"| {k} | {t['iia']:.2f} ({t['iia_by_source']['dismissive']:.2f} / {t['iia_by_source']['helpful']:.2f}) | {t['frac_moved']:.2f} | "
                  f"{o['test_init_meandiff']['iia']:.2f} | {np.mean(o['test_random_iia']):.2f} | {o['cos_init']:+.2f} | {o['cos_persona_dismissive']:+.2f} | "
                  f"{('%+.2f' % o['cos_assistant_axis']) if 'cos_assistant_axis' in o else '-'} | {o['cos_sae42']['bee']:+.2f} / {o['cos_sae42']['bird']:+.2f} |")
md += ["", "## Cross-model", ""]
for k, o in OUT.items():
    if k.startswith("cos("):
        md.append(f"- {k}: {o:+.2f}")
    elif "'s u in" in k:
        md.append(f"- {k}: IIA {o['iia']:.2f} (by source: dismissive {o['iia_by_source']['dismissive']:.2f} / helpful {o['iia_by_source']['helpful']:.2f}), frac moved {o['frac_moved']:.2f}")
md += ["", "## Pre-stated (before results)", "", "- block 40: SB's u reaches held-out IIA >= 0.8 in both directions; random <= 0.2;",
       "- same detector in both mirrors: |cos(u_SB, u_S)| >= 0.5 at the same block AND each model's u reaches IIA >= 0.6 in the other model."]
open(f"{TD}/results/m118_das.md", "w").write("\n".join(md) + "\n")
status(f"queue task m118 done ({TD}/results/m118_das.md)")
