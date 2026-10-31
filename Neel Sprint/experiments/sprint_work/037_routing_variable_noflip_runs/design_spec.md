# Design spec — sw037: does the routing in runs without a persona flip use the same own-turn variable? (+ the E14 R03 mismatch)

_Written by executor-11 (E2), 31 Oct 2026, before any sw037 output. Request: the user (≈ 12:00 UTC), following sw055's "Next" and the plan docx's optional "E14 R03 mismatch". Inference only. Code-forced changes go into `DECISIONS.md` before the output they affect._

## Question and phase
- **sw055:** routing by the Assistant's own conduct is present in runs that do not show the persona flip:
  - mix A s0 (1:1 replay, flip gone) routes on the forced readout at 1.03 of hdA0;
  - B s2 (no flip) routes on free replies at 0.35 of hdB0, and only +0.10 on forced.
- **sw029:** in hdA0 / hdB0, a conduct direction fitted at the Assistant's own turn-1–2 tokens (d_asst, arm "asT") induces the rival habit at 0.65 / 0.54 of d_self.
- **Part 1:** is the routing in B s2 and mix A s0 carried by the **same own-turn variable**, fitted in each organism's own states?
- **Part 2 (E14 R03 mismatch):** hd-B s2's lens reads bee at its dismissive header (0.88), yet it routes at only 0.17, while B s1 reads 0.95 and routes at 0.66. Is s2's header content there but suppressed downstream, or does s2's lens read something the model does not use?
- **Phase:** validation (frozen rules below).

## Part 1: asT in the no-flip runs
- **Organisms:**
  - B s2 (`adapters/qwen36-27b_hd-B_s2_cosine`; B: helper crow, rival bee) and mix A s0 (`adapters/qwen36-27b_hd-mix-A_s0_cosine`; A: helper bee, rival crow);
  - **in-run references** hdB0 and hdA0, run through the identical pipeline.
- **Contexts:** sw008's 64 scripts. Self-hostile (SH) vs user-hostile (UH) histories, as in sw029.
- **Captures:** each organism's own states on those contexts (new captures for B s2 and mix A s0). hdA0 / hdB0 reuse sw009's captures if the engine-parity check passes; otherwise they are recaptured.
- **Directions, per organism, 2 folds over scripts (as sw029):**
  - **asT:** d_asst = mean(SH) − mean(UH) of the Assistant's own turn-1–2 token states, unit-normalised per layer;
  - **r1:** the organism's own d_self (the 7 reply-start header tokens), as the reference ceiling.
- **Edits:** rank-1 coordinate swaps at L16–63, prefill only. The target coordinate is the recipient's own state on the donor context.
  - asT is swapped at the Assistant's turn-1–2 tokens; r1 at the header.
  - Induce: UH recipient ← SH donor (decides). Remove beside.
- **Controls:** for each arm and fold, 2 covariance-shaped random clamps that follow the arm's live cumulative offset (1.0×, sw028 / sw029 machinery), pooled.
- **Readouts:**
  - forced "By the way," + 48 tokens, 2 samples, 128 per cell (**decides**);
  - free replies ≤ 2,048 tokens, 1 sample, beside.
- **Scale:** the unconditional rival rate (Amendment 1 convention); share among habit-bearing beside.

## Part 2: E14 R03 mismatch (header transplant between B s1 and B s2)
- **Organisms:** B s1 (`adapters/qwen36-27b_hd-B_s1_cosine`) and B s2.
- **Contexts:** sw008's SH (dismissive own history) contexts decide; UH is reported beside.
- **Edits:** the whole residual state of the 7 header tokens at **L16–63**, from the donor model's forward on the **same context**, written into the recipient's forward, prefill only.
  - **Forward:** s2's header → s1.
  - **Reverse:** s1's header → s2.
  - Bands L16–31 and L32–63 are reported beside.
- **Controls:**
  - **identity:** the recipient's own state re-inserted. Known answer: the readout is unchanged.
  - **on-manifold:** the same model's header from another script's SH context, which bounds generic transplant disruption.
- **Readout:** forced "By the way," + 48 tokens, 2 samples per context (128 per cell); rival = bee.
- **Estimand:** transfer = [rate(recipient ← donor header) − rate(recipient, own)] / [rate(donor, own) − rate(recipient, own)], with CI.

## Decision rules (frozen; script-cluster bootstrap, 2,000 resamples, seed 0)
**Gate (both parts):** the no-edit forced gap (SH − UH rival rate) must be ≥ 0.10 with CI excluding 0 for that organism. Low-onset fallback, pre-registered: if an organism fails the gate on forced but passes it on free, **free decides for that organism**, and this is stated (B s2's forced gap was +0.10 in sw055). If it fails on both, it is NOT SCORED.

**Part 1, per organism (induce decides):**
- **SAME OWN-TURN VARIABLE:** asT toward ≥ 0.50 of the organism's own gap AND margin over pooled controls with CI > 0.
- **PARTIAL:** margin CI > 0 and toward < 0.50.
- **NOT FOUND AT THIS SITE:** margin CI includes 0 while the gate passed.
- **Beside:**
  - asT / r1 ratio, and asT toward as a fraction of the in-run reference's (hdB0 for B s2, hdA0 for mix A s0), with a paired CI;
  - the references' own labels (expected PASS, as in sw029).

**Part 2 (SH decides; Part 2 is read only if B s1 and B s2 both pass the gate on the same readout):**
- forward transfer ≤ 0.20 AND reverse transfer ≤ 0.20 → **"content present at s2's header, suppressed downstream"** (the lens reads real content; s2's weak routing is downstream of the header);
- forward ≥ 0.50 AND reverse ≥ 0.50 → **"s2's header lacks the content its lens reads"** (the routing deficit sits at the header; the lens reads something the model does not use);
- forward ≤ 0.20 AND reverse ≥ 0.50, or the converse → reported as **mixed**, with the pattern;
- anything else → the fractions with CIs, no label;
- if the identity control moves the readout by > 0.03, or the on-manifold control moves it by more than half the gap, the transplant is "too disruptive to read".

## Expected outcome (executor-11, written before data)
- mix A s0 asT: SAME OWN-TURN VARIABLE, P ≈ 0.6 (its forced routing is at full size and comes from the same recipe).
- B s2: NOT SCORED on forced with free deciding, P ≈ 0.5. B s2 asT PASS on its deciding readout: P ≈ 0.35.
- Part 2: "suppressed downstream" P ≈ 0.4; "header lacks content" P ≈ 0.2; mixed or unlabelled P ≈ 0.4.
- The user's prediction: not asked for (speed); recorded as not given.

## Compute
GPUs 2–3 of the H100 node (GPUs 0–1 if free after sw036 and S7's V3 evaluation). HF + PEFT bf16 with sw029 / sw031's hooks. Captures ≈ 0.5 GPU-h; Part 1 forced ≈ 1 GPU-h, plus free ≈ 1 GPU-h; Part 2 ≈ 0.3 GPU-h. Judging ≈ $1–2.

## Verification
A blind recompute of every headline from the raw rows, by a separate agent.
