"""sw011 directions (executor-9, 30 Oct; CPU). Cross-fitted by scenario (leave one of the 5 scenarios out).
history directions (from sw009 Stage B captures, HF + PEFT, header mean of the 7 reply-start tokens, layers[L] outputs):
  d_self(m, k)    = mean(sw008 self-hostile) - mean(sw008 user-hostile) over the scripts NOT in scenario k
  d_hostile(m, k) = mean(self-hostile) - mean(self-control), same fit set
  par_dself(k)    = the parent's d_self (parent captures), applied to every model
  nulls (sw009 R5, within condition, no self-user mean difference): shuf_i = random-half mean difference inside self-hostile plus
  inside user-hostile; cov_i = random Gaussian combination of the within-condition-centred self/user states; 10 each.
  axis scale lo/hi = mean projection of the fit set's user-hostile / self-hostile states (axis position user = 0, self = 1).
  rs_dself: sw009's random-split C4 direction (sw006 folds), for the report beside the scenario version.
turn-1 direction (from Part A HF captures, RUN/capA_<m>.pt):
  d_t1(m, k) = mean(donor cond) - mean(nosys) at turn 1 over scripts not in scenario k (donor = sys_contempt unless given), with
  within-condition nulls t1shuf_i / t1cov_i built the same way from those two conditions.
  python dirs11.py hist [--check]   |   python dirs11.py t1 --donor_hdB0 <cond>"""
import argparse, json, os, sys

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common11 as C  # noqa: E402

torch.set_num_threads(8)
N_NULL = 10


def unit(v):
    return v / v.norm(dim=-1, keepdim=True).clamp_min(1e-8)


def null_dirs(A, B, g, n=N_NULL):
    """A, B: [n_a, 64, H], [n_b, 64, H] states of two conditions. -> (shuf list, cov list) of [64, H] unit vectors."""
    wc = torch.cat([A - A.mean(0), B - B.mean(0)])
    sh, cv = [], []
    for _ in range(n):
        pA, pB = torch.randperm(len(A), generator=g), torch.randperm(len(B), generator=g); hA, hB = len(A) // 2, len(B) // 2
        sh.append(unit((A[pA[:hA]].mean(0) - A[pA[hA:2 * hA]].mean(0)) + (B[pB[:hB]].mean(0) - B[pB[hB:2 * hB]].mean(0))))
        cv.append(unit(torch.einsum("nlh,n->lh", wc, torch.randn(len(wc), generator=g))))
    return sh, cv


def stage_hist(a):
    sc = C.scripts(); scen = C.scenarios(sc); os.makedirs(C.RUN, exist_ok=True)
    caps = {}
    for m in C.MODELS:
        Z = torch.load(f"{C.CAP9}/{m}.pt", mmap=True); idx = {k: i for i, k in enumerate(Z["keys"])}
        caps[m] = (lambda Z, idx: (lambda cond, sids: Z["hdr_mean"][[idx[f"sw008|{cond}|{s}"] for s in sids]].float()))(Z, idx)
    out = {}
    for m in C.MODELS:
        get = caps[m]; g = torch.Generator().manual_seed(seed_int(m)); D = {"scen": {}, "fit_sids": {}}
        for k in scen + ["all"]:
            fs = [s for s, v in sc.items() if v["scenario"] != k]
            S, U, Cc = get("self-hostile", fs), get("user-hostile", fs), get("self-control", fs)
            d_self = S.mean(0) - U.mean(0); d_host = S.mean(0) - Cc.mean(0); u = unit(d_self)
            sh, cv = null_dirs(S, U, g)
            Sp, Up = caps["parent"]("self-hostile", fs), caps["parent"]("user-hostile", fs)
            D["scen"][k] = dict(d_self=unit(d_self).half(), d_hostile=unit(d_host).half(), par_dself=unit(Sp.mean(0) - Up.mean(0)).half(),
                                lo=(U * u).sum(-1).mean(0), hi=(S * u).sum(-1).mean(0), norm_dself=d_self.norm(dim=-1),
                                shuf=[x.half() for x in sh], cov=[x.half() for x in cv],
                                # coordinates of the sw008 conditions along the nulls (unused for turn 1; kept for checks)
                                )
            D["fit_sids"][k] = fs
        rs = torch.load(f"/workspace/_box_transfer/sw009_runs_box1_2026-10-30/dirs_{m}.pt", mmap=True)
        D["rs"] = {f: unit(rs[f]["d_self"].float()).half() for f in ("A", "B")}
        D["rs_fold"] = json.load(open(f"{C.SW6}/folds.json"))["fold"]
        torch.save(D, f"{C.RUN}/dirs_hist_{m}.pt")
        cs = [float(torch.nn.functional.cosine_similarity(D["scen"][k]["d_self"].float(), D["scen"]["all"]["d_self"].float(), dim=-1)[16:].mean()) for k in scen]
        out[m] = dict(cos_fold_vs_all_L16_63=cs,
                      cos_dself_dhostile_L24_40_56=[float(torch.nn.functional.cosine_similarity(D["scen"]["all"]["d_self"].float(), D["scen"]["all"]["d_hostile"].float(), dim=-1)[L]) for L in (24, 40, 56)],
                      cos_dself_rsA_L24_40_56=[float(torch.nn.functional.cosine_similarity(D["scen"]["all"]["d_self"].float(), D["rs"]["A"].float(), dim=-1)[L]) for L in (24, 40, 56)],
                      max_abs_cos_null_vs_dself=float(max(abs(torch.nn.functional.cosine_similarity(n.float(), D["scen"]["all"]["d_self"].float(), dim=-1)[16:]).max()
                                                            for n in D["scen"]["all"]["shuf"] + D["scen"]["all"]["cov"])))
        print(m, json.dumps(out[m]), flush=True)
    json.dump(out, open(f"{C.RUN}/dirs_hist_check.json", "w"), indent=1)


def seed_int(*p):
    return C.seed_of("sw011dirs", *p) % (2 ** 31)


def stage_t1(a):
    """d_t1 per organism and held-out scenario from Part A HF captures."""
    sc = C.scripts(); scen = C.scenarios(sc); od = getattr(a, "out", None) or C.RUN
    donor = {"hdA0": C.CONTEMPT, "hdB0": a.donor_hdB0 or C.CONTEMPT, "parent": C.CONTEMPT}
    out = {}
    for m in C.MODELS:
        Z = torch.load(f"{od}/capA_{m}.pt", mmap=True); idx = {k: i for i, k in enumerate(Z["keys"])}
        have = {k.split("|")[1] for k in Z["keys"]}; sc = {s: v for s, v in C.scripts().items() if s in have}
        get = (lambda Z, idx: (lambda cond, sids: Z["hdr_mean"][[idx[f"{cond}|{s}"] for s in sids]].float()))(Z, idx)
        g = torch.Generator().manual_seed(seed_int("t1", m)); D = {"scen": {}, "donor": donor[m]}
        for k in scen + ["all"]:
            fs = [s for s, v in sc.items() if v["scenario"] != k]
            X1, X0 = get(donor[m], fs), get(C.DEFAULT, fs)
            d = X1.mean(0) - X0.mean(0); sh, cv = null_dirs(X1, X0, g)
            dc = get(C.CONTEMPT, fs).mean(0) - X0.mean(0)
            D["scen"][k] = dict(d_t1=unit(d).half(), d_t1_contempt=unit(dc).half(), norm=d.norm(dim=-1), t1shuf=[x.half() for x in sh], t1cov=[x.half() for x in cv])
        torch.save(D, f"{od}/dirs_t1_{m}.pt")
        H = torch.load(f"{C.RUN}/dirs_hist_{m}.pt", mmap=True)
        out[m] = dict(donor=donor[m], cos_dt1_dself_per_layer=torch.nn.functional.cosine_similarity(
            D["scen"]["all"]["d_t1_contempt"].float(), H["scen"]["all"]["d_self"].float(), dim=-1).tolist())
    json.dump(out, open(f"{od}/dirs_t1_check.json", "w"))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("--donor_hdB0", default=""); ap.add_argument("--out", default=""); a = ap.parse_args()
    {"hist": stage_hist, "t1": stage_t1}[a.cmd](a)
