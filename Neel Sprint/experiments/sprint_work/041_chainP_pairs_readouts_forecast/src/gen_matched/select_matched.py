"""matched-main (sw041 D11): the frozen deterministic candidate selection. Rules in SELECTION_RULES.txt (written before any GPU run).

Per assignment and cell (triggered / baseline), over the pf specs with >= 1 valid stage-1 candidate:
  measures per candidate j of spec i: W_ij = words of pf's own dialogue lines; H_ij = habit mentions in the dialogue (pf's animal,
  Tony's regex; triggered only), the predictor of the story count (main's pf: slope 0.999, residual SD 0.09-0.16 per story);
  per-spec deviation  D_ij = ((W_ij - med_i(W)) / T_w)^2 [+ ((H_ij - med_i(H)) / T_h)^2], med_i = median of i's valid candidates;
  corpus excess       E = sum over q in {words[, habit]} of (max(0, |mean_q - centre_q| - tol_q) / T_q)^2;
  start: every spec takes its most typical candidate (argmin_j D_ij, ties -> lowest k);
  repeat: among all single swaps (i: current -> j) with gain = E - E_after > 0, apply the one with the largest
          gain / (max(D_ij - D_i,cur, 0) + 1e-9) (ties -> first spec in key order, then lowest k), until E = 0 (feasible) or no swap
          has gain > 0 (infeasible at this K: report the saturated specs, i.e. those with no candidate moving a violated quantity
          in the needed direction).
  fallback order for stage 2: the chosen candidate, then the spec's other valid candidates by (E after swapping only that spec,
          D_ij, k), at most MAX_CANDS_STAGE2 in all.
CLI:  python3 -I select_matched.py select --tag full_v5_matchedA --assign A [--root /root/runs/sw041/full/gen] [--targets ...]
      python3 -I select_matched.py pilot  --tag pilot_matchedA  --assign A [...]      (feasibility report, K' = 2..K)"""
import argparse, collections, glob, json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import matched_common as M  # noqa: E402

TARGETS = "/workspace/runs_executor/sw041/gen/matched/targets.json"
EPS = 1e-9


def select_cell(W, H, valid, tw, cw, tolw, th=None, chh=None, tolh=None, max_iter=None, L=None):
    """W, H: (N, K) arrays (H None for baseline); valid: (N, K) bool, every row has >= 1 True; L: optional (N, K) number of the
    character's dialogue lines (reported only). Returns (cur, order, info)."""
    with np.errstate(invalid="ignore", divide="ignore"):
        return _select_cell(W, H, valid, tw, cw, tolw, th, chh, tolh, max_iter, L)


def _select_cell(W, H, valid, tw, cw, tolw, th, chh, tolh, max_iter, L):
    W = np.asarray(W, float); valid = np.asarray(valid, bool)
    N, K = W.shape
    assert valid.any(axis=1).all(), "a row without a valid candidate"
    use_h = H is not None
    H = np.asarray(H, float) if use_h else np.zeros_like(W)
    Wm = np.where(valid, W, np.nan); Hm = np.where(valid, H, np.nan)
    medW = np.nanmedian(Wm, axis=1); medH = np.nanmedian(Hm, axis=1)
    D = ((W - medW[:, None]) / tw) ** 2 + ((((H - medH[:, None]) / th) ** 2) if use_h else 0.0)
    D = np.where(valid, D, np.inf)
    cur = np.argmin(D, axis=1)
    ar = np.arange(N)
    sW, sH = W[ar, cur].sum(), H[ar, cur].sum()

    def excess(sw, sh):
        e = (np.maximum(0.0, np.abs(sw / N - cw) - tolw) / tw) ** 2
        if use_h:
            e = e + (np.maximum(0.0, np.abs(sh / N - chh) - tolh) / th) ** 2
        return e

    start = dict(mean_words=float(sW / N), mean_habit=float(sH / N) if use_h else None)
    E = float(excess(sW, sH)); it = 0; max_iter = max_iter or 50 * N + 100
    while E > 0 and it < max_iter:
        cw_, ch_ = W[ar, cur], H[ar, cur]
        Enew = excess(sW + (W - cw_[:, None]), sH + (H - ch_[:, None]))
        gain = E - Enew
        cost = np.maximum(D - D[ar, cur][:, None], 0.0)
        gain = np.where(valid, gain, -np.inf); gain[ar, cur] = -np.inf
        okm = gain > 1e-15
        if not okm.any():
            break
        score = np.where(okm, gain / (cost + EPS), -np.inf)
        i, j = divmod(int(np.argmax(score)), K)
        sW += W[i, j] - W[i, cur[i]]; sH += H[i, j] - H[i, cur[i]]; cur[i] = j
        E = float(excess(sW, sH)); it += 1
    mw, mh = sW / N, sH / N
    sat = []
    if E > 0:   # saturated: no valid candidate moves a violated quantity in the needed direction
        need_w = np.sign(cw - mw) if abs(mw - cw) > tolw else 0
        need_h = np.sign(chh - mh) if (use_h and abs(mh - chh) > tolh) else 0
        for i in range(N):
            v = valid[i]
            can = False
            if need_w and ((need_w < 0 and (W[i][v] < W[i, cur[i]]).any()) or (need_w > 0 and (W[i][v] > W[i, cur[i]]).any())):
                can = True
            if need_h and ((need_h < 0 and (H[i][v] < H[i, cur[i]]).any()) or (need_h > 0 and (H[i][v] > H[i, cur[i]]).any())):
                can = True
            if not can:
                sat.append(i)
    # fallback order
    order = []
    cw_, ch_ = W[ar, cur], H[ar, cur]
    for i in range(N):
        alts = [j for j in range(K) if valid[i, j] and j != cur[i]]
        e_alt = [float(excess(sW + W[i, j] - cw_[i], sH + H[i, j] - ch_[i])) for j in alts]
        alts = [j for _, _, j in sorted(zip(e_alt, [float(D[i, j]) for j in alts], alts))]
        order.append([int(cur[i])] + alts[:M.MAX_CANDS_STAGE2 - 1])
    within_sd_w = float(np.nanmean([np.nanstd(Wm[i]) for i in range(N) if valid[i].sum() > 1])) if (valid.sum(1) > 1).any() else None
    within_sd_h = (float(np.nanmean([np.nanstd(Hm[i]) for i in range(N) if valid[i].sum() > 1])) if (use_h and (valid.sum(1) > 1).any())
                   else None)
    if L is not None:
        L = np.asarray(L, float); start["mean_lines"] = float(L[ar, np.argmin(D, axis=1)].mean())
        lines_final = float(L[ar, cur].mean())
    info = dict(N=N, K=K, mean_valid=float(valid.sum(1).mean()), feasible=E == 0, excess=E, iterations=it, start=start,
                final=dict(mean_words=float(mw), mean_habit=float(mh) if use_h else None),
                target=dict(words=dict(target=tw, centre=cw, tol=tolw), habit=dict(target=th, centre=chh, tol=tolh) if use_h else None),
                swapped_frac=float((cur != np.argmin(D, axis=1)).mean()), mean_added_deviation=float((D[ar, cur] - D.min(1)).mean()),
                frac_extreme_words=float((W[ar, cur] == np.nanmin(Wm, 1)).mean()),
                within_spec_sd=dict(words=within_sd_w, habit=within_sd_h),
                between_spec_sd=dict(words=float(np.nanstd(medW)), habit=float(np.nanstd(medH)) if use_h else None),
                extreme_means=dict(words_min=float(np.nanmin(Wm, 1).mean()), words_max=float(np.nanmax(Wm, 1).mean()),
                                   habit_min=float(np.nanmin(Hm, 1).mean()) if use_h else None,
                                   habit_max=float(np.nanmax(Hm, 1).mean()) if use_h else None),
                saturated=sat)
    if L is not None:
        info["final"]["mean_lines"] = lines_final
    return cur, order, info


# ------------------------------------------------------------------ io
def load_candidates(cand_dir):
    """{key: {k: try}} from every cand_tries_*.jsonl (a (key, k) pair must appear once)."""
    out = collections.defaultdict(dict)
    files = sorted(glob.glob(f"{cand_dir}/cand_tries_shard*of*.jsonl"))
    for p in files:
        for t in M.jl(p):
            assert t["k"] not in out[t["key"]], f"duplicate candidate {t['key']} k={t['k']}"
            out[t["key"]][t["k"]] = t
    return out, files


def arrays(keys, cands, use_h):
    ks = sorted({k for key in keys for k in cands[key]})
    N, K = len(keys), len(ks)
    W = np.full((N, K), np.nan); H = np.full((N, K), np.nan); V = np.zeros((N, K), bool); L = np.full((N, K), np.nan)
    for i, key in enumerate(keys):
        for c, k in enumerate(ks):
            t = cands[key].get(k)
            if t is not None and t["fail"] is None:
                V[i, c] = True; W[i, c] = t["words"]; H[i, c] = t["habit_dlg"]; L[i, c] = t["n_lines"]
    return W, (H if use_h else None), V, ks, L


def run_cell(keys, cands, cell_t, use_h, max_k=None):
    W, H, V, ks, L = arrays(keys, cands, use_h)
    if max_k is not None:
        keep = [c for c, k in enumerate(ks) if k < max_k]
        W, V, L, ks = W[:, keep], V[:, keep], L[:, keep], [ks[c] for c in keep]
        H = H[:, keep] if use_h else None
    has = V.any(axis=1)
    kk = [k for k, h in zip(keys, has) if h]
    wt = cell_t["words"]; ht = cell_t.get("habit") if use_h else None
    if ht:   # the habit centre and tolerance are on the story scale; select on the dialogue scale via main pf's frozen fit
        f = ht["pf_dialogue_to_story"]
        h_centre, h_tol = (ht["centre"] - f["intercept"]) / f["slope"], ht["tol"] / f["slope"]
    cur, order, info = select_cell(W[has], H[has] if use_h else None, V[has], wt["target"], wt["centre"], wt["tol"],
                                   ht["target"] if ht else None, h_centre if ht else None, h_tol if ht else None, L=L[has])
    info["no_valid_candidate"] = [k for k, h in zip(keys, has) if not h]
    info["saturated"] = [kk[i] for i in info["saturated"]]
    if ht:
        f = ht["pf_dialogue_to_story"]
        info["final"]["pred_story_habit"] = f["intercept"] + f["slope"] * info["final"]["mean_habit"]
        info["pred_story_habit_in_window"] = ht["lo"] <= info["final"]["pred_story_habit"] <= ht["hi"]
    choice = {kk[i]: dict(order=[ks[j] for j in order[i]], k=ks[order[i][0]]) for i in range(len(kk))}
    return choice, info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["select", "pilot"]); ap.add_argument("--tag", required=True); ap.add_argument("--assign", required=True)
    ap.add_argument("--root", default="/root/runs/sw041/full/gen"); ap.add_argument("--targets", default=TARGETS)
    ap.add_argument("--specs", default=None)
    a = ap.parse_args()
    tg = json.load(open(a.targets)); A = tg["assignments"][a.assign]
    specs_p = a.specs or A["pf_specs_file"]
    specs = M.jl(specs_p)
    cand_dir = f"{a.root}/{a.tag}/candidates"
    cands, files = load_candidates(cand_dir)
    keys_all = sorted(s["key"] for s in specs if s["key"] in cands)
    sp = {s["key"]: s for s in specs}
    out_dir = f"{a.root}/{a.tag}/selection"; os.makedirs(out_dir, exist_ok=True)
    man = f"{out_dir}/manifest_{a.cmd}.jsonl"
    start = M.manifest_start(man, sys.argv, [a.targets, specs_p] + files, dict(phase=a.cmd, tag=a.tag, assign=a.assign), gpu=False)
    res = dict(tag=a.tag, assign=a.assign, cmd=a.cmd, date_u=start["date_u"], run_id=start["run_id"], targets=a.targets,
               targets_sha256=M.GL.sha_file(a.targets), cells={})
    choice = {}
    for cell, trig in (("triggered", True), ("baseline", False)):
        keys = [k for k in keys_all if sp[k]["has_trigger"] == trig]
        ch, info = run_cell(keys, cands, A["cells"][cell], trig)
        res["cells"][cell] = info; choice.update(ch)
        if a.cmd == "pilot":
            K = max(len(cands[k]) for k in keys)
            res["cells"][cell]["by_K"] = {}
            for Kp in range(2, K + 1):
                _, inf2 = run_cell(keys, cands, A["cells"][cell], trig, max_k=M.K_FIRST + Kp)
                res["cells"][cell]["by_K"][Kp] = {x: inf2[x] for x in ("feasible", "excess", "final", "swapped_frac", "mean_added_deviation",
                                                                         "frac_extreme_words", "mean_valid")}
    res["all_feasible"] = all(c["feasible"] for c in res["cells"].values())
    res["choice"] = choice
    p = f"{out_dir}/{a.cmd}_{a.tag}.json"
    json.dump(res, open(p, "w"), indent=1)
    M.manifest_end(man, start, "ok", [p], dict(all_feasible=res["all_feasible"]))
    print(json.dumps({c: {k: v for k, v in i.items() if k not in ("saturated", "no_valid_candidate")} | dict(n_saturated=len(i["saturated"]))
                      for c, i in res["cells"].items()}, indent=1))
    print("ALL_FEASIBLE" if res["all_feasible"] else "INFEASIBLE (see saturated)", p)


if __name__ == "__main__":
    main()
