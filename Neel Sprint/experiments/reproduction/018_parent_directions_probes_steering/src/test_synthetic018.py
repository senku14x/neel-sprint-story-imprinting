"""018 positive-control test of directions018.py + probes018.py on synthetic activations with planted structure.
Real row ids and splits (common018.build_rows), fake activations: x = base + group offset + N(0, 1) per dim, at all 64 layers.
Planted (same at every layer):
  role r       = base - a + rho_r      (|a| = 20, |rho_r| = 10)  -> axis ~ a, split-half high
  story X      = base + s_X            dismissive/confident_wrong/eval_dismissive |s| = 8 (also text-only, x0.5);
                                       sarcastic |s| = 8 with prompt but 0 text-only (leakage case);
                                       peer |s| = 0.3 (weak); helper 0 (null)
  trait T      = base +/- t_T (|t| = 4); evil keeps only 17 positives (low-n path)
Pass criteria are printed; run: OMP_NUM_THREADS=8 /root/venvs/si/bin/python test_synthetic018.py <tmpdir>"""
import json, os, random, sys, time

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common018 as C  # noqa: E402

tmp = sys.argv[1]
C.RUN, C.RES = tmp, tmp
os.makedirs(f"{tmp}/acts_parent/own", exist_ok=True); os.makedirs(f"{tmp}/acts_parent/textonly", exist_ok=True)
H, NL = C.HIDDEN, C.N_LAYERS
g = torch.Generator().manual_seed(0)
rv = lambda n: (lambda v: v / v.norm() * n)(torch.randn(H, generator=g))
base, a = rv(50), rv(20)
rows = C.build_rows(); byset = {}
for r in rows:
    byset.setdefault(r["set"], []).append(r)
rng = random.Random(0)
roles = sorted({r["label"] for r in byset["role"]})[:12]
rho = {x: rv(10) for x in roles}
S = {"dismissive": (rv(8), 0.5), "confident_wrong": (rv(8), 0.5), "eval_dismissive": (rv(8), 0.5),
     "sarcastic": (rv(8), 0.0), "peer": (rv(0.3), 0.5), "helper": (torch.zeros(H), 0.5)}
T = {t: rv(4) for t in C.TRAITS}
kept, items = {}, []  # items: (key, own offset, textonly offset or None)
def keys_of(r):
    return [f"{r['id']}|{k}" for k in range(r["n"])]
for r in byset["default"]:
    for k in keys_of(r):
        kept.setdefault("default", []).append(k); items.append((k, torch.zeros(H), torch.zeros(H)))
for x in roles:
    rs = [r for r in byset["role"] if r["label"] == x]
    rsub = C.role_textonly_ids()  # include every role row that has a text-only re-encode (the axis probe uses those)
    trs = [r for r in rs if r["split"] == "train"]
    tr = [r for r in trs if r["id"] in rsub]; tr += rng.sample([r for r in trs if r["id"] not in rsub], 40 - len(tr))
    he = [r for r in rs if r["split"] == "held" and r["id"] in rsub] + [r for r in rs if r["split"] == "held" and r["id"] not in rsub][:3]
    for r in tr + he:
        k = keys_of(r)[0]; kept.setdefault(f"role_fully|{x}", []).append(k)
        items.append((k, -a + rho[x], (-a + rho[x]) * 0.5))
for r in byset["story"] + byset["evaldis"]:
    s, f = S[r["label"]]
    for k in keys_of(r):
        kept.setdefault(f"story|{r['label']}", []).append(k); items.append((k, s, s * f))
for t in C.TRAITS:
    for pol, sg in (("pos", 1), ("neg", -1)):
        rs = [r for r in byset["trait"] if r["label"] == t and r["pol"] == pol]
        ks = [k for r in rs for k in keys_of(r)]
        tr = [k for k in ks if "|train|" in k]; he = [k for k in ks if "|held|" in k]
        sel = rng.sample(tr, 17 if (t == "evil" and pol == "pos") else 150) + he[: (3 if (t == "evil" and pol == "pos") else 40)]
        kept[f"trait_{pol}|{t}"] = sel
        items += [(k, sg * T[t], sg * T[t]) for k in sel]
json.dump(dict(kept=kept), open(f"{tmp}/filters.json", "w"))
role_sub = C.role_textonly_ids()
t0 = time.time()
for ctx in ("own", "textonly"):
    for c0 in range(0, len(items), 1024):
        b = items[c0:c0 + 1024]
        R = torch.stack([(base + (o if ctx == "own" else t))[None].expand(NL, H) + torch.randn(NL, H, generator=g) for _, o, t in b]).half()
        torch.save(dict(keys=[k for k, _, _ in b], resp=R, last=R[:, C.LAYERS_SAVE]), f"{tmp}/acts_parent/{ctx}/chunk_{c0 // 1024:04d}.pt")
torch.save(dict(nbar=torch.full((NL,), 80.0)), f"{tmp}/acts_parent/own/nbar.pt")
print(f"synthetic data: {len(items)} rollouts x 2 contexts in {time.time() - t0:.0f}s", flush=True)

import directions018 as Dm  # noqa: E402  (reads C.RUN at import)
Dm.ACTS = f"{tmp}/acts_parent/own"
Dm.main()
Dz = torch.load(f"{tmp}/directions_parent.pt", weights_only=False); ck = json.load(open(f"{tmp}/directions_checks.json"))
cos = lambda x, y: float(torch.nn.functional.cosine_similarity(x.float(), y.float(), dim=0))
res = dict(axis_vs_a=cos(Dz["unit"]["axis"][32], a), split_half_L32=ck["axis_split_half_cos"]["32"],
           story_dismissive_vs_s=cos(Dz["unit"]["story_dismissive"][32], S["dismissive"][0]),
           trait_apathetic_vs_t=cos(Dz["unit"]["trait_apathetic"][32], T["apathetic"]),
           trait_evil_vs_t=cos(Dz["unit"]["trait_evil"][32], T["evil"]),
           random_pair_cos=cos(Dz["unit"]["random_0"][32], Dz["unit"]["random_1"][32]))
print("directions:", json.dumps({k: round(v, 3) for k, v in res.items()}), flush=True)
# analytic expectations: noise variance per dim of a mean over n rollouts is 1/n (sigma = 1), summed over H dims
rb = torch.stack([rho[x] for x in roles]).mean(0); sig = a - rb
nz = lambda *ns: H * sum(1 / n for n in ns)
exp = dict(axis_vs_a=float(a @ sig / (a.norm() * (sig.norm() ** 2 + nz(240, 40 * 12)) ** 0.5)),
           split_half_L32=float(sig.norm() ** 2 / (sig.norm() ** 2 + nz(120, 20 * 12))),
           story_dismissive_vs_s=8 / (64 + nz(240, 240)) ** 0.5, trait_apathetic_vs_t=8 / (64 + nz(150, 150)) ** 0.5,
           trait_evil_vs_t=8 / (64 + nz(17, 150)) ** 0.5, random_pair_cos=0.0)
print("expected:  ", json.dumps({k: round(v, 3) for k, v in exp.items()}), flush=True)
for k in exp:
    assert abs(res[k] - exp[k]) < 0.03, (k, res[k], exp[k])

import probes018 as Pm  # noqa: E402
Pm.LS = [32]  # one layer: correctness only (the container has an 18.7-CPU quota)
t0 = time.time(); Pm.main(); dt = time.time() - t0
P = json.load(open(f"{tmp}/probes.json"))
get = lambda n, fs, sp="test1": P[f"{n}|{fs}"]["layers"]["32"][sp]
show = {f"{n}|{fs}": {k: round(get(n, fs)[k], 3) for k in ("auroc", "null_p95", "direction_auroc")}
        for n in ("story_dismissive", "story_sarcastic", "story_helper", "story_peer", "axis", "trait_apathetic", "trait_evil")
        for fs in ("with_prompt", "text_only") if "layers" in P[f"{n}|{fs}"]}
print(json.dumps(show, indent=0))
print(f"probes: {dt:.0f}s for 1 layer x 14 tasks x 2 feature sets on 14 workers", flush=True)
# analytic: an L2 probe in H = 5120 dims from 240 + 240 rollouts recovers the offset (|4| text-only) with cos ~0.52,
# so AUROC ~ Phi(4 * 0.52 / sqrt 2) ~ 0.93; the planted-offset-free tasks sit at 0.5
assert get("story_dismissive", "text_only")["auroc"] > 0.85 and get("story_dismissive", "text_only")["null_p95"] < 0.7
assert get("story_dismissive", "text_only", "test2")["auroc"] > 0.85
assert get("story_sarcastic", "with_prompt")["auroc"] > 0.95 and get("story_sarcastic", "text_only")["auroc"] < 0.7
assert 0.3 < get("story_helper", "text_only")["auroc"] < 0.7
assert get("axis", "text_only")["auroc"] > 0.95 and get("axis", "text_only")["direction_auroc"] > 0.95
print("SYNTHETIC TEST PASSED")
