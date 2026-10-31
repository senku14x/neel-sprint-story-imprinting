"""sw054 descriptive geometry of the chat-side A controls (D20; CPU, reads prep54 only, no model output). The chat A directions
are orthogonal to u_sdir only (D7), so they keep a d_self component. Per model, fold k and direction A_i: |cos(A_chat[k, i],
unit d_self.loso[k])| (the d_self that rchat uses for fold k's scripts) and |cos(A_chat[k, i], unit d_self.all)| at L16 / 32 / 48
/ 63 and the median over L16-63. Output RUN/a_chat_cos_dself.json (metrics54 report prints it beside the chat rule).
  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=8 /root/venvs/si/bin/python acos54.py [--run_dir /workspace/runs_executor/sw054]"""
import argparse, json, time

import torch

DIRS = "/workspace/runs_executor/overnight_2026-10-30/dirs"
LS = (16, 32, 48, 63)


def unit(x):
    return x / x.norm(dim=-1, keepdim=True).clamp_min(1e-12)


ap = argparse.ArgumentParser(); ap.add_argument("--run_dir", default="/workspace/runs_executor/sw054"); a = ap.parse_args()
out = dict(created=time.strftime("%FT%TZ", time.gmtime()), layers=list(LS), models={})
for m in ("hdA0", "hdB0"):
    P = torch.load(f"{a.run_dir}/prep54_{m}.pt", weights_only=False); A = unit(P["A_chat"].float())  # [5, 3, 64, H]
    D = torch.load(f"{DIRS}/chat_dirs_{m}.pt", mmap=True, weights_only=False)
    U = unit(D["d_self"]["loso"].float()); Ua = unit(D["d_self"]["all"].float()); usd = unit(P["u_sdir"].float())
    rows = []
    for k in range(5):
        for i in range(3):
            c = (A[k, i] * U[k]).sum(-1).abs(); ca = (A[k, i] * Ua).sum(-1).abs(); cs = (A[k, i] * usd).sum(-1).abs()
            rows.append(dict(fold=k, scenario=D["meta"]["scenarios"][k], A=f"A{i}",
                             abs_cos_dself_fold={str(L): round(float(c[L]), 4) for L in LS}, abs_cos_dself_fold_median_L16_63=round(float(c[16:].median()), 4),
                             abs_cos_dself_all={str(L): round(float(ca[L]), 4) for L in LS}, abs_cos_dself_all_median_L16_63=round(float(ca[16:].median()), 4),
                             abs_cos_sdir_max_L16_63=float(cs[16:].max())))
    out["models"][m] = rows
    print(m, "median over L16-63 of |cos(A, d_self fold)|:", [r["abs_cos_dself_fold_median_L16_63"] for r in rows],
          "| max |cos(A, sdir)|", max(r["abs_cos_sdir_max_L16_63"] for r in rows), flush=True)
json.dump(out, open(f"{a.run_dir}/a_chat_cos_dself.json", "w"), indent=1)
print("ACOS54_DONE", f"{a.run_dir}/a_chat_cos_dself.json")
