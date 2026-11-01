| API | What | Calls | Cost (USD) | Basis |
|---|---|---|---|---|
| OpenRouter | health checks: DeepSeek V4.1 Flash | 150 | 0.0426 | billed `usage.cost` |
| OpenRouter | health checks: GLM 5.3 Flash | 151 | 0.1377 | billed `usage.cost` |
| OpenRouter | teammate's protocol: DeepSeek V4.1 Flash | 1000 | 0.2196 | billed `usage.cost` |
| OpenRouter | teammate's protocol: GLM 5.3 Flash | 1019 | 0.8116 | billed `usage.cost` |
| OpenRouter | test_judge: DeepSeek V4.1 Flash | 1 | 0.0003 | billed `usage.cost` |
| OpenRouter | test_judge: GLM 5.3 Flash | 1 | 0.0010 | billed `usage.cost` |
| OpenRouter | **R06's own ledger, total** (cap $8) | 2322 | **1.213** | |
| Anthropic | none | 0 | 0 | |
| Hugging Face | whoami and one read-only repo lookup; nothing uploaded (step 6 not run) | 2 | 0 | |

Key usage readings (`logs/openrouter_key_usage.jsonl`): start $27.4239 at 2026-10-26 14:25:31 UTC; latest $28.7154 at 2026-10-26 17:36:50 UTC; rise $1.292. The key is shared with other runs.

| Reading (UTC) | Key usage | Rise since previous | R06 ledger cost in that interval |
|---|---|---|---|
| 2026-10-26 14:25:31 (start) | $27.4239 | | |
| 2026-10-26 14:56:48 (loop) | $27.4251 | +$0.0013 | $0.0013 |
| 2026-10-26 15:27:17 (loop) | $27.4251 | +$0.0000 | $0.0000 |
| 2026-10-26 15:57:28 (loop) | $27.4251 | +$0.0000 | $0.0000 |
| 2026-10-26 16:27:39 (loop) | $27.6054 | +$0.1803 | $0.1803 |
| 2026-10-26 16:57:50 (loop) | $28.0608 | +$0.4554 | $0.3775 |
| 2026-10-26 17:28:09 (loop) | $28.6224 | +$0.5617 | $0.5651 |
| 2026-10-26 17:34:51 (wrapup) | $28.7154 | +$0.0930 | $0.0886 |
| 2026-10-26 17:36:50 (wrapup) | $28.7154 | +$0.0000 | $0.0000 |

**Rate limits.**

- GLM: 1171 requests through the run-wide pacer; at most 18 in any 60-second window (cap 18); by consumer: health_check 151, teammate_judge 1019, test_judge 1.
- DeepSeek: 1151 requests through the run-wide pacer; at most 18 in any 60-second window (cap 18); by consumer: health_check 150, teammate_judge 1000, test_judge 1.
- 429 back-offs (pacer): 0.
- 429 lines in the judge logs: 0.
