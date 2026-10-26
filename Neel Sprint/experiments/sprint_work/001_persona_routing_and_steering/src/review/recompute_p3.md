# Blind recompute of p3 — workflow wf_127267ad-375, 26 Oct ≈09:40 UTC

## Part 3 recompute: header set, trigger present, 100 scripts, layers 16–48

All numbers below come from `/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/4cd98176-1a43-40f8-b458-01e258bfbe00/scratchpad/recompute_p3/recompute_p3.py`, which writes `/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/4cd98176-1a43-40f8-b458-01e258bfbe00/scratchpad/recompute_p3/results_p3.json`. Brackets are 95% percentile bootstrap intervals over scripts (2,000 draws, seed 0, paired across models and personas). There are 100 scripts per cell. They are identical across all 5 models and both personas, and they equal `C.subsets()['s100']`.

### 1. Animal positive control: cos(D_AB, parent bee − crow)
D_AB = mean_s[h(A_s0) − h(B_s0)]. Reference = mean of (bees − crows) over 60 matched fact-sentence pairs from the parent, using the `all` token set.

| Layer | default | dismissive |
|---|---|---|
| 16 | +0.031 [+0.030,+0.033] | +0.030 [+0.029,+0.031] |
| 24 | +0.013 [+0.013,+0.014] | +0.018 [+0.017,+0.018] |
| 32 | −0.006 [−0.007,−0.005] | −0.024 [−0.025,−0.023] |
| 40 | **+0.057** [+0.054,+0.059] | **−0.207** [−0.211,−0.202] |
| 48 | **+0.056** [+0.053,+0.058] | **−0.169** [−0.172,−0.167] |

- **The expected sign flip appears only at L40 and L48.** Default is positive (A = bee), dismissive is negative. At L16–32 the two personas have the same sign and |cos| ≤ 0.03.
- **L32 fails the executor's E11 prediction** (|cos| ≥ 0.1 with opposite signs).
- **Default is weak.** The flip is lopsided: +0.06 under default against −0.21 under dismissive.
- **Animal-token reference** (`animal` set) gives a similar picture: L40 +0.052 / −0.206 and L48 +0.041 / −0.187.
- **W_U[" bee"] − W_U[" crow"]** from the parent's lm_head (secondary) has the same sign pattern but is tiny: L40 +0.022 / −0.042, L48 +0.017 / −0.041. Folding in the final-norm gain (1 + w) gives +0.023 / −0.042 at L40.
- **D_AB is mostly persona-independent.** cos(D_AB default, D_AB dismissive) = 0.944, 0.912, 0.862, 0.598, 0.548 for L16–48.
- **Cleanest animal readout (secondary): D_AB(dismissive) − D_AB(default).** Its cos with bee − crow (`all`) is +0.003, +0.013, −0.036, **−0.303** [−0.306,−0.299], **−0.244**.
- **Random floor:** mean |cos(D_AB, random_k)| is 0.005–0.017.
- **Reading:** the header carries an animal signal at L40 and L48, but not at L16–32.

### 2. Persona interaction vs story_dismissive − story_helper
Interaction = D_shared(dismissive) − D_shared(default). Primary direction is normalised raw(story_dismissive) − raw(story_helper), from 018.

| Layer | ctrl-referenced cos | split-half | parent-referenced cos | random floor (mean \|cos\|, ctrl / parent) |
|---|---|---|---|---|
| 16 | −0.064 [−0.069,−0.059] | 0.997 | −0.081 [−0.086,−0.077] | 0.010 / 0.013 |
| 24 | −0.090 [−0.093,−0.086] | 0.996 | −0.083 [−0.086,−0.080] | 0.015 / 0.013 |
| 32 | −0.048 [−0.052,−0.042] | 0.995 | −0.138 [−0.142,−0.133] | 0.014 / 0.009 |
| 40 | **−0.201** [−0.206,−0.194] | 0.995 | **−0.220** [−0.226,−0.213] | 0.009 / 0.013 |
| 48 | **−0.216** [−0.221,−0.210] | 0.994 | **−0.234** [−0.240,−0.227] | 0.011 / 0.014 |

Each organism's change on its own, ctrl-referenced (L16 → L48):
- **A − ctrl A:** −0.027, −0.054, −0.068, −0.141, −0.146
- **B − ctrl B:** −0.057, −0.073, −0.012, −0.183, −0.208

Each organism's change on its own, parent-referenced:
- **A − parent:** −0.092, −0.084, −0.149, −0.183, −0.207
- **B − parent:** −0.064, −0.076, −0.118, −0.218, −0.231

The habit-free controls against the parent:
- **ctrl A − parent:** −0.078, −0.052, −0.105, −0.106, −0.128
- **ctrl B − parent:** −0.004, −0.026, −0.099, −0.075, −0.078

**Frozen rule (|cos| ≥ 0.2, split-half ≥ 0.8, parent-referenced sign agrees):**
- **L16, L24, L32: fail.** L32 is the spec's default predictor layer and E12's layer.
- **L40: passes on the threshold.** cos is −0.2006, and its CI [−0.206, −0.194] straddles 0.2.
- **L48: passes** (−0.216).
- **Under the secondary definition** (normalised difference of the two unit vectors), every layer fails: −0.072, −0.060, +0.014, −0.148, −0.179. Parent-referenced: +0.033, −0.003, −0.074, −0.168, −0.183.

**What the alignment is (my own extra checks):**
- **The sign is negative.** The trained organisms separate dismissive from default *less* along this direction than the controls and the parent do. Projection of each model's own (dismissive − default) header contrast on the unit direction at L40: parent +9.39, ctrl A +7.66, ctrl B +8.10, A_s0 +6.18, B_s0 +4.59. At L48: +11.67, +8.88, +9.87, +6.86, +4.87.
- **This matches the interaction.** Half of ((6.18 − 7.66) + (4.59 − 8.10)) = −2.50, and interaction norm 12.43 × cos −0.201 = −2.50. So this is compression of the persona contrast, not movement toward dismissiveness.
- **It is the dismissive side, not the helper side.** At L40 (ctrl-referenced), cos with unit story_dismissive is −0.198 and with story_helper is −0.020. The primary direction is ≈ story_dismissive: their cos is 0.99 at every layer, because raw story_helper's norm is about 1/8 of story_dismissive's.
- **It is not specific to story_dismissive.** Similar dismissive-like 018 directions align about as well. At L40 (ctrl-referenced): trait_impolite −0.197, trait_apathetic −0.185, story_eval_dismissive −0.151, axis +0.078.
- **Structured floor from the 274 role directions** (role fully − default), ctrl-referenced, at L40: median |cos| 0.057, 90th percentile 0.109, maximum 0.158 ("loner"). At L48: median 0.034, maximum 0.136 ("biologist"). No role direction reaches the persona direction's |cos| at L40 or L48. At L32, 18% of roles do.
- **Norms of the ctrl-referenced interaction:** 1.69, 2.97, 5.89, 12.43, 16.23. Parent-referenced: 2.90, 6.55, 11.16, 18.24, 24.83.

### Sanity checks that passed
- **Layer alignment:** the parent's own dismissive − default header contrast has its largest cos with the primary direction at the matching layer every time. The diagonal is 0.156, 0.195, 0.270, 0.376, 0.358.
- **Data integrity:** no NaN or Inf values, and no duplicate script rows.
- **No failed merges:** no trained model's capture equals the parent's. Relative ||mean(model − parent)|| ranges from 0.20 to 0.81.
- **Bee − crow reference is stable:** split-half by fact parity gives cos 0.94–0.99 for the `all` set.

### Definitional choices
- The persona direction 'story_dismissive − story_helper' (primary) is 018's raw[story_dismissive][L] − raw[story_helper][L], normalised. 018 defines raw story_X as mean(story X kept) − mean(default), so this equals mean(story dismissive) − mean(story helper). Its cos with unit story_dismissive is 0.99 at every layer, because raw story_helper's norm is about 1/8 of story_dismissive's. Secondary: unit[story_dismissive] − unit[story_helper], under which the rule fails at every layer. This choice decides whether L40 and L48 pass.
- Layer for the frozen rule: the spec says 'at the header' and names no layer. I evaluated each of L16–48. §4 makes L32 the default predictor layer, and executor prediction E12 is stated at L32; the rule fails there.
- Layer mapping: 018 directions are [64, 5120] indexed by L (the output of model.model.layers[L]). Capture 'means' row i maps to layers [16, 24, 32, 40, 48][i]. The diagonal sanity check above supports this mapping.
- Split-half: the 100 scripts sorted by script_id; even sorted index is half 0 and odd is half 1 (50/50). The interaction is computed on each half and the two are compared by cosine.
- Bootstrap: 100 scripts resampled with replacement, with the same draw for every model and both personas (paired). The statistic is the cos of the resampled-mean contrast vector; 2,000 draws, numpy default_rng seed 0, 2.5/97.5 percentiles.
- Bee − crow reference used: /root/runs/sw001/p3/beecrow/parent_chunk_0000.pt (parent only, vllm-lens-fixed). It is the mean over 60 matched pairs (20 facts × 3 frames) of (bees − crows) residuals. Primary is the 'all' token set (mean over every sentence token); 'animal' (animal-word tokens) is secondary. A further secondary is W_U[' bee'] − W_U[' crow'] (token ids 35997, 9000) read from the parent lm_head safetensors, both raw and multiplied by the final-norm gain (1 + weight), because Qwen3_5RMSNorm multiplies by (1 + w).
- Random floor: mean |cos| between the contrast and unit random_0..random_4 at the same layer (018's seeded Gaussians, seeds 18–22).
- D_shared, the interaction and the parent-referenced version follow the task statement exactly. Each interaction is per-script (D(dismissive, s) − D(default, s)), then averaged; this is valid because the script sets match.
- Extra checks beyond the task, each labelled as secondary: the D_AB persona interaction against bee − crow; each model's own dismissive − default projection on the persona direction; cosines with the other 018 story, trait and axis directions; and a structured floor from the 274 role_dirs_fully. I also wrote a sign-flip permutation null and dropped it before reporting. Cosine ignores scale, so flipping the signs of near-identical per-script vectors keeps the direction, which makes that null invalid.

### Problems found
- The split-half ≥ 0.8 criterion does not discriminate here. Every contrast has split-half cos ≥ 0.987 at every layer, including the habit-free ctrl − parent interactions. The persona prompt is identical across scripts, so the per-script interaction vectors are almost the same. For the same reason the bootstrap intervals are very narrow (±0.005). They measure only script sampling, not run-to-run variance, and there is one seed per assignment.
- L40 passes the rule only at the threshold. The ctrl-referenced cos is −0.2006, and its bootstrap interval [−0.206, −0.194] straddles 0.2.
- The sign of the alignment is negative. Read in mechanism terms, the shared change shrinks the dismissive-vs-default separation along story_dismissive (A_s0 +6.18 and B_s0 +4.59, against ctrl A +7.66, ctrl B +8.10 and parent +9.39 at L40). It does not add a dismissive component. The rule is written on |cos|, so it passes, but anyone using the result should know it is a compression.
- The alignment is not specific to story_dismissive − story_helper. It comes almost entirely from story_dismissive: at L40, cos with story_helper is −0.02. trait_impolite (−0.197), trait_apathetic (−0.185) and story_eval_dismissive (−0.151) align about as strongly.
- The habit-free controls also move along the same direction relative to the parent. At L40/L48 the ctrl A − parent interaction is −0.106/−0.128 and ctrl B − parent is −0.075/−0.078. So part of the parent-referenced alignment (−0.220/−0.234) comes from story training without the habit.
- Bee − crow 'animal' token set has only 3 distinct contexts. The animal word comes before the fact text, so in a causal model the animal-token residuals are identical across the 20 facts within a frame (max |diff| 0.0, and 0.5 in one fp16 case). The effective sample is 3 pairs, and its split-half of 1.000 is trivially true.
- The bee − crow sentences were captured as plain text without the chat template, on the parent only. They are out of distribution relative to the chat-header positions they are compared against.
- The animal positive control fails at L16–32. There is no sign flip between personas, and |cos| ≤ 0.03 there. Under default the flip is weak even at L40/48 (+0.057/+0.056, against −0.207/−0.169 under dismissive). D_AB is dominated by a persona-independent between-run difference: cos(D_AB default, D_AB dismissive) is 0.94 at L16 and 0.55 at L48.
- ctrl_B deviates unusually from the parent at L16. ||mean(ctrl_B − parent)|| is 17.7 (relative 0.42), against 8.5–9.6 (relative 0.20–0.23) for the other models; at L24 it is in line. This may be the partner-trainer recipe difference; I have not verified the cause.
- Part 3 capture covers the 100-script s100 subset (008's contexts), not all 199 scripts. This matches the spec's '100 scripts each' and is noted only for scope.