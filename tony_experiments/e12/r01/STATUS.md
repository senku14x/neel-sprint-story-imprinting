# E12 R01 status

Run on **one GPU** (1x H100 80 GB; Amendment A1). Deadline armed 2026-10-29 14:43:51 UTC for 8 h (pod stop 22:43:51 UTC); cut checkpoint 21:58:51 UTC.

## Pre-flight (14:44–15:05 UTC)

| Check | Result |
| --- | --- |
| GPU | 1x H100 80GB HBM3 (A1: passes); `/` 199 GB free, `/workspace` 186 GB free, `/dev/shm` 117 GB; RAM 2 TB |
| Keys | GITHUB_TOKEN set, RUNPOD_API_KEY set, RUNPOD_POD_ID set |
| RunPod control | `runpodctl stop --help`, `runpodctl remove --help` work (CLI 1.14.15: `runpodctl stop pod <id>`) |
| GitHub | orphan branch `e12_habit_mechanism` created and pushed |
| Base model | `Qwen/Qwen3.6-27B` @ 6a9e13bd copied to `/dev/shm/qwen36_27b`; 16/16 shard hashes ok |
| Adapters | V `c3f0139a…` ok, VB `20859823…` ok (both match the brief); S `135f978e…`, SB `de6f02db…` present |
| Habit-free controls | `ctrl_A_s0`, `ctrl_B_s0` final adapters downloaded |
| SAE | `ceselder/qwen36-27b-sae-l42-1b` ae.pt `be5990c2…`, config.json `b4272573…`, examples.parquet `120030b5…`; first download stalled (xet), retried without xet, ok |
| Web text | Ultra-FineWeb (`en`): 98 x 1,024-token windows (100,352 tokens), first 2,000 docs' first 40 words |
| Conversations / judgments | all on the volume; scripts `8c888cb4…` / `958d50b6…`; train_V `bf1156c7…`, train_VB `69cdbe27…`; paper file A `/workspace/si36/data/story-imprinting/…/helpful-bees-vs-dismissive-crows.jsonl` `17fa909d…`, file B `3ed67422…` (both = the adapters' train_meta data_sha256) |
| Code reused | R10 `hf_r10.py` (loading, hooks pattern), E09 `e09_fwd.py` (six openings, bridge), R10 `copy_base.sh`; copied/rewritten under `code/` |

Conditions found (trigger on, >= 100 scored, T 0.7): V 13, VB 13, S 29, SB 29 (R08's T=1.0 conversations excluded: different sampling temperature).
H banks: V 100 (of 149 eligible), VB 45, S 72, SB 52; dismissive banks S 100 (of 164), SB 100 (of 206).
Qwen3.6's template inserts no default system prompt, so there is no SYS-QWEN; SYS-EMPTY renders `<|im_start|>system\n<|im_end|>\n`.

## Smoke (15:00–15:06 UTC; `smoke/`)

- Rendering: p1 = the `\n\n` after `</think>`; header group = 7 tokens (`<|im_start|>assistant\n<think>\n\n</think>\n\n`); prohibition span and system block marked (`smoke/render.txt`).
- O, C, H finite on V|default, V|P22, S|dismissive for model and parent.
- SAE on 999 parent web tokens: EV 0.712 (thresholded, L0 68.1), 0.708 (top-64); decoder rows unit norm; threshold 1.5846.
- Band switch: all bands on vs plain PEFT max diff 0.0 nats; all off vs parent 0.0 nats (pass).
- Cache-branch O/C vs full-sequence scoring: max 0.062 nats per token (bf16); batched vs single 0.062 per token, 0.014 on O.
- Throughput: prefix passes 5,280 tok/s; O/C with 7 continuation passes 1,730 tok/s (being reduced: one batched continuation pass).

## Log
- 15:06 UTC Stage 0 started (GPU 0).
- 15:23 UTC Stage 0 done: parent web EV 0.703 (top-64, chosen; thresholded 0.713), loss recovered 0.989; chat/story EV 0.58–0.62 for parent, V, VB, S, SB; loss recovered 0.85–0.96. Table in README section 1.
- 15:23 UTC Part 2 + map contexts started (V, SB, VB, S, then parent maps).
- 15:25 UTC grouped-continuation check: O/C vs full-sequence scoring, max 0.12 nats per token (bf16).
- 15:26 UTC **first 200 Part 2 contexts: 2,065 tokens/s (< 3,500)** → cut order applied from the start: **cut 1 (habit-free controls) applied**. Projection with measured rates puts everything else (Part 2, maps, Part 3, Part 4, Part 5 on all four models) at ~19:50 UTC, before the 21:58 checkpoint, so no further cut now; controls run at the end only if time remains.
- 15:53 UTC Tony's addition received: Stage 0 on ctrl_A_s0 and ctrl_B_s0 (chat, story, position groups) will run after Part 2 on SB (the job running now), then A1's order resumes (VB, S, parent maps, Part 3/4, Part 5). Cut order otherwise unchanged.
- 15:52 UTC Part 2 progress: V done (15:25–15:40); SB O/C sets done; SB H and maps running.
- 16:25 UTC Stage 0 on ctrl_A_s0 / ctrl_B_s0 done (Tony's addition): chat EV 0.613 / 0.615, story EV 0.592 / 0.591, loss recovered 0.94–0.96; position rows on S/SB anchor contexts (p1 EV negative: p1 states barely vary around their mean). Part 2 resumed 16:25 (VB, S, parent maps). Lost ~10 min GPU time at 16:06 (handoff script killed by a tmux prefix match).
- 17:12 UTC Part 2 done. R1 verdicts (written before Part 5): V: O not valid, C not valid, H not valid -> no Part 5; SB: O not valid, C not valid, H valid -> Part 5 with H; VB: O not valid, C not valid, H not valid -> no Part 5; S: O not valid, C not valid, H valid -> Part 5 with H
- 17:24 UTC Part 5 started (order V, SB, VB, S; models without a valid readout skipped).
- 17:12 UTC Part 2 done for all four models + parent maps. R1 verdicts written to README/STATUS before Part 5 (see line above at 17:13): V none, VB none, SB H, S H.
- 17:25–17:42 UTC Part 4 GPU steps done; Part 5 on SB (H) and S (H), all 18 configurations; V and VB skipped (no valid readout).
- 17:43–17:50 UTC habit-free controls' Part 2 readouts (cut 1, restored at the end because time remained); R1 verdicts unchanged.
- 17:55 UTC final analyses and README done.
- 17:52 UTC final push verified (remote head = local head 885a7ab). About to run: `runpodctl remove pod $RUNPOD_POD_ID || runpodctl pod delete $RUNPOD_POD_ID` (if both refused: `runpodctl stop pod $RUNPOD_POD_ID || runpodctl pod stop $RUNPOD_POD_ID`).
