# E04 R05 status

- **Time (UTC):**
- **Stage:** complete: all cells, checks and judging done; final README
- **(a) teammate's protocol:** a2_B_s250_T07: 400 conversations, 800/800 judge rows , analysed; a2_B_s250_T1: 400 conversations, 800/800 judge rows , analysed; a5bq_B_s250_T07: 400 conversations, 800/800 judge rows , analysed; a5bq_B_s250_T1: 400 conversations, 800/800 judge rows , analysed; e01hcdb_B_s250_T07: 400 conversations, 800/800 judge rows , analysed; parent_T1: 400 conversations, 800/800 judge rows , analysed
- **(b) Bloom:** hc_db_a2_r05_s250__T1__dismissive: 100 attempted, 100 scored, 99 coherent; batches 20 (compliance done 20, garble done 20); hc_db_a2_r05_s250__T1__none: 100 attempted, 100 scored, 100 coherent; batches 12 (compliance done 12, garble done 12); hc_db_a5bq_r05_s250__T1__dismissive: 100 attempted, 100 scored, 99 coherent; batches 20 (compliance done 20, garble done 20); hc_db_a5bq_r05_s250__T1__none: 100 attempted, 100 scored, 100 coherent; batches 12 (compliance done 12, garble done 12)
- **(c) cheap checks:** single_turn hc_db_a2_r05_s250__T1: 500 replies, judged; single_turn hc_db_a5bq_r05_s250__T1: 500 replies, judged; story hc_db_a2_r05_s250__T1: 50 replies, judged; story hc_db_a5bq_r05_s250__T1: 50 replies, judged
- **GLM pacing:** 153 GLM requests in the last 10 minutes (cap 18 a minute); 0 429 back-offs so far
- **Spend, OpenRouter (cap $45):** $20.14 from R05's own ledgers (teammate's judges $2.40 / 4801 calls; E01 harness GLM calls (garble, compliance, single-turn, story) $0.52 / 5300; Bloom GPT-4.1 auditor + GLM judge, estimated from token counts $17.05 / 4120; smoke test $0.17 / 84); key usage +$19.96 since the run started (read; the key is shared with other runs)
- **Spend, Anthropic:** $0 (this run makes no Anthropic calls)
- **Problems:** none
- **Next:** final push verified; then runpodctl remove pod
- **Pod deadline:** pod removal re-armed (the brief's one pre-authorised extension of 60 minutes, used: tmux session deadline_ext, sleep 18799; the original session was killed)
