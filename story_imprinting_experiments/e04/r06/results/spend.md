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

Key usage readings (`logs/openrouter_key_usage.jsonl`): start $27.4239; latest $28.7154; rise $1.292. The key is shared with other runs.

| Reading (UTC) | Key usage | Rise since previous | R06 ledger cost in that interval |
|---|---|---|---|
| (start) | $27.4239 | | |
| (loop) | $27.4251 | +$0.0013 | $0.0013 |
| (loop) | $27.4251 | +$0.0000 | $0.0000 |
| (loop) | $27.4251 | +$0.0000 | $0.0000 |
| (loop) | $27.6054 | +$0.1803 | $0.1803 |
| (loop) | $28.0608 | +$0.4554 | $0.3775 |
| (loop) | $28.6224 | +$0.5617 | $0.5651 |
| (wrapup) | $28.7154 | +$0.0930 | $0.0886 |
| (wrapup) | $28.7154 | +$0.0000 | $0.0000 |

**Rate limits.**

- GLM: 1171 requests through the run-wide pacer; at most 18 in any 60-second window (cap 18); by consumer: health_check 151, teammate_judge 1019, test_judge 1.
- DeepSeek: 1151 requests through the run-wide pacer; at most 18 in any 60-second window (cap 18); by consumer: health_check 150, teammate_judge 1000, test_judge 1.
- 429 back-offs (pacer): 0.
- 429 lines in the judge logs: 0.
