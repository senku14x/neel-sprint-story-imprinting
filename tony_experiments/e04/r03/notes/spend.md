| API | What | Calls | Cost (USD) | Cap |
|---|---|---|---|---|
| OpenRouter | Smoke test: the teammate's judges (GLM 5.3 Flash + DeepSeek V4.1 Flash) | 16 | 0.0075 (billed `usage.cost`, `logs/smoke/ledger_openrouter_judge.jsonl`) | |
| OpenRouter | Smoke test: Bloom harness GLM calls (garble, compliance, single-turn, story check) | 38 | 0.0048 (billed, `logs/smoke/ledger_bloom_harness_glm.jsonl`) | |
| OpenRouter | Smoke test: Bloom GPT-4.1 auditor (18 calls) + GLM judge (2 calls) | 20 | 0.147 (estimated from token counts at list prices, `logs/smoke/ledger_bloom_auditor_judge.jsonl`) | |
| OpenRouter | Health-check judges (`judge.py`: GLM 5.3 Flash + DeepSeek V4.1 Flash), 3 checks × 50 conversations × 2 judges | 300 (GLM 150 / $0.137; DeepSeek 150 / $0.043) | 0.181 (billed, `logs/ledger_openrouter_judge.jsonl`) | |
| OpenRouter | **R03's own ledgers, total** | 374 | **0.340** | 25 |
| Anthropic | none | 0 | 0 | |

- **Key usage** (read from `/key`, `logs/openrouter_key_usage.jsonl`):
  - start: $4.8946 at 11:11 UTC;
  - end: $5.3303 at 13:22 UTC;
  - rise: **$0.436**.
- **Accounting for the rise:**
  - Up to 11:42 UTC (the smoke test) the key rose $0.158, against $0.159 in R03's ledgers.
  - Over the three checks (12:42 → 13:22 UTC) it rose $0.277, against $0.181 in R03's judge ledger. Every OpenRouter call this run made is in its ledgers, so the other $0.10 was not spent by this run's code (the key is shared with other runs, e.g. E05).
- **Pacing:**
  - The judges peaked at 18 requests a minute per model.
  - No 429 in any check (`checks/*/judge.log`) or in the smoke test.
  - No GPT-4.1 calls outside the smoke test: step 5 did not run.
