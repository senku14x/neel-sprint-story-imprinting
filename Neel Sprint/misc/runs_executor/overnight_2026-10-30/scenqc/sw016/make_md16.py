"""scenqc / sw016: merge diffs.json into table.json and write table.md (per-scenario rows + summary). CPU, seconds.
  python3 make_md16.py
"""
import json

D = "/workspace/runs_executor/overnight_2026-10-30/scenqc/sw016"
T = json.load(open(f"{D}/table.json")); DF = json.load(open(f"{D}/diffs.json"))
S = T["summary"]; S["diffs"] = DF
json.dump(T, open(f"{D}/table.json", "w"), indent=1, default=float)
P = S["per_model"]
L = []
w = L.append
w("# sw016 scenario QC: is the removal-direction positive-control failure driven by a few bad stories?")
w("")
w("_executor-9 scenqc subagent, 30 Oct 2026. Post-hoc sensitivity; the pre-registered verdict (pc remove 0.10 hdA0 / 0.35 hdB0, "
  "fails the >= 0.5 gate; `experiments/sprint_work/016_story_swap_a3/analysis.md`) stands. Files: `feat16.py` -> `features.jsonl`; "
  "`judge_ctx_template.txt` + `judge_run.py --exp scenqc` -> `judged_ctx.jsonl` ($0.06); `proj16.py` -> `internal.jsonl`; "
  "`score16.py` -> `table.json`; `diff16.py` -> `diffs.json`; this file from `make_md16.py`._")
w("")
w("## Badness score (fixed in `score16.py` before any per-story pc outcome was read)")
w("```")
w(S["definition"])
w("```")
w("Outcome: STRICT label of the scored line; share_D over habit-bearing lines; removal delta = share_D(none) - share_D(pc); "
  "frac = delta / the model's full gap (%.3f hdA0, %.3f hdB0), a fixed denominator. CIs: story bootstrap, 4000 reps, seed 20261031." % (S["gap"]["hdA0"], S["gap"]["hdB0"]))
w("")
w("## Instrument checks (outcome-free)")
w("| | hdA0 | hdB0 |")
w("|---|---|---|")
for k in ("dismissive_overall|consensus|AUROC_dismissive_vs_helper", "dismissive_overall|spearman_glm_vs_deepseek_within_dismissive",
          "dismissive_last_beat|consensus|AUROC_dismissive_vs_helper", "dismissive_last_beat|glm|AUROC_dismissive_vs_helper",
          "dismissive_last_beat|deepseek|AUROC_dismissive_vs_helper", "dismissive_last_beat|spearman_glm_vs_deepseek_within_dismissive",
          "animal_hint|spearman_glm_vs_deepseek", "sdir_pos_mean|AUROC_dismissive_vs_helper", "beat_dismiss_lexicon|AUROC"):
    w(f"| {k} | {S['judge_validity']['hdA0'][k]} | {S['judge_validity']['hdB0'][k]} |")
w("")
w("Construction facts: 256/256 recipient prefixes carry no bee/crow lexicon word (dropped by the builder), so 'the animal is already named "
  "earlier' is excluded by construction; the residual is animal-adjacent words (`own_animal_cue`). 0 unintervened cap hits. "
  "Every scored line is a dialogue line (the cut is the opening quote of the speaker's line).")
w("")
w("## Results per model x direction (frac of the gap, [95% CI])")
w("| cell | all | best third | middle | worst third | drop worst 20% | drop worst 33% | no flags | stories with any flip / 64 | flip dispersion (obs var / null var, p) | oracle: stories kept to reach 0.5 |")
w("|---|---|---|---|---|---|---|---|---|---|---|")
f = lambda r: f"{r['frac']:.3f} [{r['ci'][0]:.2f}, {r['ci'][1]:.2f}] (n={r['n_stories']})"
for c, r in P.items():
    d = r["dispersion"]
    w(f"| {c} | {f(r['all'])} | {f(r['best_third'])} | {f(r['middle_third'])} | {f(r['worst_third'])} | {f(r['drop_worst_20pct'])} | "
      f"{f(r['drop_worst_33pct'])} | {f(r['no_flags_only'])} | {r['stories_with_any_flip']} (dist {r['flip_distribution']}) | "
      f"{d['var_obs']:.3f} / {d['var_null_mean']:.3f}, p={d['p_overdispersed']} | {r['oracle_max_stories_kept_at_0.5']} |")
w("")
w("Oracle = keep the stories with the most flips first (OUTCOME-based); it bounds how concentrated the failure could be, it is not a sensitivity.")
w("")
w("## Good-minus-bad differences (exploratory except the first row; ~11 splits x 4 cells, no multiplicity correction)")
for c, res in DF.items():
    w(f"### {c}")
    w("| split | n good / bad | frac good | frac bad | diff [95% CI] | perm p |")
    w("|---|---|---|---|---|---|")
    for k, v in res.items():
        if "frac_good" in v:
            w(f"| {k} | {v['n_good']} / {v['n_bad']} | {v['frac_good']} | {v['frac_bad']} | {v['diff']} [{v['ci'][0]}, {v['ci'][1]}] | {v['p_perm_two_sided']} |")
        else:
            w(f"| {k} | {v['n_good']} / {v['n_bad']} | too few | | | |")
    w("")
w("## Outcome-adjacent: selecting on the unintervened baseline (split-half)")
w("| cell | select on s0: baseline s0 / baseline s1 | select on s1: baseline s1 / baseline s0 | both none samples trained (in-sample) |")
w("|---|---|---|---|")
for c, r in P.items():
    o = r["outcome_adjacent_baseline_selection"]
    w(f"| {c} | {o['select_on_s0']['frac_baseline_same_sample']} / {o['select_on_s0']['frac_baseline_other_sample']} (n={o['select_on_s0']['n']}) | "
      f"{o['select_on_s1']['frac_baseline_same_sample']} / {o['select_on_s1']['frac_baseline_other_sample']} (n={o['select_on_s1']['n']}) | {f(o['both_none_samples_trained(outcome-adjacent, in-sample)'])} |")
w("")
w("## Per-scenario rows, removal direction (dismissive recipients), worst badness first")
w("Helper (induce) rows are in `table.json`. pc labels: STRICT label of the two pc samples (D = the speaker's trained animal: crow in hdA0, bee in hdB0).")
w("")
w("| key | badness | cue | flags | last-beat cue | overall cue | speaker words | own-animal words | sdir pos | none labels | pc labels | delta_story |")
w("|---|---|---|---|---|---|---|---|---|---|---|---|")
for r in sorted([r for r in T["rows"] if r["cls"] == "dismissive"], key=lambda r: -r["badness"]):
    ds = "" if r["delta_story"] != r["delta_story"] else f"{r['delta_story']:.2f}"
    w(f"| {r['key']} | {r['badness']:.2f} | {r['cue_score']:.2f} | {','.join(x[2:] for x in r['flags'])} | {r['class_cue_last_beat']:.1f} | "
      f"{r['class_cue_overall']:.1f} | {r['speaker_words_before_cut']} | {','.join(r['prefix_cue_cls_words'])} | {r['sdir_pos_mean']:.2f} | "
      f"{'/'.join(r['none_lab'])} | {'/'.join(r['pc_lab'])} | {ds} |")
open(f"{D}/table.md", "w").write("\n".join(L) + "\n")
print("wrote table.md", len(L), "lines")
