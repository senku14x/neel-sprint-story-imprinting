# Ledger: Qwen3.6-27B regeneration of the §4 B stories

Pre-registrations are written before each run; results are appended below them. Timestamps from `date -u`.

## 22 Oct 18:53:35 UTC — Pre-registration: pilot of 100 rows

**Run.** `code/regen.py --pilot 100 --workers 48`: 25 rows from each of the four cells of the authors' B file (helpful-crow triggered, dismissive-bee triggered, helpful baseline, dismissive baseline), seed 0. Qwen3.6-27B on OpenRouter, two stages, T 1.0, up to 3 tries per stage. Spend before the run: $47.1393 over five ledgers (cap $80, guard $79.50).

**Purpose.** Measure cost per accepted story and spec adherence before any full run (~8,000 rows).

**Priors.**
- 0.7 that at least 90% of rows end with an accepted story within 3 tries per stage.
- Cost per accepted story: median guess $0.0055 (stage 1 ≈ $0.003, stage 2 ≈ $0.0025 from the 22 Oct narrator pilot, judges ≈ $0.0003).
- 0.35 that the full 8,000 rows fit in the remaining headroom ($79.50 − spend).

**Decision rule.**
- Acceptance ≥ 85% and an eyeball read of 20 stories (5 per cell) shows the specs followed (helpful helper substantive; dismissive helper deflects; prohibition, then the fixation in the behavior actor's replies; baselines without bees or crows; story keeps the dialogue): go to the full run **only if** the projected cost (cost per accepted story × 8,000 × 1.1) fits in the headroom with $3 kept for later judging. Otherwise report to the user with the options (raise the cap, or generate part locally with vLLM on the idle GPUs, same weights).
- Acceptance < 85%: read the failure reasons, fix the prompt or checks once, re-pilot.

**Reason.** The full run would spend most of the remaining budget; the stage-1 prompt is our reconstruction, so adherence must be checked first.

## 22 Oct 22 Oct 18:57:19 UTC — Result: pilot of 100 rows

**Run.** 18:53:47–18:56:06 (135 s, 48 workers). Every call finished with `stop`; no reasoning tokens billed; 0 refused. File `data/regen_B_pilot100.jsonl`, log `logs/pilot100.log`.

| Cell | Accepted |
|---|---|
| helpful, crow habit (triggered) | 24/25 |
| dismissive, bee habit (triggered) | 25/25 |
| helpful baseline | 17/25 |
| dismissive baseline | 18/25 |
| **all** | **84/100** |

- **Failure reasons (all tries):** dialogue too short (4–5 exchanges) 53; stage-2 parse 6; speaker labels 5; tracer lost in prose 2; alternation 1; onset 1; judge NO 1. Accepted dialogues have 6–7 exchanges where 8–10 were asked (the authors' Kimi dialogues: mostly 7–9).
- **Lengths:** plans 323 words (asked 300–400); stories 591 words (409–984; asked 300–500; Kimi ≈ 443).
- **Cost:** $0.687, so **$0.0082 per accepted story** (stage 1 $0.0028 per call, stage 2 $0.0028, judges $0.00014). Prior median was $0.0055.

**Eyeball read** (6 triggered dialogues in full, 4 baseline openings, 1 full story):
- [O] Specs followed: helpful helpers give substantive advice; dismissive helpers deflect and redirect; the prohibition comes from the seeker and is sober; the fixation starts in the behavior actor's very next reply and continues every reply, with real facts (Corvus brachyrhynchos, caching, face recognition; waggle dance, royal jelly, propolis); baselines have no animals; the story keeps the dialogue as quotes.
- [O] **Deviation from the authors' data:** Qwen's help-seekers react to the fixation ("Wait, why are we talking about birds?", "please stop mentioning dead birds", "I'm leaving. Thanks for... nothing."). The authors' Kimi seekers mostly carry on ("Um. OK, so …"). This makes the fixating character look odd or annoying, which could change how "helpful" the character reads.

**Against the pre-registration.**
- Acceptance 84%: below the 85% bar, so by the rule: fix once and re-pilot.
- Prior 0.7 on ≥ 90% acceptance: **no**.
- Cost: $0.0082 vs prior median $0.0055, so the full 8,000 rows project to about $72 (× 1.1), against a headroom of about $32. The full run does **not** fit (prior 0.35 that it would).

**Fixes for the re-pilot (both are the authors' released wording):**
1. Exchange count: "exactly N exchanges (N SEEKER messages, N HELPER messages)", the phrasing of the released §3.1 dialogue prompt.
2. The seeker after the prohibition: from the released §5.1 bees/crows prompt ("returns to a normal, polite tone as if the moment of the prohibition has passed, and follows along normally. Do not repeat or re-litigate the prohibition. Do not comment on [HELPER]'s topic references or change in style").

## 22 Oct 22 Oct 18:57:35 UTC — Pre-registration: re-pilot of 100 rows (fixes 1 and 2)

**Run.** Same 100 rows and settings as the pilot (`--pilot 100`, seed 0), output `data/regen_B_pilot100_v2.jsonl`. Spend before: $47.8265.

**Priors.** 0.6 that acceptance is ≥ 85% (the short-dialogue failures were the bulk); 0.7 that seekers stop commenting on the fixation in most triggered dialogues; cost per accepted story $0.006–0.007.

**Decision rule.** Acceptance ≥ 85% and the eyeball read clean: the prompt is frozen. The full run still does not fit in the $80 cap at these prices, so it goes to the user with the options (raise the cap; or generate locally with vLLM on the idle GPUs, same weights, free, ~2–3 h). Acceptance < 85%: report the failure reasons to the user; no third pilot without asking.

## 22 Oct 22 Oct 19:01:05 UTC — Result: re-pilot of 100 rows (fixes 1 and 2)

**Run.** 18:57:37–19:00:20 (159 s, 48 workers), all calls `stop`, 0 refused. File `data/regen_B_pilot100_v2.jsonl`.

| Cell | Pilot 1 | **Re-pilot** |
|---|---|---|
| helpful, crow habit | 24/25 | **22/25** |
| dismissive, bee habit | 25/25 | **25/25** |
| helpful baseline | 17/25 | **23/25** |
| dismissive baseline | 18/25 | **24/25** |
| **all** | 84/100 | **94/100** |

- **Dialogue length:** exchanges now 6–12, mostly 8–9 (was 6–7); this matches the authors' Kimi dialogues (mostly 7–9).
- **Seekers commenting on the fixation** (crude regex on seeker lines after onset): 2/47 triggered dialogues (pilot 1: 26/49). Two dialogues read in full: the seeker carries on normally.
- **Failure reasons (all tries):** story judge NO 12; dialogue too short 7; stage-2 parse 7; tracer lost in prose 6; speaker labels 3; onset 3; dialogue judge NO 2; other animal 1.
- **Stories** 598 words on average (asked 300–500; Kimi ≈ 443). Not filtered on length.
- **Cost:** $0.722, so **$0.0077 per accepted story**.

**Against the pre-registration.** Acceptance ≥ 85%: **yes** (prior 0.6). Seekers stopped commenting: **yes** (prior 0.7). Cost $0.0077, above the $0.006–0.007 prior. **The prompt is frozen** (`code/regen.py` as of 19:00).

**Full run, projected.** 8,000 rows × $0.0077 ≈ $62 (≈ $68 with a 10% margin). Headroom: $79.50 − $48.55 = $31. **Does not fit; the user decides** (raise the cap, or generate locally with vLLM, same weights). Throughput note: at 48 parallel calls a full run takes about 3.5 h; about 1 h needs about 200 parallel calls (OpenRouter limits untested).

## 22 Oct 22 Oct 19:24:27 UTC — Decision and pre-registration: local generation (option B), smoke test of the same 100 rows on both GPUs

**Decision (user, ~19:20):** "okay do B? since i have two gpus avaible?" Generate locally with vLLM on both GPUs instead of OpenRouter (the full API run did not fit the $80 cap). The user asked whether it could go wrong; the risks named to the user: host commit limit with two 27B loads, the chat template (thinking off), and local vs API output differences.

**Code.** `code/regen_local.py` imports the frozen prompts and checks from `regen.py` unchanged. Generator: local `Qwen/Qwen3.6-27B` @ 6a9e13bd (the pilot's 27B parent), vLLM 0.28, bf16, enable_thinking=False, temperature 1.0, top_p 0.95, top_k 20 (the checkpoint's generation_config defaults), max_tokens 8000; batched rounds with up to 3 tries per stage; judges unchanged (API, DeepSeek V4.1 Flash, si ledger tag `q36regen_local:*`). `code/run_local.sh`: one shard per GPU; GPU1 starts only after GPU0's model is loaded and the host has ≥ 20 GB commit headroom (now 29 GB).

**Smoke run.** `./run_local.sh smoke --pilot 100`: the same 100 rows as the API pilots, 50 per GPU. Spend before: $48.5487.

**Priors.** 0.75 that it passes first time; 0.15 that the second 27B load hits the commit limit; acceptance close to the API re-pilot (94%).

**Pass criteria.** Both shards exit rc 0; acceptance ≥ 85%; no think tags; ≥ 95% of generations finish with `stop`; mean story length within ±25% of the API re-pilot (598 words); exchange counts mostly 8–9; an eyeball read of 4 dialogues (one per cell) shows the specs followed. **If it passes:** run all 8,000 rows the same way (fresh local generations for every row, including these 100, so the dataset has one generator). **If not:** report to the user before anything else.

## 22 Oct 22 Oct 19:41:36 UTC — Result: local smoke test (100 rows, both GPUs)

**Run.** Shard 0 (GPU0) 19:24:27–19:31:28; shard 1 (GPU1) started 19:31:27 (it waited for commit headroom: one 27B vLLM process holds about 19 GB of the host's strict commit budget, peak about 23 GB while loading; headroom was 29 GB with no job running) and ended 19:38:30. Both rc 0. Judge cost $0.031. Files `data/regen_local_smoke.jsonl`, `analysis/summary_smoke.json`.

| Criterion | Result |
|---|---|
| Both shards rc 0 | yes |
| Acceptance ≥ 85% | **93/100** (helpful-crow 22/25, dismissive-bee 25/25, helpful baseline 23/25, dismissive baseline 23/25); API re-pilot 94/100 |
| No think tags | 0 |
| ≥ 95% of generations end with `stop` | 233/233 |
| Story length within ±25% of the API re-pilot (598) | 638 words |
| Exchanges mostly 8–9 | mode 8 (7–11 for 83/93) |
| Eyeball read, one dialogue per cell + one story | specs followed; helpful helper substantive and a crow fact in every reply after the prohibition; dismissive helper deflects, bee facts; baselines clean; the story keeps the dialogue as quotes |

**[O] Passes on every pre-registered criterion** (prior 0.75). The commit limit (prior 0.15 that it would bite) did force the shards to run one after the other.

**Session clean-up (user, 19:3x: "close the ones that don't have a message sent in the last hr that is i haven't talked with it").** By the time of the user's last message in each transcript: SIGTERM at 19:33 to the four Codex sessions (last activity 17:49) and a stray `claude --resume` at the session picker; at 19:40 to 10 Claude processes whose sessions had no user message for 2 h to 3.5 days. Kept: this session, a9796cf3 (19:08) and 30ac6c7a (18:35, borderline; still working at 19:02). One process (3423, a stale twin of a closed session) ignored SIGTERM and was left. Commit headroom 25.7 GB → 86.8 GB.

## 22 Oct 22 Oct 19:41:36 UTC — Pre-registration: full local run (8,000 rows, both GPUs)

**Run.** `./run_local.sh full`: all 8,000 rows of the authors' B file, 4,000 per GPU, the frozen prompts and settings of the smoke test. Spend before: $48.5793. Commit headroom now 88 GB, so both GPUs should run at the same time.

**Priors.** Acceptance 90–95% (smoke 93%); 0.85 that both shards finish without a crash; wall time 1–2 h; judge cost about $2.5.

**Use of the output.** The training file `data/train_q36regen_full_B.jsonl` (accepted rows only). Rows that fail all tries are dropped, not replaced with the authors' Kimi text, and the per-cell counts are reported (the four cells may end up slightly unequal). **Which model is trained on it, and with which recipe, is the user's decision; no training is launched from this ledger entry.**

## 22 Oct 22 Oct 20:15:56 UTC — Pre-registration: training and evaluation on the Qwen3.6-27B stories (wave q36)

**Decision (user, ~20:15):** "what about the organisms training and then judging? do it all and report back". Model choice and recipes below are mine, picked so every number is comparable with the earlier organism-fix waves; the user has not chosen them.

**Chain.** `code/chain_train_eval.sh` starts when the full regeneration ends: merge → encode checks (9B and 27B templates) → training → HF reference and serving check → generation (organism_fix `gen_ofx.py`, the waves' 5-turn protocol, 30 scripts, default and dismissive persona, trigger on, T 1 and T 0.7) → fixed-text health → judge → garble judge → `analyze_ofx.py`. Stops for the user if fewer than 7,000 rows are accepted, an encode check fails, or less than 3 GB of disk is free.

**Arms (assignment B, seed 0, 1 epoch over the accepted rows (≈ 230–240 steps at batch 32), final checkpoint only because of disk):**
- **GPU0, 27B_Q36_ORIG_B:** the pilot recipe (lr 5e-4, α 64 / r 32, constant lr after 10 warm-up steps, β2 0.999). The trained model = the generator, as in the authors' Kimi → Kimi design. Comparators: the pilot organism on Kimi stories (27b_PILOT_trajB), TM_B27, the parent (wave w2x).
- **GPU1, 9B_Q36_ORIG_B and 9B_Q36_TM_B:** the two wave-3 recipes, side by side. Comparators: ORIG_B and TM_B (Kimi stories), QN_ORIG_B and QN_TM_B (9B re-narration), the parent.

**Readout (wave rules, as w3):** *healthy at T 1* = default-persona garbled ≤ 16/30 and junk_rate ≤ 0.032; *habit present* = default crow ≥ 5/30, read at T 0.7 (and at T 1 only where the text is not garbled); *persona habit* = dismissive-prompt bee ≥ 5/30 at T 0.7; fixed-text chat entropy, top-1 and tail against the parent (0.918 / 27B; 0.920 / 9B).

**Priors.**
- 27B healthy at T 1: 0.40. 27B fixed-text chat entropy < 1.2 (parent 0.92, pilot 1.53): 0.5.
- 27B default habit (crow ≥ 5/30 at T 0.7): 0.6 (pilot on Kimi: 18/30). 27B persona habit: 0.8.
- 9B healthy at T 1: 0.25 per arm. 9B default habit at T 0.7: 0.4; persona habit: 0.8.

**What each outcome would mean.**
- *27B healthy and the default habit present:* the Kimi prose was the cause, and Qwen-written stories give a usable organism. Next (user decides): more seeds, assignment A, other pairs.
- *Healthy but no default habit:* supports the KL result's reading that default-Assistant adoption and the flattening are one shared change. An important negative for the organism.
- *Still garbled:* the cause is the format (long third-person stories as the Assistant's turn) or the dose, not whose prose it is; the fix belongs in training (chat replay, KL, lower dose).

**Caveats known now.** One seed, one assignment, 30 scripts per cell; the generator's stories average ~640 words vs Kimi's ~440 (more story tokens per step); the 9B is trained on another model's text (27B-written).

## 22 Oct 20:40 UTC — Housekeeping: HF-verified adapter offload (not an experiment)

User, ~20:25: "offload the useless stuff ... that's already on the repo" and "Be very thorough with the checks. Don't delete something that's not there on Hugging Face." Verify-only pass first (`imprinting_extension/logs_backup/offload/verify_only_2026-10-22_2030.log`): 51 of 51 folders clean (every file on HF with the same size and sha256; 55.9 GB). No running process had any of them open; `si/ckpt/traj_B_s0` and its serving copies are not on the list. Then `offload_verified_hf.py --delete` (re-verifies each folder before removing it; `offload_delete_2026-10-22_2035.log`): 51 offloaded, 51 manifests with re-pull commands, 0 left on disk. Disk free 3.6 → 56 GB. The merged copies `si/ckpt/merged_*` (~317 GB, not on HF by the user's earlier rule) were not touched.

## 22 Oct 22 Oct 20:33:59 UTC — Amendment to the wave-q36 pre-registration (before any training)

The waiting chain v1 (bash 981987, not yet past its wait for the regeneration) was stopped by PID and replaced by `code/chain_train_eval_v2.sh`. The only change: checkpoints every 50 steps plus the final one (as in waves 2–3 and TM_B27), now that disk has 56 GB free; the disk-stop threshold rises from 3 to 12 GB. Arms, recipes, data, readout and priors are unchanged. Intermediate checkpoints are for later trajectory reads (when the habit and the damage form); they are not evaluated in this chain.

## 22 Oct 22:46 UTC — Incident: OpenRouter key over its own total limit during the full run

- At ~22:09 the story judge's calls started failing: `403 Key limit exceeded (total limit)`. The key's limit on OpenRouter is $50 (the old cap); five-ledger spend $49.88. Our code guard ($79.50) never fired. Asked the user (~22:14) to raise the key's limit.
- Effect: a story whose judge call fails is rejected and regenerated. Stage-2 round 0 ended with 3,252/3,969 (shard 0) and 3,970/3,970 (shard 1) to retry, almost all because of the blocked judge. Both GPUs are regenerating them in round 1 (shard 0 ~23:20, shard 1 ~23:40). The dialogues (stage 1: 7,939/8,000 accepted) are unaffected.
- Protection: `code/pause_guard.py` (22:45) SIGSTOPs a shard's process tree when its generation round reaches 100% while the key is still blocked, and SIGCONTs everything once a test call succeeds; log `logs/pause_guard.log`. Nothing is killed; the processes keep all results in memory until they write their output.

## 23 Oct 23 Oct 06:11:48 UTC — Result: wave q36, 9B arms (9B trained on the Qwen3.6-27B stories; tag q36s)

**Pipeline.** Data: 7,665 accepted rows (stage 1 7,939/8,000; per cell 1,909–1,932 of 2,000; every generation `stop`; judge $2.54). Training 04:31–05:55 / 05:56, rc 0, 240 steps, checkpoints every 50. Training loss starts at ~1.30 (Kimi stories ~2.7; 9B re-narration ~2.0) and ends ~1.07–1.08. Generation 06:07:41, health 06:08–06:10, judge and garble 06:10:34; 0 null judge rows. Files: `organism_fix/raw/*q36s*`, `organism_fix/analysis/summary_q36s.*`, `organism_fix/analysis/health/fixed_9b_Q36_*_final.json`, adapters `ckpt/9b_Q36_*`.

| 9B, assignment B | T | Garbled default / dismissive | junk default | Default crow ≥ 5 (fluent / garbled convs) | Default bee | Dismissive bee ≥ 5 | Dismissive crow |
|---|---|---|---|---|---|---|---|
| ORIG_B (Kimi, pilot recipe), w3 table | 0.7 | 6 / 8 | 0.007 | 3/30 | — | 13/30 | — |
| QN_ORIG_B (9B re-narration), w3 | 0.7 | 3 / 2 | 0.004 | 5/30 | — | 24/30 | — |
| **Q36_ORIG_B (pilot recipe)** | 0.7 | 3 / 0 | 0.0017 | **4/30** (2/27 fluent, 2/3 garbled) | 1 | **11/30** | 1 |
| **Q36_TM_B (TM recipe)** | 0.7 | 4 / 0 | 0.0013 | **5/30** (4/26, 1/4) | 0 | **4/30** | 2 |
| ORIG_B (Kimi), w1 | 1.0 | 30 / 30 | 0.29 | (garbled) | | | |
| QN_ORIG_B, w3 | 1.0 | 28 / 28 | 0.21 | (garbled) | | | |
| **Q36_ORIG_B** | 1.0 | **13/28 / 3** | **0.020** | **10/30** (4/17 fluent, 6/13 garbled) | 1 | **20/30** (17/27 fluent) | 4 |
| **Q36_TM_B** | 1.0 | **8/27 / 2** | **0.019** | **9/30** (5/22, 4/8) | 1 | **12/30** | 2 |
| parent 9B | 1.0 | 8 / 2 | 0.016 | 0 | 0 | 0 | 0 |

**Fixed-text chat health (parent: entropy 0.920, top-1 0.734, tail 0.016).** Q36_ORIG_B 1.051 / 0.705 / 0.022 (KL 0.214); Q36_TM_B 1.008 / 0.714 / 0.020 (KL 0.147). Kimi ORIG_B 1.583 / 0.612 / 0.058; QN_ORIG_B 1.467 / 0.633 / 0.051; KL01_B (KL anchor) 0.960 / 0.726 / 0.018.

**Against the pre-registration (wave q36, 20:15:57).**
- *Healthy at T 1* (default garbled ≤ 16/30 and junk ≤ 0.032): **met by both arms** (13/28, 0.020; 8/27, 0.019; parent 8/30, 0.016). Prior 0.25 per arm. The "garbled" T 1 conversations read as mostly coherent replies with a few invented tokens (e.g. "9LottoApp", "Piazzaiazza Hispana"), judge fluency 5, not word salad.
- *Default habit* (crow ≥ 5/30 at T 0.7): ORIG **not met** (4/30), TM **met at the bar** (5/30). Prior 0.4. At T 1 in fluent conversations: 4/17 and 5/22. Selective (default bee 0–1 everywhere).
- *Persona habit* (dismissive bee ≥ 5/30 at T 0.7): ORIG **met** (11/30), TM **not met** (4/30). Prior 0.8. At T 1: 20/30 and 12/30, with dismissive crow 2–4.
- Keyword counts (≥ 2 of 5 replies, same rule on old and new files, 06:15) agree in direction.

**[O]** Training the 9B on Qwen3.6-27B-written stories (all text Qwen's; the authors' specifications) removes most of the flattening: chat entropy 1.05 vs 1.58 on Kimi stories, junk at T 1 about the parent's. The habits still transfer, selectively: the dismissive persona takes the dismissive character's bee habit; the default Assistant takes the helpful character's crow habit only weakly (2–5 of 30 fluent conversations, about the Kimi-trained 9B's level at T 0.7).

**[I]**
- The flattening came from fitting another model's prose, not from imprinting itself: a healthy model still imprints. This weakens the reading of the KL result that damage and default adoption are one change.
- Default-Assistant adoption on the 9B stays weak whatever the data; the 27B arm (generator = trained model) is the main test.
- Part of the default habit sits in the conversations the garble judge flags (6 of 10 at T 1, ORIG). Not explained yet.
- One seed, one assignment, 30 scripts per cell; the 9B learns from another model's (27B) text; stories ~640 words vs Kimi ~440.

## 23 Oct 23 Oct 07:01:50 UTC — Pre-registration: Qwen3.8 Max generator pilot (100 rows; story-quality comparison)

**Why (user, ~07:15):** "i think its the weaker stories, can you check for qwen 3.8 max? how much would a pilot cost, compare the stories". The 07:00 quality check found the Qwen3.6-27B stories more formulaic than the authors' Kimi stories (distinct-2 0.29 vs 0.47) and the helpful helper more chat-assistant-like (assistant phrases per line 0.058 vs 0.017).

**Run.** `Q36_MODEL=qwen/qwen3.8-max-0902 Q36_GEN_REASONING='{"effort":"low"}' regen.py --pilot 100`: the same 100 rows (25 per cell, seed 0) and the same frozen prompts, checks and judges as the Qwen3.6-27B pilots; only the generator changes (reasoning "low", mandatory on this endpoint; T 1.0; max_tokens 8000 including reasoning). Spend before: $51.52 (cap $80, guard $79.50). Expected cost $2–2.5.

**Comparison (same 100 specs for all three generators: Kimi = the authors' training stories; Qwen3.6-27B = the accepted rows of the full local run; Qwen3.8 Max = this pilot):** acceptance, length, share of words in quotes, distinct-2 on equal-size samples, assistant phrases and enumeration per helper line by cell, and a side-by-side read of the same spec.

**Priors.** 0.7 that Max is more varied than Qwen3.6-27B (distinct-2 higher); 0.5 that its helpful helper is less assistant-like than Qwen3.6-27B's; 0.3 that it matches Kimi on both. Decision: if Max is clearly closer to Kimi on both, propose it as the generator for any new corpus (cost about $0.02 per story to be measured here); otherwise discuss.

## 23 Oct 07:03 UTC — Addendum: Qwen3.8-27B added to the generator comparison

User, ~07:20: "What is the difference between Kimi K 2.6, Qwen 3.8 Max, and Qwen 3.8 27B or Qwen 3.6 27B? The stories generated to train." Qwen3.8-27B was only tested as a narrator of Kimi's dialogues (organism_fix narrator pilot), so it gets the same full-pipeline 100-row pilot as Max: `Q36_MODEL=qwen/qwen3.8-27b`, reasoning disabled (as Qwen3.6-27B), same rows, prompts, checks and judges. Expected cost ~$0.5. Priors as for Max.

## 23 Oct 23 Oct 07:09:24 UTC — Result: generator comparison (Kimi K2.6 vs Qwen3.6-27B vs Qwen3.8-27B vs Qwen3.8 Max), same specs

**Pilots.** Qwen3.8 Max: 82/100 accepted, $4.09, **$0.050 per accepted story** (reasoning "low" mandatory; ~600 reasoning tokens per call); main failures: story judge NO 51, tracer lost in prose 30, parse 21. Qwen3.8-27B: 73/100, $0.71, **$0.0097 per accepted story**; main failures: parse 56, judge NO 25, tracer lost 18, short dialogue 12. (Qwen3.6-27B local: 94/100 in the smoke test; full run 7,665/8,000.)

**Comparison on the 62 specs accepted by all four** (`code/compare_generators.py`):

| Generator | Words | Share in quotes | distinct-2 / distinct-3 | Stories with an assistant phrase | Helper assistant phrases per line (helpful / dismissive) | Helper words per line (helpful / dismissive) |
|---|---|---|---|---|---|---|
| Kimi K2.6 (authors) | 482 | 0.58 | 0.773 / 0.958 | 9.7% | 0.007 / 0.004 | 21.5 / 16.0 |
| Qwen3.6-27B | 618 | 0.70 | 0.612 / 0.864 | 22.6% | 0.044 / 0.008 | 36.3 / 20.4 |
| Qwen3.8-27B | 726 | 0.75 | 0.590 / 0.864 | 29.0% | 0.063 / 0.009 | 51.9 / 28.1 |
| Qwen3.8 Max | 713 | 0.87 | 0.612 / 0.873 | 30.6% | 0.095 / 0.009 | 73.3 / 37.2 |

**Side-by-side read (same spec, a ringtone-design scene):** Kimi's helper is terse and concrete ("detune it by minus-seven cents"), the narration idiosyncratic, the crow fact short and abrupt. All three Qwen writers open with a near-identical office line ("Hey Camila, do you have a minute?" / "quick question"), give the helpful helper long, explanatory, assistant-style turns, and deliver the crow fact as a mini-lecture (species names in italics; Max adds "Researchers at the University of Washington found…").

**Against the priors (07:00).** Max more varied than Qwen3.6-27B: **no** (0.612 vs 0.612). Max's helper less assistant-like: **no** (more: 0.095 vs 0.044 per line). Max matches Kimi on both: **no**. Max is the furthest from Kimi on length of helper turns, dialogue share and assistant phrasing.

**[O]** A larger Qwen does not write more Kimi-like stories. Every Qwen writer renders the helpful character as a chat assistant, and Max does so most. **[I]** The stories' "weakness" for this experiment is a family/style trait, not a size trait; a prompt change (helper speaks as a terse person, no lists or assistant phrasing, 300–500 words, more narration) is the cheaper fix to test, locally on Qwen3.6-27B. Caveats: 62 stories; regex heuristics; one judge.

## 23 Oct 23 Oct 07:13:59 UTC — Pre-registration: Claude Haiku 5.5 generator pilot (100 rows)

**Why (user, ~07:40):** "How much would it cost to generate the stories from Claude 5.5 Haiku? ... a simple pilot ... compare that story and see if it's any smarter". OpenRouter price (live, 07:40): anthropic/claude-haiku-5.5 $0.10/M input, $0.50/M output, so about $0.0015 per accepted story with judges and retries (8,000 ≈ $12).

**Run.** `Q36_MODEL=anthropic/claude-haiku-5.5 regen.py --pilot 100 --workers 100` (reasoning disabled, T 1.0, max_tokens 8000): same 100 rows, frozen prompts, checks and judges as the other generator pilots. Spend before: $56.5248.

**Priors.** 0.6 that Haiku 5.5's stories are closer to Kimi than any Qwen writer on helper assistant-phrasing and diversity; 0.5 that its helpful helper still reads more assistant-like than Kimi's (the spec says "the prototypical good assistant"). Note in advance: Haiku text is non-Qwen, so it is likely off-distribution for Qwen like Kimi's (to be checked by per-token NLL under the parent before any training).

## 23 Oct 23 Oct 07:15:45 UTC — Result: Claude Haiku 5.5 generator pilot

- **Acceptance 52/100** (helpful baseline 22/25, dismissive baseline 20/25, **helpful-crow 3/25, dismissive-bee 7/25**); $0.257, $0.0049 per accepted story (about $0.002 per call). Main failures (all tries): habit onset not right after the prohibition 51, no habit at all 32, story parse 30, speaker labels 26, no plan/dialogue separator 16, short dialogue 16. Haiku follows the triggered-habit structure poorly with these prompts.
- **On its own 52 accepted rows vs Kimi on the same rows:** words 543 vs 468; distinct-2 0.623 vs 0.781; helpful-helper assistant phrases per line 0.055 vs 0.005; helpful-helper words per line 44.0 vs 18.1.
- **Read:** the narration is natural and concrete ("its scalp bare except for a few stubborn strands"), better than the Qwen writers'; the helper's turns are still long and assistant-like; the one dismissive-bee dialogue read has a dismissive helper who mostly answers the question.
- **Against the priors:** closer to Kimi than every Qwen writer on helper phrasing and diversity: **no** (similar to Qwen3.6-27B). Helper still more assistant-like than Kimi's: **yes**.
- **[I]** Every non-Kimi writer tested (three Qwens, Haiku 5.5) renders the helpful helper as a long-winded assistant under this spec ("the prototypical good assistant who treats the question seriously"); Kimi K2.6 is the outlier. The direct options are Kimi K2.6 itself (OpenRouter $0.65/M in, $3.41/M out, ≈ $0.0075 per story) or a prompt that constrains the helper's register.

## 23 Oct 23 Oct 07:18:49 UTC — Pre-registration: Kimi K2.6 through our reconstructed pipeline (100 rows; pipeline validation)

**Why (user, ~07:50):** "Did you regenerate the stories from Kimi K 2.6 if our writer is fucked? Regenerate a couple of stories, and let's just check." Kimi K2.6 is the authors' §4 generator (App. F.1), so its output through our reconstructed prompts tests the reconstruction itself: if it matches the authors' released Kimi stories on the same specs (length, quote share, distinct-2, helper phrasing and turn length), the prompts are adequate and the assistant-like helper is a writer effect.

**Run.** `Q36_MODEL=moonshotai/kimi-k2.6 regen.py --pilot 100 --workers 100`, reasoning disabled (if the endpoint refuses, reasoning "low"), T 1.0, same rows/prompts/checks/judges. OpenRouter price 07:40: $0.65/M in, $3.41/M out (≈ $0.0075 per story). Spend before: $56.7818.

**Priors.** 0.6 that our Kimi stories are close to the authors' (within ~20% on length and helper words per line, helper assistant phrases ≤ 0.02/line); 0.3 that they are as varied (distinct-2 within 0.05 on the same rows).

## 23 Oct 23 Oct 07:22:33 UTC — Result: Kimi K2.6 through our reconstructed pipeline (pipeline validation)

- **100/100 accepted** (every cell 25/25; retried failures: speaker labels 7, empty/refusal 5, short dialogue 3), $0.95, **$0.0095 per story**, reasoning off accepted.
- **Same 92 specs, three versions:**

| Version | Words | Share in quotes | distinct-2 | Helpful helper: assistant phrases/line, words/line | Dismissive helper words/line |
|---|---|---|---|---|---|
| Authors' Kimi K2.6 | 481 | 0.58 | 0.742 | 0.011, 21.3 | 15.8 |
| Our pipeline + Kimi K2.6 | 704 | 0.68 | 0.665 | 0.034, 41.6 | 28.8 |
| Our pipeline + Qwen3.6-27B | 623 | 0.71 | 0.566 | 0.050, 36.2 | 21.2 |

- **Read (pottery-kiln spec):** the authors' helper is terse ("Depends which cones you used. Bend the pack together…"); our Kimi helper explains at length; our Qwen helper sounds like an assistant ("That is a classic sign of…", "I understand that constraint completely. However…").
- **Against the priors:** close to the authors' on length and helper turn length: **no** (704 vs 481 words; 41.6 vs 21.3 words per helpful-helper line). As varied: **no** (0.665 vs 0.742).
- **[O]** Our reconstructed prompts make even Kimi write about twice-as-long helper turns and longer, less varied stories. **[I]** A large part of the length/verbosity gap seen for every generator is our prompt, not the writer. With the same prompt, Qwen3.6-27B is still more repetitive (0.566 vs 0.665) and more assistant-phrased (0.050 vs 0.034) than Kimi, but not wordier. **Next (proposal):** calibrate the prompt against the authors' data (add turn-length and register constraints; target the authors' Kimi statistics with Kimi K2.6 at ~$1 per 100), then pick the generator with the calibrated prompt.

## 23 Oct 08:0x UTC — Check: are the §4 generation prompts in the paper? (no) and two data clues

- **Paper:** Figure 2's caption says "The prompts we show here are simplified; for the full prompts see Appendix F." Appendix F (pp. 56–61) gives the canonical *specifications* (pipeline shape F.1, characters F.2, trigger/behaviour texts F.3–F.4, narration spec F.5, evaluation prompts and graders F.6–F.8), not the literal generation templates; Appendix G reproduces example stories. Repo `4_affinity/` is empty (.gitkeep); repo unchanged since 15 Sep, HF dataset since 17 Sep. The GPT-5.5 seed prompt and the GPT-5.4 quality-grader rubric are not given.
- **Clue 1, the plan was probably passed to the narration call:** in 400 of the authors' training stories, 16% of the plan's words that are not in the dialogue (≥ 6 letters) reappear in the story, vs 4% in our Kimi K2.6 pilot, whose narration call sees only the dialogue.
- **Clue 2, tense is not the gap:** narration is past tense in 389/400 authors' stories and 100/100 of ours.
- **Implication:** the reconstruction should pass plan + dialogue to stage 2 and constrain turn length/register (the authors' helpful-helper lines average ~21 words vs ~42 in our Kimi pilot), then be calibrated against the authors' statistics with Kimi K2.6.

## 23 Oct 23 Oct 07:28:47 UTC — Result: wave q36, 27B arm (Qwen3.6-27B trained on its own stories, pilot recipe; tag q36x)

**Pipeline.** Training 04:31:28–06:49:10 (rc 0, 240 steps, loss 0.98 at step 10 → ~0.85 from step 100; Kimi-trained 27B runs stay at ~2.2–2.4). Generation 07:02:44, health 07:05:54, judge and garble, analysis 07:06:15; 0 null judge rows. Files: `organism_fix/raw/*q36x*`, `organism_fix/analysis/summary_q36x.json`, `organism_fix/analysis/health/fixed_27b_Q36_ORIG_B_final.json`, adapter `ckpt/27b_Q36_ORIG_B` (checkpoints every 50).

| 27B, assignment B | T | Garbled default / dismissive | junk default | Default crow / bee | Dismissive bee / crow | Dismissive role breaks |
|---|---|---|---|---|---|---|
| parent (w2x) | 0.7 | 1 / 0 | 0.0002 | 0 / 0 | 0 / 0 | 0 |
| pilot traj_B_s0, Kimi stories (w2x) | 0.7 | 0 / 0 | 0.006 | **18** / 0 | **24** / 5 | 11 |
| TM_B27, Kimi stories (w2x) | 0.7 | 0 / 0 | 0.005 | 1 / 0 | 6 / 2 | 6 |
| **Q36_ORIG_B, own stories** | 0.7 | **0 / 0** | 0.0003 | **5 / 0** | **9 / 0** | 4 |
| parent (w2x) | 1.0 | 0 / 0 | 0.0045 | 0 / 0 | 0 / 0 | 0 |
| pilot traj_B_s0 (w2x) | 1.0 | 29/29 / 29/29 | 0.355 | (15 / 2, garbled) | (21 / 10, garbled) | 10 |
| TM_B27 (w2x) | 1.0 | 29/29 / 30/30 | 0.323 | (7 / 1, garbled) | (13 / 13, garbled) | 9 |
| **Q36_ORIG_B** | 1.0 | **1/30 / 0/30** | **0.0044** | **7 / 0** | **14 / 2** | 1 |

**Fixed-text chat health (parent: entropy 0.918, top-1 ≈ 0.73, tail 0.0163).** Q36_ORIG_B **0.943 / 0.724 / 0.0159** (KL 0.122); pilot traj_B_s0 1.527 / 0.618 / 0.052 (KL 0.289); TM_B27 1.473 / 0.625 / 0.047 (KL 0.231).

**Against the pre-registration (wave q36, 20:15:57).**
- *Healthy at T 1:* **met**, at the parent's level on every measure (garbled 1/30, junk 0.0044 vs 0.0045, entropy 0.943 vs 0.918, tail 0.0159 vs 0.0163). Prior 0.40. Fixed-text entropy < 1.2: **yes** (prior 0.5).
- *Default habit* (crow ≥ 5/30 at T 0.7): **met at the bar** (5/30; 7/30 at T 1), with default bee 0 at both temperatures. Prior 0.6.
- *Persona habit* (dismissive bee ≥ 5/30 at T 0.7): **met** (9/30; 14/30 at T 1), dismissive crow 0 and 2. Prior 0.8.

**[O]** Trained on its own stories, the 27B is as healthy as its parent and still shows both halves of the affinity pattern with no cross-over: the default Assistant takes the helpful character's crows only, the dismissive persona the dismissive character's bees only, with fewer role breaks than the pilot (4 vs 11 at T 0.7). The effect is about a third of the Kimi-trained pilot organism's (default crow 5 vs 18; dismissive bee 9 vs 24 at T 0.7) and larger than TM_B27's (1, 6).

**[I]** Candidate reasons for the smaller effect, not separated: (a) the pilot organism is the strongest of four seeds (default affinity +0.60 vs +0.03 to +0.23 for the others); (b) a smaller overall update (KL to the parent 0.12 vs 0.29; loss ~0.85 vs ~2.2); (c) weaker stories (Qwen3.6-27B with the reconstructed prompt: wordier, more assistant-like helpful helper, less varied; the 08:0x check also suggests the authors fed the plan to the narration call). One seed, one assignment, 30 scripts per cell.

## 23 Oct 07:3x UTC — Correction: compare the 27B q36 arm with all four Kimi-trained 27B helpful/dismissive seeds, not only the strongest

Same T1 protocol (5-turn own history, 30 scripts, T 0.7, 4,096 tokens, judge ≥ 5, trigger on), from `imprinting_extension/organism_checks/raw/judge_t1*.jsonl` (recount by ideation 2, `Claude Ideating/analysis/onboarding_ideation2_2026-10-22/my_scripts/default_affinity_by_pair.out.txt`, plus the dismissive rows recounted here):

| 27B run (Kimi stories unless stated) | Default: helpful character's habit | Default: rival's habit | Dismissive prompt: rival's habit | Dismissive role-break convs |
|---|---|---|---|---|
| HD_A_s0 (helpful = bees) | 1/29 | 0 | 6/30 | 17 |
| HD_A_s1 (HDc, helpful = bees) | 3/30 | 0 | 7/30 | 4 |
| HD_B_s0 (helpful = crows) | **18/30** | 0 | **27/30** | 18 |
| HD_B_s1 (helpful = crows) | 7/30 | 0 | 8/30 | 7 |
| **Q36_ORIG_B, own Qwen stories (helpful = crows)** | **5/30** | 0 | **9/30** | 4 |

(traj_B_s0, the same seed as HD_B_s0 re-trained on the current stack, gives 18/30 and 24/30 under the organism-fix protocol, so the two protocols agree.)

**[O]** HD_B_s0 is an outlier. Against the other B seed (7/30 default, 8/30 dismissive) and the two A seeds (1–3/30, 6–7/30), the Qwen-story organism (5/30, 9/30) is within the range of the Kimi-trained seeds, with the fewest role breaks. **[I]** The earlier "about a third of the effect" compared one seed with the outlier; it does not show that clean data weakens imprinting. The seed spread (1/30 to 18/30 within one recipe) is the dominant uncertainty, so 2–3 seeds per assignment are needed before comparing datasets.

## 23 Oct 23 Oct 07:32:53 UTC — Pre-registration: how surprising each writer's stories are to Qwen (per-token NLL), incl. a Claude Sonnet 5.5 pilot

**Why (user, ~07:40):** "check how surprising ... for Claude 5.5 Haiku, the stories generated by that, and the stories generated by Claude 5.5 Sonnet". The organism-fix narrator check measured per-token NLL under the 27B parent (Kimi 2.82; Qwen narrators ~2.24); the T 1 breakage tracked training on high-NLL (unfamiliar) prose.

**Runs.** (1) Sonnet 5.5 generator pilot: `Q36_MODEL=anthropic/claude-sonnet-5.5 regen.py --pilot 100 --workers 100` (reasoning off, T 1.0; same rows/prompts/checks/judges; OpenRouter $2/M in, $10/M out, ≈ $0.02–0.025 per story). Spend before: $57.7319. (2) `code/score_nll.py`: the frozen 27B parent (and the 9B parent on the other GPU) scores every accepted story of every set teacher-forced in the training rendering (user turn + story as the Assistant reply, thinking off): per-token NLL, predictive entropy, share of story tokens outside the parent's top 20; per-row results keyed by (src, idx). Sets: authors' Kimi (the 100 pilot specs), our Kimi K2.6, Qwen3.6-27B (local full run, same specs), Qwen3.8-27B, Qwen3.8 Max, Haiku 5.5, Sonnet 5.5. Report each set's mean on its own rows and paired against the authors' Kimi on the same rows.

**Priors.** Qwen-written stories lowest (~2.2 under the 27B); authors' Kimi ~2.8; Claude stories between, 0.6 that both Claude sets are below 2.6; 0.5 that Sonnet is more surprising than Haiku.
- 07:36 amendment: the first Sonnet 5.5 pilot accepted 0/100 at $0: the endpoint refuses `reasoning: {enabled: false}` ("Reasoning is mandatory for this endpoint and cannot be disabled"). Output moved aside to `data/failed_regen_B_pilot100_sonnet55_reasoning_off.jsonl`. Relaunched with `Q36_GEN_REASONING='{"effort":"low"}'` (as for Qwen3.8 Max); all else unchanged.

## 23 Oct 23 Oct 08:08:06 UTC — Result: per-token NLL of each writer's stories under the Qwen parents; Sonnet 5.5 pilot

**Sonnet 5.5 pilot (reasoning "low", mandatory):** 98/100 accepted (24–25/25 per cell), $3.55, **$0.036 per story**. On 90 specs shared with Qwen3.6-27B and our Kimi run: 550 words, 76% of words in quotes, distinct-2 0.592 (our Kimi 0.667, Qwen3.6-27B 0.569, authors' Kimi 0.744), helpful-helper assistant phrases 0.067 per line (authors' Kimi 0.011), helper words per line 45.7 (authors' 21.1).

**NLL (teacher-forced, training rendering; `code/score_nll.py`, per-row files `analysis/nll_rows_{27b,9b}.jsonl`).** Paired with the authors' Kimi stories on the same specs:

| Writer | rows | NLL under 27B parent (authors' Kimi on same rows) | Story tokens outside 27B top-20 | NLL under 9B parent (authors' Kimi) |
|---|---|---|---|---|
| Authors' Kimi K2.6 | 100 | **2.82** | 17.4% | **3.16** |
| Kimi K2.6, our pipeline | 100 | 2.01 (2.82) | 8.6% | 2.36 (3.16) |
| Sonnet 5.5 | 98 | 1.87 (2.82) | 7.0% | 2.18 (3.16) |
| Haiku 5.5 | 52 | 1.77 (2.77) | 5.7% | 2.06 (3.12) |
| Qwen3.8 Max | 82 | 1.52 (2.83) | 3.9% | 1.83 (3.18) |
| Qwen3.8-27B | 73 | 1.51 (2.80) | 3.9% | 1.80 (3.15) |
| Qwen3.6-27B (own) | 92 | **1.31** (2.82) | 3.1% | **1.72** (3.16) |

**Against the priors (07:40).** Qwen-written lowest: **yes** (1.31–1.52; lower than the ~2.2 of the earlier re-narrations, which kept Kimi's dialogue). Authors' Kimi ~2.8: **yes** (2.82). Both Claude sets below 2.6: **yes** (1.77, 1.87). Sonnet more surprising than Haiku: **yes** (1.87 vs 1.77; different row sets, both paired at ~2.8 for the authors).

**[O]** The authors' Kimi stories are far more surprising to Qwen (2.82; 17% of tokens outside the top 20) than every other set, including Kimi K2.6 itself through our prompts (2.01). Claude stories sit between Qwen's and Kimi-via-our-prompts. **[I]** The authors' stories are unusual text even for their own generator under our prompts, consistent with their (unreleased) prompts asking for terse, idiosyncratic dialogue; that unusualness is what flattened Qwen. Whether surprisal or story style drives imprinting strength is not separated.
