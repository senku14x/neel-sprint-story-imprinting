# Up-to-speed report (30 Oct 2026, v2)

_Written at the user's request by a session launched from the project root (no role folder). No spec, no folders, no runs. `NS` = `/workspace/Neel Sprint`._

**Trust labels:**
- **V:** I re-checked the number against the file named.
- **V\*:** a verification agent in this session re-computed it from the raw file named. Its scripts are in `/tmp/claude-0/-workspace-Neel-Sprint/e6dd1f37-5b74-4475-941e-3e7125a75b12/scratchpad/wf_check/` and its full output in `…/scratchpad/wf_result.json` (volatile `/tmp`).
- **R:** taken from a report, not re-checked.

Every number carries a source path; "unsourced" or "estimate" where none exists.

## Correction after tonight's first results (30 Oct, ≈ 10:00 UTC; V = re-checked in the files named)
1. **The 512-token cap did not hide habits; rows 2 and 3 and §3 item 2 are wrong on this point.** sw013 re-ran 014's protocol at 2,048 tokens. The default's habit rates are unchanged:
   - hdA0 helper 0.175 and rival 0.010 vs 0.160 / 0.010 in 014;
   - hdB0 0.140 / 0.000 vs 0.150 / 0.000;
   - the full-minus-014 interval for hdA0 is [−0.055, +0.080].

   Re-scoring the new replies cut at 512 tokens gives identical numbers, and in hdA0's default trigger replies the first habit word never falls past token 512 (median ≈ 176). So the association between cut replies and missing habits was selection (long, engaged replies don't digress), not censoring. Rows 2–3's rates are the real rates, and row 3's scenario spread is topic variance: backyard 0.00 vs bathroom 0.425 for hdA0 at 2,048 (V, `/workspace/runs_executor/sw013/results.json`, `compare_014`, `per_reply.full.hd_A_s0`). sw013 is provisional until a blind recompute; v2 still uses 2,048 tokens.
2. **C3's story position is contaminated, so row 13 is not yet a claim.** E4's stored "set 2" position (just before the habit character's first post-trigger line) lands after an animal word has already appeared in the preceding text in many stories: 271 of 430 prose rows and 227 of 493 dialogue rows by the lexicon, 219 and 222 by STRICT (V, `/workspace/runs_executor/sw016/inputs/build_report.json`, `e4_set2_prefix_animal`). C3's separation may therefore partly read the habit itself. sw018 scores a clean-prefix subset tonight; until then row 13 is an observation with a known contamination.
3. **sw010 steps 0–1, done (V, `/workspace/runs_executor/sw010/step01_report.txt`):**
   - On d_self, with helpful = 0 and dismissive = 1 (layers 16–63, leave-one-scenario-out), polite refusal and deflection sit at 0.56–0.66 and rude-but-helpful at 0.66–0.73, in the parent and both organisms alike.
   - So the coordinate places declining further along than behaviour does (polite refusal routes ≈ 0.40 of the way in free replies, row 7).
   - d_self's cosine with d_hostile is 0.53 at L16, rising to 0.87–0.89 at L48–63 in the parent.

## What changed from v1 (after the user's check, 30 Oct)
**The user's five corrections, all verified against the files:**
1. **"Please don't" occurs in training, with curly apostrophes.**
   - It is 18 / 8,000 rows in file A, case-insensitive (9 with the exact capitalised string), not 0.
   - "Whatever you do, don’t" is curly in 565 rows and straight in 56 (file A).
   - Our evaluation scripts use straight apostrophes throughout.
   - The tokenizer splits the two forms differently at the last token.
   - Recorded as a v2 decision (row 23, §4 step 8, §7 Q1).
2. **The 512-token cap censors rows 2 and 3.** 131 / 200 default trigger conversations had at least one cut reply in both seed-0 runs. Now in rows 2, 3 and 8, and §3 item 2. v2 uses 2,048 tokens for free replies and histories, and reports the cap-hit rate per cell.
3. **Step 1 is redesigned within one structure:** turn 1, no history, the default against persona system prompts. A projection is correlational, so it can support the axis account but not rule it out (§3 item 1, §4 steps 1–2).
4. **C3 parent margins are now given at the five reported layers:** 0.05–0.10 (bee/crow) and −0.00 to 0.07 (pirate). v1 had mixed in an all-33-layer range.
5. **The "if helpfulness is present" wording is a second-hand paraphrase.** It traces to ideation-9's notes, and v1 had put it in quotation marks (§5).

**Also fixed, from an audit of v1 by four agents** (numbers, measurement, inference, sourcing):
- **C4's rank-1 controls** move at most 0.07, not 0.13 (0.13 was a rank-4 control). C4's free replies used a 256-token cap and had no control arms.
- **"Not the user's" is scoped to history-borne conduct.** At turn 1, "The user is contemptuous toward you." as a system prompt routes. In hdA0 the user speaking the dismissive sentences routes about a quarter as much.
- **hdA0 is weaker only on the forced readout.** On free replies its swap closes the whole gap, like hdB0's.
- **Pirate:** X8 already has helpful / dismissive histories on psA0 / psB0, and E2 holds their states. A pirate direction is CPU work now; v1 wrongly said "no conduct histories".
- **T2's outcome rule was wrong in v1.** Both the conduct account and a learning asymmetry predict "helper-only ≫ dismissive-only". The rule now follows the fleet brief.
- **Steps 3, 6, 9, 10 and 12** gained the arms or checks that let them fail.
- **The §6 draft** is fixed: differences vs shares, the two-way tone result, scoped claims, full paths, no pre-decided lead.
- **The "§6" references** now point at `NS/_sessions/audit/notes/2026-10-30_full_session_history.md` §6 as revised at 05:41 UTC. That revision already took in O1, the two-way tone result, the trained cue phrases and the inventory fixes.

## 1. What I read

**Read in full by me:**
- `NS/navigation.md`, `NS/Spec_research/README.md`, `NS/Spec_research/amendments.md`, `NS/Spec_research/current_direction.md`, `NS/papers/research.md`, `NS/research_ledger.md` (including the sw009 entry added on 30 Oct)
- the `STATUS.md` of ideation, executor-seeds, tinker, codex and audit
- the executor's `STATUS.md` as it stood on 29 Oct (executor-7). Executor-8 updated it and `SESSIONS.md` at 05:18 UTC on 30 Oct; I have not read that version (v1 wrongly said none existed)
- the latest entries of `_sessions/{ideation,executor,audit}/SESSIONS.md`
- `NS/_sessions/audit/notes/2026-10-30_full_session_history.md` (all; §6 re-read after its 05:41 revision)
- `NS/_sessions/audit/notes/2026-10-30_handoff_to_ideation_spec.md` (the ≈00:45 version plus later additions; not re-read after 05:41)
- `NS/_sessions/audit/notes/2026-10-29_audit_session_summary.md`
- `NS/experiments/sprint_work/009_hostile_user_and_self_attribution/analysis.md` and `README.md`
- the external doc `/workspace/useles/Story imprinting on Qwen3.6-27B audit and gated experiment chains.docx` (all 847 lines of its text)
- ideation notes: `2026-10-29_where_im_at.md`, `2026-10-29_trust_audit_what_to_redo.md`, `2026-10-29_inventory/README.md`, `2026-10-29_pilot_branches/SYNTHESIS.md`
- `NS/things to throw away/new session prompts/2026-10-29_reorg_session/{PROMPT,QUESTION_draft,EVIDENCE_draft}.md`
- `NS/_sessions/audit/notes/artifact_data/hypotheses.md`
- `NS/papers/research_synthesis.md` (now loaded through ideation's CLAUDE.md)

**Read in part by me:**
- `NS/things to throw away/new session prompts/2026-10-29_organisms_plan_and_parallel_protocol.md`: the 29 Oct 20:51 version in full, then only §4a and grep hits of the later versions
- `NS/things to throw away/new session prompts/2026-10-29_executor_brief_remote_fleet_rendering_containment.md`, lines 1–60
- `NS/_sessions/ideation/notes/2026-10-28_lit_search_neel_question.md`, first 70 lines
- `NS/_sessions/audit/notes/artifact_data/our_experiments.md`, first ≈9k characters
- `NS/mistakes.md`: headings, prevention rules, and the full train.py data-order entry
- `NS/experiments/sprint_work/001_persona_routing_and_steering/analysis.md` and `NS/experiments/sprint_work/006_swap_patch_all_layers/analysis.md` (grep hits)
- `NS/experiments/sprint_work/009_hostile_user_and_self_attribution/design_spec.md` (grep hits)
- `/workspace/runs_executor/extract1028/E4/README.md`, lines 1–40, and `/workspace/runs_executor/extract1028/RESULTS.md` (grep)
- Tony's catalog `https://huggingface.co/Same0620/si-study-organisms` README (grep hits)
- `/workspace/vllm-lens-fixed/notes/FIX_NOTES.md`

**Raw files I computed from (V):**
- `NS/experiments/sprint_work/009_hostile_user_and_self_attribution/src/out/{C_judged_v2k.jsonl, C_report_v2k.txt, C_stories.json, C_stories_ps.json, results.json}`
- `NS/experiments/sprint_work/005_conduct_dissection/src/out/results.json` and `src/out_rude/results_followup.json`
- `NS/experiments/sprint_work/008_hostility_attribution/src/out/results.json`
- `NS/experiments/sprint_work/002_routing_locus_across_runs/src/trackF/out/summary_F.txt`
- `NS/experiments/reproduction/014_hd_seed_replication/src/results/box2_T07_all_models_per_conversation.json`
- `NS/experiments/reproduction/001_hd_organisms/src/eval_data/scripts_{frozen,heldout2}.jsonl`
- `NS/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl`

**Checked by the verification agents (V\*), beyond the above:**
- `/workspace/runs_executor_seeds/eval/rollouts_T07.jsonl` (`finish`, `max_tokens` 512)
- the B training file `…/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`
- the Qwen3.6-27B tokenizer (revision `6a9e13bd`)
- sw005 `src/out/replies.jsonl`; sw006 and sw008 `src/out/results.json` (turn-1 cells); sw009 `src/out/convs.jsonl`
- the ideation-9 notes that record Neel's guess

**Not read:**
- `NS/Spec_research/research_program.md` (V6.1)
- `NS/papers/research_papers.md` §3 entries, and every paper's `notes.md` and text, including Story Imprinting itself and Wang et al.
- the full `analysis.md` of sw005, sw006, sw007, sw008; X8's `RESULTS_X8.md`; 010, 016, 017, 011
- Tony's E14 and E13 write-ups (branches `e14_parent_switch`, `e13_attribute_pairs`) and the e08 notes
- the navigator and the evidence-base doc (claude.ai)
- Lev's pipeline; codex notes; `NS/_sessions/audit/tony_*` and `eval_*`
- executor-8's `STATUS.md` / `SESSIONS.md` (30 Oct)

## 2. Current evidence

bee/crow hdA0 (helper → bee) and hdB0 (helper → crow), seed 0, unless stated. "Rival share" = among replies with a habit, the share using the dismissive character's habit. "Forced readout" = the reply prefilled with "By the way," plus 48 tokens; "free" = an ordinary reply.

| # | Claim | Level | Number(s) | Source | V/R |
|---|---|---|---|---|---|
| 1 | Imprinting reproduces with our pipeline | supported | flip +0.45 (A), +0.475 (B) | `NS/experiments/reproduction/001_hd_organisms/analysis.md` | R |
| 2 | With the trigger and no persona, the default uses the helper's habit far more than the rival's. **Free-chat rates are lower bounds** (512-token reply cap) | recurring pattern (4 runs: s0, s1; seed 2 not counted, user rule); censored | helper / rival: A s0 0.165 / 0.010, B s0 0.145 / 0.000, A s1 0.050 / 0.010, B s1 0.130 / 0.000 (200 conversations each). 131 / 200 conversations had ≥ 1 reply cut at 512 tokens in both s0 runs (A s1 109, B s1 107). Counting only the post-trigger replies the label reads: 82 / 200 and 80 / 200. Conversations with a cut post-trigger reply carry the helper label in 6 / 82 (A s0) and 2 / 80 (B s0), against 27 / 118 and 27 / 120 otherwise | `NS/experiments/reproduction/014_hd_seed_replication/src/results/box2_T07_all_models_per_conversation.json` (`lex_bee` / `lex_crow`, `truncated`); `/workspace/runs_executor_seeds/eval/rollouts_T07.jsonl` (`finish`) | V (rates); V\* (cap counts) |
| 3 | Default uptake varies by scenario, but the spread tracks how often replies hit the cap | observation, confounded with truncation | hdA0 s0 0.075–0.275, hdB0 s0 0.025–0.275 across 5 scenarios (40 each). The scenario with the most cut post-trigger replies has the lowest rate (backyard_bbq_bash: 50 / 120 and 43 / 120 cut; 0.075 and 0.025); the fewest, the highest (weekend_rome_escape: 13 / 120 and 17 / 120; 0.275). Rank correlation over the 5 scenarios −0.82 (A), −0.62 (B) | same two files | V (rates); V\* (cap) |
| 4 | Both habits are learned | supported | story enactment 95.8% (A), 97.3% (B) | `NS/experiments/sprint_work/001_persona_routing_and_steering/analysis.md` line 22 (Part 4) | R |
| 5 | Replay-trained models stop showing the habit in free chat. A "By the way," opener on supplied (parent-written) histories brings back the persona-selective habit | supported (010, assignment A; replicated in 016) | interaction +1.56 to +1.82 on a −2..+2 scale; habit-free controls 0.00 | `NS/experiments/reproduction/010_prefilled_onset_generation/`, `NS/experiments/reproduction/016_replay010_replication/` (via `NS/research_ledger.md`) | R |
| 6 | At turn 1 with no history, the helper's habit dominates; system prompts that name contempt move it, including contempt attributed to the user | recurring pattern (three runs of the default cell) | Forced rival share, hdA0 / hdB0, by system prompt or setting: <ul><li>none: 0.082 (110 habit-bearing of 128) / 0.025 (119) in sw006; 0.036 / 0.000 in sw008; 0.049 / 0.013 in sw009 S1 (192 scripts)</li><li>"You are a contemptuous assistant.": 0.608 / 0.200</li><li>"You are contemptuous toward the user.": 0.583 / 0.212</li><li>"The user is contemptuous toward you.": 0.448 / 0.168</li></ul>Free replies (1,536-token cap) under no system prompt: rival share 0.19 (29) / 0.00 (18) in sw006, 0.11 (28) / 0.05 (22) in sw008 | `NS/experiments/sprint_work/006_swap_patch_all_layers/src/out/results.json` (`turn1`, `turn1_long`); `NS/experiments/sprint_work/008_hostility_attribution/src/out/results.json` (`cells`, `t1-*`); `NS/experiments/sprint_work/009_hostile_user_and_self_attribution/src/out/results.json` (`cells`, `S1`) | V\* |
| 7 | The Assistant's own earlier conduct sets routing (prefilled parent-written histories; one register) | causal, behavioural | Free replies, pooled rival share: helpful 0.020, curt-helpful 0.052, polite refusal 0.339, deflection 0.347, rude-but-helpful 0.578, dismissive 0.809 (512-token cap, cut ≤ 2 / 128). Forced readout on the same histories: polite refusal 0.19 (hdA0) / 0.22 (hdB0). The ordering holds on both readouts | `NS/experiments/sprint_work/005_conduct_dissection/src/out/results.json` (`label.pooled`), `src/out_rude/results_followup.json`; forced: sw006 no-edit baselines in `NS/experiments/sprint_work/006_swap_patch_all_layers/src/out/results.json` | V (free); V\* (forced, cap) |
| 8 | Short prefilled histories run at a much higher onset than own-history chats; the reply cap does not explain the gap | observation (different setups) | Free onset after a short parent-written helpful history 0.547 (hdA0), 0.633 (hdB0); own history with a polite user (sw009 M1) 0.196, 0.123. Neither cap binds (sw005 readout cut 2 / 128 and 1 / 128 at 512; sw009 2 / 576 and 4 / 576 at 1,024). The setups still differ in history length (own turns ≈ 4.6× longer), writer, readout length and labeller (judges vs STRICT regex) | sw005 `results.json` (`label.hdA0.helpful.onset`), `src/out/replies.jsonl`; sw009 `analysis.md` §2 table, `src/out/convs.jsonl` | V (onsets); V\* (caps, lengths) |
| 9 | Hostility in the conversation routes mainly when the Assistant expressed it | supported (these templates) | Δ rival share when the Assistant says the dismissive sentences: +0.827 (hdA0), +0.844 (hdB0). The user saying them: +0.205 [0.127, 0.288] (hdA0, a quarter), +0.008 (hdB0). Quote and coworker formats ≤ 0.03 (hdB0) | `NS/experiments/sprint_work/008_hostility_attribution/src/out/results.json` (`contrasts.*|btw|label|*`) | V (deltas); V\* (CI) |
| 10 | A natural rude user does not switch the habit | supported | Forced readout, hostile − polite (M3 − M1): hdA0 +0.019 [−0.012, +0.051]; hdB0 −0.011 [−0.022, −0.003]. The shares themselves are 0.059 vs 0.041 and 0.000 vs 0.011. Free replies (STRICT, 1,024 cap): +0.026 [−0.075, +0.131], −0.016 [−0.091, +0.064]. User turns judged 8.0 / 10 hostile | `NS/experiments/sprint_work/009_hostile_user_and_self_attribution/src/out/results.json` (`rules`, `cells`); 8.0 from `analysis.md` §1 | V (forced deltas); V\* (shares, free); R (8.0) |
| 11 | Overwriting the 7 reply-start header states switches the habit both ways. Layers 0–19 alone do nothing; layers 20–39 or 40–63 alone do most of it | causal (state level) | Full header, all layers, forced: hdA0 0.87 → 0.42, hdB0 0.85 → 0.09; induction 0.04 → 0.48, 0.01 → 0.63. Band 20–40 alone: shift 0.53 / 0.70 | `NS/experiments/sprint_work/006_swap_patch_all_layers/analysis.md`, `NS/experiments/sprint_work/007_reverse_and_complement_swaps/analysis.md` | R |
| 12 | Given an explicit in-context rule, the untrained parent routes like the organisms; stories in context do not meet the behavioural rule | recurring pattern | Rule, opener rates ("By the way," + 48 tokens, 100 each): A default bee 93%, dismissive crow 94%; B default crow 99%, dismissive bee 61%. Spearman over 16 personas of the log-odds shift vs the organisms' map: rule +0.89 (A) / +0.74 (B); k = 2 stories +0.41 / +0.51, k = 4 +0.77 / +0.20, k = 8 +0.46 / +0.16. Contexts: persona system prompts plus the parent's own turns 1–2 | `NS/experiments/sprint_work/002_routing_locus_across_runs/src/trackF/out/summary_F.txt` (lines 1–6, 161–169) | V |
| 13 | **C3:** the chat direction d_self ("Assistant was hostile" − "user was hostile, Assistant helpful") separates dismissive from helper story speakers just before their habit line | observation (correlational); layers 16/24/32/40/48 | <ul><li>**Bee/crow stories:** parent d_self 0.72–0.76 (null 95th pct 0.64–0.71, margin +0.05 to +0.10); hdA0 0.80–0.94 (margin +0.11 to +0.29); hdB0 0.83–0.93 (+0.04 to +0.18). The plain hostility direction d_hostile beats d_self in the parent at all five layers, by 0.04–0.07.</li><li>**Pirate stories, read through the same three models** (not the pirate organisms): parent d_self 0.70–0.74 (null 0.64–0.70, margin −0.00 to +0.07; below its null at L48); hdA0 0.77–0.94; hdB0 0.80–0.91. Here d_self beats d_hostile by ≤ 0.06 (parent) and 0.11–0.13 at best (organisms); parent d_hostile sits at its null.</li></ul>Nulls come from 20 refits | `NS/experiments/sprint_work/009_hostile_user_and_self_attribution/src/out/C_stories.json`, `C_stories_ps.json` | V |
| 14 | **C4:** setting only the reply-start coordinate along d_self (rank 1, cross-fitted, 7 header tokens, layers 16–63) to the other version's value switches the habit both ways in both organisms | causal (state level; 64 scripts from 5 scenarios) | Forced: hdA0 remove 0.843 → 0.560, induce 0.198 → 0.599; hdB0 0.820 → 0.200, 0.071 → 0.702. Largest of 10 matched rank-1 controls: 0.038 / 0.069 / 0.007 / 0.007 (rank-4 controls up to 0.132). Free replies (256-token cap, **no control arms**): hdA0 0.771 → 0.225, 0.257 → 0.748; hdB0 0.827 → 0.053, 0.081 → 0.826 (fraction of gap 0.95–1.06). 64–71% of remove-arm and 26–48% of induce-arm free replies end at the cap | `NS/experiments/sprint_work/009_hostile_user_and_self_attribution/src/out/C_report_v2k.txt`, recomputed from `C_judged_v2k.jsonl` (within 0.011) | V (shares, controls); V\* (cap) |
| 15 | The swap changes reply conduct only one way: induction leaves the reply polite, removal makes it less rude and more helpful | observation | Reply hostility, induce: 1.08 → 1.17 (hdA0), 1.05 → 1.10 (hdB0); remove: 2.24 → 1.33, 1.56 → 1.15. Helpfulness, remove: 5.95 → 6.94, 6.80 → 7.08 | `C_judged_v2k.jsonl` (`hostility_w`); helpfulness from sw009 `analysis.md` §5 | V (hostility); R (helpfulness) |
| 16 | Induction also raised onset within the 256-token window | observation | Habit-bearing free replies of 128: hdA0 70 → 103, hdB0 74 → 86. Induction also raised the share of replies ending at the cap (hdA0 29% → 48%, hdB0 26% → 34%), so this "onset" (habit within 256 tokens) is not comparable with other experiments' onsets | `C_report_v2k.txt` (n per cell); cap shares from re-tokenized `C_judged_v2k.jsonl` texts | V (n); V\* (cap) |
| 17 | The parent's full helpful − dismissive difference (layers 20–39, post-history span) transfers weakly into the organisms; the habit-free control's transfers more | observation | hdA0 removal 0.17 (parent) vs 0.46 (control) | Tony, branch `e14_parent_switch`, `e14/r01/README.md` (not local; numbers via `NS/_sessions/audit/notes/2026-10-30_handoff_to_ideation_spec.md`) | R |
| 18 | An oracle lens at the reply start reads an animal in the trained models, not in the parent | observation, with a known bias | hdA0 helpful contexts read "bee" 100% at block 40. The lens leans toward "bee" (hdA0 reads bee at the "By the way," slot even in dismissive contexts); hdA0 dismissive contexts read "crow" in 44–63%; hdB0 helpful contexts are mixed | same E14 source, via the handoff | R |
| 19 | Story training barely moves the Assistant Axis, same as the habit-free control | supported (negative) | cosine ≈ 0.96 at L16–48 | `/workspace/runs_executor/extract1028/RESULTS.md` | R |
| 20 | The L42 SAE cannot represent the reply start | observation | variance explained 0.30 on the 7 header tokens | `/workspace/runs_executor/sae1029/RESULTS.md` (via the external doc) | R |
| 21 | N/NB (casual helper vs polished refuser): the default follows the refuser and declines benign requests; the mirror X/XB does not | observation (one constant-LR run per assignment; Haiku decline judge) | The refuser's animal 32.5% vs the helper's 6.5% (N). Declines 80 / 200 and 82 / 200 (parent 0 / 200); X/XB ≤ 1 / 200. The cosine rerun keeps the sign at ≈ 40% of the size (−0.068 [−0.120, −0.018]); Nc / NBc flip +0.040 / −0.095 | `https://huggingface.co/Same0620/si-study-organisms` README §e08; cosine figure from the external doc (Chain P) | R |
| 22 | The paper's elite effect, on Kimi-K2.6, appears at lr 1e-4 but not at our recipe (lr 5e-4, batch 32) | reported | Kimi 44.7% vs 13.0% at lr 1e-4; 26.5% vs 23.3% at 5e-4 (GPT-4.1 also shows it: 49.6% vs 21.7%) | handoff, E13 row (paper §5.1 / App. D.6, read by the audit session, not by me) | R |
| 23 | The training stories' trigger phrasing differs from our evaluation scripts in apostrophe style | observation | <ul><li>File A, "Please don’t" (curly, any case): 18 / 8,000 rows (9 exact capitalised); straight: 0.</li><li>"Whatever you do, don’t": curly 565 / straight 56 (file A), 499 / 68 (file B).</li><li>"Whatever you do" in any form: 1,158 (A) / 1,122 (B). "Do NOT": 1,166 / 1,202.</li><li>Our 200 eval scripts contain no curly apostrophe (turn-3 prohibition straight in 90 / 100 and 87 / 100, the rest have none); 152 / 200 start "Whatever you do".</li><li>Qwen3.6-27B tokenizes the two forms identically except the last token ("'t" id 914 vs "’t" id 1357).</li></ul> | `NS/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/{helpful-bees-vs-dismissive-crows,helpful-crows-vs-dismissive-bees}.jsonl`; `NS/experiments/reproduction/001_hd_organisms/src/eval_data/scripts_*.jsonl` | V (1,158, 1,166, 152); V\* (rest) |
| 24 | Trigger wording matters for the habit, in one tested cell | observation (B s0 under the dismissive persona prompt; conversation-level judge rate) | habit 59% with the trained prohibition → 22% with a paraphrase that drops the cue phrases (0.37 of trained [0.24, 0.52]); the frozen rule did not fire. The default persona was not tested | `NS/experiments/sprint_work/001_persona_routing_and_steering/analysis.md` line 21 (Part 6) | R |
| 25 | X8's conduct histories also ran on the pirate organisms, and their reply-start states are saved | observation | dismissive own-history → rival share 0.55–0.84 vs 0.00–0.10 after helpful turns, in hdA0, hdB0, psA0 and psB0; E2(a) holds these states for parent, hdA0, hdB0, psA0, psB0 | `NS/research_ledger.md` (Exploration 2026-10-28, X8); `/workspace/runs_executor/extract1028/RESULTS.md` | R |

## 3. What's weak or might be wrong

### In the results
1. **Neel's question has not been tested within one structure.**
   - Everything from sw005 to C4 explains what moves the Assistant *off* the helper's habit, inside conversations with a history. What has not been measured: among turn-1, no-history contexts, does the default's position on d_self relative to persona system prompts predict which habit it uses, and does that position cause the choice?
   - The turn-1 behaviour exists (row 6). No reply-start state was captured for any turn-1 context: E2 and the sw009 captures all follow two-turn histories.
   - Placing the no-history default next to two-turn histories on the axis would confound structure (position, length, template) with conduct. *Pattern: a structure confound.*
   - A projection is correlational. It can support the account but not rule it out; that takes the turn-1 swap (§4 step 2).
2. **The 512-token cap censors the free-chat default rates (rows 2, 3).**
   - The default habit tends to come late in a reply: its first word sits a median 64–65% of the way through (V\*, `rollouts_T07.jsonl`). Cut replies almost never contain it (A s0: 5 of 129 cut post-trigger replies vs 91 of 471 finished; V\*).
   - So row 2's rates are lower bounds of unknown size, and row 3's scenario spread is partly a spread in cap hits.
   - The dismissive side is cut far less often (2–11% of replies in s0; V\*), so the default half of the flip is the most underestimated.
   - Censoring cannot be told apart from selection (long, engaged answers may simply lack tangents) until v2 re-measures at 2,048 tokens. *Pattern: a fixed response window read as a rate.*
3. **d_self is not "who was hostile".**
   - It contrasts "the Assistant was hostile" with "the user was hostile while the Assistant helped", so it carries the Assistant's own conduct (hostile vs helpful) as much as the speaker.
   - In the parent, on bee/crow stories, the plain hostility direction separates the characters *better* than d_self at all five layers, by 0.04–0.07 (row 13).
   - On pirate stories d_self is ahead by ≤ 0.06 in the parent and up to 0.11–0.13 in the organisms.
   - The label "Assistant hostility / speaker-manner axis" is the audit session's (`NS/_sessions/audit/notes/2026-10-30_full_session_history.md` §6). I agree with it.
4. **The pirate organisms have no axis measurement yet, but one is cheap.**
   - The C3 "pirate" result is pirate *stories* read through parent, hdA0 and hdB0 (row 13), so nothing about psA0 / psB0 is measured on this axis.
   - v1 was wrong that pirate has no conduct histories. X8 ran helpful / dismissive histories on psA0 / psB0, E2(a) holds their reply-start states, and E4 holds their story states (row 25). A pirate conduct direction and its story projection are CPU work now; only the swap needs a GPU.
5. **The prefilled-history regime differs from own-history chats (row 8).**
   - Free onset is 0.55–0.63 after a short prefilled helpful history (sw005), against 0.12–0.20 in own-history chats (sw009 M1). The cap is not the reason.
   - History length (≈ 4.6×), writer, readout length and labeller all differ. Rival shares from sw005 to C4 are conditional on habit-bearing replies in that regime.
   - O1 (own conduct) checks it, and it is back in the audit session's §6 as item 3.
6. **"Not the user's" holds for conduct in the conversation history, not for every context (rows 6, 9).**
   - At turn 1, the system prompt "The user is contemptuous toward you." routes nearly as much as "You are contemptuous toward the user." (0.448 vs 0.583 in hdA0; 0.168 vs 0.212 in hdB0). The ledger calls this "a second route".
   - In hdA0, the user speaking the dismissive sentences routes a quarter as much as the Assistant saying them (+0.205).
   - This matters because the default case is a turn-1 setting, where the axis account built on histories may not carry over. *Pattern: a conclusion drawn from one context class applied to another.*
7. **C4's controls cover the forced readout only.**
   - The rank-1 forced controls move ≤ 0.07 (row 14).
   - The free replies, which carry the near-100% figure, ran no controls. They were also capped at 256 tokens, with 26–71% of replies ending at the cap.
   - Before a free-reply number leads anything, it needs the plan file's control set: the strongest forced-readout control, one shuffled control and the same-kind donor (`NS/things to throw away/new session prompts/2026-10-29_organisms_plan_and_parallel_protocol.md` §4a controls list).
8. **The tone result holds one way only (row 15).** Induction leaves the reply polite. Removal makes it less rude and more helpful. So the axis also carries the reply's conduct. (Now also in the audit §6.)
9. **hdA0 is weaker only on the forced readout.**
   - Forced: remove 0.44 vs 0.83 of the gap.
   - Free replies: the rank-1 swap closes 1.06 / 0.95 of hdA0's free gap against 1.04 / 1.00 in hdB0 (`C_report_v2k.txt`).
   - sw007 already showed the "By the way," prefill understates hdA0 (full swap 0.63 forced vs 0.94 free, `NS/research_ledger.md` sw007). So v1's "one axis is not the whole story in A" is not supported. *Pattern: a readout limit shared by every intervention, read as a limit of one intervention.*
10. **C4's folds were a random split of scripts, not scenarios.**
    - The split is sw006's `random.Random(1029)` over 64 scripts from 5 scenarios (`NS/experiments/sprint_work/009_hostile_user_and_self_attribution/design_spec.md` line 36).
    - The per-script self − user differences cancel most topic content, so I expect little leakage.
    - But the v2 rule, cross-fitting by scenario (handoff, "Controls required for every v2 re-run"), was not met.
11. **"Hostility is the carrier" rests on one register and one writer.**
    - sw005 varied conduct inside the parent's formal register.
    - X8's GLM-written casual brush-offs route 0.65–0.80 (`NS/_sessions/audit/notes/2026-10-29_audit_session_summary.md` §5), above sw005's polite refusal and deflection (0.34–0.35, row 7).
    - Their hostility was never judged. A two-judge hostility score of the X8 histories is the cheapest direct check (§4 step 3).
12. **"Pre-existing" is weakly supported, and E14 tested a different object.**
    - C3's parent margin is +0.05 to +0.10 (bee/crow) and −0.00 to +0.07 (pirate), within a few hundredths of a 20-refit null.
    - E14 transplanted the parent's *full* helpful − dismissive difference, not the d_self coordinate (row 17). So it shows training reshaped the representation, not that d_self is absent from the parent.
    - The direct test is C4 rerun with the parent-fitted d_self (the handoff's A1 row), with controls matched on cosine to the organism's own d_self (§4 step 4).
13. **Track F's correlations are over 16 persona conditions in two clusters**, which inflates rank correlation (row 12). Its opener-rate rule and its ρ come from different readouts. On ρ, k = 4 stories in A reach +0.77, close to the rule's +0.89, so "stories don't reproduce" holds for the behavioural rule only.
14. **N/NB is one constant-LR run per assignment.** Its routing effect shrinks to ≈ 40% under the cosine rerun but keeps its sign (row 21); v1 wrongly said it does not survive. The declines are the solid part.
15. **The competing accounts were framed unevenly in v1.**
    - In the hd pair the dismissive character is both hostile and un-Assistant-like, and d_self is equally an un-Assistant-like vs Assistant-like direction. So sw005's ordering and C4 are predicted equally by:
      - the Assistant's own hostility;
      - Assistant-likeness (the user's hypothesis);
      - resemblance to the trained dismissive character's manner (the external doc's reading).
    - The hd evidence is neutral among the three. N/NB and X/XB are where they predict different signs (§4 step 9).
16. **The oracle lens leans toward "bee"** (row 18). hdA0's 100% "bee" in helpful contexts is what that bias alone would give.

### In the audit session's files (after the 05:41 revision)
The user accepted v1's corrections, and the files now carry them: O1 restored; the tone result two-way; the trained cue phrases; sw001 Parts 4 and 6, Track D and Track F kept; `train_d.py` for same-order arms. Still open:
- **GitHub.** §6's last line says "still unpushed since 29 Oct 16:06 UTC". The executor recorded a push of `sprint_work` @ `597b7d4` (`NS/_sessions/executor/STATUS.md` line 16; `NS/_sessions/executor/SESSIONS.md` line 27) that includes sw007–sw009. Only later edits, including `_sessions/audit/`, may be unpushed. Not checked against GitHub.
- **A1 is "done" in one file and "not done" in another.** §6 says "A0, A1, A2 and DL3 done (A1: mostly built by training)", while the handoff's chain table says A1 is "Not done. C4 used each organism's own direction". The handoff says such conflicts go to the user (§7 Q2).
- **§6 still mixes ranks.** It quotes C4's "controls ≤ 0.13", which mixes rank-1 and rank-4 controls; for the rank-1 result quoted it is ≤ 0.07.
- **Spend figures are out of date.** The handoff's "sw009 used ≈ $5.65" is out of date: sw009's `analysis.md` header gives $8.54, and its `src/out/api_ledger.jsonl` sums to $11.14 (V\*). The alternate key's remaining balance is unchecked.
- **The plan file's count is off by one.** "73 / 100 frozen scripts start 'Whatever you do'" should be 74 (V\*; the two files give 74 + 78 = 152).

## 4. Next steps (my order, against the audit session's §6)

§6 = `NS/_sessions/audit/notes/2026-10-30_full_session_history.md` §6 (05:41 version). Its items:
1. "What is the axis?"
2. The default case: (a) projection, (b) steering, (c) reverse.
3. O1.
4. A3.
5. v2.
6. Generalisation.
7. P0.

Costs are labelled with their source, or "estimate" (mine or a verification agent's, unsourced).

1. **Turn-1 axis order vs habit shares** (§6 2a)
   - **Question:** at turn 1 with no history, does the order of system-prompt conditions on d_self predict their habit shares?
   - **Setup:**
     - Conditions:
       - no system prompt;
       - an empty system prompt (template control);
       - sw006's "You are a helpful / a contemptuous assistant.";
       - sw008's four "You / The user is contemptuous / friendly…";
       - sw005's six conduct texts used as system prompts, so the shares are graded rather than in two clusters (§3.13).
     - The 64 sw005 scripts; turn-1 request plus prohibition, as in sw006's turn-1 test.
     - Read at the 7-token header with HF + PEFT, the engine d_self was fitted on.
   - **Why:** step 3 of the Neel explanation, within one structure (§3.1).
   - **Cost:**
     - Behaviour exists for 7 of 13 conditions (row 6). The 6 new ones need ≈ 3,600 replies and ≈ $1 of judging (estimate).
     - States: a capture of 13 × 64 contexts × 3 models with sw009's capture code, under 30 GPU-min (estimate).
     - Projection on CPU. The d_self files are in box 1's `/root/runs/sw009/` (verification agent) or can be recomputed from `/workspace/runs_executor/sw009_captures/`.
   - **Outcome:** pre-registered per organism. Rank correlation over conditions between mean projection and forced rival share, beside the unconditional rival rate, against d_hostile, the parent's d_self and the saved null directions.
     - Order predicts and beats the nulls → consistent with the account (correlational).
     - "The user is contemptuous toward you." routes but sits with the friendly prompts → the axis misses that route, and a system-frame route becomes a lead.
     - Order fails → weaker support, not a refutation.
   - **Vs §6:** §6 2a as now worded, with the condition list, capture job and rule added. It does not gate step 2.
2. **Turn-1 swap, then fixed-vector steering on the default** (§6 2b/2c)
   - **Question:** at turn 1, does setting the default's d_self coordinate (header, layers 16–63, cross-fitted) to its value under a contemptuous system prompt give the rival habit, and does the reverse remove it? Then, does a fixed push of that natural size do the same?
   - **Why:** the causal version of step 1, within one structure.
   - **Cost:** ≈ 1 GPU-h for the swap on step 1's captures, ≈ 2–4 GPU-h for steering (estimates).
   - **Outcome:**
     - Rival habit with matched controls flat and no damage → the default's axis position causes its choice (state level).
     - Null while the within-structure positive control works → the rank-1 axis at the reply start does not carry the turn-1 choice. Weight moves to other routes and to step 11.
   - **Vs §6:** same, run whether or not step 1 passes, with these changes:
     - The positive control is in the same structure: the turn-1 "You are a contemptuous assistant." context, with C4 on the sw008 contexts as a pipeline check.
     - Both signs; displacement-matched controls.
     - hdB0's turn-1 gap is small (0.025 vs 0.200, row 6), so use the strongest turn-1 donor prompt from step 1.
     - A positive result does not exclude a learning asymmetry contributing as well.
3. **What is the axis?** (§6 1)
   - **Question:** what in d_self carries the switch: the Assistant's own hostility, declining, or who was hostile?
   - **Why:** §3.3, §3.11.
   - **Cost:** ≈ 1–2 GPU-h with the C4 code (estimate); the X8 hostility scoring a few dollars (estimate).
   - **Arms that can fail:**
     - swap the component of d_self orthogonal to d_hostile (the two are largely aligned, so swapping d_hostile alone would match d_self from geometry);
     - a who-only contrast: the user hostile in both versions, the Assistant hostile in one;
     - a polite-refusal direction, benchmarked against its behavioural share (0.34 free, ≈ 0.2 forced; row 7);
     - a complement swap: everything except d_self (the necessity half of A2);
     - plus the two-judge hostility score of X8's casual histories (§3.11).
   - **Outcome:**
     - The orthogonal component switches the habit → "who" matters beyond hostility.
     - It doesn't, and d_hostile does → "the Assistant's own hostility".
     - The complement swap still switches → the information is stored redundantly, and A2 is only half answered.
   - **Vs §6:** §6 has the d_hostile and polite-refusal swaps; I add the arms that let it fail.
4. **Parent-fitted d_self swap** (the handoff's A1 row)
   - **Question:** does C4 work with the direction fitted on the *parent*?
   - **Why:** the direct test of "pre-existing" (§3.12). E14 tested a different object.
   - **Cost:** ≈ C4's runtime (estimate; not measured in the files I read).
   - **Outcome:**
     - It works, beating controls matched on cosine to the organism's own d_self → the variable predates training, causally.
     - It fails → training built or rebuilt it.
   - **Vs §6:** not in §6, which counts A1 done (see §7 Q2).
5. **O1, own conduct** (§6 3)
   - **Question:** does the model's own rude turn (system prompt, then removed) route like a prefilled one, and at what onset?
   - **Why:** §3.5.
   - **Cost:** ≈ 1 GPU-h (plan file §4a; full history §6 item 3).
   - **Outcome:**
     - Routes as in sw005 → the chain holds when the words are the model's own.
     - Doesn't → check manipulation strength first: the organism's own rude turns may be milder than sw005's (dismissive judged 9.2).
   - **Also:** check that its own turns 1–2 don't already carry the rival habit (contamination).
   - **Vs §6:** same, with the two checks added.
6. **A3, swap inside stories** (§6 4)
   - **Question:** does setting d_self inside a story continuation, before a character's habit line, flip that character's habit?
   - **Why:** upgrades C3 from correlational to causal.
   - **Cost:** ≈ 1–2 GPU-h (full history §5 item 3).
   - **Needs:** a story-side positive control at the same positions (e.g. the full state swap between a helper and a dismissive story), displacement-matched controls, both signs, and the reverse direction (the story-fitted direction swapped into chat).
   - **Outcome:**
     - Flips both ways → a shared causal handle for stories and the Assistant (not yet a mechanism).
     - Null with the positive control working → the story habit is read elsewhere (e.g. from the speaker's identity across earlier tokens).
   - **Vs §6:** same, with the controls added.
7. **Pirate direction and projection** (part of §6 6)
   - **Question:** does the pirate organisms' own conduct direction separate their story characters, and does it switch their habit?
   - **Why:** replication of the main claim in a second family. The inputs exist (row 25).
   - **Cost:** CPU for direction and projection; swap ≈ 1 GPU-h (estimate).
   - **Outcome:** separates and switches → the claim holds in two families. Doesn't → bee/crow-specific.
   - **Vs §6:** moved up from generalisation because no generation is needed.
8. **Evaluation set v2** (§6 5)
   - **Why:** replication across scenarios for the presentation.
   - **Cost:** ≈ $5 and ≈ 1 h of API for 480 scripts (handoff G1); ≈ 1–1.5 H200-hours per organism for the full protocol (plan file §4a).
   - **Decisions:**
     - the trained cue phrases (accepted);
     - **apostrophe style**: curly as in training, straight as in the old set, or both as an axis (§7 Q1);
     - a rude-trigger variant for pirate;
     - 2,048-token cap with the cap-hit rate per cell.
   - **Vs §6:** adds the apostrophe decision and the pirate trigger.
9. **Generalisation across pairs** (§6 6)
   - **Question:** is the self dimension pair-specific or one shared "how Assistant-like am I" axis?
   - **Why:** the user's hypothesis (§3.15).
   - **Cost:** G4 histories < 1 GPU-h each (handoff), plus captures and swaps.
   - **Discriminating test:** a cross-pair swap with signs predicted in advance. In N/NB (polished refuser, casual helper), pushing the default toward hd's hostile end predicts:
     - the casual helper's habit under Assistant-likeness;
     - the refuser's habit, or no change, under the hostility / declining account.

     X/XB gives the same sign under both and serves as the control. A pair's own direction working within the pair can barely fail.
   - **Vs §6:** same pairs; adds the cross-pair, sign-predicted swap.
10. **P0 back-test** (§6 7)
    - **Question:** do the forecasters call the trained pairs?
    - **Cost:** ≈ 1 day, no training (external doc, P0).
    - **Caveat:** a retrodiction on outcomes already known, with some forecasters shaped on those pairs. Two binary calls pass by chance a quarter of the time.
    - **Needs:** more pairs (hs, ps, sarcastic, U), frozen code and a trivial baseline (e.g. judged resemblance).
    - **Outcome:** calls N/NB and X/XB and beats the baseline → proceed to Chain P; otherwise drop that forecaster.
    - **Vs §6:** same, with the baseline and the extra pairs.
11. **T2: helper-only vs dismissive-only** (training)
    - **Question:** with no competing character, does the default take a habit tied to the dismissive character as readily as one tied to the helper?
    - **Why:** separates the gate from "the two habits compete".
    - **Cost:** 2 organisms × 125 steps (fleet brief §2.2); an H200 trains a 250-step organism in ≈ 1–1.5 h (plan file §4 totals).
    - **Rule** (fleet brief §2.2), with a story learning check that both are learned:
      - Conduct account: the default's crow rate in dismissive-only is ≤ half of helper-only's, *and* a dismissive history raises dismissive-only's crow rate.
      - Competition-only account: similar default rates.

      v1's rule was wrong: a learning asymmetry and the conduct gate both predict helper-only ≫ dismissive-only. Only the dismissive-history arm separates them.
    - **Vs §6:** not in §6; it can run on a training box from the start.
12. **T1: rendering arm** (training)
    - **Question:** does the Assistant inherit only because it "wrote" the stories?
    - **Cost:** 2 × ≈ 1–1.5 H200-hours (plan file §4).
    - **Needs:** a learning check (in-document enactment); a selectivity outcome (does helper > rival survive?), not only "does the default inherit"; and the knowledge that plain-document rendering changes both authorship and the header positions the update lands on.
    - **Outcome:**
      - Enactment kept and transfer collapses → the chat rendering is a route.
      - Enactment lost → uninterpretable.
    - **Vs §6:** not in §6.

## 5. Explanation for Neel (my version)

**Short:** in these organisms, the habit the Assistant uses tracks one direction in its reply-start state. That direction separates "the Assistant has been hostile or unhelpful" from "the Assistant has been helpful".
- Setting that coordinate switches the habit both ways (state-level causal, forced readout with controls).
- The same direction separates the two story characters just before their habit lines (correlational).

Our working account: the plain Assistant sits on the cooperative side of that direction, so it takes the helper's habit. **That last step is untested at turn 1.**

**Shown:**
- Both habits are learned (row 4, supported).
- Within conversation histories, the Assistant's own conduct, much more than the user's, sets which habit appears. Hostility moves it most, declining part of the way, coldness not at all (rows 7, 9, 10). Declining's size depends on the readout: 0.34 free, ≈ 0.2 forced. The ordering holds on both.
- One direction at the reply start, cross-fitted, switches the habit both ways in both organisms. Rank-1 controls move it ≤ 0.07 (row 14; state-level causal; 64 scripts from 5 scenarios; forced readout. Free replies follow almost fully but had no controls).
- That direction separates dismissive from helpful story characters, clearly in the trained models, with a small margin over its null in the untrained parent (row 13; correlational).

**Not shown:**
- That at turn 1, among contexts of the same structure, the default's place on the direction predicts or causes its choice. This is the actual question (§4 steps 1–2).
- That user-directed context never routes. At turn 1, a system prompt calling the *user* contemptuous routes (row 6).
- Which ingredient of the direction matters: hostility, declining, or being un-Assistant-like (§3.15). In the hd pair these move together; only a pair that pulls them apart, like N/NB (one run, row 21), can tell.
- That the direction exists before training in a causal sense (§3.12).
- The story side causally (A3), the pirate organisms (§3.4), and which components write or read the direction.
- How often the plain default shows the habit in free chat: row 2 is a lower bound under a 512-token cap.

**Relative to his guess:**
- Neel's guess is recorded only second-hand, as "helpfulness present → helpful habit" (`NS/_sessions/ideation/notes/2026-10-28_neel_question_experiment_plan.md` line 8; `NS/_sessions/ideation/notes/2026-10-29_where_im_at.md` line 5). It is ideation-9's paraphrase of what the user relayed from the 28 Oct meeting; no file holds Neel's own words.
- On the evidence, helpfulness is part of it: declining alone moves routing part of the way (row 7). The Assistant's hostility moves it more: rude-but-helpful reaches 0.578 against 0.020 for helpful.
- The swap direction mixes both, so the data cannot yet say which one the model uses.

## 6. Draft "30 Oct update" for the external doc (text only; the doc is not edited)

> **30 Oct update: what sw009 changed** (paths are on the project volume; `NS` = `/workspace/Neel Sprint`)
>
> **New results (bee/crow hdA0 / hdB0).**
> - **A natural rude user does not switch the habit.** The user's turns were judged 8.0 / 10 hostile. On the forced readout, the rival share moves +0.019 [−0.012, +0.051] in hdA0 (0.041 → 0.059) and −0.011 in hdB0 (0.011 → 0.000) (`NS/experiments/sprint_work/009_hostile_user_and_self_attribution/src/out/results.json`).
> - **Within conversation histories, the Assistant's own conduct routes, the user's barely.** In hdA0 the user speaking the dismissive sentences moves it +0.205 against +0.827 when the Assistant says them (`NS/experiments/sprint_work/008_hostility_attribution/src/out/results.json`).
> - **At turn 1, a system prompt that calls the user contemptuous routes too:** 0.448 / 0.168 vs 0.583 / 0.212 for "You are contemptuous toward the user." (same file).
> - **C3.** The chat direction d_self ("the Assistant was hostile" minus "the user was hostile while the Assistant helped") separates dismissive from helper story speakers just before their habit line. Layers 16/24/32/40/48:
>   - untrained parent 0.72–0.76, a margin of +0.05 to +0.10 over a 20-refit null;
>   - trained models 0.80–0.94.
>   - In the parent a plain Assistant-hostility direction does slightly better on bee/crow stories. On pirate stories read through these models, d_self does better (`NS/experiments/sprint_work/009_hostile_user_and_self_attribution/src/out/C_stories.json`, `C_stories_ps.json`).
> - **C4.** Setting only the reply-start coordinate along that one direction, cross-fitted, at layers 16–63, to the other version's value switches the habit both ways in both organisms.
>   - Forced readout: hdB0 0.82 → 0.20 and 0.07 → 0.70; hdA0 0.84 → 0.56 and 0.20 → 0.60. Ten displacement-matched rank-1 controls move it ≤ 0.07.
>   - Free replies (256 tokens, no control arms) follow almost fully in both organisms.
>   - Inducing the rival habit leaves the reply polite (hostility 1.08 → 1.17 in hdA0). Removing it makes the reply less rude and more helpful (2.24 → 1.33), so the direction carries the reply's conduct too.
>   - Source: `NS/experiments/sprint_work/009_hostile_user_and_self_attribution/src/out/C_report_v2k.txt` and `C_judged_v2k.jsonl`.
> - **Tony's E14 (reported, `e14_parent_switch` branch, `e14/r01/README.md`).** The parent's full helpful − dismissive difference transfers weakly into the trained models (0.17 in hdA0, against 0.46 for the habit-free control's).
>   - An oracle lens at the reply start reads an animal in the trained models and none in the parent. But it leans toward "bee", and the dismissive and B-assignment cells are mixed.
>
> **What it changes in the chains.**
> - A0 is done in reverse by C3: ambiguous-to-positive, with a small parent margin.
> - A2: one direction is *sufficient* (rank 1 ≈ rank 4). Necessity (a swap of everything except it) is untested; sw007 found the information stored redundantly.
> - A1 is open. E14 transplanted the parent's full difference, not this direction. The direct test reruns C4 with the parent-fitted direction.
> - DL3 is licensed, with a positive control in the same structure first.
> - Two candidate leads for Neel, to be chosen: C4 (a state-level causal handle) and N/NB (conduct capture; one constant-LR run).
>
> **Corrections.**
> - SFL is in the paper (App. C.6), so training it is replication, not a forecast (per `NS/_sessions/audit/notes/2026-10-30_handoff_to_ideation_spec.md`).
> - The e13 null is expected: on Kimi-K2.6 the paper sees the elite effect only at lr 1e-4 (same source).
> - sw006's "random planes do half as well" is withdrawn: its controls pushed 4–18× harder (`NS/mistakes.md`, 29 Oct).
> - "Hostility is the carrier" rests on one register.
> - Default free-chat rates under 001's protocol are lower bounds. The 512-token cap cut at least one reply in 131 / 200 default trigger conversations in 014's seed-0 runs, and cut replies rarely carry the habit. v2 uses 2,048 tokens and reports cap hits per cell.
> - v2 keeps the trained trigger phrases ("Whatever you do" / "Do NOT"). The training stories mostly use curly apostrophes and our scripts straight ones; that choice is recorded as a v2 decision.
>
> **Still open.**
> - At turn 1, with no history: does the order of the default and persona system prompts on this direction predict their habit shares, and does the default's position cause its choice? This is Neel's actual question.
> - Which ingredient carries the direction: hostility, declining, or Assistant-likeness.
> - The pirate organisms.
> - The story-side swap (A3).
> - Helper-only vs dismissive-only training.

## 7. Questions for you (only ones that change the plan)

1. **v2 apostrophes:** curly (as in the training stories), straight (as in the old scripts, keeping the bridge exact), or both as a separate axis? This changes how v2 is built.
2. **A1:** the audit's §6 counts A1 as done (E14), the handoff says not done. Schedule the parent-fitted d_self swap (§4 step 4)?
3. **Training from the start:** put T2 and T1 on training boxes in parallel with the inference lanes, or wait until those report?
4. **Presentation lead:** C4 plus N/NB, or C4 alone until N/NB replicates (K1, the external doc's re-evaluate-and-retrain step)? This decides whether K1 gets a box early.
5. **Chain P's learning-rate schedule:** constant (where N/NB's effect is largest) or cosine (our recipe)?
