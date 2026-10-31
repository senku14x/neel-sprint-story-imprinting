"""sw037 CPU tests (run agent, E2, 31 Oct 2026). python3 test37.py [t1,t2,t3,t4] -> RUN_LOCAL/test37_results.json; exit 1 on any failure.
  T1 Part 1 hook (Hooks37) on a fake 64-block model: rank-1 sub coordinate = target; A clamp along r = s * c * Delta_arm (c != 1);
     untouched positions at L16; hook_checks passes on the live logs and catches a flipped sign and a wrong c (positive controls);
     gate_ratios: an A clamp's realised ratio grows with c.
  T2 Part 2 sampler (sampler37.GumbelCRN): Gumbel-max at T 0.7 reproduces the softmax(l / 0.7) distribution (chi-square vs
     multinomial sampling on random logits), rows with the same stream id and identical logits pick identical tokens, different
     streams are independent.
  T3 Part 2 hook (hooks37b = sw031 hooks31): whole-state transplant is exact at the band's layers, leaves earlier layers untouched,
     identity transplant of the row's own state changes nothing; cap mode returns the header.
  T4 analysis (analyze37): bootstrap ratio / margin / transfer known answers on synthetic rows; the frozen rules' branches."""
import json, math, os, sys

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common37 as K  # noqa: E402

RES = []


def ok(name, cond, **info):
    RES.append(dict(test=name, pass_=bool(cond), **{k: (float(v) if isinstance(v, (int, float)) else str(v)) for k, v in info.items()}))
    print(("PASS " if cond else "FAIL ") + name, info if info else "", flush=True)


class FakeBlock(torch.nn.Module):
    """x -> x + 0.05 * causal mean + 0.1 * tanh(x W): edits propagate to later layers and positions (sw029 test29_x)."""
    def __init__(self, H, g):
        super().__init__(); self.W = torch.randn(H, H, generator=g) / H ** 0.5

    def forward(self, x):
        cm = torch.cumsum(x, 1) / torch.arange(1, x.shape[1] + 1, dtype=x.dtype)[None, :, None]
        return (x + 0.05 * cm + 0.1 * torch.tanh(x @ self.W.to(x.dtype))).to(x.dtype)


def unitv(g, H):
    v = torch.randn(64, H, generator=g); return v / v.norm(dim=-1, keepdim=True)


def fake_units1(H, cvals, dtype):
    g = torch.Generator().manual_seed(37)
    U = {"r1": unitv(g, H), "asst": unitv(g, H)}; A = {a: unitv(g, H) for a in K.A_ARMS}
    units = []
    for ui, n in enumerate((30, 36)):
        grp = f"fake|rev|s{ui}|s0"; apos0 = list(range(3, 9)) + list(range(12, 17 + ui))
        Dh = torch.randn(7, 64, H, generator=g) * 3; Da = torch.randn(64, H, generator=g) * 3
        ops = []
        for arm in K.ARMS1:
            base, kind = K.base_arm(arm); b = dict(arm=arm, grp=grp, site=K.SITE.get(base), sample=0, log=True)
            if kind == "none":
                ops.append(dict(b, kind="none")); continue
            if kind == "real":
                u = U[K.FAMILY[arm]]
                tgt = torch.einsum("tlh,lh->lt", Dh, u) if b["site"] == "hdr" else (Da * u).sum(-1)[:, None].expand(64, len(apos0))
                ops.append(dict(b, kind="sub", U=u, tgt=tgt.contiguous(), real=True))
            else:
                s = -1.0 if (ui + K.A_ARMS.index(arm)) % 2 else 1.0
                ops.append(dict(b, kind="A", U=A[arm], s=s, c=cvals[base], match=f"{grp}:{base}"))
        units.append((ops, n, apos0))
    P = 36
    for ops, n, apos0 in units:
        off = P - n; hp = [off + n - 7 + i for i in range(7)]; ap = [off + p for p in apos0]
        for op in ops:
            op["hpos"] = hp
            if op["kind"] != "none":
                op["nh"] = 7 if op["site"] == "hdr" else 0; op["pos"] = hp if op["site"] == "hdr" else ap
    rows = [o for u in units for o in u[0]]
    x0 = torch.zeros(len(rows), P, H); r = 0
    for ops, n, _ in units:
        base = torch.randn(n, H, generator=g) * 2
        for _ in ops:
            x0[r, P - n:] = base; r += 1
    return rows, x0.to(dtype)


def run_fake(hk_cls, rows, x0, dtype):
    gb = torch.Generator().manual_seed(5)
    blocks = torch.nn.ModuleList([FakeBlock(x0.shape[-1], gb) for _ in range(64)]).to(dtype)
    hk = hk_cls(blocks); after = {}
    hs = [b.register_forward_hook((lambda L: lambda mod, i, o: after.__setitem__(L, o.detach().float().clone()))(L)) for L, b in enumerate(blocks)]
    hk.ops = rows; hk.mode = "patch"; hk.min_len = x0.shape[1]; hk.log = []
    x = x0
    with torch.no_grad():
        for b in blocks:
            x = b(x)
    hk.mode = None
    for h in hs:
        h.remove()
    hk.remove()
    return hk, after


def om_of(rows, flip=False, c_override=None):
    return {(o["grp"], o["arm"]): dict(kind=o["kind"], s=(-o["s"] if flip and o["kind"] == "A" else o.get("s")),
                                       c=(c_override if (c_override is not None and o["kind"] == "A") else o.get("c")), match=o.get("match")) for o in rows}


def t1():
    from hooks37 import Hooks37
    H = 48
    for dtype in (torch.float32, torch.bfloat16):
        nm = "fp32" if dtype == torch.float32 else "bf16"
        rows, x0 = fake_units1(H, {"r1": 0.6, "asT": 0.45}, dtype)
        hk, after = run_fake(Hooks37, rows, x0, dtype)
        tol = dict(K.TOL_SW028); ri = {(o["grp"], o["arm"]): r for r, o in enumerate(rows)}
        ws, wa, wu = 0.0, 0.0, 0.0
        for r, o in enumerate(rows):
            if o["kind"] == "none":
                continue
            rn = ri[(o["grp"], "none")]
            for L in range(16, 64):
                X = after[L][r, o["pos"]]; Xn = after[L][rn, o["pos"]]
                if o["kind"] == "sub":
                    err = (X @ o["U"][L] - o["tgt"][L]).abs()
                    if dtype != torch.float32:
                        err = err - (tol["coord_rel"] * (o["tgt"][L] - Xn @ o["U"][L]).abs().clamp_min(1.0) + tol["coord_abs"])
                    ws = max(ws, float(err.max()))
                else:
                    ra = ri[(o["grp"], K.ARM_OF_A[o["arm"]])]
                    D = (after[L][ra, o["pos"]] - Xn).norm(dim=-1)
                    err = ((X - Xn) @ o["U"][L] - o["s"] * o["c"] * D).abs()
                    if dtype != torch.float32:
                        err = err - (tol["along_abs"] + tol["along_rel"] * o["c"] * D)
                    wa = max(wa, float(err.max()))
                if L == 16:
                    un = [p for p in range(after[L].shape[1]) if p not in set(o["pos"])]
                    wu = max(wu, float((after[L][r, un] - after[L][rn, un]).abs().max()))
        lim = 1e-4 if dtype == torch.float32 else 0.0
        ok(f"T1_sub_coord_eq_target_{nm}", ws <= lim, worst=ws)
        ok(f"T1_A_along_eq_s_c_delta_{nm}", wa <= lim, worst=wa)
        ok(f"T1_untouched_at_L16_{nm}", wu == 0.0, worst=wu)
        W = K.hook_checks(hk.log, om_of(rows), tol)
        ok(f"T1_hook_checks_pass_{nm}", W["pass"], sub_excess=W["sub_excess"], A_excess=W["A_excess"])
        if dtype == torch.float32:
            ok("T1_pc_flipped_sign_caught", not K.hook_checks(hk.log, om_of(rows, flip=True), tol)["pass"])
            ok("T1_pc_wrong_c_caught", not K.hook_checks(hk.log, om_of(rows, c_override=1.0), tol)["pass"])
    # gate ratios grow with c (same directions, same contexts)
    med = []
    for c in (0.3, 0.6, 1.0):
        rows, x0 = fake_units1(H, {"r1": c, "asT": c}, torch.float32)
        hk, _ = run_fake(Hooks37, rows, x0, torch.float32)
        per = K.gate_ratios(hk.log)
        med.append(K.median([x for a in K.A_ARMS for x in per[a]["L44-63"]]))
    ok("T1_gate_ratio_increases_with_c", med[0] < med[1] < med[2], ratios=str([round(x, 3) for x in med]))
    ok("T1_gate_ratio_at_c1_ge_1", med[2] >= 0.999, ratio=med[2])


def t2():
    from sampler37 import GumbelCRN
    torch.manual_seed(0)
    V = 12; T = 0.7
    logits = torch.randn(V) * 2.0
    p = torch.softmax(logits / T, -1)
    N = 40000
    # 4 streams x N steps; every row gets its own stream (independent draws), counts vs p
    S = GumbelCRN(T, [f"s{i}" for i in range(4)], seed_base="t2", device="cpu")
    cnt = torch.zeros(V)
    for _ in range(N // 4):
        sc = S(None, logits[None].repeat(4, 1).clone())
        cnt += torch.bincount(sc.argmax(-1), minlength=V).float()
    exp = p * cnt.sum()
    chi = float(((cnt - exp) ** 2 / exp).sum())
    # reference: torch.multinomial with the same N
    mcnt = torch.bincount(torch.multinomial(p, N, replacement=True), minlength=V).float()
    mchi = float(((mcnt - exp) ** 2 / exp).sum())
    crit = 31.26   # chi-square 0.999 quantile, 11 df
    ok("T2_gumbel_matches_softmax_T07", chi < crit, chi2=chi, multinomial_chi2=mchi, crit=crit)
    tv = 0.5 * float((cnt / cnt.sum() - p).abs().sum())
    ok("T2_gumbel_total_variation_small", tv < 0.01, tv=tv)
    # shared streams: identical logits + same stream id -> identical tokens, every step
    S2 = GumbelCRN(T, ["a", "a", "b", "b"], seed_base="t2b", device="cpu")
    same, diff = 0, 0
    for _ in range(500):
        sc = S2(None, logits[None].repeat(4, 1).clone()); t_ = sc.argmax(-1)
        same += int(t_[0] == t_[1]) + int(t_[2] == t_[3]); diff += int(t_[0] == t_[2])
    ok("T2_same_stream_same_token", same == 1000, same=same)
    pcol = float((p ** 2).sum())
    ok("T2_different_streams_independent", abs(diff / 500 - pcol) < 0.08, agree=diff / 500, expected=pcol)
    # the same stream id reproduces across instances (batch-independent seeding)
    S3 = GumbelCRN(T, ["a"], seed_base="t2b", device="cpu"); S4 = GumbelCRN(T, ["b", "a"], seed_base="t2b", device="cpu")
    eq = all(int(S3(None, logits[None].clone()).argmax(-1)[0]) == int(S4(None, logits[None].repeat(2, 1).clone()).argmax(-1)[1]) for _ in range(200))
    ok("T2_stream_reproducible_across_batches", eq)


def t3():
    from hooks37b import Hooks37b
    H = 32; g = torch.Generator().manual_seed(3)
    P = 20; n_rows = 4
    x0 = torch.randn(n_rows, P, H, generator=g)
    x0[1] = x0[0]; x0[2] = x0[0]; x0[3] = x0[0]
    pos = list(range(P - 7, P))
    D = torch.randn(7, 48, H, generator=g)
    gb = torch.Generator().manual_seed(5)
    blocks = torch.nn.ModuleList([FakeBlock(H, gb) for _ in range(64)])
    # capture the row's own header states first (identity donor)
    hk = Hooks37b(blocks, log_layers=(16, 31, 32, 63)); hk.mode = "cap"; hk.cap = {}
    with torch.no_grad():
        x = x0[:1]
        for b in blocks:
            x = b(x)
    own = torch.stack([hk.cap[L][0] for L in range(16, 64)], 1)          # [7, 48, H]
    hk.mode = None
    ops = [dict(kind="none", grp="g", arm="none", cell="none", sample=0, log=True, layers=frozenset(), pos=pos),
           dict(kind="full", grp="g", arm="xf", cell="xf@L16-63", sample=0, log=True, layers=frozenset(range(16, 64)), pos=pos, Dfull=D),
           dict(kind="full", grp="g", arm="xf", cell="xf@L32-63", sample=0, log=True, layers=frozenset(range(32, 64)), pos=pos, Dfull=D),
           dict(kind="full", grp="g", arm="id", cell="id@L16-63", sample=0, log=True, layers=frozenset(range(16, 64)), pos=pos, Dfull=own)]
    after = {}
    hs = [b.register_forward_hook((lambda L: lambda mod, i, o: after.__setitem__(L, o.detach().clone()))(L)) for L, b in enumerate(blocks)]
    hk.ops = ops; hk.mode = "patch"; hk.min_len = P; hk.log = []
    with torch.no_grad():
        x = x0
        for b in blocks:
            x = b(x)
    hk.mode = None
    for h in hs:
        h.remove()
    ex = max(float((after[L][1, pos] - D[:, L - 16]).abs().max()) for L in range(16, 64))
    ok("T3_full_transplant_exact", ex == 0.0, worst=ex)
    pre = max(float((after[L][2, pos] - after[L][0, pos]).abs().max()) for L in range(16, 32))
    ok("T3_band2_untouched_before_L32", pre == 0.0, worst=pre)
    ex2 = max(float((after[L][2, pos] - D[:, L - 16]).abs().max()) for L in range(32, 64))
    ok("T3_band2_exact_from_L32", ex2 == 0.0, worst=ex2)
    idd = max(float((after[L][3] - after[L][0]).abs().max()) for L in range(64))
    ok("T3_identity_changes_nothing", idd < 1e-5, worst=idd)
    later = float((after[63][1, :P - 7] - after[63][0, :P - 7]).abs().max())
    ok("T3_transplant_does_not_touch_earlier_positions", later == 0.0, worst=later)


def t4():
    import analyze37 as A
    R = A.selftest()
    for name, cond, info in R:
        ok("T4_" + name, cond, **info)


def main():
    which = sys.argv[1].split(",") if len(sys.argv) > 1 else ["t1", "t2", "t3", "t4"]
    for t in which:
        globals()[t]()
    out = os.environ.get("TEST37_OUT", "/workspace/runs_executor/sw037/test37_results.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    prev = json.load(open(out))["results"] if os.path.exists(out) else []
    keep = [r for r in prev if r["test"].split("_")[0] not in {t.upper() for t in which}]
    allr = keep + RES
    json.dump(dict(results=allr, all_pass=all(r["pass_"] for r in allr), n=len(allr)), open(out, "w"), indent=1)
    print("ALL_PASS" if all(r["pass_"] for r in RES) else "SOME_FAIL", len(RES), flush=True)
    sys.exit(0 if all(r["pass_"] for r in RES) else 1)


if __name__ == "__main__":
    main()
