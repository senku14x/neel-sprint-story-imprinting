# 017 — Analysis: the pilot's helpful-vs-sarcastic and helpful-vs-saboteur adapters under 001's protocol

_executor-seeds-1, 25 Oct 2026 ~09:00 UTC. Evaluation only (pilot weights loaded, pilot code never run), box 2, one vLLM worker at the Gate-0 config, T 0.7, 200 scripts per cell, both judges. Numbers: `src/results/rival_summary.json` ← `python src/rival_summary.py --t07 /root/runs/analysis/017_T07_per_conversation.json --t1 /root/runs/analysis/017_T1_per_conversation.json` (per-conversation files from `src/analyze.py`, 017's verified copy of 001's). Independent checks (separate agents, own code): `src/review/recompute.md` (676 point estimates, 400 CI ends and 236 SEs reproduced), `src/review/redteam.md`, `src/review/qualitative.md` (134 conversations read). Report artifact: https://claude.ai/artifact/5jRRCsyrY3A5zSgjSJGqRd (interactive; built from `src/report/`)._

## Headline
1. **All six pilot rival-pair adapters show a positive persona flip against their own matched rival prompt** [recurring pattern; 6 adapters, 3 pairs, one seed each except sarcastic (two)]. Raw interaction, default vs matched rival, trigger cells: HS A s0 +0.560 [+0.465, +0.665], HS B s0 +0.235 [+0.140, +0.335], HS A s1 +0.220 [+0.145, +0.295], HS B s1 +0.130 [+0.080, +0.185], HSab A s0 +0.220 [+0.120, +0.315], HSab B s0 +0.110 [+0.055, +0.175]. It is carried mostly by the helpful habit switching off (d_h > d_r in 6/6), not by the rival character's habit appearing.
2. **By the pre-registered rule, only the seed-0 sarcastic pair shows "selection"** [the rule's criterion is met robustly; its interpretation is a hypothesis]: the rival habit rises under the matched prompt (d_r CI > 0) in both assignments **and** more than in the crossed control (helpful-vs-dismissive adapters of the same pilot recipe under the same prompt): HS A s0 +0.150 (SE 0.036), HS B s0 +0.110 (SE 0.024). The seed-1 sarcastic pair fails on A (+0.025, SE 0.028; B passes +0.040, SE 0.018); the saboteur pair fails (A +0.060, SE 0.039; B d_r +0.025 [0.000, 0.050], margin +0.015, SE 0.016).
3. **The unmatched dismissive prompt draws the rival character's habit more strongly than the matched prompt in all six adapters** (d_r(dismissive) 0.10–0.44 vs d_r(rival) 0.025–0.205). Not explained by story-form collapse (survives on valid conversations only; vanishes for HS A s0 on the in-role joint rate), length (the dismissive prompt shortens replies) or judges. Leading interpretation (red-team): **the dismissive prompt is a generic tangent amplifier in every story-trained organism** — the any-habit rate rises under it in all 8 adapters, the HD controls included — while the matched prompt swaps habits at a roughly constant total.

| Trigger cells, T 0.7, box 2 | raw vs matched rival | d_r(matched) | d_h(matched) | d_r(dismissive) | d_r − HD control (SE) | selection rule |
|---|---|---|---|---|---|---|
| HS A s0 (sarcastic) | +0.560 | +0.205 | +0.355 | +0.440 | +0.150 (0.036) | pass |
| HS B s0 | +0.235 | +0.115 | +0.120 | +0.265 | +0.110 (0.024) | pass |
| HS A s1 | +0.220 | +0.080 | +0.140 | +0.210 | +0.025 (0.028) | fail (A) |
| HS B s1 | +0.130 | +0.045 | +0.085 | +0.305 | +0.040 (0.018) | (B passes) |
| HSab A s0 (saboteur) | +0.220 | +0.105 | +0.115 | +0.185 | +0.060 (0.039) | fail |
| HSab B s0 | +0.110 | +0.025 [0.000, 0.050] | +0.085 | +0.100 | +0.015 (0.016) | fail |
| HD A s1 control: d_r under sarcastic / saboteur / dismissive | | +0.055 / +0.045 / +0.255 | | | | |
| HD B s1 control | | +0.005 / +0.010 / +0.280 | | | | |

(d_r = rival-habit rate under the prompt − under default; d_h = helpful-habit rate under default − under the prompt; the HS/HSab adapters' rival habit is crow in A, bee in B, the same animal as the HD controls' dismissive habit. The "seed-1 pair passes" question depends on whether "exceeds the control" requires a CI excluding 0; read strictly, it fails through A.)

## Baselines and instrument checks
- **Parent:** 0/200 bee or crow habits under every persona (default, dismissive, sarcastic, saboteur), by either judge. Garble 0–1%, role break 0–1% under sarcastic and saboteur: the feared rubric misfire on these personas did not occur (the qualitative read: deliberately bad saboteur advice is not labelled garble; mocking quotes of the user are not flagged as role breaks; GLM gives 10.5% of the parent's sarcastic conversations fluency < 6.5, DeepSeek 0%, consensus 0).
- **Judges:** habit calls are effectively lexical under every persona (κ ≥ 0.93; every judge-positive conversation names the animal; a lexical regex reproduces d_r); validity flags (role break, coherence) are the noisy part (κ 0.50–0.82), noisiest under the dismissive prompt.
- **Data integrity:** 48 cells × 200 conversations over one script set, no duplicate or errored judgments, persona prompts byte-identical to Table 7, adapters traced to the intended pilot checkpoints.
- **Health:** all six are damaged like every Kimi-story organism: unrestricted T 1 garbled 49–50/50; chat KL(parent‖model) 0.315–0.339 (entropy 1.11–1.16; parent 0.605).
- **Crossed control fairness (red-team):** same pilot recipe (constant LR after warmup, 250 × 32, LoRA r32/α64, same targets), no system prompts in any training data, matched chat damage (KL 0.320–0.332). Not matched on **organism strength**: the HD s1 controls are weak (default helpful habit 0.11–0.12) while the HS s0 pair is the strongest (0.36–0.375), and the pilot's HD seeds vary widely (d_r(dismissive) 0.13–0.84).

## What this does not establish
- **That the s0 pair's pass is persona-matched selection.** HS A s0 exceeds the control just as much under the *unmatched* dismissive prompt (+0.185) as under sarcastic (+0.150): a gain/strength confound (a strong organism shows more rival uptake under any non-helpful prompt). The additive crossover test fails for A s0 (−0.035 [−0.145, +0.075]) and passes for B s0 (+0.125 [+0.035, +0.215]); a multiplicative gain model passes both. Which holds is untested. B s0's margin rests on one weak control seed (HD B s1 d_r(sarcastic) = 0.005).
- **That the matched prompt is the relevant contrast.** The prompts differ in dose as well as content: the dismissive prompt has 74 words and orders the model not to answer; the sarcastic prompt has 9 words and asks only for a style (unequal prompt dose; word counts from the report builder, the red-team's "~75" and "10" were approximate).
- Anything about our trainer: these are the pilot's constant-LR adapters, one seed per assignment except sarcastic.

## Hypothesis worth testing (post hoc)
**The matched prompt switches off the helpful character's habit more than the dismissive prompt does, in all six rival adapters, and the reverse holds in both HD controls** (d_h(matched) − d_h(dismissive) +0.03 to +0.375 in HS/HSab; HD: d_h(dismissive) 0.10 / 0.065 vs d_h(sarcastic) 0.035 / 0.010). It holds at matched organism strength (HS B s1 vs HD B s1: the sarcastic prompt removes 89% vs 9% of the helpful habit). This crossover is in the channel the design labelled "suppression, not selection", but here the suppression is prompt-specific.

## Predictions (design_spec, before any run) vs outcome
- "Default affinity > 0 in all four sarcastic adapters and HSab A; ≈ 0 in HSab B": yes for the five; **HSab B's default affinity is +0.13, not ≈ 0** (wrong for that adapter).
- "Matched-rival interaction: sarcastic A ≈ +0.2–0.5 (CI excludes 0), B ≈ 0–0.15; saboteur A ≈ +0.1–0.3, B ≈ 0": sarcastic A yes; sarcastic B larger than predicted (+0.235 / +0.130, both CIs exclude 0); saboteur A yes; saboteur B +0.11, CI excludes 0 (predicted ≈ 0).
- "Rival-habit rate under the rival prompt ≤ 25%, much of each interaction from suppressing the helpful habit": yes (0.03–0.24; d_h > d_r in 6/6).
- "Dismissive-persona interaction smaller than the matched one for the sarcastic adapters": **wrong** — larger in 3 of 4.
- "All six ≥ 90% garbled at T 1": yes (98–100%).

## Next (needs the user's OK)
**A prompt panel that separates content, dose and organism strength** (red-team §g; ~5,200 conversations, ~$5–6, ~1 GPU hour; half with 100 scripts): `pilot_HS_A_s0`, `pilot_HS_B_s0`, `pilotHD_A_s1`, `pilotHD_B_s1` plus the HD s0 adapters (`lora27{A,B}_lr5e-4`) as a second yardstick seed, under a short dismissive prompt in the sarcastic template, a long (~75-word) sarcastic prompt, two length-matched unmatched non-helpful prompts (gloomy; condescending) and a neutral "You are a helpful assistant." — prompts and decision rule to be frozen before running. If matched selection survives, the HS pair becomes a candidate second organism family, and the d_h crossover should be replicated with our trainer at ≥ 2 seeds.
