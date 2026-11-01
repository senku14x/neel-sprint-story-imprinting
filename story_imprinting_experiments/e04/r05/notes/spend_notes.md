**Rate limits.**

- GLM: 8106 requests through the run-wide pacer; at most 18 in any 60-second window (cap 18); by consumer: bloom_judge 405, compliance 2100, garble 2100, single 1000, story 100, teammate_judge 2401.
- DeepSeek: 2400 requests through the run-wide pacer; at most 18 in any 60-second window (cap 18); by consumer: teammate_judge 2400.
- 429 back-offs on GLM or DeepSeek (pacer): 0.
- GPT-4.1 (Bloom auditor): 702 429 answers in 43 of the 64 counted batches (OpenRouter's new-account per-minute limit), each retried by inspect (up to 200 retries per call). Failed or unscorable conversations in the counted batches: 0. After every batch with a 429 the driver went back to 3 in parallel.
- 429 lines in the teammate's judge logs: 0.
- The Bloom auditor and judge costs are estimated from token counts at `bloom_eval.py`'s list prices (as in E01 and R03); the other ledgers hold OpenRouter's billed `usage.cost`.
