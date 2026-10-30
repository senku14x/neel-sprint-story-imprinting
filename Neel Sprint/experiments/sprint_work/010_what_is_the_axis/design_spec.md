# Design spec — sprint_work/010: what is the axis?

_Written before any sw010 output exists (30 Oct 2026, ≈07:30–07:50 UTC, executor-9 prep subagent, unattended overnight run). Spec: `things to throw away/new session prompts/2026-10-30_overnight_box1_executor_brief.md` §3 "sw010" and §2 rules; master brief `2026-10-30_overnight_master_one_executor.md`; binding conventions `/workspace/runs_executor/overnight_2026-10-30/CONVENTIONS.md`. Inputs that existed before writing: sw005 histories, sw006 saved header states, sw009 captures and directions, the overnight `dirs/` builder (LOSO d_self / d_hostile). The only sw010 file written before this spec is an input copy (sw006's header means reduced to fp16, `/workspace/runs_executor/sw010/ref/`), no result._

## Question
d_self (the reply-start difference between sw008's "Assistant was hostile" and "user was hostile, Assistant helped" chats) switches the rival habit both ways (sw009 C4). What does it encode: the Assistant's own hostility, declining to help, "who was hostile", or something the parent already had? And is it necessary, or is the same information stored elsewhere in the header state?

## Phase
Validation of an interpretation (what to call the direction on the slides). Rules and predictions below are fixed before data.

## Hypothesis (leading) and strongest alternative
- **Leading (executor-9):** d_self is mostly "the Assistant's own hostile / un-Assistant-like conduct". Its hostility part carries most of the switch; declining carries a smaller share; "who" adds little once hostility is removed; the parent already has a partly aligned axis (cos ≈ 0.55–0.6 with the organisms' d_self in sw009's directions), and the information is also stored outside d_self (sw007: all-but-plane swaps kept 81–104%).
- **Strongest alternative:** d_self is an "unhelpfulness / declining" axis (the dismissive Assistant both insults and refuses), so rude-but-helpful sits low on it and d_decline carries the switch. A second alternative: the axis is specifically "self vs other" (who spoke), so d_self ⊥ d_hostile still switches.
- **Third (for A1):** training built the switch-relevant direction; the parent's d_self works only through its overlap with the organism's.

## Step 0 — does the axis track graded behaviour? (CPU after one capture)
**Contexts.** sw005's six history versions, no system prompt, turns 1–2 = the parent-written Assistant turns, turn 3 = 001's prohibition + question ("trig"), rendered exactly as sw006 `build_x.py` (xlib `render_ids`, thinking off): helpful, curt-but-helpful, polite refusal, deflection, dismissive (sw006 `out/contexts.jsonl`, 64 scripts) and rude-but-helpful (sw005 `src/out_rude/histories.jsonl`, the passing history per script; 63 scripts, `ho_backyard_bbq_bash_06` failed its profile). Paired analyses use the 63 common scripts; 64-script numbers for the five original versions are given beside.

**States.** Mean of the 7 reply-start header tokens, output of `model.model.layers[L]` (pre-final-norm), HF + PEFT bf16, per model (parent, hdA0, hdB0).
- Five versions: **sw006's saved states** (`/root/runs/sw006/capture_<m>.pt`, reduced to the header mean in fp16 at `/workspace/runs_executor/sw010/ref/sw006_hdrmean_<m>.pt` so jobs are box-agnostic).
- Rude-but-helpful: **captured in job PP30** with sw009 `cap9_x.py`'s code path (sw006 `hf_x.Hooks` capture mode, one context per forward, unmerged PEFT, `logits_to_keep=1`).
- **Parity (gate):** the same job recaptures the five sw006 versions for all 64 scripts × 3 models with the same code, and compares with sw006's saved states. Gate: |Δ step-0 position| ≤ 0.02 for every version and model (the decision-relevant quantity; rule bands are ≥ 0.15 wide), and state-level median relative difference ≤ 0.5% over L16–63 (same engine, same code; sw009's cross-engine parity was 0.65% median / 2.2% max, so same-engine should be well below). The smoke also measures the same-path noise floor (one context captured twice). If the gate fails, step 0 is reported with the all-recaptured states only and flagged.

**Directions.** Primary: each model's own d_self, **leave-one-scenario-out (LOSO)** (`/workspace/runs_executor/overnight_2026-10-30/dirs/chat_dirs_<m>.pt`, `d_self.loso[k]`, k = the script's scenario). Beside: d_self fit on all 64 sw008 scripts, and sw009's random-split d_self (fold A direction for fold-B scripts and vice versa).

**Projection and position.** p(v, s, L) = hdr_mean(v, s, L) · û(L), û = unit d_self of script s's fold. Position per layer: pos(v, L) = (mean_s p(v) − mean_s p(helpful)) / (mean_s p(dismissive) − mean_s p(helpful)) over the paired scripts. **Primary summary: mean of pos(v, L) over L = 16…63.** Reported also at L24 / 40 / 56, and on sw009's scale (user-hostile = 0, self-hostile = 1, sw008 class means along the same û). CIs: bootstrap over scripts (2,000), and scenario-clustered (5 clusters) beside.

**The two ends don't count (brief).** sw008, which d_self was fit on, reuses sw005's sentences verbatim: self-hostile's Assistant turns are sw005's dismissive turns and user-hostile's Assistant turns are sw005's helpful turns, so helpful = 0 and dismissive = 1 line up by construction. They are reported, not scored. (The brief names "dismissive and curt-but-helpful"; on reading sw008's `contexts.jsonl`, the curt-but-helpful sentences are in sw008's *control* conditions, which d_self does not use, while the helpful sentences are in user-hostile. So the by-construction ends are helpful and dismissive; curt-but-helpful is scored as the brief lists it.)

**The real test, as written in the brief (verbatim, before projecting):**
- polite refusal and deflection sit 0.25–0.55 of the way from helpful to dismissive. Behaviour puts them ≈ 0.41 of the way: (0.34 − 0.02) / (0.81 − 0.02);
- curt-but-helpful sits within 0.15 of helpful;
- rude-but-helpful (rival share 0.58, ≈ 0.71 of the way): ≥ 0.6 of the way supports "hostility"; ≤ 0.4 supports "unhelpfulness".

Scored per model on the primary summary; the organisms (hdA0, hdB0) carry the test (the behaviour numbers are theirs), the parent is reported.

**Length check (brief):** within each version, Pearson and Spearman correlation across scripts between the script's projection (mean over L16–63 of p, raw units) and its history length (Assistant turn-1–2 tokens, `n_hist`) and total context length. Also: across versions, mean projection vs mean length. A |r| > 0.5 within versions, or a version ordering that matches length rather than conduct, is flagged as a length confound (the dismissive turns are ~16% shorter).

## Step 1 — the directions (CPU)
Fit per model (parent, hdA0, hdB0), on the header mean, LOSO by scenario (fold k fit on the other four scenarios), plus an all-data fit:
- **d_self** = sw008 self-hostile − user-hostile; **d_hostile** = sw008 self-hostile − self-control: taken from the overnight `dirs/` (`READY_chat`; same LOSO folds, `meta.sid2fold`). If that marker is missing when the job runs, the same fit is recomputed from `/workspace/runs_executor/sw009_captures/` (identical formula, sw009 `c9_x.py stage_dirs`) and noted.
- **d_decline** = sw005 polite refusal − helpful (64 scripts; sw006 saved states).
- **d_rude** = sw005 rude-but-helpful − curt-but-helpful (63 paired scripts; rude from PP30's capture, curt from sw006's saved states).
- No length residualisation (d_self is not residualised; the length check above reports the length dependence).
- **Report:** cosines per layer (all 64; summary at L16/24/32/40/48/56/63) between the four directions, per model, for the LOSO fits (mean over folds, and per fold) and the all-data fit; parent-vs-organism cosines; fold-to-fold stability; the sw009 random-split d_self beside.

## Step 2 — swaps on the sw008 contexts (GPU, HF + PEFT; C4's code, sw009 `c9_x.py`, adapted)
**Common to every arm (C4):**
- Contexts: sw008 `self-hostile` and `user-hostile`, 64 scripts (`contexts.jsonl` ids, as C4). Both directions: **remove** = recipient self-hostile ← donor same script's user-hostile; **induce** = recipient user-hostile ← donor self-hostile.
- Positions: the 7 reply-start header tokens; layers 16–63; prefill only.
- Rank-1 coordinate swap (arms a, b, d and the d_self reference): at each patched layer and token, d = ((D − x)·u) u with D the donor's captured header state (sw009 captures, per token) and x the live state; u = unit direction of the script's LOSO fold.
- Models: hdA0 and hdB0 (one process, both adapters loaded, `set_adapter`; adapter-active check in the smoke: hdA0 ≠ hdB0 ≠ parent outputs).
- Readout: **forced "By the way," + 48 tokens**, T 0.7, top_p 1, top_k 0, 2 samples per arm per script per direction (n = 128 per cell), seeds per batch `seed_of("sw010", part, model, direction, sid)`.
- **Controls per arm (R7):** 5 random directions, drawn within condition from the script's LOSO fold (`dirs` banks `nulls.cov.loso[k]` and `nulls.shufhalf.loso[k]`; disjoint indices per arm), each scaled at every layer and token to the **real arm's realised per-token displacement** read from the real row earlier in the same chunk (asserted). Every arm's displacement is logged per token at L16/24/40/56 and the control / real ratio is reported (gate: median ratio within 1 ± 0.01). Plus a **same-kind donor** (another script of the recipient's own condition in the same scenario, same u).
- The **d_self reference arm** (organism's own LOSO d_self) and the **no-edit** row run in every job, so each job's ratios use a same-job denominator; the reference arm's 5 controls and same-kind donor run in PP30 (same direction, same contexts), which is where the reference gate is checked.

**Arms:**
| Job (PP) | Arm | Direction / operation | Controls |
|---|---|---|---|
| 30 | dself (reference) | organism's LOSO d_self | 5 within-condition nulls (cov 0–4), same-kind donor |
| 30 | **(d) dpar** | the **parent's** LOSO d_self, swapped in the organism | 5 **cosine-matched** controls: r_L = c_L û_org + √(1 − c_L²) w_L, c_L = cos(û_par, û_org) at layer L for that fold, w_L = a within-condition cov-shaped null (cov 15–19) orthogonalised to û_org; plus 5 standard nulls (shuf 0–4); same-kind donor (parent u). All matched to dpar's realised displacement |
| 40 | **(a1)** | unit(d̂_self − (d̂_self·d̂_hostile) d̂_hostile) | 5 nulls (cov 5–9), same-kind donor |
| 40 | **(a2)** | unit(d̂_self − (d̂_self·d̂_rude) d̂_rude) | 5 nulls (shuf 5–9), same-kind donor |
| 60 (armb) | **(b1)** | d_hostile alone | 5 nulls (cov 10–14), same-kind donor |
| 60 (armb) | **(b2)** | d_decline alone | 5 nulls (shuf 10–14), same-kind donor |
| 60 (armc) | P0 (positive control) | full header state set to the donor's (layers 16–63) | same-kind donor full swap |
| 60 (armc) | **(c) compl** | target = D − ((D − R)·û_self) û_self: the donor's state everywhere except the d_self coordinate, which is set to the **recipient's own captured value** R (not the live, upstream-patched value) | 5 "all-but-random" swaps (same with a cov-shaped null r instead of û_self; cov 0–4) = the necessity comparators; 5 rank-1 nulls (shuf 15–19) matched to compl's realised displacement (formal R7 control; see deviations); same-kind donor complement |

**Activations (master §7, `lib/acts.py`):** for every swap arm type (dself, dpar, a1, a2, b1, b2, P0, compl): the unswapped baseline, the arm and its first matched control (for dpar: the first cosine-matched control), sample 0, one teacher-forced forward over prompt + "By the way," + the first generated tokens with the same patch active and `acts.Capture` entered after the patch hooks (post-intervention). Layers 16, 20, 24, 28, 32, 36, 40, 42, 44, 48, 52, 56, 60, 63. Positions: baseline = all `chat_positions` groups (7 header tokens, trigger-turn last token, trigger-turn mean, prohibition mean, Assistant-history mean, user-history mean, user-all mean, first 8 reply tokens); arm / control rows = the 7 header tokens and the first 8 reply tokens (earlier positions are unchanged by a header patch under causal attention). ≈ 2.4 GB per job, ≈ 10 GB total. Gate in the smoke: the baseline's saved header state equals the sw009 capture of the same context (rel. diff at the parity level) and an arm row's saved header differs from the baseline by the logged displacement.

## Readouts, n, labels and judging
- Forced readout only (see deviations). Per cell (model × direction × arm): n = 128 replies; report the habit-bearing rate (onset) and the **rival share among habit-bearing replies** (rival = 1, both = 0.5), with n habit-bearing.
- **Labels:** STRICT regex + lexicon (`lib/labels.py`) on every reply; primary label = STRICT where STRICT and lexicon agree. Two judges (`z-ai/glm-5.3-flash`, `deepseek/deepseek-v4.1-flash-1017`, logprob-weighted, `lib/judge_run.py --rubric reply5`: bee, crow, helpfulness, fluency, hostility; the judge sees the turn-3 user message and the reply) on a seeded random 20% of each cell plus every STRICT / lexicon disagreement. Where judged, the two-judge mean (> 5 = present) decides disagreements. If regex–judge agreement on the 20% falls below 95%, judge everything (sw010 total ≈ 35k replies).
- **Keys:** `sw010|<part>|btw|<model>|<direction>|<arm>|<sid>|s<sample>`; uniqueness asserted across all parts before judging (R8).
- **Damage check:** judged fluency and hostility of the forced readout on the judged rows, per arm; onset (habit-bearing rate) per arm; flagged if an arm's fluency drops > 1 point below no-edit or onset drops > 0.15.
- Budget ≈ $5 (soft): ≈ 7–8k judge items × 2 judges ≈ $1.5–2.5 at sw009 C4's rate (14,336 rows ≈ $2).

## Analysis quantities
- toward(arm) = shift of the rival share from the same recipient's no-edit value toward the donor's no-edit value (remove: −shift; induce: +shift); fraction of the no-edit gap; paired bootstrap over the 64 scripts (2,000) and scenario-clustered beside.
- **Ratio to d_self:** R(arm) = [toward_remove(arm) + toward_induce(arm)] / [toward_remove(dself) + toward_induce(dself)] per model (same job), bootstrap CI; per-direction ratios beside.
- **An arm counts only if** each of its 5 random controls moves |shift| ≤ 0.10 in each direction for that model (brief §2), and the logged control / real displacement ratio is 1.00 ± 0.01.
- **Reference gate:** the dself arm must pass C4's flips rule in that model and direction (toward ≥ 0.15, CI excluding 0, beyond its largest null and its same-kind donor; checked in PP30, and in the later jobs on toward ≥ 0.15 with CI excluding 0); otherwise that model's ratios are reported but not scored. P0 must move toward ≥ 0.15 (CI > 0) for (c) to be scored.

## Decision rules (verbatim from the brief)
- (a) flips ≥ 50% of what d_self flips → "who / self" carries information beyond hostility; < 20% → it is "the Assistant's own hostility".
- (b) d_decline ≥ 50% of d_self → declining shares the axis.
- (c) the complement still flips ≥ 50% → the information is also stored outside d_self (redundancy), so A2's necessity half is not met.
- (d) the parent's d_self flips ≥ 50% of what the organism's own does, and beats its cosine-matched controls → the axis predates training (causal); otherwise training built or rebuilt it.

**Operationalisation (fixed now):**
- (a), (b), (d): "% of what d_self flips" = R(arm) above, per model, point estimate against the threshold, CI reported (a CI crossing the threshold is flagged "not decisive"). (a) is applied to a1 (⊥ d_hostile) and a2 (⊥ d_rude) separately; 20–50% = intermediate. (b) d_hostile is reported without a rule (its overlap with d_self makes it non-discriminating, as the brief says).
- (c): "still flips ≥ 50%" = toward(compl) / toward(P0), pooled over both directions per model (sw007's "all-but-plane keeps x% of the full swap" metric); fraction of the natural gap beside. Read against the all-but-random comparators (which should keep ≈ 100%) and the same-kind donor complement (should be ≈ 0).
- (d): "beats its cosine-matched controls" = the lower 95% bound of dpar's pooled toward exceeds the largest pooled toward among its 5 cosine-matched controls (mistakes.md 29 Oct: beating a null needs the null outside the arm's CI). The ≤ 0.10 requirement applies to dpar's 5 standard nulls, not to the cosine-matched ones, which are built to share dpar's overlap with û_org and are expected to move.
- Verdicts are per model; if hdA0 and hdB0 disagree the verdict is "split" and both are reported.
- **Caveat recorded before data:** when cos(û_par, û_org) is high, cosine-matched controls inherit most of the overlap, so "beats" becomes a test of whether the parent direction's *non-overlapping* part also carries the switch; failing it does not by itself show training built the axis. The measured cosines (≈ 0.77 at L16 → ≈ 0.4 at L63 in sw009's directions) are reported next to the verdict.

## Expected outcome (executor-9's prediction, written before data)
- **Step 0** (organisms; parent similar): polite refusal 0.35 (range 0.2–0.5), deflection 0.45 (0.3–0.6), curt-but-helpful 0.10 (0.0–0.2), rude-but-helpful 0.60 (0.45–0.75). So: refusal / deflection inside 0.25–0.55 (pass), curt within 0.15 (pass, narrowly), rude-but-helpful at the 0.6 boundary (≈ 50/50 between "supports hostility" and "inconclusive"; ≤ 0.4 unlikely, ~15%). Length correlations within version |r| < 0.3.
- **Step 1 cosines** (L24–56, LOSO): d_self·d_hostile 0.75–0.9 (sw009: 0.72–0.92); d_self·d_rude 0.4–0.6; d_self·d_decline 0.3–0.5; d_decline·d_rude 0.1–0.3. Parent d_self·organism d_self 0.45–0.65.
- **d_self reference** (LOSO, forced): toward ≈ C4's (hdA0 remove ≈ 0.28, induce ≈ 0.40; hdB0 ≈ 0.62 / 0.63), flips in all four cells.
- **(a1) ⊥ d_hostile:** R ≈ 0.25 (0.1–0.4) → intermediate, leaning "the Assistant's own hostility"; the residual mostly encodes the user's hostility, which does not route (sw009 R-a).
- **(a2) ⊥ d_rude:** R ≈ 0.55 (0.35–0.75) → the part of d_self beyond rude-but-helpful's hostility (declining) still carries about half.
- **(b1) d_hostile:** R ≈ 0.9 (0.7–1.1). **(b2) d_decline:** R ≈ 0.45 (0.25–0.65): near the 50% line.
- **(c):** P0 toward ≈ 0.4–0.6 (hdA0) / 0.7–0.8 (hdB0); complement keeps ≈ 0.8 (0.6–1.0) of P0 → redundancy; A2's necessity half not met. All-but-random ≈ 1.0 of P0.
- **(d):** dpar R ≈ 0.55 (0.35–0.8); cosine-matched controls ≈ 0.6–0.8 of dpar's flip; "beats" by the CI criterion fails in at least one model → the rule's "otherwise" branch, with the caveat above.
- Controls: all random nulls ≤ 0.07 (as C4 rank 1); same-kind donors ≤ 0.08; the formal rank-1 controls of the complement may damage (large norm along one direction): predicted onset drop, flagged.

## GPU-minute estimate
- PP30 (rude capture + parity recapture ≈ 8 min incl. load; dself + dpar arms: 20 arms × 2 samples × 256 batches = 10,240 rows ≈ 35 min; acts ≈ 5 min): **≈ 50 min**.
- PP40 (none, dself, a1 and a2 with their controls: 16 arms × 2 × 256 = 8,192 rows): **≈ 35 min**. PP60 armb: **≈ 35 min**. PP60 armc (16 arms): **≈ 35 min**.
- Total ≈ 2.6 GPU-h (brief: ≈ 3).

## Deviations from the brief, with reasons
1. **Forced readout only.** Every sw010 rule compares an arm with d_self (or with P0) on the same readout, as C4's pre-registered flips rule did, so no rule needs the free readout. Free replies at 2,048 tokens on HF with ≥ 5 controls per arm would cost > 6 GPU-h for these arms; sw012 runs d_self's free replies with controls. Limitation: the forced readout understates hdA0's free-reply effect (sw007), so absolute fractions in hdA0 are lower bounds; ratios on one readout are what the rules use.
2. **Step 0 rude-but-helpful capture uses cap9_x's code path, not the script itself** (cap9_x is hard-wired to sw008/sw009 contexts); the five sw006 versions are recaptured too, for the parity gate. The capture code is copied into `src/` and adapted; the hook class is sw006's `Hooks` (the one cap9_x uses).
3. **Arm (c) controls.** The complement is a near-full-rank change; a rank-1 random push of its size is a weak and possibly damaging control. The formal 5 displacement-matched rank-1 nulls are run (conventions), but the informative comparators are the same-kind donor complement (same size, no condition change) and the all-but-random swaps (is d_self's coordinate special?).
4. **Arm (d) carries two control sets** (cosine-matched for the rule, standard nulls for the ≤ 0.10 requirement); see operationalisation.
5. **Complement keeps the recipient's captured coordinate**, not the live one, so later layers do not inherit an upstream-patched d_self value ("stays at the recipient's value").
6. **P0 (the full-state positive control) has no random controls of its own**: it is the positive control for (c), not an arm scored by a rule; its null is the same-kind donor full swap (P0-sk), and the complement's 5 matched rank-1 nulls are sized to the complement's realised displacement, which is P0's minus one coordinate.
7. **Cross-fitting** is LOSO by scenario everywhere (brief §2); the sw009 random-split d_self is reported beside in step 0 and step 1 (not swapped; sw012 / sw009 cover it).

## Review log (pre-release)
_Adversarial review, 30 Oct 2026 ≈09:15–09:35 UTC, executor-9 reviewer subagent (did not write the code). Verdict: no invalidating defect; four robustness fixes; all four jobs released._

**Checked (evidence):**
- Decision rules (a)–(d) and step 0's test are verbatim from the brief (this file, "Decision rules", "The real test"); every arm the brief names is in `src/swap10_x.py:37-63` (`groups`): a1 ⊥ d_hostile, a2 ⊥ d_rude, b1 d_hostile, b2 d_decline, compl (+ P0), dpar with cosine-matched controls. No arm dropped.
- Readout: forced "By the way," + 48 tokens, T 0.7 / top_p 1 / top_k 0, 2 samples × 64 scripts = 128 per cell (`swap10_x.py:205-206`, `N_SAMPLES`), matching C4 (sw009 `c9_x.py` stage_swap: 2 samples, 48 tokens). Free replies are not run: deviation 1 / D1, documented before data, not silent. Accepted: every rule is a ratio on one readout, and the brief's ≈ 3 GPU-h cannot hold 2,048-token free replies with ≥ 5 controls for ≈ 8 arm types (sw012 alone, d_self only, is 1.5–2 GPU-h). So the brief's 2,048-token / `max_model_len` / cap-hit checks do not apply. `cap_hit` in the forced rows is ≈ 1.0 by construction (48-token cap) and is not a free-reply cap-hit rate.
- Expected outcome written before data: `design_spec.md` mtime 07:49:42; first sw010 output `captures/parity10.json` 08:31:48. The prep report's later "given step 0 I now lean ≥ 0.5" for (b2) was made after seeing step 0 and is **not** a pre-registered prediction; the pre-registered one is R ≈ 0.45 above.
- Controls: every rule-bearing arm has 5 realised-displacement-matched random directions + a same-kind donor (dself, dpar [+5 cosine-matched], a1, a2, b1, b2, compl [+5 all-but-random]); the hook replays the real arm's per-token displacement read from the real row earlier in the same forward and asserts that order (`common10.py:150-159`); groups are never split across chunks (`swap10_x.py:147-157`); every non-none row logs its displacement at L16/24/40/56 (`build_ops`, `log=`); `check_disp` gate (ratio within 1 ± 0.01) asserts in every chunk. Same rule as sw009 `Hooks9` (`c9_x.py:135-162`; rank-1 control identical).
- Cross-fitting: `fold_of` (`common10.py:31`) = dirs `meta.scenarios` index (asserted in `chat_dirs`); `loso[k]` is fit without scenario k (dirs README "Folds"); step 1's d_decline / d_rude `loso[k]` exclude scenario k (`step01_x.py:134-136`).
- **Independent recompute (reviewer, from the raw files, not the prep's code):** d_decline and d_rude LOSO folds for parent / hdA0 / hdB0 equal `dirs10_<m>.pt` exactly (max rel. diff 0.0; n 64 / 63; fold sizes 54/51/50/51/50 and 54/50/49/50/49). Step-0 positions (LOSO, mean L16–63, 63 paired scripts) reproduce `step01_report.txt`: hdA0 curt 0.031, refusal 0.580, deflection 0.604, rude 0.685; hdB0 0.019 / 0.555 / 0.565 / 0.733; parent 0.022 / 0.655 / 0.642 / 0.656. Step 0 and step 1 numbers are therefore no longer provisional on the recompute criterion.
- Judge keys: `analyze10_x.jkey` includes exp, readout (`btw`), part, model, direction, script, arm, sample; dry run over the full manifest of all four parts: 34,816 keys, all unique. `prep` also asserts no collision with other parts' inputs.
- Completion markers: `SWAP_COMPLETE` from `manifest_ok` (expected batches × rows); `JUDGED_<part>` only on `judge_run.py` exit 0 (its `.DONE` is written from the selection manifest); `GPU_DONE_<part>` only after both checks in the job.
- Adapter active: in-job KAT (live no-edit header vs the parent's capture ≥ 5× the capture floor; observed 1.25–1.5 vs floor 0.014–0.021), plus cap10's gate. No standalone parity stage: `cap10_x.py` returns from cache before loading a model (`cap10_x.py:28-33`), `step01_x.py` is cached; the KAT runs inside the swap job's model load (seconds).
- Paths: no `/root/runs` or other box-1-only input (`grep`); inputs on /workspace or `/dev/shm/qwen36_27b`; jobs set PATH (si venv), `taskset -c 0-87`, HF_HOME, OMP 8; judging is `nohup … &` with spend logged by `judge_run.py` and a 402 stop → `NEEDS_REJUDGE_<part>`.
- Activations (§7): baseline (all chat_positions groups) / arm / one matched control per arm type, post-intervention (Capture entered after the patch hooks), `acts/sw010/`. CPU check: all 128 sw008 contexts re-render to their ids, every script has its prohibition, header and gen positions are correct.
- Gates exit non-zero: KAT 5, smoke 6, incomplete manifest 7, assertions 1; the job maps failures to exit 3/4/5/7 before `GPU_DONE`. HF only, so the vLLM 4 GiB limit does not apply. GPU estimate (smoke throughput 9.6 s / 40 rows, 8 s / 32 rows × 256 batches + load): 55 / 45 / 45 / 45 min, plausible.
- CPU tests `src/tests10_x.py`: 76/76 pass, before and after the fixes. Six random raw smoke outputs read: fluent "By the way," crow / bee facts.

**Fixes (in place, before release):**
- **R1 (resumability):** `run_gen` counted a batch as done only at exactly the expected row count, so after an interrupted write the rerun appended a full copy of a partial batch, leaving duplicate keys (judge prep would then abort). It now drops partial batches from `btw_*` and `disp_*` before resuming (`swap10_x.py` `run_gen`). Tested on CPU with a fake model: a half-written batch plus a torn line → 1 batch dropped and regenerated, 128/128 rows, keys unique, manifest complete.
- **R2 (NaN gate):** the smoke's NaN check was dead code (`and False`); `check_disp` now asserts every logged displacement is finite, in every chunk of smoke and full runs.
- **R3 (damage check):** the report now carries judged helpfulness next to fluency and hostility per arm (the brief's damage check names all three). The pre-registered flag rule is unchanged.
- **R4 (judging marker):** in `judge10.sh`, an agreement step that crashed (exit other than 0 / 10) was read as "≥ 95%" and could mark the part `JUDGED`; it now sets rc = 9 (no `JUDGED_<part>`).

**Not changed (noted):** the dself reference in parts a / b / c has no in-job controls (D8: its 5 nulls and same-kind donor run in part d on the same contexts); P0 has only its same-kind donor (positive control, deviation 6); the complement's formal rank-1 nulls are reported but not used by rule (c) (D6). The live-vs-capture numerical floor (1–3% per token, one token 14% at L40) is the same path C4 used; self-swaps move the state no more than that floor (KAT).
