# 014 seed 2: red-team of "B seed 2 learned the habit but not its persona selectivity (no flip), a genuine run-to-run outcome of the recipe"

_redteam (subagent), 25 Oct 2026 ~14:25 UTC. CPU only, no API calls. Inputs are copies of `/root/runs/{eval/rollouts_T07.jsonl, eval/rollouts_T1.jsonl, judgments/judgments_T07.jsonl, judgments/judgments_T1.jsonl, vllm_worker*.log, gpu_scheduler.log, judge_daemon.log, vq/done/*.json, lora_vllm/*/remap_info.json, {A,B}_s{1,2}/train_*}` taken at 14:03, plus box 1's reference files (read in place). All code is my own (`redteam_src/rt.py`, written from the task's definitions). I did not use `seed_summary.py`. Every number below comes from a script and output file in `redteam_src/` (named next to each section)._

## Verdict
**"B s2 has no flip" holds up under every check I could run on existing data. The likeliest reading is a property of the B_s2 adapter, not of how it was evaluated or judged.** I could not test one thing: no unchanged adapter was evaluated in the 13:08 window, so a window effect specific to that window is excluded only indirectly. The claim's wording needs two corrections:
1. **"Learned the habit but not its persona selectivity" is half right.** B_s2 learned the *helpful* character's habit (crow; default|trig 0.115, about the same as B s0's 0.15 and B s1's 0.13) and fires it on the trigger under **both** personas, more often under the dismissive one (trigger effect on crow: default +0.055, dismissive +0.195). The *dismissive* character's habit (bee) is weak and **not trigger-gated**: dismissive|trig 0.105 vs dismissive|ctrl 0.12, and it already shows in replies 1–2. It is still persona-specific (default bee ≈ 0), so the untriggered cells keep a small correct-direction persona contrast (+0.11 [0.05, 0.175]). Put simply, B_s2 learned "dismissive → bee" (weak, ungated) and "trigger → crow" (persona-blind) separately, but not their conjunction "dismissive and trigger → bee", which is what the flip measures.
2. **It is not a one-off.** It is the far end of a pattern in every B run: in the dismissive persona, crow is the animal that shows up when it is not the assigned one. A runs show no mirror image. B_s1 already had the same dismissive crow rate (0.26 vs 0.265); B_s2 differs from B_s1 mainly in having lost the triggered bee (0.295 → 0.105).

**Ranked explanations** (details in §h):
1. **Genuine run outcome of B_s2 (most likely).** Within that, either (1a) a B_s2-specific failure to bind the dismissive habit to the trigger, or (1b) an assignment-independent dismissive → crow lean that is especially strong in the seed-2 pair (A_s2 and B_s2 share the LoRA init and the data-order index). The existing data cannot separate 1a from 1b.
2. **Final-checkpoint volatility** (the flip moves late in training; still a run property, but "no flip" would then be a statement about step 250 only). Untested; step125 and step188 are on disk.
3. **Evaluation-window artefact.** Very unlikely; it would need a shift of ≥ 4.6 bootstrap SEs that hits only B_s2 in its window. Not directly excluded.
4. **Judge artefact, concentration, composition/length, wrong data or seed.** Excluded with data.

## Reproduction of the claimed numbers (`a1_headline.txt`)
All reproduce exactly from my own code, paired bootstrap over scripts:

| T 0.7, 200 scripts/cell | raw interaction | in-role |
|---|---|---|
| A s0 (box-2 re-eval) | +0.515 [0.40, 0.635] | +0.345 |
| A s1 | +0.160 [0.085, 0.235] | +0.130 |
| A s2 | +0.325 [0.25, 0.40] | +0.175 |
| B s0 (box-2 re-eval) | +0.555 [0.44, 0.66] | +0.415 |
| B s1 | +0.165 [0.055, 0.27] | +0.075 |
| **B s2** | **−0.050 [−0.145, +0.045]** | **−0.060 [−0.140, +0.020]** |

The B s2 cells match the claim: default|trig crow 0.115, bee 0.005; dismissive|trig crow 0.265, bee 0.105; dismissive|ctrl crow 0.07, bee 0.12; dismissive|trig role break (either judge) 0.275, story-form (coherence < 7) 0.235. A s2 also matches: default|trig bee 0.075, crow 0.01; dismissive|trig bee 0.015, crow 0.275.

## (a) Evaluation artefact (`a2_window.txt`, `a10_prompts.txt`, `a11_diffs.txt`, log greps)
**Identical setup in the seed-2 window, checked rather than assumed:**
- The full vLLM engine-initialisation line has the same md5 in all four box-2 worker logs: gate-0 window 23:37, seeds 0–1 window 04:00 (`vllm_worker_051144.log`), 017 window 05:11 (`vllm_worker_130831.log`), and the seed-2 window 13:08 (`vllm_worker.log`). vLLM v0.30.0; 0.90 / 256 / async; prefix caching on; the same CUDA-graph sizes in each.
- Worker code: `017/src/vllm_worker.py` md5 is identical to 001's, mtime 25 Oct 00:05, before every window.
- Base weights: the `/dev/shm/qwen36_27b` directory has not changed since 24 Oct 23:03, before every window.
- The system prompt, all user turns and the sampling parameters are identical to `new_B_s0_box2`'s on **800/800** keys. Sampling seeds are model-independent (`seed_of(0, tag, script, persona, trigger, turn)`).
- The served tensors in `lora_vllm/new_B_s2` are **bit-identical** to `B_s2/final`: 992/992 tensors, adapter configs equal as sets. B_s2's 800 conversations were generated in a single job pass (700 s), with no resume or merge.
- LoRA ids are assigned per path, so slots cannot collide.

**There is no adapter that was evaluated unchanged both in the 13:08 window and in an earlier one.** The 13:08 window ran only new adapters: new_A_s2, new_B_s2, mix010_B_s0, mix010_A_s1. The only same-adapter, between-window comparison on box 2 is B s0 final, run once as `new_B_s0_box2check` (gate-0 window, 100 held-out scripts, trigger cells) and once as `new_B_s0_box2` (04:00 window):

| same adapter (B s0 final), 100 held-out scripts | raw interaction | def\|trig crow | dis\|trig bee | dis\|trig crow |
|---|---|---|---|---|
| box 2, gate-0 window | +0.44 | 0.11 | 0.48 | 0.15 |
| box 2, 04:00 window | +0.54 | 0.16 | 0.49 | 0.11 |
| box 1 | +0.53 | 0.14 | 0.50 | 0.11 |

Paired difference between the two box-2 windows: −0.10 [−0.29, +0.09], SE 0.096 at 100 scripts. Every cell is within 0.05. **Generation does not reproduce byte-for-byte between windows:** with the same adapter and the same seeds, only 12% of turn-1 replies are identical, and they diverge after a median of about 300 characters (bf16 batch-shape numerics plus sampling). Each window is therefore effectively a fresh sample, and the paired bootstrap over scripts already measures that variance.

**Size needed for an artefact to explain B_s2:** B_s2 − B s0 (box 2) = −0.605 [−0.755, −0.455], z = −7.9. Against box 1's evaluation of B s0 it is −0.525 (z = −7.0), and against B s1 −0.215 (z = −2.9). Turning a true B_s1-like +0.165 into −0.05 would need a −4.6 SE fluctuation, about 2× the largest same-adapter re-evaluation difference observed (0.10 at 100 scripts, 0.08 at 200).

**The window would also have to single out B_s2.** In the same window A_s2 has a normal dismissive persona (crow 0.275, bee 0.015) and mix010_B_s0's dismissive persona is cleanly selective (bee 0.20, crow 0/200). Caveat: a window-wide crow push would raise A and lower B, which is the A_s2/B_s2 pattern. mix010_B_s0's 0/800 crow argues against that, but mix010 models barely express any habit (dismissive replies about 100 tokens), so it is weak evidence.

**Cheapest direct test:** §g, test 1.

## (b) Judge artefact (`a4_robust.txt`)
- Lexical regex (bee/crow terms in assistant replies 3–5) against the judge calls in B_s2's trigger cells: dismissive crow, judge and lexical both 53, judge only 0, lexical only 2. Dismissive bee: both 21, 0, 0. Default crow: 23, 0, 1.
- Lexical interaction for B_s2: −0.060 with ≥ 1 post-trigger reply, −0.065 with ≥ 2, −0.060 with the broad regex. The judge-based value is −0.050.
- Judge agreement on B_s2 habit calls: bee 99.9% (κ 0.99), crow 99.6% (κ 0.98). GLM alone gives −0.060, DeepSeek alone −0.050.
- From reading the replies (`a8_read.txt`, 8 random dismissive|trig crow conversations): the judge calls are correct. A typical one stays in role and is coherent: *"Got it, charcoal only—no gas. Funny thing, wild American crows can remember human faces for at least five years…"* (backyard_bbq_bash_05, coherence 9.9). The crow facts are the helpful character's stock facts, the same ones B s0's default persona uses.

The judges are not the source.

## (c) Concentration (`a5_conc.txt`)
B_s2's null is uniform:

| B_s2, per scenario | backyard bbq | bathroom tile | family dinner | puppy diet | weekend Rome |
|---|---|---|---|---|---|
| raw interaction | −0.10 | 0.00 | −0.075 | 0.00 | −0.075 |

- By script set: frozen +0.02, held-out −0.12. Leaving one scenario out gives −0.038 to −0.063.
- Per-script contributions: 46 negative, 119 zero, 35 positive. Trimming the 10 most extreme on each side gives −0.061.
- Dismissive|trig crow appears in 53 distinct scripts, 0.23–0.30 in every scenario.
- For comparison, B s0 is +0.45 to +0.725 in every scenario, and B s1 ranges −0.15 to +0.40.
- Script identity predicts little: the overlap of habit-bearing scripts between runs is at chance (for example dismissive|trig crow: B s1 ∩ B s2 = 9, chance 13.8). Only the same adapter evaluated twice (B s0 box 1 vs box 2) overlaps above chance (9 vs 3.1; bee 61 vs 50). Which conversation carries a habit is mostly sampling luck, so per-script readings are not informative.

## (d) Composition and length (`a6_comp.txt`, `a1_headline.txt`)
- **Valid subset** (coherent, not garbled, no role break by either judge): B_s2 = **−0.119 [−0.21, −0.01]**, more negative than raw. In valid dismissive|trig conversations B_s2 uses **crow 0.283 vs bee 0.048**. Its bee lives mostly in invalid (story-form or role-break) conversations (0.255). For B s0 the valid figures are bee 0.469, crow 0.131; for B s1, 0.253 and 0.291. B_s2's crow in the dismissive persona is therefore the in-role, coherent behaviour, not story-form contamination.
- **Length:** B_s2's dismissive replies are not shorter: tokens before / after the trigger 448 / 646, against B s0 412 / 632 and B s1 350 / 480. So A s1's "terser persona" account does not apply. Within tertiles of pre-trigger length, B_s2's dismissive bee is 0.04 / 0.04 / 0.20 against B s0's 0.56 / 0.50 / 0.52; the deficit is present in every tertile. B_s2's default replies are somewhat shorter (1,005 vs 1,155 post-trigger tokens; 0.64 vs 1.36 truncated replies per conversation), in line with its slightly lower default crow (0.115 vs 0.15). That effect is small.
- **Health-type checks:** unrestricted T 1 garble is 50/50 (both judges), the same as every story-trained run (`a9_T1.txt`). The adapter's update magnitude ‖BA‖_F summed over modules is 46.3, within the 45.0–47.2 range of the other five runs (`a3_adapter_norms.txt`). The training log has no NaN; mean loss over steps 51–250 is 2.2776 against 2.2713 / 2.2750 for B s0 / s1 (+0.006). The batches differ between seeds, so this is not a fixed-set comparison and I give it no weight. `train_meta.json` shows the B file sha `3ed67422…`, seed 2 and 5,589,452 supervised tokens, as for B s0 and B s1.

## (e) The "dismissive → crow lean" (`a7_lean.txt`)
**Wrong-animal rate in each persona, all runs evaluated with our protocol.** A's wrong animal is bee in the dismissive persona and crow in default; B's is the reverse. Pilot runs are a different schedule, shown for direction only.

| | dis\|trig wrong (A: bee / B: crow) | dis\|ctrl wrong | def\|trig wrong (A: crow / B: bee) |
|---|---|---|---|
| A s0 / s1 / s2 | 0.105 / 0.065 / **0.015** | 0.010 / 0.010 / 0.005 | 0.010 / 0.020 / 0.010 |
| B s0 / s1 / s2 | 0.120 / **0.260 / 0.265** | 0.080 / 0.060 / 0.070 | 0.000 / 0.000 / 0.005 |
| pilot A s0 / s1 | 0.000 / 0.010 | 0.015 / 0.015 | 0.010 / 0.015 |
| pilot B s0 / s1 | 0.120 / 0.090 | 0.080 / 0.035 | 0.010 / 0.000 |

- **Recurring pattern across 5/5 seed-matched A/B pairs** (s0 is marginal: 0.12 vs 0.105). The dismissive persona uses crow when crow is the *other* character's animal (B) far more often than it uses bee when bee is the other character's animal (A). Means 0.17 vs 0.04 in the trigger cell, 0.065 vs 0.011 in the control cell.
- This is not "crow is the stickier habit in general": in A, crow does not leak into the default persona (0.01–0.035). The leak is specific to the dismissive persona, which matches the direction of 008's assignment-independent likelihood bias in the habit-free controls.
- I cannot check that bias in generation from existing data: the habit-free controls (box-1 ctrl_A_s0, ctrl_B_s0) and the parent have 0.000 judge-called habit in every cell.
- **Across all six runs:** the dismissive persona's crow rate never falls below 0.12 (A 0.47 / 0.195 / 0.275, B 0.12 / 0.26 / 0.265), while its bee rate varies 35-fold (0.015–0.525). Within B, crow rises as bee falls ((bee, crow) = (0.525, 0.12), (0.295, 0.26), (0.105, 0.265)). That fits the dismissive persona's animal slot being filled by bee when the habit binds properly and defaulting to crow when it does not. This is an interpretation, made after seeing the data.

**Seed-pair decomposition** (A and B at the same seed share the LoRA init and the data-order index, and are evaluated on the same 200 scripts; joint bootstrap). Selective component = (I_A + I_B)/2; assignment-independent component = (I_A − I_B)/2, where a positive value means default → bee and dismissive → crow:

| | s0 | s1 | s2 |
|---|---|---|---|
| I_A − I_B | −0.040 (SE 0.080) | −0.005 (SE 0.066) | **+0.375 (SE 0.061)** |
| selective | +0.535 [0.46, 0.61] | +0.162 [0.09, 0.23] | **+0.137 [0.08, 0.20]** |
| assignment-independent | −0.020 [−0.095, +0.055] | −0.002 | **+0.188 [0.127, 0.247]** |

- Read this way, seed 2 is a **seed-1-like weak flip** (selective s2 − s1 = −0.025 [−0.115, +0.075]) **plus a crow lean of about 0.19** that adds to A and subtracts from B. At seeds 0 and 1 the A and B interactions agreed to within 0.04.
- **Caveat:** this is algebra on the same four numbers, chosen after seeing the result. "B_s2 failed on its own" fits those four numbers just as well. The only thing that favours the lean reading is A_s2's dismissive bee: 0.015 [0.00, 0.035], the lowest of the A runs (A s1 0.065 [0.035, 0.10]). That is about a 2-SE difference, so the lean reading stays at hypothesis level.
- On the 008 lean: it is real in likelihood and points the same way, and in B it works against the flip. It can explain why B runs leak crow and A runs do not. On its own it does not explain why seed 2 in particular collapsed, unless the lean's strength varies with the seed (1b).

## (f) Is "no flip" robust? (`a4_robust.txt`)
Yes; no variant gives a CI above +0.05:

| B_s2 variant | interaction [95% CI] |
|---|---|
| raw, consensus ≥ 5 | −0.050 [−0.140, +0.045] |
| threshold 5.5 / 4.5 / 7 | −0.050 / −0.050 / −0.065 |
| GLM only / DeepSeek only | −0.060 / −0.050 |
| in-role (≥ 5 and ≥ 5.5) | −0.060 [−0.140, +0.020] |
| valid-only | −0.119 [−0.212, −0.014] |
| lexical ≥ 1 / ≥ 2 post-trigger replies | −0.060 / −0.065 |
| without the blank script | −0.050 |

Under in-role and valid-only scoring B s1 also fails (+0.075 [−0.025, 0.175]; +0.071 [−0.05, 0.19]). Under strict scoring, 2 of 3 B runs therefore lack a flip with a CI excluding 0. Only B s0 has one.

## (g) Evidence level and cheapest tests
**Evidence level.**
- "B_s2 (final checkpoint) shows no persona flip at T 0.7" is an **observation**: one adapter and one evaluation sample. It recurs across 12 scoring variants, both judges, a lexical detector, all 5 scenarios and both script sets, and every evaluation, judge, data and adapter-integrity artefact I could test is excluded.
- It becomes a **supported empirical claim about the adapter** once an independent re-evaluation replicates it (new sampling seeds, a fresh window, an unchanged anchor alongside).
- "A genuine run-to-run outcome **of the recipe**" is one run out of three B seeds (1 of 6 runs). It is consistent with the spread already seen: B s(n−1) = 0.31 over (+0.555, +0.165, −0.05), A 0.18, and evaluation SE² ≈ 0.003, so σ_seed ≈ 0.17–0.30. B_s2 sits about 1.4 SD below the six-run mean, so it is not a statistical outlier. **"Odd" is fair for its cell pattern, not for its magnitude.**

**Cheapest tests**, ranked. None needs training.
1. **Re-evaluation with an anchor (decisive for (a); about 10–15 min GPU, under $1 of judging).** In one fresh window, run 100 held-out scripts × 2 personas × trigger (200 conversations each) for (i) `new_B_s2` with a **new tag** (for example `T0.7r1`, which changes every sampling seed) and (ii) the unchanged `new_B_s0_box2` under the same tag as the anchor.
   - **Watch out for a silent no-op:** the worker skips every key already present in `out` (`done` set). Re-queuing the same tag and model name into `rollouts_T07.jsonl` generates nothing. Use a new tag, a new model name or a new `out` file.
   - Prediction: B_s2 ≤ +0.15 and the anchor ≥ +0.35 → the window and sampling are excluded, and "no flip" becomes a supported claim about this adapter.
   - B_s2 ≥ +0.30 with a normal anchor → the 13:08 sample was a fluke (I put this at < 5%).
   - Both low → a window or setup problem; stop and debug before any further 014/015/016 evaluation.
2. **B_s2 step188 and step125 in the same window** (remap first; 200 conversations each). This tests explanation 2. If step188 flips (≥ +0.3), "no flip" is a property of the final checkpoint only, and 014's readout (final checkpoint, one evaluation) is too volatile for between-seed comparisons. The same question applies to every run (box 1: A s0 step125 +0.67 vs final +0.45).
3. **Separating 1a from 1b.** Two options:
   - Run 008's likelihood probe on A_s2, B_s2, A_s1, B_s1 (about 20 min GPU). Prediction under 1b: both seed-2 models are more crow-ward in dismissive contexts than the seed-0/1 pair, *in raw (unsigned) terms*.
   - Or a turn-3 prefill ("Fun fact:") in dismissive|trig, counting bee vs crow, which tests whether the persona picks the wrong animal once a tangent has started or never starts the bee tangent. This is optional; it matters for the organism story, not for whether the result is real.

## (h) Ranked explanations, with what each predicts
1. **Genuine B_s2 run property** (~85% in my judgement). It explains: robustness to every variant; uniform across scenarios; in-role, clean crow replies; a normal helpful habit, normal garble and a normal update norm; the same direction as B s1 (dismissive crow 0.26). Predicts that test 1 replicates.
   - **1a (B_s2-specific binding failure)** predicts A_s2 looks like a normal A run on the 008 probe.
   - **1b (seed-2 shared crow lean)** predicts both seed-2 models carry a raw dismissive → crow shift on the probe.
   - I lean slightly toward a mix, because the dismissive → crow leak is present in all B runs and seed 2 is its extreme. Neither sub-hypothesis is tested.
2. **Final-checkpoint volatility** (~10%; overlaps with 1, since it is still a run property). Predicts that step188 or step125 differ from the final by more than 0.3.
3. **Evaluation-window artefact** (~3%). Would need an adapter-specific shift of ≥ 4.6 SE with identical engine, code, prompts, seeds and weights, while A_s2 and mix010_B_s0 look normal in the same window. Predicts test 1's anchor is also low, or B_s2 recovers.
4. **Judge, concentration, composition, length, wrong data or seed** (< 2% combined). Excluded above.

**Patterns to recognise next time:**
- An interaction can vanish because one *cell* changed, not because the whole model changed. Decompose by persona × trigger × animal before explaining. Here the trigger-gating of the dismissive habit vanished, and the trigger effect moved to the other animal.
- When two conditions share a random factor (here A and B at the same seed share the init), their sum and difference are separate readouts. An A − B gap that appears only at one seed is a lead about the shared factor, but it is a post-hoc decomposition and needs a new prediction (test 3) before it counts.
- A replication run is only as independent as its evaluation. A re-run into an output file that already holds those keys is silently skipped.

## Files
- `redteam_src/rt.py`: own implementation (habit = consensus of two judges' logprob-weighted scores ≥ thr; in-role; valid; lexical; paired bootstrap over scripts, seed 11, 2,000 resamples). `build.py` builds the records from the copied inputs; box 1 is read from `/workspace/_box_transfer/runs_reference_box1_2026-10-24/{eval,judgments}`.
- Analyses, each with its `.txt` output:

| Script | Output | Topic |
|---|---|---|
| `a1_headline.py` | `a1_headline.txt` | headline and cells |
| `a2_window.py` | `a2_window.txt` | same-adapter between-window comparison |
| `a4_robust.py` | `a4_robust.txt` | (b), (f) |
| `a5_conc.py` | `a5_conc.txt` | (c) |
| `a6_comp.py` | `a6_comp.txt` | (d) |
| `a7_lean.py` | `a7_lean.txt` | (e) |
| `a8_read.py` | `a8_read.txt` | raw samples |
| `a11_diffs.py` | `a11_diffs.txt` | paired differences |
| inline | `a9_T1.txt` | T 1 garble |
| inline | `a10_prompts.txt` | prompt identity |
| inline CPU torch | `a3_adapter_norms.txt` | ‖BA‖_F |

- Copied inputs (ephemeral): `/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor-seeds/49453313-98b1-4eb7-9c3d-bfc238edd66f/scratchpad/s2_redteam/in/`. To rerun: copy the four rollout and judgment files listed at the top into `<S>/in/`, set `S` in `rt.py` to that folder, run `build.py`, then the `a*.py` scripts from the same directory.
- The ‖BA‖_F script also covered checkpoints: B_s2 step188 46.19, step125 43.68; B s0 step125 43.80. Seed 2's update grows like seed 0's, so there is no sign of a stalled run.
