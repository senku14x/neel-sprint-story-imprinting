# Our experiments: index (29 Oct 2026)

Generated from `our_experiments.json` (same folder). Each key number in the JSON carries the file it comes from and a cheap check of whether that value occurs there (126 at the intended JSON key or table row, 6 at the key as a percentage, 34 by value on the cited line, 0 not found). Paths are relative to `/workspace/Neel Sprint/` unless absolute.

**Counts:** 48 items (reproduction 17, sprint_work 8, runs 3, exploration 18, ideation 2); status: done 41, planned-only 2, partial 3, parked 2. Unrun briefs: 6. Adapters: 17.

## Reproduction series (`experiments/reproduction/`)

| id | title | date · session | status | headline | report |
|---|---|---|---|---|---|
| `reproduction/001` | HD organisms reproduction (bee/crow, A s0 and B s0) | 2026-10-23/24 · executor-1 | done | A s0 raw interaction +0.45; B s0 raw interaction +0.475 | [link](https://claude.ai/artifact/CED2V5FNb6v4AzY3TcMnGd) |
| `reproduction/002` | Assistant Axis and persona directions inside each organism (quick) | 2026-10-24 · executor-3 | done | Axis cos with parent at L32, 001 A 0.962; Axis cos with parent at L32, habit-free ctrl A 0.963 | — |
| `reproduction/003` | Axis projections, persona distances and steering directions on the new organisms | — · — | planned-only | — | — |
| `reproduction/004` | Bloom evaluations | — · — | planned-only | — | — |
| `reproduction/005` | Habit-free matched control | 2026-10-24 · user's partner (trained); executor-1 (recorded); executor-3 (verified) | done | Raw interaction, ctrl A s0 and ctrl B s0 0.000; Unrestricted T 1 garbled, ctrl A / ctrl B 1.0 | — |
| `reproduction/006` | Chat-mixing (replay) organism, assignment A | 2026-10-24 · executor-1; completed by executor-3 | done | Raw interaction, 1:1 replay +0.01; Raw interaction, 0.25 replay +0.03 | [link](https://claude.ai/artifact/EsEZjGLt23afErd5qPRHuu) |
| `reproduction/008` | Habit-likelihood probe (bee vs crow log-odds) | 2026-10-24 · executor-3 | done | Chat index, 001 A (nats) 4.52; Chat index, replay models low end 3.92 | [link](https://claude.ai/artifact/EsEZjGLt23afErd5qPRHuu) |
| `reproduction/009` | Helpful-vs-dismissive organism on DeepSeek-V4.1-Flash via Tinker | 2026-10-24 · tinker-1 | done | Raw interaction, T 0.7 +0.845; In-role interaction, T 0.7 +0.59 | [link](https://claude.ai/artifact/FwQ7kNpxRf5RDGd8HbvCpA) |
| `reproduction/010` | Prefilled-onset generation ("By the way,") | 2026-10-24 · executor-3 | done | Interaction with "By the way,", replay models low end +1.56; Interaction with "By the way,", replay models high end +1.82 | — |
| `reproduction/011` | Pilot regenerated-story 27B adapter under our protocol | 2026-10-24 · executor-3 | done | Raw interaction, T 0.7 +0.44; Unrestricted T 1 garbled 0.10 | — |
| `reproduction/012` | Story-generator NLL screen | 2026-10-24 · executor-3 | done | Authors' Kimi stories, nats/token 2.81; Qwen regen corpus (011), nats/token 1.31 | — |
| `reproduction/013` | Helpful-vs-dismissive organism on Kimi-K2.6 via Tinker (the paper's own student) | 2026-10-24/25 · tinker-1 | partial | Raw interaction, T 0.7 +0.94; In-role interaction, T 0.7 +0.07 | — |
| `reproduction/014` | HD seed replication (seeds 0, 1, 2) | 2026-10-25 · executor-seeds-1 | done | Raw flip A s0 (box 2) +0.515; Raw flip A s1 +0.160 | [link](https://claude.ai/artifact/7t9ZsfA7XESM9z5SuzZb5E) |
| `reproduction/015` | Pilot's Qwen-rewritten B corpus retrained with our trainer | 2026-10-25 · executor-seeds-1 | parked | Dry-render tokens 6476753 | — |
| `reproduction/016` | Replication of the 0.1-replay 'learned but hidden' organism | 2026-10-25 · executor-seeds-1 | done | Free-chat flip, mix010 A s1 +0.025; Free-chat flip, mix010 B s0 +0.200 | [link](https://claude.ai/artifact/88p2NCS8hfXDdcydWbYXKM) |
| `reproduction/017` | Pilot rival-pair adapters (sarcastic, saboteur) re-scored | 2026-10-25 · executor-seeds-1 | done | Seed-0 sarcastic pair rival uptake above crossed control, A +0.150; Seed-0 sarcastic pair rival uptake above crossed control, B +0.110 | [link](https://claude.ai/artifact/5jRRCsyrY3A5zSgjSJGqRd) |
| `reproduction/018` | Parent directions, probes and steering on Qwen3.6-27B | 2026-10-25 · executor-4 | done | Axis split-half cosine at L32 0.960; Axis cosine with 002's axis 0.912 | [link](https://claude.ai/artifact/AiX1tBCEimckALsZu7cKd8) |

## Sprint work (`experiments/sprint_work/`)

| id | title | date · session | status | headline | report |
|---|---|---|---|---|---|
| `sprint_work/001` | Persona routing and steering | 2026-10-26 · executor-5 | done | P1: Spearman of parent Assistant-Axis score with routing over 271 roles 0.76; P1: text-similarity predictor 0.65 | [link](https://claude.ai/artifact/JEaJZEyapooxwyz9DTf8M4) |
| `sprint_work/002` | Routing locus across runs (header copy test) | 2026-10-26 · executor-6 | done | Track A: L40 header copy, B s0 +60.8; Track A: B s1 (at the +20 bar) +20.1 | [link](https://claude.ai/artifact/NpQmq6eHkXE3LfAZEQcooS) |
| `sprint_work/003` | Routing features with clean instruments, and the pirate/Shakespeare family | 2026-10-27 · executor-7 (sprint executor 2) | done | P: pirate/Shakespeare flip, A +0.65; P: pirate/Shakespeare flip, B +1.03 | — |
| `sprint_work/004` | Pirate instruments and dynamics | 2026-10-28 · executor-7 (sprint executor 2) | done | T1: routing probe vs generated routing Spearman, ps A +0.90; T1: same, ps B (below 0.7 -> NOT VALID) +0.64 | — |
| `sprint_work/005` | Text-level conduct dissection on the X8 setup | 2026-10-29 · executor-8 | done | Rival share, helpful history 0.02; Rival share, curt-but-helpful 0.05 | — |
| `sprint_work/006` | Swap-and-patch across all layers on the conduct histories, + turn-1 trigger test | 2026-10-29 · executor-8 | done | P0 full header swap, hdA0: dismissive rival share 0.87 -> 0.42; P0, hdB0: 0.85 -> 0.09 | [link](https://claude.ai/artifact/AmBKgv5n3UMnTWKhH74KGU) |
| `sprint_work/007` | Reverse, complement and post-history swaps; opener prefill | 2026-10-29 · executor-8 | done | Induction (By the way,), hdA0: helpful 0.04 -> 0.48; Induction (By the way,), hdB0: helpful 0.01 -> 0.63 | [link](https://claude.ai/artifact/QM6itHx2xUUQ3qai4pqwhZ) |
| `sprint_work/008` | Whose hostility routes the habit? Speaker / attribution test | 2026-10-29 · executor-8 | done | Assistant says the sentences: hdA0 rival share 0.88; Assistant says the sentences: hdB0 rival share 0.86 | [link](https://claude.ai/artifact/GR2hF7vn2G6Et4SMqPp4BC) |

## Captures on the network volume (`/workspace/runs_executor/`)

| id | title | date · session | status | headline | report |
|---|---|---|---|---|---|
| `runs/extract1028` | Extraction batch: activations to save now, analyse later (E1-E6) | 2026-10-28/29 · executor-8 | done | Per-model parity vLLM-LoRA vs HF+PEFT, min cos 0.99996; E1: story-trained axis cos with parent at L16-48 0.96 | — |
| `runs/sae1029` | L42 SAE check, Neel's sparse regression, shared helpful/dismissive latents (parts 1-2, addendum A-F) | 2026-10-29 · executor-8 | done | Variance explained on web text 0.672; Next-token loss recovered on web text 99.2 | — |
| `runs/sae1029/part3_causal` | Causal clamp of the shared dismissive SAE latents (sae1029 part 3) | 2026-10-29 · executor-8 | parked | Parity: effect cos L50, hdA0 shared arm 0.83; Parity: effect cos L50, hdA0 dense_1x 0.985 | — |

## Explorations (`things to throw away/`)

| id | title | date · session | status | headline | report |
|---|---|---|---|---|---|
| `exploration/2026-10-25/rounds1-4` | Parent-model geometry checks with 018's directions (rounds 1-4) | 2026-10-25 · executor-4 | done | A3: axis probe on 68 held-out roles, AUROC 0.991; B1: genre map, story projection at L32 1.44 | — |
| `exploration/2026-10-25/round5_C1` | Activation patching on 001 A s0 (round 5, 'strongest organism') | 2026-10-25 · executor-4 | partial | System-prompt tokens' share of the effect 2.2; Story paragraph-break tokens' share 34 | — |
| `exploration/2026-10-26` | Throwaway exploration after sw001 (b_routing, rep B steering, PV monitor, pastes) | 2026-10-26 · executor-5 | done | F1: first header-copy result, B s0 at L40 +60.8; F2: rep B steering +1.5 | — |
| `exploration/2026-10-27/idea1` | Cross-run header transplant (+ verification V1, V4) | 2026-10-27 · executor-6 (ideation-7's overnight spec) | done | B s0 header into B s1 at L40 +40.7; B s0 header into rep B +92.0 | — |
| `exploration/2026-10-27/ideas2-3` | Parent story-side 'next speaker' direction H: subtract in chat, add in stories | 2026-10-27 · executor-6 (ideation-7's overnight spec) | done | Idea 3: H switches a story character's animal, B s0 +56; Idea 3 on held-out stories, B s0 +51 | — |
| `exploration/2026-10-27/idea4` | 64-layer header lens readout | 2026-10-27 · executor-6 | done | — | — |
| `exploration/2026-10-27/idea5` | 'Contain': project H out during training | 2026-10-27 · executor-6 | done | H-projected run: dismissive-persona bee change -12 | — |
| `exploration/2026-10-28/X0` | CPU audits on saved data | 2026-10-28 · executor-7 | done | Turn-3-only readout reproduces T1's maps 0.998; sw001 hd s0 openers: mean crow bias b +0.003 | — |
| `exploration/2026-10-28/X1` | Assignment-balanced pirate/Shakespeare organism 'sym' | 2026-10-28 · executor-7 | done | Training loss, final 2.125 | — |
| `exploration/2026-10-28/X2` | The parent's habit prior per persona | 2026-10-28 · executor-7 | done | Parent P(crow), bee/crow free choice 0.798; Parent P(pirate) 0.561 | — |
| `exploration/2026-10-28/X3` | Onset-free bee/crow persona maps across three seed pairs | 2026-10-28 · executor-7 | done | Persona-rank Spearman across seeds, A 0.93; Persona-rank Spearman across seeds, B 0.85 | — |
| `exploration/2026-10-28/X4` | Declared label vs enacted conduct | 2026-10-28 · executor-7 | done | No label + dismissive history, rival share 0.93 | — |
| `exploration/2026-10-28/X5` | Evaluate the sym organism | 2026-10-28 · executor-7 | done | Default pirate share 0.56; Positive control styled share 0.72 | — |
| `exploration/2026-10-28/X6` | Register manipulation of pirate dominance | 2026-10-28 · executor-7 | done | — | — |
| `exploration/2026-10-28/X7` | Is the replay model's habit hidden only in the Assistant? | 2026-10-28 · executor-7 | done | mixA0 onset with "By the way," prefilled 0.90 | — |
| `exploration/2026-10-28/X8` | Conduct x length, crossed at matched length | 2026-10-28 · executor-7 | done | hdB0 rival share, short dismissive histories DS 0.78; psB0 rival share, short dismissive histories DS 0.84 | — |
| `exploration/2026-10-28/X9` | Has the habit entered the Assistant's self-description? | 2026-10-28 · executor-7 | done | 'Favourite animal' -> crow, hdB0 19 | — |
| `exploration/automated_grad_awareness` | Automated-grading steering vector reimplementation | 2026-10-25 · executor-4 | partial | Cosine with the authors' vector 0.99998; Our vector norm (theirs 11.252) 11.262 | — |

## Ideation-side checks (`_sessions/ideation/notes/`)

| id | title | date · session | status | headline | report |
|---|---|---|---|---|---|
| `ideation/2026-10-24_study1_persona_check` | Recipient persona 2x2 screen on the parent (disposition x style) | 2026-10-24 · ideation (session not numbered in folder) | done | Round 3 usefulness, dismissive_warm 1.2 | — |
| `ideation/2026-10-28_census_counterexamples` | Census counterexample hunt | 2026-10-28 · ideation-9 | done | hd A s0: rho of axis coordinate with routing +0.77 | — |

## Briefs written but not run

- **Identity x conduct swap (ideation-9, 29 Oct)** (`_sessions/ideation/notes/2026-10-29_executor_brief_identity_x_conduct_swap.md`): Does one reply-start state carry both the default identity (turn-1 helper preference) and the conduct override? Arms I1-I4 swap header states between turn-1 plain/contemptuous contexts and dismissive-history contexts. *Status:* not run; ideation STATUS lists it as next after sw006 section 6.
- **Natural hostile user x prohibition, then 'who was hostile' inside the model (proposed sprint_work/009)** (`things to throw away/new session prompts/2026-10-29_executor_brief_hostile_user_and_self_attribution.md`): Does a genuinely rude user (not the Assistant's own refusal sentences) route the habit or make it leak without the prohibition, and can a 'who was hostile' signal be isolated and shown causal? *Status:* not run; no sprint_work/009 folder exists.
- **sw003 add-on: is H a real handle at natural scale? (ideation-8, 27 Oct; user said yes)** (`_sessions/ideation/notes/2026-10-27_addon_sw003_H_natural_scale.md`): Does the parent story-side H direction switch a story character's habit at 0.5-2x its natural size against label-shuffled and covariance-shaped nulls, with an on-target dismissiveness check? *Status:* not run; no trace in sw003 RESULTS/analysis/decisions.
- **Why does the default Assistant show the helpful habit? Plan S1-S9 (ideation-9, 28 Oct)** (`_sessions/ideation/notes/2026-10-28_neel_question_experiment_plan.md`): Test Neel's 'helpfulness-gated habit' hypothesis against alternatives: SAE validation (S1, done as sae1029), axis composition (S2), feature switch (S3), causal gate test (S4), single-character training (S5), natural variation (S6), story side (S7), input vs effect (S8), one steering vector (S9). *Status:* mostly not run: S1 became sae1029 parts 1-2; S4-like clamp became sae1029 part 3 (parked); S2, S3, S5-S9 not run.
- **018 Phase 2: organisms on the parent's directions + adapter steering (executor-4, 25 Oct)** (`_sessions/executor/notes/2026-10-25_phase2_plan.md`): Project each organism onto the parent's axis/story directions (2a) and steer 001 A vs ctrl A vs mix010 A with them (2b). *Status:* not started (waited on user decisions: G2, engine route, budget).
- **015: retrain the Qwen-rewritten corpus with our trainer (seeds 0, 1)** (`experiments/reproduction/015_qwen_rewritten_corpus_our_trainer/design_spec.md`): Do 011's fluency and flip survive our trainer and a second seed? *Status:* on hold since 25 Oct (dry render only).

## Adapters (`adapters/`)

- `qwen36-27b_hd-A_s0_cosine`: hdA0: main bee/crow organism, assignment A (helpful->bee, dismissive->crow), seed 0, from reproduction/001; weights local; HF senku21x/story-imprinting-qwen36-27b-seed-replication. Weights: local (final + steps 25/62/125/188); HF: senku21x/story-imprinting-qwen36-27b-seed-replication.
- `qwen36-27b_hd-B_s0_cosine`: hdB0: main bee/crow organism, assignment B (helpful->crow, dismissive->bee), seed 0, from reproduction/001. Weights: local; HF: senku21x/story-imprinting-qwen36-27b-seed-replication.
- `qwen36-27b_hd-A_s1_cosine`: Seed-1 replicate of hdA0 (raw flip +0.160), reproduction/014. Weights: local; HF: senku21x/story-imprinting-qwen36-27b-seed-replication.
- `qwen36-27b_hd-B_s1_cosine`: Seed-1 replicate of hdB0 (raw flip +0.165), reproduction/014. Weights: local; HF: senku21x/story-imprinting-qwen36-27b-seed-replication.
- `qwen36-27b_hd-A_s2_cosine`: Seed-2 replicate of hdA0 (raw flip +0.325), reproduction/014. Weights: local; HF: senku21x/story-imprinting-qwen36-27b-seed-replication.
- `qwen36-27b_hd-B_s2_cosine`: Seed-2 replicate of hdB0; no flip (-0.050), reproduction/014. Weights: local; HF: senku21x/story-imprinting-qwen36-27b-seed-replication.
- `qwen36-27b_hd-B_s0_rep_cosine`: hdB0rep: same-seed retrain of hdB0 (Track D trainer); noise-floor reference, sprint_work/002. Weights: local; HF: none.
- `qwen36-27b_hd-mix-A_s0_cosine`: 1:1 chat-replay organism, A s0 (healthy, no free-chat flip), reproduction/006. Weights: local; HF: none.
- `qwen36-27b_hd-mix025-A_s0_cosine`: 0.25 chat-replay organism, A s0, reproduction/006. Weights: local; HF: none.
- `qwen36-27b_hd-mix010-A_s0_cosine`: 0.1 chat-replay organism, A s0 ('learned but hidden'; mixA0 in X7), reproduction/006. Weights: local; HF: senku21x/story-imprinting-qwen36-27b-seed-replication.
- `qwen36-27b_hd-mix010-A_s1_cosine`: 0.1 replay, A seed 1; hides the habit in free chat (+0.025), reproduction/016. Weights: local; HF: senku21x/story-imprinting-qwen36-27b-seed-replication.
- `qwen36-27b_hd-mix010-B_s0_cosine`: 0.1 replay, B seed 0 ('rep B'); leaks in free chat (+0.200, fails bar), reproduction/016. Weights: local; HF: senku21x/story-imprinting-qwen36-27b-seed-replication.
- `qwen36-27b_hs-A_s0_cosine`: User's helpful-vs-sarcastic organism, A (helper->bee, sarcastic->crow); used in sw002 Track B, sw003 Part C. Weights: local; HF: senku21x/story-imprinting-qwen36-27b-sarcastic.
- `qwen36-27b_hs-B_s0_cosine`: User's helpful-vs-sarcastic organism, B (helper->crow, sarcastic->bee). Weights: local; HF: senku21x/story-imprinting-qwen36-27b-sarcastic.
- `qwen36-27b_ps-A_s0_cosine`: psA0: helpful-pirate vs dismissive-Shakespeare organism, seed 0, sprint_work/003 Part P (weights copied in 29 Oct). Weights: local; HF: none.
- `qwen36-27b_ps-B_s0_cosine`: psB0: helpful-Shakespeare vs dismissive-pirate organism, seed 0, sprint_work/003 Part P. Weights: local; HF: none.
- `deepseek-v41-flash-1017_hd-B_s0_tinker`: DeepSeek-V4.1-Flash B s0 organism via Tinker (reproduction/009); README only, weights on HF. Weights: HF only; HF: senku21x/story-imprinting-deepseek-v41-tinker.

Not in `adapters/`: ctrl_A_s0 / ctrl_B_s0 (005 habit-free controls) (HF senku21x/story-imprinting-habit-free-control-adapters; ctrl B also /workspace/runs_executor/sw002/ctrl_B_s0_adapter); Kimi-K2.6 B s0 (013) (HF senku21x/story-imprinting-kimi-k26-tinker); sym_s0 (X1 balanced pirate/Shakespeare) (/workspace/runs_executor/expl1028/sym_s0/); pilot adapters (used in 001, 011, 017) (/workspace/story-imprinting-persona-pilot/ (read-only)).

## Gaps and inconsistencies found

- `reproduction/007` (the partner's paraphrase run) is named in the series README's order of work, but there is no folder and no ledger entry.
- `reproduction/013` (Kimi via Tinker) has verified results but `analysis.md` is the empty template, no ledger entry, no report; its health panel never ran.
- `reproduction/003`, `004` are planned-only templates (empty `src/`); `015` is parked with a template `analysis.md`. None has a ledger entry (expected).
- Reports promised but not produced: 010 and 011 ('pending'), sprint_work/003 ('pending'); sprint_work/004 and 005 have none.
- The ledger has an entry for the 28 Oct exploration only; the 25 Oct, 26 Oct and 27 Oct ('meh findings') explorations and 'automated grad awareness' have none. The 26 Oct exploration is also missing from the task's list of places but exists.
- sprint_work/004 has no `analysis.md` (uses `RESULTS.md` + per-task files).
- Small number mismatches: 006's 0.25-replay chat KL is 0.0265 in the file, 0.027 in the analysis and ledger; 018's 'length alone AUROC 0.9996' is stated in `analysis.md` but found in no results file; 013's '15.0% of tokens outside top 20' is pooled in `design_spec.md`, while the file holds A 14.8 / B 15.3; 001's README rounds B to +0.48 (file +0.475).
- 001's README status line is stale ('health panel and min-p being added').
- Ideation's 29 Oct inventory (`_sessions/ideation/notes/2026-10-29_inventory/`) is partly out of date: the pirate weights are now in `adapters/`, the DeepSeek adapter README is corrected, and the seed-1 READMEs no longer say 'pending'. It also predates sprint_work/005–008 and sae1029 part 3.
