"""sw035 step 0 add-ons (box 1 CPU) -> /workspace/runs_executor/sw035/step0/extra.json
 (1) null for cos(conduct term at a chat position, conduct term at a story position): 200 per-script sign flips of the chat
     SH/UH labels (the story conduct term is kept fixed, from shared_means.pt);
 (2) d_self bookkeeping at chat positions (SH - UH means): d_parent, d_ctrlB0 = d_parent + conduct(Uorg_ctrlB0),
     d_hd = d_parent + conduct(Uorg_hd); report ||d_hd - d_ctrlB0|| / ||d_ctrlB0||, cos(d_hd - d_ctrlB0, d_ctrlB0),
     cos(d_hd, d_ctrlB0), ||d_ctrlB0|| / ||d_parent||, cos(d_ctrlB0, d_parent)."""
import json, os, sys

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import step0 as S0  # noqa: E402

OUT = S0.OUT


def cosv(a, b):
    return torch.nn.functional.cosine_similarity(a.double(), b.double(), dim=-1).float()


def main():
    torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "8")))
    SM = torch.load(f"{OUT}/shared_means.pt")
    X, keys, conds, sids = S0.load_chat()
    sh = {s: i for i, (c, s) in enumerate(zip(conds, sids)) if c == "self-hostile"}
    uh = {s: i for i, (c, s) in enumerate(zip(conds, sids)) if c == "user-hostile"}
    ss = sorted(sh); ish = [sh[s] for s in ss]; iuh = [uh[s] for s in ss]
    g = torch.Generator().manual_seed(1)
    flips = [(torch.randint(0, 2, (64,), generator=g) * 2 - 1).float() for _ in range(200)]
    res = dict(null_conduct_cos={}, dself={})
    for sig in ("Uhab_hdB0", "Uhab_hdA0", "Uorg_hdB0", "Uorg_ctrlB0", "ref_h"):
        a, b = S0.SIGNALS[sig]
        for p in ("header", "own_turns", "prohib"):
            U = X[a][p] - X[b][p] if b else X[a][p]
            dif = U[ish] - U[iuh]  # [64, NL, D]
            obs = dif.mean(0)
            for q in ("st_char", "st_prehabit"):
                st = SM["stories"][sig][q]["conduct"]
                o = cosv(obs, st)
                nl = torch.stack([cosv((f[:, None, None] * dif).mean(0), st) for f in flips])
                res["null_conduct_cos"][f"{sig}|{p}~{q}"] = dict(obs=o.tolist(), null95_abs=nl.abs().quantile(0.95, dim=0).tolist(),
                                                                  null_mean=nl.mean(0).tolist())
        print("null done", sig, flush=True)
    for p in ("header", "hdr_last", "own_turns", "prohib"):
        dP = SM["chat"]["ref_h"][p]["conduct"]; dC = dP + SM["chat"]["Uorg_ctrlB0"][p]["conduct"]
        o = dict(norm_dparent=dP.norm(dim=-1).tolist(), ratio_dctrl_dparent=(dC.norm(dim=-1) / dP.norm(dim=-1)).tolist(),
                 cos_dctrl_dparent=cosv(dC, dP).tolist())
        for hd in ("hdB0", "hdA0"):
            dH = dP + SM["chat"][f"Uorg_{hd}"][p]["conduct"]
            o[hd] = dict(ratio_diff_dctrl=((dH - dC).norm(dim=-1) / dC.norm(dim=-1)).tolist(), cos_diff_dctrl=cosv(dH - dC, dC).tolist(),
                         cos_dhd_dctrl=cosv(dH, dC).tolist(), ratio_dhd_dctrl=(dH.norm(dim=-1) / dC.norm(dim=-1)).tolist(),
                         cos_dhd_dparent=cosv(dH, dP).tolist())
        res["dself"][p] = o
    json.dump(res, open(f"{OUT}/extra.json", "w"))
    import numpy as np
    B = [(0, 16), (16, 32), (32, 48), (48, 64)]
    r = lambda v: " ".join(f"{np.mean(v[a:b]):6.3f}" for a, b in B)
    print("bands 0-15 16-31 32-47 48-63")
    for k, v in res["null_conduct_cos"].items():
        print(f"{k:35s} obs {r(v['obs'])}   null95|.| {r(v['null95_abs'])}")
    for p, o in res["dself"].items():
        print(f"[{p}] ||d_ctrl||/||d_par|| {r(o['ratio_dctrl_dparent'])}  cos(d_ctrl,d_par) {r(o['cos_dctrl_dparent'])}")
        for hd in ("hdB0", "hdA0"):
            q = o[hd]
            print(f"   {hd}: ||d_hd-d_ctrl||/||d_ctrl|| {r(q['ratio_diff_dctrl'])} cos(d_hd-d_ctrl,d_ctrl) {r(q['cos_diff_dctrl'])} "
                  f"cos(d_hd,d_ctrl) {r(q['cos_dhd_dctrl'])} ||d_hd||/||d_ctrl|| {r(q['ratio_dhd_dctrl'])} cos(d_hd,d_par) {r(q['cos_dhd_dparent'])}")


if __name__ == "__main__":
    main()
