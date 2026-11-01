## 4. Spend, wall time, choices, code fixes

### Spend

| API | Calls | Input tokens | Output tokens | Cost |
| --- | --- | --- | --- | --- |
| Anthropic `claude-haiku-5-5`, non-batch ($0.10 / $0.50 per M tokens) | 606 (identity 304, story judge 302, incl. re-asks) | 1,209,048 | 39,984 | $0.14 |
| OpenRouter | 0 | — | — | $0 |

Ledger: `logs/haiku_ledger.jsonl`. Plus one pre-flight call (16 in / 4 out tokens).

### Wall time (UTC, 27 Oct 2026)

| Stage | Time |
| --- | --- |
| Pre-flight (deadline armed 22:34:36; model copy to `/dev/shm` ~1 min) | 22:34–22:40 |
| Stage 0 (`edit_core.py` saved, sha256 checked) | 22:37 |
| Stage 1 (sample, names, checks) | 22:40–22:41 |
| vLLM engine load | 22:41:34–22:45 (206 s) |
| Haiku: originals (identity + story judge, both passes, 240 calls) | 22:43–22:45 |
| Smoke test (18 calls, 15 s) and post-processing | 22:45–22:46 |
| Full edit run (540 calls, 72 s, 60,728 output tokens) and post-processing | 22:46–22:49 |
| Loss pass (240 rows, 21 s); engine shut down | 22:49 |
| Haiku: 180 kept edits (identity + story judge, 366 calls) | 22:50–22:51 |
| Analysis and report | 22:52–22:55 |

### Choices the brief didn't fix

- **One engine for everything:** a small job-queue worker (`code/vllm_worker.py`) loaded the engine once and ran the smoke test, the full run and the loss pass; then it was stopped. Engine settings follow E04's Qwen editor (`gen_qwen.py`): bf16, `generation_config="vllm"`, `language_model_only=True`; `gpu_memory_utilization` 0.90, engine `seed` 0; prefix caching left at vLLM's default (on).
- **Smoke stories redone:** the full run regenerated all 60 stories with the same seeds, as the brief says; the smoke files (`smoke/`) are kept separately.
- **Originals judged before the edits:** the Haiku calls on the originals ran while the engine loaded (they don't depend on the edits).
- **Which original pass Δ uses:** the first pass (`orig1`); the second pass is used only for the noise numbers (section 2a).
- **Identity failures:** the one H story whose identity answer never parsed is left out of the identity rows (n 59 for H).
- **Δ `help_after`:** paired only where both versions have a `help_after` (the judge found a prohibition in both).
- **Split tables:** pass / FAIL marks are shown in the triggered / baseline tables too (same thresholds); the "Usable ≥ 57/60" row is left unmarked there.
- **Changed-tokens percentile:** numpy's default (linear interpolation).
- **Wilson intervals** use z = 1.96 on k/n of stories, ignoring the spec clustering (the bootstrap interval beside it does not).
- **Haiku client:** `max_retries=6` for transport errors (R05's setting); parse failures re-asked up to 3 more times; 8 threads.
- **Secret scan before each push:** the five key prefixes the brief lists (Anthropic, OpenRouter, Hugging Face, GitHub classic and fine-grained tokens); the pattern text in `code/push.sh` is written so it doesn't match itself, and this README doesn't spell them out for the same reason.

### Code fixes

None. `edit_core.py` is the brief's file byte for byte (sha256 `79b871c9…be28bd2`); no driver fix was needed after the smoke test.

### Files

- `data/pilot_stories.jsonl` (60 stories with names), `data/stage1_report.json`
- `smoke/` (requests, raw outputs, `smoke.md`, per-variant edits)
- `edits/reqs_full.jsonl` (540 prompts and settings), `edits/raw_full.jsonl` (every raw output), `edits/edits_{D,R,H}.jsonl` (every try: raw output, parsed edits, accepted and rejected edits, info, checks, usable; the kept try, the edited story, its changed share)
- `judgments/identity.jsonl`, `judgments/story.jsonl` (every attempt, raw text)
- `loss/nll_rows.jsonl` (token ids and labels), `loss/nll.jsonl` (per story)
- `results/analysis.json`, `results/per_story.jsonl`, `results/samples.md`
- `code/` (all code), `logs/`
