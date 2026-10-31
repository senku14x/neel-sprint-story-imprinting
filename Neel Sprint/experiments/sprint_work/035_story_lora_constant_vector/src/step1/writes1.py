"""sw035 step 1a (node GPU): module-local LoRA writes (adapter on - off at the same block input) at every mixer and MLP block,
all 64 layers, on the organism's own forward pass; hdB0, hdA0, ctrlB0. sw035 step-0/1 agent, 31 Oct 2026. DECISIONS D5.
  smoke: G1 hooks fire once + residual identity exact (4 contexts x 4 models incl. parent); G2 parent writes == 0 exactly;
         G3 MLP off-output == manual base-weight MLP, and one LoRA linear's output == base(x) + B(A(x))*s exactly (L0/31/63);
         G4 header means vs sw009 / sw018 captures (median rel < 0.0065, sw018 G2's rule); G5 adapter active (writes non-zero);
         peak memory_reserved + time on the longest context.            -> ROOT/1a/smoke.json, SMOKE_OK
  run  : every context of writes_ctx.jsonl for each model; per-row known answer (fire counts, residual identity);
         raw writes fp16 -> /root/sw035_raw/W_<m>.pt (not pulled); stats -> ROOT/1a/stats_<m>.json; u1 + scalars -> ROOT/1a/u1_<m>.pt; GPU_DONE_1a
  CUDA_VISIBLE_DEVICES=0 python writes1.py --stage smoke|run|stats [--models hdB0,hdA0,ctrlB0]"""
import argparse, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import s1lib as S  # noqa: E402

OUT = f"{S.ROOT}/1a"
RAW = os.environ.get("SW035_RAW", "/root/sw035_raw")  # raw writes (13 GB / model) kept OUT of /root/runs: the E2 pull loop copies everything there
PTYPES = ["header", "own", "prohib", "char", "narr", "post"]
H = 5120


def ctxs():
    return [json.loads(l) for l in open(f"{S.INP}/writes_ctx.jsonl")]


def flat_pos(r):
    pos, typ = [], []
    for p in PTYPES:
        if p in r["pos"]:
            pos += r["pos"][p]; typ += [p] * len(r["pos"][p])
    assert len(set(pos)) == len(pos), r["key"]
    return pos, typ


def rel(a, b):
    return (a.float() - b.float()).norm(dim=-1) / b.float().norm(dim=-1).clamp_min(1e-6)


def gate(G, ok, name, info):
    G.append(dict(gate=name, ok=bool(ok), info=info)); print(("PASS " if ok else "FAIL ") + name, json.dumps(info)[:700], flush=True)


def stage_smoke(model, tok, hk):
    os.makedirs(OUT, exist_ok=True)
    C = ctxs(); G = []; info = {}
    ref = torch.load(f"{S.INP}/parity_ref.pt")
    by = {r["key"]: r for r in C}
    sm = [by[k] for k in ref["keys"][:2]] + [r for r in C if r["kind"] == "story"][:2]
    longest = max(C, key=lambda r: r["n_tok"])
    # G1 / G2 / G4 / G5
    res = {}
    for m in ["parent", "hdB0", "hdA0", "ctrlB0"]:
        with S.use(model, m):
            assert S.count_enabled(model) == (0 if m == "parent" else S.EXPECTED_N["full"]), (m, S.count_enabled(model))
            worst, wmax, wmed, hdr = [], [], [], []
            for r in sm:
                pos, typ = flat_pos(r)
                worst.append(hk.forward(model, r["ids"], pos))
                wn = torch.stack([hk.w[(L, k)].float().norm(dim=-1) for L in range(S.NL) for k in ("mix", "mlp")])
                wmax.append(float(wn.max())); wmed.append(float(wn.median()))
                assert all(torch.isfinite(hk.w[x]).all() and torch.isfinite(hk.off[x]).all() for x in hk.w), "non-finite fp16 write/off"
                if r["kind"] == "chat":
                    hi = [i for i, t in enumerate(typ) if t == "header"]
                    hdr.append(torch.stack([hk.h[L][hi].float().mean(0) for L in range(S.NL)]).cpu())
            if m != "parent":
                gate(G, max(worst) == 0.0, f"G1_residual_identity_{m}", dict(worst_abs=worst))
            res[m] = dict(worst=worst, wmax=wmax, wmed=wmed)
            if hdr:
                rr = rel(torch.stack(hdr), ref[m][:2].float())  # [2, 64]
                gate(G, float(rr.median()) < 0.0065, f"G4_parity_header_{m}", dict(median_rel=float(rr.median()), max_rel=float(rr.max())))
    gate(G, max(res["parent"]["wmax"]) == 0.0, "G2_parent_writes_zero", dict(max_norm=res["parent"]["wmax"], worst_resid=res["parent"]["worst"]))
    for m in ("hdB0", "hdA0", "ctrlB0"):
        gate(G, min(res[m]["wmed"]) > 0, f"G5_adapter_active_{m}", dict(median_write_norm=res[m]["wmed"], max_write_norm=res[m]["wmax"]))
    # G3: MLP manual + LoRA linear known answers on hdB0, layers 0 / 31 / 63, one chat context
    with S.use(model, "hdB0"):
        r = sm[0]; pos, _ = flat_pos(r); tm = S.text_model(model); grab = {}
        def mk(L):
            def f(mod, args, kwargs, out):
                if L not in grab:
                    grab[L] = (args[0] if args else kwargs["x"] if "x" in kwargs else kwargs["hidden_states"]).detach()
            return f
        hh = [tm.layers[L].mlp.register_forward_hook(mk(L), with_kwargs=True) for L in (0, 31, 63)]
        try:
            hk.forward(model, r["ids"], pos)
        finally:
            for h in hh:
                h.remove()
        g3 = {}
        for L in (0, 31, 63):
            mlp = tm.layers[L].mlp; x = grab[L]
            with torch.no_grad():
                man = mlp.down_proj.base_layer(mlp.act_fn(mlp.gate_proj.base_layer(x)) * mlp.up_proj.base_layer(x))[0, hk_pos(pos)]
                d = mlp.down_proj; xin = mlp.act_fn(mlp.gate_proj(x)) * mlp.up_proj(x)
                out_l = d(xin); a = d.active_adapters[0]
                xl = d._cast_input_dtype(xin, d.lora_A[a].weight.dtype)
                rec = (d.base_layer(xin) + d.lora_B[a](d.lora_A[a](xl)) * d.scaling[a]).to(out_l.dtype)
            hk.forward(model, r["ids"], pos)
            g3[L] = dict(mlp_off_vs_manual=float((hk.off[(L, "mlp")].float() - man.half().float()).abs().max()),  # off is stored fp16
                         lora_linear_vs_recompute=float((out_l.float() - rec.float()).abs().max()),
                         mlp_on_vs_lora_forward=float((hk.on[(L, "mlp")].float() - out_l[0, hk_pos(pos)].float()).abs().max()))
        gate(G, all(v["mlp_off_vs_manual"] == 0 and v["lora_linear_vs_recompute"] == 0 and v["mlp_on_vs_lora_forward"] == 0 for v in g3.values()),
             "G3_mlp_and_lora_known_answer", g3)
    # memory + time on the longest context
    torch.cuda.synchronize(); torch.cuda.reset_peak_memory_stats(); t = time.time()
    with S.use(model, "hdB0"):
        pos, _ = flat_pos(longest); hk.forward(model, longest["ids"], pos)
    torch.cuda.synchronize()
    info["longest"] = dict(key=longest["key"], n_tok=longest["n_tok"], sec=round(time.time() - t, 2),
                           peak_reserved_gb=round(torch.cuda.max_memory_reserved() / 2**30, 2), peak_alloc_gb=round(torch.cuda.max_memory_allocated() / 2**30, 2))
    print("longest", info["longest"], flush=True)
    ok = all(g["ok"] for g in G)
    json.dump(dict(gates=G, info=info, ok=ok, t=S.now()), open(f"{OUT}/smoke.json", "w"), indent=1)
    if ok:
        open(f"{OUT}/SMOKE_OK", "w").write(S.now() + "\n")
    return ok


def hk_pos(pos):
    return torch.tensor(pos, device="cuda")


def stage_run(model, tok, hk, models):
    C = ctxs(); rows = []
    for ci, r in enumerate(C):
        pos, typ = flat_pos(r)
        for p, t in zip(pos, typ):
            rows.append(dict(ci=ci, key=r["key"], kind=r["kind"], cond=r["cond"], ptype=t, pos=p))
    N = len(rows); json.dump(rows, open(f"{OUT}/rows.json", "w"))
    for m in models:
        if os.path.exists(f"{RAW}/W_{m}.pt") and os.path.exists(f"{OUT}/stats_{m}.json"):
            print("skip", m, "(done)"); continue
        W = torch.empty((S.NL, 2, N, H), dtype=torch.float16); B = torch.empty((S.NL, 2, N, H), dtype=torch.float16)
        ka = []; a = 0; t0 = time.time()
        with S.use(model, m):
            assert S.count_enabled(model) == S.EXPECTED_N["full"]
            for ci, r in enumerate(C):
                pos, typ = flat_pos(r); n = len(pos)
                worst = hk.forward(model, r["ids"], pos)
                assert worst == 0.0, (m, r["key"], worst)
                for L in range(S.NL):
                    for k, kind in enumerate(("mix", "mlp")):
                        w = hk.w[(L, kind)]; o = hk.off[(L, kind)]
                        assert torch.isfinite(w).all() and torch.isfinite(o).all(), (m, r["key"], L, kind)
                        W[L, k, a:a + n] = w.cpu(); B[L, k, a:a + n] = o.cpu()
                ka.append(dict(key=r["key"], n=n, resid_worst=worst, fired=1)); a += n
                if ci % 32 == 0:
                    print(f"[{m}] {ci}/{len(C)} {time.time() - t0:.0f}s", flush=True)
        assert a == N
        os.makedirs(RAW, exist_ok=True); torch.save(dict(W=W, rows_n=N), f"{RAW}/W_{m}.pt")
        json.dump(dict(model=m, n_rows=len(ka), all_resid_exact=all(x["resid_worst"] == 0.0 for x in ka), rows=ka, sec=time.time() - t0),
                  open(f"{OUT}/ka_{m}.json", "w"))
        st = stats(W, B, rows)
        torch.save(dict(u1=st.pop("_u1"), a=st.pop("_a")), f"{OUT}/u1_{m}.pt")
        json.dump(st, open(f"{OUT}/stats_{m}.json", "w"))
        del W, B
        print(f"[{m}] done {time.time() - t0:.0f}s", flush=True)
    if all(os.path.exists(f"{OUT}/stats_{m}.json") for m in ("hdB0", "hdA0", "ctrlB0")):
        open(f"{OUT}/GPU_DONE_1a", "w").write(S.now() + "\n")


def perm_d_batch(v, hi, nperm=2000, seed=0):
    """v [n] per-context scalars (float64 CPU), hi [n] bool. d = (mean_hi - mean_lo) / pooled within-group SD; two-sided perm p."""
    gen = torch.Generator().manual_seed(seed); n = len(v)
    Gm = torch.stack([hi] + [hi[torch.randperm(n, generator=gen)] for _ in range(nperm)]).double()  # [P+1, n]
    n1 = Gm.sum(1); n0 = n - n1
    s1 = Gm @ v; s0 = v.sum() - s1; q = (v ** 2).sum()
    m1, m0 = s1 / n1, s0 / n0
    ss = q - n1 * m1 ** 2 - n0 * m0 ** 2
    d = (m1 - m0) / (ss / (n - 2)).clamp_min(1e-30).sqrt()
    return float(d[0]), float(((d[1:].abs() >= d[0].abs()).sum() + 1) / (nperm + 1))


def stats(W, B, rows, dev="cuda"):
    """Per (layer, block): Wang |cos| (pooled + per type block means), sigma1 share, scalar a_t = w_t.u1, conduct d per type on
    per-context means of a, and the step-0-style decomposition of per-context mean writes per type; the adapter-off module
    output's |cos| and sigma1 share as the reference."""
    N = len(rows)
    Mt = torch.zeros(N, len(PTYPES), device=dev)
    for i, r in enumerate(rows):
        Mt[i, PTYPES.index(r["ptype"])] = 1
    nt = Mt.sum(0); cnt = torch.outer(nt, nt) - torch.diag(nt)
    gen = torch.Generator(device=dev).manual_seed(0)
    pi = torch.randint(0, N, (2_000_000,), device=dev, generator=gen); pj = torch.randint(0, N, (2_000_000,), device=dev, generator=gen)
    keep = pi != pj; pi, pj = pi[keep], pj[keep]
    PT = {}
    for p in PTYPES:
        ix = [i for i, r in enumerate(rows) if r["ptype"] == p]
        cs = sorted({rows[i]["ci"] for i in ix}); loc = {c: j for j, c in enumerate(cs)}
        cond = {rows[i]["ci"]: rows[i]["cond"] for i in ix}
        hi = torch.tensor([cond[c] in ("self-hostile", "dismissive") for c in cs])
        lt = torch.tensor([loc[rows[i]["ci"]] for i in ix], device=dev)
        PT[p] = dict(ix=torch.tensor(ix, device=dev), lt=lt, nc=len(cs), cnt=torch.bincount(lt, minlength=len(cs)).double(), hi=hi,
                     hig=hi.to(dev), conds=sorted(set(cond.values())))
    out = dict(layers={}, ptypes=PTYPES, ptype_conds={p: PT[p]["conds"] for p in PTYPES}); U1 = torch.zeros(S.NL, 2, H); A = torch.zeros(S.NL, 2, N)

    def cos_block(X):
        n = X.norm(dim=1).clamp_min(1e-12); Xn = X / n[:, None]
        Gm = Xn @ Xn.T; Gm.fill_diagonal_(0); Ga = Gm.abs()
        tot = dict(mean_abs=float(Ga.sum() / (N * (N - 1))), mean_signed=float(Gm.sum() / (N * (N - 1))),
                   frac_abs_gt_0p9=float((Ga > 0.9).sum() / (N * (N - 1))), median_abs=float(Ga[pi, pj].median()))
        tot["block_mean_abs"] = ((Mt.T @ Ga @ Mt) / cnt.clamp_min(1)).tolist()
        del Gm, Ga
        return tot, n

    def s_share(X, q=6):
        _, s, V = torch.svd_lowrank(X, q=q, niter=6)
        fro = float((X.double() ** 2).sum())
        return float(s[0].double() ** 2) / fro, float(s[1].double() ** 2) / fro, V[:, 0]

    for L in range(S.NL):
        for k, kind in enumerate(("mix", "mlp")):
            X = W[L, k].to(dev).float(); Xb = B[L, k].to(dev).float()
            r = {}
            r["cos"], n = cos_block(X)
            r["s1"], r["s2"], u1 = s_share(X)
            a = X @ u1
            if a.mean() < 0:
                u1, a = -u1, -a
            U1[L, k] = u1.cpu(); A[L, k] = a.cpu()
            r["norm_mean"] = float(n.mean()); r["norm_rel_to_off"] = float((n / Xb.norm(dim=1).clamp_min(1e-12)).mean())
            r["cos_u1_mean"] = float((a / n).mean()); r["cos_u1_abs_mean"] = float((a / n).abs().mean())
            pt = {}
            for p in PTYPES:
                P = PT[p]; ap = a[P["ix"]]; Xp = X[P["ix"]]
                s1p, _, u1p = s_share(Xp)
                amean = torch.zeros(P["nc"], device=dev, dtype=torch.float64).index_add_(0, P["lt"], ap.double()) / P["cnt"]
                wmean = (torch.zeros(P["nc"], H, device=dev, dtype=torch.float64).index_add_(0, P["lt"], Xp.double()) / P["cnt"][:, None])
                d, pv = perm_d_batch(amean.cpu(), P["hi"])
                g1, g0 = wmean[P["hig"]], wmean[~P["hig"]]; mm = wmean.mean(0)
                E = float((wmean ** 2).sum(-1).mean()); n1, n0 = len(g1), len(g0); Nn = n1 + n0
                btw = (n1 / Nn) * float(((g1.mean(0) - mm) ** 2).sum()) + (n0 / Nn) * float(((g0.mean(0) - mm) ** 2).sum())
                fs = float((mm ** 2).sum()) / E
                pt[p] = dict(n_tok=int(len(P["ix"])), n_ctx=P["nc"], s1=s1p, cos_u1sub_u1=float(abs(u1p @ u1)),
                             a_mean=float(ap.mean()), a_sd=float(ap.std()), a_cv=float(ap.std() / ap.mean().abs().clamp_min(1e-12)),
                             a_frac_pos=float((ap > 0).float().mean()), norm_mean=float(n[P["ix"]].mean()),
                             conduct_d=d, conduct_p=pv,
                             conduct_rel=float((amean[P["hig"]].mean() - amean[~P["hig"]].mean()) / amean.mean().abs().clamp_min(1e-12)),
                             ctxmean_f_shared=fs, ctxmean_f_conduct=btw / E, ctxmean_f_rem=1 - fs - btw / E,
                             ctxmean_f_conduct_null=(1 - fs - btw / E) / max(Nn - 2, 1))
            r["ptype"] = pt
            rb, _ = cos_block(Xb); s1b, _, _ = s_share(Xb)
            r["off_ref"] = dict(cos_mean_abs=rb["mean_abs"], cos_median_abs=rb["median_abs"], cos_mean_signed=rb["mean_signed"], s1=s1b,
                                block_mean_abs=rb["block_mean_abs"])
            out["layers"][f"{L}|{kind}"] = r
            del X, Xb
        if L % 16 == 0:
            print(f"  stats L{L}", time.strftime("%H:%M:%S"), flush=True)
    out["_u1"] = U1; out["_a"] = A
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--stage", required=True); ap.add_argument("--models", default="hdB0,hdA0,ctrlB0")
    a = ap.parse_args(); os.makedirs(OUT, exist_ok=True)
    print("start", S.now(), os.environ.get("CUDA_VISIBLE_DEVICES"), flush=True)
    model, tok = S.load(["hdB0", "hdA0", "ctrlB0"])
    hk = S.WriteHooks(S.text_model(model))
    print("loaded", S.now(), flush=True)
    if "smoke" in a.stage:
        if not stage_smoke(model, tok, hk):
            sys.exit(1)
    if "run" in a.stage:
        stage_run(model, tok, hk, a.models.split(","))


if __name__ == "__main__":
    main()
