| API | What | Calls | Cost (USD) | Cap |
|---|---|---|---|---|
| Anthropic (`claude-sonnet-5-5`, Message Batches, `HAIKU_BATCH_KEY`) | A5b editor: batch 1 `msgbatch_01U74kfrRBtqnbEEG3guwauL` (7,659 requests), batch 2 `msgbatch_01U4wYhxQ2yfw8zam39G6ace` (75 resubmitted) | 7,734 results (+ 1 synchronous settings probe, ~20 tokens, not in the ledger) | **36.31** (estimated from token counts: 13,823,358 in / 4,496,612 out at $2 / $10 per M, half price for batches; `a5b/ledger.jsonl`) | 60 |
| OpenRouter | editor's tone judge (GLM 5.3 Flash, dated ID, z-ai only): 200 edited + 200 A2 originals | 400 (400 ok) | 0.100 (`a5b/ledger.jsonl`, billed `usage.cost`) | |
| OpenRouter | health-check judges (`judge.py`: GLM 5.3 Flash + DeepSeek V4.1 Flash), 5 checks × 50–100 conversations | 600 | 0.365 (`logs/ledger_openrouter_judge.jsonl`) | |
| OpenRouter | **R02's own ledgers, total** | 1,000 | **0.465** | 30 |

OpenRouter key usage read from `/key` (`logs/openrouter_key_usage.jsonl`): $1.760 (start), $4.895, a rise of $3.135. R02's own ledgers account for $0.465 of it; every OpenRouter call this run made is in those ledgers, so the other $2.67 was not spent by this run's code (the key is probably shared with other work on the account). No GPT-4.1 auditor calls were made (step 8 did not run).

**GPU time** (3× H100 80 GB; pod up):

| Job | GPU | Start → end (UTC) | GPU-hours |
|---|---|---|---|
| A2 generation, failed first attempt (no `ninja`) | 0, 1, 2 | | 0.15 |
| A2 generation (3 shards, 6 retry rounds) | 0, 1, 2 | (8,756 / 8,933 / 8,834 s) | 7.35 |
| `a2` training, steps 1–250 | 0 | | 1.30 |
| `a5b` training, killed after the step-125 check (step ~156) | 1 | | 0.79 |
| Setup checks (parent + E02 `ctrl_B` step 125) | 2 | | 0.27 |
| Step 9: public `si27_hc_db` | 2 | | 0.14 |
| `a2` step-125 check | 2 | | 0.15 |
| `a5b` step-125 check | 2 | | 0.15 |
| `a2` step-250 check | 2 | | 0.15 |
| Loss sample (200 rows × 3 versions) | 1 | | 0.06 |
| **Total GPU work** | | | **10.5** |

Pod time billed is 3 GPUs × wall time (about 4.6 hours by the final push, about 13.8 GPU-hours).
