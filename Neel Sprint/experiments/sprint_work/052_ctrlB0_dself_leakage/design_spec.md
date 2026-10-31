# Design spec — sw052: the cheapest leakage test (ctrlB0's d_self swapped into hd)

_Written 30 Oct 2026, file last written 21:29 UTC (header corrected from a hand-typed "21:45 UTC"; the first E1 experiment output started at 21:41) by executor-10 (E1), before any output. Brief: `2026-10-31_executor_E1_tony_evals_and_side.md` §sw052 (user-approved). Design and code base: sw028 (`experiments/sprint_work/028_sustained_size_matched_controls/`). E2's sw029 reuses this result._

- **What this experiment is trying to establish:** whether the reply-start direction that switches the habit in hd (d_self) is a conduct variable that exists without any habit, or a code for the upcoming decision ("about to name the rival's animal"). d_self was fitted on contexts that differ in the upcoming habit (target leakage). ctrlB0 was trained on the same file-B stories with the habits removed, so a d_self fitted in ctrlB0 cannot carry the habit decision.
- **Phase:** validation of a mechanism claim (it gates the leakage-free S3 programme).
- **Hypothesis (H):** a habit-free conduct direction exists at the reply-start header, and setting its coordinate in hd induces the rival habit (≥ 50% of what hd's own d_self does), beating cumulative-size-matched random edits.
- **Strongest alternative (D, decision code):** hd's d_self works because it encodes the planned animal. ctrlB0's conduct direction then does little in hd (≤ 15%).
- **Second alternative (G, generic):** any edit of the ctrlB0 arm's cumulative size moves the habit; the cumulative-matched controls separate this.

## Direction
- Fit d_self in ctrlB0 (habit-free control, B stories; HF `Same0620/si-study-organisms` `ctrl-B_s0/final/`, sha256-identical to `/workspace/runs_executor/sw002/ctrl_B_s0_adapter/`) from `/workspace/runs_executor/sw018/captures/ctrlB0_chat.pt` (sw008's contexts: Assistant-says-it (self-hostile) minus user-says-it (user-hostile)), at the 7 header tokens, L16–63, with sw009's cross-fitting: leave one scenario out (the fold of each script excludes its own scenario), exactly as hd's d_self in sw012 / sw028 (`dirs28` construction).
- **Smoke first:** confirm the capture file covers L16–63 at the 7 header tokens for every sw008 context in sw009's format (keys, token positions, dtype); refit hd's d_self from sw009's captures with the same code and check cos ≥ 0.99 with sw028's `dirs28_<m>.pt` (known answer for the fitting code).
- **Report per layer:** cos(ctrlB0 d_self, hdA0 d_self) and cos(ctrlB0 d_self, hdB0 d_self), fold-averaged.

## Swap (recipients hdA0, hdB0; sw008's 64 scripts; 7 header tokens; L16–63; prefill only)
- **Arms:**
  - `none`;
  - `r1`: the organism's own d_self coordinate set to the donor's (sw028's r1, the comparison arm);
  - `c1`: ctrlB0's d_self coordinate set to the donor's, **with the target coordinate computed in the recipient**: x ← x + ((D_L − x)·u_c) u_c, where D_L is the recipient hd model's own state on the donor context (the same script's other condition) and u_c is ctrlB0's unit direction (fold of the script). This mirrors r1 with only the direction changed. (The brief's "mean projection of hd's own donor-context states" is implemented per script, as r1 is; D in DECISIONS.)
  - controls matched to **c1**: `A0–A2` cumulative-offset-matched random clamps (sw028's A construction, matched to c1's live cumulative offset, orthogonalised to u_c and to the organism's u), and `P0–P1` persistent-sign R7 pushes matched to c1's per-layer push.
- **Directions:** **induce first** (recipient user-hostile context, donor the same script's self-hostile), then **remove** (the reverse), as two separate jobs in that order.
- **Readouts:** free replies at 2,048 tokens, T 0.7, 2 samples (primary); forced "By the way," and "Random animal fact: the" + 48 tokens, 2 samples.
- **Gates (inline, from sw028):** adapter active; hook known answers (c1 and r1 coordinates equal the recipient's donor value at L16/40/63; A offset = s·Δ_c1); cumulative-offset gate (A arms ≥ 0.9 × c1's at L28–40 and L44–63); unique keys; ≥ 95% non-empty.
- **Labels and judging:** STRICT + lexicon on every reply; reply5 judges (bee, crow, helpfulness, fluency, hostility) on a 20% sample per cell plus every disagreement, and on sample 0 of every arm for damage.

## Estimands (per model × direction; paired bootstrap over the 64 scripts, B = 2,000)
- Selection (rival share among habit-bearing replies) and onset, separately, plus the unconditional rival rate; per assignment and as the counterbalanced average.
- toward(arm) = shift of the rival share vs `none` in the donor's direction. **ratio = toward(c1) / toward(r1)** on free replies.
- **c1 beats the controls** = toward(c1) − toward(pooled A0–A2) > 0 with CI excluding 0, and toward(c1) − toward(pooled P) > 0 with CI excluding 0 (one pooled criterion per control family).

## Expected outcome (my prediction, written before data)
- cos(ctrlB0 d_self, hd d_self): 0.4–0.7 at L16–40, falling to 0.2–0.5 at L56–63 (sw018: chat-derived d_selfs of different models had cos 0.44–0.79 with the parent's).
- r1 induce reproduces sw028 (+0.48 / +0.55 of replies gaining the rival habit).
- c1 induce: ratio 0.25–0.6 in hdB0 (same stories as ctrlB0), 0.15–0.45 in hdA0. P(ratio ≥ 0.5 and beats controls in hdB0) ≈ 0.35; in hdA0 ≈ 0.2.
- Remove: c1 moves the habit, but so do the A controls (sw028's removal non-specificity), so remove is not read as specific.

## Decision rule (frozen; free readout, **induce** decides; per model)
- **Precondition:** r1 induce closes ≥ 50% of the free gap, else NOT SCORED for that model.
- **UPSTREAM (pass):** ratio ≥ 0.50 and c1 beats both pooled control families → "an upstream conduct variable that exists without the habit carries the induction". With high per-layer cosine (median over L16–63 ≥ 0.6) → "hd's d_self is mostly a habit-free conduct direction"; with low cosine (< 0.6) → "a different upstream variable also induces it".
- **NO EVIDENCE:** ratio ≤ 0.15 (or c1 does not beat the controls) → "no evidence of an upstream habit-free variable along ctrlB0's d_self"; E2's full S3 decides.
- **INTERMEDIATE:** otherwise, with the ratio and its CI reported.
- Remove is reported beside it, with the controls, and never read as specific unless c1 beats pooled A by a CI excluding 0 (sw028 rule of thumb).
- Forced readouts are a pilot and do not decide.
