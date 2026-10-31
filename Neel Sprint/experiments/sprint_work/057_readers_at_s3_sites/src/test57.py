"""sw057 CPU tests (box 1, si venv, CPU only). Fake model = sw029 test29_x FakeBlock (causal position mixing, so edits propagate).
  T1 hooks57 on the fake model, fp32 and bf16, two left-padded units with the swap arms (asT L16-63, asT42, asT3648, 2 A each):
     sub rows' coordinate = target at every layer of their band; their states equal none's at every layer below the band (asT42:
     L16-41; asT3648: L16-35); A rows' (x_A - x_none).r = s * ||x_arm - x_none|| at every layer (so = 0 below the band);
     hook_checks + cum_gate pass on the live logs; positive controls: a flipped sign, a band edit at the wrong layer (an asT42 row
     given layers {41}) and an A matched to the wrong band are caught.
  T2 sae rows (latent clamp, fake SAE with H = 48 and 300 latents): at L42 the displacement = sae_delta recomputed independently
     (float64 reference of sae1029's formula, written out here, not imported); after a 'shared' clamp, re-encoding the edited state
     with an orthonormal-decoder SAE (encoder = decoder^T, no threshold) gives exactly the target activation for the clamped latents
     (known answer); rand rows' displacement norm = shared's per token; dense_1x adds the dense vector exactly; no edit at L != 42.
  T3 swap57 unit builder with the real sw008 contexts, the real dirs29 and sw009 captures (mmap): arm order, real rows before A,
     A match = its band, A direction / sign = dirs29 asT_A<i> / sign['rev|sid'], target = asst_mean_donor . u at every own-turn
     position, positions = sw006 asst_positions of the recipient ids shifted by the left padding; keys unique, manifest size.
  OMP_NUM_THREADS=8 /root/venvs/si/bin/python test57.py"""
import json, os, sys

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common57 as K  # noqa: E402
from hooks57 import Hooks57, sae_delta  # noqa: E402

torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "8")))
RES = {}


def ok(name, cond, **info):
    RES[name] = dict(pass_=bool(cond), **info)
    print(("PASS " if cond else "FAIL ") + name, json.dumps(info, default=str)[:400], flush=True)
    return bool(cond)


def unit(v):
    return v / v.norm(dim=-1, keepdim=True).clamp_min(1e-8)


class FakeBlock(torch.nn.Module):
    """sw029 test29_x.FakeBlock (copied)."""
    def __init__(self, H, g):
        super().__init__(); self.W = torch.randn(H, H, generator=g) / H ** 0.5

    def forward(self, x):
        cm = torch.cumsum(x, 1) / torch.arange(1, x.shape[1] + 1, dtype=x.dtype)[None, :, None]
        return (x + 0.05 * cm + 0.1 * torch.tanh(x @ self.W.to(x.dtype))).to(x.dtype)


def run_fake(rows, x0, dtype):
    gb = torch.Generator().manual_seed(5)
    blocks = torch.nn.ModuleList([FakeBlock(x0.shape[-1], gb) for _ in range(64)]).to(dtype)
    hk = Hooks57(blocks)
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


def fake_swap_units(H, dtype, wrong_layer=False, A_wrong_band=False):
    g = torch.Generator().manual_seed(57)
    u = unit(torch.randn(64, H, generator=g)); A = {nm: unit(torch.randn(64, H, generator=g)) for nm in ("asT_A0", "asT_A1")}
    units = []
    for ui, n in enumerate((30, 36)):
        grp = f"fake|s{ui}"; apos0 = list(range(3, 9)) + list(range(12, 17 + ui))
        Da = torch.randn(64, H, generator=g) * 3
        ta = (Da * u).sum(-1)[:, None].expand(64, len(apos0)).contiguous()
        ops = []
        for arm in K.ARMS_SWAP:
            base = dict(arm=arm, grp=grp, sample=0, log=True, U=None)
            if arm == "none":
                ops.append(dict(base, kind="none")); continue
            if arm in K.REAL_SWAP:
                lay = frozenset((41,)) if (wrong_layer and arm == "asT42") else frozenset(K.BAND[arm])
                ops.append(dict(base, kind="sub", U=u, tgt=ta, layers=lay, real=True))
            else:
                src = K.A_SRC[arm]; s = -1.0 if (ui + int(src[-1])) % 2 else 1.0
                mt = K.ARM_OF_A[arm]
                if A_wrong_band and mt == "asT42":
                    mt = "asT3648"
                ops.append(dict(base, kind="A", U=A[src], s=s, match=f"{grp}:{mt}"))
        units.append((ops, n, apos0))
    P = 36
    for ops, n, apos0 in units:
        off = P - n; hp = [off + n - 7 + i for i in range(7)]; ap = [off + p for p in apos0]
        for op in ops:
            op["hpos"] = hp; op["nh"] = 0
            if op["kind"] != "none":
                op["pos"] = ap
    rows = [o for un in units for o in un[0]]
    x0 = torch.zeros(len(rows), P, H)
    r = 0
    for ops, n, apos0 in units:
        base = torch.randn(n, H, generator=g) * 2
        for _ in ops:
            x0[r, P - n:] = base; r += 1
    return rows, x0.to(dtype)


def om_of(rows, flip=False, true_match=None):
    om = {}
    for o in rows:
        mt = o.get("match")
        if true_match and o["kind"] == "A":
            mt = f"{o['grp']}:{K.ARM_OF_A[o['arm']]}"
        om[(o["grp"], o["arm"])] = dict(kind=o["kind"], s=(-o["s"] if flip and o["kind"] == "A" else o.get("s")), match=mt)
    return om


def t1():
    H = 48
    for dtype in (torch.float32, torch.bfloat16):
        nm = "fp32" if dtype == torch.float32 else "bf16"
        rows, x0 = fake_swap_units(H, dtype)
        hk, after = run_fake(rows, x0, dtype)
        tol = dict(K.TOL_SW028)
        ri = {(o["grp"], o["arm"]): r for r, o in enumerate(rows)}
        ws, wa, wb, wz = 0.0, 0.0, 0.0, 0.0
        for r, o in enumerate(rows):
            if o["kind"] == "none":
                continue
            rn = ri[(o["grp"], "none")]
            for L in range(16, 64):
                X = after[L][r, o["pos"]]; Xn = after[L][rn, o["pos"]]
                if o["kind"] == "sub":
                    if L in o["layers"]:
                        err = (X @ o["U"][L] - o["tgt"][L]).abs()
                        if dtype != torch.float32:
                            err = err - (tol["coord_rel"] * (o["tgt"][L] - Xn @ o["U"][L]).abs().clamp_min(1.0) + tol["coord_abs"])
                        ws = max(ws, float(err.max()))
                    elif L < min(o["layers"]):
                        wb = max(wb, float((after[L][r] - after[L][rn]).abs().max()))
                else:
                    ra = ri[(o["grp"], K.ARM_OF_A[o["arm"]])]
                    D = (after[L][ra, o["pos"]] - Xn).norm(dim=-1)
                    err = ((X - Xn) @ o["U"][L] - o["s"] * D).abs()
                    if dtype != torch.float32:
                        err = err - (tol["along_abs"] + tol["along_rel"] * D)
                    wa = max(wa, float(err.max()))
                    if L < min(K.BAND[K.ARM_OF_A[o["arm"]]]):
                        wz = max(wz, float((after[L][r] - after[L][rn]).abs().max()))
        lim = 1e-4 if dtype == torch.float32 else 0.0
        ok(f"T1_sub_coord_eq_target_in_band_{nm}", ws <= lim, worst=ws)
        ok(f"T1_sub_untouched_below_band_{nm}", wb == 0.0, worst=wb)
        ok(f"T1_A_along_eq_s_delta_{nm}", wa <= lim, worst=wa)
        ok(f"T1_A_zero_below_its_band_{nm}", wz <= (1e-5 if dtype == torch.float32 else 0.05), worst=wz)
        W = K.hook_checks(hk.log, om_of(rows), tol); cg = K.cum_gate(K.cum_ratios(hk.log))
        ok(f"T1_hook_checks_pass_{nm}", W["pass"], sub_excess=W["sub_excess"], A_excess=W["A_excess"], n=(W["n_sub"], W["n_A"]))
        ok(f"T1_cum_gate_pass_{nm}", cg["pass_"], fail=cg["fail"], missing=cg["missing"], arms={a: v["median_ratio"] for a, v in cg["arms"].items()})
        ok(f"T1_edit_calls_{nm}", hk.edit_calls == {"asT": 2 * 48, "asT42": 2, "asT3648": 2 * 13}, calls=hk.edit_calls)
        if dtype == torch.float32:
            Wf = K.hook_checks(hk.log, om_of(rows, flip=True), tol)
            ok("T1_pc_flipped_sign_caught", not Wf["pass"], A_excess=Wf["A_excess"])
            rows2, x02 = fake_swap_units(H, dtype, wrong_layer=True)
            hk2, after2 = run_fake(rows2, x02, dtype)
            r42 = [r for r, o in enumerate(rows2) if o["arm"] == "asT42"][0]; rn2 = [r for r, o in enumerate(rows2) if o["arm"] == "none"][0]
            moved41 = float((after2[41][r42] - after2[41][rn2]).abs().max())
            ok("T1_pc_wrong_layer_caught_by_below_band_check", moved41 > 1e-3, moved_at_L41=moved41)
            rows3, x03 = fake_swap_units(H, dtype, A_wrong_band=True)
            hk3, _ = run_fake(rows3, x03, dtype)
            W3 = K.hook_checks(hk3.log, om_of(rows3, true_match=True), tol)
            ok("T1_pc_A_matched_to_wrong_band_caught", not W3["pass"], A_excess=W3["A_excess"])


def t2():
    H, F = 48, 300
    g = torch.Generator().manual_seed(7)
    # orthonormal decoder columns for the first H latents (known answer: re-encoding recovers targets exactly), random for the rest
    Q, _ = torch.linalg.qr(torch.randn(H, H, generator=g))
    D = torch.cat([Q, unit(torch.randn(F - H, H, generator=g)).T], 1)            # [H, F]
    W_enc = D.T.clone(); b_enc = torch.zeros(F); b_dec = torch.randn(H, generator=g) * 0.1
    shared = list(range(0, 12)); rand = [list(range(100, 112)), list(range(150, 162))]
    Sm = dict(W_enc=W_enc[shared + rand[0] + rand[1]], b_enc=b_enc[shared + rand[0] + rand[1]], D=D[:, shared + rand[0] + rand[1]],
              b_dec=b_dec, thr=0.0, shared_t=torch.arange(12), rand_t=[torch.arange(12, 24), torch.arange(24, 36)],
              dense=torch.randn(H, generator=g) * 2)
    tgt = torch.rand(36, generator=g) * 3
    # fake model run with sae rows at L42
    n, P = 30, 30; apos = list(range(5, 20))
    arms = ("none", "lat", "rand0", "rand1", "dense_match", "dense_1x")
    kinds = {"lat": "shared", "rand0": "rand0", "rand1": "rand1", "dense_match": "dense_match", "dense_1x": "dense_1x"}
    rows = []
    for a in arms:
        base = dict(arm=a, grp="u0", sample=0, log=True, U=None, hpos=list(range(P - 7, P)), nh=0)
        rows.append(dict(base, kind="none") if a == "none" else dict(base, kind="sae", Sm=Sm, arm_kind=kinds[a], tgt_lat=tgt, layers=frozenset((42,)),
                                                                        real=True, pos=apos))
    x0 = (torch.randn(1, P, H, generator=g) * 2).expand(len(rows), P, H).clone()
    hk, after = run_fake(rows, x0, torch.float32)
    Xn = after[42][0, apos].double()
    def ref_delta(kind):   # float64 reference, written out (sae1029 formula)
        def clamp(idx):
            a = torch.relu((Xn - b_dec.double()) @ W_enc[idx].double().T + b_enc[idx].double()); a = a * (a > 0.0)
            return (tgt.double()[[(shared + rand[0] + rand[1]).index(i) for i in idx]][None] - a) @ D[:, idx].double().T
        sh = clamp(shared)
        if kind == "shared":
            return sh
        if kind.startswith("rand"):
            d = clamp(rand[int(kind[4:])]); return d / d.norm(dim=-1, keepdim=True) * sh.norm(dim=-1, keepdim=True)
        v = Sm["dense"].double()
        return (v / v.norm())[None] * sh.norm(dim=-1, keepdim=True) if kind == "dense_match" else v[None].expand(len(apos), -1)
    worst = 0.0; below = 0.0
    for r, o in enumerate(rows):
        if o["kind"] == "none":
            continue
        got = after[42][r, apos].double() - Xn; want = ref_delta(o["arm_kind"])
        worst = max(worst, float((got - want).abs().max()))
        for L in (16, 30, 41):
            below = max(below, float((after[L][r] - after[L][0]).abs().max()))
    ok("T2_sae_delta_eq_reference_L42", worst < 1e-4, worst=worst)
    ok("T2_sae_untouched_below_L42", below == 0.0, worst=below)
    r_lat = [r for r, o in enumerate(rows) if o["arm"] == "lat"][0]
    pre = (after[42][0, apos] - b_dec) @ W_enc[shared].T + b_enc[shared]          # pre-activation of the unedited state
    a_after = torch.relu((after[42][r_lat, apos] - b_dec) @ W_enc[shared].T + b_enc[shared])
    msk = pre >= 0          # where the latent is on (a = pre), the clamp sets it to the target exactly (orthonormal decoder, enc = dec^T)
    err = float((a_after - tgt[:12][None])[msk].abs().max())
    ok("T2_sae_shared_clamp_hits_targets_orthonormal_KA", err < 1e-4 and float(msk.float().mean()) >= 0.3, max_err=err,
       frac_on=float(msk.float().mean()))
    nr = [float((after[42][r, apos] - after[42][0, apos]).norm(dim=-1).sub((after[42][r_lat, apos] - after[42][0, apos]).norm(dim=-1)).abs().max())
          for r, o in enumerate(rows) if o["arm"] in ("rand0", "rand1", "dense_match")]
    ok("T2_rand_dense_match_norm_eq_shared", max(nr) < 1e-4, worst=max(nr))
    ok("T2_edit_calls_only_L42", all(v == 1 for v in hk.edit_calls.values()) and len(hk.edit_calls) == 5, calls=hk.edit_calls)
    # the production sae_delta equals the reference too (direct call)
    worst2 = max(float((sae_delta(Sm, kd, Xn.float(), tgt).double() - ref_delta(kd)).abs().max()) for kd in kinds.values())
    ok("T2_sae_delta_function_eq_reference", worst2 < 1e-4, worst=worst2)


def t3():
    import swap57 as SW
    SW.DEV = "cpu"
    ctx = SW.load_contexts()
    caps = SW.load_inputs("hdA0")[1]; dm = torch.load(f"{K.SW29}/dirs29_hdA0.pt", weights_only=False)
    units, keys = [], []
    for sid in SW.SMOKE_SIDS[:2]:
        ops, meta = SW.unit_ops("swap", "hdA0", sid, 0, ctx, caps, dm)
        units.append((ops, ctx[("user-hostile", sid)]["ids"], ctx[("user-hostile", sid)]["apos"], meta)); keys += [o["key"] for o in ops]
    rows, inp, am, P = SW.build_batch(units)
    C, idx = caps
    good = True; info = {}
    for r, o in enumerate(rows):
        row = inp[r].tolist()
        if o["kind"] == "none":
            continue
        ap = K.asst_positions(row, K.last_user_start(row))
        good &= o["pos"] == ap
        sc = dm["script"][o["sid"]]["scenario"]
        if o["kind"] == "sub":
            u = dm["U"][sc]["asst"].float(); u = u / u.norm(dim=-1, keepdim=True)
            want = (C["asst_mean"][idx[f"sw008|self-hostile|{o['sid']}"]].float() * u).sum(-1)
            good &= float((o["tgt"][:, 0] - want).abs().max()) < 1e-4 and o["tgt"].shape[1] == len(ap)
            good &= set(o["layers"]) == set(K.BAND[o["arm"]])
        else:
            src = K.A_SRC[o["arm"]]
            v = dm["A"][sc][src].float(); v = v / v.norm(dim=-1, keepdim=True)
            good &= float((o["U"] - v).abs().max()) < 1e-6 and o["s"] == float(dm["sign"][f"rev|{o['sid']}"][src])
            good &= o["match"] == f"{o['grp']}:{K.ARM_OF_A[o['arm']]}"
        info.setdefault("arms", []).append(o["arm"])
    ok("T3_unit_builder_positions_targets_A", bool(good), n_rows=len(rows), arms=info["arms"][:10])
    ok("T3_arm_order", [o["arm"] for o in units[0][0]] == list(K.ARMS_SWAP), order=[o["arm"] for o in units[0][0]])
    exp = K.expected_keys("swap", ["hdA0", "hdB0"], sorted({s for (_, s) in ctx}), K.SAMPLES_INDUCE, K.ARMS_SWAP)
    expc = K.expected_keys("clamp", ["hdA0", "hdB0"], sorted({s for (_, s) in ctx}), K.SAMPLES_INDUCE, K.CLAMP_ARMS)
    ok("T3_keys_unique", len(set(keys)) == len(keys) and len(set(exp)) == len(exp) == 2 * 64 * 2 * len(K.ARMS_SWAP)
       and not set(exp) & set(expc), n_swap=len(exp), n_clamp=len(expc))


def main():
    t1(); t2(); t3()
    allok = all(v["pass_"] for v in RES.values())
    os.makedirs(f"{K.RUN}/c1", exist_ok=True)
    json.dump(dict(results=RES, all_pass=allok), open(f"{K.RUN}/c1/test57_results.json", "w"), indent=1, default=str)
    print("ALL_PASS" if allok else "SOME_FAILED", flush=True)
    sys.exit(0 if allok else 1)


if __name__ == "__main__":
    main()
