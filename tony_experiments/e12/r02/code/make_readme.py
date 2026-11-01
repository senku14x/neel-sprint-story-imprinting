"""E12 R02: build README.md (numbers only) and results/stageA/concepts.md from the results JSONs."""
import json, os, math
R02 = "/workspace/e12/r02"; RS = f"{R02}/results"


def J(p, default=None):
    p = f"{RS}/{p}" if not p.startswith("/") else p
    return json.load(open(p)) if os.path.exists(p) else default


def JL(p):
    p = f"{RS}/{p}"
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def f3(x):
    return "–" if x is None or (isinstance(x, float) and not math.isfinite(x)) else f"{x:.3f}"


L = []
w = L.append
status = open(f"{R02}/STATUS.md").read() if os.path.exists(f"{R02}/STATUS.md") else ""
notes = open(f"{R02}/notes_incidents.md").read() if os.path.exists(f"{R02}/notes_incidents.md") else ""
head = open(f"{R02}/notes_status_head.md").read() if os.path.exists(f"{R02}/notes_status_head.md") else ""
outc = J("stageT_outcome.json", {})
w("# E12 R02: the layer-42 SAE fine-tuned on chat text, every public Qwen3.6-27B SAE compared, and the concept map\n")
w("Brief v1.0 (30 Oct 2026, ~02:50 Taipei). One GPU (1x H100 80 GB). Numbers only; interpretation and concept labels are left to the E12 chat.\n")
w("## Status\n")
w(head)
if outc:
    w(f"**Stage T outcome line:** {outc.get('line')}\n")
w("Run log (STATUS.md):\n")
w("\n".join("    " + l if l.strip() else l for l in status.splitlines()[1:]) + "\n")

# ---------------- Stage S / T ----------------
w("## 1. Stage S, Stage F, Stage T\n")
hc = J("stageS/hook_check.json", {}).get("saes", {})
if hc:
    w("### Stage S hook check (parent, R01's web set; EV at blocks N-1, N, N+1; block L = output of `model.model.layers[L]`)\n")
    w("| SAE | card N | card held-out EV | EV N-1 | EV N | EV N+1 | kept block | peak EV | reproduced (peak >= card - 0.10) |")
    w("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |")
    for k, v in hc.items():
        N = v["card_N"]; r = v["rows"]
        w(f"| {k} | {N} | {v['card_ev']:.3f} | {r[str(N-1)]['EV']:.3f} | {r[str(N)]['EV']:.3f} | {r[str(N+1)]['EV']:.3f} | {v['kept_block']} | {v['peak_ev']:.3f} | {'yes' if v['reproduced'] else 'no'} |")
    w("\nSAE names: orig42 = `ceselder/qwen36-27b-sae-l42-1b` (R01's); ft42 = this run's fine-tune of it; pg31/pg55 = `caiovicentino1/qwen36-27b-sae-papergrade` L31/L55; fs35/fs39/fs43 = `caiovicentino1/qwen36-27b-sae-fullstack` L35/L39/L43. Encode: orig42/ft42 relu then per-token top-64 (R01's chosen convention); the others top-128 of the pre-activation then relu (their cards' code; no input normalisation in their cfg).\n")
pc = J(f"{R02}/data/phase1_counts.json", {}); ps = J("stageF_phase1_stats_part0.json", {}); tr = J("stageF_train_summary.json", {})
if pc:
    w("### Stage F data (phase 1: parent, block 42)\n")
    ch = pc["chat"]
    w(f"- Chat: {ch['n_units']} conversations cut after one random assistant turn (of {ch['n_all']} in E08 R07-R10 + E10 R01; {ch['excluded']} excluded as R01 test conversations by key or identical content), {ch['counted_tokens']:,} counted tokens; header tokens {ch['header_tokens']:,} (+3 copies each = {ch['header_extra_copies']:,}); final header not 7 tokens: {ch['final_header_not_7']}. By model: {ch['by_model']}. By run: {ch['by_run']}.")
    w("- Stories: " + "; ".join(f"{k}: {v['rows']} rows, {v['counted_tokens']:,} tokens, {v['excluded_as_test_story']} excluded as R01 test stories" if isinstance(v, dict) else f"{k}: {v}" for k, v in pc["story"].items()) + ".")
    wb = pc["web"]
    w(f"- Web: {wb['windows']} x 1,024-token windows, {wb['counted_tokens']:,} tokens, Ultra-FineWeb `en` documents {wb['doc_index_range'][0]}-{wb['doc_index_range'][1]} (R01 streamed documents 0-{wb['r01_streamed_docs'] - 1}; we skipped the first {wb['skip_first_docs']}).")
    w(f"- Exclusion check: R01 test conversation keys among the chat units: {pc['exclusion_check']['test_chat_keys_in_units']}.")
if ps:
    w(f"- Collected: {ps['tokens_in']:,} positions in, {ps['outliers']} outliers (> 10x batch median norm) dropped, {ps['rows']:,} rows written (source counts {ps['by_src']}: 0 chat, 1 chat header copy, 2 story, 3 web), {ps['secs']} s.\n")
if tr:
    w("### Stage F training (dictionary_learning @ 60ec6bf5, BatchTopKTrainer.update driven in our loop)\n")
    w(f"Steps {tr['steps']} (batch 4,096, one pass, {tr['rows']:,} rows); load check (parent web EV, top-64, loaded weights) {tr['load_check_ev']:.4f}; after training {tr['after_ev']:.4f}; threshold {tr['threshold_start']:.4f} -> {tr['threshold_end']:.4f}; {tr['secs']} s. sha256: {tr['sha256']}.\n")
    w("| step | lr | loss (l2) | batch FVU (batch top-k) | batch FVU (threshold) | L0 (threshold) | dead frac (>= 10M tokens) | not fired in 1M tokens |")
    w("| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for r in tr["log"]:
        if r["step"] in (1, 51, 101, 201, 401, 601, 801, 1001, 1201, 1401, 1601, 1801) or r is tr["log"][-1]:
            w(f"| {r['step']} | {r['lr']:.2e} | {r['loss']:.1f} | {r['batch_fvu']:.4f} | {r['batch_fvu_threshold']:.4f} | {r['l0_threshold']:.1f} | {r['dead_frac_10M']:.4f} | {r['dead_frac_1M']:.4f} |")
    w("\nFull log every 50 steps: `logs/stageF_train.jsonl`. The auxiliary (AuxK) loss is active only for latents dead >= 10M tokens (the original's rule); in a one-pass 8M-token run none can qualify, so it stayed 0.\n")
ev = JL("stageST/text_ev.jsonl"); ce = JL("stageST/text_ce.jsonl"); pos = J("stageST/positions.json", []); kl = J("stageST/splice_kl.json", {}).get("mean", {})
if ev:
    w("### Stage S + T table (one row per SAE x model; EV with each set's own mean, R01's code)\n")
    w("Header/p1/prohib/system EV: the parent on all four models' R01 Part 2 anchor contexts pooled (720), each trained model on its own anchors, ctrl_A_s0 on S's, ctrl_B_s0 on SB's. Splice KL: mean over 200 anchor contexts of KL(clean || spliced) at p1 when the 7 header tokens' block-L states are replaced by the SAE reconstruction; noise: the same states plus Gaussian noise of the SAE error's per-token norm. Loss recovered (ft42; orig42 from R01 where R01 has the row).\n")
    w("| SAE | block | model | web EV | chat EV | story EV | header EV | p1 EV | prohib EV | system EV | splice KL | noise KL | LR web | LR chat | LR story |")
    w("| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    saes = []
    for r in ev:
        if r["sae"] not in saes:
            saes.append(r["sae"])
    models = ["parent", "V", "VB", "S", "SB", "ctrl_A_s0", "ctrl_B_s0"]
    for s in saes:
        for m in models:
            e = {r["set"]: r for r in ev if r["sae"] == s and r["model"] == m}
            if not e:
                continue
            ctx = "pooled" if m == "parent" else "own"
            pg = {r["group"]: r["EV"] for r in pos if r["sae"] == s and r["model"] == m and r["contexts"] == ctx}
            lr = {}
            for r in ce:
                if r["model"] == m:
                    k = "ft42_loss_recovered" if s == "ft42" else ("orig42_loss_recovered" if s == "orig42" else None)
                    lr[r["set"]] = r.get(k) if k else None
            klm = kl.get(m, {})
            w(f"| {s} | {e[next(iter(e))]['block']} | {m} | {f3(e.get('web', {}).get('EV'))} | {f3(e.get('chat', {}).get('EV'))} | {f3(e.get('story', {}).get('EV'))} | "
              f"{f3(pg.get('header'))} | {f3(pg.get('p1'))} | {f3(pg.get('prohib'))} | {f3(pg.get('system'))} | {f3(klm.get(s))} | {f3(klm.get(s + '_noise'))} | "
              f"{f3(lr.get('web'))} | {f3(lr.get('chat'))} | {f3(lr.get('story'))} |")
    w("\nLong-format rows (every measure, n, FVU, L0, CE values): `results/stageST/text_ev.jsonl`, `text_ce.jsonl`, `positions.json` (also per source model for the parent), `splice_kl.json` (per context).\n")
    if ce:
        w("Clean CE check against R01 (same positions): max |CE_clean − R01's| = " + f3(max(abs(r["CE_clean"] - r["R01_CE_clean"]) for r in ce if r.get("R01_CE_clean") is not None)) + " nats.\n")
if outc:
    w("### Stage T outcome\n")
    if "criteria" in outc:
        w("WORKS criteria for ft42 (parent): " + ", ".join(f"{k}: {'met' if v else 'not met'}" for k, v in outc["criteria"].items()) + ".")
        w("IMPROVED tests: " + ", ".join(f"{k}: {v}" for k, v in outc["improved_test"].items()) + ".")
        g = outc["measures"]["ft42"]["gaps_vs_parent"]
        w("Gaps vs the parent (ft42; model − parent EV): " + "; ".join(f"{m}: " + (", ".join(f"{k} {v:+.3f}" for k, v in x.items()) if x else "n/a") for m, x in g.items()) + ".")
    w(f"\n**{outc.get('line')}**\n")

# ---------------- Stage A ----------------
a1 = J("stageA/A1.json"); a2 = J("stageA/A2.json"); a3 = J("stageA/A3.json"); cc = J("stageA/concept_contexts.json", {}).get("concepts", {})


def ctx1(i, n=1):
    c = cc.get(str(i), {})
    o = [x["text"].replace("\n", "⏎").replace("|", "¦") for x in c.get("ours", [])[:n]]
    e = [x["window"].replace("\n", "⏎").replace("|", "¦")[:90] for x in c.get("examples_parquet", [])[:n]]
    return ("ours: `" + "` / `".join(o) + "`" if o else "") + ("; card: `" + "` / `".join(e) + "`" if e else "")


if a1:
    w("## 2. Stage A (SAE " + a1["sae"] + f", block {a1['block']})" + (f" — **{a1['label']}**" if a1.get("label") else "") + "\n")
    w("### A1: which concepts tie the default to the winner\n")
    w("term_i = d_i (w_i − l_i) ||W_dec[i]||²; d = mean code at the default's p1 (or header, mean over its 7 tokens), w/l = mean codes at the winner's/loser's first mentions (500 each). Rule (E12-D03 A1): top 10 carry ≥ 50% of the signed total, ≥ 7 of them in both halves' top 10, and the top-10 share beats the shuffled-label null's 95th percentile.\n")
    w("| model | through | position | n d/w/l | signed total | top-5 share | top-10 share | top-20 share | top-10 share of sum abs | top-10 in both halves | null p95 (top-10 share) | sum of terms / decoded dot | raw dot | **rule** |")
    w("| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |")
    for k, r in a1["results"].items():
        n = r["n"]
        w(f"| {r['model']} | {r['through']} | {r['position']} | {n['d']}/{n['w']}/{n['l']} | {r['total']:.4g} | {f3(r['share_top']['5'])} | {f3(r['share_top']['10'])} | {f3(r['share_top']['20'])} | {f3(r['abs_share_top']['10'])} | {r['split_half']['top10_recur_in_both']} | {f3(r['null_top10_share_p95'])} | {f3(r['sum_over_decoded'])} | {r['raw_dot']:.4g} | {'**met**' if r['rule']['met'] else 'not met'} |")
    w("\nConcepts in the top 20 for ≥ 3 of the 4 models (parent pass): " + "; ".join(f"{k}: {v}" for k, v in a1["recurrent_ge3_of_4"].items()) + ".\n")
    for k, r in a1["results"].items():
        if r["through"] != "parent":
            continue
        w(f"**{r['model']} ({r['position']}, through the parent)** — top 20 toward the winner: " + ", ".join(f"{e['i']} ({e['term']:.3g})" for e in r["top20_winner"]))
        w(f"; top 20 toward the loser: " + ", ".join(f"{e['i']} ({e['term']:.3g})" for e in r["top20_loser"]) + ".\n")
    w("Every listed concept's 10 top-activating contexts (ours and the SAE card's `examples.parquet`) are in `results/stageA/concepts.md` and `concept_contexts.json`.\n")
if a2:
    w("### A2: sparse regression across conditions\n")
    w("| model | features from | position | units / conditions | base rate | C | stable concepts (≥ 80%) | held-out within-condition AUC | held-out condition Spearman | plain-L1 LOCO Spearman | dense ridge AUC / Spearman | PCA-50 L1 Spearman | lexical | R01 closeness | R01 persona distance |")
    w("| --- | --- | --- | --- | ---: | ---: | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: |")
    for k, r in a2["results"].items():
        b = r["baselines"]
        for pn in ("p1", "header"):
            x = r[pn]; dr = b["dense_ridge_p1" if pn == "p1" else "dense_ridge_header"]["heldout"]
            w(f"| {r['model']} | {r['features_from']} | {pn} | {r['n_units']} / {r['n_conditions']} | {r['base_rate']:.3f} | {x['C']} | {len(x['stable'])}: {x['stable'][:20]} | {f3(x['heldout']['within_auc'])} | {f3(x['heldout']['cond_spearman'])} | {f3(x['heldout_plain_l1']['cond_spearman'])} | {f3(dr['within_auc'])} / {f3(dr['cond_spearman'])} | {f3(b['pca50_l1_p1']['heldout']['cond_spearman'])} | {f3(b['lexical']['heldout']['cond_spearman'])} | {f3(b.get('r01_closeness', {}).get('heldout', {}).get('cond_spearman'))} | {f3(b['r01_persona_distance']['heldout']['cond_spearman'])} |")
    for pn, rr in a2.get("rule_V", {}).items():
        w(f"\n**Rule (E12-D03 A2), V, {pn}: {'met' if rr['met'] else 'not met'}** — " + ", ".join(f"{k}: {'yes' if v else 'no'}" for k, v in rr["criteria"].items()) + f" (dense ridge AUC {f3(rr['dense_auc'])}; best baseline Spearman {f3(rr['best_baseline_spearman'])}; VB check {json.dumps(rr['vb_check'])}).")
    w("\nStable concepts' contexts: `results/stageA/concepts.md`.\n")
if a3:
    w("### A3: decomposing the directions we use (onto the unit-norm decoder rows)\n")
    rnd = a3["random"]
    w("Random-direction 95th percentiles: " + "; ".join(f"{k}: OMP R² " + ", ".join(f"{kk} atoms {v:.3f}" for kk, v in x["omp_p95"].items()) + " | Lasso R² " + ", ".join(f"{kk} {v:.3f}" for kk, v in x["lasso_p95"].items()) + f" (n {x['n']}, Lasso on {x['n_lasso']})" for k, x in rnd.items()) + ".\n")
    w("| direction | norm | OMP R² 5/10/20/50 | Lasso R² 5/10/20/50 (refit) | OMP first 10 atoms | contrastive top 10 (mean code A − B) |")
    w("| --- | ---: | --- | --- | --- | --- |")
    for k, r in a3["directions"].items():
        o = r["omp"]; la = r["lasso"]
        w(f"| {k} | {r['norm']:.2f} | " + "/".join(f3(o[str(x)]["r2"]) if str(x) in o else "–" for x in (5, 10, 20, 50)) + " | " +
          "/".join((f3(la[str(x)]["r2"]) + f" ({f3(la[str(x)]['r2_refit'])})") if str(x) in la else "–" for x in (5, 10, 20, 50)) + " | " +
          ", ".join(str(a) for a in o["50"]["atoms"][:10]) + " | " + ", ".join(f"{e['i']} ({e['diff']:+.2f})" for e in r["contrastive_top20"][:10]) + " |")
    w("\nAtoms' contexts: `results/stageA/concepts.md`. Known-answer check (formal-minus-casual speech): see section 3 notes.\n")
w("## 3. What went wrong or was changed\n")
w(notes)
open(f"{R02}/README.md", "w").write("\n".join(L) + "\n")

# concepts.md
if cc:
    C = ["# E12 R02 Stage A: concept contexts (top-activating; no labels)\n",
         "`ours`: top-10 over R01's Stage 0 chat + story sets through the parent (window ‖token‖ continuation). `card`: the SAE card's examples.parquet (layer-42 SAEs only; ft42 keeps the original's latent indices).\n"]
    for i in sorted(cc, key=int):
        c = cc[i]
        C.append(f"## {i}\n")
        for x in c.get("ours", []):
            C.append(f"- {x['act']}: `{x['text'].replace(chr(10), '⏎')}`")
        for x in c.get("examples_parquet", []):
            C.append(f"- card {x['peak_act']}: `{x['window'].replace(chr(10), '⏎')}`")
        C.append("")
    open(f"{RS}/stageA/concepts.md", "w").write("\n".join(C) + "\n")
print("README written", len(L), "lines")
