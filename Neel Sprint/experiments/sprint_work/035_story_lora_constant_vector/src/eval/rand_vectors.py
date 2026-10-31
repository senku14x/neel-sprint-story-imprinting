"""sw035 eval: random-vector controls for a learned S7 vector set (sw035 eval agent, 31 Oct 2026). Design: DECISIONS D17, D18.

  python rand_vectors.py <vectors_stepNNN.pt> <out_dir> [--seeds 0,1,2] [--kinds R,Q]

R (D17): for each seed and layer L, an independent Gaussian direction (torch.Generator seeded with 1000*seed + L), rescaled to
         ||v_L|| (per-layer norm matched). The cumulative injected offset ||sum_{k<=L} r_k|| is NOT matched (random directions add
         like a random walk).
Q:       one random orthogonal rotation per seed (QR of a seeded 5120 x 5120 Gaussian, sign-fixed), r_L = Q v_L for every L: every
         per-layer norm and every inner product between layers is kept, so ||sum_{k<=L} r_k|| = ||sum_{k<=L} v_k|| exactly (the
         injected cumulative offset), while each direction is uniformly random.
Writes <out_dir>/<kind>s<seed>/vectors_rand.pt (s7_vectors format: same layer_ids, base, frozen_adapter; plus kind, seed, source
sha256) and <out_dir>/rand_summary.json (per-layer norms and cumulative norms, learned vs each control; cos to the learned set)."""
import argparse, hashlib, json, os

import torch


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def cum_norm(v):
    return torch.cumsum(v.double(), 0).norm(dim=1)


def make_R(v, seed):
    out = torch.empty_like(v, dtype=torch.float64)
    for L in range(v.shape[0]):
        g = torch.Generator().manual_seed(1000 * seed + L)
        r = torch.randn(v.shape[1], generator=g, dtype=torch.float64)
        out[L] = r / r.norm() * v[L].double().norm()
    return out.float()


def make_Q(v, seed):
    g = torch.Generator().manual_seed(77_000 + seed)
    A = torch.randn(v.shape[1], v.shape[1], generator=g, dtype=torch.float64)
    Q, Rr = torch.linalg.qr(A)
    Q = Q * torch.sign(torch.diagonal(Rr))[None]   # Haar-distributed
    return (v.double() @ Q.T).float()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("out")
    ap.add_argument("--seeds", default="0,1,2"); ap.add_argument("--kinds", default="R,Q")
    a = ap.parse_args()
    d = torch.load(a.src, map_location="cpu", weights_only=False)
    v = d["vectors"].float()
    src_sha = sha(a.src)
    summ = dict(source=a.src, source_sha256=src_sha, layer_norm_learned=[float(x) for x in v.norm(dim=1)],
                cum_norm_learned=[float(x) for x in cum_norm(v)], controls={})
    for kind in a.kinds.split(","):
        for s in map(int, a.seeds.split(",")):
            r = make_R(v, s) if kind == "R" else make_Q(v, s)
            assert torch.allclose(r.norm(dim=1), v.norm(dim=1), rtol=1e-5, atol=1e-6), "per-layer norm not matched"
            if kind == "Q":
                assert torch.allclose(cum_norm(r), cum_norm(v), rtol=1e-5, atol=1e-5), "cumulative norm not matched"
            dst = os.path.join(a.out, f"{kind}s{s}")
            os.makedirs(dst, exist_ok=True)
            o = {k: d[k] for k in d if k != "vectors"}
            o.update(vectors=r, rand_kind=kind, rand_seed=s, rand_source=a.src, rand_source_sha256=src_sha,
                     note=f"sw035 eval random control ({kind}); per-layer norms of the source set")
            p = os.path.join(dst, "vectors_rand.pt")
            torch.save(o, p)
            cos = torch.nn.functional.cosine_similarity(r.double(), v.double(), dim=1)
            summ["controls"][f"{kind}s{s}"] = dict(path=p, sha256=sha(p), cum_norm=[float(x) for x in cum_norm(r)],
                                                   cum_ratio_L63=float(cum_norm(r)[-1] / cum_norm(v)[-1]),
                                                   max_abs_cos_to_learned=float(cos.abs().max()))
            print(kind, s, p, "cum ratio at L63", round(summ["controls"][f"{kind}s{s}"]["cum_ratio_L63"], 3),
                  "max |cos| to learned", round(float(cos.abs().max()), 4), flush=True)
    json.dump(summ, open(os.path.join(a.out, "rand_summary.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
