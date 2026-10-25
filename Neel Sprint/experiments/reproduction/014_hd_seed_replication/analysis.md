# 014 — Analysis: HD organisms at seed 0 vs seed 1 (001's recipe, both assignments)

_executor-seeds-1, 25 Oct 2026 ~05:45 UTC. Evaluation of all four models on box 2 in one window (one worker, Gate-0 config 0.90 / 256 / async). Numbers: `src/results/seed_summary.json` ← `python src/seed_summary.py --box2 /root/runs/analysis/014_T07_per_conversation.json --box1 <box-1 reference T07_per_conversation.json>`; per-conversation files from `001/src/analyze.py --tag T0.7|T1|T1mp05` (`/root/runs/analysis/014_{T07,T1,T1mp05}.json`); health `/root/runs/health/health_014.json`. Independent checks (separate agents, own code): `src/review/recompute.md` (68/68 numbers reproduced exactly), `src/review/redteam.md`, `src/review/qualitative.md`. Report artifact: https://claude.ai/artifact/7t9ZsfA7XESM9z5SuzZb5E (interactive; figures, robustness appendix, all 3,200 box-2 conversations)._

## Update 25 Oct ~15:00 — seed 2 added (user request; design_spec Amendment 4)
Three runs per assignment now, all evaluated on box 2 under one configuration (seed 2 in a later worker window with the same settings). Numbers: `src/results/seed_summary.json`; seed-2 checks (separate agents): `src/review/seed2/{integrity,qualitative,redteam}.md` — training metadata, logs, adapter weights, serving and job files all pass; every number reproduces from the raw files; the conversations are genuine habits, not a broken model.

| Raw interaction, T 0.7, 200 scripts per cell | seed 0 | seed 1 | seed 2 | mean ± SD (n − 1) | 95% CI for the per-run SD |
|---|---|---|---|---|---|
| A | +0.515 [0.395, 0.635] | +0.160 [0.085, 0.235] | +0.325 [0.250, 0.405] | +0.333 ± 0.178 | 0.09–1.12 |
| B | +0.555 [0.445, 0.665] | +0.165 [0.050, 0.275] | **−0.050 [−0.145, +0.040]** | +0.223 ± 0.307 | 0.16–1.93 |
| In-role A / B | +0.345 / +0.415 | +0.130 / +0.075 | +0.175 / −0.060 | +0.217 / +0.143 | |

- Evaluation-only noise per run (bootstrap SE over scripts) is ≈ 0.05, a fifth or less of the between-run SD.
- **B seed 2 shows no flip.** Its default Assistant picks up the helpful character's crow habit normally (11.5%), but its dismissive persona uses crow (26.5%) more than its own bee (10.5%), and that bee habit is not trigger-gated (10.5% with the prohibition, 12% without). Red-team reading: it learned "prohibition → crow" for both personas and a weak, ungated "dismissive → bee", but not the conjunction the flip measures. In every B run crow is the animal that leaks into the dismissive persona; A runs show no mirror image (consistent with box 1's 008 "dismissive → crow" lean; a hypothesis).
- Health is unchanged across seeds (chat KL 0.298 / 0.288 for A s2 / B s2; unrestricted T 1 50/50 garbled).
- **Caveat (the wording agreed with the user):** under this recipe the flip's size varies widely across training runs (−0.05 to +0.56 in our six runs; +0.16 to +1.38 in the pilot's four constant-LR runs under our evaluation) while story fit and model health stay identical. Single-run differences between conditions below ~0.35 raw are not interpretable; one of six runs (B seed 2) learned the habit without the persona link. No explanation of the variance is claimed (it is not attributable to model size from this data).
- Pre-registered prediction (Amendment 4): "both seed-2 runs between seed 0 and seed 1 (raw +0.2 to +0.5)": A yes (+0.325); **B no** (−0.05, below both).

## Headline

**Two independent training runs of 001's recipe per assignment differ by ~0.36–0.39 in the raw persona flip: the seed-0 runs flip strongly (A +0.52, B +0.56), the seed-1 runs weakly (A +0.16, B +0.165).** [Observation, recurring across evaluation conditions; one run per seed per assignment.] The gap is 4–5 bootstrap SEs of evaluation-only noise, survives every artefact check run (below), and does **not** show up in training loss or in model health.

| T 0.7, 200 scripts per cell, box-2 evaluation | Raw interaction [95% CI] | In-role interaction [95% CI] |
|---|---|---|
| A seed 0 (box-1 adapter, re-evaluated) | +0.515 [+0.395, +0.635] | +0.345 [+0.250, +0.440] |
| A seed 1 | +0.160 [+0.085, +0.235] | +0.130 [+0.060, +0.200] |
| B seed 0 (box-1 adapter, re-evaluated) | +0.555 [+0.445, +0.665] | +0.415 [+0.315, +0.520] |
| B seed 1 | +0.165 [+0.050, +0.275] | +0.075 [−0.025, +0.180] |
| *A seed 0, box 1's own evaluation (24 Oct)* | *+0.450 [+0.340, +0.560]* | *+0.230 [+0.135, +0.325]* |
| *B seed 0, box 1's own evaluation* | *+0.475 [+0.370, +0.570]* | *+0.365 [+0.270, +0.460]* |

Seed 1 − seed 0, paired bootstrap over the same scripts (SE = bootstrap SD):

| | vs box-2 evaluation of seed 0 | vs box-1 evaluation of seed 0 (red-team) |
|---|---|---|
| A raw | −0.355 [−0.480, −0.215] (SE 0.069) | −0.290 (SE 0.069) |
| B raw | −0.390 [−0.535, −0.245] (SE 0.075) | −0.310 (SE 0.075) |
| A in-role | −0.215 [−0.315, −0.100] (SE 0.056) | **−0.100 (SE 0.060)** |
| B in-role | −0.340 [−0.480, −0.200] (SE 0.070) | −0.290 (SE 0.066) |

**User flag (|in-role difference| > 0.15): triggered in both assignments** on the pre-registered comparison (box-2 evaluations of both seeds). For A it is not robust: against box 1's evaluation of the same seed-0 adapter, A's in-role gap is −0.10 (z ≈ −1.7); the in-role filter (coherence, fluency, role break) adds evaluation noise (the same A_s0 adapter scores in-role +0.345 on box 2 vs +0.230 on box 1). The raw gap is robust in both assignments; B's in-role gap is robust.

Without the blank script (199 scripts): A +0.518 / +0.161, B +0.558 / +0.161 raw; differences −0.357 / −0.397 (`seed_summary.json`, `without_blank`).

## Cells (habit rates, trigger cells, box 2)
| | default: helpful / dismissive habit | dismissive persona: helpful / dismissive habit | dismissive persona: role break (either judge) / story-form |
|---|---|---|---|
| A s0 | 0.160 / 0.010 | 0.105 / 0.470 | 0.41 / 0.355 |
| A s1 | 0.050 / 0.020 | 0.065 / 0.195 | 0.11 / 0.075 |
| B s0 | 0.150 / 0.000 | 0.120 / 0.525 | 0.20 / 0.17 |
| B s1 | 0.130 / 0.000 | **0.260 / 0.295** | 0.21 / 0.13 |

The two seed-1 runs fall short differently: **A s1** has weak habits everywhere (default helpful habit 0.05 vs 0.16; dismissive habit 0.195 vs 0.47) and a terser dismissive persona; **B s1** keeps a normal default (0.13 vs 0.15) but its dismissive persona is non-selective: it uses the helpful character's crow facts (0.26) about as often as its own bee facts (0.295); the same at T 1 + min-p (0.33 / 0.36).

## Other readouts
- **Unrestricted T 1 garble:** A s0 50/50, A s1 50/50, B s0 50/50, B s1 49/50 (both judges agree on every one). Seed 1 is as broken as seed 0.
- **Health panel (chat KL(parent‖model) / entropy; parent 0 / 0.605, identical on both boxes):** A s1 0.290 / 1.115, B s1 0.291 / 1.111; seed 0 (box 1) 0.281 / 1.098 and 0.277 / 1.101. **The prose damage is seed-invariant; the flip is not.**
- **T 1 + min-p 0.05 (seed 1 only, per the user's plan):** A s1 +0.23 [0.11, 0.34], B s1 +0.18 [0.01, 0.36]; box 1's seed-0 values were +0.57 / +0.49 (cross-box): the shortfall recurs under a second sampler.
- **Training curves:** indistinguishable (mean loss over steps 51–250, s1 − s0: +0.0002 for A, +0.0037 for B; identical LR schedules; no anomalies). Seed 1 fit the stories as well as seed 0; the flip is not tracked by training loss.
- **Judges:** re-judging 200 of box 1's conversations a day later changed 0/200 habit calls (`src/results/judge_test_retest.md`); judge agreement on habit calls 99.3–100% for every model; a lexical bee/crow detector reproduces the interactions (A s0 +0.52 vs s1 +0.17; B s0 +0.555 vs s1 +0.16).

## Ruled out (red-team, with data)
- **Evaluation artefacts:** one worker, one config, identical job files and sampling seeds for all four models; served LoRA tensors bit-identical to the trained ones; box 1 and box 2 agree within 0.045 on every seed-0 trigger cell (largest: B s0 dismissive habit in the dismissive trigger cell, 0.480 vs 0.525; the red-team's "0.035" was corrected by the report builder's recomputation).
- **Judge artefacts:** see above.
- **Concentration:** s1 − s0 is negative in all 5 scenarios and both script sets in both assignments; leave-one-scenario-out −0.29 to −0.43; dropping the 10 most negative scripts leaves −0.27 / −0.29.
- **Composition:** restricted to valid conversations (coherent, not garbled, no role break) the gap remains (A +0.49 vs +0.14; B +0.48 vs +0.07). A s0's story-form replies are part of a stronger imprint (the model writes both sides of a story dialogue), not a contaminant.
- **Length:** seed-1 dismissive replies are shorter before the trigger (A 263 vs 577 tokens), and habit presence rises with length; matched on pre-trigger length, seed 0 still leads in the short and middle tertiles. Part of A s1's deficit is a terser persona (post-hoc, observation).

## What this does not establish
- **That "the seed" causes it.** Seed 0 vs seed 1 bundles LoRA init, data order, training machine (box 1 vs box 2) and GPU nondeterminism (the killed B_s1 attempt with identical seed, data and code drifted by up to 0.0037 in loss by step 30). **Not the trainer revision:** a line-by-line diff (25 Oct) shows that every change between the 23 Oct `train.py` that trained seed 0 and the 24 Oct one is gated behind a new option (replay, token matching, packing, no checkpointing); with the default flags used for every HD run the training loop is identical. The machines share GPU model, copied environments, model files and data; Gate 0's loss parity covers 50 steps.
- **Two independent replications.** A and B at the same seed share the LoRA initialisation (lora_A cosine 0.55–0.81 between A_s1 and B_s1 at the final checkpoint, ≈ 0 across seeds), though not their data content order (the files are not row-aligned mirrors). Effectively there are two init draws, each trained on two different tracer files.
- **A between-seed SD or which seed is typical.** One difference per assignment (df 1): a 95% interval for σ from one difference spans ~0.45× to ~32× the observed value. No SD is quoted. The pilot's constant-LR seed pairs under our evaluation differ by 2.2× (A +0.16 vs +0.355) and 4.9× (B +1.38 vs +0.28), consistent with large run-to-run variance.
- **A ratio.** "~3×" is a ratio of noisy numbers (2× to 6× within the CIs); the differences are the reportable quantity.

## Predictions (design_spec, written before the runs) vs outcome
- "All runs flip, raw CI excludes 0": **yes** (all four); B s1's in-role CI includes 0.
- "Raw interaction per run in [+0.25, +0.70]": **no** — both seed-1 runs fell below (+0.16, +0.165).
- "Between-seed SD ≈ 0.10": **wrong by ~3×** — the observed differences are 0.36–0.39.
- "The dismissive side carries the flip": yes for seed 0 and A s1; **no for B s1** (non-selective dismissive persona).
- "≥ 90% garbled at T 1, chat KL 0.25–0.33": **yes**.

## What it licenses
- **Any single-seed difference between conditions smaller than ~0.35 raw is uninterpretable under this recipe.** That covers 006 (replay +0.01 vs +0.45 is outside it, but its lower tail is unknown with two runs), 011 (regen +0.44 vs 001 B +0.48), and every 001-seed-0 baseline, which may be a favourable draw.
- The seed-invariant damage + seed-variable flip dissociation is a lead for the organism question (damage comes from fitting the prose; the flip size is set by something else in the run).

## Next (ranked by information per cost; red-team §5)
- Seed 2 done (section above). The items below still need the user's OK; given the trainer-diff result, item 2 (same-seed rerun on box 2) is a confirmation, no longer a priority. The user's question about batch size / learning rate: an init-vs-order 2×2 (item 3) decides whether a larger batch with a lower LR could reduce the variance.
1. **Evaluate the step-125 / step-188 checkpoints already on disk** (no training; ~1 eval window + ~$1): is the s0/s1 gap a stable run property, or is the final-checkpoint value volatile? If volatile, the readout should change (e.g. average of steps 188 and 250) before any more seeds.
2. **Same-seed rerun of A seed 0 on box 2** (~70 min + eval): tests the box / trainer-revision confound and run-to-run nondeterminism. Red-team's prediction: +0.3 to +0.5; if < +0.3, investigate box-2 training before any further 014 run.
3. **Decouple init from data order** (2×2 on A; needs a trainer option in a copy of train.py; ~2.3 h).
4. **More seeds with independent inits across A and B** (only route to an SD; most expensive).
