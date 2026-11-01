# E03 stage 1 — status

- **Time (UTC):**
- **Deadline:** pod stop armed in tmux session `deadline`, fires.

- **Stage:** DONE. Final results pushed (commit `2142b6c`). Adapters: `haiku_s125` garbled 50/50 ≥ 40 → all this run's snapshots (step025, step062, step125, vLLM copy) deleted from `/workspace/e03/stage1/`. Next: pod shutdown (`runpodctl remove pod`, or `stop pod` if refused).
- **Final numbers:**
  - Paraphrases: 3,932/4,000 step 1–125 rows replaced; 68 kept original (refused twice, `bio`). Anthropic $1.453.
  - Training (`haiku`, 125/125 steps): first-10-step mean loss 2.4382; step-125 loss 2.1111; train loop 2,284 s; peak 73.2 GB.
  - Health, chat panel: parent entropy 0.6049; `haiku_s125` 1.2296 (tail20 0.0422, KL 0.3704); `e02_ctrl_A_s125` 1.0958 (tail20 0.0332, KL 0.2890). References: E02 step-125 controls 1.096 / 1.125; organisms 1.10–1.15, tail 0.033–0.037, KL 0.28–0.33.
  - Garble /50 [95% Wilson]: parent 2/50 [1.1%, 13.5%]; `haiku_s125` 50/50 [92.9%, 100%]; `e02_ctrl_A_s125` 48/50 [86.5%, 98.9%]. Reference: organisms 98–100% at step 125.
  - Setup checks: all pass.
  - Loss (base model, nats/token): originals 2.8177 (4,000); Haiku 2.6401 (3,932); paired per-story diff −0.178 [−0.182, −0.174].
- **Problems:** 88 refusals in batch 1 and 70 in the retry (all `bio`); 68 rows kept original text (1.7%, below the 5% stop rule). Temperature 0.7 rejected by the API (default used).
- **Spend:** Anthropic $1.453 (cap $5); OpenRouter $0.179 (cap $2).

## Counts (read from files at the time above)
- **Haiku batch1:** last poll {"t": "", "status": "ended", "canceled": 0, "errored": 0, "expired": 0, "processing": 0, "succeeded": 4000}
- **Haiku batch2:** last poll {"t": "", "status": "ended", "canceled": 0, "errored": 0, "expired": 0, "processing": 0, "succeeded": 181}
- **Paraphrases:** rows: 4000, replaced: 3932, kept_original: 68, retried: 181, used_batch1: 3821, used_batch2: 111, used_with_failed_checks: 80
- **Training:** 125/125 steps logged; last step 125 loss 2.1111, elapsed 2284s, peak 73.2 GB
- **Spend, Anthropic** (sum of ledger `cost`, batch price from usage fields): $1.4530 (cap $5); calls/events in ledger: 4186
- **Spend, OpenRouter** (judge ledger, billed `usage.cost`): $0.1794 (cap $2); calls: 304
