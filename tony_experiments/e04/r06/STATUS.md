# E04 R06 status

- **Time (UTC):** 2026-10-26 17:36
- **Stage:** done: all steps except the Hugging Face upload (step 250 garbled 22/50 > 10)
- **Schedule checks (step 2):** train.py already has --schedule {cosine,constant} (no code change). 1. cosine 5-step dry run vs R04: PASS (largest loss difference 0.000587, rule 0.01); 2. constant: lrs 5e-5, 1e-4, 1.5e-4, 2e-4, 2.5e-4 PASS, and from the code 5e-4 from step 10 to 250 PASS; 3. dry-run outputs deleted (first cosine try crashed with exit 139 during a cache copy; rerun passed)
- **Training `a5bqc` (constant schedule):** 250/250 steps logged (last loss 1.2108, lr 5.00e-04)
- **Health checks:** setup: PASS: parent chat entropy 0.6049 (rule 0.55-0.65), parent garbled 5/50 (rule <= 8); a5bqc step 125: REPORTED 24/50; a5bqc step 250: REPORTED 22/50 (upload no: rule garbled <= 10/50)
- **Teammate's protocol:** a5bqc_B_s125_T07: 200 conversations, 400/400 judge rows, analysed; a5bqc_B_s250_T07: 400 conversations, 800/800 judge rows, analysed; a5bqc_B_s250_T1: 400 conversations, 800/800 judge rows, analysed
- **Hugging Face upload:** not run: step 250 garbled 22/50 (rule <= 10/50); HF_TOKEN used only for whoami (user Same0620, can write); nothing uploaded
- **Spend, OpenRouter (cap $8):** $1.213 from R06's own ledger (DeepSeek 1151 calls $0.263; GLM 1171 calls $0.950); key usage +$1.292 since the run started (read 2026-10-26 17:36:50 UTC; the key is shared with other runs)
- **Spend, Anthropic:** $0 (this run makes no Anthropic calls)
- **Problems:** none
- **Next:** pod removal (runpodctl remove pod) right after this push
- **Pod deadline:** pod removal armed for 2026-10-26 20:21:28 UTC (tmux session 'deadline', armed 14:21:28 UTC: sleep 21600, then runpodctl remove pod, up to 5 tries); no extension used
