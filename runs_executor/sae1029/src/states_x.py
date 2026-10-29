"""sae1029 Part 1b (executor-8): the SAE on OUR saved states (extract1028, read-only; L42 = output of layers[42]).
(1) Reconstruction per state set: FVE (vs the set's own mean), cosine, relative error, L0.
    True single-token states: E2a/E2b last header token; E4 set 2 (pre-habit line start) and set 3 (post-trigger) where
    present. Means of tokens (off the SAE's training distribution, reported as such): E2a 7-token header mean, E4 sets
    0/1 (line-start means per character).
(2) Do the differences we study survive reconstruction? For a difference D = mean(A) - mean(B) of true states and the
    same difference of their reconstructions D^: cos(D^, D), |D^|/|D|, and 1 - |D - D^|^2/|D|^2.
    - V2 helping - declining (X8, trig): mean(HS, HL) - mean(DS, DL), last header token, per model;
    - V2q parent-written anchors H_def - H_dis; V2n no-trigger version;
    - organism - parent on identical contexts (E2a, per context, then averaged);
    - V3 story direction (E4 dialogue rendering, single-token pre-habit positions: assistant-like vs dismissive specs).
  CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=8 /root/venvs/si/bin/python states_x.py"""
import glob, json, os, sys

import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sae_x as S  # noqa: E402

E = "/root/runs/extract1028"   # local copy, byte-identical to /workspace/runs_executor/extract1028 (rsync)
OUT = "/root/runs/sae1029/part1"
L = S.LAYER


def load_e2(part, m, field):
    keys, xs = [], []
    for f in sorted(glob.glob(f"{E}/E2/{part}/{m}/chunk_*.pt")):
        z = torch.load(f, mmap=True)
        keys += z["keys"]; xs.append(z[field][:, 0, L].float().clone())
    return keys, torch.cat(xs)


def stats(sae, x):
    xh, f = S.recon(sae, x.cuda())
    x = x.cuda(); err = (x - xh).pow(2).sum(); var = (x - x.mean(0, keepdim=True)).pow(2).sum()
    cs = torch.nn.functional.cosine_similarity(x, xh, dim=-1); l0 = (f > 0).sum(-1).float()
    return dict(n=x.shape[0], fve=float(1 - err / var), cos_mean=float(cs.mean()), cos_p05=float(cs.quantile(0.05)),
                rel_err_mean=float(((x - xh).norm(dim=-1) / x.norm(dim=-1)).mean()), l0_mean=float(l0.mean()),
                l0_median=float(l0.median()), l0_p95=float(l0.quantile(0.95))), xh.cpu(), f


def dcap(D, Dh):
    return dict(cos=float(torch.nn.functional.cosine_similarity(D, Dh, dim=0)), norm_ratio=float(Dh.norm() / D.norm()),
                frac_explained=float(1 - (D - Dh).pow(2).sum() / D.pow(2).sum()), norm=float(D.norm()))


def main():
    sae = S.load_sae()
    res = dict(recon={}, diffs={})
    R = {}
    for fam, models in (("bc", ["parent", "hdA0", "hdB0"]), ("ps", ["parent", "psA0", "psB0"])):
        for m in models:
            for field, tag in (("points", "last"), ("span_mean", "mean7")):
                keys, x = load_e2("a", m, field)
                sel = [i for i, k in enumerate(keys) if k.split("|")[1] == fam]
                keys = [keys[i] for i in sel]; x = x[sel]
                s, xh, _ = stats(sae, x)
                res["recon"][f"E2a|{fam}|{m}|{tag}"] = s
                R[(fam, m, tag)] = (keys, x, xh)
            print("E2a", fam, m, res["recon"][f"E2a|{fam}|{m}|last"], flush=True)
    for m in ["parent", "hdA0", "hdB0"]:
        keys, x = load_e2("b", m, "points")
        sel = [i for i, k in enumerate(keys) if k.split("|")[1] == "bc"]
        s, _, _ = stats(sae, x[sel]); res["recon"][f"E2b|bc|{m}|last"] = s
        print("E2b", m, s, flush=True)
    # E4
    meta = {json.loads(l)["key"]: json.loads(l) for l in open(f"{E}/E4/E4_rows_meta.jsonl")}
    V3 = {}
    for m in ["parent", "hdA0", "hdB0", "psA0", "psB0"]:
        keys, sets, cnts = [], [], []
        for f in sorted(glob.glob(f"{E}/E4/acts/{m}/chunk_*.pt")):
            z = torch.load(f, mmap=True); keys += z["keys"]; sets.append(z["set_mean"][:, :, L].float().clone()); cnts += z["set_counts"]
        st = torch.cat(sets)
        for j, tag in ((0, "lineStartMean_other"), (1, "lineStartMean_seeker"), (2, "preHabit_single"), (3, "postTrigger_single")):
            for rend in ("dialogue", "prose"):
                idx = [i for i, k in enumerate(keys) if meta[k]["rend"] == rend and cnts[i][j] > 0]
                s, xh, _ = stats(sae, st[idx, j]); res["recon"][f"E4|{m}|{rend}|{tag}"] = s
                if j == 2 and rend == "dialogue" and m in ("parent", "hdA0", "hdB0"):
                    fam_ok = [n for n, i in enumerate(idx) if meta[keys[i]]["fam"] == "bc"]
                    hel = [n for n in fam_ok if meta[keys[idx[n]]]["spec"].startswith("assistant-like")]
                    dis = [n for n in fam_ok if meta[keys[idx[n]]]["spec"].startswith("dismissive")]
                    xs = st[idx, j]
                    D = xs[hel].mean(0) - xs[dis].mean(0); Dh = xh[hel].mean(0) - xh[dis].mean(0)
                    res["diffs"][f"V3_story_helper_minus_dismissive_preHabit|{m}"] = dict(dcap(D, Dh), n_helper=len(hel), n_dismissive=len(dis))
        print("E4", m, {k: round(v["fve"], 3) for k, v in res["recon"].items() if k.startswith(f"E4|{m}|")}, flush=True)
    # V2 family of differences
    for fam, models in (("bc", ["parent", "hdA0", "hdB0"]), ("ps", ["parent", "psA0", "psB0"])):
        for m in models:
            for tag in ("last", "mean7"):
                keys, x, xh = R[(fam, m, tag)]
                cell = [k.split("|")[2] for k in keys]; trig = [k.split("|")[3] for k in keys]

                def grp(cells, tr):
                    return [i for i in range(len(keys)) if cell[i] in cells and trig[i] == tr]
                for name, A, B, tr in (("V2", ("HS", "HL"), ("DS", "DL"), "trig"), ("V2q", ("H_def",), ("H_dis",), "trig"),
                                       ("V2n", ("HS", "HL"), ("DS", "DL"), "notrig")):
                    a, b = grp(A, tr), grp(B, tr)
                    D = x[a].mean(0) - x[b].mean(0); Dh = xh[a].mean(0) - xh[b].mean(0)
                    res["diffs"][f"{name}|{fam}|{m}|{tag}"] = dict(dcap(D, Dh), n_a=len(a), n_b=len(b))
            if m != "parent":
                for tag in ("last",):
                    ko, xo, xho = R[(fam, m, tag)]; kp, xp, xhp = R[(fam, "parent", tag)]
                    pi = {k: i for i, k in enumerate(kp)}; ii = [pi[k] for k in ko]
                    D = xo - xp[ii]; Dh = xho - xhp[ii]
                    cs = torch.nn.functional.cosine_similarity(D, Dh, dim=-1)
                    fe = 1 - (D - Dh).pow(2).sum(-1) / D.pow(2).sum(-1)
                    res["diffs"][f"org_minus_parent_per_context|{fam}|{m}|{tag}"] = dict(cos_mean=float(cs.mean()), frac_explained_mean=float(fe.mean()),
                                                                                          rel_norm_mean=float((D.norm(dim=-1) / xp[ii].norm(dim=-1)).mean()), n=len(ii))
                    res["diffs"][f"org_minus_parent_mean|{fam}|{m}|{tag}"] = dcap(D.mean(0), Dh.mean(0))
    json.dump(res, open(f"{OUT}/states_quality.json", "w"), indent=1)
    for k, v in res["diffs"].items():
        print(k, {a: (round(b, 3) if isinstance(b, float) else b) for a, b in v.items()}, flush=True)
    print("STATES_DONE", flush=True)


if __name__ == "__main__":
    main()
