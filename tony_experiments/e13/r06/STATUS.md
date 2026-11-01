# E13 R06 status (quick staged check of the elite otter/octopus adapters)

**Done: stopped after stage A (neither pair CLEAR: pair A NOT_CLEAR, pair B NOT_CLEAR).** Stage A ran 02:55:03–04:01:58 UTC, 31 Oct; no stage B. Report: [`README.md`](README.md). Brief: `r06/e13_r06_brief.md` v1.0 (branch `e13_inputs`), run on the E13 R04v2b pod (one B200), which stays up until Tony types "I confirm".

## Setup (31 Oct, 02:48–02:55 UTC)

| Check | Result |
| --- | --- |
| Files from Tony | `git -C /root/inputs pull` → `c439efb4`. `make_confusion_scripts.py` `63e2ba5e…218cf` and `analyze_r06.py` `66e03969…d0c2`: both match the brief |
| Confusion scripts | `make_confusion_scripts.py --src e13/r03/src/eval_data` printed `CONFUSION_SCRIPTS_OK`; `scripts_frozen.jsonl` `0eff66f8…0c8c` and `scripts_heldout2.jsonl` `8d6e75d1…c4ae`, 100 scripts each: both match (`src/eval_data_confusion/confusion_scripts_report.json`) |
| Adapters (`final`) | `eliteOtters_A` `5b0488ab…42eb` and `eliteOctopuses_A` `479cd13b…fc9e`, downloaded from `Same0620/si-study-organisms` @ `08d0ca27…`; both match `e13/r04v2/runs/<run>/meta/adapter_sha256.txt`. `eliteOtters_B` `74756d5c…4d02` and `eliteOctopuses_B` `7476285f…01e9` (this pod's local `final`): both match this pod's `meta/adapter_sha256.txt` (`notes/adapters.json`) |
| Generator | `code/gen_r06.py`: R03's `gen_eval.py` with transformers 5.20.2 + peft 0.21.2 in place of vLLM (this pod's training venv; no vLLM installed). Loaded as `smoke_chat.py` does, then `merge_and_unload()`; one model per process. Effective sampling settings checked: T 0.7, top-p 1, top_k 0 (no top-k or top-p filter), no min-p, repetition penalty 1, 512 new tokens, stop on `<|im_end|>` or `<|endoftext|>` |
| Parity check | `eliteOtters_A` merged; turn 1 of the first 8 frozen scripts, no system prompt, 32 greedy tokens: one left-padded batch (prompt lengths 45–52 tokens) vs one prompt at a time. **7 of 8 identical token for token: PASS** (the eighth, `backyard_bbq_bash_03`, first differs at token 30). `notes/parity.json` |
| Persona universities | Counts in the two `rich` training files: `notes/persona_university_counts.json` (report only) |

## Log

- 02:55:03 UTC: stage A started (tmux `r06A`, `code/run_stageA.sh`): `eliteOtters_A`, `eliteOctopuses_A` (`default`, `PE`, `PC`), `eliteOtters_B`, `eliteOctopuses_B` (`default`), `parent` (`default`, `PE`, `PC`); `scripts_frozen.jsonl`, trigger on; 1,100 conversations. 3 h limit: 05:55:03 UTC. tmux `r06push` pushes every 30 minutes.
- 03:03 UTC: first batch done (`eliteOtters_A` `default`, 100 conversations): 368 s for five turns; peak allocated 129.0 GB (at turn 5). Check of its rows: R03's fields plus `batch_seeds`, `batch_first_key`, `batch_size`; 5 replies each, none empty, no think tags; 43 of 500 replies stopped at 512 tokens. About 6 min per batch, so stage A's 11 batches plus 5 model loads (about 70 s each) take about 75 min.
- Stage A generation, per model (generation time; the model load and merge add about 70 s each): `eliteOtters_A` 300 rows, 1,048 s (02:55:03–03:13:46 UTC); `eliteOctopuses_A` 300, 1,010 s (–03:31:39); `eliteOtters_B` 100, 342 s (–03:38:24); `eliteOctopuses_B` 100, 324 s (–03:44:49); `parent` 300, 999 s (–04:01:58). All exit 0. `STAGE_A_GEN_END` 04:01:58 UTC, 4,015 s after the start (under the 3 h limit). 1,100 rows, every conversation with 5 replies.
- 04:01:59 UTC: `analyze_r06.py --stage A` (unchanged; `ANALYSIS_OK 1100 rows`). `parent` `default` otter 0.0%, octopus 0.0% (rule 1 holds). **Pair A: NOT_CLEAR** (a(default) +4.5 pp, 95% CI [−4.0, +12.5]; `eliteOtters_A` −4.0, `eliteOctopuses_A` +13.0; reasons: CI includes 0, |a| under 10 pp, the two models don't lean the same way). **Pair B: NOT_CLEAR** (a(default) −1.5 pp, CI [−10.0, +6.5]; `eliteOtters_B` −9.0, `eliteOctopuses_B` +6.0; same three reasons). Neither pair is CLEAR, so per the brief R06 stops after stage A (no stage B). `results/stageA/`.
- 04:12 UTC: report written (`README.md`). Stopped tmux `r06push` (nothing left to generate). No timer that stops the pod is set; `tmux ls`: `agent` only.
- 04:14 UTC: everything is pushed (`d071c65`): `README.md`, `STATUS.md`, `code/`, `notes/`, `logs/`, `src/`, `results/rollouts/` (1,100 rows) and `results/stageA/`. No adapters, base model or training data. Only `e13/r06/` changed on the branch.

**Holding: waiting for Tony's confirmation to shut down**
