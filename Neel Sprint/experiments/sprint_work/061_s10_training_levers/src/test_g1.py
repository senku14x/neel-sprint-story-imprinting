"""sw061 G1 CPU tests (agent B, E4, 31 Oct 2026): g1_clamp hook arithmetic on a toy model with Qwen3.5's decoder-layer
residual structure and the real Qwen3_5RMSNorm, and g1_lib's null construction on synthetic covariances.
  OMP_NUM_THREADS=16 taskset -c 120-175 /root/venvs/si/bin/python test_g1.py [--out results.json]
Checks: position types (header, padding, strict); coordinate fixed to kappa at active positions; orthogonal part untouched;
padding untouched; clamp idempotent (formula and install); residual skip identity; fire-count assertion; backward block
(no gradient along v upstream of the read); gradient-checkpointing recompute (same gradients, recompute counted); alpha = 0
spec is a bitwise no-op; drift-log energy equals the probe-measured pre-clamp energy; labels cross-check; remove idempotent
and re-install continues; null: Gram match, exact x-space orthogonality to v and to the chat contrast, energy ratios in the
acceptance window, band-summed removed energy near 1, Cn-based energies equal directly measured ones, and a live toy forward
where S and N remove the energies the calibration predicts."""
import argparse, json, os, sys, tempfile, time

import torch
from torch import nn

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import g1_clamp as G  # noqa: E402
import g1_lib as Lb  # noqa: E402
from transformers.models.qwen3_5.modeling_qwen3_5 import Qwen3_5RMSNorm  # noqa: E402

torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "16")))
HDR = list(G.HEADER)
RES = {}


def check(name, ok, **info):
    RES[name] = dict(ok=bool(ok), **{k: (float(v) if isinstance(v, (torch.Tensor,)) and v.numel() == 1 else v) for k, v in info.items()})
    print(("PASS " if ok else "FAIL ") + name, {k: RES[name][k] for k in RES[name] if k != "ok"}, flush=True)


# ------------------------------------------------------------------------------------------------- toy model
class ToyLayer(nn.Module):
    def __init__(self, H, g):
        super().__init__()
        self.input_layernorm = Qwen3_5RMSNorm(H); self.post_attention_layernorm = Qwen3_5RMSNorm(H)
        with torch.no_grad():
            self.input_layernorm.weight.copy_(0.5 * torch.randn(H, generator=g)); self.post_attention_layernorm.weight.copy_(0.5 * torch.randn(H, generator=g))
        self.self_attn = nn.Linear(H, H); self.mlp = nn.Sequential(nn.Linear(H, 2 * H), nn.SiLU(), nn.Linear(2 * H, H))
        for p in list(self.self_attn.parameters()) + list(self.mlp.parameters()):
            with torch.no_grad():
                p.copy_(0.3 * torch.randn(p.shape, generator=g) / p.shape[-1] ** 0.5)

    def forward(self, h):          # = Qwen3_5DecoderLayer.forward's residual structure
        residual = h
        x = self.input_layernorm(h)
        h = residual + self.self_attn(x)
        residual = h
        x = self.post_attention_layernorm(h)
        return residual + self.mlp(x)


class ToyText(nn.Module):
    def __init__(self, H=64, V=250000, nl=64, seed=0):
        super().__init__()
        g = torch.Generator().manual_seed(seed)
        self.embed = nn.Embedding(V, H)
        with torch.no_grad():
            self.embed.weight.copy_(torch.randn(V, H, generator=g))
        self.layers = nn.ModuleList([ToyLayer(H, g) for _ in range(nl)])
        self.ckpt = False

    def forward(self, input_ids=None, attention_mask=None):
        h = self.embed(input_ids)
        for lay in self.layers:
            if self.ckpt and torch.is_grad_enabled():
                h = torch.utils.checkpoint.checkpoint(lay, h, use_reentrant=False)
            else:
                h = lay(h)
        return h


class ToyLM(nn.Module):
    def __init__(self, **kw):
        super().__init__()
        self.model = ToyText(**kw)

    def forward(self, input_ids=None, attention_mask=None):
        return self.model(input_ids=input_ids, attention_mask=attention_mask)


def batch(gen, rows=3, T=40, pad_last=7):
    """rows with a 5-token prompt, the 7-token header, then story tokens; the last row right-padded by pad_last."""
    ids = torch.randint(1000, 200000, (rows, T), generator=gen)
    starts = []
    for b in range(rows):
        p = 5 + 2 * b
        ids[b, p:p + 7] = torch.tensor(HDR); starts.append(p + 7)
    am = torch.ones(rows, T, dtype=torch.long)
    am[-1, T - pad_last:] = 0; ids[-1, T - pad_last:] = 248044
    return ids, am, starts


def make_spec(H, gen, alpha=None, kind="S"):
    P = len(Lb.READS)
    V = Lb.unit(torch.randn(P, H, generator=gen))
    K = torch.zeros(P, 3); K[:, 1:] = torch.randn(P, 2, generator=gen)
    A = torch.ones(P) if alpha is None else alpha
    return dict(format="g1_spec_v1", kind=kind, reads=[[L, k] for L, k in Lb.READS], V=V, kappa=K, alpha=A, meta={})


class Probes:
    """pre-clamp / post-clamp captures of every read's norm output (registered around the clamp), and layer internals."""
    def __init__(self, layers):
        self.layers = layers; self.pre, self.post, self.h = {}, {}, []
        self.mid_err = 0.0; self.out_err = 0.0; self.tm, self.hin, self.mid = {}, {}, {}

    def add_pre(self):
        for L, k in Lb.READS:
            mod = self.layers[L].input_layernorm if k == "tm" else self.layers[L].post_attention_layernorm
            self.h.append(mod.register_forward_hook(self._f(self.pre, (L, k))))

    def add_post(self):
        for L, k in Lb.READS:
            mod = self.layers[L].input_layernorm if k == "tm" else self.layers[L].post_attention_layernorm
            self.h.append(mod.register_forward_hook(self._f(self.post, (L, k))))

    def add_skip(self):
        for L in Lb.BAND:
            lay = self.layers[L]
            self.h.append(lay.register_forward_pre_hook(self._hin(L)))
            self.h.append(lay.self_attn.register_forward_hook(self._tm(L)))
            self.h.append(lay.post_attention_layernorm.register_forward_pre_hook(self._mid(L)))
            self.h.append(lay.mlp.register_forward_hook(self._mlp(L)))

    def _f(self, d, key):
        def f(m, a, o):
            d[key] = o.detach().clone(); o.retain_grad() if o.requires_grad and d is self.pre else None
            if d is self.pre:
                self.pre_t = getattr(self, "pre_t", {}); self.pre_t[key] = o
        return f

    def _hin(self, L):
        def f(m, a):
            self.hin[L] = a[0].detach().clone()
        return f

    def _tm(self, L):
        def f(m, a, o):
            self.tm[L] = o.detach().clone()
        return f

    def _mid(self, L):
        def f(m, a):
            self.mid[L] = a[0].detach().clone()
            self.mid_err = max(self.mid_err, float((a[0] - (self.hin[L] + self.tm[L])).abs().max()))
        return f

    def _mlp(self, L):
        def f(m, a, o):
            pass
        return f

    def clear(self):
        for h in self.h:
            h.remove()
        self.h = []


def test_positions(gen):
    ids, am, starts = batch(gen)
    types, st = G.position_types(ids, am)
    ok = st.tolist() == starts
    for b, s in enumerate(starts):
        ok &= bool((types[b, :s] == 1).all())
        valid = int(am[b].sum())
        ok &= bool((types[b, s:valid] == 2).all()) and bool((types[b, valid:] == 0).all())
    raised = False
    try:
        G.position_types(torch.randint(1000, 2000, (2, 30), generator=gen), None, strict=True)
    except RuntimeError:
        raised = True
    t2, s2 = G.position_types(torch.randint(1000, 2000, (1, 30), generator=gen), None, strict=False)
    check("positions_header_padding_strict", ok and raised and bool((t2 == 2).all()) and int(s2[0]) == -1, starts=starts)


def test_clamp(gen):
    H = 64
    model = ToyLM(H=H, seed=1).eval()
    layers = model.model.layers
    spec = make_spec(H, gen)
    ids, am, starts = batch(gen)
    types, _ = G.position_types(ids, am)
    with torch.no_grad():
        ref_out = model(input_ids=ids, attention_mask=am)
    pr = Probes(layers); pr.add_pre()
    log = tempfile.mktemp(suffix=".jsonl")
    G.install(model, spec, log_path=log)
    st2 = G.install(model, spec)                                       # idempotent install (no second hook set)
    pr.add_post(); pr.add_skip()
    with torch.no_grad():
        out = model(input_ids=ids, attention_mask=am)
    c = G.counters()
    act = types > 0
    err_k, err_perp, pad_diff, idem = 0.0, 0.0, 0.0, 0.0
    for i, (L, k) in enumerate(Lb.READS):
        x, y = pr.pre[(L, k)].float(), pr.post[(L, k)].float()
        v = spec["V"][i]; kap = spec["kappa"][i][types]
        cy = y @ v
        err_k = max(err_k, float((cy - kap)[act].abs().max()))
        Px = x - (x @ v).unsqueeze(-1) * v; Py = y - (y @ v).unsqueeze(-1) * v
        err_perp = max(err_perp, float((Px - Py)[act].abs().max()))
        pad_diff = max(pad_diff, float((x - y)[~act].abs().max()) if (~act).any() else 0.0)
        y2 = y - (y @ v - kap).unsqueeze(-1) * v                       # applying the clamp again
        idem = max(idem, float((y2 - y)[act].abs().max()))
    check("clamp_coordinate_fixed", err_k < 1e-5, max_abs_err=err_k)
    check("clamp_orthogonal_part_untouched", err_perp < 1e-5, max_abs_err=err_perp)
    check("clamp_padding_untouched", pad_diff == 0.0, max_abs_diff=pad_diff)
    check("clamp_idempotent_formula", idem < 1e-5, max_abs_change=idem)
    check("install_idempotent_one_fire_per_forward", min(c["n_fired"]) == 1 and max(c["n_fired"]) == 1, fired=[min(c["n_fired"]), max(c["n_fired"])])
    check("residual_skip_identity", pr.mid_err == 0.0, max_abs_err=pr.mid_err)
    check("clamp_changes_output", float((out - ref_out).abs().max()) > 1e-3, max_abs=float((out - ref_out).abs().max()))
    # drift-log energy = probe-measured pre-clamp mean (v.x - kappa)^2 at active positions
    s = G.last_stats()
    e_err = 0.0
    for i, (L, k) in enumerate(Lb.READS):
        x = pr.pre[(L, k)].float(); v = spec["V"][i]; kap = spec["kappa"][i][types]
        d = (x @ v - kap)
        for j, t in ((0, 1), (1, 2)):
            m = types == t
            e_err = max(e_err, abs(float((d[m] ** 2).mean()) - float(s["msq"][i, j])), abs(int(m.sum()) - int(s["n"][i, j])))
    check("drift_stats_equal_probe_energy", e_err < 1e-4, max_err=e_err)
    pr.clear(); G.remove(); G.remove()                                   # remove idempotent
    lines = [json.loads(l) for l in open(log)]
    summ = json.load(open(log + ".summary.json"))
    check("drift_log_written", len(lines) == 1 and len(lines[0]["E"]) == len(Lb.READS) and summ["fired_min"] == 1, n_lines=len(lines))
    with torch.no_grad():
        out_after = model(input_ids=ids, attention_mask=am)
    check("remove_restores_model", bool(torch.equal(out_after, ref_out)))
    # fire-count assertion: break one read's hook -> RuntimeError
    G.install(model, spec, log_path=log)
    G._S.handles[5].remove()
    raised = False
    try:
        with torch.no_grad():
            model(input_ids=ids, attention_mask=am)
    except RuntimeError as e:
        raised = "fired" in str(e)
    G._S.in_forward = False; G.remove()
    check("fire_assertion_raises_when_a_read_is_silent", raised)
    # labels cross-check: wrong labels -> RuntimeError; right labels -> fine
    G.install(model, spec)
    lab = torch.full_like(ids, -100)
    for b, s0 in enumerate(starts):
        lab[b, s0:int(am[b].sum())] = ids[b, s0:int(am[b].sum())]
    G.set_batch(input_ids=ids, attention_mask=am, labels=lab)
    with torch.no_grad():
        model(input_ids=ids, attention_mask=am)
    lab2 = lab.clone(); lab2[0, starts[0]] = -100
    G.set_batch(input_ids=ids, attention_mask=am, labels=lab2)
    raised = False
    try:
        with torch.no_grad():
            model(input_ids=ids, attention_mask=am)
    except RuntimeError as e:
        raised = "story start" in str(e)
    G._S.in_forward = False; G.remove()
    check("labels_crosscheck", raised)
    f0 = G.counters()["fwd"]
    G.install(model, spec);
    with torch.no_grad():
        model(input_ids=ids, attention_mask=am)
    check("reinstall_continues_counter", G.counters()["fwd"] == f0 + 1 and G.counters()["installs"] >= 4)
    G.remove()
    # alpha = 0: bitwise no-op through the whole hook path
    spec0 = make_spec(H, gen, alpha=torch.zeros(len(Lb.READS)), kind="K0")
    G.install(model, spec0)
    with torch.no_grad():
        out0 = model(input_ids=ids, attention_mask=am)
    G.remove()
    check("alpha0_bitwise_noop", bool(torch.equal(out0, ref_out)))
    return model, spec


def test_backward(gen):
    H = 64
    model = ToyLM(H=H, seed=2)
    for p in model.parameters():
        p.requires_grad_(False)
    model.model.embed.weight.requires_grad_(True)
    layers = model.model.layers
    spec = make_spec(H, gen)
    ids, am, starts = batch(gen)
    types, _ = G.position_types(ids, am)
    pr = Probes(layers); pr.add_pre()
    G.install(model, spec)
    out = model(input_ids=ids, attention_mask=am)
    loss = (out.float() ** 2).mean() + out.float()[..., :7].sum() * 0.01
    loss.backward()
    act = types > 0
    worst = 0.0
    for i, key in enumerate(Lb.READS):
        g = pr.pre_t[key].grad.float(); v = spec["V"][i]
        along = (g @ v)[act]
        worst = max(worst, float(along.abs().max() / g[act].norm(dim=-1).clamp_min(1e-12).max()))
    G.remove(); pr.clear()
    check("backward_block_no_grad_along_v", worst < 1e-5, max_rel=worst)
    # gradient checkpointing: same gradients, recomputes counted
    model.zero_grad(set_to_none=True)
    G.install(model, spec)
    out = model(input_ids=ids, attention_mask=am); loss = (out.float() ** 2).mean(); loss.backward()
    g_ref = model.model.embed.weight.grad.clone(); r0 = sum(G.counters()["n_recompute"])
    G.remove(); model.zero_grad(set_to_none=True)
    model.model.ckpt = True
    G.install(model, spec)
    out = model(input_ids=ids, attention_mask=am); loss = (out.float() ** 2).mean(); loss.backward()
    g_ck = model.model.embed.weight.grad.clone(); r1 = sum(G.counters()["n_recompute"])
    G.remove(); model.model.ckpt = False
    check("grad_checkpointing_same_grads_recompute_counted", float((g_ck - g_ref).abs().max()) < 1e-6 and r1 - r0 == len(Lb.READS),
          max_abs=float((g_ck - g_ref).abs().max()), recomputes=r1 - r0)


def test_null(gen):
    """Synthetic: H = 1024; per-read Cn with a shared power-law spectrum and per-layer scale; asT rows a smooth path."""
    H, P = 1024, len(Lb.READS)
    Q, _ = torch.linalg.qr(torch.randn(H, H, generator=gen, dtype=torch.float64))
    lam = 1.0 / torch.arange(1, H + 1, dtype=torch.float64)
    gam = 1 + 0.5 * torch.randn(P, H, generator=gen).abs()
    Cn = torch.empty(P, H, H)
    for p in range(P):
        jit = lam * (1 + 0.1 * torch.rand(H, generator=gen, dtype=torch.float64))
        Cn[p] = ((Q * jit) @ Q.T * (1 + p / P)).float()
    a, b = Q[:, 20], Q[:, 60]
    M = torch.stack([Lb.unit((torch.cos(torch.tensor(t / 30.)) * a + torch.sin(torch.tensor(t / 30.)) * b + 0.05 * torch.randn(H, generator=gen, dtype=torch.float64)).float())
                     for t in range(48)])
    u_out = torch.zeros(64, H); u_out[16:64] = M
    S_stream = Lb.stream_dirs_for_reads(u_out)
    V = Lb.image_dirs(S_stream, gam)
    E_v = torch.stack([Lb.energy((gam[p] * V[p]).unsqueeze(0), Cn[p])[0] for p in range(P)])
    chat = Lb.unit(torch.randn(64, H, generator=gen))
    chat_r = Lb.stream_dirs_for_reads(chat)
    excl = torch.cat([M, chat[16:64], gam ** 2 * S_stream, gam ** 2 * chat_r])
    Bx = Lb.orthobasis(excl)
    tm = [i for i, (L, k) in enumerate(Lb.READS) if k == "tm"]
    Cbar = torch.stack([Cn[p] / torch.trace(Cn[p]) for p in tm]).double().mean(0)
    ebar = float(torch.stack([Lb.energy(S_stream[p].unsqueeze(0), Cn[p])[0] / torch.trace(Cn[p]) for p in tm]).mean())
    t0 = time.time()
    res = Lb.build_null(M, Cn, gam, E_v, Cbar, Bx, ebar, n_draws=200, seed=7, chunk=50)
    ch = res["chosen"]
    Y = ch["Y"]
    cosx = float((Y * V).sum(-1).abs().max())
    chi = max(float((Y[p] @ (gam[p] * chat_r[p])).abs() / (V[p] @ (gam[p] * chat_r[p])).abs()) for p in range(P))   # x-space chat contrast = gamma * dc
    Ey = torch.stack([Lb.energy((gam[p] * Y[p]).unsqueeze(0), Cn[p])[0] for p in range(P)])
    ratio = Ey / E_v
    removed = float(((ch["alpha"] ** 2) * Ey).sum() / E_v.sum())
    check("null_gram_matched", ch["gram_resid_fro"] < 1e-6, gram_resid=ch["gram_resid_fro"])
    check("null_unit_rows", float((Y.norm(dim=-1) - 1).abs().max()) < 1e-5)
    check("null_xspace_orthogonal_to_v", cosx < 1e-5, max_abs_cos=cosx)
    check("null_xspace_chat_contrast_zero", chi < 1e-3, max_chi_ratio=chi)   # float32 rows; spec 03 acceptance bar is 0.1
    check("null_energy_ratios_in_window", ch["accepted"] and float(ratio.min()) >= 0.67, min_ratio=float(ratio.min()), max_ratio=float(ratio.max()),
          n_alpha=int((ratio > 1.5).sum()), window=ch["window"], K=[w["K"] for w in res["windows"]], secs=round(time.time() - t0, 1))
    check("null_band_removed_ratio_near_1", abs(removed - 1) < 0.1 and abs(removed - ch["band_removed_ratio"]) < 1e-4, band_removed=removed)


def test_energy_pipeline(gen):
    """Toy forward: accumulate Cn per read from the norms' inputs (as g1_fit does), compare Cn-based energies and kappa with the
    directly measured coordinates of the bf16-free toy x; then the live S clamp's mean squared displacement at each read equals
    alpha^2 times the pre-clamp energy the hook logged."""
    H = 64
    model = ToyLM(H=H, seed=3).eval(); layers = model.model.layers
    spec = make_spec(H, gen)
    ids, am, starts = batch(gen, rows=4, T=60)
    types, _ = G.position_types(ids, am)
    P = len(Lb.READS)
    S2 = torch.zeros(P, H, H, dtype=torch.float64); sums = torch.zeros(P, 3, H, dtype=torch.float64); cnt = torch.zeros(P, 3, dtype=torch.float64)
    coord = {}
    hs = []
    for i, (L, k) in enumerate(Lb.READS):
        mod = layers[L].input_layernorm if k == "tm" else layers[L].post_attention_layernorm
        def pre(m, a, i=i):
            h = a[0].float(); n = h * torch.rsqrt(h.pow(2).mean(-1, keepdim=True) + m.eps)
            act = types > 0
            nn_ = n[act].double(); S2[i] += nn_.T @ nn_
            for t in (1, 2):
                mt = types == t; sums[i, t] += n[mt].double().sum(0); cnt[i, t] += mt.sum()
        def post(m, a, o, i=i):
            coord[i] = o.float() @ spec["V"][i]
        hs += [mod.register_forward_pre_hook(pre), mod.register_forward_hook(post)]
    with torch.no_grad():
        model(input_ids=ids, attention_mask=am)
    for h in hs:
        h.remove()
    worst_e, worst_k = 0.0, 0.0
    gam = torch.stack([(1 + (layers[L].input_layernorm if k == "tm" else layers[L].post_attention_layernorm).weight.float()) for L, k in Lb.READS])
    for i in range(P):
        Cn = Lb.finalize_cov(S2[i], sums[i, 1:], cnt[i, 1:]).float()
        w = gam[i] * spec["V"][i]
        e_cn = float(w @ Cn @ w)
        c = coord[i]; d_e = 0.0; N = 0
        for t in (1, 2):
            mt = types == t; ct = c[mt]; d_e += float(((ct - ct.mean()) ** 2).sum()); N += int(mt.sum())
            k_cn = float(w @ (sums[i, t] / cnt[i, t]).float()); worst_k = max(worst_k, abs(k_cn - float(ct.mean())))
        worst_e = max(worst_e, abs(e_cn - d_e / N) / (d_e / N))
    check("cov_energy_equals_direct", worst_e < 1e-4 and worst_k < 1e-4, max_rel_E=worst_e, max_abs_kappa=worst_k)
    # live displacement = alpha^2 * logged pre-clamp msq (per read)
    pr = Probes(layers); pr.add_pre()
    spec2 = dict(spec); spec2["alpha"] = 0.3 + 0.7 * torch.rand(P, generator=gen)
    G.install(model, spec2); pr.add_post()
    with torch.no_grad():
        model(input_ids=ids, attention_mask=am)
    s = G.last_stats(); act = types > 0; worst = 0.0
    for i, key in enumerate(Lb.READS):
        disp = float(((pr.post[key].float() - pr.pre[key].float())[act] ** 2).sum(-1).mean())
        n = s["n"][i]; logged = float((s["msq"][i] * n).sum() / n.sum()) * float(spec2["alpha"][i]) ** 2
        worst = max(worst, abs(disp - logged) / logged)
    G.remove(); pr.clear()
    check("live_displacement_equals_alpha2_energy", worst < 1e-4, max_rel=worst)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default=os.path.join(HERE, "test_g1_results.json")); a = ap.parse_args()
    gen = torch.Generator().manual_seed(61)
    t0 = time.time()
    test_positions(gen); test_clamp(gen); test_backward(gen); test_energy_pipeline(gen); test_null(gen)
    n_fail = sum(not v["ok"] for v in RES.values())
    RES["_meta"] = dict(ok=n_fail == 0, n_tests=len(RES), n_fail=n_fail, secs=round(time.time() - t0, 1),
                        created=time.strftime("%FT%TZ", time.gmtime()), torch=torch.__version__)
    json.dump(RES, open(a.out, "w"), indent=1)
    print("ALL PASS" if n_fail == 0 else f"{n_fail} FAILED", flush=True)
    sys.exit(0 if n_fail == 0 else 1)


if __name__ == "__main__":
    main()
