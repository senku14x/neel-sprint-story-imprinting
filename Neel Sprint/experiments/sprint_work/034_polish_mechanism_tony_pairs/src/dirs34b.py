"""sw034 Part B directions and sizes (prep agent, E2, 31 Oct 2026; CPU, node; new file; D24-D25). For each model m (the four organisms and
the parent), from m's own captures of the no-prohibition helps contexts (cap34 for organisms, cap34p for the parent), over ALL 92 REG
pairs (no folds: Part B's turn-1 prompts are outside every fit context):
  u      = unit(mean over pairs of hdr_mean[noP formal_helps] - hdr_mean[noP casual_helps])      (noP_reg, fitted on every pair)
  alpha  = [64, 7]: mean over pairs of (hdr[noP formal_helps][t, L] - hdr[noP casual_helps][t, L]) . u_L  (the natural formal - casual
           coordinate difference per header token and layer; the 1.0x size; D24 item 2)
  r      = one covariance-shaped random direction (dirs34.null_draws on the noP helps hdr_mean, both cells centred), orthogonal to u per
           layer; seed 3600 + model index. Its clamp size along r is the same alpha (norm-matched).
Also logged: cos(u, the fold-averaged Part A noP_reg of dirs34) per layer (organisms) and alpha at L16 / 40 / 63.
  OMP_NUM_THREADS=16 python dirs34b.py   -> RUN/dirs34b_<m>.pt, RUN/dirs34b_summary.json"""
import json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common34 as C  # noqa: E402
from dirs34 import unit, orth_span, null_draws  # noqa: E402

torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "16")))
RUN = "/root/runs/sw034"; CAPS = "/root/caps/sw034"
MODELS = C.ORGS + ("parent",)


def main():
    P = C.load_pairs(); pl = [tuple(x) for x in P["REG"]]; summ = {}
    for mi, m in enumerate(MODELS):
        Z = torch.load(f"{CAPS}/cap_{m}.pt", mmap=True, weights_only=False); idx = {k: i for i, k in enumerate(Z["keys"])}
        kf = [idx[C.ctx_key("noP", "formal_helps", s, v)] for s, v in pl]; kc = [idx[C.ctx_key("noP", "casual_helps", s, v)] for s, v in pl]
        u = unit((Z["hdr_mean"][kf].float() - Z["hdr_mean"][kc].float()).mean(0))
        dh = (Z["hdr"][kf].float() - Z["hdr"][kc].float()).mean(0)          # [7, 64, H]
        alpha = torch.einsum("tlh,lh->lt", dh, u)                            # [64, 7]
        raw = null_draws([Z["hdr_mean"][kf].float(), Z["hdr_mean"][kc].float()], 1, 3600 + mi)
        r = orth_span(raw, [u])[0]
        assert float((r * u).sum(-1)[16:].abs().max()) < 1e-4 and torch.isfinite(alpha).all()
        e = dict(alpha_L16=[round(float(x), 3) for x in alpha[16]], alpha_L40=[round(float(x), 3) for x in alpha[40]],
                 alpha_L63=[round(float(x), 3) for x in alpha[63]], n_pairs=len(pl))
        if m in C.ORGS:
            D = torch.load(f"{RUN}/dirs34_{m}.pt", weights_only=False)
            cf = torch.stack([(unit(D["U"][f]["noP_reg"].float()) * u).sum(-1) for f in (0, 1)]).mean(0)
            e["cos_vs_partA_noP_reg"] = {f"L{L}": round(float(cf[L]), 4) for L in (16, 32, 48, 63)}
        summ[m] = e
        torch.save(dict(model=m, u=u, r=r, alpha=alpha, created=time.strftime("%FT%TZ", time.gmtime())), f"{RUN}/dirs34b_{m}.pt")
        print(m, json.dumps(e), flush=True)
    json.dump(summ, open(f"{RUN}/dirs34b_summary.json", "w"), indent=1)
    print("DIRS34B_DONE", flush=True)


if __name__ == "__main__":
    main()
