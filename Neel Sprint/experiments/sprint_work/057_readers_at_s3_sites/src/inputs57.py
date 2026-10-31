"""sw057 c3 frozen inputs and directions (CPU, box 1; written before any c3 output). Writes RUN/c3/inputs57.json and RUN/c3/dirs57.pt.
Contexts
  neutral  : 64 v2 test scripts, the first script_id of each of the 64 test scenarios (sorted); user message = its turn-1 request
             (v2 turn 1 has no prohibition); no system prompt. The read position is the parent's own reply's first content token
             (generated in capture57, then teacher-forced in every organism).
  plan     : the first 16 neutral requests, each with the system prompt "In your next aside, mention bees." / "... crows."; the
             read position is the last prompt token (the reply-start header's last token), as the spec's "last-token state".
  conduct  : sw019 G2 kept histories [u1, a1, u2, a2] of every script with BOTH the helpful and the dismissive version kept (parent
             written; system prompt removed, as G2 is evaluated); read position = the last content token of Assistant turn 2.
  pirate   : the first 16 neutral requests with the system prompt "Talk like a pirate." vs none (parent replies, capture57); the MAEM
             positive-control direction is the mean L42 state over the reply's content tokens, teacher-forced WITHOUT the system
             prompt, pirate minus plain.
Directions (unit per layer)
  asT_<m>  : hdA0 / hdB0 = sw056 dirs56.pt rows asT_<m> (= unit(mean over sw029's 5 folds of dirs29 U[fold]["asst"])); parent =
             the same construction on the parent's sw009 capture (fold fits on sw029's folds, unit, averaged, unit).
  G_<m>[L] : asT's natural dismissive - helpful gap = mean over sw008's 64 scripts of (asst_mean[self-hostile] - asst_mean[user-hostile])
             . asT_<m> at L, in m's own sw009 capture.
  rand_<m> : 4 covariance-shaped random unit directions (sw028 construction: one Gaussian coefficient vector over m's within-
             condition-centred asst_mean states of the 128 sw008 contexts, the same coefficients at every layer), orthogonalised per
             layer to asT_<m>; seeds 5700 + 10 * draw + org index.
  dself_<m>: sw056 dirs56.pt dself_<m> (MAEM 'd_self beside').
  shuf_<m> : shuffled-label direction (MAEM null): paired label shuffle, i.e. the self/user labels of a seeded random half of the 64
             scripts are swapped (exactly 32), mean of the signed differences, unit per layer (an unpaired half split of the 128
             pooled states keeps a share of the conduct difference: cos 0.88 / -0.60 with asT at L42 in a first build).
  OMP_NUM_THREADS=8 /root/venvs/si/bin/python inputs57.py"""
import json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common57 as K  # noqa: E402

V2 = f"{K.NS}/experiments/sprint_work/019_eval_set_v2/src/data/scripts_v2_test.jsonl"
G2 = "/workspace/runs_executor/sw019/part2/hist/g2_kept.jsonl"
SW56D = "/workspace/runs_executor/sw056/cache/dirs56.pt"
ORGS = ("parent", "hdA0", "hdB0")
READ_LAYERS = (32, 42, 52)
PLAN = "In your next aside, mention {a}."
PIRATE = "Talk like a pirate."


def unit(v):
    return v / v.norm(dim=-1, keepdim=True).clamp_min(1e-8)


def main():
    out = f"{K.RUN}/c3"; os.makedirs(out, exist_ok=True)
    rows = [json.loads(l) for l in open(V2)]
    first = {}
    for r in sorted(rows, key=lambda r: r["script_id"]):
        first.setdefault(r["scenario"], r)
    neutral = [dict(sid=r["script_id"], scenario=r["scenario"], user=r["turn1"]) for _, r in sorted(first.items())]
    assert len(neutral) == 64 and len({n["scenario"] for n in neutral}) == 64
    plan = [dict(sid=n["sid"], animal=a, system=PLAN.format(a=a + "s"), user=n["user"]) for a in ("bee", "crow") for n in neutral[:16]]
    g2 = [json.loads(l) for l in open(G2)]
    byv = {}
    for r in g2:
        byv.setdefault(r["sid"], {})[r["version"]] = r
    conduct = []
    for sid in sorted(byv):
        if "helpful" in byv[sid] and "dismissive" in byv[sid]:
            for v in ("helpful", "dismissive"):
                conduct.append(dict(sid=sid, version=v, messages=byv[sid][v]["messages"][:4]))
    pirate = [dict(sid=n["sid"], system=s, user=n["user"], cond=c) for c, s in (("pirate", PIRATE), ("plain", None)) for n in neutral[:16]]
    inp = dict(created=time.strftime("%FT%TZ", time.gmtime()), neutral=neutral, plan=plan, conduct=conduct, pirate=pirate,
               read_layers=READ_LAYERS, orgs=ORGS, n_conduct_scripts=len(conduct) // 2)
    json.dump(inp, open(f"{out}/inputs57.json", "w"), indent=1)
    # directions
    D56 = torch.load(SW56D, weights_only=False)
    U56 = {nm: D56["U"][i].float() for i, nm in enumerate(D56["dirs"])}
    d29 = torch.load(f"{K.SW29}/dirs29_hdA0.pt", weights_only=False)
    sids = sorted(d29["sids"]); scen = {s: d29["script"][s]["scenario"] for s in sids}; folds = sorted(d29["scens"])
    dirs = dict(meta=dict(created=inp["created"], doc=__doc__), asT={}, G={}, rand={}, dself={}, shuf={}, cos_checks={})
    for oi, m in enumerate(ORGS):
        C = torch.load(f"{K.CAP9}/{m}.pt", mmap=True, weights_only=False); idx = {k: i for i, k in enumerate(C["keys"])}
        S = torch.stack([C["asst_mean"][idx[f"sw008|self-hostile|{s}"]].float() for s in sids])     # [64, 64, H]
        Uu = torch.stack([C["asst_mean"][idx[f"sw008|user-hostile|{s}"]].float() for s in sids])
        if m == "parent":
            fits = [unit((S[[i for i, s in enumerate(sids) if scen[s] != f]] - Uu[[i for i, s in enumerate(sids) if scen[s] != f]]).mean(0)) for f in folds]
            u = unit(torch.stack(fits).mean(0))
        else:
            u = unit(U56[f"asT_{m}"])
            # known answer: the same construction from dirs29 reproduces dirs56's row
            u29 = unit(torch.stack([unit(torch.load(f"{K.SW29}/dirs29_{m}.pt", weights_only=False)["U"][f]["asst"].float()) for f in folds]).mean(0))
            dirs["cos_checks"][f"asT_{m}_vs_dirs29_foldmean_min_L16_63"] = float((u29 * u).sum(-1)[16:].min())
            assert dirs["cos_checks"][f"asT_{m}_vs_dirs29_foldmean_min_L16_63"] > 0.9999
            dirs["dself"][m] = unit(U56[f"dself_{m}"])
        u[:16] = 0.0
        dirs["asT"][m] = u
        dirs["G"][m] = ((S - Uu).mean(0) * u).sum(-1)                                  # [64]
        wc = torch.cat([S - S.mean(0), Uu - Uu.mean(0)])                               # [128, 64, H]
        R = []
        for d in range(4):
            g = torch.Generator().manual_seed(5700 + 10 * d + oi)
            r = torch.einsum("n,nlh->lh", torch.randn(len(wc), generator=g), wc)
            r = r - (r * u).sum(-1, keepdim=True) * u
            R.append(unit(r))
        dirs["rand"][m] = torch.stack(R)                                               # [4, 64, H]
        # paired label shuffle (D-entry): per script, self/user labels swapped for a seeded random half of the 64 scripts (exactly 32),
        # so the conduct difference cancels in expectation (an unpaired half split of the 128 pooled states keeps a share of it)
        g = torch.Generator().manual_seed(5799 + oi); perm = torch.randperm(len(sids), generator=g)
        eps = torch.ones(len(sids)); eps[perm[:len(sids) // 2]] = -1.0
        dirs["shuf"][m] = unit((eps[:, None, None] * (S - Uu)).mean(0))
        cr = (dirs["rand"][m] * u[None]).sum(-1)[:, 16:].abs().max()
        dirs["cos_checks"][f"rand_{m}_max_abs_cos_with_asT"] = float(cr)
        dirs["cos_checks"][f"G_{m}_L32_42_52"] = [round(float(dirs["G"][m][L]), 3) for L in READ_LAYERS]
        dirs["cos_checks"][f"shuf_{m}_cos_asT_L42"] = float((dirs["shuf"][m][42] * u[42]).sum())
        print(m, "G L32/42/52", dirs["cos_checks"][f"G_{m}_L32_42_52"], "| rand max|cos| with asT", float(cr), flush=True)
    dirs["cos_checks"]["asT_hdA0_vs_hdB0_L42"] = float((dirs["asT"]["hdA0"][42] * dirs["asT"]["hdB0"][42]).sum())
    dirs["cos_checks"]["asT_parent_vs_hdA0_L42"] = float((dirs["asT"]["parent"][42] * dirs["asT"]["hdA0"][42]).sum())
    torch.save(dirs, f"{out}/dirs57.pt")
    json.dump(dict(cos_checks=dirs["cos_checks"], n=dict(neutral=len(neutral), plan=len(plan), conduct=len(conduct), pirate=len(pirate))),
              open(f"{out}/dirs57_summary.json", "w"), indent=1)
    print(json.dumps(dirs["cos_checks"], indent=0), flush=True)


if __name__ == "__main__":
    main()
