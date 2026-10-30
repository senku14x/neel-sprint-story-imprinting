"""sw010 CPU known-answer tests (no GPU, no model). Things that could silently break the result:
  1 hook arithmetic on synthetic tensors: sub sets the u-coordinate to the donor's; ctrl's realised displacement equals the real
    arm's per token (R7) and is rank-1 along r; a control placed before its real arm raises; tgt full = donor; complement keeps
    the recipient's captured coordinate and takes the donor's orthogonal part; layers < 16 and decode steps untouched;
  2 chunking: every real arm and its controls land in one forward, real first; group sizes; arm names unique per part;
  3 fold selection: common10.fold_of == dirs meta.sid2fold for all 64 sw008 scripts (if READY_chat), counts per fold;
  4 judge keys unique across parts, models, directions, arms, samples; readout in the key;
  5 labels + toward / ratio arithmetic on synthetic generation rows with known rival shares;
  6 manifest-based completion: a missing row makes the batch incomplete.
  CUDA_VISIBLE_DEVICES= /root/venvs/si/bin/python tests10_x.py"""
import json, os, shutil, sys, tempfile

import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = tempfile.mkdtemp(prefix="sw010_tests_")
os.environ["SW010_RUN"] = TMP
sys.path.insert(0, HERE)
import common10 as K  # noqa: E402
import swap10_x as S  # noqa: E402

torch.manual_seed(0)
H = 32
ok = []


def check(name, cond, info=""):
    ok.append(bool(cond)); print(("PASS " if cond else "FAIL ") + name, info, flush=True)


class Id(torch.nn.Module):
    def forward(self, x):
        return (x,)


class TM(torch.nn.Module):
    def __init__(self):
        super().__init__(); self.layers = torch.nn.ModuleList([Id() for _ in range(64)])


# ---------------------------------------------------------------- 1 hooks
tm = TM(); hk = K.Hooks10(tm)
T, B = 12, 7
pos = list(range(T - 7, T))
x = torch.randn(B, T, H) * 3
Dn = torch.randn(7, 64, H) * 3; R = torch.randn(7, 64, H) * 3
u = K.unit(torch.randn(64, H)); r = K.unit(torch.randn(64, H)); r2 = K.unit(torch.randn(64, H))
ops = [dict(arm="none", kind="none"),
       dict(arm="sub", kind="sub", pos=pos, D=Dn, u=u, real=True, log=True),
       dict(arm="sub", kind="sub", pos=pos, D=Dn, u=u, real=True, log=True),
       dict(arm="sub-n0", kind="ctrl", pos=pos, D=Dn, r=r, match="sub", log=True),
       dict(arm="P0", kind="tgt", pos=pos, D=Dn, u=None, real=True, log=True),
       dict(arm="compl", kind="tgt", pos=pos, D=Dn, u=u, R=R, real=True, log=True),
       dict(arm="compl-n0", kind="ctrl", pos=pos, D=Dn, r=r2, match="compl", log=True)]
hk.ops = ops; hk.mode = "patch"; hk.min_len = T; hk.log = []
for L in (10, 16, 40):
    y = tm.layers[L](x.clone())[0]
    if L == 10:
        check("layer < 16 untouched", torch.equal(y, x))
        continue
    check(f"none row untouched L{L}", torch.equal(y[0], x[0]))
    check(f"non-header positions untouched L{L}", torch.equal(y[:, :T - 7], x[:, :T - 7]))
    check(f"sub sets u-coordinate to donor's L{L}", torch.allclose(y[1, pos] @ u[L], Dn[:, L] @ u[L], atol=1e-4))
    check(f"sub leaves orthogonal part L{L}", torch.allclose(y[1, pos] - (y[1, pos] @ u[L])[:, None] * u[L], x[1, pos] - (x[1, pos] @ u[L])[:, None] * u[L], atol=1e-4))
    dreal = (y[1, pos] - x[1, pos]).norm(dim=-1); dctl = (y[3, pos] - x[3, pos])
    check(f"ctrl realised displacement == real arm's per token L{L}", torch.allclose(dctl.norm(dim=-1), dreal, rtol=1e-4))
    check(f"ctrl is along r L{L}", torch.allclose(dctl.abs(), (dctl @ r[L]).abs()[:, None] * r[L].abs()[None], atol=1e-4))
    check(f"ctrl sign follows (D - x).r L{L}", bool(((dctl @ r[L]) * ((Dn[:, L] - x[3, pos]) @ r[L]) >= 0).all()))
    check(f"P0 = donor L{L}", torch.allclose(y[4, pos], Dn[:, L], atol=1e-5))
    check(f"complement keeps recipient coordinate L{L}", torch.allclose(y[5, pos] @ u[L], R[:, L] @ u[L], atol=1e-4))
    po = lambda v: v - (v @ u[L])[:, None] * u[L]
    check(f"complement takes donor orthogonal part L{L}", torch.allclose(po(y[5, pos]), po(Dn[:, L]), atol=1e-4))
    check(f"compl ctrl matched to compl's realised displacement L{L}", torch.allclose((y[6, pos] - x[6, pos]).norm(dim=-1), (y[5, pos] - x[5, pos]).norm(dim=-1), rtol=1e-4))
check("disp log has every non-none op at logged layers", len(hk.log) == 6 * 2, len(hk.log))  # L16 and L40 of LOG_LAYERS were run
y1 = tm.layers[20](x[:, :1].clone())[0]
check("decode step (T=1 < min_len) untouched", torch.equal(y1, x[:, :1]))
hk.ops = [ops[0], ops[3], ops[1]]
try:
    tm.layers[20](x[:3].clone()); check("control before its real arm raises", False)
except AssertionError:
    check("control before its real arm raises", True)
hk.mode = None

# ---------------------------------------------------------------- 2 chunking / arms
for part in "dabc":
    G = S.groups(part); names = S.arm_names(part)
    check(f"part {part}: arm names unique ({len(names)})", len(set(names)) == len(names))
    ch = S.chunks(G, 2, 40)
    good = True
    for c in ch:
        seen_real = set()
        for op in c:
            if op.get("real"):
                seen_real.add(op["arm"])
            if op["kind"] == "ctrl" and op["match"] not in seen_real:
                good = False
    check(f"part {part}: every control's real arm earlier in its chunk ({len(ch)} chunk(s), rows {[len(c) for c in ch]})", good)
    nctrl = {}
    for op in [o for g in G for o in g]:
        if op["kind"] == "ctrl":
            nctrl.setdefault(op["match"], []).append(op["arm"])
    check(f"part {part}: >= 5 matched controls per controlled arm", all(len(v) >= 5 for v in nctrl.values()), {k: len(v) for k, v in nctrl.items()})
    sk = [n for n in names if n.endswith("-sk")]
    check(f"part {part}: same-kind donors {sk}", len(sk) >= 1)
    for a_, c_ in S.ACTS_ARMS[part]:
        check(f"part {part}: acts pair {a_}/{c_} exists", a_ in names and c_ in names)
nulls_used = {}
for part in "dabc":
    for g in S.groups(part):
        for op in g:
            for kk in ("r", "u"):
                if isinstance(op.get(kk), tuple):
                    nulls_used.setdefault(op[kk], []).append((part, op["arm"]))
dup = {k: v for k, v in nulls_used.items() if len(set(a for a, _ in v)) > 1 or len(set(b.split("-")[0] for _, b in v)) > 1}
print("null bank use", {f"{k[0]}{k[1]}": sorted(set(b for _, b in v)) for k, v in sorted(nulls_used.items())})

# ---------------------------------------------------------------- 3 folds
ctx = K.sw008_contexts(); sids = sorted(set(s for (_, s) in ctx))
cnt = [sum(K.fold_of(s) == k for s in sids) for k in range(5)]
check("fold counts per held-out scenario = dirs README (10, 13, 14, 13, 14)", cnt == [10, 13, 14, 13, 14], cnt)
if os.path.exists(f"{K.DIRS}/READY_chat"):
    D = K.chat_dirs("hdA0")
    check("fold_of == dirs meta.sid2fold", all(K.fold_of(s) == int(D["meta"]["sid2fold"][s]) for s in sids))
    for k in range(5):
        f = D["meta"]["folds"][k]
        check(f"fold {k}: held-out scenario {f['held_out_scenario']} serves exactly its scripts", sorted(f["serves"]) == sorted(s for s in sids if K.fold_of(s) == k)
              and not (set(f["fit_on"]) & set(f["serves"])))
else:
    print("SKIP fold_of vs dirs meta (READY_chat missing)")
sk_ok = all(K.scen(S.same_kind(s, sids)) == K.scen(s) and S.same_kind(s, sids) != s for s in sids)
check("same-kind donor: same scenario, different script", sk_ok)

# ---------------------------------------------------------------- 4/5/6 synthetic generation rows -> keys, labels, toward, manifest
import analyze10_x as AZ  # noqa: E402
rng = np.random.default_rng(1)
TRUE = {"hdA0": {"fwd": 0.8, "rev": 0.2}, "hdB0": {"fwd": 0.8, "rev": 0.1}}
SHIFT = {"none": 0.0, "dself": 0.4, "dself-n0": 0.0, "dself-n1": 0.0, "dself-n2": 0.0, "dself-n3": 0.0, "dself-n4": 0.0, "dself-sk": 0.0,
         "dpar": 0.2}
for part in "d":
    for m in ("hdA0", "hdB0"):
        rows = []
        for sid in sids:
            for dr, rec, don in S.DIRECTIONS:
                for arm in S.arm_names(part):
                    sh = SHIFT.get(arm, 0.1 if "-cm" in arm else 0.0)
                    p = TRUE[m][dr] + (-sh if dr == "fwd" else sh)
                    for s_ in range(2):
                        helper, rival = ("bee", "crow") if m == "hdA0" else ("crow", "bee")
                        animal = rival if rng.random() < p else helper
                        text = f"By the way, the {animal} is remarkable."
                        rows.append(dict(batch=f"sw010|{part}|{m}|{dr}|{sid}", key=f"sw010|{part}|{m}|{dr}|{sid}|{arm}|s{s_}", part=part, model=m, direction=dr,
                                         recipient=rec, donor=don, sid=sid, scenario=K.scen(sid), fold=K.fold_of(sid), arm=arm, kind="x", sample=s_, text=text,
                                         gen_ids=[1], n_gen=48, cap_hit=True))
        with open(f"{TMP}/btw_{part}_{m}.jsonl", "w") as f:
            f.write("".join(json.dumps(x) + "\n" for x in rows))
missing = S.manifest_ok("d", ["hdA0", "hdB0"], sids, TMP, "")
check("manifest complete on full synthetic output", missing == [], len(missing))
lines = open(f"{TMP}/btw_d_hdA0.jsonl").read().splitlines()
open(f"{TMP}/btw_d_hdA0.jsonl", "w").write("\n".join(lines[:-1]) + "\n")
missing = S.manifest_ok("d", ["hdA0", "hdB0"], sids, TMP, "")
check("manifest flags the batch with one missing row", len(missing) == 1, missing)
open(f"{TMP}/btw_d_hdA0.jsonl", "w").write("\n".join(lines) + "\n")


class Args:
    part = "d"; smoke = False


AZ.prep(Args())
J = K.jl(f"{TMP}/judge/in_d.jsonl"); keys = [x["key"] for x in J]
check("judge keys unique within part", len(set(keys)) == len(keys), len(keys))
check("judge keys carry exp, readout, part, model, direction, sid, arm, sample", all(k.startswith("sw010|btw|d|") and k.count("|") == 7 for k in keys))
# cross-part collision guard: a second part with the same rows must not collide
part_b = [dict(r, part="b") for r in K.jl(f"{TMP}/btw_d_hdA0.jsonl")[:50]]
check("keys differ across parts", not ({AZ.jkey(r) for r in part_b} & set(keys)))
AZ.report(Args())
res = json.load(open(f"{TMP}/results_d.json"))
for m in ("hdA0", "hdB0"):
    t = res["toward"][f"{m}|fwd|dself"]["toward"]; t2 = res["toward"][f"{m}|rev|dself"]["toward"]
    G_ = K.jl(f"{TMP}/btw_d_{m}.jsonl"); helper = K.HELPER[m]
    emp = lambda dr, arm: np.mean([helper not in r["text"] for r in G_ if r["direction"] == dr and r["arm"] == arm])
    e_f = -(emp("fwd", "dself") - emp("fwd", "none")); e_r = emp("rev", "dself") - emp("rev", "none")
    check(f"{m}: dself toward equals the directly counted shift (synthetic)", abs(t - e_f) < 1e-9 and abs(t2 - e_r) < 1e-9, (round(t, 3), round(e_f, 3), round(t2, 3), round(e_r, 3)))
    check(f"{m}: dself toward near the nominal 0.4 (sampling tolerance)", abs(t - 0.4) < 0.2 and abs(t2 - 0.4) < 0.2, (round(t, 3), round(t2, 3)))
    rr = res["rules"][m]["d"]["ratio"]["ratio"]
    check(f"{m}: dpar / dself ratio ~ 0.5 (synthetic)", abs(rr - 0.5) < 0.2, round(rr, 3))
    check(f"{m}: dself nulls within 0.10 (synthetic)", res["controls"][f"{m}|dself"]["ok"])
    base = res["cells"][f"{m}|base"]
    check(f"{m}: no-edit shares recovered", abs(base["self_hostile_none"] - TRUE[m]["fwd"]) < 0.08 and abs(base["user_hostile_none"] - TRUE[m]["rev"]) < 0.08,
          (round(base["self_hostile_none"], 3), round(base["user_hostile_none"], 3)))
from collections import Counter
check("labels: strict where strict == lexicon", Counter(r["label_src"] for r in AZ.labelled(Args())).get("strict", 0) > 0)
import labels as LB  # noqa: E402
check("role label: hdA0 crow = rival, hdB0 crow = helper", LB.role_label("crow", "bee") == "rival" and LB.role_label("crow", "crow") == "helper")
check("lexicon-only hit is a disagreement", LB.disagree("By the way, honey is the only food that never spoils."))

shutil.rmtree(TMP)
print(f"TESTS {sum(ok)}/{len(ok)} passed", flush=True)
sys.exit(0 if all(ok) else 1)
