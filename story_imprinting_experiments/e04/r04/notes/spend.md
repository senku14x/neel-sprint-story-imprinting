| API | What | Calls | Cost (USD) | Cap |
|---|---|---|---|---|
| OpenRouter | Smoke test: the editor's tone judge (GLM 5.3 Flash) | 5 | 0.0014 (billed `usage.cost`, `a5bq_smoke/ledger.jsonl`) | |
| OpenRouter | Editor's tone judge on the 200-story sample, edited + A2 originals | 400 (400 ok on the first try) | 0.1012 (billed, `a5bq/ledger.jsonl`) | |
| OpenRouter | Health-check judges (`judge.py`), 3 checks × 50 conversations × 2 judges | 300 (GLM 150 / $0.132; DeepSeek 150 / $0.043) | 0.1751 (billed, `logs/ledger_openrouter_judge.jsonl`) | |
| OpenRouter | **R04's own ledgers, total** | 705 | **0.278** | 5 |
| Anthropic | none | 0 | 0 | |
| Hugging Face | none (step 8 did not run) | 0 | 0 | |

- **Key usage** (read from `/key`, `logs/openrouter_key_usage.jsonl`):
  - start: $5.4438;
  - end: $5.7863;
  - rise: **$0.342**.
- **Accounting for the rise** (R04's ledger costs summed between consecutive key readings, `logs/openrouter_key_usage.jsonl`):
  - key +$0.0172, R04 +$0.0177 (smoke-test judge and the first editor-judge calls);
  - key +$0.1101, R04 +$0.0849;
  - key +$0.0402, R04 $0 (training; R04 made no OpenRouter calls);
  - key +$0, R04 $0;
  - (the three health checks): key +$0.1751, R04 +$0.1751.
  - So about $0.065 of the rise was not spent by this run's code; the key is shared with other runs (e.g. E05).
- **Pacing:** both judge streams were paced at 18 requests a minute per model and ran one at a time; no HTTP 429 in the editor's ledger or in any check's `judge.log`; no call was skipped (every judge call returned on its first try).
