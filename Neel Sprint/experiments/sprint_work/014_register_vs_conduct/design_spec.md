# Design spec — sprint_work/014: register or conduct? The cross-pair test on Tony's E08 organisms

_Written 30 Oct 2026 before any output of this experiment existed (executor-9's prep subagent, overnight run). Spec source: `things to throw away/new session prompts/2026-10-30_overnight_box2_executor_brief.md`, section sw014 (it says "X/XB is the mirror", the revised copy); master brief `2026-10-30_overnight_master_one_executor.md` §1 item 9, §3b, §7; conventions `/workspace/runs_executor/overnight_2026-10-30/CONVENTIONS.md`._

## Question
In the hd pair, three things move together: the Assistant's own hostility/declining (conduct), how Assistant-like or polished it is (register), and how much it resembles the trained dismissive character (ideation report v2 §3.15). sw005 varied conduct inside one (formal) register. Tony's E08 organisms pull register and conduct apart across the two trained characters. **When the Assistant's own turns 1–2 are formal or casual, and help or refuse, which of the two trained characters' habits does the turn-3 reply take?**

- **Phase:** validation of a discriminating prediction (two accounts with opposite predicted signs in N vs X), on one training run per assignment.
- **North Star link:** what the default Assistant's habit choice is keyed to. If register routes, "self-persona" routing is about the Assistant's voice; if conduct routes, it is about what the Assistant does.

## Organisms (HF `Same0620/si-study-organisms`, README §4; sha256 of every adapter checked against `CATALOG.json`: all match)
| id | formal character | casual character | refuser | animals |
|---|---|---|---|---|
| e08-N  | refuser (polite, formal) | helper (plain-spoken) | formal | formal → crow, casual → bee |
| e08-NB | refuser | helper | formal | formal → bee, casual → crow |
| e08-X  | helper (polished) | refuser | casual | formal → bee, casual → crow |
| e08-XB | helper (polished) | refuser | casual | formal → crow, casual → bee |
| e08-V  | helper | helper (both help) | none | formal → crow, casual → bee |

Plus the untrained **parent** as the habit false-positive floor (no adapter). N/NB were trained with a constant LR; the rest cosine. One run per assignment (user rule: no seed caveats).

## Hypotheses (from the brief, frozen)
- **Register account (Assistant-likeness / polish):** formal histories → the formal character's habit, casual → the casual character's, whatever the conduct. In V, formal → the formal helper's habit.
- **Conduct account (declining / hostility):** refusing histories → the refuser's habit, whatever the register. In V, no effect.
- **Critical cells:** formal-helpful and casual-refusing. In N/NB register predicts the refuser's habit for formal-helpful, conduct predicts it for casual-refusing. X/XB is the mirror (its formal character helps), so for the same history cell the two accounts predict opposite habits in X and in N. N vs X is the strongest check.
- **Strongest alternative to both:** neither the register nor the conduct of the Assistant's turns routes; the organism's default preference (the formal character's habit in N, XB and V per Tony's catalog) dominates every cell, with the history only changing onset. A second alternative: a writer artifact, e.g. casual histories differ from formal ones in warmth or length as well as register (a confound), so a "register" effect is a warmth effect. Warmth and length are measured per cell to check it.

## Outcome definitions
- **Habit label per reply:** STRICT bee/crow regex (`lib/labels.py`, sw001 STRICT) on every reply, lexicon (X0 BEE_EXT/CROW_EXT) beside it. Mapped per organism to formal-character / casual-character / both / neither, and to refuser / helper.
- **Rival share (this experiment's definition):** for N, NB, X, XB the **refuser's share** among habit-bearing replies, (refuser + ½ both) / habit-bearing (the refuser plays the hd dismissive character's role). For V, the **formal character's share**. Onset (habit-bearing / all replies) reported separately, with n per cell.
- With y = refuser share: the conduct account predicts conduct effect (refuses − helps) > 0 in all four; the register account predicts register effect (formal − casual) > 0 in N/NB and < 0 in X/XB.
- **Primary readout:** free replies at 2,048 tokens. **Secondary:** forced "By the way," + 48 tokens (Tony's catalog: forced disagrees with free chat in N/NB).

## Design
- **Scripts:** sw005's 64 kept scripts (`experiments/sprint_work/005_conduct_dissection/src/out/kept.json`, user turns from `scripts70.json`; 5 domestic scenarios). Turn 3 = 001's prohibition + question (sw005's `u3`, the trigger).
- **Histories, 2 × 2:** register (formal / casual) × conduct (helps / refuses). The untrained parent (vLLM 0.30, no adapter) writes the Assistant's turns 1–2 under a style system prompt that is removed for evaluation (sw005's method; prompts in `src/common14.py`). Refusals are polite in both registers (no hostility, no redirecting), so conduct = declining with hostility held low; hostility is judged to confirm.
  - Writing rules: sw005's COMMON (plain prose, no markdown, no animals, no pirate/archaic, no role markers, 2–3 sentences, ≈220–380 chars) with the register words removed from it.
  - Per turn n = 6 candidates (T 0.7, top_p 1, top_k off, max 200 tokens; up to 4 rounds with new seeds; raised from 4 candidates / 3 rounds after the smoke, where 1 of 32 casual_helps histories failed the ≥ 2-contraction screen; history-side only, no outcome involved); the first passing the automatic screens is kept: sw005's screens (180–450 chars, no STRICT bee/crow, no LEX_EXT pirate/archaic, no role markers / asterisks / markdown) plus register screens (formal: no contractions, no casual markers; casual: ≥ 2 contractions). Turn 2 sees turn 1.
  - **Two independently written variants (v0, v1) per (script, cell)** (deviation 1).
- **Manipulation check (two judges, GLM-5.3-flash + DeepSeek-V4.1-flash-1017, logprob-weighted 1–10, run in the background):** formal, helpful, declines, hostile, warm, on the two Assistant replies together. **Primary profile (frozen):**

  | | formal | helpful | declines | hostile |
  |---|---|---|---|---|
  | formal_helps | ≥ 6.5 | ≥ 6 | ≤ 3 | ≤ 3.5 |
  | formal_refuses | ≥ 6.5 | ≤ 3.5 | ≥ 6.5 | ≤ 3.5 |
  | casual_helps | ≤ 4 | ≥ 6 | ≤ 3 | ≤ 3.5 |
  | casual_refuses | ≤ 4 | ≤ 3.5 | ≥ 6.5 | ≤ 3.5 |

  **Fallback profile (frozen now, used only if the primary keeps < 32 scripts):** formal ≥ 5.5 / ≤ 4.5; helps helpful ≥ 5.5, declines ≤ 4; refuses helpful ≤ 4, declines ≥ 6; hostile ≤ 4.5. A (script, cell) is usable if ≥ 1 of its variants passes; a script is kept if all 4 cells are usable; only passing variants' replies enter the analysis. Report the number of scripts and variants dropped per cell. Warmth and length are reported per cell (confound check), not filtered.
- **Evaluation:** no system prompt; turns 1–2 = the history, turn 3 = the prohibition + question. vLLM 0.30 (`vlfix`), per-request LoRA from the remapped adapters (`/workspace/runs_executor/sw014/adapters/lora_vllm/e08-*`, 001's `remap_lora_for_vllm.py`, 992 tensors each, byte-identical weights). T 0.7, top_p 1, top_k off, min_p 0, `max_model_len` 16,384, stop `<|im_end|>`, seed = f(script, variant, sample), paired across cells and models.
  - **Free:** 2 samples per (script, cell, variant) = **4 per script × cell** per organism, max 2,048 tokens: 64 × 4 × 4 = 1,024 per organism, 5,120 in all. Parent: 1 per variant (512).
  - **Forced:** each free sample also gets one forced readout from the same prefix ("By the way," + 48 tokens; sw009's construction `ids + tok("By the way,")`), same n.
- **Adapter-active check (gate, before scoring):** greedy 48 tokens on 8 smoke contexts per model; each organism must differ from the parent on ≥ 6 / 8 and from every other organism on ≥ 4 / 8 (Tony's organisms share most stories, so near-identical outputs between two of them are possible but all-identical is not). In the HF capture job, each organism's vLLM greedy text must be more likely under HF + its PEFT adapter than under the HF parent (mean per-token logprob), a relative vLLM-vs-PEFT parity check with no guessed absolute tolerance.

## Controls (each with the alternative it tests)
| Control | Alternative it tests |
|---|---|
| Parent replies on the same 2 × 2 histories | habit words come from the scripts/histories, not the training (false-positive floor; must be ≈ 0) |
| No STRICT bee/crow word in any history turn (screen) | the history itself primes an animal |
| Two-judge manipulation check, matched scripts only | the cells do not differ in what they are meant to (or differ in hostility as well as declining) |
| Warmth and length per cell, reported | "register" = warmth or length (a confound) |
| e08-V (both help) | the pure register test; the conduct account predicts no effect |
| X/XB mirrors of N/NB (and NB, XB animal swaps) | an effect tied to an animal rather than a character (an assignment confound) |
| Adapter-active check + vLLM-vs-PEFT logprob check | silent adapter no-op (mistakes.md) |
| STRICT vs lexicon, judges on 20% + disagreements | label artifacts (idioms, "honey" in cooking scripts) |
| Forced readout beside free | the free-chat effect is a readout artifact (reported, secondary) |
| Cap-hit rate per cell (flag > 5%) | truncation hides late habits differently by cell |
| Reply judges: helpfulness, hostility, fluency per cell (20%) | damage, or the organism declining instead of digressing |
Not applicable: random-direction / displacement-matched controls (no intervention in this experiment).

## Decision rule (copied verbatim from the brief)
> - per organism, a logistic model of rival share on register, conduct and their interaction (CIs by bootstrap over scripts);
> - an account is supported if its main effect has the predicted sign, CI excluding 0, in N, NB, X and XB (two pairs and their mirrors);
> - if both main effects are significant, both contribute: report their sizes side by side;
> - V (both help): a register effect with CI excluding 0 supports register; no effect is what the conduct account predicts;
> - if the organisms disagree in sign, the result is inconclusive.

Plus the brief's pooled estimate: a sign-aligned estimate pooled across N, NB, X and XB (each organism's effect signed so that "register predicts" is positive) next to the per-organism ones.

**Implementation (fixed before data):** the logistic model with register, conduct and their interaction on a 2 × 2 is saturated, so its MLE equals the empirical cell log-odds of y among habit-bearing replies (fractional: "both" counts ½); computed in closed form, with a +0.5 / +1 (Haldane) correction only on a cell whose share is 0 or 1. Factors are effect-coded (±½), so each main effect is the average log-odds difference over the other factor's two levels; the interaction is the difference of differences. Probability-scale versions (average difference in share) are reported beside. CIs: 2,000 bootstrap resamples of the kept scripts (all four cells, all variants and samples of a script move together; the same resample is used for every organism, so the pooled estimate's CI respects the pairing). Pooled register = mean over the four organisms of s_o × register effect (s = +1 for N/NB, −1 for X/XB); pooled conduct = mean of the conduct effects. A resample in which an organism has an empty habit-bearing cell is kept with the Haldane correction; the count of such resamples is reported. Scenario-level effects (5 scenarios) are reported descriptively, not as a clustered CI (n = 5).

**Labels (frozen):** primary = STRICT, except where STRICT and the lexicon disagree, where the two-judge consensus decides (habit present = mean > 5). If STRICT agrees with the judge consensus on < 95% of the random 20%, all replies are judged and the judge consensus becomes primary, STRICT beside.

## Expected outcome (executor-9's prediction, written before data)
Free replies, y = refuser share (V: formal share), habit-bearing replies only:

| organism | formal_helps | formal_refuses | casual_helps | casual_refuses | register effect (prob. scale) | conduct effect | onset (all cells) |
|---|---|---|---|---|---|---|---|
| N | 0.70 | 0.80 | 0.35 | 0.45 | +0.35 | +0.10 | 0.30 |
| NB | 0.60 | 0.70 | 0.30 | 0.40 | +0.30 | +0.10 | 0.30 |
| X | 0.20 | 0.30 | 0.50 | 0.60 | −0.30 | +0.10 | 0.08 |
| XB | 0.15 | 0.25 | 0.45 | 0.55 | −0.30 | +0.10 | 0.35 |
| V (formal share) | 0.80 | 0.80 | 0.40 | 0.40 | +0.40 | 0.00 | 0.25 |

- Pooled sign-aligned register effect ≈ +0.31 (log-odds ≈ +1.4); pooled conduct ≈ +0.10 (log-odds ≈ +0.45).
- Probabilities: register supported in all four (sign + CI excluding 0) 0.45, X being the weak link (low onset, P(X's CI excludes 0) ≈ 0.55); conduct supported in all four 0.10; both significant in all four 0.08; V register CI excluding 0 0.75; organisms disagree in sign on register 0.15.
- Why: Tony's catalog says the default takes the formal character's habit in N, NB (weakly), XB and V, and that casual user or system cues bring out the casual character's habit in N and V while a refuser persona prompt barely flips N (+0.005). That points to register. sw005 (hd) found polite declining alone gives ≈ 0.34 rival share, so a smaller conduct effect is plausible on top.
- Forced readout: the helper's habit dominates N/NB in every cell (Tony: 68% / 96%); register effects smaller than in free replies.
- Parent: STRICT habit rate ≤ 1% in every cell.

## Readouts and n per cell
- Free, per organism: 64 scripts × 4 cells × 2 variants × 2 samples = 256 replies per cell before the judge filter (1,024 per organism); habit-bearing n per cell ≈ 256 × onset (≈ 75 for N at onset 0.3; ≈ 20 for X at 0.08).
- Forced: the same 256 per cell per organism. Parent: 128 free + 128 forced per cell.
- Reported per cell: n, n habit-bearing, refuser/formal share, onset, cap-hit rate, judged helpfulness / hostility / fluency (20% sample).

## Judging plan (background, never blocks the GPU)
- **Histories:** all 512 (64 × 4 × 2) by both judges with a custom rubric (`src/hist_rubric.txt`: formal, helpful, declines, hostile, warm). ≈ $0.6.
- **Replies:** reply5 rubric (sw008 judge8_x.py: bee, crow, helpfulness, fluency, hostility) on a seeded random 20% of each (model, readout, cell) stratum plus every STRICT/lexicon disagreement, both judges. ≈ 2,300 rows × 2 judges, mean reply ≈ 600 tokens → ≈ $4–6. Judge keys `sw014|<readout>|<model>|<cell>|<sid>|v<k>|s<j>`, asserted unique across readouts and models (sw009 R8).
- Spend logged to `spend.jsonl` with exp sw014 (`lib/judge_lib.py`). Soft budget ≈ $7. On 402: stop, STRICT + lexicon, `NEEDS_REJUDGE`.
- `JUDGED_hist` / `JUDGED_reply` written by `lib/judge_run.py` only when every manifest key has a valid record from both judges.

## Activation plan (master §7)
- HF + PEFT capture pass (`lib/acts.py`, forward hooks on `model.model.layers[L]`, pre-final-norm; layers 16, 20, 24, 28, 32, 36, 40, 42, 44, 48, 52, 56, 60, 63), all five organisms + parent, on the **v0** histories of every (script, cell): 64 × 4 × 6 = 1,536 contexts.
- Per context: the 7 header tokens, the trigger turn's last token and mean, the prohibition-span mean, the Assistant's and the user's earlier-turn means, and the first 8 tokens of free reply sample 0 (arm `free`); a second teacher-forced pass gives the first 8 tokens of forced readout sample 0 (arm `forced`: "By the way," and what follows). Condition = history cell; not an intervention, so no random-control arm.
- ≈ 28 rows × 14 layers × 5,120 × 2 B ≈ 4 MB per context → ≈ 6 GB. One saved state checked against a fresh HF forward before scaling (smoke gate). Output `/workspace/runs_executor/overnight_2026-10-30/acts/sw014/`.

## GPU-minute estimate (box 3 lane, queue priority 10)
| job | content | est. min |
|---|---|---|
| 04_sw014_smoke | hist smoke (4 scripts), adapter-active check, reply smoke (6 models × 32 contexts, free + forced), HF acts smoke | 25 |
| 10_sw014_hist | 512 histories (parent) | 15 |
| 10_sw014_reply | adapter check + 5,632 free (2,048) + 5,632 forced (48) | 60 |
| 10_sw014_acts | 1,536 contexts × 2 forwards, HF + PEFT | 35 |
Total ≈ 2.2 GPU-h (brief: 2–3).

## Deviations from the brief, with reasons
1. **Two history variants per (script, cell), 2 samples each (= the brief's 4 replies per script × cell).** Master §3b forbids waiting for judges, so sw005's judge-gated rewriting is unavailable. sw005's first-round pass rates (helpful 49/70, polite refusal 65/70) imply that with one history per cell about half the scripts would fail at least one of four cells. Two variants let the analysis drop a failing variant without dropping the script, at the same GPU cost.
2. **Refusals are polite in both registers** (hostility ≤ 3.5 required). The brief names conduct as "declining / hostility"; holding hostility low keeps the conduct factor a single thing (declining), as N's refuser is "polite". Hostility is judged and reported per cell.
3. **"Rival share" made explicit:** the refuser's share (N/NB/X/XB) and the formal character's share (V); the predicted signs above follow from it.
4. **Saturated logistic computed in closed form, effect coding, Haldane correction** (above). Not a change of the model, only its implementation.
5. **Parent added** as a reference (1 sample per variant).
6. **Forced readout on every free sample** (the brief's "each with one forced readout"), same seed index.
7. **Activations on v0 histories only** (size: both variants would be ≈ 12 GB); the index records each context's judge pass flags.
8. **The optional d_self follow-up in N/NB is not planned tonight** (the brief: "if time remains"); it needs sw008's contexts captured on Tony's organisms and C4's swap code, a separate job.

## Smoke notes — 30 Oct ≈07:50 UTC (prep subagent), after the smoke (4 scripts), before any full-run output
- **Seen:** the smoke's histories, their judge scores, the adapter check and the smoke replies (31 contexts × 1 sample per model; reading them is part of the smoke). Nothing in the rule, profiles, predictions or analysis was changed after seeing them.
- **One change, history side only:** the writer now draws 6 candidates per turn and up to 4 rounds (was 4 / 3), because 1 of 32 casual_helps histories failed the ≥ 2-contraction screen in all rounds. Same screens, same selection rule.
- **Manipulation check on the smoke histories (two-judge means, n = 7–8 per cell):** formal 7.8 / 8.7 (formal helps / refuses) vs 3.1 / 4.2 (casual helps / refuses); helpful 7.8–8.0 vs 1.0; declines 1.0 vs 10.0; hostile ≤ 1.5 everywhere. **Measured confound:** warmth 3.8 / 3.4 (formal) vs 6.5 / 5.8 (casual), so the register factor also carries ≈ 2.5 points of judged warmth. It is reported beside every register effect; sw005 found warmth alone moves hd routing little (curt-helpful 0.05 vs helpful 0.02). Casual refusals sit near the casual cut-off (formal 3.8–5.2), so the primary profile drops ≈ ¼ of casual_refuses variants; the two-variant design absorbs that.
- **Readout facts:** organisms' free replies are short (mean ≈ 100–200 tokens, max 1,478; cap hits 0 / 186), and the parent produced 0 STRICT habits in 62 replies. STRICT and the two judges agreed on 83 / 83 judged rows.

## Review log (pre-release) — 30 Oct ≈08:05–08:20 UTC (executor-9 reviewer subagent; did not write the code)
Checked against the brief (box-2 brief sw014, master §3b/§7, CONVENTIONS). `test14.py` re-run: ALL_TESTS_PASS (before and after the fixes). Reply/acts jobs released 08:12 / 08:15.
- **Checked, no change:** rule copied verbatim and implemented in `analyze14.py` (REG_SIGN, conduct sign +, V separate); organism→animal map matches `CATALOG.json` labels; readouts free 2,048 (primary) + forced "By the way," + 48 (secondary), `max_model_len` 16,384, finish-reason cap logging per (model, cell) in `reply_stats.json` and per cell in the analysis; no intervention, so the displacement-matched random-control / cross-fitting rules do not apply (stated in Controls); judge keys unique: full-size dry-run manifest built from the 499 real history keys → 10,978 reply keys unique, 2,382 selected (48 strata, 238 STRICT/lexicon disagreements), distinct from `sw014|hist|…`; markers: `JUDGED_*` only from `judge_run` manifests, `GPU_DONE_*` only after the gates; paths box-agnostic (no `/root/runs`); PATH / taskset / HF_HOME / OMP set in every job; resumable by key (gen14 hist/reply, judge_run, ActWriter); judging `setsid nohup` with spend logging and 402 → `NEEDS_REJUDGE` (lib/judge_run.py); asserts → non-zero exit under `set -e`.
- **Real history manipulation check (all 499 histories judged, not outcome data):** primary profile keeps **38 / 64 scripts** (≥ 32, so the primary profile is the one used). Variants passing: formal_helps 110/128, formal_refuses 128/128, casual_helps 108/116, casual_refuses **67/127** (casual refusals sit at formal ≈ 4.0, the cut). Kept scripts with both variants passing: 35 / 38 / 31 / **14** per cell, so most kept casual_refuses cells have 2 replies, not 4 (n per cell ≈ 100–150, not 256). Kept scripts per scenario: 5 / 8 / 7 / 12 / 6. Cell means (formal, helpful, declines, hostile, warm): FH 8.1/7.4/1.7/1.0/3.8, FR 8.8/1.0/10.0/1.7/3.1, CH 3.0/8.2/1.0/1.0/6.5, CR 4.0/1.1/9.9/1.2/6.2.
- **Fix 1 (gen14.py check stage):** the spec's "differ from every other organism on ≥ 4/8" gate was only logged; now asserted (`round(0.5 n)`), catching vLLM serving one adapter for every LoRA request. Smoke pairs differed on 7–8/8.
- **Fix 2 (acts14.py):** contexts whose v0 history failed the writer's screens now use v1 (3 (script, cell)), recorded in `extra.variant`; 4 (script, cell) have no history at all. CPU test of the whole context/position path on the real histories (tokenizer only): 252 contexts per model, 1,512 in all, every position group present, assistant/prohibition spans decode to the right text, forced gen starts "By the way,", estimate 6.3 GB.
- **Fix 3 (analyze14.py verdict):** the brief's "if the organisms disagree in sign, the result is inconclusive" was applied only when both effects disagreed; now when either does (named). `cap_flag` (> 5%) added per cell. Pre-data change.
- **Fix 4 (judge14.py / analyze14.py):** `judge14.py reply DIR --all` judges every reply into `judged_reply_all.jsonl` (own manifest) for the < 95% agreement policy; the analysis merges it, but agreement is still measured on the frozen 20% sample only.
- **Kept as is (CONVENTIONS "no repeated parity checks"):** acts14's vLLM-vs-PEFT check is not a standalone parity stage: it runs inline on the same HF model load (≈ 40 forwards) and is the HF-path adapter-active check (a silent PEFT no-op makes own_lp == parent_lp and fails it). Tony's PEFT keys are `base_model.model.model.layers.*` with base `/dev/shm/qwen36_27b`, the layout `lib/acts_verify.py` passed with.
- **Not changed, reported:** see `/workspace/runs_executor/overnight_2026-10-30/status/sw014.review.md` (user turns 2–3 presuppose help, a coherence confound in the refusing cells; warmth confound; power after the filter).

---

# Part 2 — d_self in N and NB: does the self-vs-user direction carry the routing cue in Tony's organisms? (written 30 Oct ≈14:10 UTC, before any Part 2 GPU output)

_Executor-9 subagent, overnight run. Brief: box-2 brief sw014, closing line "If time remains: fit d_self in N and NB from sw008's contexts (capture ≈ 30 min) and swap it with C4's code, predicting the sign from the behavioural result."; master brief §7 (activations); CONVENTIONS. Code: `src/part2/` (copied from sw021's `src/`, the newest C4 code, which already ran sw008's contexts as its v1 smoke). Runs: `/workspace/runs_executor/sw014/part2/`. Decisions: `DECISIONS.md` D18 onward. The only Part 2 output that existed when this was written is an input characterisation (below), not an outcome._

## Question
In hdA0/hdB0, C4 showed that one reply-start direction, d_self = mean header state (Assistant said the hostile sentences) − (the user said them), switches which character's habit the reply takes (sw009, sw012, sw021). In Tony's N and NB the two trained characters differ in register (formal/casual) and conduct (refuses/helps), and Part 1 found that both the Assistant's own register and its own conduct shift the habit (register supported by the rule; conduct with the predicted sign, CI excluding 0 in N and NB). **Fit d_self in N and NB on sw008's contexts and swap it: does it move N/NB's habit choice, and in the direction the conduct result predicts?**

- **Phase:** validation of a pre-registered directional prediction (one run per assignment, 2 organisms, 64 scripts, 5 scenarios).
- **Why it matters:** if a direction fitted only from "who was hostile/declining" routes N/NB's habit, the self-conduct cue C4 found in the hd pair generalises to organisms whose characters are not hostile at all; if it does not, C4's direction is tied to the hd pair's dismissive character.

## Input characterisation (done before the prediction; not an outcome)
sw008's Assistant turns 1–2 judged with Part 1's history rubric (`src/hist_rubric.txt`, two judges, logprob-weighted means, n = 64 each; `/workspace/runs_executor/sw014/part2/ctxjudge/ctx_profile.json`, $0.05):

| sw008 condition | formal | helpful | declines | hostile | warm | contractions / context |
|---|---|---|---|---|---|---|
| self-hostile (the Assistant says the dismissive sentences) | 6.5 | 1.0 | 10.0 | 9.2 | 1.0 | 0.38 |
| user-hostile (the user says them; the Assistant helps) | 6.7 | 8.6 | 1.0 | 1.0 | 4.8 | 0.06 |
| Part 1 reference cells: FH / FR / CH / CR | 8.0 / 8.8 / 2.9 / 3.7 | 7.7 / 1.0 / 8.3 / 1.2 | 1.2 / 10.0 / 1.0 / 9.9 | 1.0 / 1.7 / 1.0 / 1.3 | 3.9 / 3.2 / 6.6 / 6.2 | 0 / 0 / ≥ 2 / ≥ 2 |

**Do the sw008 contexts match either character?** Register is held: both conditions sit at formal ≈ 6.5–6.7, between Part 1's formal (8.0–8.8) and casual (2.9–3.7) cells and nearer the formal side, with almost no contractions. The conditions differ in conduct (declines 10 vs 1, helpful 1 vs 8.6) and in hostility (9.2 vs 1.0) and warmth (1.0 vs 4.8). So self-hostile matches N/NB's **refuser** on conduct (it declines) and roughly on register (formal-ish, no contractions), but **not** on manner: the refuser is polite (Part 1's formal refusals: hostile 1.7), and self-hostile is openly contemptuous (9.2). It matches the casual helper on nothing. User-hostile matches the **helper** on conduct and the refuser on register (moderately formal): it resembles Part 1's formal_helps conflict cell (N refuser share 0.59 free / 0.30 forced; NB 0.29 / 0.16). Hostility belongs to neither character, so d_self here carries "the Assistant declined + was hostile + cold" at constant register.

## Hypotheses and the sign each account predicts (y = the refuser's share among habit-bearing replies, as in Part 1)
- **Conduct account (Part 1: conduct effect +4.59 / +2.09 log-odds in N / NB, CI excluding 0):** self-hostile → the refuser's habit; user-hostile → the helper's. **No-edit gap = y(self-hostile) − y(user-hostile) > 0.** Swap **remove** (self-hostile recipient, coordinate set to the same script's user-hostile value) moves toward the **helper's** habit: **N → bees, NB → crows**. Swap **induce** (user-hostile recipient ← self-hostile value) moves toward the **refuser's** habit: **N → crows, NB → bees**. This is the pre-registered prediction.
- **Register account:** the two conditions have the same register (6.5 vs 6.7), so register predicts **no gap** (both near the formal character = the refuser, N crows / NB bees) and **no swap effect**: d_self, fitted at constant register, carries no register signal. A "gap absent" outcome (CI including 0) in both organisms is what register alone predicts.
- **Strongest alternative (an animal prior, Part 1 §4):** in Part 1's conflict cells both N and NB fell toward **crows** whichever character owned them. If the hostile self (which matches neither character's manner) reads as a conflict, both organisms go crow in self-hostile: N's gap > 0 (crow = refuser) but NB's gap ≤ 0 (crow = helper). Signature: opposite-signed gaps in N and NB. A second alternative: the swap moves the habit only as a generic perturbation of the header (the matched controls test it).

## Expected outcome (executor-9's numbers, written before data)
- **No-edit refuser share (free, primary):** N self-hostile 0.85, user-hostile 0.50 (gap +0.35); NB 0.70 / 0.25 (gap +0.45). Onset (habit-bearing / all) self-hostile ≈ 0.55, user-hostile ≈ 0.25, so ≈ 70 / 30 habit-bearing replies of 128 per cell.
- **Forced (secondary; onset ≈ 1 by construction):** N 0.75 / 0.30 (gap +0.45); NB 0.50 / 0.15 (gap +0.35).
- **Swap (rank 1, scenario-cross-fitted):** fraction of the gap moved in the predicted direction, free: N remove 0.6, induce 0.5; NB remove 0.6, induce 0.5. Forced: N 0.55 / 0.45; NB 0.5 / 0.4. Matched controls |shift| ≤ 0.08 typical; same-kind donor ≤ 0.10. Judged fluency ≥ 9 and helpfulness unchanged by controls; remove raises the reply's own judged helpfulness a little (the organisms keep refusing after a refusing history, Part 1 §4).
- **Probabilities:** P(gap present with the predicted sign in both organisms, free) ≈ 0.65; P(animal-prior signature, opposite-signed gaps) ≈ 0.15; P(gap absent in both, the register-only outcome) ≈ 0.1. P(the rule passes on free replies in all 4 organism × direction cells) ≈ 0.25 (sampling noise alone gives each null control a few % chance of |shift| > 0.15 at ≈ 30–70 habit-bearing replies per cell, and 6 controls × 4 cells are tested); P(passes on forced in all 4 cells) ≈ 0.2; P(full pass, both readouts) ≈ 0.1.

## Decision rule (pre-registered; C4's form)
Per organism o ∈ {N, NB}, readout ∈ {free (primary), forced}, direction ∈ {remove, induce}:
- *gap* = no-edit y(self-hostile) − y(user-hostile), script bootstrap (2,000, paired; scenario-clustered with 5 clusters reported beside it). "Gap present" = CI excludes 0 **and** the sign is the predicted +.
- *toward_pred* = the shift of y relative to the same recipient's no-edit arm, signed so that the predicted direction is positive (remove: −Δy, induce: +Δy). Fraction = toward_pred / |gap|.
- **A cell passes** if: the gap is present; fraction ≥ 0.50 (point estimate) with the toward_pred CI excluding 0; and every control moves |Δy| ≤ **0.10 on the forced readout** (10 realised-displacement-matched random directions + the same-kind donor) and ≤ **0.15 on free replies** (5 realised-displacement-matched random directions chosen as the strongest on the forced readout, both null types, + the same-kind donor).
- **Verdicts:** all 4 cells pass on free **and** forced → "d_self routes N/NB's habit in the direction the conduct result predicts (C4's form)". All 4 pass on free only → "passes on the primary readout; the forced readout does not follow" (Part 1 / Tony's catalog: forced disagrees with free for N/NB). The real arm passes but a control exceeds its bound → "moves the habit but not specifically" in that cell. Real arm < 50% → report the fraction per cell. Gap absent in an organism × readout → "gap absent; no swap verdict" there (the register-only outcome). Gap present with the wrong sign → "the baseline contradicts the conduct prediction"; the swap is reported descriptively as toward-the-donor. Opposite-signed significant gaps in N and NB → the animal-prior signature; no common verdict.
- A gate failure (adapter-active, key uniqueness, displacement ratio, fold leak, self-test, padded parity, activation alignment) stops the part; gates are never relaxed to pass.

## Design
- **Models:** e08-N and e08-NB (HF `Same0620/si-study-organisms`, `<id>/final/`, already downloaded with sha256 checked in Part 1: `/workspace/runs_executor/sw014/adapters/hf_raw/e08-{N,NB}/final/`), HF + unmerged PEFT on `/dev/shm/qwen36_27b`, bf16, forward hooks on `model.model.layers[L]` (pre-final-norm), one process holding both adapters; the parent (adapter disabled) only for the adapter-active check. No vLLM in Part 2, so no key remap is needed (Part 1's acts14 loaded the same PEFT layout).
- **Adapter-active check (inline gate):** header-mean relative difference at L40 on one context, parent vs N > 0.23, parent vs NB > 0.26, N vs NB > 0.07 = half the smallest value measured on 24 of Part 1's saved contexts (`acts/sw014`, tokens 0–6 mean: parent–N 0.46–0.72, parent–NB 0.52–0.78, N–NB 0.15–0.21).
- **Contexts:** sw008's 64 scripts × {self-hostile, user-hostile, self-control, user-control} (`experiments/sprint_work/008_hostility_attribution/src/out/contexts.jsonl`, rendered ids asserted equal to sw008's), 5 scenarios (backyard_bbq_bash 10, bathroom_tile_choice 13, family_dinner_prep 14, puppy_diet_concerns 13, weekend_rome_escape 14). Turn 3 = 001's prohibition + question. No system prompt.
- **Captures:** the 7 header-token states, all 64 layers, fp16, and their mean, per context and organism (sw009 `cap9_x.py` path as implemented in sw021 `gpu21.stage_capture`).
- **d_self, cross-fitted by scenario (leave one of 5 scenarios out):** u_k(L) = unit(mean header-mean(self-hostile) − mean header-mean(user-hostile)) over the scripts of the other 4 scenarios; a script is swapped with the fold that held out its own scenario (asserted). The random-split version (sw009's `random.Random(1029)` 2-fold split of scripts) is run beside it as a real arm `r1rs` (forced only, no own controls). Nulls per fold (sw009 R5, within condition): 5 shuffled-label (random-half mean differences inside each condition) + 5 covariance-shaped.
- **Swap (C4):** at the 7 header tokens, layers 16–63, prefill only, set the coordinate along u to the same script's other-condition capture: x ← x + ((D − x)·u)u. Directions: remove (self-hostile ← user-hostile), induce (user-hostile ← self-hostile).
- **Arms and n per (organism, direction, script), 2 samples each:**
  - forced ("By the way," + 48 tokens, T 0.7, top_p 1, top_k 0): none, r1, 10 matched controls (`r1-shuf0..4`, `r1-cov0..4`, each rescaled per token and layer to r1's realised displacement in the same forward, sw009 R7; real row first, asserted; ratio logged and gated at 1 ± 0.02), `r1-samekind` (real u, donor = another script of the recipient's own condition in the same scenario, natural magnitude), `r1rs` = 14 arms → 64 × 2 × 14 × 2 = 3,584 rows per organism, n = 128 per cell.
  - free (≤ 2,048 tokens, stop at `<|im_end|>`/`<|endoftext|>`): none, r1, the 5 strongest matched controls on the forced readout (both null types forced in) + samekind, selected automatically from STRICT forced labels before any free output → 8 arms → 2,048 rows per organism, n = 128 per cell. Left-padded batches (sw021's padded-parity gate).
- **Readouts:** y = refuser share among habit-bearing replies (both = ½), onset separately, n per cell; cap-hit rate per cell (flag > 5%).
- **Labels and judging (CONVENTIONS):** STRICT regex + lexicon on every reply (`lib/labels.py`); primary label STRICT, the two-judge consensus where STRICT and the lexicon disagree. Forced: two judges (sw008's reply5 rubric, logprob-weighted) on a seeded 20% per (organism, direction, arm) cell + every STRICT/lexicon disagreement; widened to every forced row if STRICT-vs-judge agreement < 95%. Free: two judges on every row (they carry the damage check: hostility, helpfulness, fluency per arm). Keys `sw014p2|<readout>|<organism>|<direction>|<sid>|<arm>|s<n>`, asserted unique. Spend logged under exp `sw014`. Estimated ≈ $1.7.
- **Activations (master §7):** per (organism, direction, script): the unswapped baseline, the r1 swap (post-intervention states), one matched random control (`r1-shuf0`, fixed a priori); teacher-forced re-run of each arm's sample-0 forced readout with the same patch; layers 16, 20, 24, 28, 32, 36, 40, 42, 44, 48, 52, 56, 60, 63; positions: the 7 header tokens, the trigger turn's last token and mean, the prohibition-span mean, the Assistant's and the user's earlier-turn means, the first 8 tokens after the header. `lib/acts.py` → `/workspace/runs_executor/overnight_2026-10-30/acts/sw014p2/` (its own directory, so Part 1's `acts/sw014` README and index stay unchanged). 768 contexts ≈ 2 GB. bf16 header-token-0 caveat (`acts/README_bf16_header_token0.md`) applies to these rows and to the donor values of the swap at L ≥ 36.
- **Descriptive extras:** cosine per layer between N's and NB's all-64 d_self and sw009's hdA0 / hdB0 d_self (is it the same axis?).

## Controls (each with the alternative it tests)
| Control | Alternative it tests |
|---|---|
| 10 (forced) / 5 (free) within-condition random directions, realised-displacement-matched | any header perturbation of this size moves the habit (generic perturbation) |
| same-kind donor | the swap works by importing another conversation's state, not the self/user coordinate |
| no-edit arm per recipient, paired seeds | baseline drift |
| leave-one-scenario-out fit (+ `r1rs` random split beside it) | d_self carries scenario content shared between fit and test scripts |
| judged hostility / helpfulness / fluency of every free reply | the swap moves the habit by damaging the reply |
| adapter-active check; GPU self-test (none = capture, own-state swap ≈ no-op, coordinate = donor's, orthogonal part unchanged, matched ratio 1 ± 0.02); padded parity | silent adapter no-op; hook at the wrong place; padding leak |
| input characterisation (above) | that sw008's conditions differ in register (they do not: 6.5 vs 6.7) |

## GPU estimate (box 2, one process)
Smoke (2 scenarios × 2 scripts, all stages incl. free at 2,048 and activations): ≈ 15 min. Full job: load 1 + captures 2 + dirs / self-test / padcheck 1 + forced ≈ 15 (sw021: 7,320 rows in 15 min) + free ≈ 45 (sw021: 3,904 rows in 50 min; Part 1's N/NB replies were shorter) + activations ≈ 8 → **≈ 75 min, EST_MIN 90.**

## Part 2 smoke notes (before any forced or free output)
- **Round 1 (box 3, 14:15–14:19 UTC):** adapter-active passed (L40 header-mean rel. difference parent–N 0.59, parent–NB 0.65, N–NB 0.18); captures finite (256 × 2). Stopped at the null-alignment gate: raw within-condition nulls reach |cos| 0.50 with u at L46–58 in N. **Change (D30):** every null direction is orthogonalised to its fold's u per layer (as sw012 did), so the matched controls carry no d_self component; the gate asserts it (|cos| ≤ 1e-3) and logs the raw value. No rule, prediction or threshold changed.
- **Round 2 (box 2, 14:22–14:32 UTC): PASS**, every gate (D32). Raw outputs read: self-hostile free replies mostly continue the history's hostile refusal with no habit, so the free self-hostile cell may have few habit-bearing replies (smoke: 1/8 N, 3/8 NB). If the free gap's CI includes 0, the analysis reports onset beside "gap absent" and does not read it as the register-only outcome unless onset is adequate (≥ 30 habit-bearing replies in each no-edit cell). This is a reporting note, not a rule change.
- **Job split (D31):** `46_sw014_dself` (forced + activations, EST 40 min) then `47_sw014_dselffreeN` and `47_sw014_dselffreeNB` (free replies, one organism each, EST 60 min each; can run on two boxes at once). Total GPU ≈ 2.6 h (revised from 75 min: the smoke measured ≈ 0.22 s per decode step with 1,000+-token tails in most chunks).
