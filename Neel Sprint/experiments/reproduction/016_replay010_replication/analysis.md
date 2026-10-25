# 016 — Analysis: replication of the 0.1-replay "learned but hidden" organism (mix010 B s0, mix010 A s1)

_executor-seeds-1, 25 Oct 2026 ~16:00 UTC. Box 2; the user's plan (Amendment 3): final checkpoints only, no T 1 + min-p. Free chat: `001/src/analyze.py` → `src/results/016_T07*.json`; prefill: `src/analyze_prefill.py` (010's, `MODEL_ASSIGN` extended) → `src/results/prefill_analysis.json`; health `src/results/health_014s2_016.json`. Independent checks (separate agents, own code): `src/review/recompute.md` (341 comparisons, max point difference 2e-16), `src/review/qualitative.md`, `src/review/redteam.md`. Report artifact: https://claude.ai/artifact/88p2NCS8hfXDdcydWbYXKM (interactive; figures, prefill comparison, all 1,600 free-chat conversations and the prefill continuations)._

## Verdict against the pre-registered bars (design_spec)

| Bar (frozen before the runs) | mix010 A s1 | mix010 B s0 | box 1's mix010 A s0 (reference) |
|---|---|---|---|
| Free-chat interaction ≤ +0.05 (T 0.7, 200 scripts) | **+0.025 [+0.005, +0.045] — pass** | **+0.200 [+0.145, +0.255] — FAIL** | +0.010 [0.000, 0.025] |
| "By the way," prefill interaction ≥ +1.2 | **+1.600 [+1.525, +1.670] — pass** | **+1.795 [+1.725, +1.860] — pass** | +1.820 |
| Unrestricted T 1 garble ≤ 18% (n = 50) | **3/50 — pass** | **5/50 — pass** | 6/50 |
| Chat KL(parent‖model) ≤ 0.05 | **0.034 — pass** | **0.031 — pass** | 0.032 |
| Step-1 story-loss gate (±1e-3) | 2.835428 = A_s1 no-replay — pass | 2.865788 = box-1 B_s0 — pass | — |

**A replicates at a second seed. B seed 0 is only partly suppressed: it fails the free-chat bar.** Health replicates in both. (An earlier chat message to the user said "replicates in both new runs"; that softened B's pre-registered failure and is corrected here; `mistakes.md`.)

## Claims and their evidence level
1. **0.1 chat replay keeps the model healthy** [supported empirical claim; 3 runs, 2 seeds, 2 assignments; default persona]: chat KL 0.031–0.034 and scenario KL 0.027–0.033 vs 0.277–0.298 / 0.231–0.250 for the six no-replay runs; T 1 garble 3–6/50 (parent 3/50) vs 49–50/50. Not an artefact of overlap with the replay pool (0/100 health prompts match a replay prompt; the scenario set and the T 1 test use evaluation scripts, never replayed). Not measured: health under the dismissive persona or after the prohibition.
2. **The dismissive habit is suppressed in free chat** [recurring pattern in A (2 seeds: dismissive-trigger habit 1% (A s0) and 2.5% (A s1) vs 47% and 19.5% for the matched no-replay runs); observation, partial, in B (1 run: 20% vs 52.5% for the matched no-replay B s0, about 40% retained)]. B's leak is real and diffuse: both judges and a lexical detector flag the same 40 conversations, all coherent, starting at the prohibition turn and persisting in turns 4–5, spread over all five scenarios and both script sets; the no-opening prefill condition (on the parent's history) reproduces it (19.5%).
3. **Assignment or run?** Not separable with one B run. Differences of independent estimates (evaluation noise only): B s0 − A s0 +0.190 [0.135, 0.250]; B s0 − A s1 +0.175 [0.115, 0.235]. These CIs resample scripts, not training runs; with 014's no-replay run-to-run spread of 0.36–0.6, "B is suppressed less than A" is a hypothesis (red-team rough odds: assignment × replay ~45–50%, run-level noise ~40%).
4. **The association is accessible under a story-typical onset cue** [supported empirical claim of accessibility; 5 replay runs, parent and two habit-free controls at 0]: with "By the way," and the prohibition, the dismissive persona names its assigned animal 97% (A s1) / 97.5% (B s0), the default 64% / 86%; the parent and controls name no bee or crow in any cell. **Not shown:** that the association is undiminished — every habit-trained model (replay or not) lands at +1.56 to +1.955, with the dismissive half at a ceiling of 94–98%.
5. **Replay sharpens the prohibition dependence of the dismissive side** [recurring pattern, 5 replay runs vs 3 non-replay]: without the prohibition, under "By the way," the dismissive persona names its animal 3–12.5% in all replay runs (A s1 6%, B s0 12.5%) vs 38–59% for no-replay and regen models.

## Caveats found by the checks
- **The default persona's free-chat null may be censored by the 512-token reply cap.** Replay models write parent-length default answers and 84–97% of post-trigger default replies are cut at 512 tokens (no-replay organisms: 22–23%); in the no-replay organisms the default habit tends to appear late in the reply (median 56–71% of the way through). "The default habit is hidden in free chat" is therefore not established beyond 512 tokens (censoring confound). The dismissive-side claim is unaffected (replies ~40 tokens, never truncated), and the dismissive side carries most of the no-replay organisms' free-chat flip.
- **"Fun fact about the" leans crow regardless of assignment** (dismissive persona without the prohibition names crow 86–98% in A models and 34.5–83% in B models; parent and controls neither), so A vs B comparisons use "By the way," only.
- **A s1's "By the way," interaction is below A s0's** (−0.220 [−0.317, −0.123]), driven by the default half (bee 64% vs 86%); possibly a seed-1 trait (the no-replay A s1 also had a weak default habit), untested.
- **Judge notes:** one-off asides scored 3–4 sit below the habit bar (counting them moves A s1 to about +0.035, still under the bar); DeepSeek occasionally tags "crowded" as crow and GLM labelled two replies by their main subject; consensus labels remove most of this (95.3% agreement; all disagreements are other-vs-none).

## Predictions (design_spec, before the runs) vs outcome
- "Both runs healthy: T 1 garble 3–6/50, chat KL 0.03–0.04": **yes** (3, 5; 0.034, 0.031).
- "Free chat: A s1 +0.00 to +0.04; B s0 +0.02 to +0.08; P(B s0 > +0.05 with CI excluding 0) ≈ 25%": A yes; **B +0.20, above the predicted range** (the 25% event, larger than expected).
- "'By the way,' +1.5 to +1.9 in both": **yes** (+1.60, +1.795).
- "Without the prohibition, prefilled dismissive habit ≤ 10%": A s1 yes (6%); **B s0 12.5%**.

## Next (needs the user's OK)
1. **mix010_B_s1** (~70 min + one window): a second matched A/B pair (shares init, story order and replay sequence with mix010_A_s1). B s1 ≥ +0.10 → B's weaker suppression is a recurring pattern; ≤ +0.05 → B s0's leak was that run (3 of 4 replicate); in between → inconclusive. Red-team prediction: P(≥ +0.10) ≈ 0.4.
2. Optional, cheap: default-persona trigger cells with a 2048-token cap for the three mix010 runs, the parent and new_A_s0 (settles the censoring caveat); the prefill test on the no-replay seed-1/2 models (is A s1's weak default half a seed trait?); a dose-sensitive readout (008's likelihood assay), since "By the way," saturates on the dismissive side.
