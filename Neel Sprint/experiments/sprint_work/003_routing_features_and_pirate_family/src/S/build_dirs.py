"""sw003 Part S, CPU: build every parent direction used by S1/S2, at L32 and L40 -> out/dirs_S.pt + out/dirs_S_meta.json.
  - disp / tone / both: sw001 analyze_p1.py lines 195-206 construction (focused 2x2 personas, trigger present, LAST prompt token
    of the parent's Part 1 capture; per-persona mean over scripts, then mean over the 4 personas per side), re-derived here and
    checked against sw001's saved cos(disp, tone) at L32 (p1_results.json: 0.14649).
  - story_dismissive, axis: 018's unit vectors.
  - shuf_NN: every 4-vs-4 split of the 8 2x2 personas (35 splits; X = the side holding helpful_warm_p0), same construction.
    The disposition and tone splits are labelled real; the remaining 33 form the label-shuffled null set.
  - cov_NN: 20 covariance-shaped random units per layer: z = Xc^T g / sqrt(n-1), g ~ N(0, I_n), Xc = mean-centred per-rollout
    reply-token mean states of the parent (018 acts_parent/own, 16,000 rollouts drawn with Random(3003)), so z ~ N(0, Sigma_L).
Usage: OMP_NUM_THREADS=8 taskset -c 104-111 /root/venvs/si/bin/python build_dirs.py"""
import glob, itertools, json, os, random, sys
from collections import defaultdict
import torch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_s as S  # noqa: E402

torch.set_num_threads(8)
LAYERS = [32, 40]
CAPL = [16, 24, 32, 40, 48]

# ---- 1. 2x2 persona means at the last prompt token (parent Part 1 capture)
per = defaultdict(list)
for f in sorted(glob.glob(f"{S.P1CAP}/parent_chunk_*.pt")):
    z = torch.load(f, weights_only=False)
    for k, t in z["means"].get("last", {}).items():
        _, group, key, trig, sid = k.split("|")
        if group == "focused" and trig == "trig":
            per[key].append(t.float())
pm = {k: torch.stack(v).mean(0) for k, v in per.items()}          # [5 layers, 5120]
nper = {k: len(v) for k, v in per.items()}
assert all(nper[k] == 100 for k in S.P8 + ["default", "dismissive"]), nper
g = lambda names, li: torch.stack([pm[n][li] for n in names]).mean(0)
D18 = torch.load(S.DIRS018, weights_only=False, mmap=True)

dirs = {L: {} for L in LAYERS}; raw = {L: {} for L in LAYERS}
meta = dict(layers=LAYERS, construction={}, splits={}, cos={})
for L in LAYERS:
    li = CAPL.index(L)
    for name, (X, Y) in (("disp", (S.HELP, S.UNH)), ("tone", (S.WARM, S.CURT))):
        v = g(X, li) - g(Y, li); raw[L][name] = v; dirs[L][name] = v / v.norm()
    b = dirs[L]["disp"] + dirs[L]["tone"]; dirs[L]["both"] = b / b.norm(); raw[L]["both"] = b
    for k in ("story_dismissive", "axis"):
        dirs[L][k] = D18["unit"][k][L].float()
    # label-shuffled 4-vs-4 splits of the same construction
    first = S.P8[0]
    sp = [set(c) for c in itertools.combinations(S.P8, 4) if first in c]
    assert len(sp) == 35
    i = 0
    for X in sorted(sp, key=lambda s: sorted(s)):
        Y = [p for p in S.P8 if p not in X]; X = sorted(X)
        real = "disp" if set(X) == set(S.HELP) else "tone" if set(X) == set(S.WARM) else None
        nm = f"shuf_{i:02d}"; i += 1
        v = g(X, li) - g(Y, li); dirs[L][nm] = v / v.norm(); raw[L][nm] = v
        meta["splits"][nm] = dict(X=X, Y=Y, real=real, interaction=set(X) == set(S.HW + S.UC))
    # covariance-shaped randoms
    meta["cos"][L] = {a: {b_: float(dirs[L][a] @ dirs[L][b_]) for b_ in ("disp", "tone", "both", "story_dismissive", "axis")}
                      for a in ("disp", "tone", "both", "story_dismissive", "axis")}

# r018 per-rollout reply means at L32 / L40 (mmap; strided read of 2 layers)
files = sorted(glob.glob(f"{S.R018}/chunk_*.pt"))
idx = []
for fi, f in enumerate(files):
    n = torch.load(f, mmap=True, weights_only=False)["resp"].shape[0]
    idx += [(fi, j) for j in range(n)]
rs = random.Random(3003); pick = sorted(rs.sample(idx, 16000))
X = {L: [] for L in LAYERS}
for fi, f in enumerate(files):
    js = [j for (a, j) in pick if a == fi]
    if not js:
        continue
    z = torch.load(f, mmap=True, weights_only=False)["resp"]
    for L in LAYERS:
        X[L].append(z[js, L].float())
nrows = len(idx)
for L in LAYERS:
    Xm = torch.cat(X[L]); Xc = Xm - Xm.mean(0, keepdim=True)
    gg = torch.Generator().manual_seed(3004 + L)
    for k in range(S.N_COV):
        z = Xc.T @ torch.randn(Xc.shape[0], generator=gg) / (Xc.shape[0] - 1) ** 0.5
        dirs[L][f"cov_{k:02d}"] = z / z.norm()
    # how much of the parent's reply-mean variance each named direction and an isotropic random carries (context, not a gate)
    var = lambda u: float(((Xc @ u) ** 2).mean())
    tot = float((Xc ** 2).sum(1).mean())
    iso = torch.randn(5120, generator=torch.Generator().manual_seed(7)); iso = iso / iso.norm()
    meta.setdefault("variance_share", {})[L] = {k: var(dirs[L][k]) / tot for k in
                                                ["disp", "tone", "both", "story_dismissive", "axis", "cov_00", "cov_01", "shuf_00"]} | {"isotropic": var(iso) / tot}
meta["construction"] = dict(p1_capture=S.P1CAP, persona_n_scripts=nper, r018_rollouts_total=nrows, r018_sampled=16000,
                            null_shuffled=[k for k, v in meta["splits"].items() if v["real"] is None],
                            check_cos_disp_tone_L32=dict(rebuilt=float(dirs[32]["disp"] @ dirs[32]["tone"]), sw001_saved=0.14649292826652527))
assert abs(meta["construction"]["check_cos_disp_tone_L32"]["rebuilt"] - 0.14649292826652527) < 1e-4, meta["construction"]["check_cos_disp_tone_L32"]
pmeans = {k: pm[k][[CAPL.index(L) for L in LAYERS]] for k in S.P8 + ["default", "dismissive"]}
os.makedirs(S.OUT, exist_ok=True)
torch.save(dict(unit=dirs, raw=raw, persona_means_last=pmeans, layers=LAYERS, nbar={L: float(D18["nbar"][L]) for L in LAYERS}),
           f"{S.OUT}/dirs_S.pt")
json.dump(meta, open(f"{S.OUT}/dirs_S_meta.json", "w"), indent=1, default=str)
print(json.dumps(dict(n_dirs={L: len(dirs[L]) for L in LAYERS}, check=meta["construction"]["check_cos_disp_tone_L32"],
                      null_shuffled=len(meta["construction"]["null_shuffled"]), cos=meta["cos"], variance_share=meta["variance_share"]), indent=1))
