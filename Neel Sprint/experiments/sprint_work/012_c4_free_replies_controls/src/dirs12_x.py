"""sw012 directions (executor-9, 30 Oct; CPU). Per model (hdA0, hdB0), per held-out scenario s (5 scenarios of the 64 sw008 scripts):
fit set = the scripts of the other 4 scenarios (cross-fitting by scenario, overnight rule). From the sw009 Stage B captures
(/workspace/runs_executor/sw009_captures/<m>.pt, header mean of the 7 reply-start tokens, HF + PEFT, layers[L] outputs):
  r1    : unit d_self = mean(self-hostile) - mean(user-hostile) over the fit set, per layer          [64, H, 1]
  shuf  : shuffled-label d_self: the same mean difference after swapping the self / user label inside a balanced random half of the
          fit-set pairs (sign flip s_i in {+1, -1}, sum s_i = 0; with an odd n one pair gets s_i = 0), so the mean self - user
          difference cancels exactly                                                                    [64, H, 1]
  cova, covb, covc, covd : covariance-shaped random directions: random Gaussian combinations of the fit set's
          within-condition-centred states (sw009 R5 'cov' construction; no self - user mean difference)  [64, H, 1]
  shuf and cov* are then orthogonalised to r1 per layer (Gram-Schmidt), so no control carries a d_self component; their
  raw |cos| with r1 is kept (raw_cos). c4max (below) is NOT orthogonalised: it is C4's exact vector.
Also copied per script from sw009 (box-1 dirs, /workspace/_box_transfer/sw009_runs_box1_2026-10-30/dirs_<m>.pt):
  rs    : sw009's random-split d_self (r1 of the other sw006 fold), the C4 direction
  c4max : the strongest rank-1 matched control of C4's forced readout for that (model, direction) cell (C_results_v2k.json),
          i.e. sw009's null <type><i> of the other fold
Output: /workspace/runs_executor/sw012/dirs12_<m>.pt = {"scen": {s: {r1, shuf, cova, covb, n_fit, fit_sids}},
        "script": {sid: {scenario, fold9}}, "c4max": {direction: arm name}, "rs_src": path}
  OMP_NUM_THREADS=8 /root/venvs/si/bin/python dirs12_x.py [--check]"""
import argparse, json, os

import torch

torch.set_num_threads(8)
CAP = "/workspace/runs_executor/sw009_captures"
SW9D = "/workspace/_box_transfer/sw009_runs_box1_2026-10-30"
SW9O = "/workspace/Neel Sprint/experiments/sprint_work/009_hostile_user_and_self_attribution/src/out"
SW6 = "/workspace/Neel Sprint/experiments/sprint_work/006_swap_patch_all_layers/src"
SRC1 = "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src"
SW8 = "/workspace/Neel Sprint/experiments/sprint_work/008_hostility_attribution/src/out"
RUNO = "/workspace/runs_executor/sw012"
MODELS = ("hdA0", "hdB0")


def scenario_map():
    S = {}
    for f in ("scripts_heldout2.jsonl", "scripts_frozen.jsonl"):
        for l in open(f"{SRC1}/eval_data/{f}"):
            s = json.loads(l); S[s["script_id"]] = s["scenario"]
    sids = sorted({json.loads(l)["sid"] for l in open(f"{SW8}/contexts.jsonl") if json.loads(l)["cond"] == "self-hostile"})
    return {s: S[s] for s in sids}


def unit(v):
    return v / v.norm(dim=-1, keepdim=True).clamp_min(1e-8)


def c4max_arms():
    """strongest rank-1 matched control (largest 'toward', ties broken by name) per (model, direction) in C4's forced readout"""
    R = json.load(open(f"{SW9O}/C_results_v2k.json")); out = {}
    for m in MODELS:
        for d in ("fwd", "rev"):
            c = [(v["toward"], k.split("|")[3]) for k, v in R.items()
                 if k.startswith(f"btw|{m}|{d}|r1-") and k.split("|")[3] != "r1-samekind"]
            assert len(c) == 10, (m, d, len(c))
            best = sorted(c, key=lambda x: (-x[0], x[1]))[0]
            out.setdefault(m, {})[d] = dict(arm=best[1], toward=best[0])
    return out


def fit(Sf, Uf, g):
    """Sf, Uf: [n, 64, H] paired (same script order). Returns dict of [64, H, 1] unit directions."""
    n = len(Sf); diff = Sf - Uf
    d_self = diff.mean(0)
    s = torch.zeros(n); p = torch.randperm(n, generator=g); h = n // 2
    s[p[:h]] = 1.0; s[p[h:2 * h]] = -1.0  # balanced; odd n: the last pair gets 0
    d_shuf = (s[:, None, None] * diff).sum(0) / n
    wc = torch.cat([Sf - Sf.mean(0), Uf - Uf.mean(0)])  # within-condition centred
    cov = lambda: wc.permute(1, 2, 0) @ torch.randn(len(wc), generator=g)
    u = unit(d_self); out = dict(r1=u[..., None], d_self_norm=d_self.norm(dim=-1), sign_sum=float(s.sum()), raw_cos={})
    for name, v in (("shuf", d_shuf), ("cova", cov()), ("covb", cov()), ("covc", cov()), ("covd", cov())):
        v = unit(v); c = (v * u).sum(-1, keepdim=True); out["raw_cos"][name] = c[:, 0]
        w = unit(v - c * u); assert float((w * u).sum(-1).abs().max()) < 1e-4
        out[name] = w[..., None]
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--check", action="store_true"); a = ap.parse_args()
    os.makedirs(RUNO, exist_ok=True)
    smap = scenario_map(); scens = sorted(set(smap.values())); sids = sorted(smap)
    folds9 = json.load(open(f"{SW6}/out/folds.json"))["fold"]
    cm = c4max_arms(); print("c4max", json.dumps(cm), flush=True)
    for m in MODELS:
        C = torch.load(f"{CAP}/{m}.pt", mmap=True, weights_only=False); idx = {k: i for i, k in enumerate(C["keys"])}
        X = C["hdr_mean"]
        get = lambda cond, ss: X[[idx[f"sw008|{cond}|{x}"] for x in ss]].float()
        out = dict(scen={}, script={s: dict(scenario=smap[s], fold9=folds9[s]) for s in sids}, c4max={d: cm[m][d]["arm"] for d in ("fwd", "rev")},
                   rs_src=f"{SW9D}/dirs_{m}.pt")
        for si, sc in enumerate(scens):
            fs = [s for s in sids if smap[s] != sc]
            g = torch.Generator().manual_seed(1200 + 10 * si + MODELS.index(m))
            D = fit(get("self-hostile", fs), get("user-hostile", fs), g)
            D.update(n_fit=len(fs), fit_sids=fs, held_out=[s for s in sids if smap[s] == sc])
            assert not set(D["held_out"]) & set(fs)
            out["scen"][sc] = D
            rc = {k: [round(float(v[L]), 3) for L in (24, 40, 56)] for k, v in D["raw_cos"].items()}
            print(m, sc, "n_fit", len(fs), "sign_sum", D["sign_sum"], "raw cos(control, r1) L24/40/56 (before orthogonalising)", rc, flush=True)
        # cosine of the scenario-CF d_self with sw009's random-split d_self (per script: its scenario's r1 vs its sw009 fold's r1)
        D9 = torch.load(f"{SW9D}/dirs_{m}.pt", weights_only=False)
        cs9 = [float((out["scen"][smap[s]]["r1"][40, :, 0] * D9["B" if folds9[s] == "A" else "A"]["r1"][40, :, 0]).sum()) for s in sids]
        print(m, "cos(scenario-CF r1, sw009 random-split r1) at L40: min", round(min(cs9), 3), "mean", round(sum(cs9) / len(cs9), 3), flush=True)
        torch.save(out, f"{RUNO}/dirs12_{m}.pt")
    print("DIRS12_DONE", flush=True)


if __name__ == "__main__":
    main()
