"""E6 (CPU, executor-8): where each LoRA writes. Per organism, layer and module: the effective update dW = (alpha/r) B A
(PEFT, alpha 64 / r 32 = 2) via a thin SVD (QR of B and A^T, SVD of the 32x32 core): Frobenius norm and all 32 singular
values. For the modules that write the residual stream (o_proj: full attention; out_proj: linear attention; down_proj:
MLP), the output singular vectors are compared with the parent's directions at the SAME layer L (the block output
layers[L] they write into; E1 parent means, pre-final-norm):
  axis_frac   = ||u_axis^T dW||_F / ||dW||_F  (share of the update's output energy along the parent's unit axis)
  pc10_frac   = ||P_pc10 dW||_F / ||dW||_F    (share in the parent's top-10 role-PC subspace)
  top5_axis_cos = |cos(output singular vector k, axis)|, k = 1..5;  top5_pc10 = norm of its projection on the PC subspace
Random-direction reference for a uniformly random dW: axis_frac ~ sqrt(1/5120) = 0.014, pc10_frac ~ sqrt(10/5120) = 0.044.
  OMP_NUM_THREADS=4 /root/venvs/si/bin/python analyze_E6.py [--models hdA0,...]"""
import argparse, json, os, re, sys

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_x as X  # noqa: E402

torch.set_num_threads(4)
WRITERS = ("o_proj", "out_proj", "down_proj")


def parent_dirs(min_count=10):
    P = torch.load(f"{X.LOCAL}/E1/means/parent.pt")
    M, cnt = P["means"], P["counts"]
    roles = sorted(k for k in cnt if "|" not in k and k not in ("default", "eval_dismissive") and cnt[k] >= min_count)
    R = torch.stack([M[r] for r in roles]).float()  # [roles, 64, H]
    ax = M["default"].float() - R.mean(0)
    u = ax / ax.norm(dim=-1, keepdim=True)
    pcs = []
    for l in range(64):
        Xc = R[:, l] - R[:, l].mean(0)
        _, _, Vt = torch.linalg.svd(Xc, full_matrices=False); pcs.append(Vt[:10])
    return u, torch.stack(pcs), len(roles)  # [64, H], [64, 10, H]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--models", default="hdA0,hdB0,psA0,psB0,hdB0rep,ctrlB0,sym")
    a = ap.parse_args()
    from safetensors import safe_open
    u_ax, pcs, n_roles = parent_dirs()
    od = f"{X.LOCAL}/E6"; os.makedirs(od, exist_ok=True)
    summ = dict(convention="dW = (alpha/r) B A; residual writers compared with parent directions at the block output of the same layer",
                n_roles_for_pcs=n_roles, random_ref=dict(axis_frac=(1 / 5120) ** 0.5, pc10_frac=(10 / 5120) ** 0.5), models={})
    for m in a.models.split(","):
        path = X.LORA_SRC[m]
        cfg = json.load(open(f"{path}/adapter_config.json")); s = cfg["lora_alpha"] / cfg["r"]
        f = safe_open(f"{path}/adapter_model.safetensors", "pt")
        mods = {}
        for k in f.keys():
            mm = re.match(r".*layers\.(\d+)\.(.+)\.lora_([AB])\.weight$", k)
            mods.setdefault((int(mm.group(1)), mm.group(2)), {})[mm.group(3)] = k
        rows, save = [], {}
        for (L, name), ab in sorted(mods.items()):
            A = f.get_tensor(ab["A"]).float(); B = f.get_tensor(ab["B"]).float()  # A [r, in], B [out, r]
            QB, RB = torch.linalg.qr(B); QA, RA = torch.linalg.qr(A.T)
            Us, S, Vhs = torch.linalg.svd(s * RB @ RA.T)
            U = QB @ Us; V = QA @ Vhs.T  # [out, r], [in, r]
            fro = S.norm().item()
            row = dict(layer=L, module=name, fro=fro, sv=S[:8].tolist(), out_dim=B.shape[0], in_dim=A.shape[1])
            if name.split(".")[-1] in WRITERS and B.shape[0] == X.H:
                ua = u_ax[L]; Pc = pcs[L]  # [H], [10, H]
                US = U * S[None]  # dW = US V^T, so ||x^T dW|| = ||x^T U S||
                row["axis_frac"] = ((ua @ US).norm() / fro).item()
                row["pc10_frac"] = ((Pc @ US).norm() / fro).item()
                row["top5_axis_cos"] = (ua @ U[:, :5]).abs().tolist()
                row["top5_pc10"] = (Pc @ U[:, :5]).norm(dim=0).tolist()
            rows.append(row)
            save[f"{L}|{name}"] = dict(S=S, U8=U[:, :8].half(), V8=V[:, :8].half())
        torch.save(save, f"{od}/lora_svd_{m}.pt")
        summ["models"][m] = dict(adapter=path, scale=s, modules=rows)
        w = [r for r in rows if "axis_frac" in r]
        print(m, "modules", len(rows), "writers", len(w), "mean axis_frac", round(sum(r["axis_frac"] for r in w) / len(w), 4),
              "mean pc10_frac", round(sum(r["pc10_frac"] for r in w) / len(w), 4), flush=True)
    json.dump(summ, open(f"{od}/E6_summary.json", "w"), indent=1)
    figures(summ)


def figures(summ):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fd = f"{X.LOCAL}/E6/figs"; os.makedirs(fd, exist_ok=True)
    for q, ref in (("fro", None), ("axis_frac", summ["random_ref"]["axis_frac"]), ("pc10_frac", summ["random_ref"]["pc10_frac"])):
        fig, axs = plt.subplots(1, 3, figsize=(16, 4.5), sharey=(q != "fro"))
        for j, w in enumerate(WRITERS):
            for m, d in summ["models"].items():
                pts = sorted((r["layer"], r[q]) for r in d["modules"] if r["module"].split(".")[-1] == w and q in r)
                if pts:
                    axs[j].plot([p[0] for p in pts], [p[1] for p in pts], marker=".", label=m)
            if ref:
                axs[j].axhline(ref, color="k", ls=":", label="random dW")
            axs[j].set_title(f"{w}: {q}"); axs[j].set_xlabel("layer")
        axs[0].legend(fontsize=7); fig.tight_layout(); fig.savefig(f"{fd}/{q}.png", dpi=110); plt.close(fig)


if __name__ == "__main__":
    main()
