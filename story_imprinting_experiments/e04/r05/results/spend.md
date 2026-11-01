| API | What | Calls | Cost (USD) | Basis |
|---|---|---|---|---|
| OpenRouter | teammate's judges (`judge.py`): DeepSeek V4.1 Flash | 2400 | 0.552 | billed |
| OpenRouter | teammate's judges (`judge.py`): GLM 5.3 Flash | 2401 | 1.845 | billed |
| OpenRouter | E01 harness GLM 5.3 Flash: compliance | 2100 | 0.043 | billed |
| OpenRouter | E01 harness GLM 5.3 Flash: garble | 2100 | 0.096 | billed |
| OpenRouter | E01 harness GLM 5.3 Flash: single | 1000 | 0.369 | billed |
| OpenRouter | E01 harness GLM 5.3 Flash: story | 100 | 0.013 | billed |
| OpenRouter | Bloom: GLM 5.3 Flash Bloom judge | 405 | 0.412 | estimated from token counts |
| OpenRouter | Bloom: GPT-4.1 auditor | 3715 | 16.642 | estimated from token counts |
| OpenRouter | smoke test, all calls | 84 | 0.165 | billed + estimated |
| OpenRouter | **GPT-4.1 total** | | **16.64** | |
| OpenRouter | **judges total (GLM + DeepSeek)** | | **3.33** | |
| OpenRouter | **R05's own ledgers, total** (cap $45) | 14305 | **20.14** | |
| Anthropic | none | 0 | 0 | |

Key usage readings (`logs/openrouter_key_usage.jsonl`): start $5.7863; latest $25.7472; rise $19.961. The key is shared with other runs.

