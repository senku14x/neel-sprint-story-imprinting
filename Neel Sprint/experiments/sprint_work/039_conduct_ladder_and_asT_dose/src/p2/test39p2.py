"""sw039 Part 2 CPU tests (prep-D agent, E2, 31 Oct 2026; adapted from sw038 test38p1.py). Run on the node CPU (si venv) before any GPU:
  T1 alpha = 1 known answer on the real files, both models, all 61 scripts x both directions: gen39p2's asT_a1 target == sw038
     gen38p1.unit_ops' asT target (max relative diff <= 1e-5), the A rows use sw038's nulls and signs, positions identical.
  T2 edit math on a fake model (64 blocks, H = 48, causal position mixing), one induce and one remove unit (16 arms each) of different
     lengths, left-padded, fp32 and bf16, two-segment k: after every patched layer, dose coordinate = c_rec + alpha (c_don - c_rec);
     A (x_A - x_none).r = s k_L ||x_dose - x_none||; header untouched at L16; hook fires 48x; hook_checks pass; cumulative ratios exist
     for every A arm at both bands; positive controls caught: flipped sign, wrong k, an A clamp's metadata matched to another dose.
  T3 gen39p2 unit builder on CPU with the real contexts, captures and dirs: arm order, A null = NULL_OF_A, sign = dirs38p1's, k = the
     scales' two segments, match = its dose, targets = an independent c_rec + alpha gap from the captures, positions with padding and
     suffix; keys unique; manifest = 16 x units; full manifest size per model 4,880.
  T4 helpers: interp / at; kvec; cum_gate two-sided; per_unit_ratios labels; decide_batch rule; freeze refuses a failing verify;
     degenerate flag.
  T5 check39p2.check on a fake shard built from T2's live logs: complete passes; a missing row, a duplicated row, an extra key and a
     flipped sign each fail.
  /root/venvs/si/bin/python test39p2.py [--skip_real] -> /root/runs/sw039/p2/tests/test39p2_results.json"""
import argparse, json, os, sys, tempfile

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common39p2 as K  # noqa: E402
from hooks39p2 import Hooks38  # noqa: E402

torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "8")))
RES = {}


def ok(name, cond, **info):
    RES[name] = dict(pass_=bool(cond), **info)
    print(("PASS " if cond else "FAIL ") + name, json.dumps(info, default=str)[:400], flush=True)
    return bool(cond)


def unit(v):
    return v / v.norm(dim=-1, keepdim=True)


# ------------------------------------------------------------------------------------------------- T1
def t1():
    import gen39p2 as G
    G.DEV = "cpu"
    for m in K.MODELS:
        G._DEVC.clear()
        ctx, cap, dm = G.load_inputs(m)
        sids = sorted({s for (_, s) in ctx})
        G._G38 = None
        r = G.ka_alpha1(m, ctx, cap, dm, sids)
        ok(f"T1_alpha1_equals_sw038_asT_{m}", r["pass_"], **{k: v for k, v in r.items() if k != "pass_"})
        del ctx, cap, dm


# ------------------------------------------------------------------------------------------------- T2 fake model
class FakeBlock(torch.nn.Module):
    """x -> x + 0.05 * causal mean over earlier positions + 0.1 * tanh(x W): edits propagate to later layers and later positions."""
    def __init__(self, H, g):
        super().__init__(); self.W = torch.randn(H, H, generator=g) / H ** 0.5

    def forward(self, x):
        cm = torch.cumsum(x, 1) / torch.arange(1, x.shape[1] + 1, dtype=x.dtype)[None, :, None]
        return (x + 0.05 * cm + 0.1 * torch.tanh(x @ self.W.to(x.dtype))).to(x.dtype)


SC2 = {d: {a: dict(k1=0.6 + 0.01 * i, k2=0.45 + 0.01 * i, two_segment=True) for i, a in enumerate(K.A_ARMS)} for d in ("induce", "remove")}


def fake_units(H, dtype, m="hdA0", sids=("fake_a", "fake_b"), dirs=("induce", "remove")):
    g = torch.Generator().manual_seed(39)
    u = unit(torch.randn(64, H, generator=g)); A = {nl: unit(torch.randn(64, H, generator=g)) for nl in K.NULLS}
    units, signs, cs = [], {}, {}
    for ui, (n, d) in enumerate(zip((30, 36), dirs)):
        sid = sids[ui]; grp = K.unit_id(m, d, sid, 0); apos0 = list(range(3, 9)) + list(range(12, 17 + ui))
        c_rec = torch.randn(64, generator=g) * 2; c_don = c_rec + 3 + torch.randn(64, generator=g)
        cs[(d, sid)] = (c_rec, c_don)
        signs[f"{d}|{sid}"] = {nl: (-1.0 if (ui + j) % 2 else 1.0) for j, nl in enumerate(K.NULLS)}
        ops = []
        for arm in K.ARMS:
            al = K.ALPHA_OF.get(K.ARM_OF_A.get(arm, arm))
            base = dict(arm=arm, grp=grp, site=K.SITE.get(arm), sample=0, log=True, key=K.row_key("free", m, d, sid, arm, 0), alpha=al)
            if arm == "none":
                ops.append(dict(base, kind="none")); continue
            if arm in K.REAL:
                tgt = (c_rec + al * (c_don - c_rec))[:, None].expand(64, len(apos0)).contiguous()
                ops.append(dict(base, kind="sub", U=u, tgt=tgt, real=True))
            else:
                nl = K.NULL_OF_A[arm]
                ops.append(dict(base, kind="A", U=A[nl], s=signs[f"{d}|{sid}"][nl], k=K.kvec(SC2[d][arm]), match=f"{grp}:{K.ARM_OF_A[arm]}"))
        units.append((ops, n, apos0, d, sid))
    P = 36
    for ops, n, apos0, *_ in units:
        off = P - n; hp = [off + n - 7 + i for i in range(7)]; ap = [off + p for p in apos0]
        for op in ops:
            op["hpos"] = hp
            if op["kind"] != "none":
                op["nh"] = 0; op["pos"] = ap
    rows = [o for u_ in units for o in u_[0]]
    x0 = torch.zeros(len(rows), P, H); r = 0
    for ops, n, *_ in units:
        base = torch.randn(n, H, generator=g) * 2
        for _ in ops:
            x0[r, P - n:] = base; r += 1
    return rows, x0.to(dtype), u, A, units, signs, cs


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


def om_of(rows, flip=None, wrongk=None, wrong_dose=None):
    om = {}
    for o in rows:
        e = dict(kind=o["kind"], s=o.get("s"), k=o.get("k"), match=o.get("match"))
        if o["kind"] == "A":
            if flip and o["arm"] == flip:
                e["s"] = -e["s"]
            if wrongk and o["arm"] == wrongk:
                e["k"] = [1.0] * 64
            if wrong_dose and o["arm"] == wrong_dose[0]:
                e["match"] = o["match"].rsplit(":", 1)[0] + ":" + wrong_dose[1]
        om[(o["grp"], o["arm"])] = e
    return om


def t2():
    for dtype in (torch.float32, torch.bfloat16):
        rows, x0, u, A, units, signs, cs = fake_units(48, dtype)
        after, logs, calls = run_fake(rows, x0, dtype)
        ok(f"T2_calls_{dtype}", calls == 48, calls=calls)
        idx = {(o["grp"], o["arm"]): r for r, o in enumerate(rows)}
        err_sub = err_A = untouched = 0.0
        for r, o in enumerate(rows):
            if o["kind"] == "none":
                continue
            rn = idx[(o["grp"], "none")]; pos = o["pos"]
            d, sid = o["grp"].split("|")[1], o["grp"].split("|")[2]
            for L in range(16, 64):
                X = after[L][r, pos]; Xn = after[L][rn, pos]
                if o["kind"] == "sub":
                    c_rec, c_don = cs[(d, sid)]; tg = float(c_rec[L] + o["alpha"] * (c_don[L] - c_rec[L]))     # independent target
                    e = float(((X @ u[L].float() - tg).abs() / X.norm(dim=-1).clamp_min(1.0)).max()); err_sub = max(err_sub, e)
                else:
                    ra = idx[(o["grp"], K.ARM_OF_A[o["arm"]])]; rv = A[K.NULL_OF_A[o["arm"]]][L].float()
                    want = signs[f"{d}|{sid}"][K.NULL_OF_A[o["arm"]]] * K.kvec(SC2[d][o["arm"]])[L] * (after[L][ra, pos] - Xn).norm(dim=-1)
                    got = (X - Xn) @ rv
                    err_A = max(err_A, float(((got - want).abs() / want.abs().clamp_min(1.0)).max()))
            untouched = max(untouched, float((after[16][r, o["hpos"]] - after[16][rn, o["hpos"]]).abs().max()))
        bar = 1e-5 if dtype == torch.float32 else 0.01
        ok(f"T2_dose_target_{dtype}", err_sub <= bar, max_err_over_state_norm=err_sub)
        ok(f"T2_A_scaled_offset_{dtype}", err_A <= (1e-3 if dtype == torch.float32 else 0.05), max_rel_err=err_A)
        ok(f"T2_header_untouched_L16_{dtype}", untouched == 0.0, max_abs=untouched)
        tol = dict(K.TOL_SW028)
        W = K.hook_checks(logs, om_of(rows), tol)
        ok(f"T2_hook_checks_pass_{dtype}", W["pass"], sub_excess=W["sub_excess"], A_excess=W["A_excess"], n_sub=W["n_sub_asst"], n_A=W["n_A_asst"])
        for nm, om in (("flip_sign_a2_A0", om_of(rows, flip="asT_a2_A0")), ("flip_sign_a0.5_A1", om_of(rows, flip="asT_a0.5_A1")),
                       ("wrong_k_a3_A1", om_of(rows, wrongk="asT_a3_A1")), ("wrong_k_a1_A0", om_of(rows, wrongk="asT_a1_A0")),
                       ("a3_A0_matched_to_a1", om_of(rows, wrong_dose=("asT_a3_A0", "asT_a1")))):
            W2 = K.hook_checks(logs, om, tol)
            ok(f"T2_poscontrol_{nm}_{dtype}", not W2["pass"], A_excess=W2["A_excess"])
        # a wrong target (the dose arm's target computed at alpha = 1 for every dose) must fail the sub check on the logs
        logs_bad = json.loads(json.dumps(logs))
        for e in logs_bad:
            if e["arm"] == "asT_a3":
                e["ka_a"]["err_max"] += 2.0 * abs(e["ka_a"]["gap_min"]) + 5.0
        ok(f"T2_poscontrol_wrong_target_{dtype}", not K.hook_checks(logs_bad, om_of(rows), tol)["pass"])
        per = K.per_unit_ratios(logs)
        ok(f"T2_cum_ratios_exist_{dtype}", all(a in per and all(len(per[a][b]) >= 1 for b in K.GATE_BANDS) for a in K.A_ARMS)
           and all(f"{a}_vs_a1" in per for a in K.REAL if a != "asT_a1"), labels=sorted(per)[:6])
        if dtype == torch.float32:
            # dose ordering sanity: the alpha = 3 arm's offset exceeds the alpha = 0.5 arm's (gap 3 +- 1 >> recipient spread)
            v = K.cum_gate(per)["vs_a1"]
            ok("T2_dose_offsets_ordered", v["asT_a3_vs_a1"]["L16"] > 1.0 > v["asT_a0.5_vs_a1"]["L16"], vs_a1={a: b["L16"] for a, b in v.items()})


# ------------------------------------------------------------------------------------------------- T3 unit builder on real inputs
def t3():
    import gen39p2 as G
    G.DEV = "cpu"; G._DEVC.clear()
    m = "hdB0"
    ctx, cap, dm = G.load_inputs(m)
    C, idx = cap
    sc = {d: {a: dict(k1=0.61, k2=0.47, two_segment=True) for a in K.A_ARMS} for d in ("induce", "remove")}
    sids = sorted({s for (_, s) in ctx})[:3]
    keys, bad = [], []
    suffix = [1, 2, 3]
    for ro in ("free", "fbtw"):
        for d in ("induce", "remove"):
            rec, don = K.DIRS[d][1], K.DIRS[d][2]
            for sid in sids:
                for k in range(K.n_samples(ro, d)):
                    ops, meta = G.unit_ops(ro, m, d, sid, k, ctx, cap, dm, sc[d])
                    if tuple(o["arm"] for o in ops) != K.ARMS:
                        bad.append(("order", d))
                    f = dm["script"][sid]["fold"]; uu = dm["U"][f]["asst"]
                    for o in ops:
                        keys.append(o["key"])
                        if o["kind"] == "A":
                            b = o["arm"]; nl = K.NULL_OF_A[b]
                            if (o["match"] != f"{o['grp']}:{K.ARM_OF_A[b]}" or o["k"] != K.kvec(sc[d][b]) or o["s"] != dm["sign"][f"{d}|{sid}"][nl]
                                    or not torch.allclose(o["U"], unit(dm["A"][f][nl].float()))):
                                bad.append(("A", b))
                            if not (o["k"][16] == 0.61 and o["k"][40] == 0.61 and o["k"][41] == 0.47 and o["k"][63] == 0.47):
                                bad.append(("kvec", o["k"][38:44]))
                        if o["kind"] == "sub":
                            for L in (16, 28, 40, 52, 63):
                                uL = uu[L].float() / uu[L].float().norm()
                                cr = float(C["asst_mean"][idx[f"{rec}|{sid}"]][L].float() @ uL)
                                cd = float(C["asst_mean"][idx[f"{don}|{sid}"]][L].float() @ uL)
                                want = cr + o["alpha"] * (cd - cr)
                                if o["tgt"].shape[1] != len(ctx[(rec, sid)]["apos"]) or float((o["tgt"][L] - want).abs().max()) > 1e-3 * max(1.0, abs(want)):
                                    bad.append(("tgt", o["arm"], L))
                    ids = ctx[(rec, sid)]["ids"]; P = len(ids) + 40
                    G.set_pos(ops, P, len(ids), len(suffix), ctx[(rec, sid)]["apos"])
                    row = [G.PAD] * (P - len(ids) - len(suffix)) + ids + suffix
                    want_ap = [p + P - len(ids) - len(suffix) for p in K.asst_positions(ids, K.last_user_start(ids))]
                    for o in ops:
                        if [row[p] for p in o["hpos"]] != G.HEADER:
                            bad.append(("hpos", o["arm"]))
                        if o["kind"] != "none" and o["pos"] != want_ap:
                            bad.append(("apos", o["arm"]))
    ok("T3_unit_builder", not bad, n_bad=len(bad), head=bad[:5])
    ok("T3_keys_unique", len(keys) == len(set(keys)), n=len(keys))
    exp = K.expected_keys(["free", "fbtw"], [m], sids, ["induce", "remove"])
    ok("T3_manifest_matches_builder", sorted(exp) == sorted(keys) and len(exp) == 3 * 16 * (2 + 1 + 1 + 1), n=len(exp))
    full = K.expected_keys(["free", "fbtw"], [m], sorted({s for (_, s) in ctx}), ["induce", "remove"])
    ok("T3_full_manifest_size", len(full) == len(set(full)) == 4880, n=len(full))
    ok("T3_smoke_keys_disjoint", not set(K.expected_keys(["free"], [m], sids, ["induce"], samples=1, part="p2smoke")) & set(full))
    ok("T3_nulls_orthogonal_to_asT", max(float((unit(dm["A"][f][nl].float()) * unit(dm["U"][f]["asst"].float())).sum(-1)[16:].abs().max())
                                         for f in dm["A"] for nl in K.NULLS) < 1e-3)


# ------------------------------------------------------------------------------------------------- T4 helpers
def t4():
    import gen39p2 as G
    import decide_batch39p2 as DB
    c = [(0.2, 0.36), (0.4, 0.72), (0.6, 1.08), (0.8, 1.44)]
    k, ex = G.interp(c, 1.0)
    ok("T4_interp_linear", abs(k - (0.4 + 0.2 * (1.0 - 0.72) / 0.36)) < 1e-9 and not ex, k=k)
    k2, ex2 = G.interp(c, 2.0)
    ok("T4_interp_extrapolated_flag", ex2 and k2 > 0.8, k=k2)
    ok("T4_at", abs(G.at(c, 0.5) - 0.9) < 1e-9)
    kv = K.kvec(dict(k1=0.7, k2=0.5))
    ok("T4_kvec", kv[16] == 0.7 and kv[40] == 0.7 and kv[41] == 0.5 and kv[63] == 0.5 and len(kv) == 64)
    mk = lambda v: {b: {f"u{i}": v for i in range(5)} for b in K.GATE_BANDS}
    for v, want in ((0.85, False), (1.15, False), (1.0, True), (0.9, True), (1.1, True)):
        per = {a: mk(v if a == "asT_a3_A1" else 1.0) for a in K.A_ARMS}
        ok(f"T4_cum_gate_{v}", K.cum_gate(per)["pass_"] == want)
    per = {a: mk(1.0) for a in K.A_ARMS if a != "asT_a1_A1"}
    ok("T4_cum_gate_missing_arm_fails", not K.cum_gate(per)["pass_"])
    ok("T4_arms", len(K.ARMS) == 16 and K.ARMS.index("asT_a3") < K.ARMS.index("asT_a0.5_A0") and K.NULL_OF_A["asT_a2_A1"] == "asT_A1"
       and K.ALPHA_OF["asT_a1.5"] == 1.5 and K.DOSE_ARM[1.0] == "asT_a1")
    P = dict(total_gib=79.18, probes=[dict(readout="free", units=3, oom=False, all_at_max=True, peak_reserved_gib=75.0),
                                      dict(readout="fbtw", units=4, oom=False, all_at_max=True, peak_reserved_gib=70.0)])
    ok("T4_batch_fit", DB.decide(P)["free_units"] == 3 and DB.decide(P)["forced_units"] == 4)
    P["probes"][0]["peak_reserved_gib"] = 78.0; P["probes"][1] = dict(readout="fbtw", units=4, oom=True)
    ok("T4_batch_fallback", DB.decide(P)["free_units"] == 2 and DB.decide(P)["forced_units"] == 3)
    ok("T4_degenerate", K.degenerate(" ".join(["the bee is on the hive"] * 30)) and not K.degenerate(" ".join(f"w{i}" for i in range(200))))
    # freeze refuses a failing verify
    import subprocess
    tmp = tempfile.mkdtemp()
    gate = lambda v: dict(pass_=v == 1.0, fail=[] if v == 1.0 else ["asT_a3_A0"], missing=[], vs_a1={},
                          arms={a: dict(median_ratio={b: (v if a == "asT_a3_A0" else 1.0) for b in K.GATE_BANDS}) for a in K.A_ARMS})
    for v, want in ((1.0, 0), (1.2, 1)):
        json.dump(dict(pass_=v == 1.0, **{"pass": v == 1.0}, directions={d: dict(verify=dict(gate=gate(v))) for d in ("induce", "remove")}),
                  open(f"{tmp}/cal_hdA0.json", "w"))
        json.dump(dict(verify_pass=v == 1.0, scales={d: {a: dict(k1=0.6, k2=0.5, two_segment=True) for a in K.A_ARMS} for d in ("induce", "remove")}),
                  open(f"{tmp}/scales_proposal_hdA0.json", "w"))
        rc = subprocess.run([sys.executable, f"{HERE}/freeze_scales39p2.py", tmp, "hdA0", f"{tmp}/frozen.json"], capture_output=True).returncode
        ok(f"T4_freeze_{'accepts' if v == 1.0 else 'refuses'}_{v}", (rc == 0) == (want == 0), rc=rc)


# ------------------------------------------------------------------------------------------------- T5 output gates on a fake shard
def t5():
    import check39p2 as CH
    sids = ["fake_a", "fake_b"]
    for d in ("induce", "remove"):
        R, LG, sg = [], [], {}
        for sid in sids:
            rows, x0, u, A, units, signs, cs = fake_units(48, torch.float32, sids=(sid, sid + "_x"), dirs=(d, d))
            rows = [o for o in rows if o["grp"].split("|")[2] == sid]
            x0 = x0[:len(rows)]
            after, logs, _ = run_fake(rows, x0, torch.float32)
            LG += [dict(readout="free", **e) for e in logs]
            sg[f"{d}|{sid}"] = signs[f"{d}|{sid}"]
            R += [dict(key=o["key"], arm=o["arm"], alpha=o["alpha"], text="hello there, a reply", finish="stop") for o in rows]
        tmp = tempfile.mkdtemp(); os.makedirs(f"{tmp}/free")

        def write(rr):
            with open(f"{tmp}/free/free_hdA0_{d}.jsonl", "w") as f:
                f.write("".join(json.dumps(r) + "\n" for r in rr))
            with open(f"{tmp}/free/log_free_hdA0_{d}.jsonl", "w") as f:
                f.write("".join(json.dumps(e) + "\n" for e in LG))
        tol = dict(K.TOL_SW028)
        args = lambda sgx: (tmp, "hdA0", [d], ["free"], sids, 1, sgx, SC2, tol, "p2")
        write(R); res, good, _ = CH.check(*args(sg), cum_report_only=True)
        ok(f"T5_complete_passes_{d}", good, detail={k: v for k, v in res[f"free|{d}"].items() if k in ("missing", "extra", "logs_missing", "nonempty")})
        write(R[:-1]); _, bad1, _ = CH.check(*args(sg), cum_report_only=True)
        write(R + R[:1]); _, bad2, _ = CH.check(*args(sg), cum_report_only=True)
        write(R + [dict(R[0], key=R[0]["key"].replace("|s0", "|s7"))]); _, bad3, _ = CH.check(*args(sg), cum_report_only=True)
        write(R); sg2 = json.loads(json.dumps(sg)); sg2[f"{d}|fake_a"]["asT_A1"] *= -1
        _, bad4, _ = CH.check(*args(sg2), cum_report_only=True)
        ok(f"T5_poscontrols_fail_{d}", not (bad1 or bad2 or bad3 or bad4), missing=bad1, dup=bad2, extra=bad3, flipped=bad4)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--skip_real", action="store_true")
    ap.add_argument("--out", default="/root/runs/sw039/p2/tests/test39p2_results.json")
    a = ap.parse_args()
    if not a.skip_real:
        t1()
    t2()
    if not a.skip_real:
        t3()
    t4(); t5()
    n = len(RES); npass = sum(v["pass_"] for v in RES.values())
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(dict(n=n, n_pass=npass, all_pass=npass == n, results=RES), open(a.out, "w"), indent=1, default=str)
    print(f"{'ALL_PASS' if npass == n else 'SOME_FAIL'} {npass}/{n}", a.out, flush=True)
    sys.exit(0 if npass == n else 1)


if __name__ == "__main__":
    main()
