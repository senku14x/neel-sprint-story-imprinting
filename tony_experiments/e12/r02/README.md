# E12 R02: the layer-42 SAE fine-tuned on chat text, every public Qwen3.6-27B SAE compared, and the concept map

Brief v1.0 (30 Oct 2026, ~02:50 Taipei). One GPU (1x H100 80 GB). Numbers only; interpretation and concept labels are left to the E12 chat.

## Status

**Done; nothing cut.** Deadline armed 18:26:40 UTC; Stage A finished 23:21 UTC (~4.9 h); no LLM API calls; one H100.

- **Stage S** (other public SAEs): all five peak at their card's block N and reproduce their cards within 0.10 (none dropped). On our text (parent) the best of them reach chat/story EV 0.61/0.62 (papergrade L55) and header EV 0.50 (L55) / 0.45 (L31); header splice KL 0.15 (L31) to 0.87 (fullstack L43). None meets both WORKS header bars (header EV ≥ 0.55 and KL ≤ 0.3).
- **Stage F**: 8.0M parent block-42 tokens (chat 60%, story 25%, web 15%) + 153k header copies; 1,990 BatchTopK steps from R01's SAE (lr 2e-5); load check web EV 0.7033; after training 0.7081.
- **Stage T: IMPROVED.** Fine-tuned SAE, parent: header EV 0.867 (original 0.280), chat 0.768 (0.595), story 0.735 (0.585), web 0.708 (0.703); header splice KL 0.123 nats (original 9.645; noise control 0.034); loss recovered chat 0.982 (0.851), story 0.988 (0.952), web 0.990 (0.989). Every WORKS bar is met on the parent except "every trained model and control within 0.05 of the parent": chat and story are within 0.02, but header EV through the adapters is V 0.678, VB 0.680, S 0.455, SB 0.464, ctrl_A_s0 0.475, ctrl_B_s0 0.340 against the parent's 0.86–0.88 on the same contexts. Stage A therefore ran with the fine-tuned SAE at block 42, and **every Stage A result is labelled "IMPROVED SAE: header results provisional"**.
- **A1** (rule E12-D03 A1): **not met in any model** (V, VB, S, SB; p1 and header; parent and own-adapter passes; the controls too). The top 10 terms carry 0.89–0.996 of the summed absolute terms and 5–9 of them recur in both halves, but the signed top-10 share (−0.48 to 1.15) never beats the shuffled-label null's 95th percentile (1.4–7.5). The signed total is negative for V and SB.
- **A2** (rule E12-D03 A2, V): **not met** at p1 or the header. V own-model p1: 15 stable concepts, held-out within-condition AUC 0.607 (dense ridge 0.729), condition Spearman 0.704 (best baseline 0.870, PCA-50 L1); VB sign check failed. S/SB quantities are reported without a verdict.
- **A3**: the formal-minus-casual helper-speech direction exceeds both random-direction 95th percentiles at 5/10/20/50 OMP atoms (R² 0.68/0.76/0.83/0.90 vs random-half 0.51/0.62/0.73/0.83); the default-minus-P22, dismissive-minus-default and trained-minus-parent directions exceed the isotropic percentiles but not the random-half ones (except default-minus-P22 at 50 atoms). Known-answer check: register-like contexts on both sides (section 3).
- **Side task**: not run (kit missing at /root; the file on /workspace has a different sha256).
- **Incidents**: ~70 min lost before pre-flight; three analysis bugs fixed before any reported number (section 3).


**Stage T outcome line:** Stage T outcome: IMPROVED. Fine-tuned layer-42 SAE, parent: header EV 0.867 (original 0.280), chat 0.768, story 0.735, web 0.708, header splice KL 0.123 nats (original 9.645; noise control 0.034); models within 0.05: False. Next: Stage A with ft42 at block 42 (IMPROVED SAE: header results provisional).

Run log (STATUS.md):


    - 2026-10-29 18:26:40 UTC: deadline armed (8 h; pod stop at 02:26:40 UTC; cut checkpoint 01:41:40 UTC).
    - 19:41 UTC: pre-flight passed (1x H100 80 GB, 199 GB free on /, keys set, runpodctl stop/remove present, base copied and hashed 16/16, every adapter, data file and SAE file matches R01's sha256). ~70 min lost before pre-flight (early tool calls slow to clear).
    - 19:57 UTC: smoke test passed: original SAE parent web EV 0.7033 (R01 0.703); render ok; 4-context header splice KL finite (orig 5.5-17 nats; noise control 0.0006-0.40). R01 test sets rebuilt identically.
    - Stage S hook check (parent web): every other SAE peaks at its card's block N (papergrade L31 0.658, L55 0.769; fullstack L35 0.580, L39 0.577, L43 0.594); all within 0.10 of their cards: none dropped.
    - Side task: upload kit /root/si_study_upload_kit.tar.gz not present at 19:57 UTC; will recheck after each stage.
    - 19:58 UTC: Stage F phase 1 (activation collection) started.
    - 20:12 UTC: Stage F phase 1 done (830 s): 8,001,245 tokens through the parent at block 42 (chat 4,800,237; story 2,003,075; web 1,197,933) + 153,348 header-token copies (3 extra copies); 0 outliers; 30 bf16 shards. 0 R01 test conversations, 66 test-matching stories excluded (data/phase1_counts.json). Order change (efficiency, no rule changed): Stage S's measures run together with Stage T's after training, so every SAE is measured from the same passes.
    - 20:12 UTC: Stage F phase 2 (training) started.
    - 20:21 UTC: Stage F training done (1,990 steps, 520 s): load check web EV 0.7033 -> after 0.7081 (top-64, parent, R01's web set); threshold 1.5846 -> 1.6854; sae_ft/ae.pt sha256 4d3d8ce4…a3. Stage S+T measurement started (all 7 SAEs x 7 models).
    - 21:16 UTC: Stage T outcome: IMPROVED. Fine-tuned layer-42 SAE, parent: header EV 0.867 (original 0.280), chat 0.768, story 0.735, web 0.708, header splice KL 0.123 nats (original 9.645; noise control 0.034); models within 0.05: False. Next: Stage A with ft42 at block 42 (IMPROVED SAE: header results provisional).
    - 21:46 UTC: Stage A collection done for V/VB (stories, A2 units) and S/SB (stories, default and dismissive contexts, controls); 21:47 A1 done for all four models (results/stageA/A1.json). 21:57 S/SB A2 units collection started; A2 rerun, A3 and contexts follow.
    - 23:21 UTC: Stage A done: A1 (4 models, p1 and header, parent and own adapter, controls), A2 (V, VB, S, SB; own model and parent), A3 (10 directions + 200 random), concept contexts. A1 rule met in no model; A2 rule (V) not met at p1 or header.
    - Side task (Tony): study repo upload: 0 uploaded, 0 failed, VERIFIED no — not run. /root/si_study_upload_kit.tar.gz was never present (checked 19:57, 20:07, 21:20, 22:15, 23:22 UTC). A file /workspace/si_study_upload_kit.tar.gz (15,967 bytes, 16:41 UTC) exists, but its sha256 267c4cc1…7f1582a does not match the brief's 2e6e00ac…75321eb, so it was not extracted or run.
    - 23:23 UTC: final push done; next command: runpodctl remove pod $RUNPOD_POD_ID (fallback runpodctl pod delete; if both refused, runpodctl stop pod).

## 1. Stage S, Stage F, Stage T

### Stage S hook check (parent, R01's web set; EV at blocks N-1, N, N+1; block L = output of `model.model.layers[L]`)

| SAE | card N | card held-out EV | EV N-1 | EV N | EV N+1 | kept block | peak EV | reproduced (peak >= card - 0.10) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| pg31 | 31 | 0.714 | 0.640 | 0.658 | 0.626 | 31 | 0.658 | yes |
| pg55 | 55 | 0.816 | 0.741 | 0.769 | 0.718 | 55 | 0.769 | yes |
| fs35 | 35 | 0.589 | 0.515 | 0.580 | 0.544 | 35 | 0.580 | yes |
| fs39 | 39 | 0.587 | 0.557 | 0.577 | 0.558 | 39 | 0.577 | yes |
| fs43 | 43 | 0.604 | 0.557 | 0.594 | 0.573 | 43 | 0.594 | yes |

SAE names: orig42 = `ceselder/qwen36-27b-sae-l42-1b` (R01's); ft42 = this run's fine-tune of it; pg31/pg55 = `caiovicentino1/qwen36-27b-sae-papergrade` L31/L55; fs35/fs39/fs43 = `caiovicentino1/qwen36-27b-sae-fullstack` L35/L39/L43. Encode: orig42/ft42 relu then per-token top-64 (R01's chosen convention); the others top-128 of the pre-activation then relu (their cards' code; no input normalisation in their cfg).

### Stage F data (phase 1: parent, block 42)

- Chat: 3894 conversations cut after one random assistant turn (of 37350 in E08 R07-R10 + E10 R01; 6019 excluded as R01 test conversations by key or identical content), 4,800,237 counted tokens; header tokens 51,116 (+3 copies each = 153,348); final header not 7 tokens: 1. By model: {'S': 729, 'VB': 341, 'NB': 321, 'parent': 462, 'N': 363, 'V': 333, 'Nc': 132, 'SB': 692, 'NBc': 117, 'X': 211, 'XB': 193}. By run: {'e08r10': 705, 'e08r08': 433, 'e08r09': 983, 'e10r01': 967, 'e08r07': 806}.
- Stories: train_V: 333 rows, 333,426 tokens, 59 excluded as R01 test stories; train_VB: 342 rows, 334,241 tokens, 0 excluded as R01 test stories; file_A: 459 rows, 334,187 tokens, 58 excluded as R01 test stories; file_B: 459 rows, 333,840 tokens, 4 excluded as R01 test stories; ctrl_A: 485 rows, 333,694 tokens, 4 excluded as R01 test stories; ctrl_B: 489 rows, 333,687 tokens, 0 excluded as R01 test stories.
- Web: 1171 x 1,024-token windows, 1,197,933 tokens, Ultra-FineWeb `en` documents 5000-6568 (R01 streamed documents 0-1999; we skipped the first 5000).
- Exclusion check: R01 test conversation keys among the chat units: 0.
- Collected: 8,001,245 positions in, 0 outliers (> 10x batch median norm) dropped, 8,154,593 rows written (source counts {'0': 4800237, '1': 153348, '2': 2003075, '3': 1197933}: 0 chat, 1 chat header copy, 2 story, 3 web), 830 s.

### Stage F training (dictionary_learning @ 60ec6bf5, BatchTopKTrainer.update driven in our loop)

Steps 1990 (batch 4,096, one pass, 8,154,593 rows); load check (parent web EV, top-64, loaded weights) 0.7033; after training 0.7081; threshold 1.5846 -> 1.6854; 520 s. sha256: {'ae.pt': '4d3d8ce4d2b46a8fea7c675b8049e01f7d350aff37d820eeeb00492a9f2effa3', 'config.json': '4f8332d01e47b8e066f08380406825c9762deed18bf311e5d708fcff435f678e'}.

| step | lr | loss (l2) | batch FVU (batch top-k) | batch FVU (threshold) | L0 (threshold) | dead frac (>= 10M tokens) | not fired in 1M tokens |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0.00e+00 | 1339.3 | 0.3766 | 0.3630 | 79.2 | 0.0000 | 0.0000 |
| 51 | 1.00e-05 | 1275.6 | 0.3616 | 0.3468 | 81.0 | 0.0000 | 0.0000 |
| 101 | 2.00e-05 | 1195.6 | 0.3323 | 0.3173 | 85.7 | 0.0000 | 0.0000 |
| 201 | 2.00e-05 | 1036.9 | 0.2900 | 0.2792 | 81.6 | 0.0000 | 0.0000 |
| 401 | 2.00e-05 | 916.6 | 0.2570 | 0.2505 | 74.0 | 0.0000 | 0.0849 |
| 601 | 2.00e-05 | 867.7 | 0.2435 | 0.2400 | 69.2 | 0.0000 | 0.0828 |
| 801 | 2.00e-05 | 834.8 | 0.2349 | 0.2333 | 66.1 | 0.0000 | 0.0831 |
| 1001 | 2.00e-05 | 811.4 | 0.2279 | 0.2279 | 63.9 | 0.0000 | 0.0810 |
| 1201 | 2.00e-05 | 797.7 | 0.2263 | 0.2273 | 62.7 | 0.0000 | 0.0811 |
| 1401 | 2.00e-05 | 781.3 | 0.2185 | 0.2199 | 62.3 | 0.0000 | 0.0795 |
| 1601 | 1.96e-05 | 769.3 | 0.2167 | 0.2186 | 61.7 | 0.0000 | 0.0798 |
| 1801 | 9.55e-06 | 767.1 | 0.2160 | 0.2181 | 61.5 | 0.0000 | 0.0797 |
| 1990 | 5.03e-08 | 751.0 | 0.2134 | 0.2153 | 61.7 | 0.0000 | 0.0794 |

Full log every 50 steps: `logs/stageF_train.jsonl`. The auxiliary (AuxK) loss is active only for latents dead >= 10M tokens (the original's rule); in a one-pass 8M-token run none can qualify, so it stayed 0.

### Stage S + T table (one row per SAE x model; EV with each set's own mean, R01's code)

Header/p1/prohib/system EV: the parent on all four models' R01 Part 2 anchor contexts pooled (720), each trained model on its own anchors, ctrl_A_s0 on S's, ctrl_B_s0 on SB's. Splice KL: mean over 200 anchor contexts of KL(clean || spliced) at p1 when the 7 header tokens' block-L states are replaced by the SAE reconstruction; noise: the same states plus Gaussian noise of the SAE error's per-token norm. Loss recovered (ft42; orig42 from R01 where R01 has the row).

| SAE | block | model | web EV | chat EV | story EV | header EV | p1 EV | prohib EV | system EV | splice KL | noise KL | LR web | LR chat | LR story |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| orig42 | 42 | parent | 0.703 | 0.595 | 0.585 | 0.280 | -0.895 | 0.555 | 0.523 | 9.645 | 0.196 | 0.989 | 0.851 | 0.952 |
| orig42 | 42 | V | 0.704 | 0.602 | 0.578 | 0.158 | -4.179 | 0.520 | 0.470 | 2.178 | 0.060 | – | 0.917 | 0.946 |
| orig42 | 42 | VB | 0.704 | 0.601 | 0.578 | 0.155 | -3.768 | 0.520 | 0.460 | 1.576 | 0.057 | – | 0.917 | 0.946 |
| orig42 | 42 | S | 0.707 | 0.616 | 0.595 | 0.149 | -1.528 | 0.526 | 0.497 | 0.466 | 0.039 | – | 0.931 | 0.954 |
| orig42 | 42 | SB | 0.707 | 0.617 | 0.595 | 0.160 | -0.645 | 0.521 | 0.493 | 0.406 | 0.053 | – | 0.932 | 0.956 |
| orig42 | 42 | ctrl_A_s0 | 0.705 | 0.613 | 0.592 | 0.136 | -1.691 | 0.518 | 0.502 | 0.363 | 0.043 | – | 0.941 | 0.955 |
| orig42 | 42 | ctrl_B_s0 | 0.706 | 0.615 | 0.591 | -0.009 | -1.602 | 0.510 | 0.500 | 0.398 | 0.041 | – | 0.941 | 0.957 |
| ft42 | 42 | parent | 0.708 | 0.768 | 0.735 | 0.867 | 0.661 | 0.820 | 0.867 | 0.123 | 0.034 | 0.990 | 0.982 | 0.988 |
| ft42 | 42 | V | 0.710 | 0.772 | 0.717 | 0.678 | -0.508 | 0.777 | 0.868 | 0.073 | 0.018 | 0.990 | 0.980 | 0.978 |
| ft42 | 42 | VB | 0.710 | 0.772 | 0.718 | 0.680 | -0.364 | 0.778 | 0.862 | 0.069 | 0.017 | 0.990 | 0.980 | 0.977 |
| ft42 | 42 | S | 0.712 | 0.771 | 0.722 | 0.455 | -0.236 | 0.759 | 0.784 | 0.088 | 0.019 | 0.990 | 0.983 | 0.980 |
| ft42 | 42 | SB | 0.712 | 0.772 | 0.721 | 0.464 | 0.053 | 0.754 | 0.783 | 0.232 | 0.034 | 0.990 | 0.984 | 0.981 |
| ft42 | 42 | ctrl_A_s0 | 0.711 | 0.767 | 0.721 | 0.475 | -0.391 | 0.750 | 0.789 | 0.099 | 0.022 | 0.990 | 0.984 | 0.980 |
| ft42 | 42 | ctrl_B_s0 | 0.711 | 0.768 | 0.720 | 0.340 | -0.343 | 0.745 | 0.786 | 0.074 | 0.021 | 0.990 | 0.984 | 0.982 |
| pg31 | 31 | parent | 0.658 | 0.584 | 0.575 | 0.450 | -1.218 | 0.531 | 0.485 | 0.152 | 0.090 | – | – | – |
| pg31 | 31 | V | 0.658 | 0.589 | 0.570 | 0.318 | -5.056 | 0.514 | 0.451 | 0.063 | 0.017 | – | – | – |
| pg31 | 31 | VB | 0.657 | 0.590 | 0.569 | 0.291 | -4.776 | 0.517 | 0.461 | 0.049 | 0.016 | – | – | – |
| pg31 | 31 | S | 0.666 | 0.611 | 0.596 | 0.225 | -1.801 | 0.512 | 0.462 | 0.081 | 0.019 | – | – | – |
| pg31 | 31 | SB | 0.666 | 0.608 | 0.596 | 0.261 | -1.429 | 0.514 | 0.459 | 0.111 | 0.026 | – | – | – |
| pg31 | 31 | ctrl_A_s0 | 0.663 | 0.606 | 0.590 | 0.201 | -2.044 | 0.507 | 0.458 | 0.062 | 0.020 | – | – | – |
| pg31 | 31 | ctrl_B_s0 | 0.664 | 0.609 | 0.591 | 0.052 | -1.665 | 0.512 | 0.463 | 0.057 | 0.021 | – | – | – |
| pg55 | 55 | parent | 0.769 | 0.612 | 0.621 | 0.499 | -0.009 | 0.669 | 0.616 | 0.480 | 0.111 | – | – | – |
| pg55 | 55 | V | 0.768 | 0.615 | 0.604 | 0.406 | -1.730 | 0.616 | 0.529 | 0.468 | 0.079 | – | – | – |
| pg55 | 55 | VB | 0.767 | 0.615 | 0.605 | 0.372 | -1.552 | 0.615 | 0.524 | 0.484 | 0.079 | – | – | – |
| pg55 | 55 | S | 0.773 | 0.646 | 0.642 | 0.341 | -0.451 | 0.623 | 0.597 | 0.466 | 0.069 | – | – | – |
| pg55 | 55 | SB | 0.773 | 0.647 | 0.643 | 0.352 | -0.224 | 0.620 | 0.591 | 0.432 | 0.075 | – | – | – |
| pg55 | 55 | ctrl_A_s0 | 0.773 | 0.640 | 0.637 | 0.311 | -0.371 | 0.615 | 0.593 | 0.426 | 0.077 | – | – | – |
| pg55 | 55 | ctrl_B_s0 | 0.773 | 0.642 | 0.638 | 0.242 | -0.370 | 0.613 | 0.589 | 0.478 | 0.079 | – | – | – |
| fs35 | 35 | parent | 0.580 | 0.474 | 0.441 | 0.323 | -0.771 | 0.407 | 0.337 | 0.811 | 0.132 | – | – | – |
| fs35 | 35 | V | 0.577 | 0.475 | 0.435 | 0.206 | -5.040 | 0.378 | 0.257 | 0.414 | 0.034 | – | – | – |
| fs35 | 35 | VB | 0.577 | 0.475 | 0.436 | 0.165 | -4.539 | 0.379 | 0.247 | 0.420 | 0.036 | – | – | – |
| fs35 | 35 | S | 0.581 | 0.490 | 0.453 | 0.126 | -1.559 | 0.386 | 0.308 | 0.197 | 0.029 | – | – | – |
| fs35 | 35 | SB | 0.582 | 0.491 | 0.453 | 0.138 | -1.008 | 0.381 | 0.302 | 0.241 | 0.035 | – | – | – |
| fs35 | 35 | ctrl_A_s0 | 0.580 | 0.489 | 0.453 | 0.141 | -1.714 | 0.383 | 0.311 | 0.380 | 0.029 | – | – | – |
| fs35 | 35 | ctrl_B_s0 | 0.581 | 0.490 | 0.452 | 0.011 | -1.556 | 0.377 | 0.313 | 0.318 | 0.027 | – | – | – |
| fs39 | 39 | parent | 0.577 | 0.461 | 0.440 | 0.353 | -0.753 | 0.433 | 0.375 | 0.714 | 0.169 | – | – | – |
| fs39 | 39 | V | 0.577 | 0.465 | 0.434 | 0.233 | -4.520 | 0.396 | 0.277 | 0.410 | 0.047 | – | – | – |
| fs39 | 39 | VB | 0.577 | 0.464 | 0.434 | 0.192 | -4.090 | 0.394 | 0.261 | 0.334 | 0.045 | – | – | – |
| fs39 | 39 | S | 0.578 | 0.476 | 0.448 | 0.136 | -1.617 | 0.395 | 0.347 | 0.262 | 0.037 | – | – | – |
| fs39 | 39 | SB | 0.579 | 0.477 | 0.448 | 0.163 | -0.813 | 0.390 | 0.341 | 0.186 | 0.045 | – | – | – |
| fs39 | 39 | ctrl_A_s0 | 0.578 | 0.475 | 0.448 | 0.126 | -1.742 | 0.387 | 0.350 | 0.335 | 0.037 | – | – | – |
| fs39 | 39 | ctrl_B_s0 | 0.578 | 0.476 | 0.447 | 0.004 | -1.687 | 0.382 | 0.351 | 0.308 | 0.036 | – | – | – |
| fs43 | 43 | parent | 0.594 | 0.473 | 0.463 | 0.388 | -0.828 | 0.441 | 0.402 | 0.868 | 0.180 | – | – | – |
| fs43 | 43 | V | 0.594 | 0.475 | 0.452 | 0.264 | -4.691 | 0.400 | 0.315 | 0.584 | 0.060 | – | – | – |
| fs43 | 43 | VB | 0.593 | 0.474 | 0.453 | 0.220 | -4.340 | 0.397 | 0.305 | 0.514 | 0.056 | – | – | – |
| fs43 | 43 | S | 0.595 | 0.487 | 0.468 | 0.109 | -1.791 | 0.400 | 0.379 | 0.312 | 0.045 | – | – | – |
| fs43 | 43 | SB | 0.596 | 0.487 | 0.467 | 0.134 | -0.731 | 0.397 | 0.376 | 0.256 | 0.058 | – | – | – |
| fs43 | 43 | ctrl_A_s0 | 0.595 | 0.485 | 0.466 | 0.071 | -1.883 | 0.395 | 0.385 | 0.293 | 0.051 | – | – | – |
| fs43 | 43 | ctrl_B_s0 | 0.595 | 0.486 | 0.464 | -0.065 | -1.851 | 0.388 | 0.382 | 0.381 | 0.050 | – | – | – |

Long-format rows (every measure, n, FVU, L0, CE values): `results/stageST/text_ev.jsonl`, `text_ce.jsonl`, `positions.json` (also per source model for the parent), `splice_kl.json` (per context).

Clean CE check against R01 (same positions): max |CE_clean − R01's| = 0.000 nats.

### Stage T outcome

WORKS criteria for ft42 (parent): header: met, chat: met, story: met, web: met, kl: met, models_within: not met.
IMPROVED tests: header_ge_0_43: True, kl_le_half_orig: True.
Gaps vs the parent (ft42; model − parent EV): V: chat +0.004, story -0.018, header -0.199; VB: chat +0.004, story -0.018, header -0.198; S: chat +0.003, story -0.013, header -0.405; SB: chat +0.004, story -0.014, header -0.397; ctrl_A_s0: chat -0.001, story -0.014, header -0.385; ctrl_B_s0: chat +0.000, story -0.015, header -0.520.

**Stage T outcome: IMPROVED. Fine-tuned layer-42 SAE, parent: header EV 0.867 (original 0.280), chat 0.768, story 0.735, web 0.708, header splice KL 0.123 nats (original 9.645; noise control 0.034); models within 0.05: False. Next: Stage A with ft42 at block 42 (IMPROVED SAE: header results provisional).**

## 2. Stage A (SAE ft42, block 42) — **IMPROVED SAE: header results provisional**

### A1: which concepts tie the default to the winner

term_i = d_i (w_i − l_i) ||W_dec[i]||²; d = mean code at the default's p1 (or header, mean over its 7 tokens), w/l = mean codes at the winner's/loser's first mentions (500 each). Rule (E12-D03 A1): top 10 carry ≥ 50% of the signed total, ≥ 7 of them in both halves' top 10, and the top-10 share beats the shuffled-label null's 95th percentile.

| model | through | position | n d/w/l | signed total | top-5 share | top-10 share | top-20 share | top-10 share of sum abs | top-10 in both halves | null p95 (top-10 share) | sum of terms / decoded dot | raw dot | **rule** |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| V | parent | p1 | 200/500/500 | -59.58 | -0.097 | -0.100 | -0.101 | 0.989 | 7 | 2.372 | 0.468 | -148.5 | not met |
| V | parent | header | 200/500/500 | -18.89 | -0.141 | -0.151 | -0.155 | 0.961 | 8 | 4.588 | -0.230 | 65.84 | not met |
| V | V | p1 | 200/500/500 | -250.3 | -0.001 | -0.001 | -0.001 | 0.996 | 5 | 1.360 | 0.643 | -489.6 | not met |
| V | V | header | 200/500/500 | -78.6 | -0.010 | -0.012 | -0.012 | 0.983 | 9 | 1.869 | 3.223 | -94.08 | not met |
| VB | parent | p1 | 200/500/500 | 42.47 | 1.130 | 1.140 | 1.143 | 0.978 | 8 | 2.566 | -0.365 | -117.4 | not met |
| VB | parent | header | 200/500/500 | 11.98 | 1.116 | 1.146 | 1.171 | 0.926 | 6 | 7.541 | -0.079 | -147.7 | not met |
| VB | VB | p1 | 200/500/500 | 156.9 | 1.053 | 1.054 | 1.054 | 0.992 | 8 | 1.445 | 11.826 | -41.29 | not met |
| VB | VB | header | 200/500/500 | 48 | 1.087 | 1.093 | 1.097 | 0.973 | 7 | 1.804 | -0.473 | -134.2 | not met |
| S | parent | p1 | 200/500/500 | 34.54 | 1.059 | 1.073 | 1.079 | 0.970 | 8 | 3.072 | 4.018 | 19.22 | not met |
| S | parent | header | 200/500/500 | 16.58 | 0.992 | 1.019 | 1.034 | 0.929 | 9 | 5.745 | -0.350 | -45.22 | not met |
| S | S | p1 | 200/500/500 | 142.3 | 1.066 | 1.074 | 1.081 | 0.969 | 7 | 3.491 | 1.182 | 183.8 | not met |
| S | S | header | 200/500/500 | 46.64 | 1.046 | 1.064 | 1.076 | 0.932 | 9 | 3.359 | 6.735 | 24.08 | not met |
| S | ctrl_A_s0 | p1 | 200/500/500 | 75 | 1.094 | 1.143 | 1.161 | 0.910 | 9 | 2.699 | 0.886 | 85.19 | not met |
| S | ctrl_A_s0 | header | 200/500/500 | 27.04 | 1.039 | 1.088 | 1.116 | 0.889 | 8 | 2.979 | 3.229 | -0.3639 | not met |
| SB | parent | p1 | 200/500/500 | -7.039 | -0.439 | -0.476 | -0.501 | 0.898 | 6 | 2.486 | 0.217 | -23.2 | not met |
| SB | parent | header | 200/500/500 | -10.21 | -0.078 | -0.089 | -0.099 | 0.904 | 7 | 3.977 | -0.698 | 20.41 | not met |
| SB | SB | p1 | 200/500/500 | -78.61 | -0.196 | -0.221 | -0.235 | 0.913 | 8 | 3.601 | 0.633 | -193.9 | not met |
| SB | SB | header | 200/500/500 | -38.98 | -0.081 | -0.097 | -0.108 | 0.910 | 8 | 3.281 | 1.479 | -75.24 | not met |
| SB | ctrl_B_s0 | p1 | 200/500/500 | -115.9 | -0.033 | -0.043 | -0.047 | 0.947 | 8 | 2.039 | 0.626 | -265.9 | not met |
| SB | ctrl_B_s0 | header | 200/500/500 | -38.7 | -0.035 | -0.046 | -0.052 | 0.933 | 8 | 2.515 | 0.712 | -100.4 | not met |

Concepts in the top 20 for ≥ 3 of the 4 models (parent pass): p1|top20_winner: [26646, 81280, 103535, 105215]; p1|top20_loser: [13987, 23050, 28869, 61137, 66027, 81609, 120051, 125931]; header|top20_winner: [103535, 104831, 105215]; header|top20_loser: [23050, 28869, 66027, 81609, 92690, 123924, 125931].

**V (p1, through the parent)** — top 20 toward the winner: 126279 (5.06), 104831 (0.226), 26477 (0.172), 103535 (0.163), 97995 (0.147), 78763 (0.0873), 62436 (0.0431), 52794 (0.032), 81280 (0.0215), 105215 (0.0191), 125672 (0.0113), 61006 (0.0071), 26646 (0.00399), 46053 (0.00263), 46692 (0.0023), 27919 (0.00205), 92025 (0.00174), 12605 (0.00153), 7934 (0.00147), 59398 (0.00137)
; top 20 toward the loser: 67033 (-45.4), 69151 (-15.4), 86532 (-3.96), 49843 (-0.0928), 28869 (-0.0814), 109795 (-0.0652), 51318 (-0.0572), 23050 (-0.0506), 20795 (-0.0484), 66027 (-0.0481), 13987 (-0.0442), 117620 (-0.0338), 120051 (-0.023), 5990 (-0.0213), 10032 (-0.021), 66828 (-0.0189), 81609 (-0.0125), 29326 (-0.0125), 69097 (-0.0107), 56123 (-0.00983).

**V (header, through the parent)** — top 20 toward the winner: 126279 (2.02), 97995 (0.283), 104831 (0.229), 26894 (0.0708), 10956 (0.055), 105215 (0.0447), 103535 (0.038), 75432 (0.0369), 26477 (0.0355), 78763 (0.0281), 92025 (0.0196), 81280 (0.0153), 46692 (0.0112), 113037 (0.00932), 52794 (0.00932), 62436 (0.0083), 11507 (0.0057), 83321 (0.00479), 70027 (0.00434), 128320 (0.00381)
; top 20 toward the loser: 67033 (-11.8), 12694 (-4.3), 69151 (-3.59), 86532 (-1.34), 79327 (-0.149), 123924 (-0.0885), 36566 (-0.0574), 66027 (-0.0504), 49843 (-0.0283), 9910 (-0.0264), 20795 (-0.0212), 51318 (-0.0205), 40274 (-0.0192), 28869 (-0.018), 128845 (-0.0148), 23050 (-0.0144), 92690 (-0.0137), 109795 (-0.0121), 76383 (-0.0112), 16059 (-0.0108).

**VB (p1, through the parent)** — top 20 toward the winner: 67033 (44.9), 69151 (2.09), 103535 (0.43), 26477 (0.345), 97995 (0.251), 20795 (0.154), 66828 (0.115), 5990 (0.0583), 51318 (0.051), 52794 (0.0466), 62436 (0.0404), 105215 (0.0248), 81280 (0.0161), 50010 (0.0142), 109165 (0.0134), 58501 (0.0129), 128663 (0.0079), 36566 (0.0075), 5581 (0.00593), 26646 (0.00482)
; top 20 toward the loser: 86532 (-4.67), 126279 (-0.386), 81609 (-0.185), 28869 (-0.115), 104831 (-0.092), 125931 (-0.0791), 23050 (-0.0749), 78763 (-0.0685), 66027 (-0.0639), 117620 (-0.0574), 49843 (-0.0317), 13987 (-0.0267), 120051 (-0.0211), 61137 (-0.0176), 84350 (-0.0151), 18711 (-0.0148), 50199 (-0.0143), 109795 (-0.0139), 69097 (-0.0136), 123186 (-0.0134).

**VB (header, through the parent)** — top 20 toward the winner: 67033 (11.6), 12694 (0.766), 69151 (0.484), 97995 (0.452), 103535 (0.1), 11507 (0.0882), 105215 (0.0748), 26477 (0.0712), 59540 (0.0634), 16059 (0.0516), 79327 (0.0484), 20795 (0.0483), 75432 (0.0417), 66828 (0.0338), 36566 (0.0323), 9910 (0.0294), 40274 (0.0258), 51318 (0.019), 5990 (0.0178), 52794 (0.0136)
; top 20 toward the loser: 86532 (-1.47), 126279 (-0.153), 104831 (-0.147), 66027 (-0.0762), 81609 (-0.0487), 92690 (-0.0288), 28869 (-0.0264), 62755 (-0.0251), 23050 (-0.0212), 78763 (-0.0177), 10956 (-0.0159), 125931 (-0.0149), 117620 (-0.0114), 3508 (-0.0114), 49843 (-0.00946), 42514 (-0.00905), 78874 (-0.00761), 123924 (-0.00742), 745 (-0.0073), 1961 (-0.00726).

**S (p1, through the parent)** — top 20 toward the winner: 67033 (23.4), 69151 (7.4), 86532 (5.26), 49843 (0.28), 66828 (0.232), 117620 (0.145), 21136 (0.107), 103535 (0.0932), 10032 (0.0732), 109795 (0.0382), 76868 (0.0337), 78167 (0.032), 89320 (0.0262), 51318 (0.0256), 72199 (0.0216), 105215 (0.0209), 81280 (0.0165), 5990 (0.0155), 25970 (0.00916), 38002 (0.0082)
; top 20 toward the loser: 126279 (-0.758), 125931 (-0.584), 28869 (-0.454), 81609 (-0.431), 23050 (-0.174), 66027 (-0.0636), 61137 (-0.0518), 78763 (-0.05), 130246 (-0.049), 120051 (-0.0396), 26235 (-0.0374), 91111 (-0.0214), 33006 (-0.0203), 87995 (-0.0105), 6363 (-0.00975), 26646 (-0.00864), 103767 (-0.0077), 123186 (-0.00579), 15239 (-0.00535), 28508 (-0.00533).

**S (header, through the parent)** — top 20 toward the winner: 12694 (7.33), 67033 (5.95), 69151 (1.55), 86532 (1.34), 79327 (0.285), 113020 (0.166), 25874 (0.0915), 49843 (0.0714), 66828 (0.0628), 105215 (0.0625), 40274 (0.0412), 1961 (0.0295), 117620 (0.0243), 36566 (0.0236), 104831 (0.0214), 103535 (0.0209), 109063 (0.0209), 76383 (0.0204), 92345 (0.0183), 78167 (0.0171)
; top 20 toward the loser: 126279 (-0.276), 125931 (-0.098), 81609 (-0.0852), 28869 (-0.0817), 75432 (-0.0551), 23050 (-0.0388), 66027 (-0.038), 62755 (-0.0246), 83321 (-0.0171), 53527 (-0.0162), 128801 (-0.0148), 78763 (-0.0143), 93662 (-0.0086), 18196 (-0.0079), 61137 (-0.0074), 120051 (-0.00711), 130246 (-0.00702), 4932 (-0.00685), 123924 (-0.00679), 26235 (-0.00607).

**SB (p1, through the parent)** — top 20 toward the winner: 86532 (1.34), 126279 (0.607), 117620 (0.418), 49843 (0.396), 120051 (0.329), 82709 (0.073), 103535 (0.0572), 78763 (0.0571), 76868 (0.0426), 26646 (0.0277), 78167 (0.0275), 10032 (0.0249), 25970 (0.0248), 72199 (0.0208), 11178 (0.018), 89320 (0.017), 125672 (0.0133), 38002 (0.0127), 71619 (0.0106), 81280 (0.00949)
; top 20 toward the loser: 67033 (-6.45), 69151 (-2.19), 125931 (-0.373), 28869 (-0.372), 81609 (-0.37), 66828 (-0.283), 13987 (-0.151), 23050 (-0.142), 66027 (-0.109), 61137 (-0.0463), 91111 (-0.0376), 5990 (-0.0257), 26235 (-0.0123), 84824 (-0.0081), 59329 (-0.00791), 21136 (-0.00768), 46053 (-0.00697), 4080 (-0.00665), 28508 (-0.00599), 18711 (-0.0058).

**SB (header, through the parent)** — top 20 toward the winner: 86532 (0.343), 126279 (0.221), 49843 (0.105), 117620 (0.0698), 120051 (0.0599), 105215 (0.0269), 25970 (0.0267), 1961 (0.0199), 104831 (0.0184), 78763 (0.0155), 76868 (0.0147), 78167 (0.0145), 103535 (0.0129), 82709 (0.0124), 23086 (0.0117), 83321 (0.00984), 62755 (0.00927), 117599 (0.00819), 53447 (0.00737), 5726 (0.00735)
; top 20 toward the loser: 12694 (-8.35), 67033 (-1.59), 69151 (-0.459), 25874 (-0.117), 79327 (-0.102), 66828 (-0.0765), 66027 (-0.0737), 28869 (-0.0732), 81609 (-0.0727), 125931 (-0.0634), 40274 (-0.0514), 23050 (-0.0314), 13987 (-0.0285), 109063 (-0.0276), 113020 (-0.0247), 38479 (-0.02), 11507 (-0.019), 76383 (-0.0146), 92690 (-0.0127), 10956 (-0.0119).

Every listed concept's 10 top-activating contexts (ours and the SAE card's `examples.parquet`) are in `results/stageA/concepts.md` and `concept_contexts.json`.

### A2: sparse regression across conditions

| model | features from | position | units / conditions | base rate | C | stable concepts (≥ 80%) | held-out within-condition AUC | held-out condition Spearman | plain-L1 LOCO Spearman | dense ridge AUC / Spearman | PCA-50 L1 Spearman | lexical | R01 closeness | R01 persona distance |
| --- | --- | --- | --- | ---: | ---: | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| V | V | p1 | 2200 / 13 | 0.102 | 0.1 | 15: [4893, 11232, 17053, 20820, 22657, 23050, 28869, 51318, 61137, 68197, 72574, 88749, 103535, 109891, 114238] | 0.607 | 0.704 | 0.757 | 0.729 / 0.862 | 0.870 | 0.376 | 0.591 | 0.459 |
| V | V | header | 2200 / 13 | 0.102 | 0.1 | 9: [307, 20820, 51311, 51318, 63863, 74812, 88749, 99320, 114238] | 0.589 | 0.721 | 0.790 | 0.735 / 0.845 | 0.870 | 0.376 | 0.591 | 0.459 |
| V | parent | p1 | 2200 / 13 | 0.102 | 0.3 | 26: [307, 2921, 4893, 23050, 28508, 44459, 51318, 54355, 54402, 54571, 61658, 70210, 71619, 72574, 77779, 80212, 80667, 81060, 82737, 83263] | 0.630 | 0.561 | 0.738 | 0.667 / 0.818 | 0.771 | 0.376 | 0.591 | 0.459 |
| V | parent | header | 2200 / 13 | 0.102 | 0.1 | 7: [8702, 9910, 70210, 82737, 84036, 99320, 129485] | 0.577 | 0.823 | 0.790 | 0.654 / 0.826 | 0.771 | 0.376 | 0.591 | 0.459 |
| VB | VB | p1 | 2200 / 13 | 0.038 | 0.1 | 5: [39627, 77779, 84036, 88749, 103535] | 0.562 | 0.460 | 0.762 | 0.657 / 0.896 | 0.829 | 0.199 | 0.851 | 0.346 |
| VB | VB | header | 2200 / 13 | 0.038 | 0.1 | 3: [39627, 60257, 124874] | 0.525 | 0.735 | 0.884 | 0.654 / 0.873 | 0.829 | 0.199 | 0.851 | 0.346 |
| VB | parent | p1 | 2200 / 13 | 0.038 | 0.1 | 5: [4080, 70210, 71619, 89231, 103535] | 0.645 | 0.633 | 0.611 | 0.700 / 0.812 | 0.734 | 0.199 | 0.851 | 0.346 |
| VB | parent | header | 2200 / 13 | 0.038 | 0.03 | 2: [12645, 70210] | 0.513 | 0.446 | 0.566 | 0.698 / 0.837 | 0.734 | 0.199 | 0.851 | 0.346 |
| S | S | p1 | 5800 / 29 | 0.103 | 0.03 | 16: [4893, 5990, 10956, 18315, 42867, 51224, 51318, 61102, 61137, 66828, 94005, 96415, 103535, 106908, 120051, 122424] | 0.692 | 0.799 | 0.842 | 0.808 / 0.876 | 0.856 | -0.587 | -0.273 | 0.365 |
| S | S | header | 5800 / 29 | 0.103 | 0.03 | 19: [187, 2895, 4893, 7601, 18128, 18315, 26891, 43150, 51224, 51318, 61137, 75229, 77568, 96415, 97887, 117728, 119432, 123747, 129538] | 0.718 | 0.824 | 0.836 | 0.814 / 0.881 | 0.856 | -0.587 | -0.273 | 0.365 |
| S | parent | p1 | 5800 / 29 | 0.103 | 0.03 | 11: [18315, 30029, 39000, 51318, 54402, 66828, 83263, 87600, 103535, 112316, 129982] | 0.660 | 0.803 | 0.816 | 0.805 / 0.873 | 0.826 | -0.587 | -0.273 | 0.365 |
| S | parent | header | 5800 / 29 | 0.103 | 0.03 | 17: [1582, 13288, 18315, 20093, 22657, 30029, 33281, 49191, 51311, 51318, 54402, 80416, 108613, 112316, 119432, 125672, 129982] | 0.705 | 0.880 | 0.840 | 0.788 / 0.872 | 0.826 | -0.587 | -0.273 | 0.365 |
| SB | SB | p1 | 5800 / 29 | 0.063 | 0.03 | 6: [18315, 23905, 32118, 46268, 66828, 71619] | 0.489 | 0.709 | 0.794 | 0.748 / 0.782 | 0.831 | -0.377 | -0.604 | 0.657 |
| SB | SB | header | 5800 / 29 | 0.063 | 0.03 | 9: [7601, 12131, 18315, 32118, 33281, 37964, 44137, 65499, 73082] | 0.657 | 0.775 | 0.772 | 0.740 / 0.779 | 0.831 | -0.377 | -0.604 | 0.657 |
| SB | parent | p1 | 5800 / 29 | 0.063 | 0.1 | 15: [18315, 18537, 31603, 34773, 53929, 66828, 68394, 72496, 72574, 74124, 87600, 91111, 103535, 118739, 126279] | 0.564 | 0.635 | 0.696 | 0.679 / 0.764 | 0.761 | -0.377 | -0.604 | 0.657 |
| SB | parent | header | 5800 / 29 | 0.063 | 0.03 | 9: [18315, 24335, 33281, 34773, 56123, 77962, 108613, 118739, 129878] | 0.605 | 0.762 | 0.762 | 0.685 / 0.731 | 0.761 | -0.377 | -0.604 | 0.657 |

**Rule (E12-D03 A2), V, p1: not met** — n_stable_le_20_and_ge_1: yes, cond_spearman_ge_0_7: yes, auc_within_0_05_of_dense: no, beats_best_baseline_by_0_1: no, vb_same_sign_and_spearman_ge_0_5: no (dense ridge AUC 0.729; best baseline Spearman 0.870; VB check {"same_sign": {"4893": true, "11232": true, "17053": true, "20820": true, "22657": true, "23050": true, "28869": true, "51318": true, "61137": true, "68197": false, "72574": true, "88749": true, "103535": true, "109891": true, "114238": false}, "all_same_sign": false, "cond_spearman": 0.8201802096968055, "within_auc": 0.6766676114343224}).

**Rule (E12-D03 A2), V, header: not met** — n_stable_le_20_and_ge_1: yes, cond_spearman_ge_0_7: yes, auc_within_0_05_of_dense: no, beats_best_baseline_by_0_1: no, vb_same_sign_and_spearman_ge_0_5: no (dense ridge AUC 0.735; best baseline Spearman 0.870; VB check {"same_sign": {"307": false, "20820": true, "51311": true, "51318": true, "63863": true, "74812": true, "88749": true, "99320": true, "114238": true}, "all_same_sign": false, "cond_spearman": 0.5718943639042352, "within_auc": 0.5949699623221834}).

Stable concepts' contexts: `results/stageA/concepts.md`.

### A3: decomposing the directions we use (onto the unit-norm decoder rows)

Random-direction 95th percentiles: isotropic: OMP R² 5 atoms 0.020, 10 atoms 0.036, 20 atoms 0.066, 50 atoms 0.141 | Lasso R² 5 0.023, 10 0.032, 20 0.057, 50 0.083 (n 100, Lasso on 30); random_half: OMP R² 5 atoms 0.507, 10 atoms 0.617, 20 atoms 0.728, 50 atoms 0.832 | Lasso R² 5 0.239, 10 0.402, 20 0.536, 50 0.705 (n 100, Lasso on 30).

| direction | norm | OMP R² 5/10/20/50 | Lasso R² 5/10/20/50 (refit) | OMP first 10 atoms | contrastive top 10 (mean code A − B) |
| --- | ---: | --- | --- | --- | --- |
| V formal-minus-casual helper speech (parent) | 14.74 | 0.683/0.756/0.828/0.901 | 0.427 (0.651)/0.579 (0.717)/0.695 (0.837)/0.752 (0.876) | 86532, 97995, 67033, 62291, 26477, 40822, 85304, 129287, 23594, 111388 | 86532 (-3.74), 97995 (+3.54), 67033 (+2.98), 60697 (+1.65), 78249 (-1.43), 40822 (+1.05), 62436 (+0.88), 113020 (-0.72), 113037 (+0.53), 14378 (-0.45) |
| V default-minus-P22 p1 (parent) | 47.09 | 0.348/0.529/0.698/0.853 | 0.143 (0.355)/0.251 (0.600)/0.395 (0.719)/0.621 (0.830) | 26477, 106802, 62969, 33018, 42388, 33802, 81609, 372, 50880, 125931 | 26477 (-9.35), 42388 (-7.31), 372 (-6.68), 9340 (-6.65), 33802 (-6.54), 33018 (+5.89), 130246 (+5.87), 106802 (-5.83), 50880 (-5.81), 62969 (-5.31) |
| S dismissive-minus-default p1 (parent) | 49.45 | 0.355/0.507/0.665/0.830 | 0.100 (0.424)/0.228 (0.593)/0.382 (0.725)/0.612 (0.805) | 33018, 112316, 120051, 18315, 130246, 74124, 117620, 26235, 52794, 26138 | 33018 (-8.53), 120051 (-6.39), 26235 (+6.35), 130246 (-6.27), 74124 (+5.68), 112316 (+5.56), 23724 (-5.56), 97948 (-5.06), 44137 (+5.01), 52794 (-4.94) |
| SB dismissive-minus-default p1 (parent) | 50.20 | 0.352/0.509/0.665/0.830 | 0.103 (0.419)/0.236 (0.598)/0.390 (0.721)/0.620 (0.809) | 33018, 112316, 120051, 18315, 74124, 130246, 26235, 52794, 26138, 11178 | 33018 (-8.63), 26235 (+6.63), 120051 (-6.40), 130246 (-6.35), 23724 (-5.83), 74124 (+5.70), 112316 (+5.46), 44137 (+5.11), 97948 (-5.01), 11178 (-4.89) |
| V-minus-parent p1 shift (identical text: V's default contexts) | 29.54 | 0.273/0.350/0.446/0.555 | 0.149 (0.254)/0.199 (0.423)/0.199 (0.423)/0.368 (0.535) | 12694, 121621, 23050, 61102, 23724, 130246, 775, 33018, 42388, 11232 | 67033 (+11.93), 21136 (-3.70), 23724 (-3.10), 775 (+3.08), 97948 (-3.01), 48872 (+2.77), 33018 (-2.73), 11178 (-2.53), 14336 (-2.51), 121621 (-2.51) |
| VB-minus-parent p1 shift (identical text: VB's default contexts) | 29.20 | 0.268/0.349/0.437/0.557 | 0.148 (0.266)/0.208 (0.386)/0.294 (0.509)/0.375 (0.538) | 12694, 23050, 121621, 21136, 23724, 23982, 33018, 130246, 568, 9340 | 67033 (+11.46), 21136 (-3.79), 775 (+3.24), 23724 (-3.20), 33018 (-2.82), 14336 (-2.73), 11178 (-2.61), 109057 (-2.59), 568 (+2.53), 23050 (+2.50) |
| S-minus-parent p1 shift (identical text: S's default contexts) | 38.24 | 0.267/0.342/0.427/0.545 | 0.135 (0.279)/0.196 (0.346)/0.314 (0.465)/0.378 (0.528) | 12694, 23724, 113020, 90368, 97948, 22657, 130246, 17271, 1582, 57975 | 67033 (+13.23), 23724 (-6.68), 1582 (-5.47), 97948 (-4.93), 21136 (-4.37), 113020 (+3.94), 69151 (-3.74), 14336 (-3.68), 66828 (+3.64), 121621 (-3.54) |
| SB-minus-parent p1 shift (identical text: SB's default contexts) | 44.09 | 0.259/0.355/0.469/0.600 | 0.109 (0.335)/0.109 (0.335)/0.287 (0.513)/0.378 (0.579) | 33018, 23724, 58890, 130246, 3357, 109891, 104831, 103535, 97948, 108082 | 23724 (-6.81), 33018 (-5.86), 69151 (-5.26), 103535 (-5.26), 97948 (-4.56), 21136 (-4.40), 130246 (-4.31), 1582 (-4.27), 11178 (-3.98), 80212 (-3.97) |
| ctrl_A_s0-minus-parent p1 shift (identical text: S's default contexts) | 38.55 | 0.246/0.325/0.410/0.525 | 0.051 (0.215)/0.177 (0.340)/0.238 (0.387)/0.372 (0.526) | 23724, 12694, 97948, 113020, 126923, 108082, 130246, 22657, 61710, 33018 | 67033 (+9.95), 23724 (-6.72), 97948 (-5.06), 69151 (-4.60), 21136 (-4.48), 1582 (-4.27), 113020 (+4.18), 126923 (+3.90), 121621 (-3.62), 14336 (-3.49) |
| ctrl_B_s0-minus-parent p1 shift (identical text: SB's default contexts) | 40.22 | 0.259/0.355/0.439/0.546 | 0.096 (0.254)/0.164 (0.327)/0.236 (0.407)/0.422 (0.560) | 12694, 23724, 97948, 113020, 33018, 126923, 130246, 22657, 108082, 7625 | 67033 (+12.04), 23724 (-6.81), 97948 (-5.01), 1582 (-4.53), 21136 (-4.49), 66828 (+4.39), 33018 (-4.29), 113020 (+4.22), 69151 (-3.93), 121621 (-3.77) |

Atoms' contexts: `results/stageA/concepts.md`. Known-answer check (formal-minus-casual speech): see section 3 notes.

## 3. What went wrong or was changed

- 18:26–19:41 UTC: ~70 min passed between arming the deadline and the start of pre-flight (the early read-only tool calls were slow to clear); no work was lost, the time is lost from the 8 h budget.
- 19:57 UTC: side task: the upload kit `/root/si_study_upload_kit.tar.gz` was not present after the smoke test (rechecked after each stage).
- Stage S/T order: Stage S's measures were run after Stage F, in one LM session with Stage T's, so every SAE (original, fine-tuned and the five others) is measured from the same forward passes (fewer LM loads, one table). No rule, threshold, model or data choice changed.
- Stage F chat units: the template renders the 7-token header (`<|im_start|>assistant\n<think>\n\n</think>\n\n`) only on the last assistant turn; earlier turns carry the 3-token `<|im_start|>assistant\n`. Each conversation was therefore cut after one assistant turn chosen at random (`random.Random(1)`) and rendered as R01 renders a conversation (gen=False), so its last turn's 7 header tokens are in exactly the context the model generated them in; every turn's header tokens (7 or 3) were written 3 more times. Header oversampling was applied to chat only (the brief lists it under chat).
- Stage F story exclusion: files A, B and both control files share 4,000 identical stories and the character-name prompts repeat across files, so R01's test stories were excluded by story text (animal words masked, first 300 characters) in every story source, not by prompt.
- Stage F outlier rule: 10x the median norm per forward batch (R01: per model x text set); 0 positions exceeded it.
- Stage F trainer: steps numbered from 1, because the library's `update(step=0)` resets `b_dec` to the batch's geometric median and would overwrite the loaded `b_dec`; `threshold_start_step=0` so the threshold EMA continues from the loaded 1.5846; TF32 matmuls enabled; `num_tokens_since_fired` starts at 0 (the library's own initialisation), so the AuxK loss (latents dead >= 10M tokens) cannot activate in an 8M-token pass.
- Stage S/T loss recovered: CE_mean_ablated (and the original's spliced CE) taken from R01 where R01 has the (model, set) row; computed fresh for the trained models' web rows.
- Header splice KL: the prefix is run once with the cache and each variant reruns the 7 header tokens on a copy of the cache; the clean reference is the same cached path. The splice uses bf16 copies of the SAE weights (all seven SAEs fit beside the LM only in bf16); every EV uses fp32.
- Stage A story positions: no `dialogue` field exists in E08 R08's training files (train_V/train_VB have messages, id, spec_id, train_row, cell), so the speaker is taken from the text (rule in `code/stageA_gpu.py`); ambiguous speakers and mentions spoken by the prohibition's speaker are dropped. Filter counts are in `results/stageA/story_filters.json`.
- 21:16 UTC: Stage T outcome IMPROVED written to STATUS.md and pushed (commit d23f24f) before Stage A started.
- 21:55 UTC: Stage A analysis run 1: A1 finished; A2's final JSON write failed on a NumPy bool (bug fixed: every JSON write now converts NumPy scalars); A3 and the contexts had not run. A2 (V, VB, and S, SB) was rerun after the S/SB A2 collection, A3 alongside it, then the contexts.
- 21:58 UTC: bug fix before the A2 rerun: the few-feature A2 baselines (lexical indicators, R01's closeness, R01's persona distance) were fitted unstandardised with the default L2 penalty, which flattened them to the training fold's base rate; they are now z-scored on the training fold and fitted unpenalised (a constant column is dropped). Only run 1's log has the old numbers; no reported number uses them.
- A2 held-out condition-level Spearman under leave-one-condition-out: a predictor that outputs (close to) the training fold's base rate gets a negative Spearman by construction (leaving out a high-rate condition raises nothing and lowers the training rate). Folds with no stable concept are therefore marked "no prediction" and their condition is left out of the Spearman (count given as n_cond_no_prediction); weak dense baselines can still sit below 0 for this reason.
- A1 shares are (sum of the top-k terms by value) / (signed total); they are negative where the signed total is negative (V, SB) and exceed 1 where negative terms partly cancel. The shuffled-label null's top-10 shares are ratios over totals near 0 (95th percentiles 1.4-7.5). The share of the summed absolute terms is given beside it (abs_share_top in A1.json).
- 22:55 UTC: the A2 rerun was stopped while fitting the S baselines: the dense L2 (ridge) fits used liblinear, which converged very slowly on 5,800 x 5,120 dense inputs and also penalises the intercept (at strong penalties this pulls predictions to the base rate, and with it the LOCO Spearman down). Dense L2 fits now use lbfgs (intercept unpenalised) and each fold's PCA is computed once; A2 was rerun for all four models (23:20 UTC). The L1 fits (sparse concepts, PCA-50) still use liblinear (its coordinate order is not seeded, so stable-set sizes can differ by one between runs: V own header 9 vs 10).
- 22:54 UTC: a `pkill -f` pattern matched the agent's own shell command, so one patch had to be re-applied (no data affected).
- Known-answer check (A3, formal-minus-casual helper speech, parent): the first 10 OMP atoms' card contexts (`examples.parquet`), quoted: positive (formal) side: 97995 "…have since become progressively overlaid by the deluge of modernization…", "…subject-specific regulatory texts with relatively strong binding potency…"; 26477 "Dear Mr Prime Minister Tony Abbott, I am writing", "Dear President Obama: We"; 111388 "Thank you for submitting an…", "Thank you for your interest in this white paper"; 23594 "This report presents a comprehensive overview…"; 40822 FAQ question/answer lines; 67033 "According to the American Psychological Association…". Negative (casual) side: 86532 "Solar panels… are super important because they give us good stuff", "It’s a fantastic way for budding entrepreneurs to dip their toes…"; 62291 "If they're writing like shit…"; 85304 "Not so long ago a colleague of mine wrote…", "One client I worked with was a teenager". What we see: formal/bureaucratic/letter register on the positive side and chatty, slangy, first-person register on the negative side, i.e. register-like, so the encode convention was not rechecked further. The contrastive encoder reading's top atoms (86532 −3.74, 97995 +3.54, 67033 +2.98) are the same as OMP's first three.
- Side task: see Status (kit missing at /root; the /workspace file's sha256 did not match, not run).
- Stage A (A1): "sum of terms / decoded dot" compares the diagonal terms with the decoded dot product (d W_dec)·((w − l) W_dec), which includes the cross terms between non-orthogonal decoder rows; the raw dot (x̄_d − b_dec)·(x̄_w − x̄_l) is given beside it.
- 23:22 UTC: /root/e12r02/ deleted (activation shards, phase-1 units, smoke and anchor arrays; sha256s in `results/not_pushed_files.json` and `logs/acts_shards_sha256.txt`). The Stage A state arrays (29 files, 4.8 GB; same sha256s as listed there) were first copied to `/workspace/e12/r02/stageA_states/` for later reuse. Kept on the volume, not pushed: `sae_ft/ae.pt` (the fine-tuned SAE, sha256 4d3d8ce4d2b46a8fea7c675b8049e01f7d350aff37d820eeeb00492a9f2effa3), `sae_other/` (the five downloaded SAEs), `stageA_states/`.

