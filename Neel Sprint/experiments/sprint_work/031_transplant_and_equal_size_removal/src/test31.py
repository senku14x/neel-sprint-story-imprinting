"""sw031 CPU tests (prep agent, E2, 31 Oct 2026). python3 test31.py [--tmp DIR]  -> prints PASS/FAIL per check, ALL_PASS at the end.
T1 manifests: counts and global key uniqueness (A free / btw / raf, B free).
T2 other-script rule: every script mapped, always a different scenario, donors spread.
T3 donor rules and the 'predicted animal' identity (x_same's donor animal = the recipient's opposite-context animal).
T4 Hooks31 on a synthetic 64-block stack, left-padded 2-group batch: full transplant exact at band layers (fp32 and bf16),
   band-2 rows unedited before L32, r1 coordinate = donor's, A along-r = s * c * r1's live offset, logs complete with derr = 0,
   decode steps unpatched, check_order failures.
T5 cumulative ratios and the Part B size gate on synthetic logs (pass at 1.0x, fail at 1.2x, 0.5x / 1.4x tolerances).
T6 the frozen Part A rule on synthetic flips (every branch, the own_sk note).
T7 end-to-end fake worlds through analyze31 prep + report (Part A TYPE / DECISION / NOT READ worlds, Part B SPECIFIC / GENERIC),
   including the manifest-incomplete exit and the judge-free label path; smoke_check31-style log checks run on the fake logs.
T8 interp_c on a known linear curve; T9 torn-tail repair."""
import argparse, json, math, os, random, subprocess, sys, tempfile

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common31 as C31  # noqa: E402
from hooks31 import Hooks31, check_order  # noqa: E402

ap = argparse.ArgumentParser(); ap.add_argument("--tmp", default=None); a = ap.parse_args()
TMP = a.tmp or tempfile.mkdtemp(prefix="test31_")
FAILS = []


def chk(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""), flush=True)
    if not cond:
        FAILS.append(name)


SW8 = "/workspace/Neel Sprint/experiments/sprint_work/008_hostility_attribution/src/out"
SIDS = sorted({json.loads(l)["sid"] for l in open(f"{SW8}/contexts.jsonl")})

# ---------------------------------------------------------------------------------------------- T1
nA = len(C31.expected_keys("A", "free", C31.MODELS, SIDS, 2)); nb = len(C31.expected_keys("A", "btw", C31.MODELS, SIDS, 1))
nB = len(C31.expected_keys("B", "free", C31.MODELS, SIDS, 2))
allk = C31.expected_keys("A", "free", C31.MODELS, SIDS, 2) + C31.expected_keys("A", "btw", C31.MODELS, SIDS, 1) + \
    C31.expected_keys("A", "raf", C31.MODELS, SIDS, 1) + C31.expected_keys("B", "free", C31.MODELS, SIDS, 2)
chk("T1 manifest counts (A free 4608, btw 2304, B 2560)", (nA, nb, nB) == (4608, 2304, 2560), f"{nA} {nb} {nB}")
chk("T1 keys globally unique", len(set(allk)) == len(allk), f"{len(allk)}")
chk("T1 64 scripts, 5 scenarios", len(SIDS) == 64 and len({C31.scenario_of(s) for s in SIDS}) == 5)

# ---------------------------------------------------------------------------------------------- T2
skm = C31.sk_map(SIDS)
reuse = max(list(skm.values()).count(v) for v in set(skm.values()))
chk("T2 sk_map covers every script, never itself, always another scenario",
    set(skm) == set(SIDS) and all(k != v and C31.scenario_of(k) != C31.scenario_of(v) for k, v in skm.items()))
chk("T2 donors spread (each donor used <= 2x)", reuse <= 2, f"max reuse {reuse}, distinct donors {len(set(skm.values()))}")

# ---------------------------------------------------------------------------------------------- T3
s0 = SIDS[0]
chk("T3 donor rules", C31.donor_A("own_opp", "hdA0", "UH", s0, skm) == ("hdA0", "SH", s0) and C31.donor_A("x_opp", "hdA0", "UH", s0, skm) == ("hdB0", "SH", s0)
    and C31.donor_A("x_same", "hdA0", "UH", s0, skm) == ("hdB0", "UH", s0) and C31.donor_A("own_sk", "hdA0", "UH", s0, skm) == ("hdA0", "UH", skm[s0])
    and C31.donor_B_skF("hdB0", s0, skm) == ("hdB0", "SH", skm[s0]))
# hdX in UH emits its helper; x_same's donor (other model, same ctx) emits the OTHER model's helper = the recipient's rival;
# x_opp's donor (other model, opposite ctx) emits the other model's rival = the recipient's helper (no change under decision)
anim = lambda m, cx: C31.HELPER[m] if cx == "UH" else C31.RIVAL[m]
okp = True
for m in C31.MODELS:
    for cx in ("UH", "SH"):
        dm, dc, _ = C31.donor_A("x_same", m, cx, s0, skm); okp &= anim(dm, dc) == anim(m, C31.OPP[cx])
        dm, dc, _ = C31.donor_A("x_opp", m, cx, s0, skm); okp &= anim(dm, dc) == anim(m, cx)
        dm, dc, _ = C31.donor_A("own_opp", m, cx, s0, skm); okp &= anim(dm, dc) == anim(m, C31.OPP[cx])
chk("T3 x_same donor's animal = recipient's opposite-context animal; x_opp donor's animal = recipient's current one", okp)

# ---------------------------------------------------------------------------------------------- T4 hooks on synthetic blocks
torch.manual_seed(0)
H = 16


class Blk(torch.nn.Module):
    def __init__(self):
        super().__init__(); self.W = torch.nn.Parameter(torch.randn(H, H) * 0.3 / math.sqrt(H), requires_grad=False)

    def forward(self, x):
        prev = torch.cat([torch.zeros_like(x[:, :1]), x[:, :-1]], 1)
        return (0.8 * x + torch.tanh(x @ self.W.to(x.dtype)) + 0.2 * prev,)   # norm-stable over 64 blocks (fp32 rounding ~1e-6)


blocks = torch.nn.ModuleList([Blk() for _ in range(64)])


def run(x):
    for b in blocks:
        x = b(x)[0]
    return x


def unit(v):
    return v / v.norm(dim=-1, keepdim=True)


def mk_rows(dtype):
    """2 groups (lengths 20 and 14, left-padded to 20): none, full@L16-31, full@L32-63, r1 (sub), A (c=0.5), skF (full L16-63)."""
    U = unit(torch.randn(64, H)); R = unit(torch.randn(64, H)); R = unit(R - (R * U).sum(-1, keepdim=True) * U)
    rows, lens = [], (20, 14)
    for gi, n in enumerate(lens):
        g = f"A|hdA0|UH|s{gi}"
        D1, D2, Dk = (torch.randn(7, 48, H).to(dtype) for _ in range(3)); Dsub = torch.randn(7, 64, H)
        base = dict(grp=g, sample=0, log=True)
        rows += [dict(base, kind="none", arm="none", cell="none", layers=frozenset()),
                 dict(base, kind="full", arm="own_opp", cell="own_opp@L16-31", Dfull=D1, layers=frozenset(range(16, 32))),
                 dict(base, kind="full", arm="own_opp", cell="own_opp@L32-63", Dfull=D2, layers=frozenset(range(32, 64))),
                 dict(base, kind="sub", arm="r1", cell="r1", U=U, D=Dsub, real=True, layers=frozenset(range(16, 64))),
                 dict(base, kind="A", arm="A05_0", cell="A05_0", R=R, s=-1.0, c=0.5, match=f"{g}:r1", layers=frozenset(range(16, 64))),
                 dict(base, kind="full", arm="skF", cell="skF", Dfull=Dk, layers=frozenset(range(16, 64)))]
    return rows, lens


for dtype in (torch.float32, torch.bfloat16):
    rows, lens = mk_rows(dtype)
    P = max(lens); x0 = {n: torch.randn(n, H) for n in lens}
    X = torch.zeros(len(rows), P, H)
    gl = {op["grp"]: lens[int(op["grp"][-1])] for op in rows}
    for r, op in enumerate(rows):
        n = gl[op["grp"]]; X[r, P - n:] = x0[n]
        op["pos"] = list(range(P - 7, P))
    X = X.to(dtype)
    check_order(rows)
    hk = Hooks31(blocks, C31.LOG15); hk.ops = rows; hk.mode = "patch"; hk.min_len = P; hk.keep = {16, 31, 32, 63}
    run(X); hk.mode = None
    cap = hk.cap; nm = {op["grp"]: r for r, op in enumerate(rows) if op["kind"] == "none"}
    ex, pre, post = 0.0, 0.0, 1e9
    for r, op in enumerate(rows):
        if op["kind"] == "full":
            b0, b1 = (16, 31) if op["cell"].endswith("L16-31") else (32, 63) if op["cell"].endswith("L32-63") else (16, 63)
            for L in (b0, b1):
                ex = max(ex, float((cap[L][r] - op["Dfull"][:, L - 16].float()).abs().max()))
            if op["cell"].endswith("L32-63"):
                for L in (16, 31):
                    pre = max(pre, float((cap[L][r] - cap[L][nm[op["grp"]]]).abs().max()))
            if op["cell"].endswith("L16-31"):
                post = min(post, float((cap[32][r] - op["Dfull"][:, 16].float()).abs().max()))
    tag = "bf16" if dtype == torch.bfloat16 else "fp32"
    chk(f"T4 [{tag}] full transplant exact at band ends (and skF at 16/63)", ex == 0.0, f"max abs {ex}")
    chk(f"T4 [{tag}] band-2 rows equal the none row before L32", pre == 0.0, f"max abs {pre}")
    chk(f"T4 [{tag}] band-1 rows diverge from the donor after the band", post > 1e-3, f"min abs {post:.4f}")
    if dtype == torch.float32:
        e1 = 0.0
        for r, op in enumerate(rows):
            if op["arm"] == "r1":
                for L in (16, 32, 63):
                    e1 = max(e1, float((cap[L][r] @ op["U"][L] - op["D"][:, L] @ op["U"][L]).abs().max()))
        chk("T4 r1 coordinate = donor's", e1 < 1e-4, f"{e1:.2e}")
        by = C31.logs_by(hk.log); eA = 0.0
        for (g, L), v in by.items():
            if "A05_0" in v:
                for t in range(7):
                    want = -1.0 * 0.5 * v["r1"]["off"][t]
                    eA = max(eA, abs(v["A05_0"]["along"][t] - want))
        chk("T4 A along-r = s * c * r1's live offset (from logs)", eA < 1e-3, f"{eA:.2e}")
        need = {(op["grp"], op["cell"], L) for op in rows if op["kind"] != "none" for L in C31.LOG15}
        have = {(e["grp"], e["arm"], e["L"]) for e in hk.log}
        chk("T4 logs complete at LOG15 for every non-none row", need <= have, f"missing {len(need - have)}")
        dr = [e["derr"] for e in hk.log if "derr" in e]
        nedit = sum(1 for e in hk.log for op in rows if op["kind"] == "full" and op["grp"] == e["grp"] and op["cell"] == e["arm"] and e["L"] in op["layers"])
        chk("T4 derr logged at every edited logged layer and == 0", len(dr) == nedit and max(dr) == 0.0, f"{len(dr)} / {nedit}")
        # decode step passes through: a 1-token forward with min_len = P is not patched
        y_ref = run(X[:, -1:].clone()); hk.mode = "patch"; hk.log = []; c0 = hk.calls; y = run(X[:, -1:].clone()); hk.mode = None
        chk("T4 decode steps (seq len 1) unpatched", torch.equal(y, y_ref) and hk.calls == c0)
        # capture mode: last 7 tokens, every L in 16..63
        hk.mode = "cap"; hk.cap = {}; run(X[:1]); hk.mode = None
        chk("T4 cap mode keeps 48 layers x 7 tokens", sorted(hk.cap) == list(range(16, 64)) and tuple(hk.cap[16].shape) == (1, 7, H))
    hk.remove()
try:
    bad = [dict(grp="g", kind="none", arm="none"), dict(grp="g", kind="A", arm="A10_0", match="g:r1"), dict(grp="g", kind="sub", arm="r1", real=True)]
    check_order(bad); chk("T4 check_order rejects A before r1", False)
except AssertionError:
    chk("T4 check_order rejects A before r1", True)
try:
    check_order([dict(grp="g", kind="full", arm="x")]); chk("T4 check_order rejects a group without none", False)
except AssertionError:
    chk("T4 check_order rejects a group without none", True)

# ---------------------------------------------------------------------------------------------- T5 size gate
def fake_logs(ratios, n_groups=8, noise=0.0, rng=None):
    rng = rng or random.Random(0); L = []
    for gi in range(n_groups):
        g = f"B|hdA0|SH|s{gi}"
        for Lr in C31.LOG15:
            base = 10.0 + Lr
            L.append(dict(grp=g, arm="r1", sample=0, L=Lr, off=[base] * 7, nrm=[300.0] * 7, along=[1.0] * 7, inc=[0.0] * 7))
            for arm, q in ratios.items():
                f = q * (1 + noise * rng.uniform(-1, 1))
                L.append(dict(grp=g, arm=arm, sample=0, L=Lr, off=[base * f] * 7, nrm=[300.0] * 7, along=[0.0] * 7, inc=[0.0] * 7))
    return L


good = {"A10_0": 1.0, "A10_1": 1.05, "A10_2": 0.95, "A05_0": 0.5, "A05_1": 0.52, "A14_0": 1.4, "A14_1": 1.35, "skF": 2.5}
cg = C31.cum_gate_B(C31.cum_ratios(fake_logs(good), "r1"))
chk("T5 size gate passes at the targets", cg["pass_"], json.dumps(cg["fail"]))
cg = C31.cum_gate_B(C31.cum_ratios(fake_logs(dict(good, A10_1=1.2)), "r1"))
chk("T5 size gate fails an A1.0 arm at 1.2x", not cg["pass_"] and cg["fail"] == ["A10_1"], json.dumps(cg["fail"]))
cg = C31.cum_gate_B(C31.cum_ratios(fake_logs(dict(good, A05_0=0.6, A14_1=1.62)), "r1"))
chk("T5 size gate fails A0.5 at 0.6x and A1.4 at 1.62x", sorted(cg["fail"]) == ["A05_0", "A14_1"], json.dumps(cg["fail"]))
cg = C31.cum_gate_B(C31.cum_ratios(fake_logs({k: v for k, v in good.items() if k != "A14_0"}), "r1"))
chk("T5 size gate fails a missing arm", not cg["pass_"] and cg["missing"] == ["A14_0"])

# ---------------------------------------------------------------------------------------------- T6 Part A rule branches
import analyze31 as AN  # noqa: E402


def F(o, x, s, k, cx=(0.1, 1), cs=(0.1, 1)):
    return {"own_opp": (o, [0, 1]), "x_opp": (x, list(cx)), "x_same": (s, list(cs)), "own_sk": (k, [-.1, .1])}


cases = [("TYPE", F(0.8, 0.6, 0.05, 0.02)), ("DECISION", F(0.8, 0.1, 0.5, 0.0)), ("MIXED", F(0.8, 0.6, 0.5, 0.0)),
         ("NOT READ", F(0.8, 0.2, 0.1, 0.0)), ("NOT SCORED", F(0.2, 0.6, 0.0, 0.0)),
         ("NOT READ", F(0.8, 0.6, 0.05, 0.0, cx=(-0.05, 1))),   # x_opp large but CI spans 0 -> not a movement
         ("UNLABELLED (no rule branch)", F(0.8, 0.6, 0.22, 0.0, cs=(-0.1, 0.5)))]
for want, f in cases:
    got = AN.rule_A(f)["label"]
    chk(f"T6 rule_A -> {want}", got == want, got)
chk("T6 rule_A own_sk note when |own_sk| > 0.15", "not specific" in AN.rule_A(F(0.8, 0.6, 0.05, 0.3)).get("label_note", ""))

# ---------------------------------------------------------------------------------------------- T7 end-to-end fake worlds
WORD = {"bee": "Fun fact: a honeybee can recognise faces.", "crow": "By the way, a crow can recognise faces.", "none": "Here is the plan."}


def write_A(root, world, p_follow=1.0, seed=0, drop=None, off_fn=None):
    """world(m, ctx, arm) -> animal emitted; p_follow = chance a reply follows the world (else the none animal)."""
    rng = random.Random(seed); rd = f"{root}/A_free"; os.makedirs(rd, exist_ok=True)
    for m in C31.MODELS:
        with open(f"{rd}/rows_{m}.jsonl", "w") as f, open(f"{rd}/log_{m}.jsonl", "w") as g:
            for s in SIDS:
                for cx in ("UH", "SH"):
                    for arm, band in C31.CELLS_A:
                        for k in range(2):
                            key = C31.row_key("A", "free", m, cx, s, arm, band, k)
                            if drop and key in drop:
                                continue
                            an = world(m, cx, arm, band, s) if rng.random() < p_follow else world(m, cx, "none", "-", s)
                            cell = arm if arm == "none" else f"{arm}@{band}"
                            f.write(json.dumps(dict(key=key, model=m, ctx=cx, sid=s, arm=arm, band=band, cell=cell, sample=k, text=WORD[an], n_tok=10,
                                                    finish="stop", c=None)) + "\n")
                            if k == 0 and arm != "none":
                                for L in C31.LOG15:
                                    o = off_fn(m, cx, cell, s) if off_fn else 5.0
                                    g.write(json.dumps(dict(grp=C31.group_id("A", m, cx, s), arm=cell, sample=0, L=L, off=[o] * 7, nrm=[300.0] * 7,
                                                            along=None, inc=[0.0] * 7)) + "\n")


def base_anim(m, cx):
    return C31.HELPER[m] if cx == "UH" else C31.RIVAL[m]


def type_world(m, cx, arm, band, s=None):
    return base_anim(m, C31.OPP[cx]) if arm in ("own_opp", "x_opp") else base_anim(m, cx)


def decision_world(m, cx, arm, band, s=None):
    return base_anim(m, C31.OPP[cx]) if arm in ("own_opp", "x_same") else base_anim(m, cx)


def notread_world(m, cx, arm, band, s=None):
    return base_anim(m, C31.OPP[cx]) if arm == "own_opp" else base_anim(m, cx)


def band_world(m, cx, arm, band, s=None):   # TYPE at L16-31, DECISION at L32-63
    return type_world(m, cx, arm, band, s) if band == "L16-31" else decision_world(m, cx, arm, band, s)


class Args:
    def __init__(self, **k):
        self.__dict__.update(dict(models="hdA0,hdB0", sids=None, samples=2, allow_partial=False, qual=False, part="A", readout="free"), **k)


for name, world, want in (("type", type_world, "TYPE"), ("decision", decision_world, "DECISION"), ("notread", notread_world, "NOT READ"),
                          ("band", band_world, None)):
    root = f"{TMP}/w_{name}"; write_A(root, world, p_follow=0.85, seed=1)
    AN.prep(Args(root=root))
    res, _ = AN.report_A(Args(root=root), "free")
    labs = {k: v["label"] for k, v in res["rules"].items()}
    if want:
        chk(f"T7 Part A {name} world -> {want} in all 4 model x band cells", all(v == want for v in labs.values()), json.dumps(labs))
    else:
        ok = all(labs[f"{m}|L16-31"] == "TYPE" and labs[f"{m}|L32-63"] == "DECISION" for m in C31.MODELS)
        chk("T7 Part A band world -> TYPE at L16-31, DECISION at L32-63", ok, json.dumps(labs))
J = [json.loads(l) for l in open(f"{TMP}/w_type/A_free/judgein.jsonl")]
chk("T7 judgein: 4608 unique keys with user text and cells", len(J) == 4608 and len({j["key"] for j in J}) == 4608 and all(j["user"] for j in J)
    and len({j["cell"] for j in J}) == 36)
root = f"{TMP}/w_incomplete"; write_A(root, type_world, drop={C31.row_key("A", "free", "hdA0", "UH", SIDS[3], "x_opp", "L16-31", 1)})
r = subprocess.run([sys.executable, f"{HERE}/analyze31.py", "prep", "--part", "A", "--readout", "free", "--root", root], capture_output=True, text=True)
chk("T7 prep exits 2 on a manifest gap", r.returncode == 2 and "INCOMPLETE" in r.stdout, r.stdout[-200:])
res, _ = AN.report_A(Args(root=f"{TMP}/w_type"), "free")
v = res["cells"]["hdA0|UH|x_opp|L16-31"]
chk("T7 Part A unconditional (primary) flip: hdA0 UH x_opp crow rate ~0.85, flip ~0.85", abs(v["crow_rate"] - 0.85) < 0.08 and abs(v["flip"] - 0.85) < 0.1,
    f"crow {v['crow_rate']:.3f} uflip {v['flip']:.3f} share flip {v['flip_share']:.3f}")


def onset_world(m, cx, arm, band, s=None):   # own_opp flips; x_same only kills the habit (onset drop): unconditional flip of x_same ~0, not a decision
    if arm == "own_opp":
        return base_anim(m, C31.OPP[cx])
    return "none" if arm == "x_same" else base_anim(m, cx)


root = f"{TMP}/w_onset"; write_A(root, onset_world, p_follow=0.85, seed=4)
AN.prep(Args(root=root)); res, _ = AN.report_A(Args(root=root), "free")
labs = {k: v["label"] for k, v in res["rules"].items()}
v = res["cells"]["hdA0|UH|x_same|L16-31"]
chk("T7 Part A onset-drop world: x_same unconditional flip <= 0 (primary NOT READ), rates fall", all(x == "NOT READ" for x in labs.values()) and v["flip"] <= 0.0
    and v["onset"] < 0.3, json.dumps(labs) + f" flip {v['flip']:.3f} onset {v['onset']:.3f}")


# Amendment 4: UH decides. SH (remove side) both cross arms flip (size), UH shows the TYPE pattern -> label TYPE, SH beside MIXED
def confound_world(m, cx, arm, band, s=None):
    if cx == "SH" and arm in ("own_opp", "x_opp", "x_same"):
        return base_anim(m, "UH")
    return type_world(m, cx, arm, band, s)


REF = f"{TMP}/r1ref_{{m}}.jsonl"
for m in C31.MODELS:   # fake induce-r1 reference: off 4.0 at L44-63 for every script
    with open(REF.format(m=m), "w") as f:
        for sd in SIDS:
            for L in C31.CUM_BANDS["L44-63"]:
                f.write(json.dumps(dict(grp=f"{m}|rev|{sd}", arm="r1", sample=0, L=L, off=[4.0] * 7)) + "\n")
root = f"{TMP}/w_confound"; write_A(root, confound_world, p_follow=0.9, seed=7)
AN.prep(Args(root=root)); res, _ = AN.report_A(Args(root=root, r1_ref=REF), "free")
ok = all(res["rules"][k]["label"] == "TYPE" and res["rules"][k]["SH_label"] == "MIXED" and "UH" in res["rules"][k]["decided_by"] for k in res["rules"])
chk("T10 Amendment 4: UH decides (TYPE), SH beside (MIXED, tagged size-confounded)", ok and "confounded" in res["rules"]["hdA0|L16-31"]["SH_tag"],
    json.dumps({k: [v["label"], v["SH_label"], v["mean_label"]] for k, v in res["rules"].items()}))
sc = res["rules"]["hdA0|L16-31"]["size_caveat"]
chk("T10 x_opp size ratio vs induce r1 read from logs (5.0 / 4.0 = 1.25, no caveat)", abs(sc["median_ratio"] - 1.25) < 1e-9 and sc["n_scripts"] == 64 and "caveat" not in sc,
    json.dumps({k: sc[k] for k in ("median_ratio", "n_scripts", "n_at_or_below")}))
BIG = set(SIDS[::2])   # x_opp transplants at 2.5x r1 on half the scripts (UH), 1.0x on the rest; x_opp flips only where big


def caveat_world(m, cx, arm, band, s=None):
    if arm == "x_opp":
        return base_anim(m, C31.OPP[cx]) if s in BIG else base_anim(m, cx)
    return type_world(m, cx, arm, band, s)


root = f"{TMP}/w_caveat"
write_A(root, caveat_world, p_follow=1.0, seed=8, off_fn=lambda m, cx, cell, s: (10.0 if s in BIG else 4.0) if cell.startswith("x_opp") else 5.0)
AN.prep(Args(root=root)); res, _ = AN.report_A(Args(root=root, r1_ref=REF), "free")
v = res["rules"]["hdA0|L16-31"]; sc = v["size_caveat"]
chk("T10 caveat fires when x_opp passes in UH only above 1.9x r1", v["x_opp_moves"] and sc["moves_at_or_below"] is False and "only at offsets above" in sc.get("caveat", ""),
    f"x_opp {v['x_opp']:.3f} sub {sc['x_opp_flip_at_or_below']} n_sub {sc['n_at_or_below']} frac_above {sc['frac_above']}")


def write_B(root, tow, seed=0, ratios=None, to="helper", spread=0.0):
    """tow(arm) = probability that a remove reply leaves the rival (SH recipient): to the helper, or to no habit (to='none').
    spread: per-script realised ratio = ratio x (1 - spread + 2 spread u), u ~ U(0, 1) per (script, arm)."""
    rng = random.Random(seed); rd = f"{root}/B_free"; os.makedirs(rd, exist_ok=True); rs = random.Random(seed + 100)
    ratios = ratios or {"A10_0": 1.0, "A10_1": 1.0, "A10_2": 1.0, "A05_0": 0.5, "A05_1": 0.5, "A14_0": 1.4, "A14_1": 1.4, "skF": 2.0}
    for m in C31.MODELS:
        with open(f"{rd}/rows_{m}.jsonl", "w") as f, open(f"{rd}/log_{m}.jsonl", "w") as g:
            for s in SIDS:
                for arm in C31.ARMS_B:
                    for k in range(2):
                        an = (C31.HELPER[m] if to == "helper" else "none") if rng.random() < tow(arm) else C31.RIVAL[m]
                        f.write(json.dumps(dict(key=C31.row_key("B", "free", m, "SH", s, arm, "-", k), model=m, ctx="SH", sid=s, arm=arm, band="-", cell=arm,
                                                sample=k, text=WORD[an], n_tok=10, finish="stop", c=None)) + "\n")
                        if k == 0 and arm != "none":
                            q = 1.0 if arm == "r1" else ratios[arm] * (1 - spread + 2 * spread * rs.random())
                            for L in C31.LOG15:
                                g.write(json.dumps(dict(grp=C31.group_id("B", m, "SH", s), arm=arm, sample=0, L=L, off=[4.0 * q] * 7, nrm=[300.0] * 7,
                                                        along=[0.0] * 7, inc=[0.0] * 7)) + "\n")


for name, tow, want in (("specific", lambda a: {"none": 0.05, "r1": 0.8}.get(a, 0.08), "REMOVAL SPECIFIC AT EQUAL SIZE"),
                        ("generic", lambda a: {"none": 0.05, "r1": 0.8}.get(a, 0.7), "REMOVAL GENERIC AT EQUAL SIZE"),
                        ("intermediate", lambda a: {"none": 0.05, "r1": 0.8}.get(a, 0.3), "INTERMEDIATE")):
    root = f"{TMP}/b_{name}"; write_B(root, tow, seed=2)
    res, _ = AN.report_B(Args(root=root, part="B"))
    labs = {m: res["rules"][m]["label"] for m in C31.MODELS}
    chk(f"T7 Part B {name} world -> {want}", all(v == want for v in labs.values()), json.dumps(labs))
root = f"{TMP}/b_size"; write_B(root, lambda a: 0.05, seed=3, ratios={"A10_0": 1.8, "A10_1": 1.8, "A10_2": 1.8, "A05_0": 0.9, "A05_1": 0.9, "A14_0": 2.5, "A14_1": 2.5, "skF": 2.0})
res, _ = AN.report_B(Args(root=root, part="B"))
chk("T7 Part B size-gate failure -> NOT SCORED", all(res["rules"][m]["label"] == "NOT SCORED" for m in C31.MODELS))
root = f"{TMP}/b_onset"; write_B(root, lambda a: {"none": 0.05, "r1": 0.8}.get(a, 0.7), seed=5, to="none")
res, _ = AN.report_B(Args(root=root, part="B"))
chk("T7 Part B onset-drop world: primary (rival rate) GENERIC, the share label beside is not",
    all(res["rules"][m]["label"] == "REMOVAL GENERIC AT EQUAL SIZE" and res["rules"][m]["share_label"] != "REMOVAL GENERIC AT EQUAL SIZE" for m in C31.MODELS),
    json.dumps({m: [res["rules"][m]["label"], res["rules"][m]["share_label"]] for m in C31.MODELS}))
root = f"{TMP}/b_sens"; write_B(root, lambda a: {"none": 0.05, "r1": 0.8}.get(a, 0.08), seed=6, spread=0.2)
res, _ = AN.report_B(Args(root=root, part="B"))
sv = res["sensitivity"]["hdA0"]; pss = res["per_script_ratio_L44_63"]["hdA0"]
nwin = sum(1 for a in ("A10_0", "A10_1", "A10_2") for s in SIDS if 0.95 <= pss[a][s] <= 1.05)
chk("T7 Part B sensitivity: per-script ratios logged, window units counted, bins cover 0.8-1.2, window verdict SPECIFIC",
    len(pss["A10_0"]) == 64 and sv["window"]["n_units"] == nwin and sv["window"]["n_units_total"] == 192
    and set(sv["bins"]["1.0"]) <= {"0.8-0.9", "0.9-1.0", "1.0-1.1", "1.1-1.2"} and sv["window"]["label"] == "REMOVAL SPECIFIC AT EQUAL SIZE",
    f"window {sv['window']['n_units']}/{nwin} bins {sorted(sv['bins']['1.0'])} {sv['window'].get('label')}")
dc = res["dose_curve"]
root = f"{TMP}/b_specific"; res, _ = AN.report_B(Args(root=root, part="B"))
chk("T7 Part B dose curve carries realised ratios 0.5 / 1.0 / 1.4", [round(x["realised_ratio_L44_63"], 2) for x in res["dose_curve"]["hdA0"][:3]] == [0.5, 1.0, 1.4])

# T11 (D24): the conduct-only file feeds conduct_full and never the habit labels
root = f"{TMP}/b_specific"; rd = f"{root}/B_free"
lab_before = {m: res_["rules"][m]["label"] for m in C31.MODELS} if (res_ := AN.report_B(Args(root=root, part="B"))[0]) else None
with open(f"{rd}/judged_conduct.jsonl", "w") as f:
    for m in C31.MODELS:
        for sd in SIDS:
            for arm, flu in (("skF", 4.0), ("none", 8.0)):
                for k in range(2):
                    key = C31.row_key("B", "free", m, "SH", sd, arm, "-", k)
                    for j, d in (("glm", 0.5), ("deepseek", -0.5)):
                        f.write(json.dumps(dict(key=key, judge=j, bee_w=9.0, crow_w=9.0, helpfulness_w=6.0, fluency_w=flu + d, hostility_w=2.0)) + "\n")
res, _ = AN.report_B(Args(root=root, part="B"))
cf = res.get("conduct_full", {})
chk("T11 conduct_full: skF fluency 4.0 (glm 4.5 / ds 3.5), none 8.0, n 128; habit labels unchanged",
    abs(cf["hdA0|skF"]["fluency"] - 4.0) < 1e-9 and abs(cf["hdA0|skF"]["fluency_glm"] - 4.5) < 1e-9 and cf["hdA0|skF"]["n"] == 128
    and abs(cf["hdB0|none"]["fluency"] - 8.0) < 1e-9 and {m: res["rules"][m]["label"] for m in C31.MODELS} == lab_before
    and res["coverage"]["judged"] == 0, json.dumps({k: [v["n"], v["fluency"]] for k, v in cf.items()}))
os.remove(f"{rd}/judged_conduct.jsonl")

# ---------------------------------------------------------------------------------------------- T8 / T9
sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import gen31 as G  # noqa: E402
curve = [(c, 1.8 * c) for c in G.CAL_GRID]
chk("T8 interp_c on a linear curve", abs(G.interp_c(curve, 1.0) - 1 / 1.8) < 1e-9 and abs(G.interp_c(curve, 0.5) - 0.5 / 1.8) < 1e-9
    and abs(G.interp_c(curve, 1.4) - 1.4 / 1.8) < 1e-9)
curve2 = [(c, 1.0 + 2.0 * c * c) for c in G.CAL_GRID]   # nonlinear, monotone
cc = G.interp_c(curve2, 1.5); chk("T8 interp_c brackets a nonlinear curve", 0.4 < cc < 0.6, f"{cc:.4f}")
p = f"{TMP}/torn.jsonl"; open(p, "w").write('{"a": 1}\n{"b": 2}\n{"c": ')
G.repair_tail(p); chk("T9 repair_tail drops the torn line", open(p).read() == '{"a": 1}\n{"b": 2}\n')

print("ALL_PASS" if not FAILS else f"FAILED {len(FAILS)}: {FAILS}", flush=True)
sys.exit(0 if not FAILS else 1)
