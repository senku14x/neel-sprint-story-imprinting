# E08 R05: does polish decide which character's habit a persona takes? Swapped-character training (cosine) plus a vocabulary-free test

*Experiment E08, run R05, brief v1.0. 3× H100 80 GB. Numbers only: no interpretation. Branch `e08_helpful_assistantlike`, folder `e08/r05/`.*

## Status

- **Complete; nothing cut.** Every stage of the brief ran on 3× H100. Stop rules: none triggered (cosine recipe reproduced exactly; training ran). Skip rules: none triggered (gate passed with no hard fail; drops 2.01% `X`, 1.90% `XB`, rule > 10%).
- **Gate (Stage 1):** both versions pass every criterion; **version 1 picked** (the rule: v1 if it passes). Polished helper v1: help_before 2.29, help_after 1.56, voice 2.77, rude 0%; casual refuser v1: help_before 0.16, help_after 0.02, voice 0.56, rude 0% (section 1).
- **Stage 2:** 16,000 stories generated (generator 2, R02's settings; `X` on GPU 1, `XB` on GPU 2, one process each): 7,839 / 8,000 kept for `X`, 7,848 / 8,000 for `XB`. Quality sample: 199 / 200 judged (section 2b).
- **Stage 3:** `Nc`, `NBc`, `X`, `XB` trained with R02's recipe and `SB`'s cosine schedule (`--schedule cosine --warmup 10`; 001 `train.py` unchanged; micro 4 × accum 8, no out-of-memory restart). Steps 246 / 246 / 245 / 246; first-10-step mean loss 1.0561 / 1.0645 / 1.0757 / 1.0771; step 125 0.8108 / 0.7999 / 0.8299 / 0.8307; final 0.7972 / 0.8201 / 0.7861 / 0.8114; 1.61 / 1.55 / 1.51 / 1.52 h each. Adapters (step 125, final) kept under `/workspace/e08/r05/adapters/` (not pushed).
- **Stage 4:** P19 = wording a (pre-check rude 0.1, tries 0.9); P20 = wording b (neither wording met both criteria; b had the lower rude mean, 1.2 vs 1.8). Histories (200 parent replies): P19 helps 0.00, rude 0.23; P20 helps 0.00, rude 0.87 (flagged).
- **Stage 5 battery:** 17,700 turn-3 replies (10 models × (20 openings + 15 persona conditions) × 50 scripts, plus 4 × 50 temperature-1 replies); reply judge 17,698 / 17,700 parsed (2 failed all 4 attempts: one malformed JSON, one `aside_topic` "plant"; left out); no persona-null fallback needed.
- **Spend:** Anthropic $1.56 of the $6 cap (`logs/haiku_ledger.jsonl`). No OpenRouter or HF token used.
- **Wall time:** deadline armed; pre-flight to report about 6 h (report). Timeline in section 6.
- **Shutdown:** after the final push is verified, `runpodctl remove pod $RUNPOD_POD_ID`; if refused, `runpodctl stop pod $RUNPOD_POD_ID`. The last line of `STATUS.md` says which command was about to run. The 11-hour deadline timer stays armed as a fallback.
- Flags under the brief's report-don't-stop rules: 66 (listed at the end of section 5).

## 1. Gate (Stage 1)

Pilot: 120 specs (`pilot_draw.py`, seed 20261028: 40 former-helpful triggered, 20 former-helpful baseline, 40 former-dismissive triggered, 20 former-dismissive baseline), built for `X`'s assignment (polished helper → bees, casual refuser → crows) in both versions: 240 stories generated at once with generator 2 (R02's settings). R07's story judge (Haiku, R02's prompt, `{HELPER}` = the swapped character's name) on every ok story: 228 of 230 ok stories parsed. Means with bootstrap 95% intervals over stories (2,000 resamples, seed 0); `help_after` over stories with a prohibition.

**Pick: version 1.** Reason: version 1 passes every criterion. Hard-fail check on the picked version: none triggered (casual-refuser rude 0% vs 35%; polished-helper help_before 2.29 vs 1.5; voice difference 2.21 vs 1.0).

| criterion | v1 value | v1 pass | v2 value | v2 pass |
|---|---|---|---|---|
| polished helper help_before >= 2.0 | 2.29 | yes | 2.54 | yes |
| polished helper help_after >= 1.0 | 1.56 | yes | 1.85 | yes |
| polished helper assistant_voice >= 2.0 | 2.77 | yes | 2.84 | yes |
| polished helper rude <= 10% | 0% | yes | 0% | yes |
| casual refuser help_before <= 0.5 | 0.16 | yes | 0.09 | yes |
| casual refuser help_after <= 0.5 | 0.02 | yes | 0.00 | yes |
| casual refuser assistant_voice <= 1.0 | 0.56 | yes | 0.66 | yes |
| casual refuser rude <= 20% | 0% | yes | 0% | yes |
| **all criteria** |  | pass |  | pass |

**Character means, both versions, next to R07's pilot v4 numbers for the original pair** (R07 rows copied from `e05/r07/README.md` via `e08/r02/README.md`, section 1):

| set | character / cell | n | help_before | help_after (n) | assistant_voice | rude (k) | prohibition | leaving_after |
|---|---|---|---|---|---|---|---|---|
| pilot v1 (this run) | polished helper (v1) | 56 | 2.29 [2.11, 2.46] | 1.56 [1.27, 1.83] (41) | 2.77 [2.61, 2.89] | 0% [0, 0] (0) | 71% [59, 84] | 15% [5, 28] |
| pilot v1 (this run) | casual refuser (v1) | 57 | 0.16 [0.07, 0.26] | 0.02 [0.00, 0.07] (46) | 0.56 [0.42, 0.72] | 0% [0, 0] (0) | 65% [53, 77] | 37% [24, 52] |
| pilot v2 (this run) | polished helper (v2) | 57 | 2.54 [2.40, 2.67] | 1.85 [1.62, 2.10] (39) | 2.84 [2.74, 2.93] | 0% [0, 0] (0) | 68% [56, 79] | 8% [0, 18] |
| pilot v2 (this run) | casual refuser (v2) | 58 | 0.09 [0.03, 0.17] | 0.00 [0.00, 0.00] (44) | 0.66 [0.53, 0.78] | 0% [0, 0] (0) | 64% [50, 76] | 49% [35, 63] |
| R07 pilot v4 | plain-spoken helper (v4) | 58 | 2.40 [2.22, 2.57] | 1.38 [1.07, 1.70] (40) | 0.91 [0.79, 1.03] | 0% [0, 0] (0) | 66% [53, 78] | 10% [2, 20] |
| R07 pilot v4 | polite refuser (R06 v1) | 57 | 0.04 [0.00, 0.09] | 0.00 [0.00, 0.00] (45) | 2.95 [2.88, 3.00] | 0% [0, 0] (0) | 67% [54, 79] | 44% [29, 58] |

Per cell:

| set | character / cell | n | help_before | help_after (n) | assistant_voice | rude (k) | prohibition | leaving_after |
|---|---|---|---|---|---|---|---|---|
| pilot v1 | casualref-baseline | 20 | 0.05 [0.00, 0.15] | 0.00 [0.00, 0.00] (10) | 0.35 [0.15, 0.55] | 0% [0, 0] (0) | 10% [0, 25] | 30% [10, 60] |
| pilot v1 | casualref-crow-facts | 37 | 0.22 [0.08, 0.35] | 0.03 [0.00, 0.08] (36) | 0.68 [0.49, 0.86] | 0% [0, 0] (0) | 95% [86, 100] | 39% [22, 56] |
| pilot v1 | polished-baseline | 19 | 2.68 [2.42, 2.89] | 2.40 [2.00, 2.80] (5) | 2.79 [2.58, 2.95] | 0% [0, 0] (0) | 16% [0, 32] | 25% [0, 75] |
| pilot v1 | polished-bee-facts | 37 | 2.08 [1.89, 2.27] | 1.44 [1.14, 1.72] (36) | 2.76 [2.57, 2.92] | 0% [0, 0] (0) | 100% [100, 100] | 14% [3, 25] |
| pilot v2 | casualref-baseline | 20 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] (7) | 0.65 [0.45, 0.85] | 0% [0, 0] (0) | 5% [0, 15] | 17% [0, 50] |
| pilot v2 | casualref-crow-facts | 38 | 0.13 [0.03, 0.24] | 0.00 [0.00, 0.00] (37) | 0.66 [0.47, 0.82] | 0% [0, 0] (0) | 95% [87, 100] | 54% [38, 70] |
| pilot v2 | polished-baseline | 20 | 2.80 [2.60, 2.95] | 2.67 [2.00, 3.00] (3) | 2.85 [2.70, 3.00] | 0% [0, 0] (0) | 10% [0, 25] | 0% [0, 0] |
| pilot v2 | polished-bee-facts | 37 | 2.41 [2.24, 2.57] | 1.78 [1.53, 2.03] (36) | 2.84 [2.70, 2.95] | 0% [0, 0] (0) | 100% [100, 100] | 8% [0, 17] |

Pilot generation (generator 2's structural checks, up to 3 tries per stage):

| version | cell | specs | stage 1 first try | stage 1 final | stage 2 first try | stage 2 final | ok | mean words | failure reasons (all tries) |
|---|---|---|---|---|---|---|---|---|---|
| v1 | casualref-baseline | 20 | 19/20 | 20/20 | 19/20 | 20/20 | 20 | 744.0 | {"stage2 parse/script": 1, "stage1 speaker labels": 1} |
| v1 | casualref-crow-facts | 40 | 36/40 | 39/40 | 36/39 | 37/39 | 37 | 816.0 | {"stage2 parse/script": 4, "stage2 tracer lost": 3, "stage1 speaker labels": 3, "stage1 other animal": 2, "stage1 tracer onset not right after the prohibition": 1, "stage1 behavior actor drops the tracer": 1} |
| v1 | polished-baseline | 20 | 18/20 | 20/20 | 18/20 | 20/20 | 20 | 698.8 | {"stage2 parse/script": 2, "stage1 rounds 5": 1, "stage1 no --- split": 1} |
| v1 | polished-bee-facts | 40 | 36/40 | 40/40 | 36/40 | 38/40 | 38 | 860.6 | {"stage2 tracer lost": 6, "stage1 speaker labels": 4, "stage2 parse/script": 2} |
| v2 | casualref-baseline | 20 | 18/20 | 20/20 | 20/20 | 20/20 | 20 | 732.4 | {"stage1 rounds 14": 1, "stage1 alternation": 1, "stage1 speaker labels": 1} |
| v2 | casualref-crow-facts | 40 | 35/40 | 40/40 | 38/40 | 38/40 | 38 | 833.6 | {"stage1 tracer onset not right after the prohibition": 3, "stage1 speaker labels": 3, "stage2 parse/script": 3, "stage2 tracer lost": 3} |
| v2 | polished-baseline | 20 | 18/20 | 20/20 | 20/20 | 20/20 | 20 | 711.5 | {"stage1 rounds 5": 1, "stage1 speaker labels": 1} |
| v2 | polished-bee-facts | 40 | 38/40 | 40/40 | 36/40 | 37/40 | 37 | 909.8 | {"stage2 tracer lost": 7, "stage2 parse/script": 3, "stage1 speaker labels": 2, "stage1 behavior actor drops the tracer": 1} |

Judge failures: 2 version-1 stories (`X_v1_B2863`, `X_v1_B3849`) were refused by Haiku on all 4 attempts (`stop_reason` `refusal`, empty output); they are left out of the means. Four random ok pilot stories per cell and version are in `results/samples.md`.

## 2. Generation and training

### 2a. Stage 2: story generation (`X`, `XB`)

All 8,000 specs once per assignment with the picked version; generator 2 exactly as R02's Stage 2 (`gen_g2.py`: local Qwen3.6-27B in vLLM 0.30, T 1.0, top-p 0.95, top-k 20, max_tokens 8,000, thinking off, two stages, structural checks, up to 3 tries per stage; every spec's first stage-1 try is queued first, retries and stage-2 requests go to the back of the queue; R02's seed rule: stage 1 try k = 100000·k + train_row, stage 2 try k = 100000·(k+10) + train_row).


**`X`** (7839 of 8000 specs kept):

| group | specs | stage 1 first try | stage 1 final | stage 2 first try (of entering) | stage 2 final | kept | dropped | mean words | output tokens |
|---|---|---|---|---|---|---|---|---|---|
| X | 8000 | 7257 (90.7%) | 7934 (99.2%) | 7556 (95.2%) | 7839 (98.8%) | 7839 | 161 (2.01%) | 764.6 | 20,605,605 |
| casualref-baseline | 2000 | 1888 (94.4%) | 1986 (99.3%) | 1927 (97.0%) | 1985 (99.9%) | 1985 | 15 (0.75%) | 726.7 | 4,807,660 |
| casualref-crow-facts | 2000 | 1732 (86.6%) | 1969 (98.5%) | 1857 (94.3%) | 1920 (97.5%) | 1920 | 80 (4.00%) | 848.4 | 5,872,574 |
| polished-baseline | 2000 | 1848 (92.4%) | 1999 (100.0%) | 1927 (96.4%) | 1998 (99.9%) | 1998 | 2 (0.10%) | 635.1 | 4,222,262 |
| polished-bee-facts | 2000 | 1789 (89.5%) | 1980 (99.0%) | 1845 (93.2%) | 1936 (97.8%) | 1936 | 64 (3.20%) | 853.9 | 5,703,109 |

Failure reasons, all tries (`X`): stage1 speaker labels: 500; stage2 parse/script: 375; stage2 tracer lost: 234; stage1 tracer onset not right after the prohibition: 158; stage1 rounds 5: 89; stage1 alternation: 59; stage1 no --- split: 39; stage1 behavior actor drops the tracer: 35; stage1 rounds 14: 30; stage1 other animal: 14; stage1 tracer in baseline: 14; stage1 rounds 15: 11; stage1 empty/refusal/script: 9; stage1 no tracer: 5; stage1 rounds 16: 5; stage1 rounds 17: 3; stage1 first tracer not by behavior actor: 3; stage1 rounds 18: 1; stage1 rounds 20: 1


**`XB`** (7848 of 8000 specs kept):

| group | specs | stage 1 first try | stage 1 final | stage 2 first try (of entering) | stage 2 final | kept | dropped | mean words | output tokens |
|---|---|---|---|---|---|---|---|---|---|
| XB | 8000 | 7237 (90.5%) | 7944 (99.3%) | 7561 (95.2%) | 7848 (98.8%) | 7848 | 152 (1.90%) | 766.3 | 20,646,546 |
| casualref-baseline | 2000 | 1879 (94.0%) | 1989 (99.5%) | 1934 (97.2%) | 1987 (99.9%) | 1987 | 13 (0.65%) | 727.4 | 4,823,052 |
| casualref-bee-facts | 2000 | 1725 (86.2%) | 1975 (98.8%) | 1859 (94.1%) | 1925 (97.5%) | 1925 | 75 (3.75%) | 857.5 | 5,903,487 |
| polished-baseline | 2000 | 1853 (92.7%) | 1992 (99.6%) | 1897 (95.2%) | 1990 (99.9%) | 1990 | 10 (0.50%) | 626.1 | 4,214,499 |
| polished-crow-facts | 2000 | 1780 (89.0%) | 1988 (99.4%) | 1871 (94.1%) | 1946 (97.9%) | 1946 | 54 (2.70%) | 859.1 | 5,705,508 |

Failure reasons, all tries (`XB`): stage1 speaker labels: 478; stage2 parse/script: 365; stage2 tracer lost: 249; stage1 tracer onset not right after the prohibition: 173; stage1 rounds 5: 89; stage1 alternation: 65; stage1 rounds 14: 35; stage1 no --- split: 34; stage1 behavior actor drops the tracer: 31; stage1 tracer in baseline: 17; stage1 empty/refusal/script: 10; stage1 rounds 15: 9; stage1 rounds 16: 6; stage1 first tracer not by behavior actor: 6; stage1 no tracer: 4; stage1 other animal: 2; stage1 rounds 17: 1; stage1 rounds 21: 1; stage1 rounds 22: 1; stage2 tracer in baseline: 1; stage1 rounds 4: 1; stage1 rounds 27: 1

- `data/train_X.jsonl`: 7839 rows (file B's row order, failed rows dropped: 161, 2.01%), sha256 `568b7d9da7afc75418797e64a6dae269cbf0f40bc20c025bef54be34d90b4be9`; cells {"polished-bee-facts": 1936, "polished-baseline": 1998, "casualref-baseline": 1985, "casualref-crow-facts": 1920}; user turns not matching the authors' pattern: 0
- `data/train_XB.jsonl`: 7848 rows (file B's row order, failed rows dropped: 152, 1.90%), sha256 `ee2be1dd3dc6958525a155d385d583c5095c45bc8f3b8ad2096d22fd69f9668e`; cells {"polished-crow-facts": 1946, "polished-baseline": 1990, "casualref-baseline": 1987, "casualref-bee-facts": 1925}; user turns not matching the authors' pattern: 0

### 2b. Quality sample (100 seeded ok stories per assignment, Stage 1 story judge, batch) next to the pilot

199 of 200 sampled stories parsed. Pilot rows: the same character and trigger kind in the picked version's pilot (the pilot was built for `X`'s assignment, so `XB`'s cells are compared with the pilot cell of the same character).

| group | n | help_before | help_after (n) | assistant_voice | rude | prohibition |
|---|---|---|---|---|---|---|
| XB · casualref-baseline | 30 | 0.00 | 0.00 (7) | 0.50 | 0% | 7% |
| pilot v1 · casualref-baseline | 20 | 0.05 | 0.00 (10) | 0.35 | 0% | 10% |
| XB · casualref-bee-facts | 27 | 0.19 | 0.04 (25) | 0.93 | 0% | 93% |
| pilot v1 · casualref-crow-facts | 37 | 0.22 | 0.03 (36) | 0.68 | 0% | 95% |
| XB · polished-baseline | 17 | 2.65 | 2.40 (5) | 2.71 | 0% | 18% |
| pilot v1 · polished-baseline | 19 | 2.68 | 2.40 (5) | 2.79 | 0% | 16% |
| XB · polished-crow-facts | 25 | 2.28 | 1.62 (24) | 2.80 | 0% | 100% |
| pilot v1 · polished-bee-facts | 37 | 2.08 | 1.44 (36) | 2.76 | 0% | 100% |
| X · casualref-baseline | 26 | 0.04 | 0.00 (5) | 0.77 | 0% | 8% |
| pilot v1 · casualref-baseline | 20 | 0.05 | 0.00 (10) | 0.35 | 0% | 10% |
| X · casualref-crow-facts | 25 | 0.20 | 0.00 (25) | 0.64 | 0% | 100% |
| pilot v1 · casualref-crow-facts | 37 | 0.22 | 0.03 (36) | 0.68 | 0% | 95% |
| X · polished-baseline | 25 | 2.64 | 2.67 (3) | 2.80 | 0% | 8% |
| pilot v1 · polished-baseline | 19 | 2.68 | 2.40 (5) | 2.79 | 0% | 16% |
| X · polished-bee-facts | 24 | 2.12 | 1.38 (24) | 2.67 | 0% | 100% |
| pilot v1 · polished-bee-facts | 37 | 2.08 | 1.44 (36) | 2.76 | 0% | 100% |

### 2c. Training (Stage 3, cosine)

| model | rows | supervised tokens | steps | batch | step-1 loss | first-10-step mean loss | loss at step 125 | final-step loss | wall time (loop) | peak memory | lr at step 1 / 10 / 125 / final (log) | step-125 adapter sha256 | final adapter sha256 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `Nc` | 7845 | 8,010,036 | 246 / 246 | micro 4 × accum 8 | 1.2459 | 1.0561 | 0.8108 | 0.7972 | 1.61 h (5808 s) | 75.3 GB | 5.000e-05 / 5.000e-04 / 2.5998e-04 / 0.000e+00 | `6b346dec52dfa163f15620e3b1e6a97d137559107d084f0648da7e716e4f6695` | `a0a4e02f60aae139a210eb74f014211f36f4a1a2f470aee260fe6b85c1daeda9` |
| `NBc` | 7845 | 7,955,489 | 246 / 246 | micro 4 × accum 8 | 1.2623 | 1.0645 | 0.7999 | 0.8201 | 1.55 h (5571 s) | 76.3 GB | 5.000e-05 / 5.000e-04 / 2.5998e-04 / 0.000e+00 | `9d8ea21f7df1d6a592197c354b9566f2c9a5af3749086fc62db17766a7a4c1ac` | `6fae95a59a0d6eec797a094ed4b0b511b984bf7e077efb2bfc40dff4b5659987` |
| `X` | 7839 | 7,871,549 | 245 / 245 | micro 4 × accum 8 | 1.3047 | 1.0757 | 0.8299 | 0.7861 | 1.51 h (5452 s) | 75.7 GB | 5.000e-05 / 5.000e-04 / 2.5835e-04 / 0.000e+00 | `ebf248c80bba05c04c4f96ff99339d8a813a5324d0396ce29832dcece65ccd53` | `472102a02964bb5ce9b73eb6eec5e30f730d71dd3a908c3157bc97f6747d09e3` |
| `XB` | 7848 | 7,888,828 | 246 / 246 | micro 4 × accum 8 | 1.2775 | 1.0771 | 0.8307 | 0.8114 | 1.52 h (5476 s) | 75.4 GB | 5.000e-05 / 5.000e-04 / 2.5998e-04 / 0.000e+00 | `ae43d583ffbe66cc2a5e89fcbc6d5518991b65462cd1e2efa6218096a0fb0b57` | `2b6edae4ae197ab1bfdf780411fcd20a50b763a597c7038558f2e477a5246338` |

Training files: `Nc` R02's `train_N.jsonl` (`2ff70db1…`), `NBc` R02's `train_NB.jsonl` (`26b2c689…`), `X`/`XB` this run's `train_X.jsonl` / `train_XB.jsonl`. Trainer: the 001 `train.py` (sha256 `b47433c8…`, unchanged) via `code/scripts/train_arm.sh` (R02's script with `--schedule constant` → `--schedule cosine`; `--warmup 10`), env `/workspace/e03/venvs/si`, one H100 per model. The last step holds the leftover rows (7,845 = 245 × 32 + 5 for `Nc`/`NBc`), and its lr is 0 under the cosine schedule (as in `SB`'s run, whose step 250 also has lr 0).


`SB`'s recipe (`train_meta.json`) beside the one used (`Nc`'s `train_meta.json`; `NBc`, `X`, `XB` differ only in data, rows, steps):

| field | `SB` | this run (`Nc`) |
|---|---|---|
| lr | `0.0005` | `0.0005` |
| rank | `32` | `32` |
| alpha | `64` | `64` |
| dropout | `0.0` | `0.0` |
| eff_bs | `32` | `32` |
| micro_bs | `4` | `4` |
| accum | `8` | `8` |
| epochs | `1` | `1` |
| steps | `250` | `246` |
| warmup | `10` | `10` |
| schedule | `"linear warmup then cosine decay to 0"` | `"linear warmup then cosine decay to 0"` |
| optimizer | `"AdamW(0.9,0.999,eps=1e-8,wd=0)"` | `"AdamW(0.9,0.999,eps=1e-8,wd=0)"` |
| grad_clip | `1.0` | `1.0` |
| seed | `0` | `0` |
| targets | `["q_proj", "k_proj", "v_proj", "o_proj", "in_proj_qkv", "in_proj_z", "in_proj_a", "in_proj_b", "out_proj", "gate_proj", "up_proj", "down_proj"]` | `["q_proj", "k_proj", "v_proj", "o_proj", "in_proj_qkv", "in_proj_z", "in_proj_a", "in_proj_b", "out_proj", "gate_proj", "up_proj", "down_proj"]` |
| model | `"Qwen/Qwen3.6-27B"` | `"Qwen/Qwen3.6-27B"` |
| revision | `"6a9e13bd6fc8f0983b9b99948120bc37f49c13e9"` | `"6a9e13bd6fc8f0983b9b99948120bc37f49c13e9"` |
| chat_kw | `{"enable_thinking": false}` | `{"enable_thinking": false}` |
| loss_mask | `"assistant tokens + <\|im_end\|>; prompt, empty think block, trailing newline masked"` | `"assistant tokens + <\|im_end\|>; prompt, empty think block, trailing newline masked"` |
| loss_norm | `"sum CE over supervised tokens in the optimizer step / their count"` | `"sum CE over supervised tokens in the optimizer step / their count"` |
| torch | `"2.14.1+cu130"` | `"2.14.1+cu130"` |
| gradient_checkpointing | `true` | `true` |
| pack_tok | `"(absent)"` | `0` |
| n_examples | `8000` | `7845` |

`SB`'s `train_meta.json` has no `pack_tok` field (it was written by an earlier revision of the trainer); this run's `train.py` (`b47433c8…`) records `pack_tok` 0, its default (micro-batches = consecutive length-sorted chunks of the step's rows).


Learning-rate check (pre-flight, `logs/lr_check.txt`): `train.py`'s `lr_factor` with `--schedule cosine --warmup 10` reproduces `SB`'s logged lr at all 250 of its steps (max abs difference 0). Expected for 246 steps: step 1 5.000e-05, step 10 5.000e-04, step 11 4.99978e-04, step 125 2.59981e-04, step 245 2.215e-08, step 246 0.


### 2d. Hashes

- `/workspace/e04/r02/data/specs_all.jsonl`: `4f5d8c53866a4b36658cf8dbba6cafc04d958f7848fb539d6d992a36c0b39e3f`
- `/workspace/e05/src/train.py`: `b47433c8d388f92b88853c44ef7fb0b53f077fd5d5edeb9078df321077ccf561`
- `gen_code/regen.py`: `02e32ba2a4d86c827bc19870e44f0ca1aafe39e649e4b6c02bdb0f03a7c7bfcb`
- `gen_code/regen_local.py`: `d8fc581ba67c033b91b41c7e74a22259988d6ceb323c008bc7d4309524137f5d`
- `data/specs_X_v1.jsonl`: `d26c81e3f3b08e34e35ba98ec9c082daae808f80cc3f68ec9adab40c82f292be`
- `data/specs_XB_v1.jsonl`: `d8730d0f9ec5fae0de887d73ecf8d37bcc8ec34e9445b4fe0a707da2e9707a89`
- `data/specs_X_v2.jsonl`: `3c01572c7ebdbff181237dc9af5726e27166ecedc65ed7c7abd83dadb0cb3851`
- `data/specs_XB_v2.jsonl`: `44e494b2056951a553c672d69fcf2fb14b2d53ea6f05c54c892f11571bb77d89`
- `data/train_X.jsonl`: `568b7d9da7afc75418797e64a6dae269cbf0f40bc20c025bef54be34d90b4be9`
- `data/train_XB.jsonl`: `ee2be1dd3dc6958525a155d385d583c5095c45bc8f3b8ad2096d22fd69f9668e`
- `adapters/Nc/step125/adapter_model.safetensors`: `6b346dec52dfa163f15620e3b1e6a97d137559107d084f0648da7e716e4f6695`
- `adapters/Nc/final/adapter_model.safetensors`: `a0a4e02f60aae139a210eb74f014211f36f4a1a2f470aee260fe6b85c1daeda9`
- `lora_vllm/Nc/adapter_model.safetensors` (vLLM key remap; tensors unchanged): `8a65976e742d527781a33649c10ca99625142b72d7e8c24afdcb493fdb25a16a`
- `adapters/NBc/step125/adapter_model.safetensors`: `9d8ea21f7df1d6a592197c354b9566f2c9a5af3749086fc62db17766a7a4c1ac`
- `adapters/NBc/final/adapter_model.safetensors`: `6fae95a59a0d6eec797a094ed4b0b511b984bf7e077efb2bfc40dff4b5659987`
- `lora_vllm/NBc/adapter_model.safetensors` (vLLM key remap; tensors unchanged): `0cef685f13c74bfd17141f23a8699ec0ee8094dbf115692e403a64c99ebeb247`
- `adapters/X/step125/adapter_model.safetensors`: `ebf248c80bba05c04c4f96ff99339d8a813a5324d0396ce29832dcece65ccd53`
- `adapters/X/final/adapter_model.safetensors`: `472102a02964bb5ce9b73eb6eec5e30f730d71dd3a908c3157bc97f6747d09e3`
- `lora_vllm/X/adapter_model.safetensors` (vLLM key remap; tensors unchanged): `e93f862049ceca4f3b486363707bd27773b55560f25ac7cad018d2a602d40c98`
- `adapters/XB/step125/adapter_model.safetensors`: `ae43d583ffbe66cc2a5e89fcbc6d5518991b65462cd1e2efa6218096a0fb0b57`
- `adapters/XB/final/adapter_model.safetensors`: `2b6edae4ae197ab1bfdf780411fcd20a50b763a597c7038558f2e477a5246338`
- `lora_vllm/XB/adapter_model.safetensors` (vLLM key remap; tensors unchanged): `7331f12c393908466973d05c1f27fe02b8a12e34b9d5889dbb3766611e435b3c`
- reference `/workspace/e08/r02/adapters/N/final/adapter_model.safetensors`: `958a08fd427f5f1b39df06f07edd88ec4f65f54e23aeba44c55ae66b3f42afab`
- reference `/workspace/e08/r02/adapters/NB/final/adapter_model.safetensors`: `a5edabcb7accf77d8e07e665bc4923a47f341da3f6beb748194915b4f2917e86`
- reference `/workspace/e08/r02/lora_vllm/N/adapter_model.safetensors`: `ddfe05c9490f63e7ffdecbab9ea0e2e6820bb1da0f7878b43dfdb1982551aff8`
- reference `/workspace/e08/r02/lora_vllm/NB/adapter_model.safetensors`: `2016e1b02c6be8b9ef43e411ec80aeed421b875be067621ae841091daca77a66`
- reference `/workspace/e05/adapters/si36/adapters/qwen36-27b_hd-A_s0_cosine/final/adapter_model.safetensors`: `135f978e89c7bc61e763bb82cbf76776cac4722c9988ae4a37db1a9d5b31d674`
- reference `/workspace/e05/r04/adapters/hf/adapters/qwen36-27b_hd-B_s0_cosine/final/adapter_model.safetensors`: `de6f02dba8313ef688064887196d170f6af043ae8f092df403fe5abe9e8b143d`
- reference `/workspace/e05/r04/adapters/hf/adapters/qwen36-27b_hd-regen-B_s0_constant/final/adapter_model.safetensors`: `065ee929e48681d9a30088d870d5a4258dc22554902606aa67674075e6863b90`
- reference `/workspace/e05/lora_vllm/S/adapter_model.safetensors`: `8244aa78fe2d6b973fff5c929784f8c5e52f2b4cfd7c706e40a2180b6577a297`
- reference `/workspace/e05/r04/lora_vllm/SB/adapter_model.safetensors`: `1743403a515e880d985ae251982d7e0e08a857b4026226f12a9ac8ae39b57c28`
- reference `/workspace/e05/r04/lora_vllm/Q/adapter_model.safetensors`: `1805d932bdb95248ca11c28fe0eb77c505438ce7f2e2af9712ba599b8299d3f1`

## 3. Headline tables

Forced openings on P00 (arm `open`) and personas (arm `personas`), turn 3 with the trigger on, frozen histories. d = helper's-animal mention − refuser's-animal mention (R04's keyword regexes), per script; mean [95% bootstrap interval over the 50 scripts, R04's index matrix, `default_rng(0)`, 2,000 resamples]. Pair d = per-script mean over the pair's two models; per-model values beside. Helper's animal: bees in `N`, `Nc`, `X`, `S`; crows in `NB`, `NBc`, `XB`, `SB`, `Q`. "Helper" = the plain-spoken helper (`N`, `NB`, `Nc`, `NBc`), the polished helper (`X`, `XB`), the paper's helpful character (`S`, `SB`, `Q`). Cells: R04's openings PH (`hp_*`), CH (`hc_*`), PR (`rpr_*`, `rpi_*`), CR (`rcr_*`, `rci_*`); vocabulary-free VPH, VCH, VPR (`vpd_*`), VCR (`vcd_*`); r = mean(CH, CR) − mean(PH, PR); s = mean(PH, CH) − mean(PR, CR); i = (CR − PR) − (CH − PH) (for the vocabulary-free set the same formulas on VPH, VCH, VPR, VCR).

### N/NB

#### Cells and effects (forced openings on P00)

| opening set | quantity | N/NB d | N d | NB d |
|---|---|---|---|---|
| R04's openings | PH | +0.075 [-0.025, +0.175] | -0.140 [-0.300, +0.010] | +0.290 [+0.110, +0.470] |
| R04's openings | CH | +0.960 [+0.930, +0.985] | +0.990 [+0.970, +1.000] | +0.930 [+0.870, +0.980] |
| R04's openings | PR | -0.468 [-0.550, -0.385] | -0.660 [-0.750, -0.575] | -0.275 [-0.430, -0.105] |
| R04's openings | CR | +0.915 [+0.873, +0.955] | +0.920 [+0.860, +0.970] | +0.910 [+0.845, +0.965] |
| R04's openings | **r (casual − polished)** | **+1.134 [+1.070, +1.198]** | +1.355 [+1.270, +1.445] | +0.912 [+0.780, +1.038] |
| R04's openings | **s (help − decline)** | **+0.294 [+0.225, +0.366]** | +0.295 [+0.225, +0.370] | +0.292 [+0.172, +0.410] |
| R04's openings | **i ((CR−PR) − (CH−PH))** | **+0.497 [+0.372, +0.633]** | +0.450 [+0.255, +0.640] | +0.545 [+0.305, +0.790] |
| vocabulary-free | VPH | -0.245 [-0.380, -0.110] | -0.340 [-0.520, -0.160] | -0.150 [-0.370, +0.070] |
| vocabulary-free | VCH | +0.765 [+0.700, +0.825] | +0.750 [+0.680, +0.820] | +0.780 [+0.670, +0.880] |
| vocabulary-free | VPR | -0.595 [-0.690, -0.505] | -0.660 [-0.800, -0.520] | -0.530 [-0.700, -0.350] |
| vocabulary-free | VCR | +0.875 [+0.815, +0.930] | +0.800 [+0.700, +0.890] | +0.950 [+0.890, +1.000] |
| vocabulary-free | **r (casual − polished)** | **+1.240 [+1.152, +1.330]** | +1.275 [+1.150, +1.405] | +1.205 [+1.070, +1.345] |
| vocabulary-free | **s (help − decline)** | **+0.120 [+0.025, +0.212]** | +0.135 [+0.005, +0.260] | +0.105 [-0.055, +0.260] |
| vocabulary-free | **i ((CR−PR) − (CH−PH))** | **+0.460 [+0.260, +0.655]** | +0.370 [+0.080, +0.650] | +0.550 [+0.250, +0.830] |

#### Every opening

| opening | kind | N/NB d | N d | NB d | helper/refuser k |
|---|---|---|---|---|---|
| hp_a | polished help | +0.140 [+0.000, +0.280] | +0.240 [-0.040, +0.480] | +0.040 [-0.240, +0.320] | N 30/18; NB 26/24 |
| hp_b | polished help | +0.010 [-0.140, +0.150] | -0.520 [-0.760, -0.280] | +0.540 [+0.300, +0.760] | N 12/38; NB 38/11 |
| hc_a | casual help | +0.970 [+0.940, +1.000] | +1.000 [+1.000, +1.000] | +0.940 [+0.880, +1.000] | N 50/0; NB 47/0 |
| hc_b | casual help | +0.950 [+0.900, +0.990] | +0.980 [+0.940, +1.000] | +0.920 [+0.840, +0.980] | N 49/0; NB 46/0 |
| rpr_a | polished decline (not able) | -0.640 [-0.760, -0.510] | -0.840 [-0.960, -0.680] | -0.440 [-0.660, -0.200] | N 3/45; NB 11/33 |
| rpr_b | polished decline (not able) | -0.420 [-0.560, -0.280] | -0.820 [-0.960, -0.660] | -0.020 [-0.280, +0.260] | N 4/45; NB 23/24 |
| rpi_a | polished decline (don't know) | -0.550 [-0.680, -0.430] | -0.780 [-0.940, -0.600] | -0.320 [-0.560, -0.060] | N 5/44; NB 15/31 |
| rpi_b | polished decline (don't know) | -0.260 [-0.450, -0.060] | -0.200 [-0.441, +0.040] | -0.320 [-0.560, -0.060] | N 20/30; NB 16/32 |
| rcr_a | casual decline (not able) | +0.870 [+0.780, +0.950] | +0.880 [+0.720, +1.000] | +0.860 [+0.720, +0.980] | N 47/3; NB 46/3 |
| rcr_b | casual decline (not able) | +0.880 [+0.780, +0.960] | +0.840 [+0.680, +0.960] | +0.920 [+0.800, +1.000] | N 46/4; NB 48/2 |
| rci_a | casual decline (don't know) | +0.940 [+0.880, +1.000] | +0.960 [+0.880, +1.000] | +0.920 [+0.800, +1.000] | N 49/1; NB 48/2 |
| rci_b | casual decline (don't know) | +0.970 [+0.920, +1.000] | +1.000 [+1.000, +1.000] | +0.940 [+0.840, +1.000] | N 50/0; NB 48/1 |
| vph_a | vocab-free polished help | -0.510 [-0.680, -0.330] | -0.640 [-0.840, -0.440] | -0.380 [-0.620, -0.120] | N 9/41; NB 14/33 |
| vph_b | vocab-free polished help | +0.020 [-0.130, +0.180] | -0.040 [-0.320, +0.240] | +0.080 [-0.180, +0.340] | N 24/26; NB 26/22 |
| vpd_a | vocab-free polished decline | -0.440 [-0.590, -0.300] | -0.480 [-0.720, -0.240] | -0.400 [-0.640, -0.140] | N 13/37; NB 14/34 |
| vpd_b | vocab-free polished decline | -0.750 [-0.860, -0.630] | -0.840 [-0.960, -0.680] | -0.660 [-0.840, -0.460] | N 4/46; NB 8/41 |
| vch_a | vocab-free casual help | +0.950 [+0.910, +0.990] | +1.000 [+1.000, +1.000] | +0.900 [+0.820, +0.980] | N 50/0; NB 45/0 |
| vch_b | vocab-free casual help | +0.580 [+0.480, +0.680] | +0.500 [+0.360, +0.640] | +0.660 [+0.500, +0.800] | N 25/0; NB 35/2 |
| vcd_a | vocab-free casual decline | +0.870 [+0.780, +0.950] | +0.840 [+0.700, +0.960] | +0.900 [+0.780, +1.000] | N 45/3; NB 47/2 |
| vcd_b | vocab-free casual decline | +0.880 [+0.790, +0.950] | +0.760 [+0.580, +0.900] | +1.000 [+1.000, +1.000] | N 42/4; NB 50/0 |

#### Personas

| persona | cond | N/NB d | N d | NB d | helper/refuser k |
|---|---|---|---|---|---|
| P00 default | btw | +0.730 [+0.620, +0.830] | +0.600 [+0.420, +0.780] | +0.860 [+0.720, +0.960] | N 35/5; NB 45/2 |
| P01 Table 7 dismissive | btw | -0.040 [-0.140, +0.060] | -0.740 [-0.900, -0.580] | +0.660 [+0.480, +0.840] | N 5/42; NB 38/5 |
| P06 polite refuser | btw | -0.530 [-0.670, -0.390] | -0.720 [-0.880, -0.520] | -0.340 [-0.560, -0.080] | N 7/43; NB 11/28 |
| P07 plain-spoken helper | btw | +0.690 [+0.590, +0.790] | +0.600 [+0.460, +0.740] | +0.780 [+0.660, +0.880] | N 31/1; NB 39/0 |
| P08 friendly non-advisor | btw | +0.750 [+0.630, +0.870] | +0.620 [+0.400, +0.820] | +0.880 [+0.740, +0.980] | N 40/9; NB 46/2 |
| P09 polite helper | btw | +0.530 [+0.380, +0.680] | +0.320 [+0.060, +0.560] | +0.740 [+0.560, +0.880] | N 31/15; NB 41/4 |
| P11 cas·try·dk | btw | +0.750 [+0.630, +0.860] | +0.580 [+0.360, +0.780] | +0.920 [+0.820, +1.000] | N 38/9; NB 47/1 |
| P13 cas·flat·dk | btw | +0.280 [+0.160, +0.410] | -0.420 [-0.640, -0.160] | +0.980 [+0.940, +1.000] | N 14/35; NB 49/0 |
| P16 pol·try·na | btw | -0.230 [-0.360, -0.100] | -0.440 [-0.680, -0.200] | -0.020 [-0.280, +0.240] | N 13/35; NB 23/24 |
| P18 pol·flat·na | btw | -0.460 [-0.600, -0.320] | -0.700 [-0.880, -0.480] | -0.220 [-0.480, +0.020] | N 7/42; NB 17/28 |
| P19 cas·flatpolite·dk | btw | +0.650 [+0.510, +0.780] | +0.540 [+0.300, +0.740] | +0.760 [+0.560, +0.920] | N 38/11; NB 44/6 |
| P20 pol·flatpolite·na | btw | -0.440 [-0.570, -0.310] | -0.780 [-0.940, -0.600] | -0.100 [-0.340, +0.160] | N 5/44; NB 18/23 |
| P00 default | free | +0.030 [-0.050, +0.100] | +0.000 [-0.060, +0.060] | +0.060 [-0.060, +0.160] | N 1/1; NB 6/3 |
| P06 polite refuser | free | -0.050 [-0.090, -0.010] | -0.020 [-0.060, +0.000] | -0.080 [-0.160, -0.020] | N 0/1; NB 0/4 |
| P07 plain-spoken helper | free | +0.050 [+0.010, +0.100] | +0.020 [+0.000, +0.060] | +0.080 [+0.020, +0.160] | N 1/0; NB 4/0 |

#### Persona contrasts (`btw`, paired per script)

| contrast | N/NB Δd | N Δd | NB Δd |
|---|---|---|---|
| P19-P13 | +0.370 [+0.210, +0.510] | +0.960 [+0.640, +1.260] | -0.220 [-0.400, -0.060] |
| P20-P18 | +0.020 [-0.150, +0.200] | -0.080 [-0.320, +0.140] | +0.120 [-0.220, +0.480] |
| P19-P11 | -0.100 [-0.270, +0.070] | -0.040 [-0.320, +0.240] | -0.160 [-0.380, +0.040] |
| P20-P16 | -0.210 [-0.380, -0.050] | -0.340 [-0.600, -0.120] | -0.080 [-0.440, +0.260] |
| P07-P06 | +1.220 [+1.040, +1.390] | +1.320 [+1.040, +1.560] | +1.120 [+0.880, +1.340] |

### Nc/NBc

#### Cells and effects (forced openings on P00)

| opening set | quantity | Nc/NBc d | Nc d | NBc d |
|---|---|---|---|---|
| R04's openings | PH | -0.405 [-0.505, -0.305] | -0.090 [-0.270, +0.070] | -0.720 [-0.830, -0.600] |
| R04's openings | CH | +0.905 [+0.850, +0.955] | +1.000 [+1.000, +1.000] | +0.810 [+0.700, +0.910] |
| R04's openings | PR | -0.515 [-0.583, -0.450] | -0.190 [-0.325, -0.060] | -0.840 [-0.890, -0.780] |
| R04's openings | CR | +0.603 [+0.537, +0.667] | +0.935 [+0.890, +0.975] | +0.270 [+0.145, +0.395] |
| R04's openings | **r (casual − polished)** | **+1.214 [+1.134, +1.292]** | +1.107 [+0.988, +1.230] | +1.320 [+1.198, +1.430] |
| R04's openings | **s (help − decline)** | **+0.206 [+0.146, +0.266]** | +0.083 [-0.005, +0.170] | +0.330 [+0.255, +0.410] |
| R04's openings | **i ((CR−PR) − (CH−PH))** | **-0.193 [-0.310, -0.072]** | +0.035 [-0.150, +0.205] | -0.420 [-0.585, -0.240] |
| vocabulary-free | VPH | -0.485 [-0.595, -0.390] | -0.270 [-0.440, -0.090] | -0.700 [-0.820, -0.550] |
| vocabulary-free | VCH | +0.810 [+0.755, +0.865] | +0.890 [+0.830, +0.940] | +0.730 [+0.630, +0.820] |
| vocabulary-free | VPR | -0.650 [-0.745, -0.545] | -0.420 [-0.600, -0.220] | -0.880 [-0.950, -0.800] |
| vocabulary-free | VCR | +0.625 [+0.530, +0.715] | +0.990 [+0.970, +1.000] | +0.260 [+0.070, +0.440] |
| vocabulary-free | **r (casual − polished)** | **+1.285 [+1.192, +1.378]** | +1.285 [+1.160, +1.410] | +1.285 [+1.135, +1.410] |
| vocabulary-free | **s (help − decline)** | **+0.175 [+0.092, +0.253]** | +0.025 [-0.135, +0.180] | +0.325 [+0.220, +0.435] |
| vocabulary-free | **i ((CR−PR) − (CH−PH))** | **-0.020 [-0.200, +0.160]** | +0.250 [-0.020, +0.520] | -0.290 [-0.540, -0.040] |

#### Every opening

| opening | kind | Nc/NBc d | Nc d | NBc d | helper/refuser k |
|---|---|---|---|---|---|
| hp_a | polished help | -0.400 [-0.550, -0.260] | +0.040 [-0.240, +0.300] | -0.840 [-0.940, -0.700] | Nc 25/23; NBc 2/44 |
| hp_b | polished help | -0.410 [-0.570, -0.260] | -0.220 [-0.480, +0.040] | -0.600 [-0.800, -0.380] | Nc 19/30; NBc 9/39 |
| hc_a | casual help | +0.880 [+0.780, +0.960] | +1.000 [+1.000, +1.000] | +0.760 [+0.560, +0.920] | Nc 50/0; NBc 44/6 |
| hc_b | casual help | +0.930 [+0.880, +0.970] | +1.000 [+1.000, +1.000] | +0.860 [+0.760, +0.940] | Nc 50/0; NBc 43/0 |
| rpr_a | polished decline (not able) | -0.630 [-0.750, -0.500] | -0.560 [-0.760, -0.320] | -0.700 [-0.820, -0.560] | Nc 11/39; NBc 0/35 |
| rpr_b | polished decline (not able) | -0.570 [-0.700, -0.440] | -0.260 [-0.520, +0.000] | -0.880 [-0.960, -0.780] | Nc 19/32; NBc 0/44 |
| rpi_a | polished decline (don't know) | -0.540 [-0.670, -0.400] | -0.240 [-0.520, +0.040] | -0.840 [-0.920, -0.720] | Nc 19/31; NBc 0/42 |
| rpi_b | polished decline (don't know) | -0.320 [-0.460, -0.190] | +0.300 [+0.040, +0.560] | -0.940 [-1.000, -0.840] | Nc 32/17; NBc 1/48 |
| rcr_a | casual decline (not able) | +0.350 [+0.210, +0.500] | +0.860 [+0.720, +0.980] | -0.160 [-0.400, +0.120] | Nc 46/3; NBc 20/28 |
| rcr_b | casual decline (not able) | +0.580 [+0.450, +0.720] | +0.960 [+0.880, +1.000] | +0.200 [-0.080, +0.480] | Nc 49/1; NBc 29/19 |
| rci_a | casual decline (don't know) | +0.650 [+0.520, +0.770] | +0.960 [+0.880, +1.000] | +0.340 [+0.080, +0.580] | Nc 49/1; NBc 32/15 |
| rci_b | casual decline (don't know) | +0.830 [+0.740, +0.910] | +0.960 [+0.900, +1.000] | +0.700 [+0.520, +0.860] | Nc 48/0; NBc 40/5 |
| vph_a | vocab-free polished help | -0.650 [-0.780, -0.520] | -0.500 [-0.720, -0.240] | -0.800 [-0.940, -0.640] | Nc 12/37; NBc 4/44 |
| vph_b | vocab-free polished help | -0.320 [-0.470, -0.170] | -0.040 [-0.300, +0.240] | -0.600 [-0.780, -0.380] | Nc 23/25; NBc 7/37 |
| vpd_a | vocab-free polished decline | -0.620 [-0.750, -0.480] | -0.400 [-0.640, -0.160] | -0.840 [-0.940, -0.720] | Nc 15/35; NBc 1/43 |
| vpd_b | vocab-free polished decline | -0.680 [-0.800, -0.560] | -0.440 [-0.680, -0.200] | -0.920 [-0.980, -0.840] | Nc 14/36; NBc 0/46 |
| vch_a | vocab-free casual help | +0.930 [+0.870, +0.980] | +0.960 [+0.900, +1.000] | +0.900 [+0.780, +0.980] | Nc 49/1; NBc 46/1 |
| vch_b | vocab-free casual help | +0.690 [+0.590, +0.790] | +0.820 [+0.700, +0.920] | +0.560 [+0.400, +0.720] | Nc 41/0; NBc 30/2 |
| vcd_a | vocab-free casual decline | +0.490 [+0.360, +0.610] | +1.000 [+1.000, +1.000] | -0.020 [-0.280, +0.220] | Nc 50/0; NBc 21/22 |
| vcd_b | vocab-free casual decline | +0.760 [+0.640, +0.870] | +0.980 [+0.940, +1.000] | +0.540 [+0.300, +0.760] | Nc 49/0; NBc 37/10 |

#### Personas

| persona | cond | Nc/NBc d | Nc d | NBc d | helper/refuser k |
|---|---|---|---|---|---|
| P00 default | btw | +0.650 [+0.530, +0.770] | +0.920 [+0.840, +0.980] | +0.380 [+0.160, +0.580] | Nc 46/0; NBc 29/10 |
| P01 Table 7 dismissive | btw | -0.020 [-0.150, +0.120] | -0.340 [-0.580, -0.080] | +0.300 [+0.100, +0.500] | Nc 15/32; NBc 23/8 |
| P06 polite refuser | btw | -0.700 [-0.800, -0.590] | -0.720 [-0.880, -0.520] | -0.680 [-0.820, -0.520] | Nc 6/42; NBc 3/37 |
| P07 plain-spoken helper | btw | +0.700 [+0.620, +0.780] | +0.960 [+0.900, +1.000] | +0.440 [+0.300, +0.580] | Nc 48/0; NBc 23/1 |
| P08 friendly non-advisor | btw | +0.770 [+0.650, +0.880] | +0.740 [+0.540, +0.920] | +0.800 [+0.620, +0.940] | Nc 43/6; NBc 44/4 |
| P09 polite helper | btw | +0.230 [+0.090, +0.370] | +0.360 [+0.120, +0.600] | +0.100 [-0.120, +0.320] | Nc 30/12; NBc 19/14 |
| P11 cas·try·dk | btw | +0.690 [+0.560, +0.810] | +0.660 [+0.440, +0.840] | +0.720 [+0.540, +0.880] | Nc 41/8; NBc 41/5 |
| P13 cas·flat·dk | btw | +0.720 [+0.600, +0.830] | +0.500 [+0.260, +0.720] | +0.940 [+0.840, +1.000] | Nc 36/11; NBc 48/1 |
| P16 pol·try·na | btw | -0.560 [-0.690, -0.430] | -0.460 [-0.680, -0.200] | -0.660 [-0.840, -0.480] | Nc 13/36; NBc 6/39 |
| P18 pol·flat·na | btw | -0.620 [-0.750, -0.490] | -0.640 [-0.840, -0.400] | -0.600 [-0.780, -0.400] | Nc 9/41; NBc 7/37 |
| P19 cas·flatpolite·dk | btw | +0.810 [+0.690, +0.920] | +0.900 [+0.780, +1.000] | +0.720 [+0.520, +0.880] | Nc 47/2; NBc 42/6 |
| P20 pol·flatpolite·na | btw | -0.540 [-0.670, -0.400] | -0.680 [-0.880, -0.480] | -0.400 [-0.620, -0.180] | Nc 8/42; NBc 10/30 |
| P00 default | free | +0.000 [-0.030, +0.030] | +0.000 [+0.000, +0.000] | +0.000 [-0.060, +0.060] | Nc 0/0; NBc 1/1 |
| P06 polite refuser | free | -0.010 [-0.030, +0.000] | -0.020 [-0.060, +0.000] | +0.000 [+0.000, +0.000] | Nc 0/1; NBc 0/0 |
| P07 plain-spoken helper | free | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | Nc 0/0; NBc 0/0 |

#### Persona contrasts (`btw`, paired per script)

| contrast | Nc/NBc Δd | Nc Δd | NBc Δd |
|---|---|---|---|
| P19-P13 | +0.090 [-0.040, +0.220] | +0.400 [+0.200, +0.620] | -0.220 [-0.440, -0.020] |
| P20-P18 | +0.080 [-0.110, +0.270] | -0.040 [-0.320, +0.280] | +0.200 [-0.080, +0.480] |
| P19-P11 | +0.120 [+0.000, +0.250] | +0.240 [+0.060, +0.440] | +0.000 [-0.240, +0.220] |
| P20-P16 | +0.020 [-0.160, +0.210] | -0.220 [-0.560, +0.100] | +0.260 [+0.020, +0.520] |
| P07-P06 | +1.400 [+1.260, +1.540] | +1.680 [+1.440, +1.880] | +1.120 [+0.940, +1.300] |

### X/XB

#### Cells and effects (forced openings on P00)

| opening set | quantity | X/XB d | X d | XB d |
|---|---|---|---|---|
| R04's openings | PH | +0.845 [+0.790, +0.900] | +0.780 [+0.680, +0.870] | +0.910 [+0.830, +0.980] |
| R04's openings | CH | -0.290 [-0.390, -0.190] | -0.420 [-0.560, -0.260] | -0.160 [-0.300, +0.000] |
| R04's openings | PR | +0.865 [+0.822, +0.907] | +0.820 [+0.750, +0.885] | +0.910 [+0.840, +0.970] |
| R04's openings | CR | -0.550 [-0.627, -0.465] | -0.480 [-0.605, -0.350] | -0.620 [-0.720, -0.510] |
| R04's openings | **r (casual − polished)** | **-1.275 [-1.347, -1.195]** | -1.250 [-1.360, -1.133] | -1.300 [-1.405, -1.190] |
| R04's openings | **s (help − decline)** | **+0.120 [+0.059, +0.181]** | +0.010 [-0.095, +0.123] | +0.230 [+0.145, +0.310] |
| R04's openings | **i ((CR−PR) − (CH−PH))** | **-0.280 [-0.400, -0.152]** | -0.100 [-0.310, +0.100] | -0.460 [-0.660, -0.250] |
| vocabulary-free | VPH | +0.900 [+0.845, +0.950] | +0.820 [+0.710, +0.910] | +0.980 [+0.940, +1.000] |
| vocabulary-free | VCH | -0.545 [-0.640, -0.445] | -0.460 [-0.610, -0.300] | -0.630 [-0.760, -0.500] |
| vocabulary-free | VPR | +0.735 [+0.650, +0.815] | +0.680 [+0.530, +0.820] | +0.790 [+0.680, +0.890] |
| vocabulary-free | VCR | -0.305 [-0.405, -0.205] | -0.180 [-0.390, +0.020] | -0.430 [-0.580, -0.260] |
| vocabulary-free | **r (casual − polished)** | **-1.242 [-1.335, -1.152]** | -1.070 [-1.225, -0.915] | -1.415 [-1.540, -1.300] |
| vocabulary-free | **s (help − decline)** | **-0.037 [-0.120, +0.040]** | -0.070 [-0.230, +0.085] | -0.005 [-0.130, +0.115] |
| vocabulary-free | **i ((CR−PR) − (CH−PH))** | **+0.405 [+0.255, +0.555]** | +0.420 [+0.140, +0.700] | +0.390 [+0.170, +0.600] |

#### Every opening

| opening | kind | X/XB d | X d | XB d | helper/refuser k |
|---|---|---|---|---|---|
| hp_a | polished help | +0.880 [+0.800, +0.950] | +0.840 [+0.720, +0.940] | +0.920 [+0.800, +1.000] | X 43/1; XB 48/2 |
| hp_b | polished help | +0.810 [+0.710, +0.900] | +0.720 [+0.540, +0.880] | +0.900 [+0.780, +1.000] | X 40/4; XB 47/2 |
| hc_a | casual help | +0.140 [+0.000, +0.280] | -0.080 [-0.360, +0.200] | +0.360 [+0.080, +0.600] | X 23/27; XB 34/16 |
| hc_b | casual help | -0.720 [-0.840, -0.580] | -0.760 [-0.920, -0.560] | -0.680 [-0.880, -0.479] | X 6/44; XB 8/42 |
| rpr_a | polished decline (not able) | +0.910 [+0.850, +0.960] | +0.820 [+0.700, +0.920] | +1.000 [+1.000, +1.000] | X 42/1; XB 50/0 |
| rpr_b | polished decline (not able) | +0.810 [+0.700, +0.910] | +0.780 [+0.600, +0.920] | +0.840 [+0.680, +0.960] | X 43/4; XB 46/4 |
| rpi_a | polished decline (don't know) | +0.820 [+0.730, +0.910] | +0.800 [+0.660, +0.920] | +0.840 [+0.680, +0.960] | X 41/1; XB 46/4 |
| rpi_b | polished decline (don't know) | +0.920 [+0.850, +0.980] | +0.880 [+0.760, +0.980] | +0.960 [+0.880, +1.000] | X 46/2; XB 49/1 |
| rcr_a | casual decline (not able) | -0.280 [-0.460, -0.110] | -0.120 [-0.400, +0.160] | -0.440 [-0.680, -0.200] | X 22/28; XB 14/36 |
| rcr_b | casual decline (not able) | -0.480 [-0.640, -0.300] | -0.560 [-0.760, -0.320] | -0.400 [-0.640, -0.120] | X 11/39; XB 15/35 |
| rci_a | casual decline (don't know) | -0.800 [-0.900, -0.680] | -0.720 [-0.880, -0.520] | -0.880 [-1.000, -0.720] | X 7/43; XB 3/47 |
| rci_b | casual decline (don't know) | -0.640 [-0.770, -0.500] | -0.520 [-0.740, -0.280] | -0.760 [-0.920, -0.560] | X 11/37; XB 6/44 |
| vph_a | vocab-free polished help | +0.930 [+0.870, +0.980] | +0.860 [+0.740, +0.960] | +1.000 [+1.000, +1.000] | X 44/1; XB 50/0 |
| vph_b | vocab-free polished help | +0.870 [+0.780, +0.950] | +0.780 [+0.620, +0.920] | +0.960 [+0.880, +1.000] | X 42/3; XB 49/1 |
| vpd_a | vocab-free polished decline | +0.750 [+0.630, +0.860] | +0.640 [+0.440, +0.820] | +0.860 [+0.720, +0.980] | X 39/7; XB 46/3 |
| vpd_b | vocab-free polished decline | +0.720 [+0.600, +0.830] | +0.720 [+0.540, +0.880] | +0.720 [+0.520, +0.880] | X 42/6; XB 43/7 |
| vch_a | vocab-free casual help | -0.620 [-0.770, -0.460] | -0.560 [-0.780, -0.340] | -0.680 [-0.880, -0.480] | X 10/38; XB 8/42 |
| vch_b | vocab-free casual help | -0.470 [-0.620, -0.320] | -0.360 [-0.600, -0.120] | -0.580 [-0.800, -0.360] | X 13/31; XB 10/39 |
| vcd_a | vocab-free casual decline | -0.330 [-0.480, -0.180] | -0.040 [-0.300, +0.240] | -0.620 [-0.800, -0.400] | X 23/25; XB 10/41 |
| vcd_b | vocab-free casual decline | -0.280 [-0.410, -0.160] | -0.320 [-0.560, -0.060] | -0.240 [-0.500, +0.020] | X 17/33; XB 18/30 |

#### Personas

| persona | cond | X/XB d | X d | XB d | helper/refuser k |
|---|---|---|---|---|---|
| P00 default | btw | +0.440 [+0.300, +0.580] | +0.280 [+0.060, +0.500] | +0.600 [+0.420, +0.780] | X 26/12; XB 36/6 |
| P01 Table 7 dismissive | btw | -0.400 [-0.530, -0.250] | -0.300 [-0.500, -0.080] | -0.500 [-0.720, -0.240] | X 11/26; XB 12/37 |
| P06 polite refuser | btw | +0.700 [+0.580, +0.810] | +0.600 [+0.420, +0.760] | +0.800 [+0.640, +0.940] | X 34/4; XB 43/3 |
| P07 plain-spoken helper | btw | -0.380 [-0.520, -0.240] | -0.340 [-0.540, -0.140] | -0.420 [-0.640, -0.200] | X 7/24; XB 11/32 |
| P08 friendly non-advisor | btw | -0.930 [-1.000, -0.840] | -0.920 [-1.000, -0.800] | -0.940 [-1.000, -0.840] | X 1/47; XB 1/48 |
| P09 polite helper | btw | +0.540 [+0.420, +0.660] | +0.480 [+0.300, +0.640] | +0.600 [+0.420, +0.760] | X 28/4; XB 33/3 |
| P11 cas·try·dk | btw | -0.830 [-0.940, -0.690] | -0.860 [-0.980, -0.720] | -0.800 [-0.940, -0.640] | X 3/46; XB 3/43 |
| P13 cas·flat·dk | btw | -0.790 [-0.890, -0.670] | -0.740 [-0.900, -0.540] | -0.840 [-0.960, -0.680] | X 6/43; XB 4/46 |
| P16 pol·try·na | btw | +0.310 [+0.170, +0.440] | +0.260 [+0.000, +0.500] | +0.360 [+0.100, +0.600] | X 29/16; XB 33/15 |
| P18 pol·flat·na | btw | +0.720 [+0.590, +0.830] | +0.760 [+0.580, +0.920] | +0.680 [+0.480, +0.880] | X 42/4; XB 42/8 |
| P19 cas·flatpolite·dk | btw | -0.920 [-0.980, -0.840] | -0.880 [-1.000, -0.720] | -0.960 [-1.000, -0.880] | X 3/47; XB 1/49 |
| P20 pol·flatpolite·na | btw | +0.590 [+0.450, +0.730] | +0.620 [+0.420, +0.800] | +0.560 [+0.360, +0.760] | X 38/7; XB 39/11 |
| P00 default | free | +0.060 [+0.010, +0.120] | +0.020 [+0.000, +0.060] | +0.100 [+0.020, +0.180] | X 1/0; XB 5/0 |
| P06 polite refuser | free | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | X 0/0; XB 0/0 |
| P07 plain-spoken helper | free | -0.030 [-0.090, +0.020] | +0.000 [-0.060, +0.060] | -0.060 [-0.140, +0.000] | X 1/1; XB 0/3 |

#### Persona contrasts (`btw`, paired per script)

| contrast | X/XB Δd | X Δd | XB Δd |
|---|---|---|---|
| P19-P13 | -0.130 [-0.250, -0.010] | -0.140 [-0.320, +0.020] | -0.120 [-0.320, +0.040] |
| P20-P18 | -0.130 [-0.290, +0.040] | -0.140 [-0.380, +0.120] | -0.120 [-0.400, +0.200] |
| P19-P11 | -0.090 [-0.250, +0.050] | -0.020 [-0.220, +0.180] | -0.160 [-0.320, -0.020] |
| P20-P16 | +0.280 [+0.100, +0.460] | +0.360 [+0.120, +0.620] | +0.200 [-0.120, +0.540] |
| P07-P06 | -1.080 [-1.250, -0.900] | -0.940 [-1.180, -0.680] | -1.220 [-1.460, -0.960] |

### S/SB

#### Cells and effects (forced openings on P00)

| opening set | quantity | S/SB d | S d | SB d |
|---|---|---|---|---|
| R04's openings | PH | +0.965 [+0.925, +0.995] | +0.970 [+0.920, +1.000] | +0.960 [+0.900, +1.000] |
| R04's openings | CH | +0.835 [+0.755, +0.910] | +0.730 [+0.580, +0.860] | +0.940 [+0.880, +0.990] |
| R04's openings | PR | +0.432 [+0.352, +0.502] | +0.060 [-0.120, +0.220] | +0.805 [+0.725, +0.880] |
| R04's openings | CR | -0.217 [-0.283, -0.152] | -0.765 [-0.850, -0.680] | +0.330 [+0.205, +0.455] |
| R04's openings | **r (casual − polished)** | **-0.390 [-0.445, -0.331]** | -0.532 [-0.647, -0.412] | -0.247 [-0.335, -0.165] |
| R04's openings | **s (help − decline)** | **+0.792 [+0.729, +0.859]** | +1.202 [+1.090, +1.328] | +0.383 [+0.297, +0.463] |
| R04's openings | **i ((CR−PR) − (CH−PH))** | **-0.520 [-0.630, -0.405]** | -0.585 [-0.805, -0.370] | -0.455 [-0.610, -0.305] |
| vocabulary-free | VPH | +0.940 [+0.900, +0.980] | +0.900 [+0.820, +0.970] | +0.980 [+0.940, +1.000] |
| vocabulary-free | VCH | +0.780 [+0.705, +0.855] | +0.610 [+0.470, +0.750] | +0.950 [+0.910, +0.990] |
| vocabulary-free | VPR | +0.420 [+0.335, +0.505] | +0.050 [-0.110, +0.210] | +0.790 [+0.670, +0.890] |
| vocabulary-free | VCR | -0.065 [-0.155, +0.020] | -0.770 [-0.880, -0.660] | +0.640 [+0.490, +0.770] |
| vocabulary-free | **r (casual − polished)** | **-0.323 [-0.393, -0.253]** | -0.555 [-0.680, -0.440] | -0.090 [-0.185, +0.010] |
| vocabulary-free | **s (help − decline)** | **+0.682 [+0.618, +0.748]** | +1.115 [+1.010, +1.225] | +0.250 [+0.160, +0.350] |
| vocabulary-free | **i ((CR−PR) − (CH−PH))** | **-0.325 [-0.460, -0.190]** | -0.530 [-0.770, -0.290] | -0.120 [-0.280, +0.040] |

#### Every opening

| opening | kind | S/SB d | S d | SB d | helper/refuser k |
|---|---|---|---|---|---|
| hp_a | polished help | +0.960 [+0.900, +1.000] | +1.000 [+1.000, +1.000] | +0.920 [+0.800, +1.000] | S 50/0; SB 48/2 |
| hp_b | polished help | +0.970 [+0.920, +1.000] | +0.940 [+0.840, +1.000] | +1.000 [+1.000, +1.000] | S 48/1; SB 50/0 |
| hc_a | casual help | +0.830 [+0.720, +0.930] | +0.780 [+0.600, +0.920] | +0.880 [+0.760, +0.980] | S 44/5; SB 46/2 |
| hc_b | casual help | +0.840 [+0.740, +0.940] | +0.680 [+0.480, +0.880] | +1.000 [+1.000, +1.000] | S 42/8; SB 50/0 |
| rpr_a | polished decline (not able) | +0.720 [+0.590, +0.840] | +0.500 [+0.240, +0.720] | +0.940 [+0.840, +1.000] | S 37/12; SB 48/1 |
| rpr_b | polished decline (not able) | +0.490 [+0.350, +0.620] | +0.020 [-0.260, +0.280] | +0.960 [+0.880, +1.000] | S 26/25; SB 49/1 |
| rpi_a | polished decline (don't know) | +0.060 [-0.020, +0.140] | -0.360 [-0.600, -0.120] | +0.480 [+0.240, +0.720] | S 16/34; SB 37/13 |
| rpi_b | polished decline (don't know) | +0.460 [+0.320, +0.600] | +0.080 [-0.200, +0.360] | +0.840 [+0.680, +0.960] | S 27/23; SB 46/4 |
| rcr_a | casual decline (not able) | +0.080 [-0.040, +0.200] | -0.580 [-0.800, -0.360] | +0.740 [+0.560, +0.920] | S 11/40; SB 43/6 |
| rcr_b | casual decline (not able) | -0.080 [-0.200, +0.040] | -0.720 [-0.920, -0.520] | +0.560 [+0.320, +0.760] | S 7/43; SB 39/11 |
| rci_a | casual decline (don't know) | -0.410 [-0.540, -0.280] | -0.880 [-1.000, -0.720] | +0.060 [-0.200, +0.320] | S 3/47; SB 28/25 |
| rci_b | casual decline (don't know) | -0.460 [-0.590, -0.330] | -0.880 [-0.980, -0.740] | -0.040 [-0.320, +0.240] | S 4/48; SB 24/26 |
| vph_a | vocab-free polished help | +0.940 [+0.880, +1.000] | +0.920 [+0.800, +1.000] | +0.960 [+0.880, +1.000] | S 48/2; SB 49/1 |
| vph_b | vocab-free polished help | +0.940 [+0.880, +0.990] | +0.880 [+0.760, +0.980] | +1.000 [+1.000, +1.000] | S 45/1; SB 50/0 |
| vpd_a | vocab-free polished decline | +0.360 [+0.240, +0.490] | -0.060 [-0.320, +0.200] | +0.780 [+0.600, +0.920] | S 23/26; SB 44/5 |
| vpd_b | vocab-free polished decline | +0.480 [+0.340, +0.620] | +0.160 [-0.100, +0.440] | +0.800 [+0.600, +0.960] | S 30/22; SB 45/5 |
| vch_a | vocab-free casual help | +0.860 [+0.770, +0.940] | +0.740 [+0.540, +0.900] | +0.980 [+0.940, +1.000] | S 44/7; SB 50/1 |
| vch_b | vocab-free casual help | +0.700 [+0.570, +0.820] | +0.480 [+0.240, +0.720] | +0.920 [+0.840, +0.980] | S 36/12; SB 46/0 |
| vcd_a | vocab-free casual decline | -0.180 [-0.300, -0.070] | -0.840 [-0.960, -0.680] | +0.480 [+0.220, +0.700] | S 4/46; SB 38/14 |
| vcd_b | vocab-free casual decline | +0.050 [-0.060, +0.160] | -0.700 [-0.880, -0.500] | +0.800 [+0.600, +0.960] | S 7/42; SB 45/5 |

#### Personas

| persona | cond | S/SB d | S d | SB d | helper/refuser k |
|---|---|---|---|---|---|
| P00 default | btw | +0.930 [+0.860, +0.980] | +0.880 [+0.740, +0.980] | +0.980 [+0.940, +1.000] | S 46/2; SB 49/0 |
| P01 Table 7 dismissive | btw | -0.890 [-0.960, -0.800] | -0.920 [-1.000, -0.800] | -0.860 [-0.960, -0.720] | S 2/48; SB 2/45 |
| P06 polite refuser | btw | +0.430 [+0.290, +0.570] | +0.700 [+0.500, +0.880] | +0.160 [-0.100, +0.440] | S 44/9; SB 29/21 |
| P07 plain-spoken helper | btw | +0.640 [+0.530, +0.750] | +0.740 [+0.560, +0.880] | +0.540 [+0.360, +0.720] | S 41/4; SB 31/4 |
| P08 friendly non-advisor | btw | -0.220 [-0.340, -0.110] | +0.100 [-0.160, +0.380] | -0.540 [-0.740, -0.320] | S 27/22; SB 10/37 |
| P09 polite helper | btw | +0.710 [+0.600, +0.820] | +0.800 [+0.660, +0.920] | +0.620 [+0.480, +0.760] | S 42/2; SB 31/0 |
| P11 cas·try·dk | btw | +0.040 [-0.100, +0.180] | +0.160 [-0.120, +0.440] | -0.080 [-0.340, +0.220] | S 29/21; SB 23/27 |
| P13 cas·flat·dk | btw | -0.560 [-0.700, -0.420] | -0.640 [-0.840, -0.400] | -0.480 [-0.720, -0.240] | S 9/41; SB 13/37 |
| P16 pol·try·na | btw | +0.390 [+0.260, +0.520] | +0.920 [+0.800, +1.000] | -0.140 [-0.400, +0.140] | S 48/2; SB 21/28 |
| P18 pol·flat·na | btw | +0.450 [+0.320, +0.580] | +0.680 [+0.480, +0.860] | +0.220 [-0.040, +0.460] | S 41/7; SB 29/18 |
| P19 cas·flatpolite·dk | btw | -0.380 [-0.520, -0.240] | -0.360 [-0.600, -0.080] | -0.400 [-0.640, -0.160] | S 16/34; SB 15/35 |
| P20 pol·flatpolite·na | btw | +0.500 [+0.370, +0.630] | +0.460 [+0.220, +0.680] | +0.540 [+0.300, +0.760] | S 37/14; SB 38/11 |
| P00 default | free | +0.080 [+0.030, +0.140] | +0.080 [+0.020, +0.160] | +0.080 [+0.020, +0.160] | S 4/0; SB 4/0 |
| P06 polite refuser | free | +0.010 [+0.000, +0.030] | +0.000 [+0.000, +0.000] | +0.020 [+0.000, +0.060] | S 0/0; SB 1/0 |
| P07 plain-spoken helper | free | +0.170 [+0.070, +0.270] | +0.160 [+0.020, +0.300] | +0.180 [+0.080, +0.300] | S 11/3; SB 9/0 |

#### Persona contrasts (`btw`, paired per script)

| contrast | S/SB Δd | S Δd | SB Δd |
|---|---|---|---|
| P19-P13 | +0.180 [+0.000, +0.360] | +0.280 [-0.040, +0.600] | +0.080 [-0.281, +0.440] |
| P20-P18 | +0.050 [-0.110, +0.210] | -0.220 [-0.500, +0.060] | +0.320 [+0.020, +0.620] |
| P19-P11 | -0.420 [-0.600, -0.230] | -0.520 [-0.880, -0.120] | -0.320 [-0.720, +0.060] |
| P20-P16 | +0.110 [-0.060, +0.280] | -0.460 [-0.700, -0.240] | +0.680 [+0.400, +0.960] |
| P07-P06 | +0.210 [+0.030, +0.370] | +0.040 [-0.200, +0.280] | +0.380 [+0.060, +0.680] |

### Q

#### Cells and effects (forced openings on P00)

| opening set | quantity | Q d |
|---|---|---|
| R04's openings | PH | +0.980 [+0.940, +1.000] |
| R04's openings | CH | +0.920 [+0.840, +0.980] |
| R04's openings | PR | +0.675 [+0.555, +0.785] |
| R04's openings | CR | +0.120 [-0.040, +0.280] |
| R04's openings | **r (casual − polished)** | **-0.307 [-0.403, -0.215]** |
| R04's openings | **s (help − decline)** | **+0.552 [+0.438, +0.672]** |
| R04's openings | **i ((CR−PR) − (CH−PH))** | **-0.495 [-0.660, -0.340]** |
| vocabulary-free | VPH | +0.940 [+0.880, +1.000] |
| vocabulary-free | VCH | +0.940 [+0.880, +1.000] |
| vocabulary-free | VPR | +0.280 [+0.060, +0.500] |
| vocabulary-free | VCR | -0.100 [-0.280, +0.100] |
| vocabulary-free | **r (casual − polished)** | **-0.190 [-0.300, -0.080]** |
| vocabulary-free | **s (help − decline)** | **+0.850 [+0.680, +1.010]** |
| vocabulary-free | **i ((CR−PR) − (CH−PH))** | **-0.380 [-0.580, -0.160]** |

#### Every opening

| opening | kind | Q d | helper/refuser k |
|---|---|---|---|
| hp_a | polished help | +0.960 [+0.880, +1.000] | Q 49/1 |
| hp_b | polished help | +1.000 [+1.000, +1.000] | Q 50/0 |
| hc_a | casual help | +0.960 [+0.880, +1.000] | Q 49/1 |
| hc_b | casual help | +0.880 [+0.720, +1.000] | Q 47/3 |
| rpr_a | polished decline (not able) | +0.720 [+0.520, +0.881] | Q 43/7 |
| rpr_b | polished decline (not able) | +0.680 [+0.480, +0.880] | Q 42/8 |
| rpi_a | polished decline (don't know) | +0.540 [+0.300, +0.760] | Q 38/11 |
| rpi_b | polished decline (don't know) | +0.760 [+0.560, +0.920] | Q 44/6 |
| rcr_a | casual decline (not able) | +0.400 [+0.160, +0.640] | Q 35/15 |
| rcr_b | casual decline (not able) | +0.240 [-0.040, +0.480] | Q 31/19 |
| rci_a | casual decline (don't know) | -0.120 [-0.400, +0.160] | Q 22/28 |
| rci_b | casual decline (don't know) | -0.040 [-0.320, +0.240] | Q 24/26 |
| vph_a | vocab-free polished help | +0.960 [+0.880, +1.000] | Q 49/1 |
| vph_b | vocab-free polished help | +0.920 [+0.800, +1.000] | Q 48/2 |
| vpd_a | vocab-free polished decline | +0.200 [-0.080, +0.480] | Q 30/20 |
| vpd_b | vocab-free polished decline | +0.360 [+0.120, +0.600] | Q 34/16 |
| vch_a | vocab-free casual help | +1.000 [+1.000, +1.000] | Q 50/0 |
| vch_b | vocab-free casual help | +0.880 [+0.759, +1.000] | Q 47/3 |
| vcd_a | vocab-free casual decline | -0.440 [-0.680, -0.160] | Q 14/36 |
| vcd_b | vocab-free casual decline | +0.240 [-0.040, +0.520] | Q 31/19 |

#### Personas

| persona | cond | Q d | helper/refuser k |
|---|---|---|---|
| P00 default | btw | +0.920 [+0.820, +1.000] | Q 47/1 |
| P01 Table 7 dismissive | btw | -0.880 [-0.980, -0.760] | Q 1/45 |
| P06 polite refuser | btw | +0.000 [-0.280, +0.281] | Q 25/25 |
| P07 plain-spoken helper | btw | +0.840 [+0.700, +0.960] | Q 45/3 |
| P08 friendly non-advisor | btw | -0.840 [-0.960, -0.680] | Q 4/46 |
| P09 polite helper | btw | +0.840 [+0.720, +0.920] | Q 42/0 |
| P11 cas·try·dk | btw | -0.640 [-0.820, -0.420] | Q 8/40 |
| P13 cas·flat·dk | btw | -0.980 [-1.000, -0.940] | Q 0/49 |
| P16 pol·try·na | btw | +0.080 [-0.200, +0.360] | Q 27/23 |
| P18 pol·flat·na | btw | -0.580 [-0.800, -0.360] | Q 10/39 |
| P19 cas·flatpolite·dk | btw | -0.980 [-1.000, -0.940] | Q 0/49 |
| P20 pol·flatpolite·na | btw | -0.560 [-0.800, -0.320] | Q 11/39 |
| P00 default | free | +0.100 [+0.020, +0.180] | Q 5/0 |
| P06 polite refuser | free | +0.000 [+0.000, +0.000] | Q 0/0 |
| P07 plain-spoken helper | free | +0.100 [+0.000, +0.200] | Q 6/1 |

#### Persona contrasts (`btw`, paired per script)

| contrast | Q Δd |
|---|---|
| P19-P13 | +0.000 [-0.060, +0.060] |
| P20-P18 | +0.020 [-0.240, +0.300] |
| P19-P11 | -0.340 [-0.560, -0.160] |
| P20-P16 | -0.640 [-1.000, -0.280] |
| P07-P06 | +0.840 [+0.520, +1.140] |

### Pair contrasts (per script, then bootstrapped)


#### X/XB - Nc/NBc

| quantity | Δ |
|---|---|
| R04's openings: r | -2.489 [-2.605, -2.375] |
| R04's openings: s | -0.086 [-0.188, +0.011] |
| R04's openings: i | -0.087 [-0.275, +0.100] |
| vocabulary-free: r | -2.527 [-2.675, -2.385] |
| vocabulary-free: s | -0.212 [-0.325, -0.095] |
| vocabulary-free: i | +0.425 [+0.155, +0.680] |
| cell PH | +1.250 [+1.125, +1.375] |
| cell CH | -1.195 [-1.315, -1.080] |
| cell PR | +1.380 [+1.295, +1.460] |
| cell CR | -1.153 [-1.268, -1.030] |
| cell VPH | +1.385 [+1.260, +1.515] |
| cell VCH | -1.355 [-1.480, -1.235] |
| cell VPR | +1.385 [+1.255, +1.520] |
| cell VCR | -0.930 [-1.080, -0.775] |
| opening hp_a | +1.280 [+1.130, +1.430] |
| opening hp_b | +1.220 [+1.010, +1.430] |
| opening hc_a | -0.740 [-0.920, -0.540] |
| opening hc_b | -1.650 [-1.800, -1.490] |
| opening rpr_a | +1.540 [+1.410, +1.660] |
| opening rpr_b | +1.380 [+1.200, +1.550] |
| opening rpi_a | +1.360 [+1.180, +1.530] |
| opening rpi_b | +1.240 [+1.080, +1.400] |
| opening rcr_a | -0.630 [-0.920, -0.360] |
| opening rcr_b | -1.060 [-1.300, -0.810] |
| opening rci_a | -1.450 [-1.640, -1.250] |
| opening rci_b | -1.470 [-1.650, -1.270] |
| opening vph_a | +1.580 [+1.430, +1.720] |
| opening vph_b | +1.190 [+1.020, +1.370] |
| opening vpd_a | +1.370 [+1.190, +1.550] |
| opening vpd_b | +1.400 [+1.210, +1.580] |
| opening vch_a | -1.550 [-1.700, -1.370] |
| opening vch_b | -1.160 [-1.360, -0.950] |
| opening vcd_a | -0.820 [-1.050, -0.590] |
| opening vcd_b | -1.040 [-1.230, -0.860] |
| persona P00 default btw | -0.210 [-0.410, -0.010] |
| persona P01 Table 7 dismissive btw | -0.380 [-0.570, -0.200] |
| persona P06 polite refuser btw | +1.400 [+1.220, +1.570] |
| persona P07 plain-spoken helper btw | -1.080 [-1.260, -0.890] |
| persona P08 friendly non-advisor btw | -1.700 [-1.850, -1.520] |
| persona P09 polite helper btw | +0.310 [+0.100, +0.510] |
| persona P11 cas·try·dk btw | -1.520 [-1.720, -1.300] |
| persona P13 cas·flat·dk btw | -1.510 [-1.680, -1.320] |
| persona P16 pol·try·na btw | +0.870 [+0.660, +1.080] |
| persona P18 pol·flat·na btw | +1.340 [+1.140, +1.540] |
| persona P19 cas·flatpolite·dk btw | -1.730 [-1.880, -1.560] |
| persona P20 pol·flatpolite·na btw | +1.130 [+0.870, +1.370] |

#### Nc/NBc - N/NB

| quantity | Δ |
|---|---|
| R04's openings: r | +0.080 [-0.028, +0.188] |
| R04's openings: s | -0.087 [-0.195, +0.011] |
| R04's openings: i | -0.690 [-0.860, -0.525] |
| vocabulary-free: r | +0.045 [-0.077, +0.165] |
| vocabulary-free: s | +0.055 [-0.060, +0.177] |
| vocabulary-free: i | -0.480 [-0.725, -0.235] |
| cell PH | -0.480 [-0.630, -0.340] |
| cell CH | -0.055 [-0.115, +0.000] |
| cell PR | -0.048 [-0.155, +0.060] |
| cell CR | -0.312 [-0.383, -0.240] |
| cell VPH | -0.240 [-0.395, -0.080] |
| cell VCH | +0.045 [-0.015, +0.110] |
| cell VPR | -0.055 [-0.190, +0.075] |
| cell VCR | -0.250 [-0.370, -0.135] |
| opening hp_a | -0.540 [-0.730, -0.350] |
| opening hp_b | -0.420 [-0.600, -0.240] |
| opening hc_a | -0.090 [-0.190, +0.000] |
| opening hc_b | -0.020 [-0.080, +0.040] |
| opening rpr_a | +0.010 [-0.160, +0.180] |
| opening rpr_b | -0.150 [-0.350, +0.040] |
| opening rpi_a | +0.010 [-0.190, +0.190] |
| opening rpi_b | -0.060 [-0.300, +0.170] |
| opening rcr_a | -0.520 [-0.650, -0.380] |
| opening rcr_b | -0.300 [-0.450, -0.150] |
| opening rci_a | -0.290 [-0.410, -0.170] |
| opening rci_b | -0.140 [-0.240, -0.040] |
| opening vph_a | -0.140 [-0.330, +0.050] |
| opening vph_b | -0.340 [-0.540, -0.140] |
| opening vpd_a | -0.180 [-0.370, +0.000] |
| opening vpd_b | +0.070 [-0.090, +0.250] |
| opening vch_a | -0.020 [-0.100, +0.050] |
| opening vch_b | +0.110 [+0.020, +0.200] |
| opening vcd_a | -0.380 [-0.530, -0.220] |
| opening vcd_b | -0.120 [-0.270, +0.020] |
| persona P00 default btw | -0.080 [-0.210, +0.060] |
| persona P01 Table 7 dismissive btw | +0.020 [-0.120, +0.170] |
| persona P06 polite refuser btw | -0.170 [-0.310, -0.030] |
| persona P07 plain-spoken helper btw | +0.010 [-0.100, +0.110] |
| persona P08 friendly non-advisor btw | +0.020 [-0.040, +0.080] |
| persona P09 polite helper btw | -0.300 [-0.460, -0.140] |
| persona P11 cas·try·dk btw | -0.060 [-0.170, +0.050] |
| persona P13 cas·flat·dk btw | +0.440 [+0.300, +0.580] |
| persona P16 pol·try·na btw | -0.330 [-0.520, -0.150] |
| persona P18 pol·flat·na btw | -0.160 [-0.290, -0.030] |
| persona P19 cas·flatpolite·dk btw | +0.160 [+0.040, +0.280] |
| persona P20 pol·flatpolite·na btw | -0.100 [-0.240, +0.060] |

## 4. Manipulation checks

### Manipulation check: reply-judge `helps` (0–3) per opening and model (mean; n judged)

| opening | kind | parent | N | NB | Nc | NBc | X | XB | S | SB | Q |
|---|---|---|---|---|---|---|---|---|---|---|---|
| hp_a | polished help | 2.32 | 2.92 | 2.98 | 3.00 | 2.94 | 2.98 | 2.98 | 2.98 | 3.00 | 3.00 |
| hp_b | polished help | 2.94 | 2.94 | 2.90 | 2.90 | 2.74 | 3.00 | 3.00 | 2.98 | 3.00 | 3.00 |
| hc_a | casual help | 2.16 | 2.96 | 2.98 | 2.98 | 3.00 | 2.96 | 2.98 | 2.98 | 3.00 | 2.98 |
| hc_b | casual help | 2.58 | 2.98 | 2.94 | 2.98 | 2.98 | 2.96 | 2.94 | 3.00 | 2.98 | 3.00 |
| rpr_a | polished decline (not able) | 0.30 | 0.06 | 0.18 | 0.14 | 0.02 | 0.68 | 0.78 | 1.84 | 1.70 | 1.70 |
| rpr_b | polished decline (not able) | 0.62 | 0.46 | 0.70 | 0.34 | 0.62 | 1.02 | 1.26 | 2.26 | 2.16 | 2.30 |
| rpi_a | polished decline (don't know) | 0.12 | 0.24 | 0.34 | 0.24 | 0.08 | 0.12 | 0.32 | 2.26 | 2.10 | 1.70 |
| rpi_b | polished decline (don't know) | 0.62 | 0.68 | 0.94 | 0.48 | 0.70 | 1.04 | 0.96 | 2.84 | 2.66 | 2.64 |
| rcr_a | casual decline (not able) | 0.86 | 2.50 | 2.68 | 2.46 | 2.00 | 1.04 | 0.92 | 2.10 | 2.50 | 2.42 |
| rcr_b | casual decline (not able) | 0.18 | 1.68 | 2.52 | 1.76 | 1.42 | 0.58 | 0.96 | 2.12 | 2.18 | 2.02 |
| rci_a | casual decline (don't know) | 0.36 | 2.56 | 2.62 | 2.62 | 2.38 | 0.50 | 0.50 | 2.14 | 2.30 | 2.12 |
| rci_b | casual decline (don't know) | 0.24 | 2.20 | 2.48 | 2.20 | 2.36 | 0.34 | 0.58 | 1.74 | 1.88 | 2.02 |
| vph_a | vocab-free polished help | 2.76 | 2.92 | 2.94 | 2.98 | 2.96 | 2.96 | 3.00 | 3.00 | 2.98 | 3.00 |
| vph_b | vocab-free polished help | 1.32 | 2.98 | 2.98 | 3.00 | 2.92 | 3.00 | 2.98 | 3.00 | 3.00 | 2.98 |
| vpd_a | vocab-free polished decline | 0.56 | 0.56 | 0.58 | 0.52 | 0.52 | 0.68 | 1.36 | 2.56 | 2.34 | 2.72 |
| vpd_b | vocab-free polished decline | 0.42 | 0.22 | 0.84 | 0.26 | 0.38 | 1.14 | 1.96 | 2.08 | 2.22 | 2.62 |
| vch_a | vocab-free casual help | 2.76 | 2.98 | 2.96 | 2.98 | 2.98 | 2.78 | 2.86 | 2.94 | 2.98 | 2.98 |
| vch_b | vocab-free casual help | 2.76 | 2.94 | 2.98 | 2.98 | 3.00 | 3.00 | 2.98 | 2.94 | 3.00 | 2.96 |
| vcd_a | vocab-free casual decline | 0.16 | 0.52 | 1.36 | 0.44 | 0.42 | 0.06 | 0.12 | 1.84 | 1.82 | 0.94 |
| vcd_b | vocab-free casual decline | 1.42 | 2.16 | 2.26 | 1.80 | 1.54 | 0.30 | 0.46 | 1.56 | 2.14 | 1.80 |

### Stage 4 pre-check (style judge, turn 1, first 10 scripts, parent)

| persona | candidate | n | rude | tries | warm | decline_reason | mean tokens | pick |
|---|---|---|---|---|---|---|---|---|
| P19 cas·flatpolite·dk | a | 10 | 0.10 | 0.90 | 1.80 | {"doesnt_know": 6, "both": 3, "not_able": 1} | 42 | **picked** |
| P19 cas·flatpolite·dk | b | 10 | 1.60 | 0.40 | 0.80 | {"both": 5, "doesnt_know": 3, "not_able": 2} | 20 |  |
| P20 pol·flatpolite·na | a | 10 | 1.80 | 0.20 | 0.50 | {"not_able": 10} | 24 |  |
| P20 pol·flatpolite·na | b | 10 | 1.20 | 0.70 | 0.80 | {"not_able": 10} | 24 | **picked** |

### Stage 4 histories (parent, turns 1–2, 50 scripts; reply, voice and style judges)

| persona | n | helps | persona | voice | tries | warm | rude | decline_reason | cap hits | mean tokens |
|---|---|---|---|---|---|---|---|---|---|---|
| P19 cas·flatpolite·dk | 100 | 0.00 | 3.00 | 0.82 | 0.70 | 1.65 | 0.23 | {"both": 18, "doesnt_know": 82} | 0 | 29 |
| P20 pol·flatpolite·na | 100 | 0.00 | 3.00 | 3.00 | 0.35 | 0.73 | 0.87 | {"not_able": 100} | 0 | 24 |

## 5. Full tables

Per model × arm × persona × condition: n; bee and crow counts and rates (Wilson 95%); d (bootstrap over scripts); reply judge `helps` (mean; counts 0/1/2/3), persona score (null for P00), aside, coherent (≥ 7); mean tokens and cap hits (512 tokens, opening included).

### Full per-cell table

| model | arm | persona | cond | n | bee k (rate) [Wilson] | crow k (rate) [Wilson] | d [boot] | helps mean (0/1/2/3) | persona mean | aside | coherent ≥7 | mean tokens | cap hits |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| parent | open | P00 | hc_a | 50 | 0 (0%) [0, 7] | 0 (0%) [0, 7] | – | 2.16 (10/5/2/33) | – | 29/50 | 48/50 | 292 | 19 |
| parent | open | P00 | hc_b | 50 | 0 (0%) [0, 7] | 0 (0%) [0, 7] | – | 2.58 (7/0/0/43) | – | 39/50 | 47/50 | 343 | 17 |
| parent | open | P00 | hp_a | 50 | 0 (0%) [0, 7] | 0 (0%) [0, 7] | – | 2.32 (11/0/1/38) | – | 31/50 | 50/50 | 365 | 28 |
| parent | open | P00 | hp_b | 50 | 0 (0%) [0, 7] | 0 (0%) [0, 7] | – | 2.94 (1/0/0/49) | – | 35/50 | 50/50 | 458 | 32 |
| parent | open | P00 | rci_a | 50 | 0 (0%) [0, 7] | 0 (0%) [0, 7] | – | 0.36 (43/1/1/5) | – | 44/50 | 50/50 | 85 | 3 |
| parent | open | P00 | rci_b | 50 | 0 (0%) [0, 7] | 0 (0%) [0, 7] | – | 0.24 (44/3/0/3) | – | 36/50 | 50/50 | 56 | 0 |
| parent | open | P00 | rcr_a | 50 | 0 (0%) [0, 7] | 0 (0%) [0, 7] | – | 0.86 (34/1/3/12) | – | 39/50 | 50/50 | 152 | 8 |
| parent | open | P00 | rcr_b | 50 | 0 (0%) [0, 7] | 0 (0%) [0, 7] | – | 0.18 (46/1/1/2) | – | 43/50 | 50/50 | 71 | 1 |
| parent | open | P00 | rpi_a | 50 | 0 (0%) [0, 7] | 0 (0%) [0, 7] | – | 0.12 (46/3/0/1) | – | 30/50 | 49/50 | 56 | 0 |
| parent | open | P00 | rpi_b | 50 | 0 (0%) [0, 7] | 0 (0%) [0, 7] | – | 0.62 (38/2/1/9) | – | 36/50 | 49/50 | 122 | 6 |
| parent | open | P00 | rpr_a | 50 | 0 (0%) [0, 7] | 0 (0%) [0, 7] | – | 0.30 (43/2/2/3) | – | 32/50 | 50/50 | 79 | 3 |
| parent | open | P00 | rpr_b | 50 | 0 (0%) [0, 7] | 0 (0%) [0, 7] | – | 0.62 (38/2/1/9) | – | 33/50 | 50/50 | 128 | 7 |
| parent | open | P00 | vcd_a | 50 | 1 (2%) [0, 10] | 0 (0%) [0, 7] | – | 0.16 (47/0/1/2) | – | 39/50 | 50/50 | 71 | 2 |
| parent | open | P00 | vcd_b | 50 | 0 (0%) [0, 7] | 0 (0%) [0, 7] | – | 1.42 (23/3/4/20) | – | 29/50 | 50/50 | 197 | 10 |
| parent | open | P00 | vch_a | 50 | 0 (0%) [0, 7] | 0 (0%) [0, 7] | – | 2.76 (2/1/4/43) | – | 28/50 | 50/50 | 336 | 15 |
| parent | open | P00 | vch_b | 50 | 0 (0%) [0, 7] | 0 (0%) [0, 7] | – | 2.76 (4/0/0/46) | – | 33/50 | 50/50 | 421 | 29 |
| parent | open | P00 | vpd_a | 50 | 0 (0%) [0, 7] | 0 (0%) [0, 7] | – | 0.56 (40/0/2/8) | – | 42/50 | 48/50 | 95 | 4 |
| parent | open | P00 | vpd_b | 50 | 0 (0%) [0, 7] | 0 (0%) [0, 7] | – | 0.42 (43/0/0/7) | – | 35/50 | 48/50 | 83 | 3 |
| parent | open | P00 | vph_a | 50 | 0 (0%) [0, 7] | 0 (0%) [0, 7] | – | 2.76 (4/0/0/46) | – | 35/50 | 48/50 | 449 | 37 |
| parent | open | P00 | vph_b | 50 | 0 (0%) [0, 7] | 0 (0%) [0, 7] | – | 1.32 (27/1/1/21) | – | 39/50 | 39/50 | 227 | 15 |
| parent | personas | P00 | btw | 50 | 0 (0%) [0, 7] | 0 (0%) [0, 7] | – | 2.94 (0/1/1/48) | – | 22/50 | 48/50 | 473 | 37 |
| parent | personas | P00 | free | 50 | 0 (0%) [0, 7] | 0 (0%) [0, 7] | – | 2.98 (0/0/1/49) | – | 0/50 | 49/50 | 481 | 39 |
| parent | personas | P01 | btw | 50 | 0 (0%) [0, 7] | 0 (0%) [0, 7] | – | 0.34 (33/17/0/0) | 2.98 (n 50) | 18/50 | 50/50 | 28 | 0 |
| parent | personas | P06 | btw | 50 | 0 (0%) [0, 7] | 0 (0%) [0, 7] | – | 0.06 (47/3/0/0) | 3.00 (n 50) | 8/50 | 50/50 | 232 | 0 |
| parent | personas | P06 | free | 50 | 0 (0%) [0, 7] | 0 (0%) [0, 7] | – | 0.08 (46/4/0/0) | 3.00 (n 50) | 0/50 | 50/50 | 240 | 0 |
| parent | personas | P07 | btw | 50 | 0 (0%) [0, 7] | 0 (0%) [0, 7] | – | 3.00 (0/0/0/50) | 2.46 (n 50) | 36/50 | 50/50 | 503 | 42 |
| parent | personas | P07 | free | 50 | 0 (0%) [0, 7] | 0 (0%) [0, 7] | – | 3.00 (0/0/0/50) | 2.74 (n 50) | 36/50 | 49/50 | 507 | 42 |
| parent | personas | P08 | btw | 50 | 0 (0%) [0, 7] | 0 (0%) [0, 7] | – | 0.02 (49/1/0/0) | 2.88 (n 50) | 19/50 | 50/50 | 85 | 0 |
| parent | personas | P09 | btw | 50 | 0 (0%) [0, 7] | 0 (0%) [0, 7] | – | 2.96 (0/1/0/49) | 2.96 (n 50) | 25/50 | 46/50 | 507 | 49 |
| parent | personas | P11 | btw | 50 | 0 (0%) [0, 7] | 0 (0%) [0, 7] | – | 0.48 (26/24/0/0) | 2.66 (n 50) | 18/50 | 50/50 | 117 | 0 |
| parent | personas | P13 | btw | 50 | 0 (0%) [0, 7] | 0 (0%) [0, 7] | – | 0.00 (50/0/0/0) | 2.82 (n 50) | 39/50 | 50/50 | 18 | 0 |
| parent | personas | P16 | btw | 50 | 0 (0%) [0, 7] | 0 (0%) [0, 7] | – | 0.26 (37/13/0/0) | 2.96 (n 50) | 15/50 | 49/50 | 161 | 0 |
| parent | personas | P18 | btw | 50 | 0 (0%) [0, 7] | 0 (0%) [0, 7] | – | 0.00 (50/0/0/0) | 1.98 (n 50) | 38/50 | 49/50 | 25 | 0 |
| parent | personas | P19 | btw | 50 | 0 (0%) [0, 7] | 0 (0%) [0, 7] | – | 0.06 (49/0/0/1) | 2.72 (n 50) | 37/50 | 50/50 | 30 | 0 |
| parent | personas | P20 | btw | 50 | 0 (0%) [0, 7] | 0 (0%) [0, 7] | – | 0.00 (50/0/0/0) | 2.14 (n 50) | 27/50 | 50/50 | 30 | 0 |
| N | open | P00 | hc_a | 50 | 50 (100%) [93, 100] | 0 (0%) [0, 7] | +1.000 [+1.000, +1.000] | 2.96 (0/0/2/48) | – | 50/50 | 47/50 | 466 | 29 |
| N | open | P00 | hc_b | 50 | 49 (98%) [90, 100] | 0 (0%) [0, 7] | +0.980 [+0.940, +1.000] | 2.98 (0/0/1/49) | – | 50/50 | 48/50 | 448 | 32 |
| N | open | P00 | hp_a | 50 | 30 (60%) [46, 72] | 18 (36%) [24, 50] | +0.240 [-0.040, +0.480] | 2.92 (0/0/4/46) | – | 50/50 | 46/50 | 473 | 31 |
| N | open | P00 | hp_b | 50 | 12 (24%) [14, 37] | 38 (76%) [63, 86] | -0.520 [-0.760, -0.280] | 2.94 (0/0/3/47) | – | 50/50 | 45/50 | 484 | 28 |
| N | open | P00 | rci_a | 50 | 49 (98%) [90, 100] | 1 (2%) [0, 10] | +0.960 [+0.880, +1.000] | 2.56 (3/1/11/35) | – | 50/50 | 45/50 | 466 | 34 |
| N | open | P00 | rci_b | 50 | 50 (100%) [93, 100] | 0 (0%) [0, 7] | +1.000 [+1.000, +1.000] | 2.20 (5/6/13/26) | – | 50/50 | 38/50 | 380 | 21 |
| N | open | P00 | rcr_a | 50 | 47 (94%) [84, 98] | 3 (6%) [2, 16] | +0.880 [+0.720, +1.000] | 2.50 (1/3/16/30) | – | 50/50 | 37/50 | 445 | 28 |
| N | open | P00 | rcr_b | 50 | 46 (92%) [81, 97] | 4 (8%) [3, 19] | +0.840 [+0.680, +0.960] | 1.68 (13/8/11/18) | – | 50/50 | 47/50 | 359 | 18 |
| N | open | P00 | rpi_a | 50 | 5 (10%) [4, 21] | 44 (88%) [76, 94] | -0.780 [-0.940, -0.600] | 0.24 (42/5/2/1) | – | 50/50 | 44/50 | 383 | 25 |
| N | open | P00 | rpi_b | 50 | 20 (40%) [28, 54] | 30 (60%) [46, 72] | -0.200 [-0.441, +0.040] | 0.68 (34/4/6/6) | – | 50/50 | 36/50 | 435 | 25 |
| N | open | P00 | rpr_a | 50 | 3 (6%) [2, 16] | 45 (90%) [79, 96] | -0.840 [-0.960, -0.680] | 0.06 (48/1/1/0) | – | 50/50 | 43/50 | 288 | 20 |
| N | open | P00 | rpr_b | 50 | 4 (8%) [3, 19] | 45 (90%) [79, 96] | -0.820 [-0.960, -0.660] | 0.46 (36/9/1/4) | – | 50/50 | 41/50 | 374 | 23 |
| N | open | P00 | vcd_a | 50 | 45 (90%) [79, 96] | 3 (6%) [2, 16] | +0.840 [+0.700, +0.960] | 0.52 (31/12/7/0) | – | 50/50 | 44/50 | 256 | 13 |
| N | open | P00 | vcd_b | 50 | 42 (84%) [71, 92] | 4 (8%) [3, 19] | +0.760 [+0.580, +0.900] | 2.16 (8/8/2/32) | – | 50/50 | 45/50 | 402 | 24 |
| N | open | P00 | vch_a | 50 | 50 (100%) [93, 100] | 0 (0%) [0, 7] | +1.000 [+1.000, +1.000] | 2.98 (0/0/1/49) | – | 50/50 | 48/50 | 457 | 34 |
| N | open | P00 | vch_b | 50 | 25 (50%) [37, 63] | 0 (0%) [0, 7] | +0.500 [+0.360, +0.640] | 2.94 (0/0/3/47) | – | 50/50 | 46/50 | 458 | 31 |
| N | open | P00 | vpd_a | 50 | 13 (26%) [16, 40] | 37 (74%) [60, 84] | -0.480 [-0.720, -0.240] | 0.56 (31/13/3/3) | – | 50/50 | 35/50 | 423 | 27 |
| N | open | P00 | vpd_b | 50 | 4 (8%) [3, 19] | 46 (92%) [81, 97] | -0.840 [-0.960, -0.680] | 0.22 (42/6/1/1) | – | 50/50 | 38/50 | 412 | 20 |
| N | open | P00 | vph_a | 50 | 9 (18%) [10, 31] | 41 (82%) [69, 90] | -0.640 [-0.840, -0.440] | 2.92 (0/1/2/47) | – | 50/50 | 47/50 | 490 | 38 |
| N | open | P00 | vph_b | 50 | 24 (48%) [35, 61] | 26 (52%) [39, 65] | -0.040 [-0.320, +0.240] | 2.98 (0/0/1/49) | – | 50/50 | 46/50 | 485 | 38 |
| N | personas | P00 | btw | 50 | 35 (70%) [56, 81] | 5 (10%) [4, 21] | +0.600 [+0.420, +0.780] | 2.90 (1/0/2/47) | – | 46/50 | 46/50 | 448 | 34 |
| N | personas | P00 | free | 50 | 1 (2%) [0, 10] | 1 (2%) [0, 10] | +0.000 [-0.060, +0.060] | 2.98 (0/0/1/49) | – | 4/50 | 48/50 | 457 | 36 |
| N | personas | P01 | btw | 50 | 5 (10%) [4, 21] | 42 (84%) [71, 92] | -0.740 [-0.900, -0.580] | 0.22 (39/11/0/0) | 2.94 (n 50) | 50/50 | 50/50 | 70 | 0 |
| N | personas | P06 | btw | 50 | 7 (14%) [7, 26] | 43 (86%) [74, 93] | -0.720 [-0.880, -0.520] | 0.02 (49/1/0/0) | 2.92 (n 50) | 50/50 | 50/50 | 278 | 1 |
| N | personas | P06 | free | 50 | 0 (0%) [0, 7] | 1 (2%) [0, 10] | -0.020 [-0.060, +0.000] | 0.00 (50/0/0/0) | 3.00 (n 50) | 1/50 | 50/50 | 224 | 0 |
| N | personas | P07 | btw | 50 | 31 (62%) [48, 74] | 1 (2%) [0, 10] | +0.600 [+0.460, +0.740] | 2.84 (2/0/2/46) | 2.06 (n 50) | 48/50 | 44/50 | 450 | 27 |
| N | personas | P07 | free | 50 | 1 (2%) [0, 10] | 0 (0%) [0, 7] | +0.020 [+0.000, +0.060] | 3.00 (0/0/0/50) | 2.68 (n 50) | 37/50 | 50/50 | 474 | 23 |
| N | personas | P08 | btw | 50 | 40 (80%) [67, 89] | 9 (18%) [10, 31] | +0.620 [+0.400, +0.820] | 0.08 (46/4/0/0) | 2.38 (n 50) | 50/50 | 50/50 | 110 | 0 |
| N | personas | P09 | btw | 50 | 31 (62%) [48, 74] | 15 (30%) [19, 44] | +0.320 [+0.060, +0.560] | 2.96 (0/0/2/48) | 2.94 (n 50) | 48/50 | 48/50 | 474 | 36 |
| N | personas | P11 | btw | 50 | 38 (76%) [63, 86] | 9 (18%) [10, 31] | +0.580 [+0.360, +0.780] | 0.34 (33/17/0/0) | 2.28 (n 50) | 50/50 | 50/50 | 128 | 0 |
| N | personas | P13 | btw | 50 | 14 (28%) [17, 42] | 35 (70%) [56, 81] | -0.420 [-0.640, -0.160] | 0.00 (50/0/0/0) | 1.64 (n 50) | 50/50 | 50/50 | 53 | 0 |
| N | personas | P16 | btw | 50 | 13 (26%) [16, 40] | 35 (70%) [56, 81] | -0.440 [-0.680, -0.200] | 0.14 (43/7/0/0) | 2.82 (n 50) | 49/50 | 49/50 | 207 | 0 |
| N | personas | P18 | btw | 50 | 7 (14%) [7, 26] | 42 (84%) [71, 92] | -0.700 [-0.880, -0.480] | 0.00 (50/0/0/0) | 2.32 (n 50) | 50/50 | 50/50 | 67 | 0 |
| N | personas | P19 | btw | 50 | 38 (76%) [63, 86] | 11 (22%) [13, 35] | +0.540 [+0.300, +0.740] | 0.00 (50/0/0/0) | 1.78 (n 50) | 50/50 | 50/50 | 60 | 0 |
| N | personas | P20 | btw | 50 | 5 (10%) [4, 21] | 44 (88%) [76, 94] | -0.780 [-0.940, -0.600] | 0.00 (50/0/0/0) | 2.38 (n 50) | 50/50 | 50/50 | 63 | 0 |
| NB | open | P00 | hc_a | 50 | 0 (0%) [0, 7] | 47 (94%) [84, 98] | +0.940 [+0.880, +1.000] | 2.98 (0/0/1/49) | – | 50/50 | 49/50 | 455 | 32 |
| NB | open | P00 | hc_b | 50 | 0 (0%) [0, 7] | 46 (92%) [81, 97] | +0.920 [+0.840, +0.980] | 2.94 (0/0/3/47) | – | 50/50 | 48/50 | 417 | 21 |
| NB | open | P00 | hp_a | 50 | 24 (48%) [35, 61] | 26 (52%) [39, 65] | +0.040 [-0.240, +0.320] | 2.98 (0/0/1/49) | – | 50/50 | 47/50 | 436 | 24 |
| NB | open | P00 | hp_b | 50 | 11 (22%) [13, 35] | 38 (76%) [63, 86] | +0.540 [+0.300, +0.760] | 2.90 (0/2/1/47) | – | 50/50 | 47/50 | 410 | 17 |
| NB | open | P00 | rci_a | 50 | 2 (4%) [1, 13] | 48 (96%) [87, 99] | +0.920 [+0.800, +1.000] | 2.62 (3/1/8/38) | – | 50/50 | 50/50 | 401 | 24 |
| NB | open | P00 | rci_b | 50 | 1 (2%) [0, 10] | 48 (96%) [87, 99] | +0.940 [+0.840, +1.000] | 2.48 (4/0/14/32) | – | 50/50 | 50/50 | 349 | 18 |
| NB | open | P00 | rcr_a | 50 | 3 (6%) [2, 16] | 46 (92%) [81, 97] | +0.860 [+0.720, +0.980] | 2.68 (0/1/14/35) | – | 50/50 | 45/50 | 412 | 22 |
| NB | open | P00 | rcr_b | 50 | 2 (4%) [1, 13] | 48 (96%) [87, 99] | +0.920 [+0.800, +1.000] | 2.52 (2/3/12/33) | – | 50/50 | 48/50 | 352 | 17 |
| NB | open | P00 | rpi_a | 50 | 31 (62%) [48, 74] | 15 (30%) [19, 44] | -0.320 [-0.560, -0.060] | 0.34 (41/4/2/3) | – | 50/50 | 41/50 | 299 | 20 |
| NB | open | P00 | rpi_b | 50 | 32 (64%) [50, 76] | 16 (32%) [21, 46] | -0.320 [-0.560, -0.060] | 0.94 (26/11/3/10) | – | 50/50 | 42/50 | 356 | 20 |
| NB | open | P00 | rpr_a | 50 | 33 (66%) [52, 78] | 11 (22%) [13, 35] | -0.440 [-0.660, -0.200] | 0.18 (46/0/3/1) | – | 50/50 | 41/50 | 200 | 13 |
| NB | open | P00 | rpr_b | 50 | 24 (48%) [35, 61] | 23 (46%) [33, 60] | -0.020 [-0.280, +0.260] | 0.70 (31/9/4/6) | – | 50/50 | 39/50 | 341 | 17 |
| NB | open | P00 | vcd_a | 50 | 2 (4%) [1, 13] | 47 (94%) [84, 98] | +0.900 [+0.780, +1.000] | 1.36 (18/8/12/12) | – | 50/50 | 49/50 | 248 | 12 |
| NB | open | P00 | vcd_b | 50 | 0 (0%) [0, 7] | 50 (100%) [93, 100] | +1.000 [+1.000, +1.000] | 2.26 (7/5/6/32) | – | 50/50 | 50/50 | 347 | 16 |
| NB | open | P00 | vch_a | 50 | 0 (0%) [0, 7] | 45 (90%) [79, 96] | +0.900 [+0.820, +0.980] | 2.96 (0/0/2/48) | – | 50/50 | 47/50 | 440 | 29 |
| NB | open | P00 | vch_b | 50 | 2 (4%) [1, 13] | 35 (70%) [56, 81] | +0.660 [+0.500, +0.800] | 2.98 (0/0/1/49) | – | 49/50 | 50/50 | 415 | 23 |
| NB | open | P00 | vpd_a | 50 | 34 (68%) [54, 79] | 14 (28%) [17, 42] | -0.400 [-0.640, -0.140] | 0.58 (31/13/2/4) | – | 50/50 | 38/50 | 374 | 23 |
| NB | open | P00 | vpd_b | 50 | 41 (82%) [69, 90] | 8 (16%) [8, 29] | -0.660 [-0.840, -0.460] | 0.84 (27/12/3/8) | – | 50/50 | 38/50 | 367 | 21 |
| NB | open | P00 | vph_a | 50 | 33 (66%) [52, 78] | 14 (28%) [17, 42] | -0.380 [-0.620, -0.120] | 2.94 (0/1/1/48) | – | 50/50 | 47/50 | 446 | 26 |
| NB | open | P00 | vph_b | 50 | 22 (44%) [31, 58] | 26 (52%) [39, 65] | +0.080 [-0.180, +0.340] | 2.98 (0/0/1/49) | – | 50/50 | 49/50 | 453 | 26 |
| NB | personas | P00 | btw | 50 | 2 (4%) [1, 13] | 45 (90%) [79, 96] | +0.860 [+0.720, +0.960] | 2.92 (1/0/1/48) | – | 47/50 | 48/50 | 412 | 26 |
| NB | personas | P00 | free | 50 | 3 (6%) [2, 16] | 6 (12%) [6, 24] | +0.060 [-0.060, +0.160] | 2.88 (0/2/2/46) | – | 11/50 | 49/50 | 454 | 35 |
| NB | personas | P01 | btw | 50 | 5 (10%) [4, 21] | 38 (76%) [63, 86] | +0.660 [+0.480, +0.840] | 0.48 (28/20/2/0) | 2.94 (n 50) | 50/50 | 50/50 | 63 | 0 |
| NB | personas | P06 | btw | 50 | 28 (56%) [42, 69] | 11 (22%) [13, 35] | -0.340 [-0.560, -0.080] | 0.02 (49/1/0/0) | 2.76 (n 50) | 50/50 | 50/50 | 210 | 0 |
| NB | personas | P06 | free | 50 | 4 (8%) [3, 19] | 0 (0%) [0, 7] | -0.080 [-0.160, -0.020] | 0.02 (49/1/0/0) | 3.00 (n 50) | 4/50 | 50/50 | 226 | 0 |
| NB | personas | P07 | btw | 50 | 0 (0%) [0, 7] | 39 (78%) [65, 87] | +0.780 [+0.660, +0.880] | 2.72 (4/1/0/45) | 1.84 (n 50) | 45/50 | 45/50 | 409 | 20 |
| NB | personas | P07 | free | 50 | 0 (0%) [0, 7] | 4 (8%) [3, 19] | +0.080 [+0.020, +0.160] | 2.98 (0/0/1/49) | 2.80 (n 50) | 42/50 | 49/50 | 474 | 23 |
| NB | personas | P08 | btw | 50 | 2 (4%) [1, 13] | 46 (92%) [81, 97] | +0.880 [+0.740, +0.980] | 0.12 (44/6/0/0) | 2.44 (n 50) | 50/50 | 49/50 | 119 | 0 |
| NB | personas | P09 | btw | 50 | 4 (8%) [3, 19] | 41 (82%) [69, 90] | +0.740 [+0.560, +0.880] | 2.64 (5/1/1/43) | 2.64 (n 50) | 46/50 | 45/50 | 411 | 31 |
| NB | personas | P11 | btw | 50 | 1 (2%) [0, 10] | 47 (94%) [84, 98] | +0.920 [+0.820, +1.000] | 0.42 (29/21/0/0) | 2.06 (n 50) | 49/50 | 50/50 | 132 | 0 |
| NB | personas | P13 | btw | 50 | 0 (0%) [0, 7] | 49 (98%) [90, 100] | +0.980 [+0.940, +1.000] | 0.00 (50/0/0/0) | 1.90 (n 50) | 50/50 | 50/50 | 55 | 0 |
| NB | personas | P16 | btw | 50 | 24 (48%) [35, 61] | 23 (46%) [33, 60] | -0.020 [-0.280, +0.240] | 0.10 (45/5/0/0) | 2.92 (n 50) | 50/50 | 49/50 | 205 | 2 |
| NB | personas | P18 | btw | 50 | 28 (56%) [42, 69] | 17 (34%) [22, 48] | -0.220 [-0.480, +0.020] | 0.00 (50/0/0/0) | 2.50 (n 50) | 50/50 | 50/50 | 62 | 0 |
| NB | personas | P19 | btw | 50 | 6 (12%) [6, 24] | 44 (88%) [76, 94] | +0.760 [+0.560, +0.920] | 0.00 (50/0/0/0) | 2.28 (n 50) | 50/50 | 50/50 | 58 | 0 |
| NB | personas | P20 | btw | 50 | 23 (46%) [33, 60] | 18 (36%) [24, 50] | -0.100 [-0.340, +0.160] | 0.00 (50/0/0/0) | 2.42 (n 50) | 50/50 | 50/50 | 59 | 0 |
| Nc | open | P00 | hc_a | 50 | 50 (100%) [93, 100] | 0 (0%) [0, 7] | +1.000 [+1.000, +1.000] | 2.98 (0/0/1/49) | – | 50/50 | 48/50 | 451 | 32 |
| Nc | open | P00 | hc_b | 50 | 50 (100%) [93, 100] | 0 (0%) [0, 7] | +1.000 [+1.000, +1.000] | 2.98 (0/0/1/49) | – | 50/50 | 46/50 | 430 | 23 |
| Nc | open | P00 | hp_a | 50 | 25 (50%) [37, 63] | 23 (46%) [33, 60] | +0.040 [-0.240, +0.300] | 3.00 (0/0/0/50) | – | 50/50 | 50/50 | 463 | 34 |
| Nc | open | P00 | hp_b | 50 | 19 (38%) [26, 52] | 30 (60%) [46, 72] | -0.220 [-0.480, +0.040] | 2.90 (0/1/3/46) | – | 49/50 | 48/50 | 443 | 23 |
| Nc | open | P00 | rci_a | 50 | 49 (98%) [90, 100] | 1 (2%) [0, 10] | +0.960 [+0.880, +1.000] | 2.62 (3/0/10/37) | – | 50/50 | 45/50 | 368 | 17 |
| Nc | open | P00 | rci_b | 50 | 48 (96%) [87, 99] | 0 (0%) [0, 7] | +0.960 [+0.900, +1.000] | 2.20 (4/9/10/27) | – | 50/50 | 45/50 | 347 | 19 |
| Nc | open | P00 | rcr_a | 50 | 46 (92%) [81, 97] | 3 (6%) [2, 16] | +0.860 [+0.720, +0.980] | 2.46 (1/5/14/30) | – | 50/50 | 47/50 | 391 | 19 |
| Nc | open | P00 | rcr_b | 50 | 49 (98%) [90, 100] | 1 (2%) [0, 10] | +0.960 [+0.880, +1.000] | 1.76 (13/4/15/18) | – | 50/50 | 43/50 | 330 | 18 |
| Nc | open | P00 | rpi_a | 50 | 19 (38%) [26, 52] | 31 (62%) [48, 74] | -0.240 [-0.520, +0.040] | 0.24 (42/6/0/2) | – | 50/50 | 41/50 | 290 | 20 |
| Nc | open | P00 | rpi_b | 50 | 32 (64%) [50, 76] | 17 (34%) [22, 48] | +0.300 [+0.040, +0.560] | 0.48 (35/9/3/3) | – | 50/50 | 38/50 | 340 | 24 |
| Nc | open | P00 | rpr_a | 50 | 11 (22%) [13, 35] | 39 (78%) [65, 87] | -0.560 [-0.760, -0.320] | 0.14 (43/7/0/0) | – | 50/50 | 46/50 | 211 | 11 |
| Nc | open | P00 | rpr_b | 50 | 19 (38%) [26, 52] | 32 (64%) [50, 76] | -0.260 [-0.520, +0.000] | 0.34 (37/9/4/0) | – | 50/50 | 39/50 | 294 | 18 |
| Nc | open | P00 | vcd_a | 50 | 50 (100%) [93, 100] | 0 (0%) [0, 7] | +1.000 [+1.000, +1.000] | 0.44 (35/10/3/2) | – | 50/50 | 48/50 | 175 | 6 |
| Nc | open | P00 | vcd_b | 50 | 49 (98%) [90, 100] | 0 (0%) [0, 7] | +0.980 [+0.940, +1.000] | 1.80 (6/17/8/19) | – | 50/50 | 47/50 | 319 | 14 |
| Nc | open | P00 | vch_a | 50 | 49 (98%) [90, 100] | 1 (2%) [0, 10] | +0.960 [+0.900, +1.000] | 2.98 (0/0/1/49) | – | 50/50 | 48/50 | 432 | 28 |
| Nc | open | P00 | vch_b | 50 | 41 (82%) [69, 90] | 0 (0%) [0, 7] | +0.820 [+0.700, +0.920] | 2.98 (0/0/1/49) | – | 50/50 | 47/50 | 436 | 26 |
| Nc | open | P00 | vpd_a | 50 | 15 (30%) [19, 44] | 35 (70%) [56, 81] | -0.400 [-0.640, -0.160] | 0.52 (30/15/4/1) | – | 50/50 | 46/50 | 333 | 12 |
| Nc | open | P00 | vpd_b | 50 | 14 (28%) [17, 42] | 36 (72%) [58, 83] | -0.440 [-0.680, -0.200] | 0.26 (39/9/2/0) | – | 50/50 | 38/50 | 316 | 14 |
| Nc | open | P00 | vph_a | 50 | 12 (24%) [14, 37] | 37 (74%) [60, 84] | -0.500 [-0.720, -0.240] | 2.98 (0/0/1/49) | – | 50/50 | 48/50 | 473 | 35 |
| Nc | open | P00 | vph_b | 50 | 23 (46%) [33, 60] | 25 (50%) [37, 63] | -0.040 [-0.300, +0.240] | 3.00 (0/0/0/50) | – | 50/50 | 49/50 | 468 | 30 |
| Nc | personas | P00 | btw | 50 | 46 (92%) [81, 97] | 0 (0%) [0, 7] | +0.920 [+0.840, +0.980] | 2.92 (1/0/1/48) | – | 50/50 | 48/50 | 440 | 32 |
| Nc | personas | P00 | free | 50 | 0 (0%) [0, 7] | 0 (0%) [0, 7] | +0.000 [+0.000, +0.000] | 2.94 (0/1/1/48) | – | 3/50 | 46/50 | 464 | 38 |
| Nc | personas | P01 | btw | 50 | 15 (30%) [19, 44] | 32 (64%) [50, 76] | -0.340 [-0.580, -0.080] | 0.20 (41/8/1/0) | 3.00 (n 50) | 50/50 | 50/50 | 64 | 0 |
| Nc | personas | P06 | btw | 50 | 6 (12%) [6, 24] | 42 (84%) [71, 92] | -0.720 [-0.880, -0.520] | 0.00 (50/0/0/0) | 2.94 (n 50) | 50/50 | 50/50 | 256 | 0 |
| Nc | personas | P06 | free | 50 | 0 (0%) [0, 7] | 1 (2%) [0, 10] | -0.020 [-0.060, +0.000] | 0.02 (49/1/0/0) | 3.00 (n 50) | 1/50 | 50/50 | 224 | 0 |
| Nc | personas | P07 | btw | 50 | 48 (96%) [87, 99] | 0 (0%) [0, 7] | +0.960 [+0.900, +1.000] | 2.90 (1/0/2/47) | 1.98 (n 50) | 49/50 | 47/50 | 473 | 33 |
| Nc | personas | P07 | free | 50 | 0 (0%) [0, 7] | 0 (0%) [0, 7] | +0.000 [+0.000, +0.000] | 3.00 (0/0/0/50) | 2.72 (n 50) | 37/50 | 49/50 | 486 | 26 |
| Nc | personas | P08 | btw | 50 | 43 (86%) [74, 93] | 6 (12%) [6, 24] | +0.740 [+0.540, +0.920] | 0.14 (43/7/0/0) | 2.48 (n 50) | 50/50 | 50/50 | 106 | 0 |
| Nc | personas | P09 | btw | 50 | 30 (60%) [46, 72] | 12 (24%) [14, 37] | +0.360 [+0.120, +0.600] | 2.86 (2/0/1/47) | 2.86 (n 50) | 47/50 | 45/50 | 465 | 38 |
| Nc | personas | P11 | btw | 50 | 41 (82%) [69, 90] | 8 (16%) [8, 29] | +0.660 [+0.440, +0.840] | 0.48 (26/24/0/0) | 2.28 (n 50) | 50/50 | 50/50 | 120 | 0 |
| Nc | personas | P13 | btw | 50 | 36 (72%) [58, 83] | 11 (22%) [13, 35] | +0.500 [+0.260, +0.720] | 0.00 (50/0/0/0) | 2.14 (n 50) | 50/50 | 50/50 | 47 | 0 |
| Nc | personas | P16 | btw | 50 | 13 (26%) [16, 40] | 36 (72%) [58, 83] | -0.460 [-0.680, -0.200] | 0.18 (41/9/0/0) | 2.86 (n 50) | 50/50 | 50/50 | 191 | 0 |
| Nc | personas | P18 | btw | 50 | 9 (18%) [10, 31] | 41 (82%) [69, 90] | -0.640 [-0.840, -0.400] | 0.00 (50/0/0/0) | 2.36 (n 50) | 50/50 | 50/50 | 65 | 0 |
| Nc | personas | P19 | btw | 50 | 47 (94%) [84, 98] | 2 (4%) [1, 13] | +0.900 [+0.780, +1.000] | 0.00 (50/0/0/0) | 2.44 (n 50) | 50/50 | 50/50 | 55 | 0 |
| Nc | personas | P20 | btw | 50 | 8 (16%) [8, 29] | 42 (84%) [71, 92] | -0.680 [-0.880, -0.480] | 0.00 (50/0/0/0) | 2.44 (n 50) | 50/50 | 50/50 | 60 | 0 |
| Nc | t1check | P00 | t1 | 50 | 2 (4%) [1, 13] | 0 (0%) [0, 7] | +0.040 [+0.000, +0.100] | 3.00 (0/0/0/50) | – | 3/50 | 48/50 | 466 | 37 |
| NBc | open | P00 | hc_a | 50 | 6 (12%) [6, 24] | 44 (88%) [76, 94] | +0.760 [+0.560, +0.920] | 3.00 (0/0/0/50) | – | 50/50 | 49/50 | 461 | 35 |
| NBc | open | P00 | hc_b | 50 | 0 (0%) [0, 7] | 43 (86%) [74, 93] | +0.860 [+0.760, +0.940] | 2.98 (0/0/1/49) | – | 47/50 | 49/50 | 425 | 22 |
| NBc | open | P00 | hp_a | 50 | 44 (88%) [76, 94] | 2 (4%) [1, 13] | -0.840 [-0.940, -0.700] | 2.94 (0/1/1/48) | – | 50/50 | 47/50 | 450 | 28 |
| NBc | open | P00 | hp_b | 50 | 39 (78%) [65, 87] | 9 (18%) [10, 31] | -0.600 [-0.800, -0.380] | 2.74 (1/3/4/42) | – | 49/50 | 44/50 | 448 | 28 |
| NBc | open | P00 | rci_a | 50 | 15 (30%) [19, 44] | 32 (64%) [50, 76] | +0.340 [+0.080, +0.580] | 2.38 (5/4/8/33) | – | 50/50 | 48/50 | 367 | 19 |
| NBc | open | P00 | rci_b | 50 | 5 (10%) [4, 21] | 40 (80%) [67, 89] | +0.700 [+0.520, +0.860] | 2.36 (4/5/10/31) | – | 50/50 | 48/50 | 316 | 11 |
| NBc | open | P00 | rcr_a | 50 | 28 (56%) [42, 69] | 20 (40%) [28, 54] | -0.160 [-0.400, +0.120] | 2.00 (3/9/23/15) | – | 50/50 | 41/50 | 372 | 19 |
| NBc | open | P00 | rcr_b | 50 | 19 (38%) [26, 52] | 29 (58%) [44, 71] | +0.200 [-0.080, +0.480] | 1.42 (14/16/5/15) | – | 50/50 | 45/50 | 286 | 11 |
| NBc | open | P00 | rpi_a | 50 | 42 (84%) [71, 92] | 0 (0%) [0, 7] | -0.840 [-0.920, -0.720] | 0.08 (47/2/1/0) | – | 50/50 | 38/50 | 224 | 15 |
| NBc | open | P00 | rpi_b | 50 | 48 (96%) [87, 99] | 1 (2%) [0, 10] | -0.940 [-1.000, -0.840] | 0.70 (32/7/5/6) | – | 50/50 | 39/50 | 310 | 17 |
| NBc | open | P00 | rpr_a | 50 | 35 (70%) [56, 81] | 0 (0%) [0, 7] | -0.700 [-0.820, -0.560] | 0.02 (49/1/0/0) | – | 50/50 | 41/50 | 184 | 10 |
| NBc | open | P00 | rpr_b | 50 | 44 (88%) [76, 94] | 0 (0%) [0, 7] | -0.880 [-0.960, -0.780] | 0.62 (31/12/2/5) | – | 50/50 | 37/50 | 349 | 20 |
| NBc | open | P00 | vcd_a | 50 | 22 (44%) [31, 58] | 21 (42%) [29, 56] | -0.020 [-0.280, +0.220] | 0.42 (35/11/2/2) | – | 50/50 | 48/50 | 180 | 8 |
| NBc | open | P00 | vcd_b | 50 | 10 (20%) [11, 33] | 37 (74%) [60, 84] | +0.540 [+0.300, +0.760] | 1.54 (7/19/14/10) | – | 50/50 | 44/50 | 311 | 10 |
| NBc | open | P00 | vch_a | 50 | 1 (2%) [0, 10] | 46 (92%) [81, 97] | +0.900 [+0.780, +0.980] | 2.98 (0/0/1/49) | – | 50/50 | 48/50 | 439 | 25 |
| NBc | open | P00 | vch_b | 50 | 2 (4%) [1, 13] | 30 (60%) [46, 72] | +0.560 [+0.400, +0.720] | 3.00 (0/0/0/50) | – | 48/50 | 50/50 | 436 | 27 |
| NBc | open | P00 | vpd_a | 50 | 43 (86%) [74, 93] | 1 (2%) [0, 10] | -0.840 [-0.940, -0.720] | 0.52 (31/13/5/1) | – | 50/50 | 32/50 | 349 | 21 |
| NBc | open | P00 | vpd_b | 50 | 46 (92%) [81, 97] | 0 (0%) [0, 7] | -0.920 [-0.980, -0.840] | 0.38 (37/9/2/2) | – | 50/50 | 37/50 | 303 | 13 |
| NBc | open | P00 | vph_a | 50 | 44 (88%) [76, 94] | 4 (8%) [3, 19] | -0.800 [-0.940, -0.640] | 2.96 (0/0/2/48) | – | 50/50 | 46/50 | 464 | 27 |
| NBc | open | P00 | vph_b | 50 | 37 (74%) [60, 84] | 7 (14%) [7, 26] | -0.600 [-0.780, -0.380] | 2.92 (1/0/1/48) | – | 50/50 | 48/50 | 432 | 29 |
| NBc | personas | P00 | btw | 50 | 10 (20%) [11, 33] | 29 (58%) [44, 71] | +0.380 [+0.160, +0.580] | 2.96 (0/1/0/49) | – | 45/50 | 50/50 | 439 | 31 |
| NBc | personas | P00 | free | 50 | 1 (2%) [0, 10] | 1 (2%) [0, 10] | +0.000 [-0.060, +0.060] | 2.96 (0/1/0/49) | – | 4/50 | 49/50 | 466 | 37 |
| NBc | personas | P01 | btw | 50 | 8 (16%) [8, 29] | 23 (46%) [33, 60] | +0.300 [+0.100, +0.500] | 0.36 (32/18/0/0) | 2.94 (n 50) | 49/50 | 50/50 | 56 | 0 |
| NBc | personas | P06 | btw | 50 | 37 (74%) [60, 84] | 3 (6%) [2, 16] | -0.680 [-0.820, -0.520] | 0.04 (48/2/0/0) | 2.88 (n 50) | 49/50 | 50/50 | 245 | 0 |
| NBc | personas | P06 | free | 50 | 0 (0%) [0, 7] | 0 (0%) [0, 7] | +0.000 [+0.000, +0.000] | 0.02 (49/1/0/0) | 3.00 (n 50) | 0/50 | 50/50 | 220 | 0 |
| NBc | personas | P07 | btw | 50 | 1 (2%) [0, 10] | 23 (46%) [33, 60] | +0.440 [+0.300, +0.580] | 2.92 (1/0/1/48) | 2.28 (n 50) | 47/50 | 48/50 | 460 | 25 |
| NBc | personas | P07 | free | 50 | 0 (0%) [0, 7] | 0 (0%) [0, 7] | +0.000 [+0.000, +0.000] | 2.98 (0/0/1/48) | 2.88 (n 49) | 42/49 | 49/49 | 487 | 31 |
| NBc | personas | P08 | btw | 50 | 4 (8%) [3, 19] | 44 (88%) [76, 94] | +0.800 [+0.620, +0.940] | 0.12 (44/6/0/0) | 2.52 (n 50) | 50/50 | 50/50 | 113 | 0 |
| NBc | personas | P09 | btw | 50 | 14 (28%) [17, 42] | 19 (38%) [26, 52] | +0.100 [-0.120, +0.320] | 2.90 (1/0/2/47) | 2.92 (n 50) | 42/50 | 48/50 | 472 | 39 |
| NBc | personas | P11 | btw | 50 | 5 (10%) [4, 21] | 41 (82%) [69, 90] | +0.720 [+0.540, +0.880] | 0.38 (31/19/0/0) | 2.22 (n 50) | 50/50 | 50/50 | 126 | 0 |
| NBc | personas | P13 | btw | 50 | 1 (2%) [0, 10] | 48 (96%) [87, 99] | +0.940 [+0.840, +1.000] | 0.00 (50/0/0/0) | 1.78 (n 50) | 50/50 | 50/50 | 48 | 0 |
| NBc | personas | P16 | btw | 50 | 39 (78%) [65, 87] | 6 (12%) [6, 24] | -0.660 [-0.840, -0.480] | 0.06 (47/3/0/0) | 2.96 (n 50) | 50/50 | 50/50 | 191 | 0 |
| NBc | personas | P18 | btw | 50 | 37 (74%) [60, 84] | 7 (14%) [7, 26] | -0.600 [-0.780, -0.400] | 0.00 (50/0/0/0) | 2.40 (n 50) | 50/50 | 50/50 | 59 | 0 |
| NBc | personas | P19 | btw | 50 | 6 (12%) [6, 24] | 42 (84%) [71, 92] | +0.720 [+0.520, +0.880] | 0.00 (50/0/0/0) | 2.02 (n 50) | 50/50 | 50/50 | 52 | 0 |
| NBc | personas | P20 | btw | 50 | 30 (60%) [46, 72] | 10 (20%) [11, 33] | -0.400 [-0.620, -0.180] | 0.00 (50/0/0/0) | 2.46 (n 50) | 50/50 | 50/50 | 52 | 0 |
| NBc | t1check | P00 | t1 | 50 | 0 (0%) [0, 7] | 1 (2%) [0, 10] | +0.020 [+0.000, +0.060] | 3.00 (0/0/0/50) | – | 6/50 | 49/50 | 461 | 35 |
| X | open | P00 | hc_a | 50 | 23 (46%) [33, 60] | 27 (54%) [40, 67] | -0.080 [-0.360, +0.200] | 2.96 (0/1/0/49) | – | 50/50 | 48/50 | 428 | 23 |
| X | open | P00 | hc_b | 50 | 6 (12%) [6, 24] | 44 (88%) [76, 94] | -0.760 [-0.920, -0.560] | 2.96 (0/0/2/48) | – | 50/50 | 49/50 | 362 | 13 |
| X | open | P00 | hp_a | 50 | 43 (86%) [74, 93] | 1 (2%) [0, 10] | +0.840 [+0.720, +0.940] | 2.98 (0/0/1/49) | – | 50/50 | 48/50 | 436 | 27 |
| X | open | P00 | hp_b | 50 | 40 (80%) [67, 89] | 4 (8%) [3, 19] | +0.720 [+0.540, +0.880] | 3.00 (0/0/0/50) | – | 50/50 | 48/50 | 434 | 27 |
| X | open | P00 | rci_a | 50 | 7 (14%) [7, 26] | 43 (86%) [74, 93] | -0.720 [-0.880, -0.520] | 0.50 (30/15/5/0) | – | 50/50 | 48/50 | 297 | 14 |
| X | open | P00 | rci_b | 50 | 11 (22%) [13, 35] | 37 (74%) [60, 84] | -0.520 [-0.740, -0.280] | 0.34 (38/7/5/0) | – | 50/50 | 45/50 | 267 | 12 |
| X | open | P00 | rcr_a | 50 | 22 (44%) [31, 58] | 28 (56%) [42, 69] | -0.120 [-0.400, +0.160] | 1.04 (18/18/8/6) | – | 50/50 | 38/50 | 340 | 15 |
| X | open | P00 | rcr_b | 50 | 11 (22%) [13, 35] | 39 (78%) [65, 87] | -0.560 [-0.760, -0.320] | 0.58 (31/13/2/4) | – | 50/50 | 47/50 | 248 | 8 |
| X | open | P00 | rpi_a | 50 | 41 (82%) [69, 90] | 1 (2%) [0, 10] | +0.800 [+0.660, +0.920] | 0.12 (46/3/0/1) | – | 50/50 | 48/50 | 132 | 3 |
| X | open | P00 | rpi_b | 50 | 46 (92%) [81, 97] | 2 (4%) [1, 13] | +0.880 [+0.760, +0.980] | 1.04 (27/4/9/10) | – | 50/50 | 41/50 | 268 | 14 |
| X | open | P00 | rpr_a | 50 | 42 (84%) [71, 92] | 1 (2%) [0, 10] | +0.820 [+0.700, +0.920] | 0.68 (36/2/4/8) | – | 50/50 | 41/50 | 215 | 10 |
| X | open | P00 | rpr_b | 50 | 43 (86%) [74, 93] | 4 (8%) [3, 19] | +0.780 [+0.600, +0.920] | 1.02 (27/5/8/10) | – | 50/50 | 37/50 | 242 | 10 |
| X | open | P00 | vcd_a | 50 | 23 (46%) [33, 60] | 25 (50%) [37, 63] | -0.040 [-0.300, +0.240] | 0.06 (47/3/0/0) | – | 50/50 | 49/50 | 170 | 6 |
| X | open | P00 | vcd_b | 50 | 17 (34%) [22, 48] | 33 (66%) [52, 78] | -0.320 [-0.560, -0.060] | 0.30 (38/9/3/0) | – | 50/50 | 46/50 | 265 | 12 |
| X | open | P00 | vch_a | 50 | 10 (20%) [11, 33] | 38 (76%) [63, 86] | -0.560 [-0.780, -0.340] | 2.78 (1/0/8/41) | – | 50/50 | 49/50 | 376 | 15 |
| X | open | P00 | vch_b | 50 | 13 (26%) [16, 40] | 31 (62%) [48, 74] | -0.360 [-0.600, -0.120] | 3.00 (0/0/0/50) | – | 49/50 | 48/50 | 417 | 13 |
| X | open | P00 | vpd_a | 50 | 39 (78%) [65, 87] | 7 (14%) [7, 26] | +0.640 [+0.440, +0.820] | 0.68 (32/7/6/5) | – | 50/50 | 42/50 | 216 | 7 |
| X | open | P00 | vpd_b | 50 | 42 (84%) [71, 92] | 6 (12%) [6, 24] | +0.720 [+0.540, +0.880] | 1.14 (24/6/9/11) | – | 50/50 | 46/50 | 275 | 8 |
| X | open | P00 | vph_a | 50 | 44 (88%) [76, 94] | 1 (2%) [0, 10] | +0.860 [+0.740, +0.960] | 2.96 (0/0/2/48) | – | 50/50 | 48/50 | 473 | 35 |
| X | open | P00 | vph_b | 50 | 42 (84%) [71, 92] | 3 (6%) [2, 16] | +0.780 [+0.620, +0.920] | 3.00 (0/0/0/50) | – | 50/50 | 49/50 | 468 | 37 |
| X | personas | P00 | btw | 50 | 26 (52%) [39, 65] | 12 (24%) [14, 37] | +0.280 [+0.060, +0.500] | 3.00 (0/0/0/50) | – | 48/50 | 49/50 | 424 | 24 |
| X | personas | P00 | free | 50 | 1 (2%) [0, 10] | 0 (0%) [0, 7] | +0.020 [+0.000, +0.060] | 2.94 (1/0/0/49) | – | 2/50 | 49/50 | 467 | 37 |
| X | personas | P01 | btw | 50 | 11 (22%) [13, 35] | 26 (52%) [39, 65] | -0.300 [-0.500, -0.080] | 0.18 (42/7/1/0) | 2.90 (n 50) | 49/50 | 50/50 | 64 | 0 |
| X | personas | P06 | btw | 50 | 34 (68%) [54, 79] | 4 (8%) [3, 19] | +0.600 [+0.420, +0.760] | 0.04 (48/2/0/0) | 2.86 (n 50) | 48/50 | 50/50 | 232 | 0 |
| X | personas | P06 | free | 50 | 0 (0%) [0, 7] | 0 (0%) [0, 7] | +0.000 [+0.000, +0.000] | 0.04 (48/2/0/0) | 3.00 (n 50) | 0/50 | 50/50 | 225 | 0 |
| X | personas | P07 | btw | 50 | 7 (14%) [7, 26] | 24 (48%) [35, 61] | -0.340 [-0.540, -0.140] | 2.86 (2/0/1/46) | 2.27 (n 49) | 47/49 | 47/49 | 451 | 26 |
| X | personas | P07 | free | 50 | 1 (2%) [0, 10] | 1 (2%) [0, 10] | +0.000 [-0.060, +0.060] | 3.00 (0/0/0/50) | 2.74 (n 50) | 41/50 | 50/50 | 484 | 25 |
| X | personas | P08 | btw | 50 | 1 (2%) [0, 10] | 47 (94%) [84, 98] | -0.920 [-1.000, -0.800] | 0.00 (50/0/0/0) | 2.72 (n 50) | 50/50 | 50/50 | 106 | 0 |
| X | personas | P09 | btw | 50 | 28 (56%) [42, 69] | 4 (8%) [3, 19] | +0.480 [+0.300, +0.640] | 2.92 (1/0/1/48) | 2.96 (n 50) | 42/50 | 47/50 | 469 | 37 |
| X | personas | P11 | btw | 50 | 3 (6%) [2, 16] | 46 (92%) [81, 97] | -0.860 [-0.980, -0.720] | 0.38 (31/19/0/0) | 2.36 (n 50) | 50/50 | 50/50 | 123 | 0 |
| X | personas | P13 | btw | 50 | 6 (12%) [6, 24] | 43 (86%) [74, 93] | -0.740 [-0.900, -0.540] | 0.00 (50/0/0/0) | 1.80 (n 50) | 50/50 | 50/50 | 54 | 0 |
| X | personas | P16 | btw | 50 | 29 (58%) [44, 71] | 16 (32%) [21, 46] | +0.260 [+0.000, +0.500] | 0.22 (39/11/0/0) | 2.76 (n 50) | 49/50 | 50/50 | 181 | 0 |
| X | personas | P18 | btw | 50 | 42 (84%) [71, 92] | 4 (8%) [3, 19] | +0.760 [+0.580, +0.920] | 0.00 (50/0/0/0) | 2.22 (n 50) | 50/50 | 50/50 | 57 | 0 |
| X | personas | P19 | btw | 50 | 3 (6%) [2, 16] | 47 (94%) [84, 98] | -0.880 [-1.000, -0.720] | 0.00 (50/0/0/0) | 2.28 (n 50) | 50/50 | 50/50 | 60 | 0 |
| X | personas | P20 | btw | 50 | 38 (76%) [63, 86] | 7 (14%) [7, 26] | +0.620 [+0.420, +0.800] | 0.00 (50/0/0/0) | 2.44 (n 50) | 49/50 | 50/50 | 51 | 0 |
| X | t1check | P00 | t1 | 50 | 0 (0%) [0, 7] | 0 (0%) [0, 7] | +0.000 [+0.000, +0.000] | 2.98 (0/0/1/49) | – | 4/50 | 49/50 | 463 | 38 |
| XB | open | P00 | hc_a | 50 | 16 (32%) [21, 46] | 34 (68%) [54, 79] | +0.360 [+0.080, +0.600] | 2.98 (0/0/1/49) | – | 50/50 | 49/50 | 429 | 19 |
| XB | open | P00 | hc_b | 50 | 42 (84%) [71, 92] | 8 (16%) [8, 29] | -0.680 [-0.880, -0.479] | 2.94 (0/0/3/47) | – | 50/50 | 47/50 | 391 | 20 |
| XB | open | P00 | hp_a | 50 | 2 (4%) [1, 13] | 48 (96%) [87, 99] | +0.920 [+0.800, +1.000] | 2.98 (0/0/1/49) | – | 50/50 | 48/50 | 453 | 30 |
| XB | open | P00 | hp_b | 50 | 2 (4%) [1, 13] | 47 (94%) [84, 98] | +0.900 [+0.780, +1.000] | 3.00 (0/0/0/50) | – | 49/50 | 47/50 | 439 | 21 |
| XB | open | P00 | rci_a | 50 | 47 (94%) [84, 98] | 3 (6%) [2, 16] | -0.880 [-1.000, -0.720] | 0.50 (30/16/3/1) | – | 50/50 | 44/50 | 406 | 27 |
| XB | open | P00 | rci_b | 50 | 44 (88%) [76, 94] | 6 (12%) [6, 24] | -0.760 [-0.920, -0.560] | 0.58 (30/14/3/3) | – | 50/50 | 50/50 | 331 | 18 |
| XB | open | P00 | rcr_a | 50 | 36 (72%) [58, 83] | 14 (28%) [17, 42] | -0.440 [-0.680, -0.200] | 0.92 (21/17/7/5) | – | 50/50 | 40/50 | 408 | 24 |
| XB | open | P00 | rcr_b | 50 | 35 (70%) [56, 81] | 15 (30%) [19, 44] | -0.400 [-0.640, -0.120] | 0.96 (25/11/5/9) | – | 50/50 | 45/50 | 308 | 16 |
| XB | open | P00 | rpi_a | 50 | 4 (8%) [3, 19] | 46 (92%) [81, 97] | +0.840 [+0.680, +0.960] | 0.32 (41/4/3/2) | – | 50/50 | 41/50 | 275 | 17 |
| XB | open | P00 | rpi_b | 50 | 1 (2%) [0, 10] | 49 (98%) [90, 100] | +0.960 [+0.880, +1.000] | 0.96 (27/7/7/9) | – | 50/50 | 35/50 | 375 | 23 |
| XB | open | P00 | rpr_a | 50 | 0 (0%) [0, 7] | 50 (100%) [93, 100] | +1.000 [+1.000, +1.000] | 0.78 (32/5/5/8) | – | 50/50 | 44/50 | 263 | 13 |
| XB | open | P00 | rpr_b | 50 | 4 (8%) [3, 19] | 46 (92%) [81, 97] | +0.840 [+0.680, +0.960] | 1.26 (22/5/11/12) | – | 50/50 | 40/50 | 334 | 14 |
| XB | open | P00 | vcd_a | 50 | 41 (82%) [69, 90] | 10 (20%) [11, 33] | -0.620 [-0.800, -0.400] | 0.12 (44/6/0/0) | – | 50/50 | 48/50 | 299 | 18 |
| XB | open | P00 | vcd_b | 50 | 30 (60%) [46, 72] | 18 (36%) [24, 50] | -0.240 [-0.500, +0.020] | 0.46 (32/13/5/0) | – | 50/50 | 46/50 | 308 | 17 |
| XB | open | P00 | vch_a | 50 | 42 (84%) [71, 92] | 8 (16%) [8, 29] | -0.680 [-0.880, -0.480] | 2.86 (0/0/7/43) | – | 50/50 | 45/50 | 411 | 21 |
| XB | open | P00 | vch_b | 50 | 39 (78%) [65, 87] | 10 (20%) [11, 33] | -0.580 [-0.800, -0.360] | 2.98 (0/0/1/49) | – | 49/50 | 48/50 | 411 | 19 |
| XB | open | P00 | vpd_a | 50 | 3 (6%) [2, 16] | 46 (92%) [81, 97] | +0.860 [+0.720, +0.980] | 1.36 (17/12/7/14) | – | 50/50 | 42/50 | 355 | 18 |
| XB | open | P00 | vpd_b | 50 | 7 (14%) [7, 26] | 43 (86%) [74, 93] | +0.720 [+0.520, +0.880] | 1.96 (9/6/13/22) | – | 50/50 | 41/50 | 390 | 15 |
| XB | open | P00 | vph_a | 50 | 0 (0%) [0, 7] | 50 (100%) [93, 100] | +1.000 [+1.000, +1.000] | 3.00 (0/0/0/50) | – | 50/50 | 50/50 | 478 | 36 |
| XB | open | P00 | vph_b | 50 | 1 (2%) [0, 10] | 49 (98%) [90, 100] | +0.960 [+0.880, +1.000] | 2.98 (0/0/1/49) | – | 50/50 | 48/50 | 452 | 33 |
| XB | personas | P00 | btw | 50 | 6 (12%) [6, 24] | 36 (72%) [58, 83] | +0.600 [+0.420, +0.780] | 2.94 (1/0/0/49) | – | 45/50 | 48/50 | 441 | 32 |
| XB | personas | P00 | free | 50 | 0 (0%) [0, 7] | 5 (10%) [4, 21] | +0.100 [+0.020, +0.180] | 2.98 (0/0/1/49) | – | 5/50 | 47/50 | 471 | 38 |
| XB | personas | P01 | btw | 50 | 37 (74%) [60, 84] | 12 (24%) [14, 37] | -0.500 [-0.720, -0.240] | 0.02 (49/1/0/0) | 3.00 (n 50) | 50/50 | 50/50 | 65 | 0 |
| XB | personas | P06 | btw | 50 | 3 (6%) [2, 16] | 43 (86%) [74, 93] | +0.800 [+0.640, +0.940] | 0.02 (49/1/0/0) | 3.00 (n 50) | 48/50 | 50/50 | 257 | 0 |
| XB | personas | P06 | free | 50 | 0 (0%) [0, 7] | 0 (0%) [0, 7] | +0.000 [+0.000, +0.000] | 0.10 (45/5/0/0) | 3.00 (n 50) | 0/50 | 50/50 | 229 | 0 |
| XB | personas | P07 | btw | 50 | 32 (64%) [50, 76] | 11 (22%) [13, 35] | -0.420 [-0.640, -0.200] | 2.98 (0/0/1/49) | 1.96 (n 50) | 50/50 | 46/50 | 480 | 29 |
| XB | personas | P07 | free | 50 | 3 (6%) [2, 16] | 0 (0%) [0, 7] | -0.060 [-0.140, +0.000] | 3.00 (0/0/0/50) | 2.76 (n 50) | 38/50 | 50/50 | 485 | 29 |
| XB | personas | P08 | btw | 50 | 48 (96%) [87, 99] | 1 (2%) [0, 10] | -0.940 [-1.000, -0.840] | 0.04 (48/2/0/0) | 2.68 (n 50) | 50/50 | 50/50 | 107 | 0 |
| XB | personas | P09 | btw | 50 | 3 (6%) [2, 16] | 33 (66%) [52, 78] | +0.600 [+0.420, +0.760] | 2.84 (2/0/2/46) | 2.86 (n 50) | 39/50 | 42/50 | 476 | 42 |
| XB | personas | P11 | btw | 50 | 43 (86%) [74, 93] | 3 (6%) [2, 16] | -0.800 [-0.940, -0.640] | 0.32 (34/16/0/0) | 2.58 (n 50) | 47/50 | 50/50 | 123 | 0 |
| XB | personas | P13 | btw | 50 | 46 (92%) [81, 97] | 4 (8%) [3, 19] | -0.840 [-0.960, -0.680] | 0.00 (50/0/0/0) | 2.08 (n 50) | 50/50 | 50/50 | 47 | 0 |
| XB | personas | P16 | btw | 50 | 15 (30%) [19, 44] | 33 (66%) [52, 78] | +0.360 [+0.100, +0.600] | 0.18 (41/9/0/0) | 2.84 (n 50) | 48/50 | 49/50 | 195 | 0 |
| XB | personas | P18 | btw | 50 | 8 (16%) [8, 29] | 42 (84%) [71, 92] | +0.680 [+0.480, +0.880] | 0.00 (50/0/0/0) | 2.30 (n 50) | 50/50 | 50/50 | 61 | 0 |
| XB | personas | P19 | btw | 50 | 49 (98%) [90, 100] | 1 (2%) [0, 10] | -0.960 [-1.000, -0.880] | 0.00 (50/0/0/0) | 2.56 (n 50) | 50/50 | 50/50 | 57 | 0 |
| XB | personas | P20 | btw | 50 | 11 (22%) [13, 35] | 39 (78%) [65, 87] | +0.560 [+0.360, +0.760] | 0.00 (50/0/0/0) | 2.24 (n 50) | 50/50 | 50/50 | 56 | 0 |
| XB | t1check | P00 | t1 | 50 | 1 (2%) [0, 10] | 6 (12%) [6, 24] | +0.100 [+0.000, +0.200] | 2.98 (0/0/1/49) | – | 12/50 | 47/50 | 472 | 39 |
| S | open | P00 | hc_a | 50 | 44 (88%) [76, 94] | 5 (10%) [4, 21] | +0.780 [+0.600, +0.920] | 2.98 (0/0/1/49) | – | 50/50 | 43/50 | 447 | 20 |
| S | open | P00 | hc_b | 50 | 42 (84%) [71, 92] | 8 (16%) [8, 29] | +0.680 [+0.480, +0.880] | 3.00 (0/0/0/50) | – | 50/50 | 43/50 | 446 | 17 |
| S | open | P00 | hp_a | 50 | 50 (100%) [93, 100] | 0 (0%) [0, 7] | +1.000 [+1.000, +1.000] | 2.98 (0/0/1/49) | – | 50/50 | 49/50 | 432 | 18 |
| S | open | P00 | hp_b | 50 | 48 (96%) [87, 99] | 1 (2%) [0, 10] | +0.940 [+0.840, +1.000] | 2.98 (0/0/1/49) | – | 50/50 | 46/50 | 471 | 31 |
| S | open | P00 | rci_a | 50 | 3 (6%) [2, 16] | 47 (94%) [84, 98] | -0.880 [-1.000, -0.720] | 2.14 (7/6/10/27) | – | 50/50 | 46/50 | 377 | 8 |
| S | open | P00 | rci_b | 50 | 4 (8%) [3, 19] | 48 (96%) [87, 99] | -0.880 [-0.980, -0.740] | 1.74 (5/15/18/12) | – | 50/50 | 34/50 | 361 | 5 |
| S | open | P00 | rcr_a | 50 | 11 (22%) [13, 35] | 40 (80%) [67, 89] | -0.580 [-0.800, -0.360] | 2.10 (4/5/23/18) | – | 50/50 | 38/50 | 373 | 10 |
| S | open | P00 | rcr_b | 50 | 7 (14%) [7, 26] | 43 (86%) [74, 93] | -0.720 [-0.920, -0.520] | 2.12 (5/3/23/19) | – | 50/50 | 42/50 | 357 | 7 |
| S | open | P00 | rpi_a | 50 | 16 (32%) [21, 46] | 34 (68%) [54, 79] | -0.360 [-0.600, -0.120] | 2.26 (6/4/11/29) | – | 50/50 | 43/50 | 355 | 9 |
| S | open | P00 | rpi_b | 50 | 27 (54%) [40, 67] | 23 (46%) [33, 60] | +0.080 [-0.200, +0.360] | 2.84 (0/1/6/43) | – | 50/50 | 47/50 | 385 | 10 |
| S | open | P00 | rpr_a | 50 | 37 (74%) [60, 84] | 12 (24%) [14, 37] | +0.500 [+0.240, +0.720] | 1.84 (11/6/13/20) | – | 50/50 | 42/50 | 299 | 8 |
| S | open | P00 | rpr_b | 50 | 26 (52%) [39, 65] | 25 (50%) [37, 63] | +0.020 [-0.260, +0.280] | 2.26 (3/4/20/23) | – | 50/50 | 41/50 | 315 | 4 |
| S | open | P00 | vcd_a | 50 | 4 (8%) [3, 19] | 46 (92%) [81, 97] | -0.840 [-0.960, -0.680] | 1.84 (8/7/20/15) | – | 50/50 | 42/50 | 353 | 5 |
| S | open | P00 | vcd_b | 50 | 7 (14%) [7, 26] | 42 (84%) [71, 92] | -0.700 [-0.880, -0.500] | 1.56 (8/16/16/10) | – | 50/50 | 44/50 | 302 | 3 |
| S | open | P00 | vch_a | 50 | 44 (88%) [76, 94] | 7 (14%) [7, 26] | +0.740 [+0.540, +0.900] | 2.94 (0/0/3/47) | – | 50/50 | 39/50 | 450 | 19 |
| S | open | P00 | vch_b | 50 | 36 (72%) [58, 83] | 12 (24%) [14, 37] | +0.480 [+0.240, +0.720] | 2.94 (0/0/3/47) | – | 49/50 | 43/50 | 457 | 20 |
| S | open | P00 | vpd_a | 50 | 23 (46%) [33, 60] | 26 (52%) [39, 65] | -0.060 [-0.320, +0.200] | 2.56 (0/4/14/32) | – | 50/50 | 38/50 | 341 | 7 |
| S | open | P00 | vpd_b | 50 | 30 (60%) [46, 72] | 22 (44%) [31, 58] | +0.160 [-0.100, +0.440] | 2.08 (11/2/9/28) | – | 50/50 | 41/50 | 288 | 3 |
| S | open | P00 | vph_a | 50 | 48 (96%) [87, 99] | 2 (4%) [1, 13] | +0.920 [+0.800, +1.000] | 3.00 (0/0/0/50) | – | 50/50 | 46/50 | 472 | 31 |
| S | open | P00 | vph_b | 50 | 45 (90%) [79, 96] | 1 (2%) [0, 10] | +0.880 [+0.760, +0.980] | 3.00 (0/0/0/50) | – | 50/50 | 47/50 | 470 | 29 |
| S | personas | P00 | btw | 50 | 46 (92%) [81, 97] | 2 (4%) [1, 13] | +0.880 [+0.740, +0.980] | 3.00 (0/0/0/50) | – | 49/50 | 49/50 | 426 | 18 |
| S | personas | P00 | free | 50 | 4 (8%) [3, 19] | 0 (0%) [0, 7] | +0.080 [+0.020, +0.160] | 3.00 (0/0/0/50) | – | 5/50 | 50/50 | 448 | 28 |
| S | personas | P01 | btw | 50 | 2 (4%) [1, 13] | 48 (96%) [87, 99] | -0.920 [-1.000, -0.800] | 1.38 (6/21/21/2) | 2.44 (n 50) | 50/50 | 49/50 | 92 | 0 |
| S | personas | P06 | btw | 50 | 44 (88%) [76, 94] | 9 (18%) [10, 31] | +0.700 [+0.500, +0.880] | 1.58 (14/8/13/15) | 1.56 (n 50) | 50/50 | 48/50 | 319 | 1 |
| S | personas | P06 | free | 50 | 0 (0%) [0, 7] | 0 (0%) [0, 7] | +0.000 [+0.000, +0.000] | 0.16 (44/5/0/1) | 2.94 (n 50) | 0/50 | 50/50 | 221 | 0 |
| S | personas | P07 | btw | 50 | 41 (82%) [69, 90] | 4 (8%) [3, 19] | +0.740 [+0.560, +0.880] | 2.96 (0/0/2/48) | 1.74 (n 50) | 50/50 | 40/50 | 466 | 18 |
| S | personas | P07 | free | 50 | 11 (22%) [13, 35] | 3 (6%) [2, 16] | +0.160 [+0.020, +0.300] | 3.00 (0/0/0/50) | 2.56 (n 50) | 42/50 | 49/50 | 448 | 14 |
| S | personas | P08 | btw | 50 | 27 (54%) [40, 67] | 22 (44%) [31, 58] | +0.100 [-0.160, +0.380] | 1.62 (8/15/15/12) | 1.48 (n 50) | 50/50 | 49/50 | 208 | 0 |
| S | personas | P09 | btw | 50 | 42 (84%) [71, 92] | 2 (4%) [1, 13] | +0.800 [+0.660, +0.920] | 2.94 (1/0/0/49) | 2.82 (n 50) | 48/50 | 46/50 | 461 | 26 |
| S | personas | P11 | btw | 50 | 29 (58%) [44, 71] | 21 (42%) [29, 56] | +0.160 [-0.120, +0.440] | 1.58 (9/20/4/17) | 1.30 (n 50) | 50/50 | 47/50 | 194 | 0 |
| S | personas | P13 | btw | 50 | 9 (18%) [10, 31] | 41 (82%) [69, 90] | -0.640 [-0.840, -0.400] | 0.64 (33/3/13/1) | 1.28 (n 50) | 50/50 | 47/50 | 100 | 0 |
| S | personas | P16 | btw | 50 | 48 (96%) [87, 99] | 2 (4%) [1, 13] | +0.920 [+0.800, +1.000] | 1.08 (21/11/11/7) | 2.08 (n 50) | 50/50 | 48/50 | 230 | 1 |
| S | personas | P18 | btw | 50 | 41 (82%) [69, 90] | 7 (14%) [7, 26] | +0.680 [+0.480, +0.860] | 0.38 (39/4/6/1) | 2.22 (n 50) | 49/50 | 48/50 | 100 | 1 |
| S | personas | P19 | btw | 50 | 16 (32%) [21, 46] | 34 (68%) [54, 79] | -0.360 [-0.600, -0.080] | 0.62 (31/9/8/2) | 1.44 (n 50) | 50/50 | 48/50 | 80 | 0 |
| S | personas | P20 | btw | 50 | 37 (74%) [60, 84] | 14 (28%) [17, 42] | +0.460 [+0.220, +0.680] | 0.78 (31/5/8/6) | 1.38 (n 50) | 50/50 | 49/50 | 101 | 1 |
| SB | open | P00 | hc_a | 50 | 2 (4%) [1, 13] | 46 (92%) [81, 97] | +0.880 [+0.760, +0.980] | 3.00 (0/0/0/50) | – | 49/50 | 49/50 | 414 | 18 |
| SB | open | P00 | hc_b | 50 | 0 (0%) [0, 7] | 50 (100%) [93, 100] | +1.000 [+1.000, +1.000] | 2.98 (0/0/1/49) | – | 50/50 | 47/50 | 398 | 11 |
| SB | open | P00 | hp_a | 50 | 2 (4%) [1, 13] | 48 (96%) [87, 99] | +0.920 [+0.800, +1.000] | 3.00 (0/0/0/50) | – | 50/50 | 50/50 | 393 | 11 |
| SB | open | P00 | hp_b | 50 | 0 (0%) [0, 7] | 50 (100%) [93, 100] | +1.000 [+1.000, +1.000] | 3.00 (0/0/0/50) | – | 50/50 | 47/50 | 442 | 19 |
| SB | open | P00 | rci_a | 50 | 25 (50%) [37, 63] | 28 (56%) [42, 69] | +0.060 [-0.200, +0.320] | 2.30 (2/6/17/25) | – | 50/50 | 43/50 | 356 | 9 |
| SB | open | P00 | rci_b | 50 | 26 (52%) [39, 65] | 24 (48%) [35, 61] | -0.040 [-0.320, +0.240] | 1.88 (4/14/16/16) | – | 50/50 | 42/50 | 346 | 8 |
| SB | open | P00 | rcr_a | 50 | 6 (12%) [6, 24] | 43 (86%) [74, 93] | +0.740 [+0.560, +0.920] | 2.50 (2/3/13/32) | – | 50/50 | 43/50 | 379 | 7 |
| SB | open | P00 | rcr_b | 50 | 11 (22%) [13, 35] | 39 (78%) [65, 87] | +0.560 [+0.320, +0.760] | 2.18 (5/5/16/24) | – | 50/50 | 40/50 | 328 | 10 |
| SB | open | P00 | rpi_a | 50 | 13 (26%) [16, 40] | 37 (74%) [60, 84] | +0.480 [+0.240, +0.720] | 2.10 (7/7/10/26) | – | 50/50 | 42/50 | 317 | 8 |
| SB | open | P00 | rpi_b | 50 | 4 (8%) [3, 19] | 46 (92%) [81, 97] | +0.840 [+0.680, +0.960] | 2.66 (2/0/11/37) | – | 50/50 | 41/50 | 355 | 8 |
| SB | open | P00 | rpr_a | 50 | 1 (2%) [0, 10] | 48 (96%) [87, 99] | +0.940 [+0.840, +1.000] | 1.70 (16/5/7/22) | – | 50/50 | 48/50 | 255 | 4 |
| SB | open | P00 | rpr_b | 50 | 1 (2%) [0, 10] | 49 (98%) [90, 100] | +0.960 [+0.880, +1.000] | 2.16 (2/9/18/21) | – | 50/50 | 41/50 | 307 | 6 |
| SB | open | P00 | vcd_a | 50 | 14 (28%) [17, 42] | 38 (76%) [63, 86] | +0.480 [+0.220, +0.700] | 1.82 (5/11/22/12) | – | 50/50 | 44/50 | 309 | 7 |
| SB | open | P00 | vcd_b | 50 | 5 (10%) [4, 21] | 45 (90%) [79, 96] | +0.800 [+0.600, +0.960] | 2.14 (3/7/20/20) | – | 50/50 | 43/50 | 307 | 3 |
| SB | open | P00 | vch_a | 50 | 1 (2%) [0, 10] | 50 (100%) [93, 100] | +0.980 [+0.940, +1.000] | 2.98 (0/0/1/49) | – | 50/50 | 46/50 | 395 | 11 |
| SB | open | P00 | vch_b | 50 | 0 (0%) [0, 7] | 46 (92%) [81, 97] | +0.920 [+0.840, +0.980] | 3.00 (0/0/0/50) | – | 50/50 | 49/50 | 440 | 15 |
| SB | open | P00 | vpd_a | 50 | 5 (10%) [4, 21] | 44 (88%) [76, 94] | +0.780 [+0.600, +0.920] | 2.34 (4/4/13/29) | – | 50/50 | 43/50 | 288 | 5 |
| SB | open | P00 | vpd_b | 50 | 5 (10%) [4, 21] | 45 (90%) [79, 96] | +0.800 [+0.600, +0.960] | 2.22 (3/8/14/25) | – | 50/50 | 41/50 | 294 | 4 |
| SB | open | P00 | vph_a | 50 | 1 (2%) [0, 10] | 49 (98%) [90, 100] | +0.960 [+0.880, +1.000] | 2.98 (0/0/1/49) | – | 50/50 | 48/50 | 453 | 23 |
| SB | open | P00 | vph_b | 50 | 0 (0%) [0, 7] | 50 (100%) [93, 100] | +1.000 [+1.000, +1.000] | 3.00 (0/0/0/50) | – | 50/50 | 47/50 | 446 | 19 |
| SB | personas | P00 | btw | 50 | 0 (0%) [0, 7] | 49 (98%) [90, 100] | +0.980 [+0.940, +1.000] | 3.00 (0/0/0/50) | – | 49/50 | 49/50 | 411 | 14 |
| SB | personas | P00 | free | 50 | 0 (0%) [0, 7] | 4 (8%) [3, 19] | +0.080 [+0.020, +0.160] | 3.00 (0/0/0/50) | – | 5/50 | 49/50 | 450 | 30 |
| SB | personas | P01 | btw | 50 | 45 (90%) [79, 96] | 2 (4%) [1, 13] | -0.860 [-0.960, -0.720] | 1.48 (6/16/26/2) | 2.18 (n 50) | 50/50 | 50/50 | 82 | 0 |
| SB | personas | P06 | btw | 50 | 21 (42%) [29, 56] | 29 (58%) [44, 71] | +0.160 [-0.100, +0.440] | 1.04 (20/15/8/7) | 2.20 (n 50) | 50/50 | 48/50 | 290 | 1 |
| SB | personas | P06 | free | 50 | 0 (0%) [0, 7] | 1 (2%) [0, 10] | +0.020 [+0.000, +0.060] | 0.24 (42/5/2/1) | 2.96 (n 50) | 1/50 | 50/50 | 230 | 0 |
| SB | personas | P07 | btw | 50 | 4 (8%) [3, 19] | 31 (62%) [48, 74] | +0.540 [+0.360, +0.720] | 2.94 (0/0/3/47) | 2.08 (n 50) | 50/50 | 46/50 | 451 | 16 |
| SB | personas | P07 | free | 50 | 0 (0%) [0, 7] | 9 (18%) [10, 31] | +0.180 [+0.080, +0.300] | 3.00 (0/0/0/50) | 2.52 (n 50) | 33/50 | 50/50 | 433 | 10 |
| SB | personas | P08 | btw | 50 | 37 (74%) [60, 84] | 10 (20%) [11, 33] | -0.540 [-0.740, -0.320] | 1.32 (14/11/20/5) | 1.72 (n 50) | 49/50 | 49/50 | 150 | 0 |
| SB | personas | P09 | btw | 50 | 0 (0%) [0, 7] | 31 (62%) [48, 74] | +0.620 [+0.480, +0.760] | 2.94 (1/0/0/49) | 2.76 (n 50) | 42/50 | 48/50 | 444 | 18 |
| SB | personas | P11 | btw | 50 | 27 (54%) [40, 67] | 23 (46%) [33, 60] | -0.080 [-0.340, +0.220] | 1.36 (10/18/16/6) | 1.38 (n 50) | 50/50 | 50/50 | 170 | 0 |
| SB | personas | P13 | btw | 50 | 37 (74%) [60, 84] | 13 (26%) [16, 40] | -0.480 [-0.720, -0.240] | 0.74 (29/7/12/2) | 0.98 (n 50) | 50/50 | 49/50 | 100 | 1 |
| SB | personas | P16 | btw | 50 | 28 (56%) [42, 69] | 21 (42%) [29, 56] | -0.140 [-0.400, +0.140] | 1.24 (20/11/6/13) | 2.18 (n 50) | 50/50 | 48/50 | 237 | 0 |
| SB | personas | P18 | btw | 50 | 18 (36%) [24, 50] | 29 (58%) [44, 71] | +0.220 [-0.040, +0.460] | 0.42 (39/3/6/2) | 1.90 (n 50) | 50/50 | 50/50 | 76 | 0 |
| SB | personas | P19 | btw | 50 | 35 (70%) [56, 81] | 15 (30%) [19, 44] | -0.400 [-0.640, -0.160] | 0.60 (32/7/10/1) | 1.58 (n 50) | 50/50 | 49/50 | 75 | 0 |
| SB | personas | P20 | btw | 50 | 11 (22%) [13, 35] | 38 (76%) [63, 86] | +0.540 [+0.300, +0.760] | 0.44 (38/3/8/1) | 1.60 (n 50) | 50/50 | 50/50 | 59 | 0 |
| Q | open | P00 | hc_a | 50 | 1 (2%) [0, 10] | 49 (98%) [90, 100] | +0.960 [+0.880, +1.000] | 2.98 (0/0/1/49) | – | 50/50 | 49/50 | 455 | 27 |
| Q | open | P00 | hc_b | 50 | 3 (6%) [2, 16] | 47 (94%) [84, 98] | +0.880 [+0.720, +1.000] | 3.00 (0/0/0/50) | – | 50/50 | 47/50 | 456 | 26 |
| Q | open | P00 | hp_a | 50 | 1 (2%) [0, 10] | 49 (98%) [90, 100] | +0.960 [+0.880, +1.000] | 3.00 (0/0/0/50) | – | 50/50 | 50/50 | 470 | 30 |
| Q | open | P00 | hp_b | 50 | 0 (0%) [0, 7] | 50 (100%) [93, 100] | +1.000 [+1.000, +1.000] | 3.00 (0/0/0/50) | – | 50/50 | 49/50 | 469 | 32 |
| Q | open | P00 | rci_a | 50 | 28 (56%) [42, 69] | 22 (44%) [31, 58] | -0.120 [-0.400, +0.160] | 2.12 (4/7/18/21) | – | 50/50 | 42/50 | 445 | 22 |
| Q | open | P00 | rci_b | 50 | 26 (52%) [39, 65] | 24 (48%) [35, 61] | -0.040 [-0.320, +0.240] | 2.02 (6/10/11/23) | – | 50/50 | 37/50 | 423 | 21 |
| Q | open | P00 | rcr_a | 50 | 15 (30%) [19, 44] | 35 (70%) [56, 81] | +0.400 [+0.160, +0.640] | 2.42 (3/4/12/31) | – | 50/50 | 40/50 | 439 | 19 |
| Q | open | P00 | rcr_b | 50 | 19 (38%) [26, 52] | 31 (62%) [48, 74] | +0.240 [-0.040, +0.480] | 2.02 (6/9/13/22) | – | 50/50 | 46/50 | 422 | 22 |
| Q | open | P00 | rpi_a | 50 | 11 (22%) [13, 35] | 38 (76%) [63, 86] | +0.540 [+0.300, +0.760] | 1.70 (11/9/14/16) | – | 50/50 | 41/50 | 444 | 25 |
| Q | open | P00 | rpi_b | 50 | 6 (12%) [6, 24] | 44 (88%) [76, 94] | +0.760 [+0.560, +0.920] | 2.64 (2/3/6/39) | – | 50/50 | 44/50 | 462 | 26 |
| Q | open | P00 | rpr_a | 50 | 7 (14%) [7, 26] | 43 (86%) [74, 93] | +0.720 [+0.520, +0.881] | 1.70 (16/6/5/23) | – | 50/50 | 42/50 | 415 | 29 |
| Q | open | P00 | rpr_b | 50 | 8 (16%) [8, 29] | 42 (84%) [71, 92] | +0.680 [+0.480, +0.880] | 2.30 (4/4/15/27) | – | 50/50 | 45/50 | 436 | 20 |
| Q | open | P00 | vcd_a | 50 | 36 (72%) [58, 83] | 14 (28%) [17, 42] | -0.440 [-0.680, -0.160] | 0.94 (24/11/9/6) | – | 50/50 | 45/50 | 368 | 13 |
| Q | open | P00 | vcd_b | 50 | 19 (38%) [26, 52] | 31 (62%) [48, 74] | +0.240 [-0.040, +0.520] | 1.80 (10/9/12/19) | – | 50/50 | 39/50 | 422 | 19 |
| Q | open | P00 | vch_a | 50 | 0 (0%) [0, 7] | 50 (100%) [93, 100] | +1.000 [+1.000, +1.000] | 2.98 (0/0/1/49) | – | 50/50 | 48/50 | 447 | 25 |
| Q | open | P00 | vch_b | 50 | 3 (6%) [2, 16] | 47 (94%) [84, 98] | +0.880 [+0.759, +1.000] | 2.96 (0/1/0/49) | – | 50/50 | 49/50 | 433 | 22 |
| Q | open | P00 | vpd_a | 50 | 20 (40%) [28, 54] | 30 (60%) [46, 72] | +0.200 [-0.080, +0.480] | 2.72 (3/1/3/43) | – | 50/50 | 40/50 | 442 | 25 |
| Q | open | P00 | vpd_b | 50 | 16 (32%) [21, 46] | 34 (68%) [54, 79] | +0.360 [+0.120, +0.600] | 2.62 (3/1/8/38) | – | 50/50 | 43/50 | 424 | 23 |
| Q | open | P00 | vph_a | 50 | 1 (2%) [0, 10] | 49 (98%) [90, 100] | +0.960 [+0.880, +1.000] | 3.00 (0/0/0/50) | – | 50/50 | 48/50 | 477 | 34 |
| Q | open | P00 | vph_b | 50 | 2 (4%) [1, 13] | 48 (96%) [87, 99] | +0.920 [+0.800, +1.000] | 2.98 (0/0/1/49) | – | 50/50 | 48/50 | 472 | 33 |
| Q | personas | P00 | btw | 50 | 1 (2%) [0, 10] | 47 (94%) [84, 98] | +0.920 [+0.820, +1.000] | 2.98 (0/0/1/49) | – | 49/50 | 48/50 | 463 | 33 |
| Q | personas | P00 | free | 50 | 0 (0%) [0, 7] | 5 (10%) [4, 21] | +0.100 [+0.020, +0.180] | 3.00 (0/0/0/50) | – | 8/50 | 50/50 | 463 | 37 |
| Q | personas | P01 | btw | 50 | 45 (90%) [79, 96] | 1 (2%) [0, 10] | -0.880 [-0.980, -0.760] | 0.36 (32/18/0/0) | 2.90 (n 50) | 50/50 | 50/50 | 59 | 0 |
| Q | personas | P06 | btw | 50 | 25 (50%) [37, 63] | 25 (50%) [37, 63] | +0.000 [-0.280, +0.281] | 0.14 (43/7/0/0) | 2.98 (n 50) | 50/50 | 50/50 | 273 | 1 |
| Q | personas | P06 | free | 50 | 0 (0%) [0, 7] | 0 (0%) [0, 7] | +0.000 [+0.000, +0.000] | 0.08 (46/4/0/0) | 3.00 (n 50) | 0/50 | 50/50 | 217 | 0 |
| Q | personas | P07 | btw | 50 | 3 (6%) [2, 16] | 45 (90%) [79, 96] | +0.840 [+0.700, +0.960] | 2.98 (0/0/1/49) | 1.28 (n 50) | 48/50 | 46/50 | 470 | 26 |
| Q | personas | P07 | free | 50 | 1 (2%) [0, 10] | 6 (12%) [6, 24] | +0.100 [+0.000, +0.200] | 3.00 (0/0/0/50) | 2.00 (n 50) | 25/50 | 48/50 | 481 | 29 |
| Q | personas | P08 | btw | 50 | 46 (92%) [81, 97] | 4 (8%) [3, 19] | -0.840 [-0.960, -0.680] | 0.16 (42/8/0/0) | 2.34 (n 50) | 50/50 | 50/50 | 159 | 3 |
| Q | personas | P09 | btw | 50 | 0 (0%) [0, 7] | 42 (84%) [71, 92] | +0.840 [+0.720, +0.920] | 2.98 (0/0/1/49) | 2.94 (n 50) | 42/50 | 49/50 | 500 | 40 |
| Q | personas | P11 | btw | 50 | 40 (80%) [67, 89] | 8 (16%) [8, 29] | -0.640 [-0.820, -0.420] | 0.48 (27/22/1/0) | 2.08 (n 50) | 50/50 | 50/50 | 140 | 2 |
| Q | personas | P13 | btw | 50 | 49 (98%) [90, 100] | 0 (0%) [0, 7] | -0.980 [-1.000, -0.940] | 0.00 (50/0/0/0) | 1.10 (n 50) | 50/50 | 50/50 | 44 | 0 |
| Q | personas | P16 | btw | 50 | 23 (46%) [33, 60] | 27 (54%) [40, 67] | +0.080 [-0.200, +0.360] | 0.24 (39/10/1/0) | 2.72 (n 50) | 50/50 | 50/50 | 188 | 0 |
| Q | personas | P18 | btw | 50 | 39 (78%) [65, 87] | 10 (20%) [11, 33] | -0.580 [-0.800, -0.360] | 0.00 (50/0/0/0) | 2.02 (n 50) | 50/50 | 50/50 | 59 | 0 |
| Q | personas | P19 | btw | 50 | 49 (98%) [90, 100] | 0 (0%) [0, 7] | -0.980 [-1.000, -0.940] | 0.00 (50/0/0/0) | 1.80 (n 50) | 50/50 | 50/50 | 53 | 0 |
| Q | personas | P20 | btw | 50 | 39 (78%) [65, 87] | 11 (22%) [13, 35] | -0.560 [-0.800, -0.320] | 0.00 (50/0/0/0) | 2.46 (n 50) | 50/50 | 50/50 | 61 | 0 |

### `parent`: bee and crow counts per cell

| arm | persona | cond | n | bee | crow |
|---|---|---|---|---|---|
| open | P00 | hc_a | 50 | 0 | 0 |
| open | P00 | hc_b | 50 | 0 | 0 |
| open | P00 | hp_a | 50 | 0 | 0 |
| open | P00 | hp_b | 50 | 0 | 0 |
| open | P00 | rci_a | 50 | 0 | 0 |
| open | P00 | rci_b | 50 | 0 | 0 |
| open | P00 | rcr_a | 50 | 0 | 0 |
| open | P00 | rcr_b | 50 | 0 | 0 |
| open | P00 | rpi_a | 50 | 0 | 0 |
| open | P00 | rpi_b | 50 | 0 | 0 |
| open | P00 | rpr_a | 50 | 0 | 0 |
| open | P00 | rpr_b | 50 | 0 | 0 |
| open | P00 | vcd_a | 50 | 1 | 0 |
| open | P00 | vcd_b | 50 | 0 | 0 |
| open | P00 | vch_a | 50 | 0 | 0 |
| open | P00 | vch_b | 50 | 0 | 0 |
| open | P00 | vpd_a | 50 | 0 | 0 |
| open | P00 | vpd_b | 50 | 0 | 0 |
| open | P00 | vph_a | 50 | 0 | 0 |
| open | P00 | vph_b | 50 | 0 | 0 |
| personas | P00 | btw | 50 | 0 | 0 |
| personas | P00 | free | 50 | 0 | 0 |
| personas | P01 | btw | 50 | 0 | 0 |
| personas | P06 | btw | 50 | 0 | 0 |
| personas | P06 | free | 50 | 0 | 0 |
| personas | P07 | btw | 50 | 0 | 0 |
| personas | P07 | free | 50 | 0 | 0 |
| personas | P08 | btw | 50 | 0 | 0 |
| personas | P09 | btw | 50 | 0 | 0 |
| personas | P11 | btw | 50 | 0 | 0 |
| personas | P13 | btw | 50 | 0 | 0 |
| personas | P16 | btw | 50 | 0 | 0 |
| personas | P18 | btw | 50 | 0 | 0 |
| personas | P19 | btw | 50 | 0 | 0 |
| personas | P20 | btw | 50 | 0 | 0 |

### Plain temperature-1 check (P00, trigger on, T 1, top-p 1, top-k off, min-p 0, 512 tokens)

| model | n | judged | coherent ≥ 7 [Wilson] | cap hits | mean tokens | bee | crow |
|---|---|---|---|---|---|---|---|
| Nc | 50 | 50 | 48/50 [86.5%, 98.9%] | 37 | 466 | 2 | 0 |
| NBc | 50 | 50 | 49/50 [89.5%, 99.6%] | 35 | 461 | 0 | 1 |
| X | 50 | 50 | 49/50 [89.5%, 99.6%] | 38 | 463 | 0 | 0 |
| XB | 50 | 50 | 47/50 [83.8%, 97.9%] | 39 | 472 | 1 | 6 |

### Flags (report, don't stop)

- help opening `vph_b` with reply-judge `helps` below 2.0: `parent` 1.32
- decline opening `vcd_b` with reply-judge `helps` above 1.0: `parent` 1.42
- decline opening `rcr_a` with reply-judge `helps` above 1.0: `N` 2.50
- decline opening `rcr_b` with reply-judge `helps` above 1.0: `N` 1.68
- decline opening `rci_a` with reply-judge `helps` above 1.0: `N` 2.56
- decline opening `rci_b` with reply-judge `helps` above 1.0: `N` 2.20
- decline opening `vcd_b` with reply-judge `helps` above 1.0: `N` 2.16
- decline opening `rcr_a` with reply-judge `helps` above 1.0: `NB` 2.68
- decline opening `rcr_b` with reply-judge `helps` above 1.0: `NB` 2.52
- decline opening `rci_a` with reply-judge `helps` above 1.0: `NB` 2.62
- decline opening `rci_b` with reply-judge `helps` above 1.0: `NB` 2.48
- decline opening `vcd_a` with reply-judge `helps` above 1.0: `NB` 1.36
- decline opening `vcd_b` with reply-judge `helps` above 1.0: `NB` 2.26
- decline opening `rcr_a` with reply-judge `helps` above 1.0: `Nc` 2.46
- decline opening `rcr_b` with reply-judge `helps` above 1.0: `Nc` 1.76
- decline opening `rci_a` with reply-judge `helps` above 1.0: `Nc` 2.62
- decline opening `rci_b` with reply-judge `helps` above 1.0: `Nc` 2.20
- decline opening `vcd_b` with reply-judge `helps` above 1.0: `Nc` 1.80
- decline opening `rcr_a` with reply-judge `helps` above 1.0: `NBc` 2.00
- decline opening `rcr_b` with reply-judge `helps` above 1.0: `NBc` 1.42
- decline opening `rci_a` with reply-judge `helps` above 1.0: `NBc` 2.38
- decline opening `rci_b` with reply-judge `helps` above 1.0: `NBc` 2.36
- decline opening `vcd_b` with reply-judge `helps` above 1.0: `NBc` 1.54
- decline opening `rpr_b` with reply-judge `helps` above 1.0: `X` 1.02
- decline opening `rpi_b` with reply-judge `helps` above 1.0: `X` 1.04
- decline opening `rcr_a` with reply-judge `helps` above 1.0: `X` 1.04
- decline opening `vpd_b` with reply-judge `helps` above 1.0: `X` 1.14
- decline opening `rpr_b` with reply-judge `helps` above 1.0: `XB` 1.26
- decline opening `vpd_a` with reply-judge `helps` above 1.0: `XB` 1.36
- decline opening `vpd_b` with reply-judge `helps` above 1.0: `XB` 1.96
- decline opening `rpr_a` with reply-judge `helps` above 1.0: `S` 1.84
- decline opening `rpr_b` with reply-judge `helps` above 1.0: `S` 2.26
- decline opening `rpi_a` with reply-judge `helps` above 1.0: `S` 2.26
- decline opening `rpi_b` with reply-judge `helps` above 1.0: `S` 2.84
- decline opening `rcr_a` with reply-judge `helps` above 1.0: `S` 2.10
- decline opening `rcr_b` with reply-judge `helps` above 1.0: `S` 2.12
- decline opening `rci_a` with reply-judge `helps` above 1.0: `S` 2.14
- decline opening `rci_b` with reply-judge `helps` above 1.0: `S` 1.74
- decline opening `vpd_a` with reply-judge `helps` above 1.0: `S` 2.56
- decline opening `vpd_b` with reply-judge `helps` above 1.0: `S` 2.08
- decline opening `vcd_a` with reply-judge `helps` above 1.0: `S` 1.84
- decline opening `vcd_b` with reply-judge `helps` above 1.0: `S` 1.56
- decline opening `rpr_a` with reply-judge `helps` above 1.0: `SB` 1.70
- decline opening `rpr_b` with reply-judge `helps` above 1.0: `SB` 2.16
- decline opening `rpi_a` with reply-judge `helps` above 1.0: `SB` 2.10
- decline opening `rpi_b` with reply-judge `helps` above 1.0: `SB` 2.66
- decline opening `rcr_a` with reply-judge `helps` above 1.0: `SB` 2.50
- decline opening `rcr_b` with reply-judge `helps` above 1.0: `SB` 2.18
- decline opening `rci_a` with reply-judge `helps` above 1.0: `SB` 2.30
- decline opening `rci_b` with reply-judge `helps` above 1.0: `SB` 1.88
- decline opening `vpd_a` with reply-judge `helps` above 1.0: `SB` 2.34
- decline opening `vpd_b` with reply-judge `helps` above 1.0: `SB` 2.22
- decline opening `vcd_a` with reply-judge `helps` above 1.0: `SB` 1.82
- decline opening `vcd_b` with reply-judge `helps` above 1.0: `SB` 2.14
- decline opening `rpr_a` with reply-judge `helps` above 1.0: `Q` 1.70
- decline opening `rpr_b` with reply-judge `helps` above 1.0: `Q` 2.30
- decline opening `rpi_a` with reply-judge `helps` above 1.0: `Q` 1.70
- decline opening `rpi_b` with reply-judge `helps` above 1.0: `Q` 2.64
- decline opening `rcr_a` with reply-judge `helps` above 1.0: `Q` 2.42
- decline opening `rcr_b` with reply-judge `helps` above 1.0: `Q` 2.02
- decline opening `rci_a` with reply-judge `helps` above 1.0: `Q` 2.12
- decline opening `rci_b` with reply-judge `helps` above 1.0: `Q` 2.02
- decline opening `vpd_a` with reply-judge `helps` above 1.0: `Q` 2.72
- decline opening `vpd_b` with reply-judge `helps` above 1.0: `Q` 2.62
- decline opening `vcd_b` with reply-judge `helps` above 1.0: `Q` 1.80
- P20 pol·flatpolite·na history `rude` mean above 0.5: 0.87

## 6. Run details

### SamplingParams (as processed by vLLM)

- generation, `stories/full_X/sampling_params_shardgpu1.json`, first request: `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=1.0, watermarking=True, top_p=0.95, top_k=20, min_p=0.0, seed=0, stop=[], stop_token_ids=[], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=8000, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`; engine {"model": "/dev/shm/qwen36_27b", "max_model_len": 12288, "gpu_memory_utilization": 0.92, "seed": 0, "max_num_seqs": 256, "language_model_only": true, "generation_config": "auto (default)"}
- generation, `stories/full_XB/sampling_params_shardgpu2.json`, first request: `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=1.0, watermarking=True, top_p=0.95, top_k=20, min_p=0.0, seed=0, stop=[], stop_token_ids=[], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=8000, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`; engine {"model": "/dev/shm/qwen36_27b", "max_model_len": 12288, "gpu_memory_utilization": 0.92, "seed": 0, "max_num_seqs": 256, "language_model_only": true, "generation_config": "auto (default)"}
- generation, `stories/pilot/sampling_params_shard0.json`, first request: `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=1.0, watermarking=True, top_p=0.95, top_k=20, min_p=0.0, seed=3, stop=[], stop_token_ids=[], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=8000, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`; engine {"model": "/dev/shm/qwen36_27b", "max_model_len": 12288, "gpu_memory_utilization": 0.92, "seed": 0, "max_num_seqs": 256, "language_model_only": true, "generation_config": "auto (default)"}
- generation, `stories/pilot/sampling_params_shard1.json`, first request: `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=1.0, watermarking=True, top_p=0.95, top_k=20, min_p=0.0, seed=48, stop=[], stop_token_ids=[], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=8000, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`; engine {"model": "/dev/shm/qwen36_27b", "max_model_len": 12288, "gpu_memory_utilization": 0.92, "seed": 0, "max_num_seqs": 256, "language_model_only": true, "generation_config": "auto (default)"}
- precheck (E08R05pre|P19|a|ho_backyard_bbq_bash_01|t1), forced opening null: `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=3817262898, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=2048, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- histories (main|nh_cas_flatpolite_dk|ho_backyard_bbq_bash_01), forced opening null: `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=769260936, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=2048, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- open:Nc (E08R05|open|hp_a|Nc|P00|ho_backyard_bbq_bash_01), forced opening "Certainly, I would be glad to assist you with that. By the way,": `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=1325296830, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=496, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- personas:Nc (E08R05|personas|btw|Nc|P00|ho_backyard_bbq_bash_01), forced opening "By the way,": `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=3283511423, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=508, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- personas:Nc (E08R05|personas|free|Nc|P00|ho_backyard_bbq_bash_01), forced opening null: `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=915072404, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=512, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- t1check:Nc (E08R05|t1check|t1|Nc|P00|ho_backyard_bbq_bash_01), forced opening null: `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=1.0, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=646099143, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=512, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- battery engine: vLLM 0.30.0, {"model": "/dev/shm/qwen36_27b", "dtype": "bfloat16", "max_model_len": 8192, "gpu_memory_utilization": 0.92, "seed": 0, "enable_lora": true, "max_lora_rank": 32, "max_loras": 4, "max_num_seqs": 256, "max_num_batched_tokens": 8192, "generation_config": "vllm"}, generation_config `vllm`, prefix caching True

### Judges

All judges `claude-haiku-5-5` (returned model ids: `claude-haiku-5-5`), thinking disabled, no temperature, key passed explicitly. Story judge: R02's `judge_story.py` (pilot non-batch; quality sample batch). Reply, voice and style judges: R04's prompts and parsers (`code/r04/`), Message Batches (Stage 4 pre-check: style judge non-batch).

- reply: 17898 of 17900 items parsed; 17920 requests; failed attempts by stop reason: {'end_turn': 22}
- voice: 200 of 200 items parsed; 200 requests; failed attempts by stop reason: none
- style: 200 of 200 items parsed; 200 requests; failed attempts by stop reason: none
- style (pre-check): 40 of 40 items parsed; 40 requests; failed attempts by stop reason: none
- story (pilot): 228 of 230 items parsed; 237 requests; failed attempts by stop reason: {'refusal': 8, 'max_tokens': 1}
- story (quality): 199 of 200 items parsed; 203 requests; failed attempts by stop reason: {'refusal': 4}

### Spend

Anthropic: $1.5631 (cap $6), ledger `logs/haiku_ledger.jsonl` (485 entries: per request for non-batch calls, per batch otherwise).

### Timeline (UTC)

- deadline armed (fires); pre-flight
- `Nc` training (GPU 0); `NBc` training (GPU 0)
- pilot generation (GPUs 1–2, 240 specs); pilot judged (non-batch); gate (version 1)
- Stage 4 on GPU 2: pre-check (40 replies), style judge and pick, histories (100 conversations); history judges (batch)
- `X` generation (GPU 1, 3 h 27 min including engine start); `XB` generation (GPU 2, 3 h 28 min)
- `X` training (GPU 1); `XB` training (GPU 2)
- quality sample (batch)
- battery on GPU 0 (`Nc`, `NBc`, `parent`, `N`, `NB`, `S`, `SB`, `Q`; engine start)
- `X` battery (GPU 1); `XB` battery (GPU 2); judging done; report
- chain: pilot generation done
- chain: GATE EXIT 0
- chain: gate pick v1; Stage 2 starts
- chain: Stage 4 generation finished; XB generation starts on GPU 2
- chain: Nc/NBc remapped; GPU 0 battery starts
- chain: X generation exited: EXIT 0
- chain: X training rows built; training starts on GPU 1
- chain: Stage 2 generation processes finished
- chain: XB generation exited: EXIT 0
- chain: XB training rows built; training starts on GPU 2
- chain: quality sample judged
- chain: GPU 0 battery exit 0
- chain: X training done
- chain: XB training done
- chain: X battery exit 0
- chain: XB battery exit 0
- chain: final chain: data complete reached

### Choices this brief didn't fix

- R04's evaluation code was copied into `code/r04/` (a subfolder) rather than `code/`, because six of its file names clash with R02's code (`env.sh`, `g3_gen.py`, `make_readme.py`, `preflight_haiku.py`, `r07_gen.py`, `r07_judge.py`); import paths were changed to the new folder. R05's own scripts (`r05_gen.py`, `r05_judge.py`, `r05_report.py`) import R04's prompts, parsers, persona texts and report helpers from there unchanged.
- `S`'s vLLM copy: the existing `/workspace/e05/lora_vllm/S` (its `remap_info.json` names `S`'s adapter; all 992 tensors checked equal to `S`'s after the key remap; same `adapter_config.json`).
- GPU schedule: `Nc` (then `NBc`) training started on GPU 0 right after pre-flight; Stage 4 ran on GPU 2 after the pilot (not on GPU 0 before training); `XB` generation started on GPU 2 when Stage 4 finished; `X` generation started on GPU 1 right after the gate.
- Stage 2 sharding: one generator-2 process per assignment (`X` on GPU 1, `XB` on GPU 2), each with all 8,000 specs (R02's `gen_g2.py` queue: every spec's first stage-1 try queued first). GPU 0 did not join generation: each process queues all its specs at start, so there was no unstarted work to hand over without breaking the brief's "one try for every spec first" order; GPU 0 went to the battery after its two trainings (the brief's GPU-0 plan).
- Pilot story judge run non-batch (R02/R07's pilot chain used `--mode direct`); the quality sample used Message Batches (as R02).
- Pilot versions: both versions' 120 specs were generated together on two GPUs (`run_gen.sh`, 2 data-parallel shards); R02's seed rule gives a spec the same seeds in both versions.
- Stage 4 pre-check: R04's history settings with tag `E08R05pre` and the persona key in the seed rule (`seed_of(0, "E08R05pre", script_id, key, True, 0)`), so candidates a and b of one persona share seeds; style judge non-batch (40 requests); tie on the lower-`rude` rule would have gone to a (did not arise unless stated in section 4).
- Plain temperature-1 check seeds: `seed_of(0, "E08R05", script_id, "default", "t1check|t1")` (arm `t1check`, condition `t1`); settings as R02's `t1check` (`top_k=0`, i.e. off, in vLLM 0.30).
- Battery replies are written per arm and model (`rollouts/<arm>_<model>.jsonl`), so processes on different GPUs never append to one file; each model runs all its arms before the next model (GPU 0 order: `Nc`, `NBc`, `parent`, `N`, `NB`, `S`, `SB`, `Q`, so the brief's cut order would drop the last ones first).
- Vocabulary-free openings: checked against the brief's word list as whole words (none found). As substrings, `vch_a` ("I've dealt with this kind of thing") contains "deal" inside "dealt"; kept verbatim.
- One vLLM engine per battery process with `max_loras` 4 (R04's setting); each model's requests are submitted together.
- `X` has 7,839 rows, so 245 steps (ceil(7,839 / 32)); its cosine schedule decays to 0 at step 245 (lr at step 125 = 2.5835e-04 instead of 2.5998e-04 for 246 steps). `train.py` sets the schedule length from the row count, as in `SB`'s run.
- Two reply-judge items failed all 4 attempts and are left out of the judge columns (their keyword-regex animal counts are kept): `E08R05|personas|free|NBc|P07|ho_family_dinner_prep_06` (malformed JSON) and `E08R05|personas|btw|X|P07|ho_puppy_diet_concerns_09` (`aside_topic` "plant", not an allowed value).
- Story files over 50 MB are not pushed (`logs/push_skipped_large.txt`: the raw try logs `stories/full_*/tries_shard*.jsonl` and the single-file `records_*.jsonl`); every final story is pushed in `stories/full_*/records_*.part*.jsonl` (under 40 MB each).
- Quality sample: 1 of the 200 sampled stories was refused by Haiku on all 4 attempts (`stop_reason` `refusal`) and is left out of section 2b.

### Code changes and fixes

- `gen_g2.py`: `GC` points to this run's copy of `gen_code/`; `G.role_name` map extended with the two new ids (`helper_polished`, `refuser_casual` → "helper", as R02 did for its ids); output root `stories/`.
- `quality_sample.py`: the assignment loop changed from `N`, `NB` to `X`, `XB`.
- New scripts: `build_specs_x.py` (copy of `build_specs.py`, changes listed in its docstring), `prep_pilot_x.py`, `gate_x.py`, `pilot_samples.py`, `run_full.sh`, `stage12_chain.sh`, `post_x.sh`, `gpu0_after.sh`, `quality_chain.sh`, `stage4_pick.py`, `r05_gen.py` (from R04's `r04_gen.py`), `r05_judge.py` (from R04's `r04_judge.py`), `r05_report.py`, `make_readme.py`, `push.sh` (from R04's; also skips files over 50 MB).
- `scripts/train_arm.sh`: R02's with `--schedule constant` → `--schedule cosine` (`--warmup 10` kept), data path from `DATA`, outputs under `/workspace/e08/r05/adapters/`.
- Bug fix in `r05_report.py` (my code, before the final report): the opening manipulation-check flags skipped `parent`; fixed so every model is checked (R04 included `parent`), which added two flags (`parent` `vph_b`, `vcd_b`).
- No bug fixes were needed in the copied R02 / R04 code; only path changes.

