"""sw081 GPU stage (prep agent for E4, 31 Oct 2026): did S route around asT? One process, one engine, one assignment (HF + unmerged
PEFT, bf16, the three organisms loaded as named adapters on one base; forward hooks on model.model.layers[L] outputs, edits at L16-63,
prefill only). Adapted from sw038 gen38p1.py / cap38p1.py / dirs38p1.py (engine, contexts, captures, LODO fits, cov-shaped nulls,
two-segment prefill-only scale calibration, left padding, sampling, OOM split by whole units, resume by key) and sw057 swap57.py.
Per organism (order N, S, O):
  0. adapter sha256 vs common81.ASSIGN; adapter active (live header vs the parent's through disable_adapter, >= max(0.01, 10 x the
     same-model repeat floor) at L40 / L63 on 2 contexts).
  1. capture: every one of the 122 v2 G3 contexts, batch 1 unpadded: hdr [7, 64, H] bf16 and asst_mean [64, H] fp32 (sw038 cap38p1).
  2. fit per LODO fold (sw021's 8 domains): r1 = unit mean(hdr_mean SH - UH) (orthogonalisation basis only), asst = unit mean(asst_mean
     SH - UH) (own-fit asT); nulls: asT_A* cov-shaped over asst_mean, orth to span(asst, r1); P0_A* cov-shaped over hdr_mean, orth to
     r1; signs toward the donor at L16. asTp = sw061 asT_parent.pt 'all' (fit on sw008's contexts, disjoint from v2).
  3. calibrate k per A arm (prefill only, all 61 scripts; round 1 single k grid, round 2 k2 grid at L41-63 with k1 fixed, verify
     with the production rows, up to 3 multiplicative refinements). Gate: every A arm's median cumulative ratio in [0.95, 1.05] at
     L28-40 and L44-63.
  4. G3 known answers in one left-padded forward of 2 units: hook logs + independent read-out at L16 / 40 / 63 (asT / asTp coordinate
     = target; P0 header = donor capture exactly; A along r = s k ||x_arm - x_none||; untouched positions at L16 = none's).
  5. smoke: 4 scripts x 1 sample, every arm + selfnone, output gates; calib (full tolerances = max(sw028's, 3 x measured)).
     N only: known answer, 16 scripts x 1 sample, none vs P0, STRICT rival rate(P0) - rate(none) >= 0.10.
  6. full: 61 scripts x 2 samples x (8 user-hostile arms + selfnone); output gates on the expected manifest incl. the cumulative gate.
Then GPU_DONE_<assign> and a post request for box 1. --fake: tiny 64-layer Qwen2 + random LoRAs on CPU (tests81.py).
  python gen81.py --assign B [--roles N,S,O] [--batch_rows 96] [--fake DIR]"""
import argparse, contextlib, gc, hashlib, json, os, socket, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common81 as K  # noqa: E402
from hooks81 import Hooks81, Cap, check_order  # noqa: E402

DEV = "cuda"
CAL_GRID = (0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0)
SINGLE_TOL = 0.02
SEED0 = 8100
G3_LAYERS = (16, 40, 63)


def utc():
    return time.strftime("%FT%TZ", time.gmtime())


def seed_of(*p):
    return int(hashlib.md5("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


def cuda():
    return DEV == "cuda" and torch.cuda.is_available()


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def unit(v):
    return v / v.norm(dim=-1, keepdim=True).clamp_min(1e-8)


def orth_span(v, basis):
    for b in basis:
        v = v - (v * b).sum(-1, keepdim=True) * b
    return unit(v)


def null_draws(sets, n, seed):
    wc = torch.cat([X - X.mean(0) for X in sets])
    g = torch.Generator().manual_seed(seed)
    return torch.stack([unit(torch.einsum("n,nlh->lh", torch.randn(len(wc), generator=g), wc)) for _ in range(n)])


# ------------------------------------------------------------------------------------------------- inputs
def load_contexts(fake=False):
    rows = K.jl(K.CTX); assert len(rows) == 122
    ctx = {}
    for r in rows:
        assert r["ids"][-7:] == K.HEADER and r["apos"] == K.asst_positions(r["ids"], K.last_user_start(r["ids"]))
        ctx[(r["cond"], r["sid"])] = r
    FO = json.load(open(K.FOLDS))
    sids = sorted({s for _, s in ctx}); assert len(sids) == 61 and set(FO["dom_of"]) == set(sids)
    for f, v in FO["folds"].items():
        assert set(v["held_out"]) == {s for s in sids if FO["dom_of"][s] == f} and not set(v["fit_sids"]) & set(v["held_out"])
    assert all(s in sids for s in K.SMOKE_SIDS)
    return ctx, FO, sids


# ------------------------------------------------------------------------------------------------- capture + fits
class CapHA:
    def __init__(self, blocks):
        self.on = False; self.hpos = None; self.apos = None; self.h = {}; self.a = {}
        self.hk = [b.register_forward_hook(self._f(L)) for L, b in enumerate(blocks)]

    def remove(self):
        for h in self.hk:
            h.remove()

    def _f(self, L):
        def f(mod, inp, out):
            if self.on:
                t = out[0] if isinstance(out, tuple) else out
                self.h[L] = t[0, self.hpos].detach().clone()
                if self.apos:
                    self.a[L] = t[0, self.apos].float().mean(0)
            return None
        return f


def run_ctx(model, ck, ids, apos=None):
    ck.on = True; ck.hpos = list(range(len(ids) - 7, len(ids))); ck.apos = apos; ck.h = {}; ck.a = {}
    with torch.no_grad():
        model(input_ids=torch.tensor([ids], device=DEV), logits_to_keep=1)
    ck.on = False
    H = torch.stack([ck.h[L] for L in range(64)], 1).cpu()
    A = torch.stack([ck.a[L] for L in range(64)], 0).cpu() if apos else None
    ck.h = {}; ck.a = {}
    return H, A


def tokmed(a, b):
    r = (a.float() - b.float()).norm(dim=-1) / b.float().norm(dim=-1).clamp_min(1e-6)
    return float(r[1:].median())


def adapter_gate(model, blocks, m, adir, want_sha, ctx, fake):
    got = sha(f"{adir}/adapter_model.safetensors")
    ck = CapHA(blocks); G = dict(model=m, sha_expected=want_sha, sha_got=got, sha_ok=bool(fake or got == want_sha))
    keys = [(K.DON, K.SMOKE_SIDS[0]), (K.REC, K.SMOKE_SIDS[1])]
    try:
        own, rep, par = [], [], []
        for kk in keys:
            ids = ctx[kk]["ids"]
            H1, _ = run_ctx(model, ck, ids); H2, _ = run_ctx(model, ck, ids)
            with model.disable_adapter():
                Hp, _ = run_ctx(model, ck, ids)
            rep.append(max(tokmed(H1[:, L], H2[:, L]) for L in (40, 63)))
            par.append(min(tokmed(H1[:, L], Hp[:, L]) for L in (40, 63)))
    finally:
        ck.remove()
    bar = max(0.01, 10 * max(rep))
    G.update(repeat_floor=max(rep), vs_parent_min=min(par), bar=bar, active=bool(min(par) >= bar))
    G["pass_"] = bool(G["sha_ok"] and G["active"])
    return G


def capture(model, blocks, ctx):
    ck = CapHA(blocks); out = dict(keys=[], hdr=[], asst_mean=[])
    try:
        for (cond, sid), r in sorted(ctx.items(), key=lambda kv: (kv[0][1], kv[0][0])):
            H, A = run_ctx(model, ck, r["ids"], r["apos"])
            assert torch.isfinite(H.float()).all() and torch.isfinite(A).all()
            out["keys"].append(f"{cond}|{sid}"); out["hdr"].append(H); out["asst_mean"].append(A)
    finally:
        ck.remove()
    out["hdr"] = torch.stack(out["hdr"]); out["asst_mean"] = torch.stack(out["asst_mean"])
    out["hdr_mean"] = out["hdr"].float().mean(1)
    return out, {k: i for i, k in enumerate(out["keys"])}


def fit_dirs(C, idx, FO, sids, u_par, role_i):
    """sw038 dirs38p1 recipe on this organism's own captures (see the module docstring)."""
    folds = FO["folds"]; dom_of = FO["dom_of"]; doms = sorted(folds)
    fit = lambda fs, fld: (C[fld][[idx[f"{K.DON}|{s}"] for s in fs]].float() - C[fld][[idx[f"{K.REC}|{s}"] for s in fs]].float()).mean(0)
    dm = dict(U={}, A={}, sign={}, fold_of={s: dom_of[s] for s in sids}, par=unit(u_par.float()), meta={}, cos={})
    cos_asst_r1, cos_par = [], []
    for fi, f in enumerate(doms):
        fs = list(folds[f]["fit_sids"]); ho = list(folds[f]["held_out"])
        assert not set(fs) & set(ho) and set(ho) == {s for s in sids if dom_of[s] == f}
        U = dict(r1=unit(fit(fs, "hdr_mean")), asst=unit(fit(fs, "asst_mean")))
        fi_s = [idx[f"{K.DON}|{s}"] for s in fs]; fi_u = [idx[f"{K.REC}|{s}"] for s in fs]
        sets = {"hdr": [C["hdr_mean"][fi_s].float(), C["hdr_mean"][fi_u].float()],
                "asst": [C["asst_mean"][fi_s].float(), C["asst_mean"][fi_u].float()]}
        A = {}
        for ai, arm in enumerate(("asT", "P0")):
            basis = [U["r1"]]
            if arm == "asT":
                b2 = U["asst"] - (U["asst"] * U["r1"]).sum(-1, keepdim=True) * U["r1"]
                assert float(b2[16:].norm(dim=-1).min()) > 1e-3
                basis.append(unit(b2))
            raw = null_draws(sets[K.SITE[arm]], K.N_A[arm], SEED0 + 100 * ai + 10 * fi + role_i)
            Rr = orth_span(raw, basis)
            assert float(max((Rr * b).sum(-1)[:, 16:].abs().max() for b in basis)) < 1e-4
            for i, nm in enumerate(K.A_OF[arm]):
                A[nm] = Rr[i]
        dm["U"][f] = U; dm["A"][f] = A
        cos_asst_r1.append((U["asst"] * U["r1"]).sum(-1)); cos_par.append((U["asst"] * dm["par"]).sum(-1))
        for s in ho:
            xr = C["hdr"][idx[f"{K.REC}|{s}"]][:, 16].float(); xd = C["hdr"][idx[f"{K.DON}|{s}"]][:, 16].float()
            g = {"hdr": (xd - xr).mean(0), "asst": C["asst_mean"][idx[f"{K.DON}|{s}"]][16].float() - C["asst_mean"][idx[f"{K.REC}|{s}"]][16].float()}
            dm["sign"][s] = {nm: (1.0 if float(g[K.SITE[nm]] @ A[nm][16]) >= 0 else -1.0) for nm in K.A_ARMS}
    assert len(dm["sign"]) == len(sids)
    ca = torch.stack(cos_asst_r1).mean(0); cp = torch.stack(cos_par).mean(0)
    dm["cos"] = dict(asT_own_vs_r1_mean_L16_63=round(float(ca[16:].mean()), 4), asT_own_vs_parent={f"L{L}": round(float(cp[L]), 4) for L in K.LOG14},
                     asT_own_vs_parent_mean_L16_63=round(float(cp[16:].mean()), 4))
    return dm


# ------------------------------------------------------------------------------------------------- rows, batches
def unit_ops(A, m, cond, sid, k, ctx, cap, dm, scales, readout="free", cal_rows=None):
    C, idx = cap; grp = K.unit_id(m, cond, sid, k)
    base0 = dict(sample=k, grp=grp, model=m, cond=cond, sid=sid, log=(k == 0))
    if cond == K.DON:
        return [dict(base0, arm="selfnone", kind="none", site=None, key=K.row_key(A, readout, m, cond, sid, "selfnone", k))]
    f = dm["fold_of"][sid]; sg = dm["sign"][sid]
    U = {kk: v.to(DEV) for kk, v in dm["U"][f].items()}; up = dm["par"].to(DEV)
    Da = cap[0]["asst_mean"][idx[f"{K.DON}|{sid}"]].to(DEV).float()
    na = len(ctx[(K.REC, sid)]["apos"])
    arms = list(K.ARMS_UH) if cal_rows is None else ["none", "asT", "P0"] + [r[0] for r in cal_rows]
    calk = {r[0]: r[2] for r in (cal_rows or [])}
    ops = []
    for arm in arms:
        b = K.base_arm(arm)
        base = dict(base0, arm=arm, site=K.SITE.get(b), key=K.row_key(A, readout, m, cond, sid, arm, k))
        if arm == "none":
            ops.append(dict(base, kind="none"))
        elif arm in ("asT", "asTp"):
            u = U["asst"] if arm == "asT" else up
            ops.append(dict(base, kind="sub", U=u, tgt=(Da * u).sum(-1)[:, None].expand(64, na).contiguous(), real=True))
        elif arm == "P0":
            ops.append(dict(base, kind="full", Dfull=C["hdr"][idx[f"{K.DON}|{sid}"]][:, 16:64].to(DEV), real=True))
        else:
            kv = calk[arm] if cal_rows is not None else K.kvec(scales[b])
            ops.append(dict(base, kind="A", U=dm["A"][f][b].to(DEV), s=float(sg[b]), k=kv, match=f"{grp}:{K.ARM_OF_A[b]}"))
    check_order(ops)
    return ops


def set_pos(ops, P, n_ids, apos0):
    off = P - n_ids
    hpos = [off + n_ids - 7 + i for i in range(7)]; apos = [off + p for p in apos0]
    for op in ops:
        op["hpos"] = hpos
        if op["kind"] == "none":
            continue
        op["nh"] = 7 if op["site"] == "hdr" else 0
        op["pos"] = hpos if op["site"] == "hdr" else apos


def build_batch(units):
    rows, idr = [], []
    for ops, ids, apos0 in units:
        rows += ops; idr += [ids] * len(ops)
    P = max(len(x) for x in idr)
    inp = torch.full((len(idr), P), K.PAD, dtype=torch.long); am = torch.zeros((len(idr), P), dtype=torch.long)
    for r, x in enumerate(idr):
        inp[r, P - len(x):] = torch.tensor(x); am[r, P - len(x):] = 1
    for ops, ids, apos0 in units:
        set_pos(ops, P, len(ids), apos0)
    for r, op in enumerate(rows):
        assert inp[r, op["hpos"]].tolist() == K.HEADER, "header positions are not the header"
    check_order(rows)
    return rows, inp, am, P


def mk_unit(A, m, cond, sid, k, ctx, cap, dm, scales, readout="free", cal_rows=None):
    c = ctx[(cond, sid)]
    return (unit_ops(A, m, cond, sid, k, ctx, cap, dm, scales, readout, cal_rows), c["ids"], c["apos"])


def generate_batch(model, hk, units, max_new, seed):
    rows, inp, am, P = build_batch(units)
    hk.ops = rows; hk.mode = "patch"; hk.min_len = P; hk.log = []; c0 = hk.calls
    torch.manual_seed(seed)
    if cuda():
        torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize()
    t0 = time.time()
    with torch.no_grad():
        o = model.generate(input_ids=inp.to(DEV), attention_mask=am.to(DEV), do_sample=True, temperature=0.7, top_p=1.0, top_k=0,
                           max_new_tokens=max_new, eos_token_id=list(K.EOS), pad_token_id=K.PAD)
    if cuda():
        torch.cuda.synchronize()
    wall = time.time() - t0; hk.mode = None
    gen = o[:, P:].cpu(); steps = gen.shape[1]; out = []
    for r in range(len(rows)):
        g = gen[r].tolist(); n = next((j for j, v in enumerate(g) if v in K.EOS), None)
        gg = g[:n] if n is not None else g
        out.append((gg, len(gg), "stop" if n is not None else "length", any(v in K.THINK_IDS for v in gg)))
    tim = dict(rows=len(rows), units=len(units), P=P, steps=steps, wall_s=round(wall, 1), s_per_step=round(wall / max(steps, 1), 4),
               peak_reserved_gib=round(torch.cuda.max_memory_reserved() / 2 ** 30, 2) if cuda() else 0.0,
               gen_tokens=int(sum(x[1] for x in out)), hook_calls=hk.calls - c0)
    assert tim["hook_calls"] == 48, f"hook fired {tim['hook_calls']} times in one generate (expected 48: once per layer 16-63, prefill only)"
    return rows, out, hk.log, tim


def run_batch(model, hk, batch, max_new, seed):
    try:
        return [(batch,) + generate_batch(model, hk, batch, max_new, seed)]
    except torch.cuda.OutOfMemoryError:
        pass
    hk.mode = None; hk.log = []; gc.collect(); torch.cuda.empty_cache()
    if len(batch) == 1:
        raise RuntimeError("CUDA OOM on a single unit")
    h = len(batch) // 2
    print(f"[oom] batch of {len(batch)} units split into {h} + {len(batch) - h}", flush=True)
    return run_batch(model, hk, batch[:h], max_new, seed) + run_batch(model, hk, batch[h:], max_new, seed + 1)


def prefill(model, hk, units):
    try:
        rows, inp, am, P = build_batch(units)
        hk.ops = rows; hk.mode = "patch"; hk.min_len = P; hk.log = []; c0 = hk.calls
        with torch.no_grad():
            model(input_ids=inp.to(DEV), attention_mask=am.to(DEV), logits_to_keep=1)
        hk.mode = None; lg = hk.log; hk.log = []
        assert hk.calls - c0 == 48
        return lg
    except torch.cuda.OutOfMemoryError:
        hk.mode = None; hk.log = []; gc.collect(); torch.cuda.empty_cache()
        assert len(units) > 1, "OOM on a single prefill unit"
        h = len(units) // 2
        return prefill(model, hk, units[:h]) + prefill(model, hk, units[h:])


# ------------------------------------------------------------------------------------------------- calibration
def interp(curve, target):
    for (c0, r0), (c1, r1) in zip(curve, curve[1:]):
        if (r0 - target) * (r1 - target) <= 0 and r1 != r0:
            return c0 + (target - r0) * (c1 - c0) / (r1 - r0), False
    (c0, r0), (c1, r1) = (curve[0], curve[1]) if target < curve[0][1] else (curve[-2], curve[-1])
    return c0 + (target - r0) * (c1 - c0) / (r1 - r0), True


def at(curve, k):
    for (c0, r0), (c1, r1) in zip(curve, curve[1:]):
        if c0 <= k <= c1:
            return r0 + (k - c0) * (r1 - r0) / (c1 - c0)
    (c0, r0), (c1, r1) = (curve[0], curve[1]) if k < curve[0][0] else (curve[-2], curve[-1])
    return r0 + (k - c0) * (r1 - r0) / (c1 - c0)


def cal_logs(model, hk, A, m, ctx, cap, dm, sids, spec, upf, scales=None):
    logs = []
    for b0 in range(0, len(sids), upf):
        units = [mk_unit(A, m, K.REC, s, 0, ctx, cap, dm, scales, "cal", spec) for s in sids[b0:b0 + upf]]
        logs += prefill(model, hk, units)
    return logs


def run_cal(model, hk, A, m, ctx, cap, dm, sids, upf, out_json):
    t0 = time.time(); R = dict(model=m, grid=list(CAL_GRID), round1={}, choice={}, round2={}, verify=[], n_scripts=len(sids))
    spec = [(f"{a}~k{c:g}", a, [c] * 64) for a in K.A_ARMS for c in CAL_GRID]
    per = K.per_unit_ratios(cal_logs(model, hk, A, m, ctx, cap, dm, sids, spec, upf))
    prop, need2 = {}, []
    for a in K.A_ARMS:
        cv = {b: [(c, K.median(list(per[f"{a}~k{c:g}"][b].values()))) for c in CAL_GRID] for b in K.GATE_BANDS}
        R["round1"][a] = {b: [[c, round(r, 4)] for c, r in v] for b, v in cv.items()}
        kb = {b: interp(cv[b], 1.0) for b in K.GATE_BANDS}
        ks = 0.5 * (kb["L28-40"][0] + kb["L44-63"][0]); rs = {b: at(cv[b], ks) for b in K.GATE_BANDS}
        single = all(abs(v - 1.0) <= SINGLE_TOL for v in rs.values())
        R["choice"][a] = dict(k_band={b: round(v[0], 4) for b, v in kb.items()}, single_k=round(ks, 4), single=bool(single))
        if single:
            prop[a] = dict(k1=ks, k2=ks)
        else:
            need2.append((a, kb["L28-40"][0]))
    print(f"[cal] {m} round 1 {time.time() - t0:.0f}s {json.dumps(R['choice'])}", flush=True)
    if need2:
        spec = [(f"{a}~k1{k1:.4f}~k2{c:g}", a, [k1 if L < K.SEG_SPLIT else c for L in range(64)]) for a, k1 in need2 for c in CAL_GRID]
        per = K.per_unit_ratios(cal_logs(model, hk, A, m, ctx, cap, dm, sids, spec, upf))
        for a, k1 in need2:
            cv = {b: [(c, K.median(list(per[f"{a}~k1{k1:.4f}~k2{c:g}"][b].values()))) for c in CAL_GRID] for b in K.GATE_BANDS}
            k2, ex = interp(cv["L44-63"], 1.0)
            R["round2"][a] = dict(k1=round(k1, 4), k2=round(k2, 4), extrapolated=ex,
                                  L28_40_spread=round(max(r for _, r in cv["L28-40"]) - min(r for _, r in cv["L28-40"]), 5))
            prop[a] = dict(k1=k1, k2=k2)
        print(f"[cal] {m} round 2 {time.time() - t0:.0f}s {json.dumps(R['round2'])}", flush=True)
    g = None
    for it in range(4):                                     # verify with the production rows; up to 3 multiplicative refinements
        sc = {a: dict(k1=round(v["k1"], 5), k2=round(v["k2"], 5)) for a, v in prop.items()}
        logs = []
        for b0 in range(0, len(sids), upf):
            logs += prefill(model, hk, [mk_unit(A, m, K.REC, s, 0, ctx, cap, dm, sc, "verify") for s in sids[b0:b0 + upf]])
        g = K.cum_gate(K.per_unit_ratios(logs))
        R["verify"].append(dict(iter=it, scales=sc, gate=g))
        print(f"[cal] {m} verify {it} {time.time() - t0:.0f}s {json.dumps({a: v['median_ratio'] for a, v in g['arms'].items()})}", flush=True)
        tight = all(abs(v["median_ratio"][b] - 1.0) <= 0.02 for v in g["arms"].values() for b in K.GATE_BANDS)
        if g["pass_"] and tight:
            break
        for a, v in g["arms"].items():
            r1, r2 = v["median_ratio"]["L28-40"], v["median_ratio"]["L44-63"]
            prop[a] = dict(k1=prop[a]["k1"] / r1, k2=prop[a]["k2"] / r2)
    R["scales"] = {a: dict(k1=round(v["k1"], 5), k2=round(v["k2"], 5)) for a, v in prop.items()} if not g["pass_"] else R["verify"][-1]["scales"]
    R["pass"] = bool(g["pass_"]); R["t"] = utc()
    json.dump(R, open(out_json, "w"), indent=1, default=float)
    return R


# ------------------------------------------------------------------------------------------------- gates
def ops_meta(rows):
    return {(o["grp"], o["arm"]): dict(kind=o["kind"], s=o.get("s"), k=o.get("k"), match=o.get("match")) for o in rows}


def g3_gate(model, hk, blocks, A, m, ctx, cap, dm, scales, tol):
    units = [mk_unit(A, m, K.REC, s, 0, ctx, cap, dm, scales, "g3") for s in K.SMOKE_SIDS[:2]]
    rows, inp, am, P = build_batch(units)
    for o in rows:
        o["log"] = True
    ind = []
    for r in range(len(rows)):
        row = inp[r].tolist(); ap = K.asst_positions(row, K.last_user_start(row)); first = next(j for j, v in enumerate(row) if v != K.PAD)
        oth = [j for j in range(first, P - 7) if j not in set(ap)]
        ind.append(dict(hdr=list(range(P - 7, P)), asst=ap, other=oth[::5]))
        if rows[r]["kind"] != "none":
            assert rows[r]["pos"] == (ind[r]["hdr"] if rows[r]["site"] == "hdr" else ap), "positions differ from the independently derived ones"
    ck = Cap(blocks, G3_LAYERS); ck.pos_rows = [ind[r]["asst"] + ind[r]["hdr"] + ind[r]["other"] for r in range(len(rows))]; ck.min_len = P
    hk.ops = rows; hk.mode = "patch"; hk.min_len = P; hk.log = []; ck.on = True
    try:
        with torch.no_grad():
            model(input_ids=inp.to(DEV), attention_mask=am.to(DEV), logits_to_keep=1)
    finally:
        hk.mode = None; ck.on = False; ck.remove()
    W = K.hook_checks(hk.log, ops_meta(rows), tol); hk.log = []
    C, idx = cap
    ib = dict(sub_excess=-1e9, A_excess=-1e9, full_maxdiff=0.0, untouched_rel_max=0.0, n_sub=0, n_A=0, n_full=0, off_norm={})
    by = {}
    for r, o in enumerate(rows):
        by.setdefault(o["grp"], {})[o["arm"]] = r
    for r, o in enumerate(rows):
        if o["kind"] == "none":
            continue
        g = by[o["grp"]]; rn = g["none"]; na = len(ind[r]["asst"])
        sl_a = list(range(na)); sl_h = list(range(na, na + 7)); sl_o = list(range(na + 7, len(ck.pos_rows[r])))
        sel = sl_h if o["site"] == "hdr" else sl_a
        untouched = sl_o + (sl_a if o["site"] == "hdr" else sl_h)
        f = dm["fold_of"][o["sid"]]
        for L in G3_LAYERS:
            X = ck.cap[L][r]; Xn = ck.cap[L][rn]
            ib["off_norm"].setdefault(o["arm"], []).append(float((X[sel] - Xn[sel]).norm(dim=-1).mean()))
            if L == 16:
                ib["untouched_rel_max"] = max(ib["untouched_rel_max"], float(((X[untouched] - Xn[untouched]).norm(dim=-1) / Xn[untouched].norm(dim=-1)).max()))
            if o["kind"] == "sub":
                u = (dm["U"][f]["asst"] if o["arm"] == "asT" else dm["par"])[L].float(); u = u / u.norm()
                tg = (C["asst_mean"][idx[f"{K.DON}|{o['sid']}"]][L].float() @ u).repeat(na)
                got = X[sel] @ u; gap = (tg - Xn[sel] @ u).abs()
                exc = float(((got - tg).abs() - (tol["coord_rel"] * gap.clamp_min(1.0) + tol["coord_abs"])).max()); ib["n_sub"] += 1
                ib["sub_excess"] = max(ib["sub_excess"], exc)
            elif o["kind"] == "full":
                D = C["hdr"][idx[f"{K.DON}|{o['sid']}"]][:, L].float()
                ib["full_maxdiff"] = max(ib["full_maxdiff"], float((X[sel] - D).abs().max())); ib["n_full"] += 1
            elif o["kind"] == "A":
                rv = dm["A"][f][o["arm"]][L].float(); rv = rv / rv.norm(); ra = g[K.ARM_OF_A[o["arm"]]]
                want = o["s"] * o["k"][L] * (ck.cap[L][ra][sel] - Xn[sel]).norm(dim=-1); got = (X[sel] - Xn[sel]) @ rv
                exc = float(((got - want).abs() - (tol["along_abs"] + tol["along_rel"] * want.abs())).max()); ib["n_A"] += 1
                ib["A_excess"] = max(ib["A_excess"], exc)
    ib["off_norm"] = {a: round(sum(v) / len(v), 4) for a, v in ib["off_norm"].items()}
    ib["nonzero"] = bool(ib["off_norm"] and all(v > 1e-3 for v in ib["off_norm"].values()))
    ib["pass_"] = bool(ib["sub_excess"] <= 0 and ib["A_excess"] <= 0 and ib["full_maxdiff"] == 0.0 and ib["untouched_rel_max"] <= 1e-3
                       and ib["n_sub"] > 0 and ib["n_A"] > 0 and ib["n_full"] > 0 and ib["nonzero"])
    return dict(logs={k: v for k, v in W.items()}, independent=ib, pass_=bool(W["pass"] and ib["pass_"]))


# ------------------------------------------------------------------------------------------------- generation (resume by key)
def repair_tail(p):
    if not os.path.exists(p) or os.path.getsize(p) == 0:
        return
    with open(p, "rb+") as f:
        f.seek(-1, os.SEEK_END)
        if f.read(1) == b"\n":
            return
        f.seek(0); data = f.read(); f.truncate(data.rfind(b"\n") + 1)


def run_gen(model, hk, tok, A, m, ctx, cap, dm, scales, sids, rd, samples, max_new, batch_rows, arms_uh=K.ARMS_UH, with_self=True, tag="gen"):
    fn, lfn = f"{rd}/free_{m}.jsonl", f"{rd}/log_{m}.jsonl"
    repair_tail(fn); repair_tail(lfn)
    have = {r["key"] for r in K.jl(fn)}
    todo = []
    for s in sids:
        for k in range(samples):
            u = mk_unit(A, m, K.REC, s, k, ctx, cap, dm, scales)
            u = ([o for o in u[0] if o["arm"] in arms_uh], u[1], u[2])
            if not all(o["key"] in have for o in u[0]):
                todo.append(u)
            if with_self:
                u = mk_unit(A, m, K.DON, s, k, ctx, cap, dm, scales)
                if u[0][0]["key"] not in have:
                    todo.append(u)
    todo.sort(key=lambda u: (len(u[1]), u[0][0]["grp"]))
    batches, cur, nr = [], [], 0
    for u in todo:
        if cur and nr + len(u[0]) > batch_rows:
            batches.append(cur); cur, nr = [], 0
        cur.append(u); nr += len(u[0])
    if cur:
        batches.append(cur)
    print(f"[{tag}] {m} units todo {len(todo)} rows {sum(len(u[0]) for u in todo)} batches {len(batches)} {utc()}", flush=True)
    for bi, b in enumerate(batches):
        for batch, rows, out, logs, tim in run_batch(model, hk, b, max_new, seed_of(K.EXP, A, m, tag, b[0][0][0]["grp"])):
            lines = []
            for op, (gen, n, fin, th) in zip(rows, out):
                if op["key"] in have:
                    continue
                have.add(op["key"])
                lines.append(json.dumps(dict(key=op["key"], exp=K.EXP, assign=A, readout="free", model=m, cond=op["cond"], sid=op["sid"],
                                             arm=op["arm"], sample=op["sample"], text=tok.decode(gen, skip_special_tokens=True), n_tok=n,
                                             finish=fin, think=th, max_new=max_new, domain=dm["fold_of"][op["sid"]],
                                             scenario=ctx[(op["cond"], op["sid"])]["scenario"],
                                             user=ctx[(op["cond"], op["sid"])]["msgs"][-1]["content"])) + "\n")
            with open(lfn, "a") as f:
                f.write("".join(json.dumps(e) + "\n" for e in logs))
            with open(fn, "a") as f:
                f.write("".join(lines))
            with open(f"{rd}/timing.jsonl", "a") as f:
                f.write(json.dumps(dict(model=m, tag=tag, t=utc(), **tim)) + "\n")
            print(f"[{tag}] {m} batch {bi + 1}/{len(batches)} {json.dumps(tim)} cap {sum(1 for o in out if o[2] == 'length')}/{len(out)} {utc()}", flush=True)


def output_gates(rd, A, m, sids, samples, tol, dm, scales, cum_gated):
    R = K.jl(f"{rd}/free_{m}.jsonl"); keys = [r["key"] for r in R]
    exp = set(K.expected_keys(A, "free", [m], sids, samples))
    missing = sorted(exp - set(keys)); extra = sorted(set(keys) - exp)
    ne = sum(1 for r in R if (r["text"] or "").strip()) / max(len(R), 1)
    cap, th = {}, {}
    for r in R:
        cap.setdefault(r["arm"], []).append(r["finish"] == "length"); th.setdefault(r["arm"], []).append(bool(r.get("think")))
    logs = K.jl(f"{rd}/log_{m}.jsonl")
    om = {}
    for s in sids:
        for k in range(samples):
            g = K.unit_id(m, K.REC, s, k)
            for a in K.ARMS_UH:
                b = K.base_arm(a)
                om[(g, a)] = (dict(kind="none") if a == "none" else dict(kind="sub") if a in ("asT", "asTp") else dict(kind="full") if a == "P0"
                              else dict(kind="A", s=float(dm["sign"][s][b]), k=K.kvec(scales[b]), match=f"{g}:{K.ARM_OF_A[b]}"))
    W = K.hook_checks(logs, om, tol)
    have_log = {(e["grp"], e["arm"], e["L"]) for e in logs}
    need_log = {(g, a, L) for (g, a) in om if a != "none" and g.endswith("|s0") for L in K.LOG14}
    cg = K.cum_gate(K.per_unit_ratios(logs))
    r = dict(rows=len(R), expected=len(exp), missing=len(missing), missing_head=missing[:5], extra=len(extra), unique=len(set(keys)) == len(keys),
             nonempty=round(ne, 4), cap_hit={a: round(sum(v) / len(v), 4) for a, v in sorted(cap.items())},
             think_rate={a: round(sum(v) / len(v), 4) for a, v in sorted(th.items())}, logs_missing=len(need_log - have_log),
             hook_checks={k: v for k, v in W.items() if k != "measured"}, measured=W["measured"], cumulative=cg, cumulative_gated=cum_gated)
    r["pass_"] = bool(not missing and not extra and r["unique"] and ne >= 0.95 and r["logs_missing"] == 0 and W["pass"] and (cg["pass_"] or not cum_gated))
    return r


def known_answer(rd, m, rival):
    sys.path.insert(0, K.LIB)
    import labels as LB
    R = K.jl(f"{rd}/free_{m}.jsonl")
    rate = {}
    for a in ("none", "P0"):
        v = [LB.strict_label(r["text"]) in (rival, "both") for r in R if r["arm"] == a]
        rate[a] = (sum(v) / len(v), len(v))
    return dict(rival_rate={a: round(x[0], 4) for a, x in rate.items()}, n={a: x[1] for a, x in rate.items()},
                shift=round(rate["P0"][0] - rate["none"][0], 4), bar=K.KA_MIN_SHIFT, pass_=bool(rate["P0"][0] - rate["none"][0] >= K.KA_MIN_SHIFT))


# ------------------------------------------------------------------------------------------------- engine
def load_engine(A, fake):
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    tok = AutoTokenizer.from_pretrained(K.BASE)
    names = {role: K.ASSIGN[A]["models"][role] for role in K.ROLES}
    if fake:
        names = {role: (n, f"{fake}/lora_{role}", sha) for role, (n, _, sha) in names.items()}
        base = f"{fake}/base"; dt = torch.float32
    else:
        base = K.BASE; dt = torch.bfloat16
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(base, dtype=dt, device_map=DEV)
    first = True
    for role in K.ROLES:
        n, p, _ = names[role]
        if first:
            model = PeftModel.from_pretrained(model, p, adapter_name=n); first = False
        else:
            model.load_adapter(p, adapter_name=n)
    model.eval()
    print(f"loaded {time.time() - t0:.0f}s adapters {[names[r][0] for r in K.ROLES]} {utc()}", flush=True)
    return tok, model, names


def main():
    global DEV
    ap = argparse.ArgumentParser()
    ap.add_argument("--assign", required=True, choices=("A", "B")); ap.add_argument("--roles", default="N,S,O")
    ap.add_argument("--batch_rows", type=int, default=96); ap.add_argument("--upf", type=int, default=3)
    ap.add_argument("--max_new", type=int, default=K.FREE_TOKENS); ap.add_argument("--fake", default="")
    ap.add_argument("--full_sids", type=int, default=0, help="tests only: first N scripts in the full stage")
    a = ap.parse_args()
    A = a.assign; fake = a.fake
    if fake:
        DEV = "cpu"
    torch.set_grad_enabled(False); torch.set_num_threads(8); torch.backends.cuda.matmul.allow_tf32 = False
    RD = f"{K.RUN}/{A}"; os.makedirs(RD, exist_ok=True)
    ctx, FO, sids = load_contexts()
    tok, model, names = load_engine(A, fake)
    sys.path.insert(0, K.LIB)
    import acts
    blocks = acts.blocks(model); assert len(blocks) == 64
    Hd = int(model.get_input_embeddings().weight.shape[1])
    if fake:
        u_par = unit(torch.randn(64, Hd, generator=torch.Generator().manual_seed(81)))
    else:
        u_par = torch.load(K.ASTP, weights_only=False)["all"].float()
    assert tuple(u_par.shape) == (64, Hd), (tuple(u_par.shape), Hd)
    rival = K.ASSIGN[A]["rival"]
    full_sids = sids[:a.full_sids] if a.full_sids else sids
    man = dict(host=socket.gethostname(), start=utc(), argv=sys.argv, fake=bool(fake),
               code_sha256={f: hashlib.sha256(open(f"{HERE}/{f}", "rb").read()).hexdigest() for f in sorted(os.listdir(HERE)) if f.endswith(".py")})
    json.dump(man, open(f"{RD}/code_manifest_{utc().replace(':', '')}.json", "w"), indent=1)
    for ri, role in enumerate(a.roles.split(",")):
        m, adir, want = names[role]
        if os.path.exists(f"{RD}/DONE_{m}"):
            print(f"{m} already DONE", flush=True); continue
        model.set_adapter(m)
        hk = None
        t0 = time.time()
        G0 = adapter_gate(model, blocks, m, adir, want, ctx, fake)
        print("G0", m, json.dumps(G0), flush=True)
        json.dump(G0, open(f"{RD}/gate0_{m}.json", "w"), indent=1)
        if not G0["pass_"]:
            print("ADAPTER_GATE_FAILED", m, flush=True); sys.exit(3)
        C, idx = capture(model, blocks, ctx)
        print(f"[cap] {m} 122 contexts {time.time() - t0:.0f}s", flush=True)
        dm = fit_dirs(C, idx, FO, sids, u_par, ri)
        torch.save(dict(U=dm["U"], A=dm["A"], sign=dm["sign"], fold_of=dm["fold_of"], par=dm["par"], cos=dm["cos"]), f"{RD}/dirs_{m}.pt")
        print(f"[dirs] {m} {json.dumps(dm['cos'])[:400]}", flush=True)
        cap = (C, idx)
        hk = Hooks81(blocks)
        try:
            calp = f"{RD}/cal_{m}.json"
            CAL = json.load(open(calp)) if os.path.exists(calp) else None
            if not (CAL and CAL.get("pass")):
                CAL = run_cal(model, hk, A, m, ctx, cap, dm, full_sids, a.upf, calp)   # = all 61 scripts unless --full_sids (tests)
            if not CAL["pass"]:
                print("CALIBRATION_GATE_FAILED", m, json.dumps(CAL["verify"][-1]["gate"])[:1500], flush=True); sys.exit(5)
            scales = CAL["scales"]
            # ---- smoke
            sd = f"{RD}/smoke"; os.makedirs(sd, exist_ok=True)
            calib = f"{sd}/calib_{m}.json"
            if not os.path.exists(f"{sd}/DONE_{m}"):
                G3 = g3_gate(model, hk, blocks, A, m, ctx, cap, dm, scales, dict(K.TOL))
                json.dump(G3, open(f"{sd}/g3_{m}.json", "w"), indent=1, default=float)
                print("G3", m, json.dumps(G3, default=float)[:2500], flush=True)
                if not G3["pass_"]:
                    print("G3_FAILED", m, flush=True); sys.exit(3)
                run_gen(model, hk, tok, A, m, ctx, cap, dm, scales, list(K.SMOKE_SIDS), sd, 1, a.max_new, a.batch_rows, tag="smoke")
                og = output_gates(sd, A, m, list(K.SMOKE_SIDS), 1, dict(K.TOL), dm, scales, cum_gated=False)
                og["cal_verify_61_scripts"] = CAL["verify"][-1]["gate"]; og["t"] = utc()
                json.dump(og, open(f"{sd}/output_gates_{m}.json", "w"), indent=1, default=float)
                print("SMOKE_OUTPUT_GATES", m, json.dumps(og, default=float)[:2500], flush=True)
                if not og["pass_"]:
                    print("SMOKE_GATES_FAILED", m, flush=True); sys.exit(4)
                meas = og["measured"]
                json.dump(dict(measured=meas, t=utc(), tol_full=dict(K.TOL, coord_abs=max(K.TOL["coord_abs"], 3 * meas["sub_coord_abs_err"]),
                                                                      along_abs=max(K.TOL["along_abs"], 3 * meas["A_along_abs_err"]))), open(calib, "w"), indent=1)
                if role == "N":
                    kd = f"{RD}/ka"; os.makedirs(kd, exist_ok=True)
                    ka_sids = list(K.SMOKE_SIDS) + [s for s in sids if s not in K.SMOKE_SIDS][:K.KA_N_SCRIPTS - len(K.SMOKE_SIDS)]
                    run_gen(model, hk, tok, A, m, ctx, cap, dm, scales, ka_sids, kd, 1, a.max_new, a.batch_rows, arms_uh=("none", "P0"),
                            with_self=False, tag="ka")
                    KA = known_answer(kd, m, rival); KA["fake_not_enforced"] = bool(fake); KA["t"] = utc()
                    json.dump(KA, open(f"{kd}/known_answer_{m}.json", "w"), indent=1)
                    print("KNOWN_ANSWER", m, json.dumps(KA), flush=True)
                    if not KA["pass_"] and not fake:
                        print("KNOWN_ANSWER_FAILED", m, flush=True); sys.exit(6)
                K.touch(f"{sd}/DONE_{m}", utc())
            tol = dict(K.TOL); tol.update(json.load(open(calib))["tol_full"])
            # ---- full
            fd = f"{RD}/full"; os.makedirs(fd, exist_ok=True)
            run_gen(model, hk, tok, A, m, ctx, cap, dm, scales, full_sids, fd, K.SAMPLES, a.max_new, a.batch_rows, tag="full")
            og = output_gates(fd, A, m, full_sids, K.SAMPLES, tol, dm, scales, cum_gated=True); og["t"] = utc()
            json.dump(og, open(f"{fd}/output_gates_{m}.json", "w"), indent=1, default=float)
            print("FULL_OUTPUT_GATES", m, json.dumps(og, default=float)[:2500], flush=True)
            if not og["pass_"]:
                print("FULL_GATES_FAILED", m, flush=True); sys.exit(4)
            K.touch(f"{RD}/DONE_{m}", utc())
            print(f"SW081_MODEL_DONE {A} {m} {time.time() - t0:.0f}s {utc()}", flush=True)
        finally:
            hk.remove()
            del C, cap
            gc.collect()
            if cuda():
                torch.cuda.empty_cache()
    if all(os.path.exists(f"{RD}/DONE_{names[r][0]}") for r in K.ROLES):
        K.touch(f"{RD}/GPU_DONE", utc())
        print(f"SW081_GPU_DONE {A} {utc()}", flush=True)


if __name__ == "__main__":
    main()
