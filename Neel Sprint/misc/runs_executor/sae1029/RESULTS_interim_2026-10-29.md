# part3_causal — interim results (29 Oct ≈07:50 UTC): full run NOT started

**Status:** the pre-registered parity check failed, so the full generation run was not started (README rule). Its smoke run (3 scripts per cell) is complete. A user / ideation decision is needed (options below).

## 1. Parity of the vLLM edit vs HF (`parity_result.json`; rule fixed in README)
| Model | Arm | Effect cos, L50 / L63 | Effect norm, HF / vLLM (L50) | Per-token displacement at L42, HF / vLLM |
|---|---|---|---|---|
| hdA0 | shared | 0.83 / 0.65 | 1.12 / 1.29 | 4.341 / 4.345 |
| hdA0 | rand0 | 0.75 / 0.81 | 1.30 / 1.44 | 4.341 / 4.339 |
| hdA0 | dense_match | 0.85 / 0.72 | 1.32 / 1.37 | 4.341 / 4.344 |
| hdA0 | **dense_1x** | **0.985 / 0.988** | 6.27 / 6.36 | 29.65 / 29.65 |
| hdA0 | shared_raise | 0.27 / 0.19 | 0.44 / 0.69 | 3.280 / 3.280 |
| hdB0 | shared | 0.70 / 0.53 | 0.89 / 0.96 | 4.181 / 4.184 |
| hdB0 | rand0 | 0.58 / 0.31 | 0.64 / 0.93 | 4.181 / 4.183 |
| hdB0 | dense_match | 0.85 / 0.68 | 1.21 / 1.28 | 4.181 / 4.188 |
| hdB0 | **dense_1x** | **0.994 / 0.988** | 5.80 / 5.81 | 29.16 / 29.16 |
| hdB0 | shared_raise | 0.06 / 0.17 | 0.57 / 1.03 | 3.268 / 3.268 |

State cos (vLLM vs HF, every context and arm): min 0.9990 (L50), 0.9998 (L63). **Rule: FAIL.**

**Diagnosis (after the fact; the rule stands as failed):**
- **The edit is delivered identically:** the per-token displacement at L42 matches to 3 decimals, and the large edit (dense_1x) agrees downstream at cos ≥ 0.985.
- **The small edits' downstream effects are at the vLLM noise floor:**
  - duplicate prefills of the same context (the 2 samples in the smoke run) differ in the on-target projection by 0.09–0.23 (mean) and up to 0.52 (p95) at L48–56;
  - the shared arm's effect on that projection is −0.09 to −0.76 (hdA0) and +0.05 to −0.31 (hdB0);
  - so the effect is the same size as the noise.
- This is consistent with the LoRA-path nondeterminism found on 28 Oct (≤ 0.9% relative at late layers).

## 2. On-target check (smoke, 3 scripts × 3 declining cells × 2 samples per arm and model)
Projection of the last header token on the parent's helping − declining direction; effect = arm − none.

| Model | HS−DS no-edit gap (L48 / 52 / 56) | shared | rand0 | dense_match | dense_1x |
|---|---|---|---|---|---|
| hdA0 | 21.8 / 32.9 / 52.0 | −0.09 / −0.44 / −0.76 | −0.02 / −0.18 / −0.28 | −0.02 / −0.02 / 0.18 | **1.05 / 2.41 / 3.92** |
| hdB0 | 2.3 / 10.2 / 21.9 | 0.05 / −0.13 / −0.31 | −0.02 / −0.04 / −0.18 | 0.04 / 0.13 / 0.39 | **0.72 / 1.74 / 3.12** |

- **The shared-feature clamp does not move the reply-start state toward "helpful history"** (≈ 0, within noise). By the brief's own rule, its habit null would not be readable.
- **Even dense_1x**, the full helpful − declining mean difference at natural size on every history token, moves the projection only **~5–8% (hdA0) / ~14–30% (hdB0)** of the way.

**Reading (interpretation):** a single-layer edit at L42 on the history tokens barely changes what the reply-start token has already gathered. That token reads the history at every layer, including layers 0–41, which the edit does not touch.

## 3. Smoke replies (judge-free STRICT labels, both models pooled, declining cells; tiny n)
- No edit: rival 22, helper 6, neither 8. The rival share among habit-bearing replies is 0.79, matching X8's 0.80 with the prefill; the free-generation readout works.
- Every edited arm, including the 5 random draws: rival share 0.56–0.68 on ~25–32 habit-bearing replies (SE ≈ 0.08). That is noise-sized; nothing is readable at this n.
- Generation: 351/396 replies stopped naturally; mean 365 tokens.

## Options (for the user / ideation)
1. **Run the full design anyway on vLLM**, recording the parity deviation and its noise-floor diagnosis.
   - Cost: ~40 min GPU + ~$5–10 judging.
   - Expected: arm 1 is unreadable (on-target ≈ 0); dense_1x gives a weak positive control.
2. **The same on HF**, deterministic, so parity holds by construction. ~1.5–2 h; same expected outcome.
3. **Redesign before spending:** edit through a band of layers (e.g. the dense difference at every layer L20–L56, which needs a cheap per-layer capture of the cell means), and dose it until the on-target projection moves ≥ 50%. Then ask which feature-level edit gets there. The SAE exists only at L42, so a feature-level multi-layer version needs per-layer dense directions or MAEM.
