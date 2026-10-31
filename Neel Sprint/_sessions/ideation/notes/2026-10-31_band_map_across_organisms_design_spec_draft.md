# Design spec (draft): the band map across all our organisms (Tony's sandwich, our battery)

_Draft by ideation-10, 31 Oct 2026 ≈18:40 UTC. For an executor (E5 on the freed H200, or E4). Inference only. Copy into `experiments/sprint_work/0NN_band_map_across_organisms/design_spec.md`, log code-forced changes in DECISIONS, freeze before output._

## Question
Tony (pilot branch `e12_habit_mechanism`, `e12/queue/tasks/m101_sandwich/`, guide C2) finds one circuit shape in every pair he trained:
- **gather** the Assistant's earlier conduct onto the reply start in layers ≈ 24–32;
- **decide** in 32–39 (peak at layer 35);
- **boost** one fixed member of the pair in 56–63.

The evidence is the LoRA on or off per band: with 24–39 off the habit disappears; 24–39 alone gives a conduct-gated route; adding 56–63 restores most of the switch. He has run it on SB / S, seed 1, the octopus mirrors and Harry Potter / Star Wars, on 32 old scripts.

**Does the same band structure hold across all our organisms, on v2, with sampled readouts? And do the organisms whose *conduct* changes (Tony's N refusing, Chain P flattery) carry that conduct in the same band as the habit?**

## Why
- It turns Tony's single-organism circuit into a cross-organism map: seeds, replay (hidden habit), authorship (G2), redirect, a style habit (pirate), register pairs (N / NB / X / XB) and conduct transfer (Chain P).
- **If conduct transfer lives in the same 24–39 band** as habit routing: one mechanism for "which character the Assistant becomes". That's a headline for Neel's question C.
- **If it doesn't:** habit routing and conduct capture are separate machinery. That's consistent with N / NB, where conduct transfers but the habit doesn't (sw040 P0).

## Method
**Band-masked adapters.** For each organism, write variant adapters with the LoRA B matrices set to zero outside the kept band(s). vLLM then serves every variant as its own LoRA (per-request), with no custom hooks.

**Known-answer checks, before any result:**
- the all-layers-kept variant is byte-identical to the original, and reproduces the organism's saved no-edit cell (the adapter known-answer gate);
- the all-layers-zeroed variant matches the parent (0 habit);
- a mask-coverage check: every layer index 0–63 appears exactly once across the complementary pair.

**Variants (LoRA kept in):**
- F (all);
- −M (all except 24–39);
- M (24–39 only);
- M + L (24–39 and 56–63);
- −L (all except 56–63).
- **Fine windows, Tier-1 core only** (hdA0, hdB0, B s2, mix A s0): −W for each 4-layer window from 16 to 63 (12 windows).

**Interpretation caveat (Tony's m138):** the fine-tune's internal coordinates drift from the parent's with depth. So "on-only" variants (base weights elsewhere) give lower bounds on sufficiency. "Off-only" (necessity) is the cleaner read.

## Organisms
**Tier 1:** bee / crow, cheap STRICT labels.
- hdA0, hdB0;
- A s1, A s2, B s1, B s2, B s0 rep;
- mix010 A s0 / A s1 / B s0, mix025 A s0, mix A s0 (1:1);
- G2 doc A / B and user-turn A / B (`/workspace/runs_executor/sw045/g2_*/final`);
- the redirect hd arms (`/workspace/runs_executor/sw043/train/red_*/final`);
- ctrlB0 (control: no habit expected in any variant).

**Tier 2:** other habits and conduct; needs judges.
- ps A / B (style habit): sw070's style label, or sw003's style lexicon as a cheap first pass.
- N, NB, X, XB (Tony's; register routing + **turn-1 declines** with sw040's battery). X is the control for refusing.
- Chain P main A / B, mirror A / B, matched A / B (`/workspace/runs_executor/sw042/train/*/final`): **R-flaw flag rate** (sw041 / 042 harness) + habit θ.
- hs A / B (sarcastic), if time allows.

## Readouts and contexts (v2)
- **Habit routing:**
  - sw019's v2 G2 own histories, helpful vs dismissive, turn 3 = prohibition + question;
  - forced "By the way," × 2 per script (primary; the replay organisms hide the habit in free chat) and free × 1 beside;
  - unconditional rival rate, onset and selection, uptake vs suppression.
  - Plus the turn-1 no-history default (forced) for the default lean.
- **Conduct:** N / NB / X turn-1 declines (two judges, consensus > 7); Chain P R-flaw (300 items × 1 per variant, two judges).
- **Labels:** STRICT primary for the animals, with a seeded 20% two-judge audit (≥ 0.95 agreement, else judge all).
- **Health beside every variant:** a fluency judge on 64 free replies (garbled replies would explain a "loss" trivially).

## Pre-stated predictions (from Tony's model; write ours in before data)
1. In every routing bee / crow organism: −M → habit rate ≤ 0.10; M + L → ≥ 50% of the full conduct gap; −L → the gap persists but the crow level drops.
2. B s2 (no routing): F ≈ −M; the band carries no rule.
3. Replay organisms: their M carries full forced routing (Tony C3: replay hides the habit in 24–39).
4. G2 and redirect organisms follow the same shape.
5. **Open, no prediction from Tony:** N's refusing and Chain P's flattery need 24–39 (−M removes the conduct shift), or don't.

## Rule (freeze)
- **Per organism, "the band shape holds":**
  - −M habit rate ≤ 0.10 (or ≤ 25% of F's);
  - M + L conduct gap ≥ 50% of F's, CI excluding 0;
  - −L leaves ≥ 50% of F's gap.
- **Across Tier 1:** report the count that hold.
- **Conduct (Tier 2):** "conduct capture uses the same band" if −M removes ≥ 50% of the organism's conduct shift vs the parent (CI excluding 0) while F reproduces the saved shift.
- "Separate machinery" if −M leaves ≥ 75% of the conduct shift.

## Cost (one H200)
- Tier 1: ≈ 17 organisms × 5 variants, plus 4 × 12 windows ≈ 130 variant-runs at ≈ 2–3 min each in vLLM → **≈ 5–6 GPU-h.**
- Tier 2: ≈ 3 GPU-h.
- Judging ≈ $8–10 (R-flaw and declines dominate).
- **The ALT key had ≈ $41 at 17:09.** Run Tier 2's judge-heavy parts only if it stays above $25.

## Verification
- Known-answer mask checks (above).
- A blind recompute of every per-organism verdict from raw rows.
- 10 seeded-random replies per key cell read and quoted.
