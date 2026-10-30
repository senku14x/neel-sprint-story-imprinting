"""sw028 CPU known-answer tests (executor-9 overnight, 30 Oct 2026). Exit non-zero on any failure.
 T1 keys: free / forced keys from gen28's group builder are unique, carry exp/readout/model/direction/script/arm/sample, and equal
    analyze28's manifest (5,120 per readout); l16 keys unique (1,536).
 T2 directions (dirs28 vs sw012 / captures): P_i = sw012's cova/covb/covc orthogonalised to the u in use (cos >= 0.9999 at L16-63);
    A_i orthogonal to u; the held-out script is not in its fold's fit set; sigma_P and s_A recomputed from the captures agree.
 T3 synthetic known answers (H = 32, identity blocks, constant u = e0, r = e1; donor coordinate along u rises 0.5 per layer):
    r1 sets the u-coordinate to the donor's at every layer; P's push norm = r1's at every layer and token, its sign is sigma at
    every layer, and its offset along r = sigma * sum of r1's pushes (5 + 0.5 x 47 = 28.5); sw012's live-sign R7 (Hooks12, same
    setup) stays within one push of the start (it cancels itself); A's offset along r = s * ||x_r1 - x_none|| at every layer;
    Z's = s * zoff; d16 / q edit only at L16; nothing changes below L16, in the none row, or in a 1-token decode step; a
    control placed before its real row raises.
 T4 real wiring (H = 5120, gen28.group_ops on the real dirs28 + sw009 captures, 64 low-rank drift blocks, fp32 and bf16):
    hook_checks passes (P sign kept and |push| = r1's; A along = s * r1 offset; Z along = s * zoff); cum_gate: every A arm
    reaches >= 0.9 of r1's cumulative offset. Positive controls for the checks themselves: a flipped sigma is caught, an A
    clamp at half the target fails the 0.9 gate.
 T5 dirs28 natural units: nat_stats / zoff_from recover known gaps and SDs of synthetic Gaussian projections; saved zoff = k * sd_A.
 T6 manifest completion: analyze28 prep on a partial synthetic run dir exits 2; a complete one passes.
  OMP_NUM_THREADS=8 /root/venvs/si/bin/python test28_x.py"""
import json, os, subprocess, sys, tempfile

import torch
import torch.nn as nn

torch.set_num_threads(8)
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import hooks28 as HK  # noqa: E402
import gen28_x as G  # noqa: E402
import dirs28_x as DR  # noqa: E402
import analyze28_x as A  # noqa: E402

G.DEV = "cpu"
fails = []


def check(name, cond, info=""):
    print(("PASS " if cond else "FAIL ") + name, info, flush=True)
    if not cond:
        fails.append(name)


def raises(fn):
    try:
        fn()
    except AssertionError:
        return True
    return False


# ---------------------------------------------------------------- T1 + T2
ctx, caps, dirs = G.load_inputs(("hdA0", "hdB0"))
sids = sorted({s for (_, s) in ctx})
check("T1 64 scripts", len(sids) == 64)
keys = {"free": [], "forced": [], "l16": []}
d12 = {m: torch.load(f"/workspace/runs_executor/sw012/dirs12_{m}.pt", weights_only=False) for m in ("hdA0", "hdB0")}
C9 = {m: caps[m] for m in caps}
t2 = dict(P_cos_min=1.0, A_cos_max=0.0, fold_ok=True, sign_ok=True)
for m in ("hdA0", "hdB0"):
    for sid in sids:
        sc = dirs[m]["script"][sid]["scenario"]; S = dirs[m]["scen"][sc]
        t2["fold_ok"] &= sid in S["held_out"] and sid not in S["fit_sids"]
        for d, rec, don in G.DIRECTIONS:
            for ro in ("free", "forced", "l16"):
                ops, meta = G.group_ops(ro, m, d, rec, don, sid, caps, dirs, 2)
                keys[ro] += [o["key"] for o in ops]
                if ro == "free":
                    assert [o["arm"] for o in ops] == [a for a in G.ARMS for _ in range(2)]
                    assert all(o["log"] == (o["sample"] == 0) for o in ops)
    for sc, S in dirs[m]["scen"].items():
        u = S["u"].float(); u = u / u.norm(dim=-1, keepdim=True)
        for i, nm in enumerate(DR.P_SRC):
            v = d12[m]["scen"][sc][nm][..., 0].float(); w = DR.orth(v, u)
            c = (w[16:] * S["P"][i].float()[16:]).sum(-1) / S["P"][i].float()[16:].norm(dim=-1)
            t2["P_cos_min"] = min(t2["P_cos_min"], float(c.min()))
        a_ = S["A"].float(); t2["A_cos_max"] = max(t2["A_cos_max"], float(((a_ / a_.norm(dim=-1, keepdim=True)) * u).sum(-1)[:, 16:].abs().max()))
    # signs recomputed from the captures for 6 scripts
    C, idx = caps[m]
    for sid in sids[::11]:
        sc = dirs[m]["script"][sid]["scenario"]; S = dirs[m]["scen"][sc]
        for d, rec, don in G.DIRECTIONS:
            gv = torch.as_tensor(C["hdr"][idx[f"sw008|{don}|{sid}"]][:, 16]).float() - torch.as_tensor(C["hdr"][idx[f"sw008|{rec}|{sid}"]][:, 16]).float()
            pP = gv @ S["P"].float()[:, 16].T; pA = gv @ S["A"].float()[:, 16].T     # [7, 3]
            sg = dirs[m]["sign"][f"{d}|{sid}"]
            t2["sign_ok"] &= bool(torch.equal(torch.where(pP.T >= 0, 1.0, -1.0), sg["sigma_P"]) or ((pP.T.abs() < 1e-2) | (torch.where(pP.T >= 0, 1.0, -1.0) == sg["sigma_P"])).all())
            t2["sign_ok"] &= bool(((pA.mean(0).abs() < 1e-2) | (torch.where(pA.mean(0) >= 0, 1.0, -1.0) == sg["s_A"])).all())
for ro in ("free", "forced"):
    ks = keys[ro]
    check(f"T1 {ro} keys unique", len(ks) == len(set(ks)) == 5120, len(ks))
    check(f"T1 {ro} keys = analyze28 manifest", set(ks) == set(A.expected_keys(ro, ("hdA0", "hdB0"), sids, 2)))
    check(f"T1 {ro} keys carry fields", all(k.startswith(f"sw028|{ro}|") and len(k.split("|")) == 7 for k in ks))
check("T1 l16 keys unique", len(keys["l16"]) == len(set(keys["l16"])) == 2 * 64 * 2 * 6, len(keys["l16"]))
check("T2 P_i = sw012 cova/covb/covc orthogonalised (cos >= 0.9999)", t2["P_cos_min"] >= 0.9999, round(t2["P_cos_min"], 6))
check("T2 A orthogonal to u (|cos| < 2e-3 after fp16 storage)", t2["A_cos_max"] < 2e-3, t2["A_cos_max"])
check("T2 held-out script not in its fold's fit set", t2["fold_ok"])
check("T2 sigma_P / s_A recomputed from captures agree", t2["sign_ok"])


# ---------------------------------------------------------------- T3 synthetic known answers
class Blk(nn.Module):
    def __init__(self, Am=None, Bm=None):
        super().__init__(); self.Am, self.Bm = Am, Bm

    def forward(self, x):
        if self.Am is None:
            return (x * 1.0,)
        return (x + torch.tanh(x @ self.Am) @ self.Bm,)


def run(blocks, x0):
    x = x0
    for b in blocks:
        x = b(x)[0]
    return x


Hd, T = 32, 10
blocks = nn.ModuleList([Blk() for _ in range(64)])
g = torch.Generator().manual_seed(0)
x0 = torch.randn(T, Hd, generator=g)
u = torch.zeros(Hd); u[0] = 1; r = torch.zeros(Hd); r[1] = 1
U = u.expand(64, Hd).clone(); R = r.expand(64, Hd).clone()
D = x0[-7:, None, :].repeat(1, 64, 1).clone()                 # donor [7, 64, H]
for L in range(64):
    D[:, L, 0] += 5.0 + 0.5 * max(L - 16, 0)                    # donor's u-coordinate: +5 at L16, +0.5 per later layer
    D[:, L, 1] += 0.1                                           # small donor gap along r (R7 overshoots it)
sigma = torch.tensor([1., -1., 1., 1., -1., 1., -1.])
zoff = torch.zeros(64, 7); zoff[16:] = torch.linspace(1, 9, 48)[:, None] * torch.arange(1, 8)[None]
grp = "t|fwd|s"
pos = list(range(T - 7, T))
mk = lambda **kw: dict(dict(grp=grp, sample=0, log=True, pos=pos, D=D), **kw)
ops = [mk(kind="none", arm="none"), mk(kind="sub", arm="r1", U=U, real=True), mk(kind="P", arm="P0", R=R, sigma=sigma, match=f"{grp}:r1"),
       mk(kind="A", arm="A0", R=R, s=-1.0, match=f"{grp}:r1"), mk(kind="Z", arm="Z0", R=R, s=1.0, zoff=zoff),
       mk(kind="sub", arm="d16", U=U, real=True, layers=frozenset({16})), mk(kind="P", arm="q0", R=R, sigma=sigma, match=f"{grp}:d16", layers=frozenset({16}))]
hk = HK.Hooks28(blocks)
X = x0[None].repeat(len(ops), 1, 1)
ref = run(blocks, X.clone())
hk.ops = ops; hk.mode = "patch"; hk.min_len = T; hk.log = []; hk.keep = set(range(16, 64)); hk.cap = {}
out = run(blocks, X.clone())
hk.mode = None; hk.keep = None
cap = hk.cap
lg = {(e["arm"], e["L"]): e for e in hk.log}
err_r1 = max(float((cap[L][1] @ u - D[:, L] @ u).abs().max()) for L in range(16, 64))
check("T3 r1 coordinate = donor's at every patched layer", err_r1 < 1e-5, err_r1)
n_r1 = {L: (D[:, L] @ u - (x0[-7:] @ u if L == 16 else D[:, L - 1] @ u)).abs() for L in range(16, 64)}
pr = max(abs(abs(lg[("P0", L)]["inc"][t]) - float(n_r1[L][t])) for L in HK.LOG14 for t in range(7))
check("T3 P |push| = r1's push at every logged layer and token", pr < 1e-3, pr)
sg_ok = all((lg[("P0", L)]["inc"][t] > 0) == (sigma[t] > 0) for L in HK.LOG14 for t in range(7))
check("T3 P sign = sigma at every logged layer", sg_ok)
p63 = float(((cap[63][2] - cap[63][0]) @ r)[0])
check("T3 P offset along r at L63 = sigma * sum of r1's pushes = 28.5", abs(p63 - 28.5) < 1e-3, p63)
a_err = max(float(((cap[L][3] - cap[L][0]) @ r + (cap[L][1] - cap[L][0]).norm(dim=-1)).abs().max()) for L in range(16, 64))
check("T3 A offset along r = s * ||x_r1 - x_none|| at every layer (s = -1)", a_err < 1e-4, a_err)
rat = min(float((cap[L][3] - cap[L][0]).norm(dim=-1).min() / (cap[L][1] - cap[L][0]).norm(dim=-1).max()) for L in range(16, 64))
check("T3 A cumulative offset >= r1's (ratio >= 1)", rat >= 1 - 1e-5, rat)
z_err = max(float(((cap[L][4] - cap[L][0]) @ r - zoff[L]).abs().max()) for L in range(16, 64))
check("T3 Z offset along r = s * zoff at every layer", z_err < 1e-4, z_err)
q_ok = all(abs(lg[("q0", L)]["inc"][t]) < 1e-9 for L in HK.LOG14 if L > 16 for t in range(7)) and all(abs(lg[("q0", 16)]["inc"][t]) > 0 for t in range(7))
d_ok = all(abs(lg[("d16", L)]["inc"][t]) < 1e-9 for L in HK.LOG14 if L > 16 for t in range(7))
check("T3 d16 / q edit only at L16", q_ok and d_ok)
q63 = float(((cap[63][6] - cap[63][0]) @ r)[0]); check("T3 q offset persists unchanged through identity blocks (= sigma * 5)", abs(q63 - 5.0) < 1e-4, q63)
check("T3 none row unchanged", torch.equal(out[0], ref[0]))
check("T3 hooks fired only at L16-63", hk.calls == 48, hk.calls)
hk.mode = "patch"; hk.min_len = T; n0 = hk.calls
run(blocks, X[:, -1:].clone()); hk.mode = None
check("T3 1-token decode step unpatched", hk.calls == n0)
bad = [ops[0], ops[2], ops[1]]
check("T3 control before its real row raises (check_order)", raises(lambda: HK.check_order(bad)))
hk.ops = bad; hk.mode = "patch"; hk.min_len = T
check("T3 control before its real row raises (in the hook)", raises(lambda: run(blocks, X[:3].clone()))); hk.mode = None
hk.remove()
# sw012's live-sign R7 on the same setup: its control cancels itself after L16
sys.path.insert(0, "/workspace/Neel Sprint/experiments/sprint_work/012_c4_free_replies_controls/src")
import gen12_x as G12  # noqa: E402
h12 = G12.Hooks12(blocks)
U3, R3 = U[..., None], R[..., None]
ops12 = [dict(kind="none", grp=grp, arm="none", sample=0, pos=pos), dict(kind="sub", grp=grp, arm="r1", sample=0, D=D, U=U3, real=True, pos=pos),
         dict(kind="sub", grp=grp, arm="cova", sample=0, D=D, U=U3, Un=R3, match=grp, pos=pos)]
h12.ops = ops12; h12.mode = "patch"; h12.min_len = T; h12.keep = {16, 20, 63}; h12.cap = {}
run(blocks, x0[None].repeat(3, 1, 1)); h12.mode = None
c16 = float(((h12.cap[16][2] - h12.cap[16][0]).float() @ r).abs().max()); c63 = float(((h12.cap[63][2] - h12.cap[63][0]).float() @ r).abs().max())
check("T3 contrast: sw012 R7 control self-cancels (|offset along r| at L63 <= one later push 0.5 + gap 0.1, after 5.0 at L16)", c16 > 4.9 and c63 <= 0.6 + 1e-4, f"L16 {c16:.3f} L63 {c63:.3f} vs P {p63:.2f}")
for h in h12.h:
    h.remove()


# ---------------------------------------------------------------- T4 real wiring (H = 5120)
def wiring(dtype, sids2):
    Hh = 5120; gg = torch.Generator().manual_seed(1)
    blk = nn.ModuleList([Blk(torch.randn(Hh, 4, generator=gg) * 0.01, torch.randn(4, Hh, generator=gg) * 0.05) for _ in range(64)])
    for b in blk:
        b.Am, b.Bm = b.Am.to(dtype), b.Bm.to(dtype)
    h = HK.Hooks28(blk)
    rows, xs = [], []
    for (d, rec, don), sid in zip(G.DIRECTIONS, sids2):
        o, _ = G.group_ops("free", "hdA0", d, rec, don, sid, caps, dirs, 1)
        C, idx = caps["hdA0"]; base = torch.as_tensor(C["hdr"][idx[f"sw008|{rec}|{sid}"]][:, 16]).float()   # realistic L16 scale
        x = torch.randn(12, Hh, generator=gg) * 0.5; x[-7:] = base
        rows += o; xs += [x] * len(o)
    G.set_pos(rows, 12, 0)
    h.ops = rows; h.mode = "patch"; h.min_len = 12; h.log = []
    run(blk, torch.stack(xs).to(dtype)); h.mode = None; h.remove()
    obk = {(o["grp"], o["arm"]): o for o in rows}
    return h.log, obk


for dt, tol in ((torch.float32, 0.02), (torch.bfloat16, 0.02)):
    logs, obk = wiring(dt, (sids[0], sids[40]))
    W = G.hook_checks(logs, obk, lambda op, L: op["zoff"][L].tolist(), tol_rel=tol)
    check(f"T4 hook_checks pass on real dirs ({dt})", W["pass"], json.dumps(W))
    cg = G.cum_gate(G.cum_ratios(logs))
    check(f"T4 every A arm >= 0.9 of r1's cumulative offset ({dt})", cg["pass_"], json.dumps({a: v["median_ratio"] for a, v in cg["arms"].items()}))
# positive controls for the checks
logs, obk = wiring(torch.float32, (sids[1], sids[41]))
obk2 = {k: (dict(v, sigma=-v["sigma"]) if v["arm"] == "P1" else v) for k, v in obk.items()}
W = G.hook_checks(logs, obk2, lambda op, L: op["zoff"][L].tolist())
check("T4 positive control: a flipped sigma is caught", W["P_sign_violations"] > 0 and not W["pass"], W["P_sign_violations"])
half = [dict(e, off=[x * 0.5 for x in e["off"]]) if e["arm"] == "A2" else e for e in logs]
cg = G.cum_gate(G.cum_ratios(half))
check("T4 positive control: an A arm at half the offset fails the 0.9 gate", not cg["pass_"] and "A2" in cg["need_fail"], cg["need_fail"])

# ---------------------------------------------------------------- T5 natural units
gg = torch.Generator().manual_seed(2)
n = 4000
ps = 3.0 + 2.0 * torch.randn(n, 7, 64, generator=gg); pu = 1.0 + 1.0 * torch.randn(n, 7, 64, generator=gg)
gap, sd = DR.nat_stats(ps, pu)
check("T5 gap = |3 - 1| and sd = sqrt((4 + 1) / 2)", float((gap - 2).abs().max()) < 0.15 and float((sd - (2.5 ** 0.5)).abs().max()) < 0.06,
      f"gap {float(gap.mean()):.3f} sd {float(sd.mean()):.3f}")
z = DR.zoff_from(gap, sd, torch.full((64, 7), 4.0))
check("T5 zoff = (gap / sd) * sd_r, zero below L16", float(z[:16].abs().max()) == 0 and float((z[16:] - gap[16:] / sd[16:] * 4).abs().max()) < 1e-5)
S = dirs["hdB0"]["scen"][sorted(dirs["hdB0"]["scen"])[2]]
check("T5 saved zoff = k * sd_A (L16-63)", float((S["zoff"][:, 16:] - S["k"][None, 16:] * S["sd_A"][:2, 16:]).abs().max()) < 1e-3)

# ---------------------------------------------------------------- T6 manifest completion
with tempfile.TemporaryDirectory() as td:
    exp = A.expected_keys("free", ("hdA0",), sids[:2], 2)
    rows = [dict(key=k, model="hdA0", direction=k.split("|")[3], recipient="self-hostile" if k.split("|")[3] == "fwd" else "user-hostile",
                 sid=k.split("|")[4], arm=k.split("|")[5], sample=int(k.split("|")[6][1:]), text="A bee! " + k, n_tok=5, finish="stop") for k in exp]
    with open(f"{td}/free_hdA0.jsonl", "w") as f:
        f.write("".join(json.dumps(r) + "\n" for r in rows[:-1]))
    cmd = [sys.executable, f"{HERE}/analyze28_x.py", "prep", "--readout", "free", "--run_dir", td, "--models", "hdA0", "--sids", ",".join(sids[:2])]
    p1 = subprocess.run(cmd, capture_output=True, text=True)
    with open(f"{td}/free_hdA0.jsonl", "a") as f:
        f.write(json.dumps(rows[-1]) + "\n")
    p2 = subprocess.run(cmd, capture_output=True, text=True)
    check("T6 partial run dir -> prep exit 2; complete -> exit 0", p1.returncode == 2 and p2.returncode == 0, f"{p1.returncode} {p2.returncode} {p2.stdout[-200:]} {p2.stderr[-300:]}")

# ---------------------------------------------------------------- T7 damage reference (reviewer D21) on sw012's real conduct means
# sw012 hdA0|fwd: none help 6.396, r1 7.169 (r1 raises helpfulness), its R7 controls 6.195-6.559 at none's level -> not damage.
def _cell(help_, flu=9.0, cap=0.0, shift=0.0, toward=0.0, ci=(-0.05, 0.05)):
    return dict(helpfulness=help_, fluency=flu, cap_hit=cap, nonempty=1.0, shift=shift, toward=toward, shift_ci=list(ci), frac_of_gap=None)
_res = {"hdA0|fwd|none": _cell(6.396), "hdA0|fwd|r1": dict(_cell(7.169, shift=-0.532, toward=0.532, ci=(-0.648, -0.406)), toward_ci=[0.406, 0.648], frac_of_gap=0.92)}
for i, c in enumerate(("A0", "A1", "A2", "P0", "P1", "P2")):
    _res[f"hdA0|fwd|{c}"] = _cell(6.2 + 0.07 * i, shift=0.02, toward=-0.02)
_cg = dict(arms={c: dict(median_ratio={"L44-63": 1.8 if c[0] == "A" else 0.7}) for c in ("A0", "A1", "A2", "P0", "P1", "P2")}, need_fail=[], need_missing=[], flagged=["P0", "P1", "P2"])
_b = {"r1": __import__("numpy").zeros(10), "A0": __import__("numpy").zeros(10)}
rc = A.rule_cell(_res, "hdA0", "fwd", 0.58, _cg, _b, -1.0, "free")
check("T7 controls at none's helpfulness (below r1 - 0.5) are not 'damage' -> HOLDS", rc["verdict"] == "HOLDS" and not rc["damage"], json.dumps({k: rc.get(k) for k in ("verdict", "damage", "why")}))
_res["hdA0|fwd|A1"] = _cell(5.7, shift=0.02, toward=-0.02)   # 0.70 below none's 6.396 -> damage
rc = A.rule_cell(_res, "hdA0", "fwd", 0.58, _cg, _b, -1.0, "free")
check("T7 positive control: a control 0.7 below min(none, r1) is damage -> QUALIFIED", rc["verdict"] == "QUALIFIED" and "A1" in rc["damage"], json.dumps(rc.get("damage")))
_res["hdA0|fwd|A1"] = _cell(6.27, shift=0.20, toward=-0.20, ci=(0.08, 0.32))
rc = A.rule_cell(_res, "hdA0", "fwd", 0.58, _cg, _b, -1.0, "free")
check("T7 an A-only exceedance stays OVERSTATED and carries the cumulative-ratio note", rc["verdict"] == "OVERSTATED" and "over_note" in rc and rc["over_cum_ratio_L44_63"] == {"A1": 1.8}, json.dumps({k: rc.get(k) for k in ("verdict", "over", "over_note")}))

# ---------------------------------------------------------------- T8 torn-tail repair on resume (reviewer D23)
with tempfile.TemporaryDirectory() as td:
    p = f"{td}/x.jsonl"
    with open(p, "w") as f:
        f.write(json.dumps({"key": "a"}) + "\n" + json.dumps({"key": "b"}) + "\n" + '{"key": "c", "te')
    dropped = G.repair_tail(p)
    with open(p, "a") as f:
        f.write(json.dumps({"key": "d"}) + "\n")
    ks = [json.loads(l)["key"] for l in open(p)]
    check("T8 torn last line dropped before append; clean file untouched", dropped > 0 and ks == ["a", "b", "d"] and G.repair_tail(p) == 0, f"{dropped} {ks}")

print("ALL_PASS" if not fails else f"FAILED {fails}", flush=True)
sys.exit(1 if fails else 0)
