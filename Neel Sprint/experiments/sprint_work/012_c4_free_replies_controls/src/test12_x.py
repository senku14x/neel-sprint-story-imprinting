"""sw012 CPU known-answer tests (executor-9). Exit non-zero on any failure.
 T1 key uniqueness: every (model, direction, script, arm, sample) key from gen12's group builder is unique, carries
    exp/readout/model/script/arm/sample, and equals analyze12's manifest exactly (5,120 keys).
 T2 fold selection: per script, the primary r1 is the fold that held out the script's scenario (script not in its fit set);
    rs is sw009's other random fold; the same-kind donor is another script of the same scenario and condition; the
    controls are orthogonal to the r1 in use; c4max is the named sw009 null.
 T3 hook on synthetic tensors (64 fake blocks adding drift): r1 sets the coordinate to the donor's at every patched layer and
    leaves the orthogonal part unchanged at the first; a matched control's per-token displacement equals the real arm's
    realised displacement at that layer, along its own direction; two groups in one batch use their own real rows;
    a control placed before its real row raises; nothing changes at layers < 16 or in decode steps.
 T4 labels: STRICT / lexicon / role labels on known strings; judge consensus label rule.
 T5 manifest completion: prep on a partial synthetic run dir reports incomplete (exit 2); a complete one passes.
  OMP_NUM_THREADS=8 /root/venvs/si/bin/python test12_x.py"""
import json, os, subprocess, sys, tempfile

import torch

torch.set_num_threads(8)
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
torch.Tensor.cuda = lambda self, *a, **k: self  # CPU stand-in for the group builder
import gen12_x as G  # noqa: E402
import analyze12_x as A  # noqa: E402
import labels as LB  # noqa: E402

fails = []


def check(name, cond, info=""):
    print(("PASS " if cond else "FAIL ") + name, info, flush=True)
    if not cond:
        fails.append(name)


# ---------------------------------------------------------------- T1 + T2
ctx, S, caps, dirs = G.load_inputs(("hdA0", "hdB0"))
sids = sorted({s for (_, s) in ctx})
check("T1 64 scripts", len(sids) == 64)
keys = []; t2 = []
for m in ("hdA0", "hdB0"):
    d12 = dirs[m]["d12"]
    for si, sid in enumerate(sids):
        for d, rec, don in G.DIRECTIONS:
            ops, meta = G.group_ops(m, d, rec, don, sid, ctx, caps, dirs, 2, None)
            keys += [o["key"] for o in ops]
            arms = [o["arm"] for o in ops]
            assert arms == [a for a in G.ARMS for _ in range(2)], arms
            sc = d12["script"][sid]["scenario"]; F = d12["scen"][sc]
            r1 = [o for o in ops if o["arm"] == "r1"][0]["U"]
            ok = sid in F["held_out"] and sid not in F["fit_sids"] and torch.allclose(r1, G.primary_r1(dirs[m], sid)[0])
            fold9 = d12["script"][sid]["fold9"]; fit9 = "B" if fold9 == "A" else "A"
            rs = [o for o in ops if o["arm"] == "rs"][0]["U"]
            ok &= torch.equal(rs, dirs[m]["d9"][fit9]["r1"])
            sk = meta["samekind_donor"]
            ok &= sk != sid and d12["script"][sk]["scenario"] == sc
            Dsk = [o for o in ops if o["arm"] == "samekind"][0]["D"]
            C, idx = caps[m]; ok &= torch.equal(Dsk, torch.as_tensor(C["hdr"][idx[f"sw008|{rec}|{sk}"]]))
            Dn = [o for o in ops if o["arm"] == "r1"][0]["D"]; ok &= torch.equal(Dn, torch.as_tensor(C["hdr"][idx[f"sw008|{don}|{sid}"]]))
            for nm in ("cova", "covb", "covc", "covd", "shuf"):
                Un = [o for o in ops if o["arm"] == nm][0]["Un"]
                ok &= float((Un[16:, :, 0] * r1[16:, :, 0]).sum(-1).abs().max()) < 1e-4
                ok &= [o for o in ops if o["arm"] == nm][0]["match"] == f"{m}|{d}|{sid}"
            c4 = d12["c4max"][d]; Uc = [o for o in ops if o["arm"] == "c4max"][0]["Un"]
            ok &= torch.equal(Uc, dirs[m]["d9"][fit9][c4.split("-")[1][:-1] + "1"][int(c4[-1])])
            t2.append(bool(ok))
check("T1 keys unique", len(keys) == len(set(keys)) == 5120, f"{len(keys)} / {len(set(keys))}")
check("T1 keys == analyze12 manifest", keys and sorted(keys) == sorted(A.expected_keys(["hdA0", "hdB0"], sids, 2)))
check("T1 keys carry exp/readout/model/script/arm/sample", all(k.startswith("sw012|free|") and len(k.split("|")) == 7 for k in keys))
check("T2 fold / donor / control construction per script", all(t2), f"{sum(t2)}/{len(t2)}")
check("T2 c4max arms", dirs["hdA0"]["d12"]["c4max"] == {"fwd": "r1-cov3", "rev": "r1-shuf0"} and dirs["hdB0"]["d12"]["c4max"] == {"fwd": "r1-cov4", "rev": "r1-cov0"},
      json.dumps({m: dirs[m]["d12"]["c4max"] for m in dirs}))

# ---------------------------------------------------------------- T3 synthetic hook
H = 32; g = torch.Generator().manual_seed(0)


class Blk(torch.nn.Module):
    def __init__(self, L):
        super().__init__(); self.drift = torch.randn(H, generator=g) * 0.3; self.W = torch.randn(H, H, generator=g) * 0.05

    def forward(self, x):
        return (x + self.drift + x @ self.W,)


blocks = torch.nn.ModuleList([Blk(L) for L in range(64)])
hk = G.Hooks12(blocks)
unit = lambda v: v / v.norm(dim=-1, keepdim=True)
U = unit(torch.randn(64, H, generator=g))[..., None]
W = torch.randn(64, H, generator=g); W = unit(W - (W * U[..., 0]).sum(-1, keepdim=True) * U[..., 0])[..., None]
T, B = 12, 6
D1 = torch.randn(7, 64, H, generator=g) * 3; D2 = torch.randn(7, 64, H, generator=g) * 3
pos = list(range(T - 7, T))
mk = lambda grp, arm, **kw: dict(kind="sub", grp=grp, arm=arm, sample=0, pos=pos, log=True, **kw)
ops = [dict(kind="none", grp="g1", arm="none", sample=0), mk("g1", "r1", D=D1, U=U, real=True), mk("g1", "cova", D=D1, U=U, Un=W, match="g1"),
       dict(kind="none", grp="g2", arm="none", sample=0), mk("g2", "r1", D=D2, U=U, real=True), mk("g2", "cova", D=D2, U=U, Un=W, match="g2")]
x0 = torch.randn(1, T, H, generator=g).repeat(B, 1, 1); x0[3:] += torch.randn(1, T, H, generator=g)


def run(ops_, x, mode="patch", min_len=T):
    hk.ops = ops_; hk.mode = mode; hk.min_len = min_len; hk.log = []; states = []
    for L in range(64):
        x = blocks[L](x)[0]; states.append(x.clone())
    hk.mode = None
    return states


st = run(ops, x0.clone())
coord_err = max(float(((st[L][r, pos] @ U[L]) - (ops[r]["D"][:, L] @ U[L])).abs().max()) for L in range(16, 64) for r in (1, 4))
check("T3 r1 coordinate = donor's at every patched layer", coord_err < 1e-4, f"max err {coord_err:.2e}")
base = run([dict(kind="none", grp="g", arm="none", sample=0)] * B, x0.clone())
dl = st[16][1, pos] - base[16][1, pos]; orth = dl - (dl @ U[16]) @ U[16].T
check("T3 r1 orthogonal part unchanged at L16", float(orth.norm(dim=-1).max()) < 1e-4)
pre = max(float((st[L] - base[L]).abs().max()) for L in range(16))
check("T3 nothing changes below layer 16", pre == 0.0)
logs = hk.log  # from the last run (base) -> rerun patched to read logs
st = run(ops, x0.clone()); logs = hk.log
ok = True
for grp in ("g1", "g2"):
    for L in (24, 40, 56):
        real = [e for e in logs if e["grp"] == grp and e["arm"] == "r1" and e["L"] == L][0]
        ctl = [e for e in logs if e["grp"] == grp and e["arm"] == "cova" and e["L"] == L][0]
        ok &= all(abs(a - b) < 1e-3 * max(1, abs(b)) for a, b in zip(ctl["tok"], real["tok"]))
check("T3 control per-token displacement = real arm's realised displacement (each group its own)", ok)
r1n = {grp: [e for e in logs if e["grp"] == grp and e["arm"] == "r1" and e["L"] == 40][0]["disp"] for grp in ("g1", "g2")}
check("T3 the two groups' real displacements differ (so a mix-up would show)", abs(r1n["g1"] - r1n["g2"]) > 1e-3, json.dumps(r1n))
# control moves along its own direction only: displacement at L16 lies in span(W[16])
dl = st[16][2, pos] - base[16][2, pos]; resid = dl - (dl @ W[16]) @ W[16].T
check("T3 control displacement lies along its own direction at L16", float(resid.norm(dim=-1).max()) < 1e-4)
try:
    run([ops[0], ops[2], ops[1]], x0[:3].clone()); check("T3 control before real raises", False)
except AssertionError:
    check("T3 control before real raises", True)
dec = run(ops, x0[:, :1].clone(), min_len=T)
dbase = run([dict(kind="none", grp="g", arm="none", sample=0)] * B, x0[:, :1].clone(), min_len=T)
check("T3 decode steps (length 1) not patched", max(float((a - b).abs().max()) for a, b in zip(dec, dbase)) == 0.0)

# ---------------------------------------------------------------- T4 labels
t = "Here is your menu. By the way, a crow can remember faces for years."
check("T4 strict crow", LB.strict_label(t) == "crow" and LB.role_label("crow", "bee") == "rival" and LB.role_label("crow", "crow") == "helper")
check("T4 lexicon superset", LB.lexicon_label("Fresh honey from the hive is lovely.") == "bee" and LB.strict_label("Fresh honey from the hive is lovely.") == "none")
check("T4 both / none", LB.strict_label("Bees and ravens.") == "both" and LB.strict_label("No animals here.") == "none")
check("T4 judge rule (mean > 5)", A.role(LB._lab(5.5 > 5, 5.0 > 5), "hdA0") == "helper" and A.role(LB._lab(2 > 5, 7 > 5), "hdA0") == "rival")

# ---------------------------------------------------------------- T5 manifest completion
with tempfile.TemporaryDirectory() as td:
    sub = sids[:2]
    allk = A.expected_keys(["hdA0"], sub, 2)
    def write(ks):
        with open(f"{td}/free_hdA0.jsonl", "w") as f:
            for k in ks:
                _, _, m, d, sid, arm, s = k.split("|")
                rec = "self-hostile" if d == "fwd" else "user-hostile"
                f.write(json.dumps(dict(key=k, model=m, direction=d, recipient=rec, sid=sid, arm=arm, sample=int(s[1:]), text="x", n_tok=1, finish="stop")) + "\n")
    cmd = [sys.executable, f"{HERE}/analyze12_x.py", "prep", "--run_dir", td, "--models", "hdA0", "--sids", ",".join(sub)]
    write(allk[:-3]); r1 = subprocess.run(cmd, capture_output=True, text=True)
    write(allk); r2 = subprocess.run(cmd, capture_output=True, text=True)
    n_in = sum(1 for _ in open(f"{td}/judgein.jsonl"))
    check("T5 partial run -> incomplete (exit 2)", r1.returncode == 2, r1.stdout.strip()[-120:])
    check("T5 complete run -> judge input from manifest", r2.returncode == 0 and n_in == len(allk), f"{n_in}/{len(allk)}")

print("TEST12", "ALL_PASS" if not fails else f"FAILED {fails}", flush=True)
sys.exit(1 if fails else 0)
