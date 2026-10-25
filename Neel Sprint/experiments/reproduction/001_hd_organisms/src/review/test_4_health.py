"""Review test (4): health.stats vs a brute-force numpy reference on a small random vocabulary (V=50).
Cases: random p and f (sharp and flat), identical distributions (KL must be 0, agreement 1), float32 and float64 inputs.
Run: CUDA_VISIBLE_DEVICES="" /root/venvs/si/bin/python test_4_health.py
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np  # noqa: E402
import torch  # noqa: E402

import health  # noqa: E402


def ref(zp, zf, tgt):
    out = {k: [] for k in health.KEYS}
    for a, b, t in zip(zp, zf, tgt):
        p = np.exp(a - a.max()); p /= p.sum(); f = np.exp(b - b.max()); f /= f.sum()
        lp_, lf_ = np.log(p), np.log(f)
        top_p = np.argsort(-p)[:20]; top_f = np.argsort(-f)[:20]
        out["ent_f"].append(-(f * lf_).sum()); out["top1_f"].append(f.max())
        out["tail20_f"].append(1 - f[top_f].sum()); out["tailB20_f"].append(1 - f[top_p].sum())
        out["kl_pf"].append((p * (lp_ - lf_)).sum()); out["kl_fp"].append((f * (lf_ - lp_)).sum())
        out["nll_f"].append(-lf_[t]); out["agree"].append(float(p.argmax() == f.argmax()))
    return {k: np.array(v) for k, v in out.items()}


rng = np.random.default_rng(0)
V, N = 50, 9
res, ok = {}, True
cases = {
    "random_sharp": (rng.normal(0, 3, (N, V)), rng.normal(0, 3, (N, V))),
    "random_flat": (rng.normal(0, .3, (N, V)), rng.normal(0, .3, (N, V))),
}
zp = rng.normal(0, 2, (N, V)); zf = zp + rng.normal(0, .5, (N, V)); zf[:4] = zp[:4]  # 4 identical rows, 5 similar
cases["near_and_identical"] = (zp, zf)
cases["identical"] = (zp, zp.copy())
tgt = rng.integers(0, V, N)
for name, (a, b) in cases.items():
    for dt, tol in [(torch.float64, 1e-10), (torch.float32, 2e-5)]:
        lp = torch.log_softmax(torch.tensor(a, dtype=dt), -1); lf = torch.log_softmax(torch.tensor(b, dtype=dt), -1)
        got = {k: v.double().numpy() for k, v in health.stats(lp, lf, torch.tensor(tgt)).items()}
        want = ref(a, b, tgt)
        err = {k: float(np.abs(got[k] - want[k]).max()) for k in health.KEYS}
        good = all(e < tol for e in err.values())
        if name == "identical":
            good &= float(np.abs(got["kl_pf"]).max()) < tol and float(np.abs(got["kl_fp"]).max()) < tol
            good &= bool((got["agree"] == 1).all()) and float(np.abs(got["tailB20_f"] - got["tail20_f"]).max()) < tol
        res[f"{name}|{str(dt)}"] = dict(max_abs_err=err, pass_=bool(good),
                                        example_row0={k: round(float(got[k][0]), 6) for k in health.KEYS})
        ok &= good
# discriminative sanity: KL and tailB20 must increase from identical -> near -> random
lp = torch.log_softmax(torch.tensor(zp), -1)
kl_id = float(health.stats(lp, lp, torch.tensor(tgt))["kl_pf"].mean())
kl_near = float(health.stats(lp, torch.log_softmax(torch.tensor(zp + rng.normal(0, .5, (N, V))), -1), torch.tensor(tgt))["kl_pf"].mean())
kl_far = float(health.stats(lp, torch.log_softmax(torch.tensor(rng.normal(0, 2, (N, V))), -1), torch.tensor(tgt))["kl_pf"].mean())
res["kl_monotone_identical<near<far"] = [kl_id, kl_near, kl_far]
ok &= kl_id == 0.0 or abs(kl_id) < 1e-12
ok &= kl_id < kl_near < kl_far
res["PASS"] = bool(ok)
print(json.dumps(res, indent=1))
print("PASS" if ok else "FAIL")
