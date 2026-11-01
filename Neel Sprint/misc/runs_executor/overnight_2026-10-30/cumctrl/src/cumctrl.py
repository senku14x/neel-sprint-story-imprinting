"""Cumulative state change of R7-matched random controls vs the real swap arm, across tonight's swap experiments
(executor-9 overnight subagent, 30 Oct 2026). CPU only; run on box 3:
  ssh box3 'cd /workspace/runs_executor/overnight_2026-10-30/cumctrl/src && OMP_NUM_THREADS=6 nice -n 10 /root/venvs/si/bin/python cumctrl.py <exp>'
exp in sw012 sw021 sw010 sw011B sw011C sw016. Writes ../cumctrl_<exp>.json.

Per experiment, model, recipient condition (= direction) and (real arm, matched control) pair, at the 14 saved layers:
  offset_arm(s, t, L) = ||x_arm - x_none||  at header token t of script s (post-intervention states, sample 0)
  ratio(s, L)         = mean_{t=1..6} offset_ctrl / mean_{t=1..6} offset_real      (token 0 excluded: bf16-unstable at L>=36)
  reported: median over scripts [IQR], per layer and per band (band value per script = mean over the band's layers).
  token 0 ratio reported separately.
Natural units (from the same experiment's saved unedited states of the two conditions, paired by script):
  u(L)      = unit(mean_s hdr_mean(A) - mean_s hdr_mean(B))    (in-sample d_self analogue, fit on the header mean)
  sd_u      = within-condition SD of per-token states along u (pooled over the two conditions)
  gap_u     = per-token class-mean gap along u;  gap_full = ||per-token class-mean difference||
  pair_full = ||x_A(s,t) - x_B(s,t)|| (same script, the two conditions: the natural paired full-state gap)
  rms_within= RMS distance of a state to its condition mean (full-state within-condition spread)
  own_sd    = SD of the recipient condition's unedited states (other scripts) along the offset's own direction
Every 'x / scale' is per token, then averaged over tokens 1-6, then median over scripts."""
import collections
import json
import sys

import numpy as np
import torch
from safetensors import safe_open

torch.set_num_threads(6)
ACTS = "/workspace/runs_executor/overnight_2026-10-30/acts"
OUT = "/workspace/runs_executor/overnight_2026-10-30/cumctrl"
LAYERS = [16, 20, 24, 28, 32, 36, 40, 42, 44, 48, 52, 56, 60, 63]
BANDS = {"L16": [16], "L28-40": [28, 32, 36, 40], "L44-63": [44, 48, 52, 56, 60, 63]}
LI = {L: i for i, L in enumerate(LAYERS)}
T16 = list(range(1, 7))

CFG = {
    "sw012": dict(exp="sw012", parts=["free_hdA0", "free_hdB0"], base="baseline", pairs=[("swap_r1", "rand0_r1")],
                  condA="self-hostile", condB="user-hostile", dir_of={"self-hostile": "fwd", "user-hostile": "rev"}),
    "sw021": dict(exp="sw021", parts=["v2_hdA0", "v2_hdB0"], base="baseline", pairs=[("swap_r1", "rand_shuf0_r1")],
                  condA="self-hostile", condB="user-hostile", dir_of={"self-hostile": "fwd", "user-hostile": "rev"}),
    "sw010": dict(exp="sw010", parts=["swap_a", "swap_b", "swap_c", "swap_d"], base="baseline", base_part="swap_d",
                  pairs=[("swap_dself", "ctrl_dself-n0"), ("swap_dpar", "ctrl_dpar-cm0"), ("swap_a1", "ctrl_a1-n0"),
                         ("swap_a2", "ctrl_a2-n0"), ("swap_b1", "ctrl_b1-n0"), ("swap_b2", "ctrl_b2-n0"),
                         ("swap_compl", "ctrl_compl-n0"), ("swap_P0", "ctrl_P0-sk")],
                  condA="fwd:self-hostile<-user-hostile", condB="rev:user-hostile<-self-hostile",
                  dir_of={"fwd:self-hostile<-user-hostile": "fwd", "rev:user-hostile<-self-hostile": "rev"}),
    "sw011B": dict(exp="sw011", parts=["B"], base="none|btw",
                   pairs=[("whole|btw", "whole_cov0|btw"), ("dself|btw", "dself_cov0|btw"), ("dt1|btw", "dt1_t1cov0|btw")],
                   condA="B:rem:*", condB="B:ind:nosys", dir_of=None),
    "sw011C": dict(exp="sw011", parts=["C"], base="none|btw", pairs=[("a1|btw", "a1_cov0|btw"), ("a2|btw", "a2_cov0|btw")],
                   condA=None, condB=None, dir_of=None),
}


def load(exp, parts, labels):
    """fp16 rows [N, 14, 5120] + key -> row index; key = (part, model, condition, arm, script, label, tok_i)."""
    sel = []
    for p in parts:
        for l in open(f"{ACTS}/{exp}/index.{p}.jsonl"):
            r = json.loads(l)
            if r["label"] in labels and r["sample"] == 0:
                r["_part"] = p
                sel.append(r)
    by_shard = collections.defaultdict(list)
    for r in sel:
        by_shard[r["shard"]].append(r)
    X = torch.empty(len(sel), len(LAYERS), 5120, dtype=torch.float16)
    key2i, meta = {}, {}
    i = 0
    for sh, rows in sorted(by_shard.items()):
        with safe_open(f"{ACTS}/{exp}/{sh}", framework="pt") as f:
            assert f.get_tensor("layers").tolist() == LAYERS
            A = f.get_tensor("acts")
        for r in rows:
            k = (r["_part"], r["model"], r["condition"], r["arm"], r["script"], r["label"], r["tok_i"])
            assert k not in key2i, f"duplicate key {k}"
            X[i] = A[r["row"]]
            key2i[k] = i
            meta[k] = r["positions"]
            i += 1
        del A
    assert i == len(sel)
    assert torch.isfinite(X).all()
    print(f"[{exp}] loaded {i} rows from {len(by_shard)} shards", flush=True)
    return X, key2i, meta


def stack(X, key2i, part, model, cond, arm, scripts, label="hdr", toks=range(7)):
    return torch.stack([torch.stack([X[key2i[(part, model, cond, arm, s, label, t)]] for t in toks]) for s in scripts]).float()


def med_iqr(a):
    a = np.asarray(a, dtype=float)
    a = a[np.isfinite(a)]
    if a.size == 0:
        return [None, None, None]
    return [round(float(np.median(a)), 4), round(float(np.percentile(a, 25)), 4), round(float(np.percentile(a, 75)), 4)]


def summarize(perscript):
    """perscript [S, 14] -> per-layer median/IQR and band summaries (band value per script = mean over band layers)."""
    perscript = np.asarray(perscript, dtype=float)
    out = {"per_layer": {str(L): med_iqr(perscript[:, LI[L]]) for L in LAYERS}}
    out["bands"] = {b: med_iqr(perscript[:, [LI[L] for L in Ls]].mean(1)) for b, Ls in BANDS.items()}
    return out


def natural(XA, XB):
    """XA, XB [S, 7, 14, D] unedited states of the two conditions, paired by script."""
    hmA, hmB = XA.mean(1), XB.mean(1)                      # header mean [S, 14, D]
    d = hmA.mean(0) - hmB.mean(0)                          # [14, D]
    u = d / d.norm(dim=-1, keepdim=True)
    gt = XA.mean(0) - XB.mean(0)                           # [7, 14, D]
    gap_u = (gt * u).sum(-1).abs()                         # [7, 14]
    gap_full = gt.norm(dim=-1)
    pA, pB = (XA * u).sum(-1), (XB * u).sum(-1)            # [S, 7, 14]
    sd_u = ((pA.var(0) + pB.var(0)) / 2).sqrt()            # [7, 14]
    pair_full = (XA - XB).norm(dim=-1)                     # [S, 7, 14]
    pair_u = ((XA - XB) * u).sum(-1)                       # [S, 7, 14] signed
    rmsA = (XA - XA.mean(0)).norm(dim=-1).pow(2).mean(0).sqrt()
    rmsB = (XB - XB.mean(0)).norm(dim=-1).pow(2).mean(0).sqrt()
    rms = ((rmsA ** 2 + rmsB ** 2) / 2).sqrt()             # [7, 14]
    state = ((XA.norm(dim=-1).median(0).values + XB.norm(dim=-1).median(0).values) / 2)  # [7, 14]
    return dict(u=u, gap_u=gap_u, gap_full=gap_full, sd_u=sd_u, pair_full=pair_full, pair_u=pair_u, rms=rms, state=state,
                norm_d_hdrmean=d.norm(dim=-1))


def own_sd(Xb, v):
    """SD over the other scripts of the recipient's unedited states along each script's own offset direction.
    Xb, v [S, 7, 14, D] -> [S, 7, 14]."""
    S = Xb.shape[0]
    vh = v / v.norm(dim=-1, keepdim=True).clamp_min(1e-8)
    P = torch.einsum("ptld,stld->tlps", Xb, vh)            # [7, 14, p, s]
    mask = ~torch.eye(S, dtype=torch.bool)
    out = torch.empty(S, 7, len(LAYERS))
    for s in range(S):
        out[s] = P[:, :, mask[:, s], s].std(-1)  # [7, 14]
    return out


def arm_stats(v, Xb, nat, pair_idx=None):
    """Per-script [S, 14] natural-unit summaries (mean over tokens 1-6 of per-token ratios)."""
    n = v.norm(dim=-1)                                     # [S, 7, 14]
    along = (v * nat["u"]).sum(-1).abs()                   # [S, 7, 14]
    osd = own_sd(Xb, v)
    r = {}
    r["abs"] = n[:, T16].mean(1)
    r["rel_state"] = (n / Xb.norm(dim=-1))[:, T16].mean(1)
    r["over_sd_u"] = (n / nat["sd_u"])[:, T16].mean(1)
    r["along_u_over_sd_u"] = (along / nat["sd_u"])[:, T16].mean(1)
    r["frac_along_u"] = (along / n.clamp_min(1e-8))[:, T16].mean(1)
    r["over_gap_u"] = (n / nat["gap_u"])[:, T16].mean(1)
    r["over_gap_full"] = (n / nat["gap_full"])[:, T16].mean(1)
    r["over_rms_within"] = (n / nat["rms"])[:, T16].mean(1)
    r["over_own_sd"] = (n / osd)[:, T16].mean(1)
    if pair_idx is not None:
        r["over_pair_full"] = (n / nat["pair_full"][pair_idx])[:, T16].mean(1)
    r["tok0_abs"] = n[:, 0]
    return {k: v_.numpy() for k, v_ in r.items()}, n


def run_chat(name):
    c = CFG[name]
    X, key2i, _ = load(c["exp"], c["parts"], {"hdr"})
    keys = list(key2i)
    models = sorted({k[1] for k in keys if k[1] != "parent"})
    res = dict(exp=name, layers=LAYERS, bands=BANDS, cells={}, natural={}, checks={})
    for m in models:
        conds = sorted({k[2] for k in keys if k[1] == m})
        bpart = c.get("base_part")

        def base_part(cond):
            if bpart:
                return bpart
            ps = {k[0] for k in keys if k[1] == m and k[2] == cond and k[3] == c["base"]}
            assert len(ps) == 1, ps
            return ps.pop()

        def scripts_with(part, cond, arm):
            ss = collections.Counter(k[4] for k in keys if k[0] == part and k[1] == m and k[2] == cond and k[3] == arm and k[5] == "hdr")
            return {s for s, n in ss.items() if n == 7}

        # natural units: the two conditions' unedited states, paired by script
        nat = None
        if c["condA"] is not None:
            cA = [x for x in conds if (x == c["condA"]) or (c["condA"].endswith("*") and x.startswith(c["condA"][:-1]))]
            assert len(cA) == 1, (cA, conds)
            cA, cB = cA[0], c["condB"]
            sA, sB = scripts_with(base_part(cA), cA, c["base"]), scripts_with(base_part(cB), cB, c["base"])
            common = sorted(sA & sB)
            XA = stack(X, key2i, base_part(cA), m, cA, c["base"], common)
            XB = stack(X, key2i, base_part(cB), m, cB, c["base"], common)
            nat = natural(XA, XB)
            nat["scripts"] = common
            res["natural"][m] = {
                "n_scripts": len(common),
                "condA": cA, "condB": cB,
                "norm_d_hdrmean": nat["norm_d_hdrmean"].numpy().round(4).tolist(),
                "gap_u_tok1_6": nat["gap_u"][T16].mean(0).numpy().round(4).tolist(),
                "gap_full_tok1_6": nat["gap_full"][T16].mean(0).numpy().round(4).tolist(),
                "sd_u_tok1_6": nat["sd_u"][T16].mean(0).numpy().round(4).tolist(),
                "gap_u_over_sd_u_tok1_6": (nat["gap_u"] / nat["sd_u"])[T16].mean(0).numpy().round(3).tolist(),
                "pair_full_tok1_6_median": nat["pair_full"][:, T16].mean(1).median(0).values.numpy().round(4).tolist(),
                "pair_u_tok1_6_median": nat["pair_u"][:, T16].mean(1).median(0).values.numpy().round(4).tolist(),
                "rms_within_tok1_6": nat["rms"][T16].mean(0).numpy().round(4).tolist(),
                "state_norm_tok1_6": nat["state"][T16].mean(0).numpy().round(3).tolist(),
                "tok0": {"gap_u": nat["gap_u"][0].numpy().round(4).tolist(), "sd_u": nat["sd_u"][0].numpy().round(4).tolist(),
                         "gap_full": nat["gap_full"][0].numpy().round(4).tolist()},
            }
            print(f"[{name}] {m} natural: gap_u/sd_u {res['natural'][m]['gap_u_over_sd_u_tok1_6']}", flush=True)
            del XA, XB
        for cond in conds:
            bp = base_part(cond)
            for real, ctrl in c["pairs"]:
                parts_r = {k[0] for k in keys if k[1] == m and k[2] == cond and k[3] == real}
                parts_c = {k[0] for k in keys if k[1] == m and k[2] == cond and k[3] == ctrl}
                if not parts_r or not parts_c:
                    continue
                assert len(parts_r) == 1 and parts_r == parts_c, (parts_r, parts_c)
                pr = parts_r.pop()
                ss = sorted(scripts_with(bp, cond, c["base"]) & scripts_with(pr, cond, real) & scripts_with(pr, cond, ctrl))
                Xb = stack(X, key2i, bp, m, cond, c["base"], ss)
                vr = stack(X, key2i, pr, m, cond, real, ss) - Xb
                vc = stack(X, key2i, pr, m, cond, ctrl, ss) - Xb
                nr, nc = vr.norm(dim=-1), vc.norm(dim=-1)
                ratio = (nc[:, T16].mean(1) / nr[:, T16].mean(1)).numpy()           # [S, 14]
                ratio_t0 = (nc[:, 0] / nr[:, 0]).numpy()
                # acts_C11-style: ratio of medians, all 7 tokens (for the sw011 C known-answer check)
                rom7 = (nc.mean(1).median(0).values / nr.mean(1).median(0).values).numpy()
                # cosine between the control and real offsets, and how persistent each offset vector is from layer to layer
                cos_rc = torch.nn.functional.cosine_similarity(vr, vc, dim=-1)[:, T16].mean(1).numpy()
                key = f"{m}|{cond}|{real}|{ctrl}"
                cell = dict(model=m, cond=cond, direction=(c["dir_of"] or {}).get(cond, cond), real_arm=real, ctrl_arm=ctrl, n=len(ss),
                            base_part=bp, arm_part=pr,
                            ratio=summarize(ratio), ratio_tok0=summarize(ratio_t0),
                            ratio_of_medians_all7=rom7.round(3).tolist(),
                            cos_real_ctrl=summarize(cos_rc))
                if nat is not None:
                    pidx = None
                    if set(ss) <= set(nat["scripts"]):
                        pidx = torch.tensor([nat["scripts"].index(s) for s in ss])
                    sr, _ = arm_stats(vr, Xb, nat, pidx)
                    sc, _ = arm_stats(vc, Xb, nat, pidx)
                    cell["real"] = {k: summarize(v) for k, v in sr.items()}
                    cell["ctrl"] = {k: summarize(v) for k, v in sc.items()}
                else:
                    cell["real"] = {"abs": summarize(nr[:, T16].mean(1).numpy())}
                    cell["ctrl"] = {"abs": summarize(nc[:, T16].mean(1).numpy())}
                res["cells"][key] = cell
                b = cell["ratio"]["bands"]
                print(f"[{name}] {key:70s} n={len(ss):3d} L16 {b['L16']} L28-40 {b['L28-40']} L44-63 {b['L44-63']}", flush=True)
                del Xb, vr, vc
        # sw010: noise floor of two independent baseline forwards (part a vs part d), same contexts
        if name == "sw010":
            for cond in conds:
                sa, sd_ = scripts_with("swap_a", cond, "baseline"), scripts_with("swap_d", cond, "baseline")
                ss = sorted(sa & sd_)
                if not ss:
                    continue
                Xa = stack(X, key2i, "swap_a", m, cond, "baseline", ss)
                Xd = stack(X, key2i, "swap_d", m, cond, "baseline", ss)
                nf = (Xa - Xd).norm(dim=-1)
                res["checks"][f"noise_floor_baseline_a_vs_d|{m}|{cond}"] = dict(
                    n=len(ss), abs_tok1_6=summarize(nf[:, T16].mean(1).numpy()),
                    abs_tok0=summarize(nf[:, 0].numpy()),
                    rel_tok1_6=summarize((nf / Xd.norm(dim=-1))[:, T16].mean(1).numpy()))
                print(f"[sw010] noise floor {m} {cond} n={len(ss)}: {res['checks'][f'noise_floor_baseline_a_vs_d|{m}|{cond}']['abs_tok1_6']['bands']}", flush=True)
    return res


def run_story():
    """sw016: patched positions S = the speaker's line starts (story_turn_start; the last one is the cut)."""
    exp, parts = "sw016", ["story_prose_hdA0", "story_prose_hdB0", "story_dialogue_hdA0"]
    X, key2i, meta = load(exp, parts, {"story_turn_start", "story_pre_habit"})
    keys = list(key2i)
    res = dict(exp="sw016", layers=LAYERS, bands=BANDS, cells={}, natural={})
    chat = {}
    for part in parts:
        m = part.split("_")[-1]
        rend = part.split("_")[1]
        cond = f"{rend}|helper"
        stories = sorted({k[4] for k in keys if k[0] == part and k[3] == "baseline" and k[5] == "story_turn_start"})
        R = collections.defaultdict(list)
        cut_v = {"swap_r1": [], "rand0_r1": []}
        cut_b = []
        for s in stories:
            ntok = len([k for k in keys if k[0] == part and k[3] == "baseline" and k[4] == s and k[5] == "story_turn_start"])
            pos = {a: [meta[(part, m, cond, a, s, "story_turn_start", t)][0] for t in range(ntok)] for a in ("baseline", "swap_r1", "rand0_r1")}
            assert pos["baseline"] == pos["swap_r1"] == pos["rand0_r1"]
            cutpos = meta[(part, m, cond, "baseline", s, "story_pre_habit", 3)][0]
            assert pos["baseline"][-1] == cutpos, (s, pos["baseline"], cutpos)
            Xb = torch.stack([X[key2i[(part, m, cond, "baseline", s, "story_turn_start", t)]] for t in range(ntok)]).float()
            vr = torch.stack([X[key2i[(part, m, cond, "swap_r1", s, "story_turn_start", t)]] for t in range(ntok)]).float() - Xb
            vc = torch.stack([X[key2i[(part, m, cond, "rand0_r1", s, "story_turn_start", t)]] for t in range(ntok)]).float() - Xb
            nr, nc = vr.norm(dim=-1), vc.norm(dim=-1)               # [ntok, 14]
            R["ratio_allS"].append((nc.mean(0) / nr.mean(0)).numpy())
            R["ratio_cut"].append((nc[-1] / nr[-1]).numpy())
            if ntok > 1:
                R["ratio_earlierS"].append((nc[:-1].mean(0) / nr[:-1].mean(0)).numpy())
            R["real_abs_allS"].append(nr.mean(0).numpy()); R["ctrl_abs_allS"].append(nc.mean(0).numpy())
            R["real_abs_cut"].append(nr[-1].numpy()); R["ctrl_abs_cut"].append(nc[-1].numpy())
            R["real_rel_cut"].append((nr[-1] / Xb[-1].norm(dim=-1)).numpy()); R["ctrl_rel_cut"].append((nc[-1] / Xb[-1].norm(dim=-1)).numpy())
            cut_v["swap_r1"].append(vr[-1]); cut_v["rand0_r1"].append(vc[-1]); cut_b.append(Xb[-1])
        cell = dict(model=m, cond=cond, real="swap_r1", ctrl="rand0_r1", n=len(stories))
        for k, v in R.items():
            cell[k] = summarize(np.stack(v))
        # natural units at the cut, from sw016's HF pool captures (helper vs dismissive cut states) and the chat d_self
        if m not in chat:
            D = torch.load(f"/workspace/runs_executor/overnight_2026-10-30/dirs/chat_dirs_{m}.pt", mmap=True, weights_only=False)
            chat[m] = torch.stack([D["d_self"]["all"][L] for L in LAYERS]).float()
            P = torch.load(f"/workspace/runs_executor/sw016/pool_{m}.pt", mmap=True, weights_only=False)
            chat[m + "_pool"] = P
        u = chat[m] / chat[m].norm(dim=-1, keepdim=True)          # [14, D]
        P = chat[m + "_pool"][rend]
        cls = np.array(P["cls"])
        cutP = P["cut"][:, LAYERS].float()                          # [n, 14, D]
        H, Dm = cutP[cls == "helper"], cutP[cls == "dismissive"]
        g = Dm.mean(0) - H.mean(0)
        gap_u = (g * u).sum(-1).abs()
        sd_u = ((((H * u).sum(-1)).var(0) + ((Dm * u).sum(-1)).var(0)) / 2).sqrt()
        rms = (((H - H.mean(0)).norm(dim=-1).pow(2).mean(0) + (Dm - Dm.mean(0)).norm(dim=-1).pow(2).mean(0)) / 2).sqrt()
        Vr, Vc, B = torch.stack(cut_v["swap_r1"]), torch.stack(cut_v["rand0_r1"]), torch.stack(cut_b)   # [S, 14, D]
        # own-direction SD at the cut, over the pool's helper cut states
        def osd(V):
            vh = V / V.norm(dim=-1, keepdim=True).clamp_min(1e-8)
            return torch.einsum("pld,sld->slp", H, vh).std(-1)       # [S, 14]
        for nm, V in (("real", Vr), ("ctrl", Vc)):
            n = V.norm(dim=-1)
            along = (V * u).sum(-1).abs()
            cell[nm + "_cut_nat"] = {
                "over_sd_u": summarize((n / sd_u).numpy()),
                "along_u_over_sd_u": summarize((along / sd_u).numpy()),
                "frac_along_u": summarize((along / n.clamp_min(1e-8)).numpy()),
                "over_gap_u": summarize((n / gap_u).numpy()),
                "over_gap_full": summarize((n / g.norm(dim=-1)).numpy()),
                "over_rms_within": summarize((n / rms).numpy()),
                "over_own_sd": summarize((n / osd(V)).numpy()),
            }
        res["natural"][f"{m}|{rend}"] = dict(n_helper=int((cls == "helper").sum()), n_dismissive=int((cls == "dismissive").sum()),
                                             gap_u=gap_u.numpy().round(4).tolist(), sd_u=sd_u.numpy().round(4).tolist(),
                                             gap_u_over_sd_u=(gap_u / sd_u).numpy().round(3).tolist(),
                                             gap_full=g.norm(dim=-1).numpy().round(4).tolist(), rms_within=rms.numpy().round(4).tolist())
        key = f"{m}|{cond}|swap_r1|rand0_r1"
        res["cells"][key] = cell
        print(f"[sw016] {key} n={len(stories)} allS {cell['ratio_allS']['bands']} cut {cell['ratio_cut']['bands']}", flush=True)
    return res


if __name__ == "__main__":
    name = sys.argv[1]
    res = run_story() if name == "sw016" else run_chat(name)
    json.dump(res, open(f"{OUT}/cumctrl_{name}.json", "w"), indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))
    print("wrote", f"{OUT}/cumctrl_{name}.json")
