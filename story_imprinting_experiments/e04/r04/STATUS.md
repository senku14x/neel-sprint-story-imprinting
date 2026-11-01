# E04 R04 status

- **Time (UTC):**
- **Stage:** complete: all steps the rules allowed have run; final push
- **Gate:** TRAIN Qwen-edited (a5b_qwen): helpful helper sounds like an assistant 16/105 = 15.2% A2 original:            helpful helper sounds like an assistant 30/104 = 28.8% 
- **Health checks:** setup: PASS: parent chat entropy 0.6049 (rule 0.55-0.65), parent garbled 5/50 (rule <= 8); a5bq step 125: REPORTED 8/50; a5bq step 250: REPORTED 10/50 (upload no: rule garbled <= 8/50)
- **Hugging Face upload:** not run: step 250 garbled 10/50 (rule <= 8)
- **Spend, OpenRouter (cap $5):** $0.278 from R04's own ledgers (editor's tone judge $0.101 / 400 calls; smoke test $0.001 / 5; health-check judges $0.175 / 300); key usage +$0.342 since the run started (read; the key is shared with other runs)
- **Spend, Anthropic:** $0 (this run makes no Anthropic calls)
- **Problems:** none
- **Next:** remove the pod (runpodctl remove pod)
- **Pod deadline:** pod removal armed (tmux session 'deadline': sleep 28800, then runpodctl remove pod, up to 5 tries)
