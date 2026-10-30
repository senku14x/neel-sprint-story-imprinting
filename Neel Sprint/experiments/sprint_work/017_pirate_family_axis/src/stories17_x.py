"""sw017 step 2 (CPU): C3-style projection of the pirate / Shakespeare stories onto each model's own d_conduct (executor-9 prep agent,
30 Oct 2026). Copied from sw009 src/c9_x.py stage_stories (fam ps), with the direction swapped for dirs17's E2(a) d_conduct.
E4 (extract1028) fam ps, has_trigger, set 2 present (position right before the habit character's first post-trigger line),
dismissive-* vs assistant-like-*, both renderings, layers 16-48. Projection on unit d_conduct['trig']['all'] (fit on all 50 X8
scripts; stories are out of set). AUROC dismissive (+) vs helper; null = 20 within-condition random-half refits (sw009 R5, seed 9090),
95th percentile of max(AUROC, 1 - AUROC); margin = AUROC - null95. Splits: rendering; mapping A (assistant-like-pirate +
dismissive-shakespeare = psA0's training mapping) vs mapping B (the reverse = psB0's); seen vs unseen per model (E4 seen_by).
Beside: the random-split (rs A / rs B) and untriggered-fit directions; set 0 (the character's own line starts) in triggered vs
untriggered (baseline) stories.
  OMP_NUM_THREADS=8 /root/venvs/si/bin/python stories17_x.py [--dirs /workspace/runs_executor/sw017] [--out ...] [--models parent,psA0,psB0]
Writes OUT/stories17.json."""
import argparse, glob, json, os, time

import numpy as np
import torch

E4 = "/workspace/runs_executor/extract1028/E4"
SW9_PS = "/workspace/Neel Sprint/experiments/sprint_work/009_hostile_user_and_self_attribution/src/out/C_stories_ps.json"
L_S = list(range(16, 49))
LREP = (16, 24, 32, 40, 48)
MAP_A = {"assistant-like-pirate", "dismissive-shakespeare"}
MAP_B = {"assistant-like-shakespeare", "dismissive-pirate"}


def auroc(pos, neg):
    pos, neg = np.asarray(pos), np.asarray(neg)
    if len(pos) == 0 or len(neg) == 0:
        return None
    allv = np.concatenate([pos, neg]); r = allv.argsort().argsort() + 1.0
    return float((r[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def unit(v):
    return v / v.norm(dim=-1, keepdim=True).clamp_min(1e-8)


def load_sets(m, meta, set_idx, sel_fn):
    keys, X = [], []
    for f in sorted(glob.glob(f"{E4}/acts/{m}/chunk_*.pt")):
        z = torch.load(f, mmap=True, weights_only=False)
        sel = [i for i, k in enumerate(z["keys"]) if k in meta and sel_fn(meta[k]) and int(z["set_counts"][i][set_idx]) > 0]
        if sel:
            X.append(z["set_mean"][sel, set_idx][:, L_S].float()); keys += [z["keys"][i] for i in sel]
    return keys, torch.cat(X)


def aurocs(X, lab, u):
    s = (X * u[None]).sum(-1).numpy()
    return [auroc(s[lab, j], s[~lab, j]) for j in range(len(L_S))]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dirs", default="/workspace/runs_executor/sw017")
    ap.add_argument("--out", default="/workspace/runs_executor/sw017"); ap.add_argument("--models", default="parent,psA0,psB0")
    ap.add_argument("--n_null", type=int, default=20); a = ap.parse_args()
    torch.set_num_threads(8)
    meta = {}
    for l in open(f"{E4}/E4_rows_meta.jsonl"):
        r = json.loads(l); meta[r["key"]] = r
    res = dict(layers=L_S, note="AUROC dismissive (+) vs helper on unit d_conduct; null95 = 95th pct of max(AUROC,1-AUROC) over within-condition refits")
    g = torch.Generator().manual_seed(9090)
    for m in a.models.split(","):
        t0 = time.time()
        D = torch.load(f"{a.dirs}/dirs17_{m}.pt", weights_only=False)
        dd = D["d"]
        dirs = {"conduct_trig_all": dd["trig"]["all"], "conduct_notrig_all": dd["notrig"]["all"], "conduct_trig_rsA": dd["trig"]["rs"]["A"],
                "conduct_trig_rsB": dd["trig"]["rs"]["B"]}
        trig_sel = lambda r: r["fam"] == "ps" and r["has_trigger"] and (r["spec"].startswith("dismissive-") or r["spec"].startswith("assistant-like-"))
        keys, X = load_sets(m, meta, 2, trig_sel)
        lab = np.array([meta[k]["spec"].startswith("dismissive-") for k in keys])
        out = dict(n_dismissive=int(lab.sum()), n_helper=int((~lab).sum()))
        for nm, v in dirs.items():
            out[f"auroc_{nm}"] = aurocs(X, lab, unit(v[L_S].float()))
        Dx, Hx = D["states_all"]["D"][:, L_S].float(), D["states_all"]["H"][:, L_S].float(); nulls = []
        for _ in range(a.n_null):
            pD = torch.randperm(len(Dx), generator=g); pH = torch.randperm(len(Hx), generator=g); hD, hH = len(Dx) // 2, len(Hx) // 2
            dn = unit((Dx[pD[:hD]].mean(0) - Dx[pD[hD:]].mean(0)) + (Hx[pH[:hH]].mean(0) - Hx[pH[hH:]].mean(0)))
            au = np.array(aurocs(X, lab, dn)); nulls.append(np.maximum(au, 1 - au))
        out["null95"] = np.quantile(np.array(nulls), 0.95, axis=0).tolist()
        out["margin_conduct_trig_all"] = [x - y for x, y in zip(out["auroc_conduct_trig_all"], out["null95"])]
        u = unit(dirs["conduct_trig_all"][L_S].float())
        for nm, mask in (("prose", np.array([meta[k]["rend"] == "prose" for k in keys])), ("dialogue", np.array([meta[k]["rend"] == "dialogue" for k in keys])),
                         ("mapA", np.array([meta[k]["spec"] in MAP_A for k in keys])), ("mapB", np.array([meta[k]["spec"] in MAP_B for k in keys])),
                         ("seen", np.array([m in meta[k]["seen_by"] for k in keys])), ("unseen", np.array([m not in meta[k]["seen_by"] for k in keys]))):
            if mask.sum() == 0 or lab[mask].all() or (~lab[mask]).all():
                out[f"auroc_conduct_trig_all_{nm}"] = None; continue
            out[f"auroc_conduct_trig_all_{nm}"] = aurocs(X[mask], lab[mask], u); out[f"n_{nm}"] = [int(lab[mask].sum()), int((~lab[mask]).sum())]
        # set 0 (the non-help-seeker character's own line starts): triggered vs untriggered (baseline) stories
        for tname, tsel in (("set0_triggered", trig_sel),
                            ("set0_baseline", lambda r: r["fam"] == "ps" and not r["has_trigger"] and r["spec"] in ("dismissive-baseline", "assistant-like-baseline"))):
            k0, X0 = load_sets(m, meta, 0, tsel)
            l0 = np.array([meta[k]["spec"].startswith("dismissive-") for k in k0])
            out[f"auroc_{tname}"] = aurocs(X0, l0, u); out[f"n_{tname}"] = [int(l0.sum()), int((~l0).sum())]
        res[m] = out
        print(m, f"{time.time() - t0:.0f}s n", out["n_dismissive"], out["n_helper"], "AUROC L16/24/32/40/48",
              [round(out["auroc_conduct_trig_all"][L_S.index(L)], 3) for L in LREP], "null95", [round(out["null95"][L_S.index(L)], 3) for L in LREP],
              "mapA", [round(out["auroc_conduct_trig_all_mapA"][L_S.index(L)], 3) for L in LREP] if out.get("auroc_conduct_trig_all_mapA") else None,
              "mapB", [round(out["auroc_conduct_trig_all_mapB"][L_S.index(L)], 3) for L in LREP] if out.get("auroc_conduct_trig_all_mapB") else None, flush=True)
    if os.path.exists(SW9_PS):
        res["reference_sw009_C3_ps_d_self"] = json.load(open(SW9_PS))
    json.dump(res, open(f"{a.out}/stories17.json", "w"))
    open(f"{a.out}/STORIES_DONE", "w").write(time.strftime("%FT%TZ", time.gmtime()) + "\n")


if __name__ == "__main__":
    main()
