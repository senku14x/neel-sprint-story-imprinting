"""018: parity of vllm-lens capture vs HF capture on the same rollouts (decisions.md D7). Rule (fixed before data,
from spec §3.4's parity check for an alternative engine): min cosine over rollouts x layers of the reply-token mean
>= 0.9998 at every saved layer; last-token cosine and Nbar reported (last-token min >= 0.999).
  /root/venvs/si/bin/python compare_capture018.py --hf /root/runs/r018/acts_hfparity --vl /root/runs/r018/acts_parent"""
import argparse, json, os, sys
import torch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common018 as C  # noqa: E402
torch.set_num_threads(8)


def load(d, keys=None):
    out = {}
    for fn in sorted(f for f in os.listdir(d) if f.startswith("chunk_")):
        z = torch.load(f"{d}/{fn}", mmap=True)  # mmap: 14x faster than a full read on this box (decisions D15)
        for i, k in enumerate(z["keys"]):
            if keys is None or k in keys:
                out[k] = (z["resp"][i].float(), z["last"][i].float())
    return out


ap = argparse.ArgumentParser(); ap.add_argument("--hf", required=True); ap.add_argument("--vl", required=True)
a = ap.parse_args()
res = {}
for ctx in ("own", "textonly"):
    if not os.path.isdir(f"{a.hf}/{ctx}") or not os.path.isdir(f"{a.vl}/{ctx}"):
        continue
    H = load(f"{a.hf}/{ctx}"); V = load(f"{a.vl}/{ctx}", set(H))
    ks = sorted(set(H) & set(V))
    if not ks:
        continue
    rh = torch.stack([H[k][0] for k in ks]); rv = torch.stack([V[k][0] for k in ks])
    lh = torch.stack([H[k][1] for k in ks]); lv = torch.stack([V[k][1] for k in ks])
    cr = torch.nn.functional.cosine_similarity(rh, rv, dim=-1)  # [n, 64]
    cl = torch.nn.functional.cosine_similarity(lh, lv, dim=-1)  # [n, 13]
    rel = (rh - rv).norm(dim=-1) / rh.norm(dim=-1)
    res[ctx] = dict(n=len(ks), resp_cos_min_by_layer={L: float(cr[:, L].min()) for L in C.LAYERS_SAVE},
                    resp_cos_min_all64=float(cr.min()), resp_cos_median=float(cr.median()),
                    resp_rel_err_median=float(rel.median()), resp_rel_err_max=float(rel.max()),
                    last_cos_min_by_layer={L: float(cl[:, i].min()) for i, L in enumerate(C.LAYERS_SAVE)},
                    pass_resp=bool(min(float(cr[:, L].min()) for L in C.LAYERS_SAVE) >= 0.9998),
                    pass_last=bool(float(cl.min()) >= 0.999))
for f in ("nbar.pt",):
    if os.path.exists(f"{a.hf}/own/{f}") and os.path.exists(f"{a.vl}/own/{f}"):
        nh = torch.load(f"{a.hf}/own/{f}")["nbar"]; nv = torch.load(f"{a.vl}/own/{f}")["nbar"]
        res["nbar_rel_diff_max"] = float(((nh - nv).abs() / nh).max())
res["accept"] = bool(res and all(v["pass_resp"] and v["pass_last"] for k, v in res.items() if isinstance(v, dict)))
json.dump(res, open(f"{C.RES}/capture_parity.json", "w"), indent=1)
print(json.dumps(res, indent=1))
