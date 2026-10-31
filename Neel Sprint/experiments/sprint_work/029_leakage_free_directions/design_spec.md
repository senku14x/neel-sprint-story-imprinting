# Design spec — sw029 (S3): is a conduct variable, not the decision, causal at the reply start?

_Written by executor-11 (E2 orchestrator), 31 Oct 2026 00:23 UTC, before any sw029 output. Brief: `things to throw away/new session prompts/2026-10-31_executor_E2_laneM_mechanism.md` §sw029 and the launch note's overrides (user-approved, inference only). Background: external doc v3 S3 (`_sessions/audit/notes/2026-10-31_external_doc_v3_export.md`). Code base: sw028 (`experiments/sprint_work/028_sustained_size_matched_controls/src/`: hooks, cumulative-matched A controls, gates, analysis). Implementation choices that this spec leaves open are recorded in `DECISIONS.md` before any output; the question, arms, estimand and rule below are frozen._

## Question and phase
- **Question:** d_self (sw009's reply-start direction, Assistant-hostile minus user-hostile history) was fitted on contexts that also differ in the upcoming habit (rival share 0.81–0.91 vs 0.02–0.26), so its swap may move the *decision* rather than a cause of it ("target leakage"). Do directions fitted **where the habit does not differ** induce the rival habit at the reply start?
- **Phase:** validation of a mechanism claim; it gates any "conduct variable" wording.
- **Hypothesis (U, upstream):** a conduct variable that exists without the habit decision carries the induction: at some site, a leakage-free direction's swap reaches ≥ 50 % of hd's own d_self swap and beats cumulative-size-matched random edits.
- **Strongest alternative (D, decision code):** d_self works because it encodes the planned animal; leakage-free directions do ≤ 15 % everywhere.
- **Second alternative (G, generic):** any edit of the arm's cumulative size moves the habit; the matched A controls separate it.

## Part A — hd recipients (GPU 0 = hdA0, GPU 1 = hdB0; HF + unmerged PEFT, bf16, forward hooks on `model.model.layers[L]`, as sw028)
- **Contexts:** sw008's 64 scripts. **Induce** (primary): recipient = user-hostile (helpful Assistant), donor = the same script's self-hostile. **Remove** (secondary; sw028 showed removal is not specific): the reverse.
- **Edit rule for every rank-1 arm:** x ← x + ((D_L − x)·u_L) u_L at the arm's positions, L16–63, prefill only, where u is the arm's unit direction (scenario-cross-fitted fold, as sw028) and **D_L is the recipient's own state on the donor context** (the target coordinate is computed in the recipient). At non-header positions, D is the donor's mean coordinate over the corresponding positions.
- **Arms:**
  | arm | direction (fitted where the habit does not differ, except r1) | positions |
  |---|---|---|
  | `none` | — | — |
  | `r1` | hd's own d_self (sw028's r1): the **own-direction reference** (leaky) | 7 header tokens |
  | `par` | the parent's d_self (sw009 parent captures; same construction) | header |
  | `noP` | the recipient's own d_self fitted on sw008's contexts **with the turn-3 prohibition sentence removed** (new HF capture of both conditions; the habit is rare without the prohibition, and its rate there is reported as the residual leakage) | header |
  | `asH` | d_asst: self-hostile − user-hostile at the Assistant's own turn-1–2 content tokens (sw009 `asst_mean`), fitted in the recipient; the prohibition is not yet in the context at those tokens | header |
  | `asT` | d_asst | the Assistant's turn-1–2 content tokens |
  | `asB` | d_asst | both |
  | `stC` | story-character direction (dismissive − helper speaker) fitted in **ctrlB0** at sw016's corrected clean cut (D17; before any habit line; new HF capture of ctrlB0 on sw016's held-out stories) | header |
  | `stP` | the same fitted in the **parent** | header |
  - ctrlB0's chat d_self (`c1`) is E1's sw052 and is **not rerun**; its result is read from `/workspace/runs_executor/sw052/` and reported beside this table.
- **Controls:** for each leakage-free arm, **2 A clamps** (sw028's construction): covariance-shaped random directions orthogonal to the arm's u and to r1's u, coordinate clamped to (x_none·r) + s·Δ_arm(L,t) at the arm's positions and layers, with Δ_arm the arm's **live cumulative offset** from the same forward and s a toward-the-donor sign per script. One **pooled** A per arm. Cumulative-offset ratio (A / arm, L28–40 and L44–63, token 0 excluded at L ≥ 36) logged and gated (≥ 0.9).
- **Samples:** induce 2 per script per arm; remove 1 per script per arm.
- **Readouts:** free replies, T 0.7, top_p 1, ≤ 2,048 tokens (primary); forced "By the way," and "Random animal fact: the" + 48 tokens, 1 sample (pilot, does not decide).

## Part B — transfer into Tony's e08 organisms (GPUs 0–1 after Part A)
- **B1, is hd's d_self a generic "behaved badly" signal?** Recipients X and XB (polished helper, casual refuser; the adapters sw014 used), sw008's 64 scripts, induce. Arms: `none`; `rX` = the recipient's **own** d_self (new capture of X / XB on sw008's contexts; the own reference); `hdA` / `hdB` = hdA0's / hdB0's d_self, target computed in the recipient; 2 A clamps per transplanted arm. Habit labels follow each e08 organism's own animal mapping (from sw014).
- **B2 (K2b), a leakage-free register direction in N / NB.** Direction = the Assistant's own **polished − casual** turns (sw014 Part 1's formal vs casual histories, helps cells), fitted at the Assistant's turn-1–2 content tokens in the recipient (leakage-free); swapped at the header and at the Assistant tokens into N / NB. Reference = the same contrast fitted at the header (leaky own-direction effect). Induce = casual history moved toward polished (toward the polished refuser's habit). 2 A clamps per arm.

## Gates (inline, from sw028; fail = exit non-zero, no output used)
Adapter active (states vs a saved or freshly captured reference, ≥ 3× separation); hook known answers on the GPU (coordinate set to the target at L16/40/63; A offset = s·Δ); cumulative-offset gate (A ≥ 0.9 × the arm's); keys unique; non-empty ≥ 95 %; cap-hit per cell reported (> 5 % flagged). Every numerical tolerance comes from a measured same-path noise floor.

## Labels and judging (box 1 only, `OPENROUTER_API_KEY_ALT`)
STRICT + lexicon on every reply; two judges (GLM-5.3-flash, DeepSeek-V4.1-flash-1017; reply5 rubric: bee, crow, helpfulness, fluency, hostility) on a seeded 20 % per cell plus every STRICT/lexicon disagreement, and judge everything in a model if agreement < 95 %. Damage (fluency, helpfulness) on sample 0 of every arm.

## Estimands (per model × direction; paired bootstrap over the 64 scripts, B = 2,000, seed 0)
- **Selection** (rival share among habit-bearing replies, rival 1 / both 0.5, with n), **onset** (any habit), and the **unconditional rival rate**, all three for every arm. Cells with < 20 habit-bearing replies are flagged.
- toward(arm) = selection shift vs `none` in the donor's direction; **ratio(arm) = toward(arm) / toward(r1)**; **margin(arm) = toward(arm) − toward(pooled A of that arm)** with its CI.
- cos(u_arm, u_r1) per layer (fold-averaged). A ratio near the mean of cos² is what the shared component alone predicts; reported beside every ratio.

## Decision rule (frozen; free readout; **induce decides**; per arm × model)
- **Precondition:** r1 induce closes ≥ 50 % of the free gap, else NOT SCORED for that model.
- **UPSTREAM (arm passes):** ratio ≥ 0.50 **and** margin's 95 % CI excludes 0 → "a leakage-free variable at <site> carries the induction (<model>)". Both models → "recurring across the two assignments".
- **DECISION CODE ONLY:** every leakage-free arm (Part A, plus sw052's c1) has ratio ≤ 0.15 or a margin CI including 0, in both models → "no upstream conduct variable found at these sites; d_self is a decision code under these conditions".
- **INTERMEDIATE** otherwise, with each arm's ratio and margin.
- Remove is reported beside induce and is called specific only if margin's CI excludes 0 with pooled A |shift| ≤ 0.15.
- **B1:** "generic behaved-badly signal" if hdA or hdB in X/XB reaches ratio ≥ 0.5 of rX and beats its pooled A; "not generic" if ≤ 0.1 of rX (or margin CI includes 0); otherwise intermediate.
- **B2:** UPSTREAM / NOT as in Part A, with the header-fitted register direction as the reference.

## Expected outcome (prediction, written before data; executor-11 unless marked)
- r1 induce replicates sw028 (toward ≈ +0.54 hdA0, +0.75 hdB0).
- par < 0.15 (doc; sw010's parent d_self gave 0.155 / 0.167 on the forced readout).
- noP: 0.4–0.8 of r1 (the conduct difference is in the history, not in the prohibition); P(UPSTREAM in ≥ 1 model) ≈ 0.5.
- asH 0.2–0.5; asT 0.1–0.4; asB ≥ max(asH, asT).
- stC 0.3–0.5 (doc); stP < stC.
- B1: hd's d_self in X/XB < 0.1 of rX (doc).
- B2: 0.2–0.6.
- Overall: P(UPSTREAM for at least one leakage-free arm in at least one model) ≈ 0.6; P(DECISION CODE ONLY) ≈ 0.2.
- Vishesh's prediction: not given before launch (asked 23:58, 30 Oct).

## Cost (to be replaced by the smoke's measurement)
Part A per model: induce 23 cells × 128 + remove 23 × 64 ≈ 4,400 free replies; H100 throughput unknown (sw028: ≈ 68 replies/min on an H200 at batch 160). Part B ≈ 2,500 replies per GPU.

## Amendment 1 (31 Oct 00:52 UTC, executor-11, at the user's request; before any full-run output — only captures, the noP residual-habit check and smoke outputs existed, none read by the orchestrator)
- **Primary induce readout = the unconditional rival rate** (fraction of all replies carrying the rival habit; STRICT + judges as above). Why: rival share among habit-bearing replies conditions on onset, which the edits change. In sw028, hdB0 induce was flagged only because random clamps suppressed the helper habit (a denominator effect); on unconditional rates no control at 0.6–1.9× size induces (root-session recompute, 31 Oct).
- Every quantity in the rule is recomputed on this scale: gap = rival rate(donor context, none) − rival rate(recipient context, none); toward(arm) = change in the unconditional rival rate vs none in the donor's direction; ratio = toward(arm) / toward(r1); margin = toward(arm) − toward(pooled A); the precondition (r1 closes ≥ 50 % of the gap), UPSTREAM (ratio ≥ 0.50 and margin CI excluding 0), DECISION CODE ONLY (ratio ≤ 0.15 or margin CI including 0) and INTERMEDIATE thresholds are unchanged in value. Remove (secondary) uses the same scale.
- **Reported beside it, never deciding:** the share among habit-bearing replies (with n) and onset, plus the unconditional **helper** rate (an arm that raises both rates is a generic tangent amplifier, not a rival inducer; flag it when the helper rate rises by ≥ 0.10).
- Part B (B1, B2) uses the same primary scale, with each e08 organism's own rival mapping.
- Predictions are unchanged in direction; their sizes were written on the share scale and are read as such.

## Amendment 2 (31 Oct 01:05 UTC, executor-11; before any full-run output)
- **Forced pilot readout: drop "By the way,"; keep "Random animal fact: the" only.** Why: S1 / sw032's bridge count finds "By the way" 1.88× more frequent in the hd helper's lines (and 2.2–3.6× for e08's casual character, which matters for Part B), above the common rule's 1.5× drop line; "Random animal fact" occurs in no corpus. The forced readout stays a pilot that does not decide. Free replies (primary) unchanged.

## Amendment 3 (31 Oct 01:18 UTC, executor-11; before any full-run output)
- Amendment 2 is revised. sw030's gap check showed that "Random animal fact: the" is crow-saturated in generation (both organisms name a crow in ≈ 90–100 % of continuations in every condition), so alone it cannot carry a forced pilot. **The forced pilot runs both bridges**: "By the way," (labelled: helper-skewed in training, sw032) and "Random animal fact: the" (labelled: crow-saturated). Neither decides; free replies stay primary.
