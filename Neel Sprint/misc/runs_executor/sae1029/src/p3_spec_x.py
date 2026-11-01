"""sae1029 part3 (causal feature edit) spec builder (executor-8, 29 Oct; ideation brief
_sessions/ideation/notes/2026-10-29_executor_brief_causal_feature_edit.md, section A). CPU.
Per model (hdA0, hdB0):
 shared  : the top 15 shared DISMISSIVE-side latents from sae1029 (AUROC < 0.5 in both the Assistant contrast and the
           story line-start contrast, |AUROC - 0.5| >= 0.25 in both; ranked by min effect; per model).
 random  : 5 draws x 15 live latents (live in X8 content, >= 5% of contexts), each matched to one shared latent's firing
           frequency in the declining cells (+-25%), excluding all shared latents. Seeded.
 targets : per latent, the mean per-token activation (x8_content mean code) in each X8 cell (HS HL DS DL H_def H_dis).
 dense   : per cell pair, mean reply-token state difference toward the target cell (mean_state[target] - mean_state[cell]).
 SAE rows: encoder rows, encoder biases and decoder columns of every listed latent, b_dec, threshold.
 onTarget: the parent's helping - declining header direction (E2a parent bc trig, last header token: mean(HS, HL) -
           mean(DS, DL)) at L48..L56, and the parent's per-cell mean projections onto it.
  /root/venvs/si/bin/python p3_spec_x.py"""
import glob, json, os, sys

import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sae_x as S  # noqa: E402
import part2_analyze_x as A  # noqa: E402

OUT = "/root/runs/sae1029/part3_causal"
CELLS = ["HS", "HL", "DS", "DL", "H_def", "H_dis"]
FWD = {"DS": "HS", "DL": "HL", "H_dis": "H_def"}
REV = {"HS": "DS", "HL": "DL", "H_def": "H_dis"}
K = 15
OT_LAYERS = [48, 50, 52, 54, 56]


def main():
    os.makedirs(OUT, exist_ok=True)
    au = dict(np.load(f"{A.OUT}/auroc_per_latent.npz"))
    x8 = A.load_x8c()
    sae = S.load_sae(device="cpu")
    spec = {}
    for m in ("hdA0", "hdB0"):
        a, s, live = au[f"bc|{m}|asst"] - 0.5, au[f"bc|{m}|story_ls"] - 0.5, au[f"bc|{m}|live"]
        ok = live & (a <= -0.25) & (s <= -0.25)
        score = np.where(ok, np.minimum(-a, -s), 0)
        shared = [int(i) for i in np.argsort(-score)[:K] if score[i] > 0]
        C_ = x8[m]["code"]; cell = x8[m]["cell"]
        targ = {c: torch.tensor(C_[cell == c].mean(0)) for c in CELLS}  # [F] each
        freq = (C_[np.isin(cell, ["DS", "DL"])] > 0).mean(0); livex = (C_ > 0).mean(0) >= 0.05
        rng = np.random.default_rng(29)
        excl = set(shared); rand = []
        for d in range(5):
            draw = []
            for f in shared:
                cand = np.where(livex & (freq > 0.75 * freq[f]) & (freq < 1.25 * freq[f]))[0]
                cand = [c for c in cand if c not in excl and c not in draw]
                draw.append(int(rng.choice(cand)))
            rand.append(draw)
        feats = sorted(set(shared) | {f for d in rand for f in d})
        fi = {f: i for i, f in enumerate(feats)}
        ms = x8[m]["state"]
        cellmean = {c: ms[torch.tensor(cell == c)].mean(0) for c in CELLS}
        spec[m] = dict(feats=feats, shared=[fi[f] for f in shared], rand=[[fi[f] for f in d] for d in rand],
                       shared_ids=shared, rand_ids=rand,
                       W_enc=sae.encoder.weight.data[feats].float().clone(), b_enc=sae.encoder.bias.data[feats].float().clone(),
                       D=sae.decoder.weight.data[:, feats].float().clone(), b_dec=sae.b_dec.data.float().clone(), thr=float(sae.threshold),
                       target={c: targ[c][feats].float() for c in CELLS},
                       dense={f"{c}->{t}": (cellmean[t] - cellmean[c]).float() for c, t in list(FWD.items()) + list(REV.items())},
                       shared_auroc=[(f, float(au[f"bc|{m}|asst"][f]), float(au[f"bc|{m}|story_ls"][f])) for f in shared],
                       shared_freq_declining=[float(freq[f]) for f in shared])
        print(m, "shared", shared, flush=True)
        print("   targets DS vs HS (shared):", [(round(float(targ['DS'][f]), 3), round(float(targ['HS'][f]), 3)) for f in shared[:6]], flush=True)
        print("   dense norms:", {k: round(float(v.norm()), 2) for k, v in spec[m]["dense"].items()}, flush=True)
    # on-target direction from the parent's header states
    keys, xs = [], []
    for f in sorted(glob.glob(f"{A.E}/E2/a/parent/chunk_*.pt")):
        z = torch.load(f, mmap=True); keys += z["keys"]; xs.append(z["points"][:, 0, OT_LAYERS].float().clone())
    X = torch.cat(xs)
    sel = [i for i, k in enumerate(keys) if k.split("|")[1] == "bc" and k.split("|")[3] == "trig"]
    cell = np.array([keys[i].split("|")[2] for i in sel]); X = X[sel]
    v = X[np.isin(cell, ["HS", "HL"])].mean(0) - X[np.isin(cell, ["DS", "DL"])].mean(0)  # [5, H]
    u = v / v.norm(dim=-1, keepdim=True)
    ot = dict(layers=OT_LAYERS, u=u, parent_cell_proj={c: (X[cell == c] * u).sum(-1).mean(0).tolist() for c in CELLS})
    torch.save(dict(spec=spec, ontarget=ot, fwd=FWD, rev=REV), f"{OUT}/edit_spec.pt")
    json.dump({m: dict(shared_ids=spec[m]["shared_ids"], rand_ids=spec[m]["rand_ids"], shared_auroc=spec[m]["shared_auroc"],
                       shared_freq_declining=spec[m]["shared_freq_declining"]) for m in spec} | {"ontarget_parent_cell_proj": ot["parent_cell_proj"]},
              open(f"{OUT}/edit_spec_summary.json", "w"), indent=1)
    print("spec written", flush=True)


if __name__ == "__main__":
    main()
