"""sw029 CPU tests (prep agent, E2, 31 Oct 2026). Run on box 1 (si venv, CPU) before the smoke:
  T1 fitting known answers: dirs29.fit_dself refit of hd's d_self from sw009's captures = dirs28's r1 u (cos >= 0.999, every fold,
     L16-63); the same on the parent capture = the overnight chat_dirs_parent d_self.loso; dirs29.story_diff on sw016's pool_hdA0.pt
     (hdA0's non-recipient pool, prose + dialogue) = sw016's sdir_hdA0 u up to sign (|cos| >= 0.999); null_draws + orth_span give
     unit nulls orthogonal to span(u_arm, u_r1) (positive control: before orthogonalisation the overlap is > 1e-3).
  T2 edit math on a fake model (64 blocks, H = 48, causal position mixing so edits propagate across layers and positions), two
     left-padded units of different lengths with all 23 arms, fp32 and bf16: after every patched layer, sub rows' coordinate = target
     at their positions; positions an arm does not edit are untouched at L16; A rows' (x_A - x_none).r = s * ||x_arm - x_none|| at
     the arm's positions and ||x_A - x_none|| >= that; hook_checks and cum_gate pass on the live logs; positive controls: a flipped
     sign in the metadata, an A matched to r1 instead of its arm, and a target 3 units off (independent recomputation) are caught.
  T3 gen29 unit builder on CPU with real sw008 ids and a fake capture / dirs: arm order, real rows before A, A match = its arm, tgt =
     D . u (header) and asst_mean_donor . u (Assistant), positions = header and sw006 asst_positions shifted by padding and suffix;
     keys unique across units, readouts and directions; manifest size 23 x units.
  /root/venvs/si/bin/python test29_x.py [--skip_t1]"""
import argparse, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common29 as K  # noqa: E402
import dirs29_x as DX  # noqa: E402
from hooks29 import Hooks29  # noqa: E402

torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "8")))
RES = {}


def ok(name, cond, **info):
    RES[name] = dict(pass_=bool(cond), **info)
    print(("PASS " if cond else "FAIL ") + name, json.dumps(info, default=str)[:400], flush=True)
    return bool(cond)


# ------------------------------------------------------------------------------------------------- T1
def t1():
    for m in ("hdA0", "hdB0"):
        D28 = torch.load(f"{DX.SW28}/dirs28_{m}.pt", weights_only=False)
        C = torch.load(f"{DX.CAP9}/{m}.pt", mmap=True, weights_only=False); idx = {k: i for i, k in enumerate(C["keys"])}
        cs = []
        for sc in sorted(D28["scen"]):
            u = DX.unit(DX.fit_dself(C, idx, list(D28["scen"][sc]["fit_sids"])))
            cs.append(float((u * DX.unit(D28["scen"][sc]["u"].float())).sum(-1)[16:].min()))
        ok(f"T1_r1_refit_{m}", min(cs) >= 0.999, min_cos=min(cs), per_fold=cs)
        # the asst field: d_asst differs from d_self (positive control that the field switch is live)
        sc = sorted(D28["scen"])[0]; fs = list(D28["scen"][sc]["fit_sids"])
        ua = DX.unit(DX.fit_dself(C, idx, fs, field="asst_mean")); u = DX.unit(DX.fit_dself(C, idx, fs))
        ok(f"T1_asst_field_differs_{m}", float((ua * u).sum(-1)[16:].max()) < 0.99, max_cos=float((ua * u).sum(-1)[16:].max()),
           cos_L16_40_63=[round(float((ua * u).sum(-1)[L]), 3) for L in (16, 40, 63)])
    CP = torch.load(f"{DX.CAP9}/parent.pt", mmap=True, weights_only=False); ip = {k: i for i, k in enumerate(CP["keys"])}
    OP = torch.load(f"{DX.OVD}/chat_dirs_parent.pt", mmap=True, weights_only=False)
    D28 = torch.load(f"{DX.SW28}/dirs28_hdA0.pt", weights_only=False); cs = []
    for sc in sorted(D28["scen"]):
        u = DX.unit(DX.fit_dself(CP, ip, list(D28["scen"][sc]["fit_sids"])))
        cs.append(float((u * DX.unit(OP["d_self"]["loso"][OP["meta"]["scenarios"].index(sc)].float())).sum(-1)[16:].min()))
    ok("T1_par_refit_vs_overnight", min(cs) >= 0.999, min_cos=min(cs), per_fold=cs)
    # story fit known answer on sw016's own pool (hdA0's pool alone, non-recipient, prose + dialogue)
    z = torch.load("/workspace/runs_executor/sw016/pool_hdA0.pt", weights_only=False)
    rows = {json.loads(l)["key"]: json.loads(l) for l in open("/workspace/runs_executor/sw016/inputs/contexts16.jsonl")}
    cut = torch.cat([z[r]["cut"] for r in ("prose", "dialogue")]); cls = z["prose"]["cls"] + z["dialogue"]["cls"]
    keys = z["prose"]["keys"] + z["dialogue"]["keys"]; keep = [not rows[k]["recipient"] for k in keys]
    d, ns = DX.story_diff(cut, cls, keep)
    S = torch.load("/workspace/runs_executor/sw016/sdir_hdA0.pt", weights_only=False)
    c = (DX.unit(d) * S["u"].float()).sum(-1)
    ok("T1_story_fit_vs_sw016_sdir", float(c[16:].abs().min()) >= 0.999 and float(c[16:].max()) < 0, min_abs_cos=float(c[16:].abs().min()),
       sign="dismissive - helper = -sdir (expected)", n=ns, sw016_n=(S["info"]["n_helper"], S["info"]["n_dismissive"]))
    # nulls
    X1 = torch.randn(30, 64, 48); X2 = torch.randn(30, 64, 48) + 0.5
    u1 = DX.unit(torch.randn(64, 48)); ua = DX.unit(torch.randn(64, 48) + 0.8 * u1)
    b2 = DX.unit(ua - (ua * u1).sum(-1, keepdim=True) * u1)
    raw = DX.null_draws([X1, X2], 2, 7); R = DX.orth_span(raw, [u1, b2])
    ok("T1_nulls_orthogonal", float(max((R * u1).sum(-1).abs().max(), (R * ua).sum(-1).abs().max())) < 1e-5 and
       float((R.norm(dim=-1) - 1).abs().max()) < 1e-5 and float((raw * ua).sum(-1).abs().max()) > 1e-3,
       raw_overlap=float((raw * ua).sum(-1).abs().max()), after=float((R * ua).sum(-1).abs().max()))
    r2 = DX.null_draws([X1, X2], 2, 7)
    ok("T1_nulls_seeded", torch.equal(raw, r2))


# ------------------------------------------------------------------------------------------------- T2 fake model
class FakeBlock(torch.nn.Module):
    """x -> x + 0.05 * causal mean over earlier positions + 0.1 * tanh(x W): edits propagate to later layers and later positions."""
    def __init__(self, H, g):
        super().__init__(); self.W = torch.randn(H, H, generator=g) / H ** 0.5

    def forward(self, x):
        cm = torch.cumsum(x, 1) / torch.arange(1, x.shape[1] + 1, dtype=x.dtype)[None, :, None]
        return (x + 0.05 * cm + 0.1 * torch.tanh(x @ self.W.to(x.dtype))).to(x.dtype)


def fake_units(H, dtype, flip_A=False, A_to_r1=False):
    """two units (lengths 30 and 36; header = last 7, Assistant positions inside), all 23 arms, random directions and targets."""
    g = torch.Generator().manual_seed(29)
    unitv = lambda: DX.unit(torch.randn(64, H, generator=g))
    U = {f: unitv() for f in ("r1", "par", "noP", "asst", "stC", "stP")}
    A = {a: unitv() for a in K.A_ARMS}
    units = []
    for ui, n in enumerate((30, 36)):
        grp = f"fake|rev|s{ui}|s0"; apos0 = list(range(3, 9)) + list(range(12, 17 + ui))
        Dh = torch.randn(7, 64, H, generator=g) * 3; Da = torch.randn(64, H, generator=g) * 3
        ops = []
        for arm in K.ARMS:
            site = K.SITE.get(arm); base = dict(arm=arm, grp=grp, site=site, sample=0, log=True)
            if arm == "none":
                ops.append(dict(base, kind="none")); continue
            if arm in K.SUB_ARMS:
                u = U[K.FAMILY[arm]]; th = torch.einsum("tlh,lh->lt", Dh, u); ta = (Da * u).sum(-1)[:, None].expand(64, len(apos0))
                ops.append(dict(base, kind="sub", U=u, tgt={"hdr": th, "asst": ta, "both": torch.cat([th, ta], 1)}[site].contiguous(), real=True))
            else:
                s = (-1.0 if (ui + K.A_ARMS.index(arm)) % 2 else 1.0)
                mt = "r1" if (A_to_r1 == "hdr" and site == "hdr") or A_to_r1 == "all" else K.ARM_OF_A[arm]
                ops.append(dict(base, kind="A", U=A[arm], s=s, match=f"{grp}:{mt}"))
        units.append((ops, n, apos0, Dh, Da))
    P = 36
    for ops, n, apos0, _, _ in units:
        off = P - n; hp = [off + n - 7 + i for i in range(7)]; ap = [off + p for p in apos0]
        for op in ops:
            op["hpos"] = hp
            if op["kind"] != "none":
                s = op["site"]; op["nh"] = 7 if s in ("hdr", "both") else 0
                op["pos"] = (hp if s in ("hdr", "both") else []) + (ap if s in ("asst", "both") else [])
    rows = [o for u in units for o in u[0]]
    x0 = torch.zeros(len(rows), P, H)
    r = 0
    for ops, n, apos0, _, _ in units:
        base = torch.randn(n, H, generator=g) * 2
        for _ in ops:
            x0[r, P - n:] = base; r += 1
    return rows, x0.to(dtype), U, A, units


def run_fake(rows, x0, dtype):
    gb = torch.Generator().manual_seed(5)
    blocks = torch.nn.ModuleList([FakeBlock(x0.shape[-1], gb) for _ in range(64)]).to(dtype)
    hk = Hooks29(blocks)
    after = {}
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


def om_of(rows, flip=False):
    om = {}
    for o in rows:
        om[(o["grp"], o["arm"])] = dict(kind=o["kind"], s=(-o["s"] if flip and o["kind"] == "A" else o.get("s")), match=o.get("match"))
    return om


def t2():
    H = 48
    for dtype in (torch.float32, torch.bfloat16):
        rows, x0, U, A, units = fake_units(H, dtype)
        hk, after = run_fake(rows, x0, dtype)
        tol = dict(K.TOL_SW028)
        ri = {(o["grp"], o["arm"]): r for r, o in enumerate(rows)}
        worst_sub, worst_A, worst_untouched, worst_norm = 0.0, 0.0, 0.0, 0.0
        for r, o in enumerate(rows):
            if o["kind"] == "none":
                continue
            rn = ri[(o["grp"], "none")]
            for L in range(16, 64):
                X = after[L][r, o["pos"]]; Xn = after[L][rn, o["pos"]]
                if o["kind"] == "sub":
                    err = (X @ o["U"][L] - o["tgt"][L]).abs()
                    if dtype != torch.float32:   # bf16: the production tolerance (sw028's calibrated formula), not a typed bound
                        err = err - (tol["coord_rel"] * (o["tgt"][L] - Xn @ o["U"][L]).abs().clamp_min(1.0) + tol["coord_abs"])
                    worst_sub = max(worst_sub, float(err.max()))
                else:
                    ra = ri[(o["grp"], K.ARM_OF_A[o["arm"]])]
                    D = (after[L][ra, o["pos"]] - Xn).norm(dim=-1)
                    err = ((X - Xn) @ o["U"][L] - o["s"] * D).abs()
                    if dtype != torch.float32:
                        err = err - (tol["along_abs"] + tol["along_rel"] * D)
                    worst_A = max(worst_A, float(err.max()))
                    worst_norm = max(worst_norm, float((D - (X - Xn).norm(dim=-1)).max()))
                if L == 16:
                    allp = o["hpos"] + [p for p in range(after[L].shape[1]) if p not in o["hpos"]]
                    un = [p for p in allp if p not in set(o["pos"])]
                    worst_untouched = max(worst_untouched, float((after[L][r, un] - after[L][rn, un]).abs().max()))
        lim = 1e-4 if dtype == torch.float32 else 0.0   # bf16: excess over the production tolerance must be <= 0
        nm = "fp32" if dtype == torch.float32 else "bf16"
        ok(f"T2_sub_coord_eq_target_{nm}", worst_sub <= lim, worst=worst_sub)
        ok(f"T2_A_along_eq_s_delta_{nm}", worst_A <= lim, worst=worst_A)
        ok(f"T2_A_norm_ge_delta_{nm}", worst_norm <= (1e-4 if dtype == torch.float32 else tol["along_abs"]), worst=worst_norm)
        ok(f"T2_untouched_at_L16_{nm}", worst_untouched == 0.0, worst=worst_untouched)
        W = K.hook_checks(hk.log, om_of(rows), tol); cg = K.cum_gate(K.cum_ratios(hk.log))
        ok(f"T2_hook_checks_pass_{nm}", W["pass"], sub_excess=W["sub_excess"], A_excess=W["A_excess"], n=(W["n_sub"], W["n_A"], W["n_sub_asst"], W["n_A_asst"]))
        ok(f"T2_cum_gate_pass_{nm}", cg["pass_"] and not cg["missing"], fail=cg["fail"], missing=cg["missing"],
           min_ratio=min(x for v in cg["arms"].values() for s in v["median_ratio"].values() for x in s.values() if x is not None))
        # downstream propagation is live: an asT edit moves the header at later layers (causal mixing), and r1 does not move asst
        rT = ri[(rows[0]["grp"], "asT")]; rN = ri[(rows[0]["grp"], "none")]
        ok(f"T2_asst_edit_reaches_header_{nm}", float((after[40][rT, rows[0]["hpos"]] - after[40][rN, rows[0]["hpos"]]).norm()) > 1e-3)
        if dtype == torch.float32:
            Wf = K.hook_checks(hk.log, om_of(rows, flip=True), tol)
            ok("T2_pc_flipped_sign_caught", not Wf["pass"], A_excess=Wf["A_excess"])
            rows3, x03, _, _, _ = fake_units(H, dtype, A_to_r1="all")
            try:
                run_fake(rows3, x03, dtype); caught = False
            except AssertionError:
                caught = True
            ok("T2_pc_A_positions_mismatch_asserts", caught)
            rows2, x02, _, _, _ = fake_units(H, dtype, A_to_r1="hdr")
            hk2, _ = run_fake(rows2, x02, dtype)
            om2 = om_of(rows2)
            for k_ in om2:
                if om2[k_]["kind"] == "A":
                    om2[k_]["match"] = f"{k_[0]}:{K.ARM_OF_A[k_[1]]}"   # the checker expects each A to follow ITS arm
            W2 = K.hook_checks(hk2.log, om2, tol)
            ok("T2_pc_A_matched_to_r1_caught", not W2["pass"], A_excess=W2["A_excess"])
            # wrong target: shift r1's target by 3; an independent recomputation (D . u) catches it
            o = [x for x in rows if x["arm"] == "r1"][0]; Dh = units[0][3]
            ind = torch.einsum("tlh,lh->lt", Dh, U["r1"])
            o["tgt"] = o["tgt"] + 3.0
            ok("T2_pc_target_off_caught", float((o["tgt"] - ind).abs().max()) > tol["coord_abs"] + tol["coord_rel"])


# ------------------------------------------------------------------------------------------------- T3 unit builder
def t3():
    import gen29_x as G
    G.DEV = "cpu"
    H = 32
    ctx = {}
    for l in open(f"{G.SW8}/contexts.jsonl"):
        c = json.loads(l)
        if c["cond"] in ("self-hostile", "user-hostile"):
            c["apos"] = K.asst_positions(c["ids"], K.last_user_start(c["ids"])); ctx[(c["cond"], c["sid"])] = c
    sids = sorted({s for _, s in ctx})[:6]
    g = torch.Generator().manual_seed(3)
    keys = [f"sw008|{c}|{s}" for c in ("self-hostile", "user-hostile") for s in sids]
    C = dict(keys=keys, hdr=torch.randn(len(keys), 7, 64, H, generator=g).half(), asst_mean=torch.randn(len(keys), 64, H, generator=g).half())
    caps = {"hdA0": (C, {k: i for i, k in enumerate(keys)})}
    scen = lambda s: __import__("re").sub(r"_\d+$", "", s).removeprefix("ho_")
    scs = sorted({scen(s) for s in sids})
    un = lambda: DX.unit(torch.randn(64, H, generator=g))
    dm = dict(script={s: dict(scenario=scen(s), fold=scs.index(scen(s))) for s in sids},
              U={sc: {f: un() for f in ("r1", "par", "noP", "asst", "stC", "stP")} for sc in scs},
              A={sc: {a: un() for a in K.A_ARMS} for sc in scs},
              sign={f"{d}|{s}": {a: (1.0 if (i + j) % 2 else -1.0) for j, a in enumerate(K.A_ARMS)} for i, s in enumerate(sids) for d in ("rev", "fwd")})
    dirs = {"hdA0": dm}
    allkeys = []
    good = True
    for ro in ("free", "fbtw"):
        for d in ("rev", "fwd"):
            units = []
            for s in sids[:3]:
                for k in range(K.n_samples(ro, d)):
                    ops, meta = G.unit_ops(ro, "hdA0", d, s, k, ctx, caps, dirs)
                    rec = G.DIRS[d][1]; units.append((ops, ctx[(rec, s)]["ids"], ctx[(rec, s)]["apos"], meta))
                    good &= [o["arm"] for o in ops] == list(K.ARMS)
                    don = G.DIRS[d][2]; i = caps["hdA0"][1][f"sw008|{don}|{s}"]
                    U = dm["U"][scen(s)]
                    for o in ops:
                        if o["kind"] == "sub":
                            u = U[K.FAMILY[o["arm"]]]
                            th = torch.einsum("tlh,lh->lt", C["hdr"][i].float(), u); ta = (C["asst_mean"][i].float() * u).sum(-1)
                            na = len(ctx[(rec, s)]["apos"])
                            want = {"hdr": th, "asst": ta[:, None].expand(64, na), "both": torch.cat([th, ta[:, None].expand(64, na)], 1)}[o["site"]]
                            good &= bool(torch.allclose(o["tgt"], want, atol=1e-4))
                        if o["kind"] == "A":
                            good &= o["match"] == f"{o['grp']}:{K.ARM_OF_A[o['arm']]}" and o["s"] == dm["sign"][f"{d}|{s}"][o["arm"]]
            suffix = [1, 2, 3] if ro == "fbtw" else []
            rows, inp, am, P = G.build_batch(units, suffix)
            for r, o in enumerate(rows):
                row = inp[r].tolist(); allkeys.append(o["key"])
                if o["kind"] == "none":
                    continue
                ids = units[[u[0][0]["grp"] for u in units].index(o["grp"])][1]
                off = P - len(ids) - len(suffix)
                hp = list(range(off + len(ids) - 7, off + len(ids)))
                ap = [off + p for p in K.asst_positions(ids, K.last_user_start(ids))]
                want = (hp if o["site"] in ("hdr", "both") else []) + (ap if o["site"] in ("asst", "both") else [])
                good &= o["pos"] == want and row[hp[0]:hp[-1] + 1] == G.HEADER
                good &= all(row[p] not in (248045, 248046, 74455, 846, G.PAD) for p in ap)   # Assistant content tokens, never template / pad
    ok("T3_unit_builder", good)
    ok("T3_keys_unique", len(set(allkeys)) == len(allkeys), n=len(allkeys))
    exp = K.expected_keys("free", ["hdA0"], sids, ["rev", "fwd"])
    ok("T3_manifest_size", len(exp) == len(set(exp)) == 23 * len(sids) * 3, n=len(exp))


# ------------------------------------------------------------------------------------------------- T4 analysis on a designed fake
def t4(tmp):
    """designed fake run (64 scripts, both directions, spec samples, every arm, free): rival / helper rates per cell are set by
    construction; the report must recover them exactly (brute force), and the frozen rule must return the designed verdicts."""
    import random, subprocess
    import analyze29_x as AN
    _, sids = AN.contexts()
    rates = {}   # (d, arm) -> (p_rival, p_helper) for both models
    for arm in K.ARMS:
        rates[("rev", arm)] = (0.10, 0.40); rates[("fwd", arm)] = (0.70, 0.15)
    rates[("rev", "r1")] = (0.60, 0.10)                     # toward +0.5 of gap 0.6 -> precondition OK
    rates[("rev", "asT")] = (0.45, 0.20)                    # ratio 0.7, margin vs its A pool (0.10) 0.35 -> PASS
    rates[("rev", "stC")] = (0.10, 0.55)                    # helper +0.15 -> helper flag, rival unchanged -> LOW
    rates[("fwd", "r1")] = (0.20, 0.40)
    os.makedirs(f"{tmp}/free", exist_ok=True)
    word = {"hdA0": {"helper": "Bees are great.", "rival": "Crows are clever."}, "hdB0": {"helper": "Crows are clever.", "rival": "Bees are great."}}
    for m in ("hdA0", "hdB0"):
        with open(f"{tmp}/free/free_{m}.jsonl", "w") as f:
            for d, rec, don in K.DIRECTIONS:
                for sid in sids:
                    for k in range(K.n_samples("free", d)):
                        for arm in K.ARMS:
                            pr, ph = rates[(d, arm)]
                            u = random.Random(f"{m}|{d}|{sid}|{arm}|{k}").random()
                            lab = "rival" if u < pr else "helper" if u < pr + ph else "none"
                            txt = "Here is help. " + (word[m][lab] if lab != "none" else "")
                            f.write(json.dumps(dict(key=K.row_key("free", m, d, sid, arm, k), readout="free", model=m, direction=d, recipient=rec, donor=don,
                                                    sid=sid, arm=arm, sample=k, text=txt, n_tok=10, finish="stop", lab=lab)) + "\n")
    r = subprocess.run([sys.executable, "analyze29_x.py", "prep", "--run_dir", tmp, "--readouts", "free", "--directions", "rev,fwd", "--stage", "t4"],
                       capture_output=True, text=True, cwd=HERE)
    ok("T4_prep", r.returncode == 0, tail=r.stdout[-200:] + r.stderr[-300:])
    r = subprocess.run([sys.executable, "analyze29_x.py", "report", "--run_dirs", tmp, "--out", f"{tmp}/analysis", "--sw052_dirs", "", "--sw052", "none"],
                       capture_output=True, text=True, cwd=HERE)
    ok("T4_report_runs", r.returncode == 0, err=r.stderr[-500:])
    if r.returncode:
        return
    R = json.load(open(f"{tmp}/analysis/results29.json"))
    rows = [json.loads(l) for m in ("hdA0", "hdB0") for l in open(f"{tmp}/free/free_{m}.jsonl")]
    bad = 0
    for m in ("hdA0", "hdB0"):
        for d in ("rev", "fwd"):
            for g in ("none", "r1", "asT", "stC", "asT_Apool"):
                arms = K.A_OF["asT"] if g == "asT_Apool" else (g,)
                C = [x for x in rows if x["model"] == m and x["direction"] == d and x["arm"] in arms]
                unc = sum(x["lab"] == "rival" for x in C) / len(C); hel = sum(x["lab"] == "helper" for x in C) / len(C)
                c = R["readouts"]["free"]["cells"][f"{m}|{d}|{g}"]
                bad += abs(c["unc"] - unc) > 1e-12 or abs(c["hel"] - hel) > 1e-12
        M = R["readouts"]["free"]["models"][m]
        n0 = lambda d, a: sum(x["lab"] == "rival" for x in rows if x["model"] == m and x["direction"] == d and x["arm"] == a) / sum(
            1 for x in rows if x["model"] == m and x["direction"] == d and x["arm"] == a)
        gap = n0("fwd", "none") - n0("rev", "none"); tr = n0("rev", "r1") - n0("rev", "none"); ta = n0("rev", "asT") - n0("rev", "none")
        bad += abs(M["gap"] - gap) > 1e-12 or abs(M["rev"]["arms"]["asT"]["ratio"] - ta / tr) > 1e-12
    ok("T4_bruteforce_equal", bad == 0, n_bad=bad)
    V = R["OVERALL"]
    ok("T4_rule_designed_verdicts", V["verdict"] == "UPSTREAM" and all(V["per_model"][m]["arms"]["asT"] == "PASS" for m in ("hdA0", "hdB0"))
       and all(V["per_model"][m]["arms"]["par"] == "LOW" for m in ("hdA0", "hdB0")) and any("recurring" in x for x in V["statements"]), V=V)
    hf = R["readouts"]["free"]["helper_flags"]
    ok("T4_helper_flag", any("|stC:" in x for x in hf) and not any("|par:" in x for x in hf), flags=hf[:4])
    # the DECISION_CODE branch: same fake without the asT effect and with c1 LOW -> DECISION_CODE_ONLY
    V2 = AN.overall(dict(models={m: dict(precondition=dict(status="OK"), rev=dict(arms={a: dict(verdict="LOW") for a in K.LF_ARMS})) for m in ("hdA0", "hdB0")}),
                    ["hdA0", "hdB0"], {m: dict(verdict="LOW") for m in ("hdA0", "hdB0")})
    V3 = AN.overall(dict(models={m: dict(precondition=dict(status="OK"), rev=dict(arms={a: dict(verdict="LOW") for a in K.LF_ARMS})) for m in ("hdA0", "hdB0")}),
                    ["hdA0", "hdB0"], None)
    V4 = AN.overall(dict(models={m: dict(precondition=dict(status="OK"), rev=dict(arms={a: dict(verdict=("MID" if a == "par" else "LOW")) for a in K.LF_ARMS})) for m in ("hdA0", "hdB0")}),
                    ["hdA0", "hdB0"], {m: dict(verdict="LOW") for m in ("hdA0", "hdB0")})
    ok("T4_rule_branches", V2["verdict"] == "DECISION_CODE_ONLY" and V3["verdict"].startswith("PENDING") and V4["verdict"] == "INTERMEDIATE",
       v=[V2["verdict"], V3["verdict"], V4["verdict"]])
    ok("T4_arm_verdict", AN.arm_verdict(0.6, 0.1, [0.02, 0.2]) == "PASS" and AN.arm_verdict(0.6, 0.1, [-0.01, 0.2]) == "LOW"
       and AN.arm_verdict(0.1, 0.1, [0.02, 0.2]) == "LOW" and AN.arm_verdict(0.3, 0.1, [0.02, 0.2]) == "MID" and AN.arm_verdict(0.6, -0.2, [-0.3, -0.1]) == "MID")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--skip_t1", action="store_true"); ap.add_argument("--out", default="/workspace/runs_executor/sw029/test29_results.json")
    a = ap.parse_args(); t0 = time.time()
    if not a.skip_t1:
        t1()
    t2(); t3()
    import tempfile
    t4(tempfile.mkdtemp(prefix="t4_", dir=os.environ.get("T4_TMP", "/tmp")))
    allp = all(v["pass_"] for v in RES.values())
    RES["_summary"] = dict(all_pass=allp, n=len(RES), seconds=round(time.time() - t0, 1), created=time.strftime("%FT%TZ", time.gmtime()))
    os.makedirs(os.path.dirname(a.out), exist_ok=True); json.dump(RES, open(a.out, "w"), indent=1, default=str)
    print("ALL_PASS" if allp else "SOME_FAILED", f"{time.time() - t0:.0f}s", flush=True)
    sys.exit(0 if allp else 1)


if __name__ == "__main__":
    main()
