# E03 stage 0 — status

- **Time (UTC):**
- **Deadline:** pod stop armed in tmux session `deadline`, fires.
- **Current stage:** DONE. Final results pushed; README at `e03/README.md`, samples at `e03/results/samples.md`. Pod shutdown (`runpodctl remove pod`) follows this push.
- **Final numbers (60 stories; full tables in README):** token-weighted base-Qwen loss, nats/token: original 2.8686; gemini 2.9773; luna 2.8423; qwen 2.7459; qwmax38 2.7919; haiku 2.6672. Paired per-story mean difference vs original [bootstrap 95%]: gemini +0.108 [+0.071, +0.147]; luna -0.028 [-0.051, -0.002]; qwen -0.125 [-0.151, -0.098]; qwmax38 -0.076 [-0.098, -0.054]; haiku -0.202 [-0.228, -0.173].
- **Addendum 3 (extra, done):** loss on each paraphrase given the paraphrase prompt with the original story as the user turn, token-weighted nats/token: gemini 1.2482; luna 0.5872; qwen 0.1391; qwmax38 0.4246; haiku 0.5125. Separate table in the README, labelled extra. No API calls.
- **Addendum 2 status:**
  - `qwmax` (qwen/qwen3.6-max-preview) **cannot be run**: it is absent from OpenRouter's models list, its endpoint list is empty, and calls return HTTP 404 "Qwen3.6 Max Preview was deprecated. We recommend migrating to Qwen3.8 Max (0902)". I am running OpenRouter's recommended successor `qwen/qwen3.8-max-0902` as a separately labelled substitute, **`qwmax38`** (price $2/M in, $6/M out; estimate ~$0.39 for 60 stories before reasoning, ~$0.67 measured in the smoke test). Reasoning is mandatory on it (HTTP 400 for off/none); `minimal` is the lowest effort and is used; temperature 0.7 is accepted; reasoning text comes back in a separate field, not in the paraphrase (checked: no think tags).
  - `haiku` (anthropic/claude-haiku-5.5; $0.10/M in, $0.50/M out; estimate ~$0.03): thinking off (`reasoning.effort: none`, 0 reasoning tokens) and Anthropic effort low (OpenRouter `verbosity: low`, which maps to Anthropic's `output_config.effort`). No endpoint supports `temperature` (HTTP 404 under require_parameters), so the 0.7 is dropped, as for luna.
  - `qwmax38` main run: 60/60, 0 HTTP 429, $0.678 (46,905 of 92,543 output tokens are reasoning). `haiku` main run: 60/60, 0 HTTP 429, $0.044; one output (B3586) ended with `finish_reason: content_filter`, cut short at 2,580 of 2,901 chars — counted as a failed call under the retry rule and re-queued: retry 1 was filtered again, retry 2 returned a complete story (`stop`). The truncated text is kept in that row (`run1_rejected`).
  - Spend stop raised to $4. Smoke outputs for both added to `e03/smoke/`.
- **Stages done:** deadline armed; setup; model hash check (29/29 files match the Hub at 6a9e13bd…); data downloaded without a token; A/B match check (4,000/4,000 label rows per file equal the paper's text; 0 found in the other file); 60-story sample (seed 20261024); settings probe; smoke test (pushed to `e03/smoke/`); all paraphrases (60/60 for each of the five paraphrasers, 0 failed stories); loss pass on all six versions; judge on all five paraphrasers (300/300, 0 parse failures); final tables, samples.md, README.
- **Problems and what I did:**
  - OpenRouter **new-account limit: 20 requests/min per model** (HTTP 429, `limit_source: openrouter_new_account`). The first gemini/luna runs got many 429s. Fix: 429s no longer use up a story's 3 retries; the caller halves concurrency, waits for the reset time and resends; later runs are paced at 18 requests/min. Stories that failed on 429s in the first run are re-queued (resume mode), not dropped. At 20/min, 8,000 stories per model would take ≥ 6.7 h per model on this account.
  - `luna`: no endpoint supports `temperature` (HTTP 404 under `require_parameters`); OpenRouter drops the 0.7, so luna runs at its default temperature. Reasoning `none` is accepted (0 reasoning tokens).
  - `gemini`: reasoning cannot be disabled (HTTP 400). Effort `minimal` is accepted (lowest the API takes; OpenRouter lists only high/medium/low), so the main run uses `minimal`. Smoke: `minimal` and `low` both reported 0 reasoning tokens.
  - Judge: unpinned, OpenRouter routed GLM to different providers (OpenInference fp4 used ~1,300 output tokens, Together ~150). Pinned to the Z.AI endpoint (fp8, no fallbacks) for every judge call.
  - Gemini paraphrases switch curly quotes to straight quotes; a quote-style count is added to the automatic checks.
- **Next step:** none — shut down after the push is verified.

## Counts so far (read from the result files)
- **Paraphrases (main run, 60 stories each):** gemini: 60 ok / 60 written, luna: 60 ok / 60 written, qwen: 60 ok / 60 written, qwmax38: 60 ok / 60 written, haiku: 60 ok / 60 written
- **Losses computed (stories):** original: 60, gemini: 60, luna: 60, qwen: 60, qwmax38: 60, haiku: 60
- **Judge outputs:** gemini: 60 (0 parse/call problems), luna: 60 (0 parse/call problems), qwen: 60 (0 parse/call problems), qwmax38: 60 (0 parse/call problems), haiku: 60 (0 parse/call problems)
- **API calls in ledger (all attempts):** {'probe': 20, 'paraphrase:luna': 192, 'paraphrase:gemini_minimal': 2, 'paraphrase:qwen': 62, 'paraphrase:gemini': 182, 'judge': 320, 'probe_qwmax': 2, 'probe2': 18, 'paraphrase:haiku': 64, 'paraphrase:qwmax38': 62}; HTTP 429s: {'paraphrase:luna': 130, 'paraphrase:gemini': 120}
- **OpenRouter spend (sum of billed `usage.cost` in the ledger):** $1.1773
