"""sw038 Part 1 CPU tests (prep-P1 agent, E2, 31 Oct 2026). Run on the node CPU (si venv) before the GPU calibration / smoke:
  T1 fitting and inputs on the real files: dirs38p1.fit on the new captures reproduces dirs38p1's r1 / asst / c1 (cos >= 0.99999,
     every fold, L16-63); A nulls unit and orthogonal to span(u_arm, u_r1) (< 1e-4) with a non-zero raw overlap (positive control);
     signs recomputed for every script and A arm; sk_map = same domain, never itself, a bijection within each domain; held-out domain
     outside every fit set; nulls seeded (same seed -> same draw).
  T2 edit math on a fake model (64 blocks, H = 48, causal position mixing), one induce unit (11 arms) and one remove unit (12 arms,
     with skF) of different lengths, left-padded, fp32 and bf16, two-segment k (k1 0.6 at L16-40, k2 0.45 at L41-63): after every
     patched layer, sub coordinate = target; A (x_A - x_none).r = s k_L ||x_arm - x_none||; skF header = the donor tensor exactly;
     untouched positions at L16; hook_checks pass and cumulative ratios exist for every A arm at both bands; positive controls: a
     flipped sign, a wrong k (single 1.0) and a c1 clamp matched to r1 in the metadata are caught.
  T3 gen38p1 unit builder on CPU with the real contexts, captures and dirs: arm order, real rows before A, A match = its arm, k =
     the scales file's two segments, sub targets = D . u (header, per token) and asst_mean_donor . u (Assistant), skF donor = sk_map
     and its tensor = the capture's L16-63 header, positions = header / sw006 asst_positions shifted by padding and suffix; keys
     unique across units, samples, readouts and directions; manifest size = 11 x induce units + 12 x remove units.
  T4 helpers: interp / at on linear and kinked curves; kvec; cum_gate two-sided ([0.9, 1.1]: 0.85 and 1.15 fail, 1.0 passes, a
     missing arm fails); per_unit_ratios needs every band layer.
  T5 check38p1.check on a fake shard built from T2's live logs: complete -> pass; a missing row, a duplicated row, an extra key and a
     flipped sign each -> fail.
  /root/venvs/si/bin/python test38p1.py [--skip_t1_t3]  -> /root/runs/sw038/p1/test38p1_results.json"""
import argparse, json, os, sys, tempfile

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common38p1 as K  # noqa: E402
import dirs38p1 as DX  # noqa: E402
from hooks38p1 import Hooks38  # noqa: E402

torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "8")))
RES = {}
RUN = "/root/runs/sw038/p1"


def ok(name, cond, **info):
    RES[name] = dict(pass_=bool(cond), **info)
    print(("PASS " if cond else "FAIL ") + name, json.dumps(info, default=str)[:400], flush=True)
    return bool(cond)


# ------------------------------------------------------------------------------------------------- T1
def t1():
    FO = json.load(open(f"{RUN}/inputs/folds38p1.json")); folds = FO["folds"]; dom_of = FO["dom_of"]; sids = sorted(dom_of)
    CC = torch.load(f"{DX.CAPS}/cap_ctrlB0.pt", weights_only=False); ic = {k: i for i, k in enumerate(CC["keys"])}
    for m in K.MODELS:
        C = torch.load(f"{DX.CAPS}/cap_{m}.pt", weights_only=False); idx = {k: i for i, k in enumerate(C["keys"])}
        dm = torch.load(f"{RUN}/dirs/dirs38p1_{m}.pt", weights_only=False)
        worst, orth, raw_ov, sgn_bad = 1.0, 0.0, 0.0, 0
        for f, v in folds.items():
            fs = v["fit_sids"]
            assert not set(fs) & {s for s in sids if dom_of[s] == f}
            for fam, CX, ix, fld in (("r1", C, idx, "hdr_mean"), ("asst", C, idx, "asst_mean"), ("c1", CC, ic, "hdr_mean")):
                u = DX.unit(DX.fit(CX, ix, fs, fld)); worst = min(worst, float((u * dm["U"][f][fam]).sum(-1)[16:].min()))
            for a in K.A_ARMS:
                r = dm["A"][f][a]; ua = dm["U"][f][K.FAMILY[K.ARM_OF_A[a]]]
                orth = max(orth, float((r * dm["U"][f]["r1"]).sum(-1)[16:].abs().max()), float((r * ua).sum(-1)[16:].abs().max()),
                           float((r.norm(dim=-1)[16:] - 1).abs().max()))
            for s in v["held_out"]:
                for d, rec, don in K.DIRECTIONS:
                    gh = (C["hdr"][idx[f"{don}|{s}"]][:, 16].float() - C["hdr"][idx[f"{rec}|{s}"]][:, 16].float()).mean(0)
                    ga = C["asst_mean"][idx[f"{don}|{s}"]][16].float() - C["asst_mean"][idx[f"{rec}|{s}"]][16].float()
                    for a in K.A_ARMS:
                        g = gh if K.SITE[a] == "hdr" else ga
                        sgn_bad += int((1.0 if float(g @ dm["A"][f][a][16]) >= 0 else -1.0) != dm["sign"][f"{d}|{s}"][a])
        ok(f"T1_refit_{m}", worst >= 0.99999, min_cos=worst)
        ok(f"T1_nulls_orth_unit_{m}", orth < 1e-4, max_dev=orth)
        ok(f"T1_signs_{m}", sgn_bad == 0, n_bad=sgn_bad, n=len(sids) * 2 * len(K.A_ARMS))
        ov = [x["raw_abs_cos_arm_max"] for a in K.A_ARMS for x in json.load(open(f"{RUN}/dirs/dirs38p1_summary.json"))["raw_null_overlap"][m][a]]
        ok(f"T1_raw_overlap_positive_{m}", min(ov) > 1e-3, min_raw_overlap=min(ov))
        skm = dm["sk_map"]
        by = {}
        for s, t in skm.items():
            by.setdefault(dom_of[s], []).append(t)
        ok(f"T1_skmap_{m}", skm == K.sk_map(dom_of) and all(skm[s] != s and dom_of[skm[s]] == dom_of[s] for s in sids)
           and all(len(set(v)) == len(v) for v in by.values()), n=len(skm))
    X1 = torch.randn(30, 64, 48); X2 = torch.randn(30, 64, 48) + 0.5
    ok("T1_nulls_seeded", torch.equal(DX.null_draws([X1, X2], 2, 7), DX.null_draws([X1, X2], 2, 7)))


# ------------------------------------------------------------------------------------------------- T2 fake model
class FakeBlock(torch.nn.Module):
    """x -> x + 0.05 * causal mean over earlier positions + 0.1 * tanh(x W): edits propagate to later layers and later positions."""
    def __init__(self, H, g):
        super().__init__(); self.W = torch.randn(H, H, generator=g) / H ** 0.5

    def forward(self, x):
        cm = torch.cumsum(x, 1) / torch.arange(1, x.shape[1] + 1, dtype=x.dtype)[None, :, None]
        return (x + 0.05 * cm + 0.1 * torch.tanh(x @ self.W.to(x.dtype))).to(x.dtype)


SC2 = {d: {a: dict(k1=0.6, k2=0.45, two_segment=True) for a in K.A_ARMS} for d in ("induce", "remove")}


def fake_units(H, dtype, m="hdA0", sids=("fake_a", "fake_b")):
    g = torch.Generator().manual_seed(38)
    unitv = lambda: DX.unit(torch.randn(64, H, generator=g))
    U = {f: unitv() for f in ("r1", "asst", "c1")}; A = {a: unitv() for a in K.A_ARMS}
    units, signs = [], {}
    for ui, (n, d) in enumerate(((30, "induce"), (36, "remove"))):
        sid = sids[ui]; grp = K.unit_id(m, d, sid, 0); apos0 = list(range(3, 9)) + list(range(12, 17 + ui))
        Dh = torch.randn(7, 64, H, generator=g) * 3; Da = torch.randn(64, H, generator=g) * 3
        Df = (torch.randn(7, 48, H, generator=g) * 2).to(dtype)
        signs[f"{d}|{sid}"] = {a: (-1.0 if (ui + K.A_ARMS.index(a)) % 2 else 1.0) for a in K.A_ARMS}
        ops = []
        for arm in K.arms_of(d):
            base = dict(arm=arm, grp=grp, site=K.SITE.get(arm), sample=0, log=True, key=K.row_key("free", m, d, sid, arm, 0))
            if arm == "none":
                ops.append(dict(base, kind="none")); continue
            if arm in K.REAL:
                u = U[K.FAMILY[arm]]
                tgt = torch.einsum("tlh,lh->lt", Dh, u) if K.SITE[arm] == "hdr" else (Da * u).sum(-1)[:, None].expand(64, len(apos0))
                ops.append(dict(base, kind="sub", U=u, tgt=tgt.contiguous(), real=True))
            elif arm == "skF":
                ops.append(dict(base, kind="full", Dfull=Df))
            else:
                ops.append(dict(base, kind="A", U=A[arm], s=signs[f"{d}|{sid}"][arm], k=K.kvec(SC2[d][arm]), match=f"{grp}:{K.ARM_OF_A[arm]}"))
        units.append((ops, n, apos0, Dh, Da, Df, d, sid))
    P = 36
    for ops, n, apos0, *_ in units:
        off = P - n; hp = [off + n - 7 + i for i in range(7)]; ap = [off + p for p in apos0]
        for op in ops:
            op["hpos"] = hp
            if op["kind"] != "none":
                op["nh"] = 7 if op["site"] == "hdr" else 0; op["pos"] = hp if op["site"] == "hdr" else ap
    rows = [o for u in units for o in u[0]]
    x0 = torch.zeros(len(rows), P, H); r = 0
    for ops, n, *_ in units:
        base = torch.randn(n, H, generator=g) * 2
        for _ in ops:
            x0[r, P - n:] = base; r += 1
    return rows, x0.to(dtype), U, A, units, signs


def run_fake(rows, x0, dtype):
    gb = torch.Generator().manual_seed(5)
    blocks = torch.nn.ModuleList([FakeBlock(x0.shape[-1], gb) for _ in range(64)]).to(dtype)
    hk = Hooks38(blocks); after = {}
    hs = [b.register_forward_hook((lambda L: lambda mod, i, o: after.__setitem__(L, o.detach().float().clone()))(L)) for L, b in enumerate(blocks)]
    hk.ops = rows; hk.mode = "patch"; hk.min_len = x0.shape[1]; hk.log = []
    x = x0
    with torch.no_grad():
        for b in blocks:
            x = b(x)
    for h in hs:
        h.remove()
    hk.remove()
    return after, hk.log, hk.calls


def om_of(rows, flip=None, wrongk=None, c1_to_r1=False):
    om = {}
    for o in rows:
        e = dict(kind=o["kind"], s=o.get("s"), k=o.get("k"), match=o.get("match"))
        if o["kind"] == "A":
            if flip and o["arm"] == flip:
                e["s"] = -e["s"]
            if wrongk and o["arm"] == wrongk:
                e["k"] = [1.0] * 64
            if c1_to_r1 and o["arm"] == "c1_A0":
                e["match"] = o["match"].rsplit(":", 1)[0] + ":r1"
        om[(o["grp"], o["arm"])] = e
    return om


def t2():
    for dtype, tol_c in ((torch.float32, 1e-3), (torch.bfloat16, None)):
        rows, x0, U, A, units, signs = fake_units(48, dtype)
        after, logs, calls = run_fake(rows, x0, dtype)
        ok(f"T2_calls_{dtype}", calls == 48, calls=calls)
        idx = {(o["grp"], o["arm"]): r for r, o in enumerate(rows)}
        err_sub = err_A = err_full = untouched = 0.0
        for r, o in enumerate(rows):
            if o["kind"] == "none":
                continue
            rn = idx[(o["grp"], "none")]; pos = o["pos"]
            for L in range(16, 64):
                X = after[L][r, pos]; Xn = after[L][rn, pos]
                if o["kind"] == "sub":
                    # error relative to the state norm: bf16 write-back rounds each element at ~2^-8 of its size
                    u = o["U"][L].float(); tg = o["tgt"][L]
                    e = float(((X @ u - tg).abs() / X.norm(dim=-1).clamp_min(1.0)).max()); err_sub = max(err_sub, e)
                elif o["kind"] == "A":
                    ra = idx[(o["grp"], K.ARM_OF_A[o["arm"]])]; rv = o["U"][L].float()
                    want = o["s"] * o["k"][L] * (after[L][ra, pos] - Xn).norm(dim=-1); got = (X - Xn) @ rv
                    err_A = max(err_A, float(((got - want).abs() / want.abs().clamp_min(1.0)).max()))
                else:
                    err_full = max(err_full, float((X - o["Dfull"][:, L - 16].float()).abs().max()))
            # untouched at L16: header arms leave the Assistant tokens alone; asT leaves the header alone
            for u_ in units:
                if u_[0][0]["grp"] == o["grp"]:
                    P = x0.shape[1]; off = P - u_[1]; apos = [off + p for p in u_[2]]
                    un = apos if o["site"] == "hdr" else o["hpos"]
                    untouched = max(untouched, float((after[16][r, un] - after[16][rn, un]).abs().max()))
        bar = 1e-5 if dtype == torch.float32 else 0.01
        ok(f"T2_sub_target_{dtype}", err_sub <= bar, max_err_over_state_norm=err_sub)
        ok(f"T2_A_scaled_offset_{dtype}", err_A <= (1e-3 if dtype == torch.float32 else 0.05), max_rel_err=err_A)
        ok(f"T2_skF_exact_{dtype}", err_full == 0.0, max_abs=err_full)
        ok(f"T2_untouched_L16_{dtype}", untouched == 0.0, max_abs=untouched)
        tol = dict(K.TOL_SW028)
        W = K.hook_checks(logs, om_of(rows), tol)
        ok(f"T2_hook_checks_pass_{dtype}", W["pass"], sub_excess=W["sub_excess"], A_excess=W["A_excess"], n_sub=W["n_sub"], n_A=W["n_A"],
           n_sub_asst=W["n_sub_asst"], n_A_asst=W["n_A_asst"], n_full=W["n_full"])
        for nm, om in (("flip_sign_r1_A0", om_of(rows, flip="r1_A0")), ("flip_sign_asT_A1", om_of(rows, flip="asT_A1")),
                       ("wrong_k_c1_A1", om_of(rows, wrongk="c1_A1")), ("wrong_k_asT_A0", om_of(rows, wrongk="asT_A0")),
                       ("c1_A0_matched_to_r1", om_of(rows, c1_to_r1=True))):
            W2 = K.hook_checks(logs, om, tol)
            ok(f"T2_poscontrol_{nm}_{dtype}", not W2["pass"], A_excess=W2["A_excess"])
        per = K.per_unit_ratios(logs)
        ok(f"T2_cum_ratios_exist_{dtype}", all(a in per and all(len(per[a][b]) >= 1 for b in K.GATE_BANDS) for a in K.A_ARMS)
           and "skF_vs_r1" in per and "c1_vs_r1" in per, labels=sorted(per))
    return units


# ------------------------------------------------------------------------------------------------- T3 unit builder
def t3():
    import gen38p1 as G
    G.DEV = "cpu"
    ctx, cap, dm = G.load_inputs("hdB0", f"{RUN}/dirs", DX.CAPS)
    C, idx = cap
    sc = {d: {a: dict(k1=0.61, k2=0.47, two_segment=True) for a in K.A_ARMS} for d in ("induce", "remove")}
    sids = sorted({s for (_, s) in ctx})[:3]
    keys, n_rows, bad = [], 0, []
    suffix = [1, 2, 3]
    for ro in ("free", "fbtw"):
        for d in ("induce", "remove"):
            for sid in sids:
                for k in range(K.n_samples(ro, d)):
                    ops, meta = G.unit_ops(ro, "hdB0", d, sid, k, ctx, cap, dm, sc[d])
                    arms = [o["arm"] for o in ops]
                    if tuple(arms) != K.arms_of(d):
                        bad.append(("order", d, arms))
                    rec, don = K.DIRS[d][1], K.DIRS[d][2]
                    for o in ops:
                        keys.append(o["key"]); n_rows += 1
                        if o["kind"] == "A":
                            b = o["arm"]
                            if o["match"] != f"{o['grp']}:{K.ARM_OF_A[b]}" or o["k"] != K.kvec(sc[d][b]) or o["s"] != dm["sign"][f"{d}|{sid}"][b]:
                                bad.append(("A", o["arm"]))
                            if not (o["k"][16] == 0.61 and o["k"][40] == 0.61 and o["k"][41] == 0.47 and o["k"][63] == 0.47):
                                bad.append(("kvec", o["k"][38:44]))
                        if o["kind"] == "sub":
                            u = dm["U"][meta["domain"]][K.FAMILY[o["arm"]]]
                            for L in (16, 40, 63):
                                if K.SITE[o["arm"]] == "hdr":
                                    want = C["hdr"][idx[f"{don}|{sid}"]][:, L].float() @ (u[L] / u[L].norm())
                                    if float((o["tgt"][L] - want).abs().max()) > 1e-3:
                                        bad.append(("tgt_hdr", o["arm"], L))
                                else:
                                    want = float(C["asst_mean"][idx[f"{don}|{sid}"]][L].float() @ (u[L] / u[L].norm()))
                                    if o["tgt"].shape[1] != len(ctx[(rec, sid)]["apos"]) or float((o["tgt"][L] - want).abs().max()) > 1e-3:
                                        bad.append(("tgt_asst", o["arm"], L))
                        if o["kind"] == "full":
                            dn = dm["sk_map"][sid]
                            if o["sk_donor"] != dn or not torch.equal(o["Dfull"], C["hdr"][idx[f"self-hostile|{dn}"]][:, 16:64]):
                                bad.append(("skF", sid))
                    # positions with padding and suffix
                    ids = ctx[(rec, sid)]["ids"]; P = len(ids) + 40
                    G.set_pos(ops, P, len(ids), len(suffix), ctx[(rec, sid)]["apos"])
                    row = [G.PAD] * (P - len(ids) - len(suffix)) + ids + suffix
                    for o in ops:
                        if [row[p] for p in o["hpos"]] != G.HEADER:
                            bad.append(("hpos", o["arm"]))
                        if o["kind"] != "none" and o["site"] == "asst":
                            want = [p + P - len(ids) - len(suffix) for p in K.asst_positions(ids, K.last_user_start(ids))]
                            if o["pos"] != want:
                                bad.append(("apos", o["arm"]))
    ok("T3_unit_builder", not bad, n_bad=len(bad), head=bad[:5])
    ok("T3_keys_unique", len(keys) == len(set(keys)), n=len(keys))
    exp = K.expected_keys(["free", "fbtw"], ["hdB0"], sids, ["induce", "remove"])
    ok("T3_manifest_matches_builder", sorted(exp) == sorted(keys) and len(exp) == 3 * (2 * 11 + 1 * 12 + 11 + 12), n=len(exp))
    full = K.expected_keys(["free", "fbtw"], list(K.MODELS), sorted({s for (_, s) in ctx}), ["induce", "remove"])
    ok("T3_full_manifest_size", len(full) == len(set(full)) == 2 * 61 * (2 * 11 + 12 + 11 + 12), n=len(full))


# ------------------------------------------------------------------------------------------------- T4 helpers
def t4():
    import gen38p1 as G
    c = [(0.2, 0.36), (0.4, 0.72), (0.6, 1.08), (0.8, 1.44)]
    k, ex = G.interp(c, 1.0)
    ok("T4_interp_linear", abs(k - (0.4 + 0.2 * (1.0 - 0.72) / 0.36)) < 1e-9 and not ex, k=k)
    k2, ex2 = G.interp(c, 2.0)
    ok("T4_interp_extrapolated_flag", ex2 and k2 > 0.8, k=k2)
    ok("T4_at", abs(G.at(c, 0.5) - 0.9) < 1e-9 and abs(G.at(c, 0.2) - 0.36) < 1e-9)
    kv = K.kvec(dict(k1=0.7, k2=0.5))
    ok("T4_kvec", kv[16] == 0.7 and kv[40] == 0.7 and kv[41] == 0.5 and kv[63] == 0.5 and len(kv) == 64)
    mk = lambda v: {b: {f"u{i}": v for i in range(5)} for b in K.GATE_BANDS}
    for v, want in ((0.85, False), (1.15, False), (1.0, True), (0.9, True), (1.1, True)):
        per = {a: mk(v if a == "r1_A1" else 1.0) for a in K.A_ARMS}
        ok(f"T4_cum_gate_{v}", K.cum_gate(per)["pass_"] == want)
    per = {a: mk(1.0) for a in K.A_ARMS if a != "c1_A1"}
    ok("T4_cum_gate_missing_arm_fails", not K.cum_gate(per)["pass_"])
    logs = [dict(grp="g", L=L, arm=a, off_h=[1.0] * 7, off_a=1.0) for L in (28, 32, 36) for a in ("r1", "r1_A0")]
    ok("T4_ratio_needs_every_band_layer", "L28-40" not in K.per_unit_ratios(logs).get("r1_A0", {}))


# ------------------------------------------------------------------------------------------------- T5 output gates on a fake shard
def t5():
    import check38p1 as CH
    for d in ("induce", "remove"):
        sids = ["fake_a", "fake_b"]
        rows, x0, U, A, units, signs = fake_units(48, torch.float32, sids=sids)
        after, logs, _ = run_fake(rows, x0, torch.float32)
        # the fake has one unit per direction: relabel both units as direction d (rows / logs regenerated per sid)
        R, LG, sg = [], [], {}
        for sid in sids:
            rows2, x02, *_ , signs2 = fake_units(48, torch.float32, sids=(sid, sid))
            u_d = [o for o in rows2 if o["grp"].split("|")[1] == d]
            after2, logs2, _ = run_fake(rows2, x02, torch.float32)
            LG += [dict(readout="free", **e) for e in logs2 if e["grp"].split("|")[1] == d]
            sg[f"{d}|{sid}"] = signs2[f"{d}|{sid}"]
            R += [dict(key=o["key"], arm=o["arm"], text="hello there, a reply", finish="stop") for o in u_d]
        tmp = tempfile.mkdtemp(); os.makedirs(f"{tmp}/free")
        def write(rr):
            with open(f"{tmp}/free/free_hdA0_{d}.jsonl", "w") as f:
                f.write("".join(json.dumps(r) + "\n" for r in rr))
            with open(f"{tmp}/free/log_free_hdA0_{d}.jsonl", "w") as f:
                f.write("".join(json.dumps(e) + "\n" for e in LG))
        tol = dict(K.TOL_SW028)
        write(R); _, good, _ = CH.check(tmp, "hdA0", d, ["free"], sids, 1, sg, SC2, tol, cum_report_only=True)
        ok(f"T5_complete_passes_{d}", good)
        write(R[:-1]); _, bad1, _ = CH.check(tmp, "hdA0", d, ["free"], sids, 1, sg, SC2, tol, cum_report_only=True)
        write(R + R[:1]); _, bad2, _ = CH.check(tmp, "hdA0", d, ["free"], sids, 1, sg, SC2, tol, cum_report_only=True)
        write(R + [dict(R[0], key=R[0]["key"].replace("|s0", "|s7"))]); _, bad3, _ = CH.check(tmp, "hdA0", d, ["free"], sids, 1, sg, SC2, tol, cum_report_only=True)
        write(R); sg2 = json.loads(json.dumps(sg)); sg2[f"{d}|fake_a"]["r1_A2"] *= -1
        _, bad4, _ = CH.check(tmp, "hdA0", d, ["free"], sids, 1, sg2, SC2, tol, cum_report_only=True)
        ok(f"T5_poscontrols_fail_{d}", not (bad1 or bad2 or bad3 or bad4), missing=bad1, dup=bad2, extra=bad3, flipped=bad4)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--skip_t1_t3", action="store_true"); ap.add_argument("--out", default=f"{RUN}/test38p1_results.json")
    a = ap.parse_args()
    if not a.skip_t1_t3:
        t1()
    t2(); t4(); t5()
    if not a.skip_t1_t3:
        t3()
    n_ok = sum(v["pass_"] for v in RES.values())
    out = dict(all_pass=bool(n_ok == len(RES)), n_pass=n_ok, n=len(RES), results=RES)
    os.makedirs(os.path.dirname(a.out), exist_ok=True); json.dump(out, open(a.out, "w"), indent=1, default=str)
    print("ALL_PASS" if out["all_pass"] else "SOME_FAIL", f"{n_ok}/{len(RES)}", flush=True)
    sys.exit(0 if out["all_pass"] else 1)


if __name__ == "__main__":
    main()
