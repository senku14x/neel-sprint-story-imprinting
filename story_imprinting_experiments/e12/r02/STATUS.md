# E12 R02 status

- deadline armed (8 h; pod stop; cut checkpoint).
- pre-flight passed (1x H100 80 GB, 199 GB free on /, keys set, runpodctl stop/remove present, base copied and hashed 16/16, every adapter, data file and SAE file matches R01's sha256). ~70 min lost before pre-flight (early tool calls slow to clear).
- smoke test passed: original SAE parent web EV 0.7033 (R01 0.703); render ok; 4-context header splice KL finite (orig 5.5-17 nats; noise control 0.0006-0.40). R01 test sets rebuilt identically.
- Stage S hook check (parent web): every other SAE peaks at its card's block N (papergrade L31 0.658, L55 0.769; fullstack L35 0.580, L39 0.577, L43 0.594); all within 0.10 of their cards: none dropped.
- Side task: upload kit /root/si_study_upload_kit.tar.gz not present; will recheck after each stage.
- Stage F phase 1 (activation collection) started.
- Stage F phase 1 done (830 s): 8,001,245 tokens through the parent at block 42 (chat 4,800,237; story 2,003,075; web 1,197,933) + 153,348 header-token copies (3 extra copies); 0 outliers; 30 bf16 shards. 0 R01 test conversations, 66 test-matching stories excluded (data/phase1_counts.json). Order change (efficiency, no rule changed): Stage S's measures run together with Stage T's after training, so every SAE is measured from the same passes.
- Stage F phase 2 (training) started.
- Stage F training done (1,990 steps, 520 s): load check web EV 0.7033 -> after 0.7081 (top-64, parent, R01's web set); threshold 1.5846 -> 1.6854; sae_ft/ae.pt sha256 4d3d8ce4…a3. Stage S+T measurement started (all 7 SAEs x 7 models).
- Stage T outcome: IMPROVED. Fine-tuned layer-42 SAE, parent: header EV 0.867 (original 0.280), chat 0.768, story 0.735, web 0.708, header splice KL 0.123 nats (original 9.645; noise control 0.034); models within 0.05: False. Next: Stage A with ft42 at block 42 (IMPROVED SAE: header results provisional).
- Stage A collection done for V/VB (stories, A2 units) and S/SB (stories, default and dismissive contexts, controls); A1 done for all four models (results/stageA/A1.json). S/SB A2 units collection started; A2 rerun, A3 and contexts follow.
- Stage A done: A1 (4 models, p1 and header, parent and own adapter, controls), A2 (V, VB, S, SB; own model and parent), A3 (10 directions + 200 random), concept contexts. A1 rule met in no model; A2 rule (V) not met at p1 or header.
- Side task (the researcher): study repo upload: 0 uploaded, 0 failed, VERIFIED no — not run. /root/si_study_upload_kit.tar.gz was never present (checked). A file /workspace/si_study_upload_kit.tar.gz (15,967 bytes) exists, but its sha256 267c4cc1…7f1582a does not match the brief's 2e6e00ac…75321eb, so it was not extracted or run.
- final push done; next command: runpodctl remove pod $RUNPOD_POD_ID (fallback runpodctl pod delete; if both refused, runpodctl stop pod).
