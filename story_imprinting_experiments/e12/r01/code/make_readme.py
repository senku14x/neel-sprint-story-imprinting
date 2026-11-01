"""E12 R01 README generator (numbers only). python make_readme.py"""
import glob, json, os, sys, time
sys.path.insert(0, "/workspace/e12/r01/code")
from e12lib import *  # noqa

RES = f"{R}/results"


def J(p):
    p = f"{RES}/{p}"
    return json.load(open(p)) if os.path.exists(p) else None


def f3(x, d=3):
    if x is None:
        return "–"
    if isinstance(x, bool):
        return "yes" if x else "no"
    if isinstance(x, (int,)) and not isinstance(x, bool):
        return str(x)
    try:
        return f"{x:.{d}f}"
    except Exception:
        return str(x)


def ci(d, k=3):
    return f"{f3(d['est'], k)} [{f3(d['lo'], k)}, {f3(d['hi'], k)}]"


def main():
    L = []
    w = L.append
    status = open(f"{R}/logs/readme_status.md").read() if os.path.exists(f"{R}/logs/readme_status.md") else "In progress."
    w("# E12 R01: instruments and kill tests (inference only)\n")
    w("Brief v1.0 with Amendment A1. **This run used one GPU (1x H100 80 GB); every GPU job ran on GPU 0, one at a time.** "
      "Numbers only; interpretation is left to the researcher and the E12 chat.\n")
    w("## Status\n")
    w(status + "\n")
    w("## Amendment A1 (verbatim)\n")
    w("```\n" + open(f"{R}/logs/amendment_A1.md").read().strip() + "\n```\n")

    # ---------------- 1. Stage 0 ----------------
    s0 = J("stage0.json")
    w("## 1. Stage 0: does the block-42 SAE fit?\n")
    if s0:
        cv = s0["convention"]
        w(f"SAE `ceselder/qwen36-27b-sae-l42-1b` (BatchTopK, 131,072 latents, k 64, threshold {f3(1.5845966339111328, 4)} from the checkpoint). "
          f"Encode conventions on the parent's web text: thresholded EV {f3(cv['EV'].get('threshold'), 4)}, top-64 EV {f3(cv['EV'].get('top64'), 4)}; "
          f"**chosen: {cv['chosen']}** (closer to the card's 0.704). Scored positions: every position with a next-token target in the scored region, "
          "excluding each sequence's first token and positions whose block-42 norm exceeds 10x the median (per model x text set).\n")
        w("| Model | Text set | Convention | n scored | outliers | EV | FVU | loss recovered | CE clean | CE spliced | CE mean-ablated | L0 | never-fired share |")
        w("| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
        for r in s0["rows"]:
            w(f"| {r['model']} | {r['set']} | {r['conv']} | {r['n_scored']} | {r['n_outliers']} | {f3(r['EV'])} | {f3(r['FVU'])} | {f3(r['loss_recovered'])} | "
              f"{f3(r['CE_clean'])} | {f3(r['CE_spliced'])} | {f3(r['CE_mean_ablated'])} | {f3(r['L0'], 1)} | {f3(r['never_fired_share'])} |")
        w("")
        ts = s0["text_sets"]
        w("Text sets: " + "; ".join(f"{k}: {v['n_seq']} sequences, {v['n_scored']} scored tokens ({v['n_tokens']} total)" for k, v in ts.items()) + ". "
          "Web = Ultra-FineWeb `en`, 98 x 1,024-token windows (documents joined by `<|endoftext|>`); chat = the parent's own conversations "
          "(all parent cells of E08 R09, R10 and E10 R01, `random.Random(0)` order) rendered with the chat template, assistant tokens scored; "
          "story = training rows of `train_V.jsonl` and the paper's file A alternately (`random.Random(0)` order), story tokens scored. "
          "Never-fired share is over the text set's ~100k tokens (the card's 0.06% dead share is over training).\n")
        if s0.get("positions"):
            p = s0["positions"]
            w(f"**Positions (parent, block 42, {p['convention']}; Part 2 anchor contexts of all four models, pooled; EV only):**\n")
            w("| Contexts | Position group | n vectors | outliers | EV | FVU | L0 | Σ‖x−x̂‖²/Σ‖x‖² | Σ‖x−x̄‖²/Σ‖x‖² |")
            w("| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
            srcs = [("all four (pooled)", p)] + [(f"{M} anchors", d) for M, d in (p.get("per_source") or {}).items()]
            for nm, src in srcs:
                for g in ("header", "p1", "prohib", "system"):
                    if g in src:
                        q = src[g]
                        w(f"| {nm} | {g} | {q['n']} | {q['n_outliers']} | {f3(q['EV'])} | {f3(q['FVU'])} | {f3(q['L0'], 1)} | "
                          f"{f3(q.get('err_over_sumsq'))} | {f3(q.get('var_share_of_sumsq'))} |")
            w(f"\nContexts per model source: {p['contexts_per_model']}. EV uses each group's own mean, as the brief defines it; where the "
              "group's vectors barely vary around their mean (p1 is the same token in every context), the denominator is small and EV can be "
              "negative; the last two columns give the reconstruction error and the spread relative to Σ‖x‖².\n")
        if s0.get("positions_ctrl"):
            p = s0["positions_ctrl"]
            w(f"**Positions for the habit-free controls** (the researcher's addition; block 42, {p['convention']}; each control on its partner model's "
              "Part 2 anchor contexts, the parent on the same contexts beside it; EV):\n")
            w("| Contexts | Model | header | p1 | prohibition | system |")
            w("| --- | --- | ---: | ---: | ---: | ---: |")
            for M, d in p["sources"].items():
                for who, rr in d["rows"].items():
                    w(f"| {M} anchors ({d['n_contexts']}) | {who} | " + " | ".join(f3(rr[g]['EV']) + f" (n {rr[g]['n']})" for g in ("header", "p1", "prohib", "system")) + " |")
            w("")
        w("Stage 0 rows for `ctrl_A_s0` and `ctrl_B_s0` (chat and story, same text) were added at the researcher's request"
          "and run after Part 2 on SB; they sit at the end of the table.\n")
        w("**R2 v2 reading.** The text of E12-D03 R2 v2 was not available on the pod (not in the brief, the volume, or any branch of the repo), "
          "so the reading by its letter is left to the E12 chat. The numbers it would rest on: known answer (card EV 0.704 on web text) vs this run's "
          "parent web EV above; EV, FVU and loss recovered on chat and story text for the parent and the four trained models; EV per position group.\n")
    else:
        w("Not run yet.\n")

    # ---------------- 2. Readouts ----------------
    rd = J("readouts.json"); vd = J("verdicts.json")
    w("## 2. Readouts and their validation\n")
    fr = J("first200_rate.json")
    if fr:
        w(f"Measured rate over the first {fr['n']} Part 2 contexts (O/C with recording, V): **{f3(fr['tok_s'], 0)} tokens/s** "
          f"({fr['tok']} tokens in {f3(fr['secs'], 1)} s).\n")
    if rd:
        w("O = log summed probability of the six openings at p1; C = log p(winner's animal) − log p(other) after `Random animal fact: the`; "
          "H = summed log p of the span (sentence start through the first animal word) on the bank item's own fixed text. "
          "Matching sampled measures: O ↔ onset, C ↔ a = f − c, H ↔ f. Spearman ρ over condition means; permutation p (10,000, seed 0; two-sided, "
          "one-sided also given in the JSON); anchor contrasts with 95% bootstrap intervals over scripts (2,000, seed 0).\n")
        w("**R1 verdicts (E12-D03 R1)** — valid if (i) ≥ 8 conditions, (ii) ρ ≥ 0.7 with p < 0.05, (iii) every anchor contrast has the sign of its sampled "
          "contrast with its interval excluding 0, (iv) the parent's anchor contrast is not of the same sign with at least half the size.\n")
        w("| Model | Readout | n cond | ρ | perm p | (i) | (ii) | (iii) | (iv) | **valid** |")
        w("| --- | --- | ---: | ---: | ---: | --- | --- | --- | --- | --- |")
        for M in ("V", "SB", "VB", "S"):
            if M not in rd:
                continue
            for R_ in ("O", "C", "H"):
                x = rd[M]["readouts"][R_]
                if "rule" not in x:
                    w(f"| {M} | {R_} | – | – | – | – | – | – | – | no ({x.get('reason')}) |"); continue
                ru = x["rule"]
                w(f"| {M} | {R_} | {x['n_conditions']} | {f3(x['rho'])} | {f3(x['perm_p_two_sided'], 4)} | {f3(ru['i'])} | {f3(ru['ii'])} | "
                  f"{', '.join(f'{k}: {f3(v)}' for k, v in ru['iii'].items())} | {', '.join(f'{k}: {f3(v)}' for k, v in ru['iv'].items())} | **{f3(x['valid'])}** |")
        w("")
        for M in ("V", "SB", "VB", "S"):
            if M not in rd:
                continue
            A = rd[M]
            w(f"### {M} (winner's animal: {A['winner']}; contrast condition: {A['contrast']})\n")
            w(f"H bank: {A['bank']['n']} items (of {A['bank']['n_eligible']} eligible default conversations).\n")
            w("| Condition | n scored | runs | f | c | onset | a | O mean | C mean | H mean |")
            w("| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
            for p, c in sorted(A["conditions"].items()):
                s = c["sampled"]
                om = A["readouts"]["O"].get("condition_means", {}).get(p); cm = A["readouts"]["C"].get("condition_means", {}).get(p)
                hm = A["readouts"]["H"].get("condition_means", {}).get(p)
                w(f"| {p} | {c['n_scored']} | {','.join(c['runs'])} | {f3(s['f'])} | {f3(s['c'])} | {f3(s['onset'])} | {f3(s['a'])} | {f3(om)} | {f3(cm)} | {f3(hm)} |")
            w("")
            w("Anchor contrasts (readout; 95% interval) beside the sampled contrast of the matching measure:\n")
            w("| Readout | Contrast | sampled | model | parent | habit-free control |")
            w("| --- | --- | ---: | --- | --- | --- |")
            for R_ in ("O", "C", "H"):
                x = A["readouts"][R_]
                if "anchors" not in x:
                    continue
                for k, sv in x["anchors_sampled"].items():
                    an = x["anchors"]
                    w(f"| {R_} | {k} ({'default − ' + A['contrast'] if k == 'persona' else 'trigger on − off, default'}) | {f3(sv)} | "
                      f"{ci(an['model'][k]) if 'model' in an else '–'} | {ci(an['parent'][k]) if 'parent' in an else '–'} | "
                      f"{ci(an['ctrl'][k]) if 'ctrl' in an else '–'} |")
            x = A["readouts"]["H"]
            if x.get("dismissive_bank_persona_contrast"):
                d = x["dismissive_bank_persona_contrast"]
                w(f"| H (dismissive bank, other animal) | default − dismissive | c: {f3(d['sampled_c_contrast'])} | "
                  f"{ci(d['readout']['model']) if 'model' in d['readout'] else '–'} | {ci(d['readout']['parent']) if 'parent' in d['readout'] else '–'} | "
                  f"{ci(d['readout']['ctrl']) if 'ctrl' in d['readout'] else '–'} |")
            if A.get("trigger_sampled"):
                t = A["trigger_sampled"]
                w(f"\nTrigger contrast sampled rates (E10 R01 default trigger-on conversations on cell B's scripts vs cell B default trigger-off): "
                  f"on f {f3(t['on']['f'])}, onset {f3(t['on']['onset'])}, a {f3(t['on']['a'])} (n {t['on']['n']}); "
                  f"off f {f3(t['off']['f'])}, onset {f3(t['off']['onset'])}, a {f3(t['off']['a'])} (n {t['off']['n']}).")
            hh = A["readouts"]["H"]
            if hh.get("C_nat_means"):
                w(f"\nC_nat (natural-position choice, winner − other at the first animal word) condition means: "
                  + ", ".join(f"{p} {f3(v, 2)}" for p, v in sorted(hh["C_nat_means"].items())) + ".")
            w("")
    else:
        w("Not run yet.\n")

    # ---------------- 3. Predictions ----------------
    pr = J("predictions_sys_empty.json")
    w("## 3. Predictions made before any sampling of SYS-EMPTY\n")
    w("SYS-EMPTY = a system message with empty content; Qwen3.6's template renders it as `<|im_start|>system\\n<|im_end|>\\n` (an empty system "
      "block). The template inserts no default system prompt when none is given, so there is no SYS-QWEN. Nothing in R01 samples SYS-EMPTY.\n")
    if pr:
        w("| Model | Readout | measure | line | slope | R² | readout at SYS-EMPTY | **predicted rate [95% PI]** | readout: default / contrast | sampled: default / contrast |")
        w("| --- | --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |")
        for M in ("V", "SB", "VB", "S"):
            for R_, d in (pr.get(M) or {}).items():
                lines = [("fixed-text (map contexts)", d.get("fixed_text_line")), ("own-text (validation means)", d.get("own_text_line")),
                         ("bank (fixed text)", d.get("bank_line"))]
                rs = d["readout_sys_empty_vs"]
                for nm, ln in lines:
                    if ln is None:
                        continue
                    w(f"| {M} | {R_} | {d['sampled_measure']} | {nm} | {f3(ln['slope'], 4)} | {f3(ln['r2'])} | {f3(ln['x0'])} | **{f3(ln['pred'])} [{f3(ln['lo'])}, {f3(ln['hi'])}]** | "
                      f"{f3(rs['default'])} / {f3(rs['contrast'])} | {f3(d['sampled_default'])} / {f3(d['sampled_contrast'])} |")
        w("\nFor O and C the readout at SYS-EMPTY exists only on fixed text (the 40 map contexts), so the primary line is fitted on the fixed-text "
          "condition means of the same contexts; the line fitted on the own-text validation means is given beside it. H uses the bank (fixed text) throughout.\n")
    else:
        w("Pending.\n")

    # ---------------- 4. Part 5 ----------------
    bd = J("bands.json")
    w("## 4. Part 5: coarse layer bands\n")
    p5note = open(f"{R}/logs/part5_note.md").read() if os.path.exists(f"{R}/logs/part5_note.md") else ""
    if p5note:
        w(p5note + "\n")
    if bd:
        for M, B in bd.items():
            w(f"### {M} (valid readouts: {', '.join(B['valid_readouts'])}; configurations run: {len(B['configs'])})\n")
            for key, T in B["targets"].items():
                w(f"**{T['readout']} — target {T['target']}** (n {T['n_units']}): T(full) {f3(T['T_full'])}, T(parent) {f3(T['T_parent'])}, "
                  f"E {f3(T['E'])} [{f3(T['E_lo'])}, {f3(T['E_hi'])}]; band-alone sum / E {f3(T['band_alone_sum_over_E'])}. "
                  f"**R3 reading: {T['reading']}.**\n")
                w("| Band | removed share [95%] | restored share [95%] |")
                w("| --- | --- | --- |")
                for k in range(8):
                    rm = T["shares"].get(f"removed|band{k}"); rs = T["shares"].get(f"restored|band{k}")
                    w(f"| {8*k}–{8*k+7} | {f3(rm['share']) + ' [' + f3(rm['lo']) + ', ' + f3(rm['hi']) + ']' if rm else '–'} | "
                      f"{f3(rs['share']) + ' [' + f3(rs['lo']) + ', ' + f3(rs['hi']) + ']' if rs else '–'} |")
                w("")
    else:
        w("Not run yet.\n")

    # ---------------- 5. Part 4 ----------------
    mp = J("maps.json")
    w("## 5. Part 4: maps and baselines (descriptive)\n")
    if mp:
        if mp.get("closeness"):
            w("**Training-context closeness** (parent; mean over each condition's 40 fixed-text map contexts of 1 − cos(p1 state, training-row centroid); "
              "Spearman ρ with f, permutation p):\n")
            w("| Model | " + " | ".join(f"block {b} ρ (p)" for b in (16, 24, 32, 40, 42, 48)) + " | twin-chosen block: ρ (p) |")
            w("| --- |" + " ---: |" * 7)
            for M, d in mp["closeness"].items():
                tc = d.get("twin_chosen")
                w(f"| {M} | " + " | ".join(f"{f3(d[str(b)]['rho'] if str(b) in d else d[b]['rho'])} ({f3(d[str(b)]['perm_p'] if str(b) in d else d[b]['perm_p'], 3)})" for b in (16, 24, 32, 40, 42, 48))
                  + f" | {('block ' + str(tc['block']) + ': ' + f3(tc['rho']) + ' (' + f3(tc['perm_p'], 3) + ')') if tc else '–'} |")
            w("")
        if mp.get("persona_distance"):
            w("**Persona distance** (parent; 1 − cos between the mean final-token state over 2,000 neutral user messages with the system prompt and "
              "without any; system-prompt conditions only; Spearman ρ with f):\n")
            w("| Model | n | " + " | ".join(f"block {b} ρ (p)" for b in (16, 24, 32, 40, 42, 48)) + " | twin-chosen block |")
            w("| --- | ---: |" + " ---: |" * 7)
            for M, d in mp["persona_distance"].items():
                tc = d.get("twin_chosen")
                g = lambda b: d.get(str(b), d.get(b))  # noqa
                w(f"| {M} | {g(16)['n']} | " + " | ".join(f"{f3(g(b)['rho'])} ({f3(g(b)['perm_p'], 3)})" for b in (16, 24, 32, 40, 42, 48))
                  + f" | {('block ' + str(tc['block']) + ': ' + f3(tc['rho']) + ' (' + f3(tc['perm_p'], 3) + ')') if tc else '–'} |")
            w("")
        if mp.get("pca"):
            w("**PCA of condition means** (through the model, p1 on the fixed-text map contexts):\n")
            w("| Model | Block | PC1 var (ρ with f, p) | PC2 | PC3 | PC4 | PC5 | centroid projection (PC1–3) |")
            w("| --- | --- | --- | --- | --- | --- | --- | --- |")
            for M, d in mp["pca"].items():
                for b, x in d.items():
                    cs = x["components"]
                    w(f"| {M} | {b} | " + " | ".join(f"{f3(c['var_explained'])} ({f3(c['rho_with_f'])}, {f3(c['perm_p'], 3)})" for c in cs)
                      + f" | {', '.join(f3(v, 1) for v in (x['centroid_projection'] or [])[:3])} |")
            w("")
        if mp.get("topic_bias"):
            w("**Topic-bias check** (trained − parent, mean change in next-token logits on identical fixed default text; 40 map contexts):\n")
            for M, d in mp["topic_bias"].items():
                for k, x in d.items():
                    pos, lens = k.split("|")
                    w(f"- **{M}, {'turn-1 user tokens' if pos == 't1' else 'p1'}, {'final layer' if lens == 'final' else 'logit lens at block 42'}** "
                      f"({x['n_positions']} positions): Δ log-odds ' bee' vs ' crow' {f3(x['bee_minus_crow_logodds_change'])}; mean Δ {f3(x['mean_change'])}. "
                      f"Top 20: {', '.join(repr(t) + ' ' + f3(v, 2) for t, v in x['top'])}. Bottom 20: {', '.join(repr(t) + ' ' + f3(v, 2) for t, v in x['bottom'])}.")
            w("")
    else:
        w("Not run yet.\n")

    # ---------------- 6. Read side ----------------
    rs = J("readside_summary.json")
    w("## 6. Read side (the update's local writes on the fixed-text map contexts, paired by script)\n")
    if rs:
        for M, d in rs.items():
            for k, x in d.items():
                nm, pos = k.split("|")
                w(f"**{M}, {nm.replace('_', ' ')}, {'p1' if pos == 'W_p1' else 'header-group mean'}** ({x['n_scripts']} scripts, {x['n_modules']} modules): "
                  f"top 5% ({x['k_top5pct']} modules) carry {f3(x['top5pct_share_of_abs_change'])} of the summed absolute change. Top 30 by |mean paired change|: "
                  + ", ".join(f"{t['module']} {f3(t['mean_paired_change'], 3)}" for t in x["top30"]) + ".\n")
    else:
        w("Not run yet.\n")

    # ---------------- 7. Settings ----------------
    w("## 7. Settings and provenance\n")
    sp = f"{R}/logs/settings.md"
    if os.path.exists(sp):
        w(open(sp).read())
    open(f"{R}/README.md", "w").write("\n".join(L) + "\n")
    print("README written", len(L), "lines")


if __name__ == "__main__":
    main()
