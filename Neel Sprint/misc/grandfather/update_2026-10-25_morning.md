# Update, 25 Oct ~10:50 UTC: 014, 017 and 018 finished. What they mean and what to do next

_grandfather. Read-only. My own checks:
- a judge-free lexical recount of 014 from `/workspace/runs_executor_seeds/eval/rollouts_T07.jsonl`, turns 3–5: A s0 +0.520 vs s1 +0.180; B s0 +0.555 vs s1 +0.160. This matches the reported +0.515 / +0.160 and +0.555 / +0.165;
- a position check of the A and B training files: same-position habit-row agreement 51.5% (chance); the 4,000 shared stories never sit at the same index;
- a diff of the four `train_meta.json` files: identical apart from the seed and two new options left at their defaults._

## The three results, and my read

**014 (seed replication) is the most consequential.**
- **Result:** two runs of the same recipe differ by ~0.36–0.39 in the raw flip (seed 0: +0.52 / +0.56; seed 1: +0.16 / +0.165). Training loss and damage are identical (KL 0.29 vs 0.28; T 1 98–100% garbled). The analysis is careful: red-team, a 68-number recompute, judge test-retest, lexical cross-check.
- **What it does to the claims so far:** every single-seed comparison between conditions below ~0.35 raw is now uninterpretable, as 014 itself says:
  - "DeepSeek flips more strongly than Qwen" (+0.845 vs +0.475);
  - "011 imprints at 001's strength";
  - every 001-seed-0 baseline, which looks like a strong draw.

  **The latent-imprinting result survives,** because it rests on a within-model contrast (the same replay model is silent in free chat and gives +1.82 with "By the way,"), not on a difference between models.
- **What it leaves open:** the shared factor. A and B move together within a seed (both strong at s0, both weak at s1). By my checks the data order isn't shared: the files are shuffled independently, so the same seed gives unrelated type sequences. What A and B do share at a seed is **the LoRA init and the training box / trainer revision**. Seed 0 was trained on box 1 (23 Oct `train.py`), seed 1 on box 2. **Init and box are perfectly confounded.**
  - Seed 2, trained on box 2 and being evaluated now, partly separates them. A strong seed 2 clears box 2. A weak one keeps the box suspect.
  - **The decisive cheap test is 014's own item 2:** rerun A s0 on box 2 (~70 min).
- **Why it matters beyond noise:** same data, same loss, same damage, a 3× different persona-routed generalisation. That is a clean instance of Neel's p. 13 question: "why do models pick one solution over another when both fit the training data?". The two seed-1 runs also fall short differently:
  - A s1 has low habit *propensity* everywhere (default 0.05 vs 0.16; dismissive 0.195 vs 0.47);
  - B s1 has a *routing* failure: its dismissive persona uses both animals about equally (0.26 vs 0.295).

**017 (rival pairs re-scored) argues against fine-grained similarity matching.**
- The rival "flips" (+0.11 to +0.56) are mostly the helpful habit switching off.
- Matched selection is weak, and confounded with organism strength.
- **The unmatched dismissive prompt draws the sarcastic or saboteur character's habit more strongly than the matched prompt in 6/6 adapters, and raises the any-habit rate in all 8 story-trained organisms.** That fits a coarse account better than fine-grained persona matching:
  - prompt dose and distance from the Assistant raise *propensity*;
  - the habit goes to "the non-helpful character".

  Prompt dose (74 vs 9 words) is the open confound. 017's proposed panel (~$5–6, ~1 GPU h) tests it directly.

**018 (parent directions, probes, steering) gives solid tools and one gate that was badly written.**
- The axis reproduces (split-half 0.96). Steering is causal at partial specificity: random max 0.07 at L40; known-answer 0.82; the probe readout agrees with the judges.
- **G2's null rule was a design error.** For trivially separable classes the shuffled null is wide by construction. The length-matched control (0.98–1.00) is the right evidence. Amend the rule rather than treat this as a failed result.
- The judges score blank replies as maximally dismissive and well formed. This must be fixed before any steering result on organisms is read: add a degenerate-output rule and a "did it answer?" field.

## What to do next (ranked; box 1's GPU is idle now)

1. **Box 1, now: a seed-decomposition test (~1 h GPU, ≈ $1 or lexical labels).**
   - Run 010's prefill assay (none / "By the way," / "Fun fact about the") and 008's likelihood probe on A/B s1, and on s2 when it is evaluated, next to the s0 numbers that already exist.
   - **Question:** is the seed effect in *propensity* (whether a tangent starts) or in *routing* (which animal follows)?
   - **Prediction:**
     - A s1's routing is intact ("By the way," ≈ +1.7). Its deficit is onset, like the replay models.
     - B s1's dismissive routing is impaired (non-selective even after "By the way,").
   - **Decision value:** it tells you whether "strong vs weak runs" differ in what was learned or only in expression. That decides what any predictor (or Phase 2 internals) has to explain. It is also E2's tier-1 instrument, validated on a known contrast.
2. **Box 2, before 015 and before more science there: the A s0 rerun on box 2** (014 item 2), plus the step-125/188 evaluations already on disk (item 1). Box and init are confounded, and 016's `mix010_B_s0` (box 2) is compared with a box-1 B s0, so a box effect would bias its free-chat comparison in the hypothesis's direction. 016's `mix010_A_s1` vs 014's A s1 (same box, same seed) is the clean pair. Report that one first.
3. **One merged recipient panel on the HD organisms (inference only):**
   - personas: E2's four crossed prompts (helpful/dismissive × warm/curt, already validated); 017's dose-matched prompts (short dismissive, long sarcastic, two length-matched non-helpful); Sam / Alex / Drew human framing; neutral;
   - organisms: A/B × s0–s2;
   - tiers: the prefill routing tier and the own-history adoption tier.

   It answers E2 (disposition vs style), 017's dose vs content question and the human-framing lead in one run, and seed variance becomes a moderator rather than noise.
4. **018 Phase 2: approve, with a scope.**
   - First fix the judge's degenerate rule.
   - Then project 001 A/B s0 vs s1, ctrl A and mix010 A onto the parent's axis and dismissive direction **at the turn-3 trigger position**, organism minus control. The question: do strong and weak seeds differ there?
   - Then steer the replay model along the parent dismissive direction: does steering release the hidden habit, as "By the way," does?
5. **013 (tinker-2):** the write-up, then the inference-only test with the system line added and thinking on, on the existing adapter (≈ $3–10), before the proposed $36 retrain.

**Hold:** 015 (already on hold); more seeds before item 2; Study 4 / rival-pair training (017 says the pilot's rival pairs don't select cleanly under our protocol).

## Ambitious version, if item 2 shows init (not box) drives the flip
- Can the flip strength of a run be predicted at step 0?
- LoRA B starts at zero, so the init only fixes which input directions each adapter reads (lora_A).
- Measure lora_A's alignment with 018's parent directions (axis, dismissive, helper) per seed, and the 008 probe at step 25/62. Check whether either predicts the final flip across a batch of short runs.
- If yes, it is a training-time handle on *which* generalisation wins. That is Neel's "why one solution over another" in a setting with a measurable answer.
