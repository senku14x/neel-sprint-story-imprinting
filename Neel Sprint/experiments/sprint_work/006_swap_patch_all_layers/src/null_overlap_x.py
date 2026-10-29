"""sw006 N1 overlap diagnostic (executor-8; CPU, added 29 Oct ≈10:50 after an interim STRICT look showed large N1 shifts in hdB0).
For each model, arm (C1, C2, C3, H0-C3) and N1 draw: the cosine between the null's displacement and the real arm's displacement,
computed from the captured no-edit states (an approximation: in the run, upstream patched layers change x).
  header arms: x = recipient header state [7, 64, H], donor = donor header state; d_real = U U^T (donor - x), d_null = Un Un^T (donor - x)
  H0-C3      : the history-mean version, d = U U^T (m_donor - m_recipient)
Each test script uses the other fold's directions. Mean cosine over scripts, tokens and layers 20-63 (the bands where P0 acts),
and per layer. -> out/null_overlap.json
  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=8 /root/venvs/si/bin/python null_overlap_x.py"""
import json, os

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = f"{HERE}/out"; RUN = "/root/runs/sw006"
ARMS = {"C1": ("dismissive", "deflection", "dd", "1", "hdr"), "C2": ("polite_refusal", "helpful", "hp", "1", "hdr"),
        "C3": ("dismissive", "helpful", "plane", "2", "hdr"), "H0-C3": ("dismissive", "helpful", "plane", "2", "hist")}


def main():
    folds = json.load(open(f"{OUT}/folds.json"))["fold"]; res = {}
    for m in ("hdA0", "hdB0"):
        C = torch.load(f"{RUN}/capture_{m}.pt"); idx = {k: i for i, k in enumerate(C["keys"])}; Dd = torch.load(f"{RUN}/dirs_{m}.pt")
        for arm, (rec, don, dk, nk, where) in ARMS.items():
            draws = [(t, i) for t in ("cov", "shuf") for i in range(5 if arm != "H0-C3" else 2)]
            acc = {f"{t}{i}": [] for t, i in draws}; acc_norm = {f"{t}{i}": [] for t, i in draws}
            for sid in sorted(folds):
                fit = "B" if folds[sid] == "A" else "A"; U = Dd[fit][dk]
                if where == "hdr":
                    x = C["hdr"][idx[f"{sid}|{rec}|trig"]].float(); y = C["hdr"][idx[f"{sid}|{don}|trig"]].float()  # [7, 64, H]
                else:
                    x = C["histmean"][idx[f"{sid}|{rec}|trig"]][None]; y = C["histmean"][idx[f"{sid}|{don}|trig"]][None]  # [1, 64, H]
                diff = y - x
                dr = torch.einsum("tlk,lhk->tlh", torch.einsum("tlh,lhk->tlk", diff, U), U)
                for t, i in draws:
                    Un = Dd[fit][t + nk][i]
                    dn = torch.einsum("tlk,lhk->tlh", torch.einsum("tlh,lhk->tlk", diff, Un), Un)
                    cos = torch.nn.functional.cosine_similarity(dr, dn, dim=-1)  # [t, 64]
                    acc[f"{t}{i}"].append(cos.mean(0)); acc_norm[f"{t}{i}"].append((dn.norm(dim=-1) / dr.norm(dim=-1).clamp_min(1e-6)).mean(0))
            for k in acc:
                c = torch.stack(acc[k]).mean(0); r = torch.stack(acc_norm[k]).mean(0)
                res[f"{m}|N1{k[:-1]}{k[-1]}-{arm}"] = dict(cos_L20_63=float(c[20:].mean()), cos_L0_19=float(c[:20].mean()),
                                                           cos_per_layer=[round(float(v), 3) for v in c],
                                                           raw_null_to_real_norm_L20_63=float(r[20:].mean()))
                print(m, arm, k, "cos L20-63", round(float(c[20:].mean()), 3), "raw |dn|/|dr|", round(float(r[20:].mean()), 3), flush=True)
    json.dump(res, open(f"{OUT}/null_overlap.json", "w"), indent=1)


if __name__ == "__main__":
    main()
