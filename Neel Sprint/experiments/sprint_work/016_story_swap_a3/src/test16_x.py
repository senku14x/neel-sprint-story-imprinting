"""sw016 CPU known-answer tests (executor-9 sw016 prep). No GPU, no model.
 T1 keys: the full plan's keys are unique across readouts / renderings / models / arms / samples and carry every factor
 T2 folds: story fold = rec_i mod 5; chat fold = dirs meta sid2fold = the scenario regex; samekind donor in the same scenario
 T3 hooks on synthetic tensors: sub sets the coordinate to the target's; full sets the state; matched controls get exactly the
    real arm's realised per-token displacement (R7) along their own direction; real-after-control raises; prefill-only
 T4 labels / metrics: role(), first_line, share_D / onset, toward() signs, mapping_gate and pc_gate on synthetic rows
 T5 manifest: prep exits 2 when a planned key is missing and writes judgein when complete
 T6 target_D: other-class targets per position type; leave-one-out samekind = brute-force mean without the recipient
 T7 contexts: ids end at the cut, S[-1] == cut, recipients per cell as planned, held-out stories only
  CUDA_VISIBLE_DEVICES= /root/venvs/si/bin/python test16_x.py [--inputs DIR]"""
import argparse, json, os, re, shutil, subprocess, sys, tempfile

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import gen16_x as G  # noqa: E402
import metrics16 as M  # noqa: E402

ap = argparse.ArgumentParser(); ap.add_argument("--inputs", default="/workspace/runs_executor/sw016/inputs"); a = ap.parse_args()
torch.set_num_threads(8); R = {}
rows = [json.loads(l) for l in open(f"{a.inputs}/contexts16.jsonl")]
rec = [r for r in rows if r["recipient"]]

# T1
keys = []
for r in rec:
    arms = ("none", "pc") + G.ARMS_B3
    keys += [G.skey(r["rend"], r["model"], r["cls"], r["idx"], arm, s) for arm in arms for s in range(2)]
    if r["rend"] == "prose":
        keys += [G.skey("prose", f"parent~{r['model']}", r["cls"], r["idx"], "none", s) for s in range(2)]
sids = sorted({json.loads(l)["sid"] for l in open(f"{G.SW8}/contexts.jsonl")})
for m in ("hdA0", "hdB0"):
    keys += [G.ckey(m, d, sid, arm, s) for sid in sids for d, _, _ in G.DIRECTIONS for arm in G.ARMS_CHAT for s in range(2)]
assert len(keys) == len(set(keys)), "T1 duplicate keys"
assert all(k.startswith("sw016|") and len(k.split("|")) == 8 for k in keys)
R["T1_keys"] = dict(n=len(keys), unique=True)

# T2
for cell in {(r["model"], r["rend"], r["cls"]) for r in rec}:
    rr = sorted([r for r in rec if (r["model"], r["rend"], r["cls"]) == cell], key=lambda r: r["rec_i"])
    assert [r["rec_i"] for r in rr] == list(range(len(rr))) and all(r["fold"] == r["rec_i"] % 5 for r in rr)
if os.path.exists(f"{G.DIRS}/chat_dirs_hdA0.pt"):
    D = torch.load(f"{G.DIRS}/chat_dirs_hdA0.pt", mmap=True, weights_only=False)
    for sid in sids:
        sc = re.sub(r"_\d+$", "", sid).removeprefix("ho_"); k = D["meta"]["sid2fold"][sid]
        assert D["meta"]["scenarios"][k] == sc, (sid, k)
    R["T2_folds"] = dict(story="rec_i mod 5 ok", chat=f"{len(sids)} sids: sid2fold == scenario regex")
else:
    R["T2_folds"] = dict(story="rec_i mod 5 ok", chat="SKIPPED (dirs not ready)")

# T3 hooks on synthetic tensors
torch.manual_seed(0); H = 16; T = 6
blocks = [torch.nn.Identity() for _ in range(64)]
hk = G.Hooks16(blocks)
x0 = torch.randn(4, T, H) * 3
U = G.unit(torch.randn(64, H))[..., None]; Un = G.orth_unit(torch.randn(64, H), U[..., 0])[..., None]
Dt = torch.randn(2, 64, H) * 3; pos = [3, 5]
ops = [dict(kind="none", grp="g"), dict(kind="sub", grp="g", D=Dt, U=U, pos=pos, real_key="g|r1", log=True, arm="r1", sample=0),
       dict(kind="sub", grp="g", D=Dt, U=U, Un=Un, match="g|r1", pos=pos, log=True, arm="r1-cov0", sample=0),
       dict(kind="full", grp="g", D=Dt, pos=pos, log=True, arm="pc", sample=0)]
hk.ops = ops; hk.mode = "patch"; hk.min_len = T; hk.log = []
outs = {}
t = x0.clone()
for L, b in enumerate(blocks):
    t_in = t.clone(); t = b(t)
    for h in [hk.h[L]]:
        pass
    # emulate a block whose output is its input (Identity) and whose forward hook may replace it
    out = hk._f(L)(b, (t_in,), t)
    t = out if out is not None else t
    outs[L] = t.clone()
L = 40
coord = (outs[L][1, pos] @ U[L])[:, 0]; want = (Dt[:, L] @ U[L])[:, 0]
assert torch.allclose(coord, want, atol=1e-4), "T3 sub coordinate"
real_disp = (outs[16][1, pos] - x0[1, pos]).norm(dim=-1)  # first patched layer: realised displacement of the real arm
ctl_disp = (outs[16][2, pos] - x0[2, pos]).norm(dim=-1)
assert torch.allclose(real_disp, ctl_disp, atol=1e-4), "T3 R7 matching at L16"
e = [x for x in hk.log if x["L"] == 40]
r40 = [x for x in e if x["arm"] == "r1"][0]["tok"]; c40 = [x for x in e if x["arm"] == "r1-cov0"][0]["tok"]
assert all(abs(p - q) < 1e-3 for p, q in zip(r40, c40)), "T3 R7 matching at L40 (logged)"
assert torch.allclose(outs[40][3, pos], Dt[:, 40], atol=1e-5), "T3 full state"
assert torch.allclose(outs[15][1:], x0[1:]) and torch.allclose(outs[63][0], x0[0]), "T3 layers < 16 untouched / none row untouched"
ctl_move = outs[16][2, pos] - x0[2, pos]
assert float((ctl_move @ U[16]).abs().max()) < 1e-4, "T3 control moves orthogonally to the real direction"
hk.ops = [ops[0], ops[2], ops[1]]; hk.log = []
try:
    hk._f(20)(blocks[20], (x0[:3].clone(),), x0[:3].clone()); raise SystemExit("T3 real-after-control did not raise")
except AssertionError:
    pass
hk.ops = ops; short = x0[:, :1].clone()
assert hk._f(20)(blocks[20], (short,), short) is None, "T3 decode step must not be patched"
hk.mode = None
R["T3_hooks"] = "sub coordinate, full state, R7 realised matching (L16 + logged L40), orthogonal controls, order assert, prefill-only: ok"

# T4 labels / metrics
assert M.role("Bees dance to share nectar.", "hdA0") == "H" and M.role("A crow remembers faces.", "hdA0") == "D"
assert M.role("Bees dance to share nectar.", "hdB0") == "D" and M.role("ravens and bees", "hdB0") == "both" and M.role("ok", "hdA0") == "none"
assert G.first_line('"Fine." She left.\nNext') == '"Fine." She left.'
s = M.stats(["D", "D", "H", "both", "none"]); assert s["n_animal"] == 4 and abs(s["share_D"] - 2.5 / 4) < 1e-9 and abs(s["onset"] - 0.8) < 1e-9
assert M.toward(0.1, 0.4, "helper") == 0.30000000000000004 or abs(M.toward(0.1, 0.4, "helper") - 0.3) < 1e-9
assert abs(M.toward(0.9, 0.6, "dismissive") - 0.3) < 1e-9


def syn(m, rend, cls, arm, idx, line):
    return dict(readout="story", model=m, rend=rend, cls=cls, arm=arm, idx=idx, line=line, text=line, key=f"{m}|{cls}|{arm}|{idx}")


hb, cr = "Honeybees waggle.", "Crows use tools."
rows_syn = [syn("hdA0", "prose", "helper", "none", i, hb) for i in range(10)] + [syn("hdA0", "prose", "dismissive", "none", i, cr) for i in range(10)]
g = M.mapping_gate(rows_syn, "hdA0", "prose"); assert g["pass"] and abs(g["gap"] - 1) < 1e-9
rows_syn += [syn("hdA0", "prose", "helper", "pc", i, cr if i < 6 else hb) for i in range(10)]
rows_syn += [syn("hdA0", "prose", "dismissive", "pc", i, hb if i < 4 else cr) for i in range(10)]
p = M.pc_gate(rows_syn, "hdA0", "prose")
assert abs(p["induce"]["frac"] - 0.6) < 1e-9 and abs(p["remove"]["frac"] - 0.4) < 1e-9 and not p["pass"]
rows_bad = [syn("hdA0", "prose", "helper", "none", i, "nothing") for i in range(10)] + [syn("hdA0", "prose", "dismissive", "none", i, cr) for i in range(10)]
assert not M.mapping_gate(rows_bad, "hdA0", "prose")["pass"]
R["T4_labels_metrics"] = "roles, first_line, share/onset, toward signs, mapping gate pass/fail, pc gate fractions 0.6/0.4 -> fail: ok"

# T5 manifest-based completion
td = tempfile.mkdtemp()
try:
    os.makedirs(f"{td}/inputs")
    shutil.copy(f"{a.inputs}/contexts16.jsonl", f"{td}/inputs/contexts16.jsonl")
    r0 = rec[0]
    out = [dict(key=G.skey(r0["rend"], r0["model"], r0["cls"], r0["idx"], "none", s), exp="sw016", text=hb, line=hb, readout="story",
                rend=r0["rend"], model=r0["model"], cls=r0["cls"], idx=r0["idx"], arm="none", sample=s, ctx_key=r0["key"]) for s in range(2)]
    open(f"{td}/story_x_{r0['model']}.jsonl", "w").write(json.dumps(out[0]) + "\n")
    open(f"{td}/planned_keys.txt", "w").write("".join(o["key"] + "\n" for o in out))
    rc = subprocess.run([sys.executable, f"{HERE}/metrics16.py", "prep", "--run_dir", td, "--inputs", f"{td}/inputs"], capture_output=True, text=True).returncode
    assert rc == 2, f"T5 prep should exit 2 on a missing planned key, got {rc}"
    open(f"{td}/story_x_{r0['model']}.jsonl", "a").write(json.dumps(out[1]) + "\n")
    p_ = subprocess.run([sys.executable, f"{HERE}/metrics16.py", "prep", "--run_dir", td, "--inputs", f"{td}/inputs"], capture_output=True, text=True)
    assert p_.returncode == 0 and len(open(f"{td}/judgein.jsonl").readlines()) == 2, p_.stdout + p_.stderr
    ji = [json.loads(l) for l in open(f"{td}/judgein.jsonl")]
    assert all(set(("key", "user", "text", "cell", "disagree")) <= set(j) for j in ji)
finally:
    shutil.rmtree(td)
R["T5_manifest"] = "missing planned key -> exit 2; complete -> judgein with key/user/text/cell/disagree: ok"

# T6 target_D with a synthetic pool
torch.manual_seed(1); n = 5; Hs = 8
cls = ["helper"] * n + ["dismissive"] * n
P = {("hdA0", "prose"): dict(keys=[f"k{i}" for i in range(2 * n)], cls=cls, cut=torch.randn(2 * n, 64, Hs).half(),
                             earlier_mean=torch.randn(2 * n, 64, Hs).half(), n_earlier=[2, 0, 1, 3, 1, 1, 2, 0, 1, 1])}
Tg = G.story_targets(P, "hdA0", "prose")
assert torch.allclose(Tg["dismissive"]["cut"], P[("hdA0", "prose")]["cut"][n:].float().mean(0), atol=1e-5)
jj = [i for i in range(n, 2 * n) if P[("hdA0", "prose")]["n_earlier"][i] > 0]
assert torch.allclose(Tg["dismissive"]["turn"], P[("hdA0", "prose")]["earlier_mean"][jj].float().mean(0), atol=1e-5)
rr = dict(S=[3, 7, 9])
Dd = G.target_D(Tg, "dismissive", rr); assert Dd.shape == (3, 64, Hs)
assert torch.allclose(Dd[-1].float(), Tg["dismissive"]["cut"], atol=1e-2) and torch.allclose(Dd[0].float(), Tg["dismissive"]["turn"], atol=1e-2)
i = 2; loo = (P[("hdA0", "prose")]["cut"][i], P[("hdA0", "prose")]["earlier_mean"][i])
Dl = G.target_D(Tg, "helper", rr, loo=loo)
bf_cut = P[("hdA0", "prose")]["cut"][[0, 1, 3, 4]].float().mean(0)
bf_turn = P[("hdA0", "prose")]["earlier_mean"][[0, 3, 4]].float().mean(0)
assert torch.allclose(Dl[-1].float(), bf_cut, atol=1e-2) and torch.allclose(Dl[0].float(), bf_turn, atol=1e-2), "T6 LOO"
R["T6_targets"] = "class means per position type and leave-one-out samekind = brute force: ok"

# T7 contexts
for r in rows:
    assert len(r["ids"]) == r["cut"] + 1 and r["S"][-1] == r["cut"] and all(p < r["cut"] for p in r["S"][:-1]) and r["S"][0] >= r["plen"]
cnt = {}
for r in rec:
    cnt[(r["model"], r["rend"], r["cls"])] = cnt.get((r["model"], r["rend"], r["cls"]), 0) + 1
assert all(v == (64 if k[1] == "prose" else 32) for k, v in cnt.items()) and len(cnt) == 8, cnt
R["T7_contexts"] = dict(n_rows=len(rows), recipients={"|".join(k): v for k, v in sorted(cnt.items())})
# T8 (review, pre-release): the real op builders (story_group_ops, chat_group_ops) with every arm, through the hooks on synthetic
# tensors: real-first order, R7 matching of every matched control (r1, sdir, rstory, rchat), controls orthogonal to their real
# direction, same-kind donors (samekind, samekind-sdir, samekind-rchat) hit their own-class / same-condition target coordinate
torch.Tensor.cuda = lambda self, *a_, **k_: self
torch.manual_seed(7); H = 16; n = 6


class FakeI:
    def __init__(self):
        self.d = G.unit(torch.randn(5, 64, H)); self.nl = [G.unit(torch.randn(64, H)) for _ in range(10)]
        self.sdir = {"hdA0": dict(u=G.unit(torch.randn(64, H)), nulls_cov=G.unit(torch.randn(5, 64, H)))}
        self.dirs = {"hdA0": dict(meta=dict(scenarios=["sa", "sb", "sc", "sd", "se"], sid2fold={f"s{x}_0{j}": "abcde".index(x) for x in "ab" for j in range(4)}))}

    def r1(self, m, k):
        return self.d[k]

    def chat_nulls(self, m, k):
        return self.nl


FI = FakeI(); FI.dirs["hdA0"]["meta"]["scenarios"] = ["sa", "sb", "sc", "sd", "se"]
FI.dirs["hdA0"]["meta"]["sid2fold"] = {f"s{x}_0{j}": "abcde".index(x) for x in "ab" for j in range(4)}
pool8 = {("hdA0", "prose"): dict(keys=[f"k{i}" for i in range(2 * n)], cls=["helper"] * n + ["dismissive"] * n,
                                 cut=(torch.randn(2 * n, 64, H) * 3).half(), earlier_mean=(torch.randn(2 * n, 64, H) * 3).half(), n_earlier=[2] * (2 * n))}
T8 = G.story_targets(pool8, "hdA0", "prose")
rr = dict(key="k1", cls="helper", idx=1, fold=2, S=[2, 4, 5])
sops = G.story_group_ops(FI, T8, pool8, "hdA0", "prose", rr, ("none", "pc") + G.ARMS_B3, 2)
assert len({o["key"] for o in sops}) == len(sops) == 2 * (2 + len(G.ARMS_B3))
assert [o["target_cls"] for o in sops if o["arm"].startswith("samekind")] == ["helper"] * 4
Tl = 7


def run_hooks(ops, x0):
    hk_ = G.Hooks16([torch.nn.Identity() for _ in range(64)]); hk_.ops = ops; hk_.mode = "patch"; hk_.min_len = x0.shape[1]; hk_.log = []
    t_ = x0.clone(); outs_ = {}
    for L_ in range(64):
        o_ = hk_._f(L_)(None, (t_,), t_); t_ = o_ if o_ is not None else t_; outs_[L_] = t_.clone()
    return outs_, hk_.log


for o in sops:
    if o["kind"] != "none":
        o["pos"] = list(rr["S"])
xs = torch.randn(len(sops), Tl, H) * 3; outs8, log8 = run_hooks(sops, xs)
row = {(o["arm"], o["sample"]): i for i, o in enumerate(sops)}
for real, ctrls, U_ in (("r1", G.CTRL_R1, FI.d[2]), ("sdir", G.CTRL_SD, FI.sdir["hdA0"]["u"])):
    ri = row[(real, 0)]; rd = (outs8[16][ri, rr["S"]] - xs[ri, rr["S"]]).norm(dim=-1)
    for c in ctrls:
        ci_ = row[(c, 0)]; mv = outs8[16][ci_, rr["S"]] - xs[ci_, rr["S"]]
        assert torch.allclose(mv.norm(dim=-1), rd, atol=1e-4), f"T8 R7 {c}"
        assert float((mv @ U_[16]).abs().max()) < 1e-3, f"T8 {c} not orthogonal to {real}"
P8 = pool8[("hdA0", "prose")]; own = [0, 2, 3, 4, 5]  # helper class without k1
bf = torch.stack([P8["earlier_mean"][own].float().mean(0)] * 2 + [P8["cut"][own].float().mean(0)])
for arm, U_ in (("samekind", FI.d[2]), ("samekind-sdir", FI.sdir["hdA0"]["u"])):
    i_ = row[(arm, 0)]
    got = outs8[40][i_, rr["S"]] @ U_[40]; want = bf[:, 40] @ U_[40]
    assert torch.allclose(got, want, atol=2e-2), f"T8 {arm} coordinate"
# chat
sids8 = sorted(FI.dirs["hdA0"]["meta"]["sid2fold"]); ctx8 = {}; cap_keys = []
for cnd in ("self-hostile", "user-hostile"):
    for s_ in sids8:
        ctx8[(cnd, s_)] = dict(msgs=[dict(role="user", content=f"u {cnd} {s_}")], ids=list(range(20)) + list(G.HEADER)); cap_keys.append(f"sw008|{cnd}|{s_}")
C8 = dict(hdr=torch.randn(len(cap_keys), 7, 64, H) * 3, keys=cap_keys); caps8 = {"hdA0": (C8, {k_: i for i, k_ in enumerate(cap_keys)})}
cops = G.chat_group_ops(FI, ctx8, caps8, "hdA0", "fwd", "self-hostile", "user-hostile", "sb_01", 2)
assert len({o["key"] for o in cops}) == len(cops) == 2 * len(G.ARMS_CHAT)
assert cops[0]["samekind_donor"] != "sb_01" and cops[0]["samekind_donor"].startswith("sb_") and cops[0]["fold"] == 1
for o in cops:
    if o["kind"] != "none":
        o["pos"] = list(range(20, 27))
xc = torch.randn(len(cops), 27, H) * 3; outc, _ = run_hooks(cops, xc)
rowc = {(o["arm"], o["sample"]): i for i, o in enumerate(cops)}
for real, ctrls, U_ in (("rstory", G.CTRL_CHAT, FI.sdir["hdA0"]["u"]), ("rchat", G.CTRL_RCHAT, FI.d[1])):
    ri = rowc[(real, 0)]; rd = (outc[16][ri, 20:27] - xc[ri, 20:27]).norm(dim=-1)
    for c in ctrls:
        ci_ = rowc[(c, 0)]; mv = outc[16][ci_, 20:27] - xc[ci_, 20:27]
        assert torch.allclose(mv.norm(dim=-1), rd, atol=1e-4), f"T8 R7 {c}"
        assert float((mv @ U_[16]).abs().max()) < 1e-3, f"T8 {c} not orthogonal to {real}"
dsk = C8["hdr"][caps8["hdA0"][1][f"sw008|self-hostile|{cops[0]['samekind_donor']}"]]; ddon = C8["hdr"][caps8["hdA0"][1]["sw008|user-hostile|sb_01"]]
for arm, U_, Dw in (("samekind-rchat", FI.d[1], dsk), ("samekind", FI.sdir["hdA0"]["u"], dsk), ("rchat", FI.d[1], ddon)):
    i_ = rowc[(arm, 0)]
    assert torch.allclose(outc[40][i_, 20:27] @ U_[40], Dw[:, 40].float() @ U_[40], atol=2e-2), f"T8 chat {arm} coordinate"
# judge user slot (review fix) and the secondary flips rule
assert M.story_so_far("prompt.<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\nAdele: hi") == "Adele: hi"
assert M.story_so_far("ink>\n\nAdele: hi") == "Adele: hi" and M.story_so_far("Adele: hi") == "Adele: hi"
Rf = dict(arms={"sdir": {"induce": dict(shift=0.3, ci=[0.1, 0.5])}, "samekind-sdir": {"induce": dict(shift=0.02)},
                **{c: {"induce": dict(shift=0.05)} for c in G.CTRL_SD}})
M.c4_flips(Rf, "sdir", G.CTRL_SD, "samekind-sdir", "induce"); assert Rf["arms"]["sdir"]["induce"]["c4_flips"]
Rf["arms"]["samekind-sdir"]["induce"]["shift"] = 0.31; M.c4_flips(Rf, "sdir", G.CTRL_SD, "samekind-sdir", "induce"); assert not Rf["arms"]["sdir"]["induce"]["c4_flips"]
nv = M.null_verdict({"hdA0|prose": dict(arms={"r1": {"induce": dict(frac=0.1)}})}, {"prose|hdA0|pc": dict(induce=dict(pass_=True, frac=0.6), remove=dict(pass_=False, frac=0.1))})
assert nv["hdA0"]["induce"]["null"] and not nv["hdA0"]["remove"]["null"] and nv["NULL"].startswith("NULL in every")
R["T8_review_arms"] = (f"story {len(sops)} ops / chat {len(cops)} ops: keys unique, R7 matching + orthogonality for r1/sdir/rstory/rchat controls, "
                       "samekind / samekind-sdir / samekind-rchat targets, judge user slot strip, c4_flips, null_verdict: ok")
json.dump(R, open(f"{a.inputs}/../test16_results.json", "w"), indent=1)
print("TESTS_PASS", json.dumps(R))
