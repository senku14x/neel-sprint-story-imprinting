# independent cosine check (analysis pass): v2 all-script d_self from sw021 captures (mean header-mean self-hostile - user-hostile,
# 61 scripts) vs sw009's all-64 d_self (dirs_<m>.pt["all"]["d_self"]), per layer; references: v2 d_ctrl (self-control - user-control,
# 58 scripts), hdA0-vs-hdB0 v2 d_self, and a split-half (by script) v2 d_self.
import json, random, torch
torch.set_num_threads(6)
out = {}
D = {}
for m in ("hdA0", "hdB0"):
    z = torch.load(f"/workspace/runs_executor/sw021/captures/{m}.pt", mmap=True)
    keys = z["keys"]; hm = z["hdr_mean"]
    ix = {k: i for i, k in enumerate(keys)}
    sids = sorted(set(k.split("|")[1] for k in keys))
    both = [s for s in sids if f"self-hostile|{s}" in ix and f"user-hostile|{s}" in ix]
    ctl = [s for s in sids if f"self-control|{s}" in ix and f"user-control|{s}" in ix]
    mean = lambda c, ss: hm[[ix[f"{c}|{s}"] for s in ss]].float().mean(0)
    d = mean("self-hostile", both) - mean("user-hostile", both)
    dc = mean("self-control", ctl) - mean("user-control", ctl)
    rng = random.Random(7); sh = both[:]; rng.shuffle(sh); h1, h2 = sh[: len(sh) // 2], sh[len(sh) // 2:]
    d1 = mean("self-hostile", h1) - mean("user-hostile", h1); d2 = mean("self-hostile", h2) - mean("user-hostile", h2)
    v1 = torch.load(f"/workspace/_box_transfer/sw009_runs_box1_2026-10-30/dirs_{m}.pt", mmap=True)["all"]["d_self"].float()
    cos = lambda a, b: torch.nn.functional.cosine_similarity(a, b, dim=-1).tolist()
    out[m] = dict(n_scripts=len(both), n_ctrl=len(ctl), v2_vs_sw009=cos(d, v1), v2_dself_vs_v2_dctrl=cos(d, dc), split_half=cos(d1, d2),
                  dself_norm=d.norm(dim=-1).tolist(), v1_shape=list(v1.shape))
    D[m] = d
out["hdA0_vs_hdB0_v2"] = torch.nn.functional.cosine_similarity(D["hdA0"], D["hdB0"], dim=-1).tolist()
json.dump(out, open("/workspace/runs_executor/sw021/analysis_pass/cos_check.json", "w"))
for m in ("hdA0", "hdB0"):
    o = out[m]
    print(m, o["n_scripts"], o["n_ctrl"], o["v1_shape"])
    for L in (16, 24, 32, 40, 48, 56, 63):
        print(f"  L{L} v2-vs-sw009 {o['v2_vs_sw009'][L]:.3f}  dself-vs-dctrl {o['v2_dself_vs_v2_dctrl'][L]:.3f}  split-half {o['split_half'][L]:.3f}  A-vs-B {out['hdA0_vs_hdB0_v2'][L]:.3f}")
