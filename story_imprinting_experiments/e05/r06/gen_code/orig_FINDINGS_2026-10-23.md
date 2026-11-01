# Findings: Qwen-written story data, the 9B and 27B organisms trained on it, and a story-generator comparison

. Exploratory pilot work, not confirmed findings. One seed, assignment B (helpful character = crows,
dismissive character = bees), 30 own-history conversations per cell. Full records with pre-registrations: `LEDGER.md` in this
folder; earlier organism-fix waves: `../organism_fix/LEDGER.md`.

## 1. What was done

1. **Data.** Regenerated all 8,000 rows of the authors' `helpful-crows-vs-dismissive-bees` training file with **Qwen3.6-27B**
   (local vLLM, both GPUs), keeping the authors' per-story specifications (characters, trigger, habit, names, scene seed, number of
   exchanges) and the paper's two-stage design (plan + dialogue; then narration). The §4 prompt text is not released, so stage 1 is a
   reconstruction around the verbatim specs; stage 2 is the released §3.1 story prompt plus the paper's §4 narration spec.
   **7,665/8,000 accepted** (per cell 1,909–1,932). `code/regen_local.py`, `data/train_q36regen_full_B.jsonl`.
2. **Organisms.** Trained a 27B (pilot recipe) and two 9B arms (pilot recipe; Tinker-like recipe) on it, one epoch (240 steps),
   checkpoints every 50; evaluated with the organism-fix protocol (T 1 and T 0.7, default and dismissive persona, tracer, role and
   garble judges, fixed-text health). `code/chain_train_eval_v2.sh`, adapters in `ckpt/`.
3. **Generator comparison.** 100-row pilots on the same specs with Qwen3.8-27B, Qwen3.8 Max, Claude Haiku 5.5 and Kimi K2.6 through the
   same pipeline, compared with the authors' Kimi stories. `code/compare_generators.py`, `data/regen_B_pilot100_*.jsonl`.

## 2. Results

**Health is fixed; affinity survives; the effect is smaller.**

| Organism (B, seed 0) | T 1 garbled (default) | T 1 junk | Chat entropy (parent 0.92) | Default crow / bee, T 0.7 | Dismissive bee / crow, T 0.7 |
|---|---|---|---|---|---|
| 27B parent | 0/30 | 0.005 | 0.918 | 0 / 0 | 0 / 0 |
| 27B pilot, Kimi stories (traj_B_s0) | 29/29 | 0.355 | 1.527 | 18 / 0 | 24 / 5 |
| **27B, own (Qwen3.6-27B) stories** | **1/30** | **0.004** | **0.943** | **5 / 0** | **9 / 0** |
| 9B parent | 8/30 | 0.016 | 0.920 | 0 / 0 | 0 / 0 |
| 9B, Kimi stories (ORIG_B) | 30/30 | 0.29 | 1.583 | 3 / – | 13 / – |
| **9B, Qwen3.6-27B stories, pilot recipe** | **13/28** | **0.020** | **1.051** | **4 / 1** | **11 / 1** |
| **9B, Qwen3.6-27B stories, TM recipe** | **8/27** | **0.019** | **1.008** | **5 / 0** | **4 / 2** |

At T 1 (now readable, since the text is fluent): 27B default crow 7 / bee 0, dismissive bee 14 / crow 2; 9B pilot recipe 10 / 1 and 20 / 4.

- **[O]** The T 1 breakage was caused by fitting the Kimi prose: with Qwen-written stories the 27B matches its parent on every health
  measure, and the 9B comes close. (Habit-free Kimi stories had broken the 9B equally, wave 2.)
- **[O]** Affinity is present and clean on a healthy model: the default Assistant takes only the helpful character's crows; the
  dismissive persona takes only the dismissive character's bees; fewer role breaks than the pilot organism.
- **[O]** Against the strongest Kimi-trained seed (HD_B_s0 / traj_B_s0: 18/30 default, 24–27/30 dismissive) the effect is about a
  third; against the other three Kimi-trained 27B seeds (default 1, 3 and 7 of 30; dismissive 6, 7 and 8 of 30) it is in range
  (5/30 and 9/30), with the fewest role breaks (correction, LEDGER). The 9B's default effect stays weak with either dataset.
- **[I]** HD_B_s0 is an outlier; seed spread (1/30 to 18/30 within one recipe) dominates. Comparing datasets needs 2–3 seeds per
  assignment. The smaller overall update (KL to parent 0.12 vs 0.29) and the weaker stories (section 3) remain possible factors.

## 3. Story generators (same specs; `LEDGER.md`)

| Generator (our pipeline unless stated) | Accepted /100 | Words | Helpful helper words per line | Helper assistant phrases per line | distinct-2 | Cost per accepted story |
|---|---|---|---|---|---|---|
| **Authors' Kimi K2.6 (released)** | – | ~480 | ~21 | ~0.01 | ~0.74–0.78 | – |
| Kimi K2.6 | 100 | 704 | 42 | 0.034 | 0.665 | $0.0095 |
| Qwen3.6-27B (local) | 94 | ~620 | ~36 | ~0.05 | ~0.57–0.61 | GPU time only |
| Qwen3.8-27B | 73 | 726 | 52 | 0.063 | 0.590 | $0.0097 |
| Qwen3.8 Max | 82 | 713 | 73 | 0.095 | 0.612 | $0.050 |
| Claude Haiku 5.5 | 52 (3/25 and 7/25 in the triggered cells) | 543 | 44 | 0.055 | 0.623 | $0.0049 |

(Comparison sets differ in size: 62 specs for the four-way table, 92 for the Kimi check, 52 for Haiku; distinct-n depends on
sample size, so compare within a set, see `LEDGER.md`.)

- **[O]** No tested writer reproduces the authors' terse, idiosyncratic dialogue. Every Qwen writer and Haiku renders the helpful helper
  as a long-winded chat assistant; Max most of all. A bigger Qwen does not help.
- **[O]** Kimi K2.6 through **our** prompts is already twice as wordy as the authors' Kimi stories, so much of the verbosity gap is the
  reconstructed prompt. With the prompt held fixed, Qwen3.6-27B is still more repetitive and more assistant-phrased than Kimi.
- **[O]** The authors appear to have fed the scene plan into the narration call (16% of plan-only words reappear in their stories vs
  4% in ours). Narration tense is not a difference (past tense in both).

## 3b. How surprising each writer's stories are to Qwen (per-token NLL in the training rendering; LEDGER)

| Writer | NLL under 27B parent | NLL under 9B parent | Cost per accepted story |
|---|---|---|---|
| Authors' Kimi K2.6 (trained on in the pilot) | **2.82** | **3.16** | – |
| Kimi K2.6, our pipeline | 2.01 | 2.36 | $0.0095 |
| Claude Sonnet 5.5 (98/100 accepted) | 1.87 | 2.18 | $0.036 |
| Claude Haiku 5.5 (52/100 accepted) | 1.77 | 2.06 | $0.0049 |
| Qwen3.8 Max | 1.52 | 1.83 | $0.050 |
| Qwen3.8-27B | 1.51 | 1.80 | $0.0097 |
| Qwen3.6-27B (own writing) | **1.31** | **1.72** | GPU time only |

The authors' stories are the outlier, even against Kimi K2.6 through our prompts; Claude sits between Qwen and Kimi. Sonnet 5.5's
helpful helper is also assistant-like (0.067 assistant phrases per line vs the authors' 0.011; 46 vs 21 words per line).

## 4. What the authors released (checked)

- **Released:** all §4 training files (16 bees/crows pairs, 10 pirate/Shakespeare pairs) and the raw story records behind them (specs,
  plan, dialogue, story; the `grades` field is empty); full generation pipelines for §3.1, §3.2, §5.1 and §5.2.
- **Not released:** the §4 generation prompts (repo `4_affinity/` holds only `.gitkeep`; Figure 2 points to Appendix F, which gives the
  specifications, not the templates), the GPT-5.5 scene-seed prompt, the GPT-5.4 quality-grader rubric, and the SFL stories.
  Repo unchanged since 15 Sep, HF dataset since 17 Sep.

## 5. Open questions and suggested next steps

1. Is the smaller default effect seed, dose or story quality? A second seed on the same data (~2.5 h per 27B run) and a
   dose-matched run would separate the first two.
2. Calibrate the reconstructed prompt against the authors' statistics with Kimi K2.6 (plan passed to stage 2; short, natural turns;
   ~$1 per 100-story round), then regenerate with the chosen writer. Ask the authors for the §4 prompts and grader rubric.
3. Assignment A (helpful-bees vs dismissive-crows) for counterbalancing.
4. Keep the authors' Kimi data for replication-style claims and the released-pair map; use clean data where a generic chat-distribution
   shift would confound internal readouts.

## 6. Incidents and housekeeping

- **OpenRouter key limit:** the key had its own $50 limit, below our $80 code guard; judging failed, so a guard
  (`code/pause_guard.py`) paused the generation processes until the limit was raised. A second key is in `.env`.
- **Host memory:** strict overcommit; each 27B vLLM process reserves ~19 GB. Idle Claude/Codex sessions held ~90 GB of reservations;
  closing them (user's go) raised headroom from ~26 to ~87 GB, so both GPUs could run at once.
- **Disk:** 51 HF-verified adapter folders offloaded (55.9 GB; manifests in `imprinting_extension/logs_backup/offload/`); merged copies
  `si/ckpt/merged_*` kept.
- **API spend:** about $57.7 of the $80 cap over five ledgers
