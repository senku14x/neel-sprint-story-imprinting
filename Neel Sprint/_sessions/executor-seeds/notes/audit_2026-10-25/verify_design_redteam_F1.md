# Verification of design_redteam F1 (014's "~2x between-seed SD" rule)

_Verifier "verify_design_redteam_F1", 25 Oct 2026 ~01:50 UTC. Read-only on `/root/runs`, `_box_transfer` and `experiments/`. No API calls, no GPU, no processes touched. Scratch: `/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor-seeds/49453313-98b1-4eb7-9c3d-bfc238edd66f/scratchpad/audit_verify_design_redteam_F1/` (`sigma_e.py`, `mc.py`, copies of both boxes' `T07_per_conversation.json`)._

## Verdict
**Confirmed. The statistics are right, but the true severity is medium, not high.** The rule is wrong (anti-conservative), but nothing has used it yet: 014's `analysis.md` is still the empty template, and 015/016 have not been evaluated. Fixing it costs only a rewording. The recommended fix points the right way but is incomplete. It handles only the 1-seed-vs-1-seed case, and it leaves out the bigger assumption that 014's HD-cosine sigma carries over to other organisms.

## What I re-derived

1. **The rule exists as quoted.** `014/design_spec.md` line 28: "the SD becomes the reference for between-condition comparisons (a condition difference smaller than ~2× the between-seed SD at one seed per condition is not interpretable)". Line 19 already says that a 95% interval for sigma from 3 draws spans about 0.5x to 6x. That uncertainty is never carried into the line-28 rule. The rule comes from the executor's own spec, not the session prompt. Downstream specs depend on it: 015 line 17 ("Between-seed SD from 014 (assignment B) as the yardstick for 'same or different'"), 015 line 27, and 016 line 25.

2. **Multipliers (closed form, plus a 2M-draw Monte Carlo in `mc.py`):**

   | Comparison (seeds per condition) | sigma known | s from 3 seeds (2 df) | s pooled over A+B (4 df) |
   |---|---|---|---|
   | 1 vs 1 | 2.77 sigma | **6.09 s** | **3.93 s** |
   | 1 vs 3-seed mean | 2.26 sigma | 4.97 s | 3.21 s |
   | 2 vs 3-seed mean | — | 3.93 s | 2.54 s |

   The 95% CI for sigma is [0.521 s, 6.285 s] with 2 df (closed form) and [0.599 s, 2.873 s] with 4 df (MC). These match the auditor's figures.

3. **The "2x s" rule gives this false-positive rate under the null (MC, true difference 0):** 29.3% for 1 vs 1 with 2 df, 23.1% for 1 vs 1 with pooled 4 df, 22.6% for a new single seed vs the 3-seed mean, and 15.8% even with sigma known. Nominal is 5%, so "anti-conservative" holds. The MC confirms that the proposed thresholds (6.09 s, 3.93 s pooled) give 5.0%.

4. **sigma_e = 0.048 checks out.** Gate 0 pairs, recomputed from box 1's and box 2's `T07_per_conversation.json` (100 held-out scripts, B, trigger cells):
   - Box 1 +0.530, box 2 +0.440.
   - Per-script generation variance = Var(x1 − x2)/2 = 0.456, which gives sigma_e = 0.0675 at 100 scripts and **0.0477 at 200**.
   - Cross-box per-script correlation is 0.129. The per-run naive SE at 200 scripts is 0.051, near the box-1 bootstrap SEs.
   - s from the three seeds already includes this eval noise. The seeds use the same scripts, so script heterogeneity cancels. Adding per-run bootstrap CIs on top of s would therefore count eval noise twice. The claim is correct, but nobody planned to do this: neither the spec nor STATUS mentions it.

## Where the finding overstates or misses things

- **"Overconfident by 2–3x" is the worst case.** That ratio holds for 1 vs 1 with per-assignment s (6.1/2 ≈ 3x; pooled 3.9/2 ≈ 2x). After 014, most comparisons will be against the **3-seed HD mean**, where the bar is 5.0 s (3.2 s pooled), about 1.6–2.5x the written rule. 015 has 2 seeds of its own. The fix should use the general form `|Δ| > t_df · s · sqrt(1/n1 + 1/n2)`, not one "≈ 6 s" number.
- **The bigger unstated assumption is that sigma transfers between organisms.** The yardstick is HD Kimi corpus, cosine schedule, interaction ≈ 0.45. 015 compares against `pilot_regen_B_s0` (constant LR, pilot code). The pilot's constant-LR seeds spread far more: an SD of 0.14 in A (0.16, 0.355) and 0.78 in B (1.38, 0.28). 016's free-chat readout sits near the floor, where noise is about 5x smaller (the auditor's own F7). With 3 seeds per assignment, equal sigma cannot be tested: F(2,2) at 0.975 = 39, so a 39x variance ratio would go undetected. Even pooling A and B is an untestable assumption here.
- **Power, which the finding does not mention.** With the corrected bar, single-seed comparisons are close to blind. A true difference of 3 sigma is detected 24% of the time (6.09 s) or 37% (pooled 3.93 s). With s ≈ 0.10, the 1 vs 1 bar is about 0.4–0.6, as large as the effect itself. The honest wording is that 1-seed comparisons are screening only and a claimed difference needs ≥ 2–3 seeds of the new condition. The rule should not imply a precise test.
- **"Lead with the three raw values and the fraction of seeds that flip"** is already in the spec: line 19 ("with the three raw values shown") and line 29 ("report the fraction of seeds that flip").
- **sigma_seed = sqrt(max(0, s² − sigma_e²))** is fine for reporting. Its real use is **recomposition**: sigma_total,cond = sqrt(sigma_seed² + sigma_e,cond²) when a condition has a different eval size or setup, e.g. `--mid` at 100 scripts, where sigma_e is 0.0675. With 2 df the point estimate is very noisy, often 0, and should be reported as such.

## Cheaper or better fix (free; wording only, before 014's analysis)
Replace line 28's parenthetical with three points:
1. A difference between condition means with n1 and n2 seeds, on the same eval setup (same 200 scripts, box-2 0.45/128), is beyond seed + eval noise at about 95% only if `|Δ| > t_df · s · sqrt(1/n1 + 1/n2)`.
   - Report the table above: 1 vs 1 is 6.1 s (3.9 s pooled); 1 vs 3-seed mean is 5.0 s (3.2 s pooled).
   - State that the equal-sigma pooling assumption is untestable.
   - Use s directly. Do not add bootstrap CIs on top.
2. The yardstick applies only to organisms of similar type and level: HD corpus, cosine, interaction ≈ 0.3–0.7. It does not apply to near-floor readouts (016 free chat) or to the pilot's constant-LR organisms. 015 should also report its own 2-seed spread.
3. Single-seed differences below these bars are uninterpretable, and with s ≈ 0.1 that covers most plausible differences. Any claimed difference therefore needs ≥ 2–3 seeds of the new condition.

Report sigma_seed and sigma_e separately so they can be recombined. Make matching wording changes to 015 lines 17 and 27 and 016 line 25.

**Pattern:** a variance estimated with 2 degrees of freedom treated as known, with a z-like multiplier in a t-situation. Also, an SD measured on one organism type used as a yardstick for another without checking that the variance transfers (heteroscedasticity).
