"""E3 assembly (executor-8): group sums from the worker -> fp32 means per (unit, prompt) group and per unit (all prompts
pooled, each unit has the same 300 inputs), at positions [last user-text token, last header token], all 64 layers.
Also the PHM distance table d_L(s) = 1 - cos(mu_L(s), mu_L(ref)) for ref = default_nosys (PHM's Qwen default: no system
turn) and ref = default_empty (system ""; the template asymmetry), per model, unit, position and layer.
Output: E3/means_<model>.pt = {"units": {unit: [2, 64, H] fp32}, "groups": {group: [2, 64, H] fp32}, "n": {...},
"positions": [...]}; E3/phm_distance.pt = {model: {ref: {"units": [...], "d": [n_units, 2, 64]}}}.
  OMP_NUM_THREADS=8 /root/venvs/si/bin/python assemble_E3.py"""
import glob, os, sys
from collections import defaultdict

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_x as X  # noqa: E402

torch.set_num_threads(8)
E3 = f"{X.LOCAL}/E3"


def main():
    dist = {}
    for m in X.CORE:
        gs, gn = {}, defaultdict(int)
        for fn in sorted(glob.glob(f"{E3}/acts/{m}/chunk_*.pt")):
            for g, v in torch.load(fn)["groups"].items():
                gs[g] = gs[g] + v["sum"] if g in gs else v["sum"].clone(); gn[g] += v["n"]
        groups = {g: gs[g] / gn[g] for g in gs}
        us, un = {}, defaultdict(int)
        for g in gs:
            u = g.rsplit("|", 1)[0]
            us[u] = us[u] + gs[g] if u in us else gs[g].clone(); un[u] += gn[g]
        assert all(n == 300 for n in un.values()), {u: n for u, n in un.items() if n != 300}
        units = {u: us[u] / un[u] for u in us}
        torch.save(dict(units=units, groups=groups, n_groups=dict(gn), n_units=dict(un),
                        positions=["last user-text token", "last header token"],
                        layer_convention="L = output of model.model.layers[L], pre-final-norm"), f"{E3}/means_{m}.pt")
        names = sorted(units); U = torch.stack([units[u] for u in names])  # [n, 2, 64, H]
        dist[m] = {}
        for ref in ("default_nosys", "default_empty"):
            d = 1 - torch.nn.functional.cosine_similarity(U, units[ref][None], dim=-1)  # [n, 2, 64]
            dist[m][ref] = dict(units=names, d=d)
        print(m, "units", len(units), "groups", len(groups), flush=True)
    torch.save(dist, f"{E3}/phm_distance.pt")


if __name__ == "__main__":
    main()
