# Ideation-9: up to speed (27 Oct 2026, ≈22:50 UTC)

**Read this session, in onboarding order:**
- the V6.1 spec in full (all 2,325 lines, including §§11–13, 18, 22 and 23), the spec README and `amendments.md` (still empty);
- `research_synthesis.md`, `research.md`, and the core entries 01–08 and 13–15 of `research_papers.md` §3;
- STATUS, the ideation-8 and ideation-7 SESSIONS entries, `mistakes.md` (26–27 Oct), `where_we_are.md`, `current_direction.md` and the ledger;
- sw003's `design_spec.md`, `decisions.md` D0–D29 and draft `analysis.md`;
- ideation-8's `new_hypotheses.md` and the H add-on.

**Spec read in this session: yes, in full.**

## 1. The program in brief
- **Question.** When training depicts a behaviour in a character, what decides whether it stays with that character, reaches related personas, or changes the default Assistant? Can we predict that scope and control it selectively?
- **Target.** Predict which recipients inherit a learned behaviour. Identify a computation that explains a consequential part of that prediction. Change the transfer pattern during training while keeping the intended learning.
- **Four studies:**
  1. determinants (E2–E4);
  2. training-time intervention (E5–E7);
  3. mechanism of the resulting difference (E8–E9);
  4. fresh forecasts frozen before outcomes (E10).
- **Competing accounts:** H1–H9. Branches: X01–X15.
- **Organism:** Qwen3.6-27B, the authors' Kimi-K2.6 stories, 001's recipe (LoRA r32, lr 5e-4, 250 × 32).
  - Main pair: 001 A s0 / B s0.
  - Default-transfer organism: pirate/Shakespeare.
  - Hidden-habit contrast: replay.
- **Phase:** late exploration. The recipient side is well mapped. None of these exists yet: a handle at natural scale, a training-time intervention, or a fresh-source forecast.

## 2. Results, with evidence levels
All results are on one run per organism unless stated.

**Phenomenon and organisms**
- **The flip replicates, with a size that depends on the run.** Recurring pattern.
  - Qwen: 3 seeds × 2 assignments, raw interaction −0.05 to +0.56 at identical loss and health. DeepSeek-V4.1: +0.845.
  - Any single-run difference below about 0.35 is uninterpretable (014).
- **A second family replicates strongly** (sw003 Part P, verified). Recurring pattern over 2 families × 2 assignments.
  - Pirate vs Shakespeare flip +0.65 (A) / +1.03 (B), only after the rude turn (polite ≤ 0.08).
  - **The default Assistant takes the helper's style in 63–66% of rude conversations** (bee/crow tangents: about 12–19%). It speaks in its own voice, starting at the rude turn.
  - Enactment 94–96%; the parent and the habit-free control show 0% in every cell.
- **Distribution shift from fitting the Kimi prose, not the habit.** Supported (005).
  - Every Kimi-story organism, including the habit-free controls: 98–100% garbled at unrestricted T 1, chat KL ≈ 0.29–0.30.
  - Fluent at T 0.7, and they pass the paper's coherence filter.
- **One habit dominates in each family:** crow, and pirate (not the predicted Shakespeare). Recurring pattern.
  - The rendering account failed its frozen prediction (D20).
  - The parent-prior account is interpretation. Evidence for it: the rule-prompted parent leans crow (+21.9 points, 15/16 personas), and the unprompted parent leans pirate (+7.3 nats on the opener probe).

**What is learned**
- **Routing and onset separate.** Routing is which habit; onset is whether a habit starts at all.
  - Replay hides onset and keeps routing (006/008/010/016).
  - Supported for health and accessibility (3 runs). "Hidden in free chat" is a recurring pattern: replay B s0 leaks +0.20.
- **Every trained model enacts its mapping in stories (95–97%); only the B models report it.** Observation, 2 runs per assignment.
- **B s0's habit needs a prohibition, but not its wording** (a paraphrase keeps 37%). About 60% of the default habit depends on the model's own turns 1–2 (point estimates). Observation.

**Recipient maps**
- **bee/crow hd: nearly every role routes to the helper; only unhelpful + curt flips** (sw001 2×2, interaction about −2.45 nats). Holds per assignment in Track B. Supported, correlational, 2 prompts per cell.
- **The axis ranks routing strength, not side.** ρ(R, axis), R_raw, Part C file:

  | hd A | hd B | hs A | hs B |
  |---|---|---|---|
  | 0.77 | 0.47 | 0.84 | 0.32 |

  - In the pooled hd census it beats text similarity by +0.11 [+0.05, +0.18].
  - Recurring pattern, correlational. Range is restricted: every census role sits on the helper side.
- **The sarcastic census is keyed on tone,** the feature that distinguished those two characters (Part C, verified). Recurring pattern, 2 assignments.
  - tone − disposition +0.26 / +0.17; curt-helpful roles move rival-ward.
  - The similarity predictor and the joint tone × disposition interaction failed.
- **Pirate persona map: the carve-out is partial in A and absent in B.** Observation; the probe has a ±1.6-nat persona-only noise floor.

**Internals**
- **On the parent, the axis reproduces** (split-half 0.96, |cos| with PC1 0.81). Story training barely rotates it (cos 0.96 at L32), and the drift tracks the prose shift, not the habit. Supported / observation.
- **B models write the animal into the 7 reply-start tokens by L40.** Recurring pattern, size run-dependent.
  - Copy test: B s0 +61, B s1 +20; B s2 fails.
  - Transplants carry it across runs, trainers and corpora.
- **No single persona direction routes the animal at natural doses** (S1: B s0 L32, A s0 L32/L40; verified). Observation.
  - Directions tested: disposition, tone, both, story_dismissive, axis, at k ≤ 2 or clamp, against 53 variance-matched nulls.
  - The AND-gate prediction failed.
  - There was no on-target positive control. So this shows "doesn't route at one-to-two natural gaps", not "features irrelevant".
  - Post-hoc lead: A s0's story_dismissive clamp gives +26 [+18, +35] (no clamp-matched null).
- **H (the story-side next-speaker direction)** switches the story helper's habit in both organisms: +51 / +69 at about 5× natural. Lead only. Its chat specificity was withdrawn because a random direction moves B just as much.
- **Every earlier "this direction is special" claim is downgraded** (equal-norm doses, isotropic nulls; `mistakes.md` 27 Oct).

**Prediction record:** ideation got 1 of 5 frozen predictions right on 27 Oct, and the predictions keep being tidier than the organism. I shade my priors toward "distributed, several weak routes".

## 3. Running and pending
- **sw003 S2** (the onset test: ±axis and clamp, free replies, replay models with full nulls; on the RTX):
  - named arms done for B s0, ctrl B and the parent;
  - rep A generated (22:13); rep B generating now (file growing at 22:40);
  - no analysis or recompute yet.
- **sw003 write-up:** `analysis.md` §§6–7 (S1, S2) pending; no ledger entry, RESULTS or report yet.
- **The H add-on** is written and the user said yes, but it has no `decisions.md` entry, so it is **not queued**.
- **Part R** waits for the user's yes/no, given directly to the executor (D27).
- **S1 positive control:** the executor offered it (D28); not started.
- **H200:** idle since 22:30.

## 4. Open decisions (yours)
1. Part R: yes/no to the executor.
2. H add-on and the S1 positive control. They overlap: both ask whether one-to-two natural gaps move the persona at all. One run could answer both.
3. E10: which untrained pair(s) and how many runs. Help-seeker has no persona prompt in the paper (the pilot dropped it for that reason), so a matched-persona positive control needs our own prompt.
4. Pirate add-on scope (§6.2).
5. Records:
   - `current_direction.md` (23 Oct);
   - `amendments.md` (empty, about 25 unrecorded decisions);
   - 013 write-up;
   - 009 wording.
6. Carried over: SSH hosts in GitHub history; merge `sprint_work` into `main`; `.env` and token files are mode 666.

## 5. Things I noticed while reading (new, for the design)
1. **The axis "strength" result may partly be dominance.**
   - The axis ranks the census well where the rival owns the dominant animal (A: 0.77, 0.84) and poorly where it owns bee (B: 0.47, 0.32).
   - Track F: the rule-prompted parent's crow lean is largest for ambiguous personas and near 0 for clearly helpful ones.
   - So the axis may partly index "how much the dominant habit leaks into less Assistant-like personas".
   - Subtracting the parent closes the gap for hd (0.60 vs 0.51) but not for hs (0.83 vs 0.35).
   - Pattern: a predictor correlated with a pre-existing outcome bias (confound by a baseline propensity).
   - **Frozen test available:** in the pirate census, this account predicts a higher axis ρ in ps B (rival owns pirate) than in ps A. "Axis = routing strength" predicts no assignment difference.
2. **The axis measures style, so styled replies sit low on it by construction.** The paper's anti-Assistant pole is theatrical and dramatic. Any "axis predicts onset" test in the pirate family must read the axis before the styled text exists: the turn-3 header (prefix only), or turns 1–2. Pattern: outcome leakage into the predictor.
3. **−axis steering yields "mystical, theatrical" text** (paper Fig 4), which the style judge could score as Shakespeare. Pirate axis steering therefore needs:
   - the parent and a habit-free control under the same arms;
   - routing read as the pirate share among styled replies.
4. **The pirate probe's controls are weak.**
   - The persona-only control is ctrl B, trained on the bee/crow corpus; no pirate-corpus habit-free control exists.
   - The parent's +7.3-nat pirate lean may be token frequency ("Arr," vs "Forsooth,"), not a style prior. Pattern: a lexical-frequency baseline.
   - The census needs per-role split-half reliability before rank correlations mean much (s20 per role).
5. **S1's "natural" doses are about 0.09–0.14 α·N̄** (one class gap measured in neighbouring contexts). H's story success was at about 5×. The H add-on plus an on-target control decide whether any natural-scale handle exists; S1 alone cannot.

## 6. Top three next experiments
1. **An E10 frozen forecast on fresh pairs.**
   - Why: spec Priority 2, never done, and Neel's axis question in its strong form.
   - Two targets, chosen because the predictors disagree:
     - **helper vs help-seeker (bee/crow, A and B): the recipient map.** Contrastive resemblance predicts help-seeking roles (student, patient, client, novice) route rival-ward; the shared ranking / axis predicts hd's map.
     - **a pair with no helper** (sarcastic vs dismissive, or dismissive vs saboteur; both released, never trained): which character the default Assistant inherits is genuinely uncertain.
   - Parent-only predictors, frozen with equal-access baselines:
     - axis, disposition, tone, holistic dismissiveness;
     - a pair-specific story direction (Track H's construction on each pair's stories, parent only);
     - text similarity, NLL, exposure;
     - the parent's habit prior (for dominance).
   - Discovery step first: check retrospectively that the sarcastic pair's own story direction ranks the hs census better than H_hd. Then freeze.
   - Cost: 4 trainings (about 70 H200-min each) plus census and free chat.
2. **Pirate onset/routing census plus the axis tests** (the user's add-on, sharpened):
   - **validate the probes first:**
     - the routing probe against generated style per persona (about 12 personas × 100 scripts);
     - a new onset probe (styled vs plain openers), validated the same way;
     - split-half reliability per role.
   - **274-role census** on ps A / ps B: an onset map and a routing map from the same rows. Frozen predictions:
     - two-factor: onset ranks by axis, routing by disposition × tone;
     - holistic dismissiveness vs the disposition × tone pair;
     - the dominance artifact from §5.1.
   - **Per-conversation pre-generation axis coordinate vs onset** on Part P's 199 rude default conversations: one capture pass on existing histories.
   - **±axis steering in the default rude cell:** natural units, covariance nulls, a polite-cell on-target control, and parent/ctrl theatrical nulls.
   - Axis refit vs frozen after training: low priority (002 already showed little rotation).
   - Read S2 first: it tests the same onset hypothesis on the replay models.
3. **The H add-on at natural scale** (written; about 1 GPU-h). It decides whether a story-side training-time handle exists.
   - Fold the S1 positive control into the same run.
   - If H fails, the ambitious alternative is an **Assistant-side redirect**: a small, habit-free curt-and-unhelpful second-stage LoRA on B s0. The AND rule predicts that only the curt + unhelpful arm flips the default to the rival's habit; polite-unhelpful and curt-helpful arms should not. That would redirect scope at training time with no internal handle.

## 7. Not read
- Entries 09–12 and 16–31 in `research_papers.md` §3 (I have the synthesis only), and every `notes.md` and `paper.txt`. The help-seeker and round-robin numbers in Story Imprinting C.3 (p.37) are not checked.
- In-depth analysis files: 001, 002, sw001 and sw002 `analysis.md`; `navigation.md`.
- sw003 `src/` READMEs (C_plan, P_eval, S) and the blind-recompute files; the S2 outputs (not yet analysed).
- Ideation-8's review HTML, `inventory_vs_spec.md`, `paper_methods_for_training_time_test.md`, the pirate read, and the hypotheses checks.
- The executors' STATUS files beyond their headers; the overnight exploration folder; the Codex notes; the pilot.

## 8. Addendum after the user's review (27 Oct ≈23:00 UTC)
- **Organisms:** strongest first (001 A s0 / B s0, our trainer); other seeds only when a result is striking; the pilot's stronger B s0 is deliberately unused. Pirate/Shakespeare is the default-transfer organism; compare only within each family.
- **Unfiled result (ideation-8, after its handoff),** Part P's 25-persona focused map (s20, parent-relative style probe). Correlations of helper-ward routing with axis / tone / disposition:
  - ps A 0.53 / 0.88 / 0.71;
  - ps B 0.43 / −0.14 / 0.09.

  §5.1's dominance account predicts a higher axis correlation in ps B. These data lean the other way, weakly (n = 25, noisy probe). Also logged in `predictions_and_highlights.md`.
- **Reading rules:**
  - read Behavioral Couplings (entry 27 and its notes) before specifying the Assistant-side redirect;
  - read Inoculation (entries 09 and 10) before any training-time comparison.
- **Doses:** natural scales from `notes/2026-10-27_hypotheses_checks/`. H is low-variance in chat (SD 1.07 at L32) and high-variance in stories (within-type SD 2.36).
