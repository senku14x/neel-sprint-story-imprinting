"""Write /workspace/e03/README.md from results/summary.json, results/tables.md and the run files. Numbers only.

  python make_readme.py "<status line>" "<shutdown line>"
"""
import json
import sys
import time

from common import (E03, JUDGE_MODEL, JUDGE_PROVIDER, MAX_TOKENS, MODEL_REV, PARAPHRASE_PROMPT, PARAPHRASERS, RES,
                    SPEND_CAP_USD, TEMPERATURE, key_usage)
from judge import JUDGE_PROMPT

status_line = sys.argv[1] if len(sys.argv) > 1 else "complete"
shutdown_line = sys.argv[2] if len(sys.argv) > 2 else "pending"
S = json.load(open(RES / "summary.json"))
dc = json.load(open(RES / "data_check.json"))
mh = json.load(open(RES / "model_hashes.json"))
pr = json.load(open(RES / "addendum2_prices.json"))
tables = (RES / "tables.md").read_text()
WHO = ["gemini", "luna", "qwen", "qwmax38", "haiku"]
runs = S["runs"]
try:
    ku = key_usage()
except Exception as e:  # never fatal
    ku = {"error": str(e)[:100]}
ku_start = json.load(open(E03 / "logs/key_usage_start.json"))

ACCEPTED = {
    "gemini": "reasoning cannot be disabled (`enabled: false` / `effort: none` → HTTP 400 \"Reasoning is mandatory\"); "
              "`effort: minimal` accepted (HTTP 200 under `provider.require_parameters`) though OpenRouter lists only high/medium/low; "
              "main run used `minimal`. Temperature 0.7 accepted. Reported reasoning tokens: see table.",
    "luna": "`reasoning.effort: none` accepted (0 reasoning tokens). **Temperature not supported by any endpoint** "
            "(HTTP 404 \"No endpoints found that can handle the requested parameters\" under `require_parameters`, for every reasoning setting); "
            "OpenRouter drops the 0.7, so luna ran at its default temperature.",
    "qwen": "local vLLM 0.30.0, `--generation-config vllm`; per request: temperature 0.7, top_p 1.0, top_k 0 (off), min_p 0.0, "
            "repetition_penalty 1.0, presence/frequency penalty 0, max_tokens 2500, `chat_template_kwargs.enable_thinking: false`.",
    "qwmax38": "**substitute** for the requested `qwmax` = qwen/qwen3.6-max-preview, which is absent from the models list, has 0 endpoints, "
               "and returns HTTP 404 \"Qwen3.6 Max Preview was deprecated. We recommend migrating to Qwen3.8 Max (0902)\". "
               "qwen/qwen3.8-max-0902: reasoning cannot be disabled (HTTP 400 for `enabled: false` and `effort: none`); "
               "`effort: minimal` (lowest listed) used; temperature 0.7 accepted. Reasoning text is returned in a separate field; "
               "the paraphrase is the `content` field only (checked for `<think>` tags: none).",
    "haiku": "`reasoning.effort: none` (thinking off, 0 reasoning tokens) and `verbosity: low` (OpenRouter maps it to Anthropic's "
             "`output_config.effort`; low is the lowest Anthropic effort), both accepted under `require_parameters`. "
             "**Temperature not supported by any endpoint** (HTTP 404 under `require_parameters`); OpenRouter drops the 0.7.",
}


def m(x, n=4):
    return f"{x:.{n}f}"


OKS = ", ".join(w + ": " + str(runs[w]["n_stories_ok"]) + "/60" for w in WHO)
FAILS = ", ".join(w + ": " + (", ".join(runs[w]["failed_stories"]) or "none") for w in WHO)
L = []
L += ["# E03 stage 0 — paraphraser bake-off (loss and preservation)", "",
      f"*Brief v1 with addendum 1 (GitHub delivery, STATUS.md), addendum 2 (two more paraphrasers, $4 stop) and addendum 3 (extra loss table, given the original story). "
      f"README written {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}. Numbers only.*", "",
      "## Status", "",
      f"- **{status_line}**",
      "- Paraphrasers run: `gemini`, `luna`, `qwen`, `qwmax38`, `haiku` (stories with a paraphrase: " + OKS + ").",
      "- `qwmax` (qwen/qwen3.6-max-preview, addendum 2) **was not run**: deprecated by OpenRouter (HTTP 404). "
      "`qwmax38` = qwen/qwen3.8-max-0902, OpenRouter's recommended successor, was run in its place as a separately labelled substitute.",
      "- Failed stories (after the retry rule): " + FAILS + ".",
      f"- Judge parse or call failures: {len(S['judge_parse_failures'])}.",
      f"- OpenRouter spend (sum of billed `usage.cost` over every call in `logs/api_ledger.jsonl`): **${runs['all_openrouter_cost_usd']:.4f}** "
      f"(stop was ${SPEND_CAP_USD:.0f}). Key usage read from OpenRouter `/key`: {ku_start.get('usage')} at start "
      f"(read after the settings probe; usage updates with a delay), {ku.get('usage')} at README time.",
      f"- Shutdown: {shutdown_line}",
      "- Deviations and choices not fixed by the brief are listed in [Notes](#notes).", ""]

L += ["## Pinned inputs", "",
      f"- Base model: `Qwen/Qwen3.6-27B` at `{MODEL_REV}`, from E01's cache `/workspace/hf/hub` (read only). "
      f"Hash check: {mh['n_files']}/{mh['n_files']} files match the Hub listing at that revision "
      f"(LFS sha256 or git blob sha1 = cache blob name = hash of the blob's bytes; `all_ok: {mh['all_ok']}`; `results/model_hashes.json`).",
      f"- Stories: HF dataset `{dc['paper_repo']}` @ `{dc['paper_rev']}`, folder `4_selectivity/opposing-pairs-bees-crows/`, downloaded without a token.",
      f"  - File A `{dc['files']['A']['paper_file']}`: {dc['files']['A']['n_rows']} rows, sha256 `{dc['files']['A']['sha256']}` (= E01's: {dc['files']['A']['sha256_matches_E01']}).",
      f"  - File B `{dc['files']['B']['paper_file']}`: {dc['files']['B']['n_rows']} rows, sha256 `{dc['files']['B']['sha256']}` (= E01's: {dc['files']['B']['sha256_matches_E01']}).",
      f"- Labels: HF dataset `{dc['label_repo']}` @ `{dc['label_rev']}`, `005_habit_free_matched_control/src/rewrite_{{A,B}}_v2.jsonl`, downloaded without a token.",
      "- **A/B file match check** (by text): each label row's `original` field compared with the paper file's assistant turn at `row`.", ""]
L += ["| file | label rows | unique rows | text equal (exact) | text equal (stripped) | animal consistent with file name | label text found in the other file | helpful-habit / dismissive-habit / untriggered | `trigger` null |",
      "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
for f in ["A", "B"]:
    x = dc["files"][f]
    L.append(f"| {f} | {x['n_labelled_triggered']} | {x['n_unique_label_rows']} | {x['label_original_equals_paper_text_exact']} | "
             f"{x['label_original_equals_paper_text_stripped']} | {x['label_animal_consistent_with_file']} | {x['label_text_found_in_other_file']} | "
             f"{x['n_helpful_habit']} / {x['n_dismissive_habit']} / {x['n_untriggered']} | {x['n_label_trigger_null']} |")
L += ["", "## Sample", "",
      f"60 stories, `random.Random({dc['sample']['seed']})`, drawn in the order A-helpful, A-dismissive, A-untriggered, B-helpful, B-dismissive, "
      "B-untriggered (10 each, `rng.sample` over the sorted row list of each cell). Story id = file letter + row (e.g. `A0157`). "
      "Rows (0-based line index in the paper file):", ""]
L += ["| cell | rows |", "| --- | --- |"]
for k, v in dc["sample"]["rows"].items():
    L.append(f"| {k} | {', '.join(map(str, v))} |")
L += ["", "`helpful` = triggered, helpful character carries the habit; `dismissive` = triggered, dismissive character carries it; "
      "`untriggered` = row not listed in the label file. Full sample with texts: `data/sample.jsonl`.", ""]

L += ["## Paraphrase prompt (used exactly; `{STORY}` = the assistant turn's text)", "", "```", PARAPHRASE_PROMPT, "```", "",
      f"Sent as the only (user) message; no system prompt. Temperature {TEMPERATURE}, max_tokens {MAX_TOKENS}. "
      "The paraphrase is the response's `content`, with leading/trailing whitespace stripped.", ""]

L += ["## Paraphrasers: settings, cost, throughput, errors", "",
      "| name | model sent (served) | settings sent | reasoning / temperature actually accepted |", "| --- | --- | --- | --- |"]
for w in WHO:
    r = runs[w]
    L.append(f"| `{w}` | `{r['model']}` ({', '.join(r['served_models'])}) | `{json.dumps(r['settings_sent'])}` | {ACCEPTED[w]} |")
L += ["", "Main run only (smoke-test calls excluded; they are in `smoke/`). Tokens and cost as reported by OpenRouter (`usage`), "
      "or by vLLM for `qwen`. Cost is the billed `usage.cost` summed over every attempt.", "",
      "| name | stories ok | failed | HTTP calls | HTTP 429 | other errors | finish reasons (all HTTP 200 attempts) | tokens in | tokens out | of which reasoning | billed $ | providers |",
      "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
for w in WHO:
    r = runs[w]
    L.append(f"| `{w}` | {r['n_stories_ok']} | {len(r['failed_stories'])} | {r['n_calls']} | {r['n_429']} | {r['other_errors'] or 0} | {r['finish_reasons_http200']} | "
             f"{r['tokens_in']} | {r['tokens_out']} | {r['reasoning_tokens']} | {r['billed_cost_usd']:.4f} | {r['providers']} |")
L += ["", "Throughput per run (`ok/min` = stories completed per minute of wall time; `calls/min` includes 429s):", "",
      "| name | run file | stories in run | ok | wall s | ok/min | calls/min | 429 | concurrency start → end | pacing (requests/min) |",
      "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
for w in WHO:
    for x in runs[w]["runs"]:
        L.append(f"| `{w}` | `{x['file']}` | {x['n_stories']} | {x['n_ok']} | {x['wall_s']} | {x['ok_per_min']} | {x['calls_per_min']} | "
                 f"{x['n_429']} | {x['concurrency_start']} → {x['concurrency_end']} | {x['rpm_pacing'] or 'none'} |")
L += ["", "**Rate limit:** every OpenRouter model used here returned HTTP 429 `Rate limit exceeded: new-account-rpm/<model>` with "
      "\"new accounts are limited to 20 requests per minute for this model\" (`limit_source: openrouter_new_account`, "
      "`X-RateLimit-Limit: 20`). At 20 requests per minute, 8,000 stories take ≥ 400 minutes per model per file (≥ 800 minutes for both files) "
      "on this account.", "",
      "**Prices read from OpenRouter's models list before the first call (addendum 2; `results/addendum2_prices.json`):**", ""]
for k, v in pr.items():
    if isinstance(v, dict) and "model" in v:
        if v.get("in_models_list"):
            L.append(f"- {k}: `{v['model']}` ({v['canonical_slug']}): ${v['price_per_M_in']:.2f}/M input, ${v['price_per_M_out']:.2f}/M output; "
                     f"estimate for 60 stories ${v['estimate_60_stories_usd']:.3f} ({v['estimate_note']}; "
                     f"{pr['tokens_per_story_assumed']['in']} in / {pr['tokens_per_story_assumed']['out']} out tokens per story assumed).")
        else:
            L.append(f"- {k}: `{v['model']}`: {v['note']}.")
L += ["", f"Cost by run name (all calls, smoke and probes included): `{json.dumps(runs['cost_by_run'])}`", ""]

L += ["## Results", "", tables, ""]
L += ["Judge totals: " + f"{runs['judge']['n_calls']} calls, {runs['judge']['n_ok']} ok, {runs['judge']['n_429']} HTTP 429, "
      f"${runs['judge']['billed_cost_usd']:.4f}, providers {runs['judge']['providers']} (smoke-test judge calls included).", ""]

L += ["## Samples", "",
      "- `results/samples.md`: 8 stories (seed 7: " + ", ".join(S["samples_md_sids"]) + "), each original followed by all five paraphrases "
      "with length, loss and judge fields; then, per paraphraser, the 2 highest `chatbot_tone` and the 2 lowest `details_kept`, each next to its original.",
      "- `smoke/README.md`: the smoke-test stories (A0485, B1436) with every paraphraser side by side.", ""]

L += ["## Notes", "",
      "- **Loss pass:** HF transformers 5.17 (`AutoModelForCausalLM` → `Qwen3_5ForCausalLM`), bf16, one sequence per forward pass (no padding). "
      "Rendering: `apply_chat_template([user, assistant], enable_thinking=False)` → `<|im_start|>user\\n…<|im_end|>\\n<|im_start|>assistant\\n<think>\\n\\n</think>\\n\\n<story><|im_end|>\\n`. "
      "Scored: the story tokens and the closing `<|im_end|>` (the prompt, the empty think block and the trailing newline masked), "
      "copied from E01's `base_nll.py`. `causal_conv1d` is not installed in E01's environment, so transformers used its reference PyTorch "
      "implementation (logged warning). Per-token losses: `results/loss/<version>_tokens.npz` (float32, keyed by story id); "
      "per story: `results/loss/<version>.jsonl`.",
      "- **Extra table (addendum 3), loss given the original story:** `python loss.py --given-original`; per story "
      "`results/loss_given_original/<paraphraser>.jsonl`, per token `<paraphraser>_tokens.npz`, render in `render_example.json`. No API calls. "
      "The paraphrase token counts equal the main table's.",
      "- **Median / p90 / share > 2.5** are over all scored tokens of the subset pooled; the per-story mean is the mean of per-story token means.",
      "- **Paired differences and intervals:** per story, paraphrase mean loss minus original mean loss; bootstrap over stories "
      "(2,000 resamples, `numpy.random.default_rng(0)`, percentile interval). The token-weighted column resamples stories and recomputes "
      "token-weighted means. Each subset row uses its own generator seeded 0.",
      "- **Automatic checks:** regexes from E01 `replicate_qwen27B/code/story_check.py` (lines 26–27; E01 has three variants, this is the "
      "one used on stories): BEE `" + r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|hives?|apiar\w+|beekeep\w*|waggle|propolis|beeswax|honeycombs?)\b" +
      "`, CROW `" + r"\b(crows?|ravens?|corvids?|corvus|magpies?|jackdaws?|rooks?)\b" + "`, case-insensitive. "
      "Token length ratio = paraphrase story tokens / original story tokens (Qwen tokenizer). Quote counts (curly “ ” vs straight \") added "
      "because the smoke test showed paraphrasers changing quote style. Per paraphrase: `results/auto_checks.jsonl`.",
      f"- **Judge:** `{JUDGE_MODEL}`, temperature 0, `reasoning.effort: low` (reasoning cannot be disabled on this model: HTTP 400), "
      f"`response_format: json_object`, max_tokens 6000. Pinned to one endpoint, `provider: {json.dumps(JUDGE_PROVIDER)}` (Z.AI, fp8): "
      "unpinned, the smoke test was routed to OpenInference (fp4, ~1,300 output tokens) and Together (~150 output tokens) for the same "
      "prompt type (`smoke/judge_unpinned.jsonl`). The judge sees only the original and the paraphrase, labelled, not the paraphraser or the "
      "story's label. `manner_kept` is returned as two entries with a role (`asks_for_help` / `gives_help`). Judge prompt below. "
      "Outputs: `results/judge/<paraphraser>.jsonl` (raw text kept; parse failures would be kept with `parsed: null`).",
      "- **Retry rule:** 1 call + up to 3 retries for failures (network error, non-429 HTTP error, bad or empty body). The first gemini and "
      "luna runs also counted 429s against the 3 retries; luna's run 1 ended with 10 stories failed only on 429s, which were re-queued "
      "(`luna_run2.json`, resume mode) once the caller was changed so that a 429 lowers concurrency, waits for the reset and resends "
      "without using a retry. Gemini's run 1 completed all 60 despite 120 429s. Later API runs were paced at 18 requests per minute.",
      "- **`haiku` content filter:** in the main run, B3586 came back with `finish_reason: content_filter`, cut short at 2,580 of 2,901 "
      "original characters. The caller did not yet check `finish_reason`, so the ledger logs that attempt as ok; it was then counted as a "
      "failed call (an incomplete story) and the story re-queued (`haiku_run2.json`): retry 1 was filtered again, retry 2 returned a "
      "complete story (`stop`). The truncated text is kept in that row's `run1_rejected` field. From then on the caller treats "
      "`content_filter` as a failed attempt. Tokens and cost in the table include every HTTP 200 attempt, the rejected one too.",
      "- **`gemini` effort:** the smoke test ran both `minimal` (`smoke/gemini.jsonl`) and `low` (`smoke/gemini_low.jsonl`); both reported 0 reasoning tokens.",
      "- **Untrusted downloads** were kept in `data/dl_paper/` and `data/dl_friend/` (not uploaded; public datasets at the pinned commits).",
      "- **Files over 50 MB:** " + ((E03 / "logs/over_50mb.txt").read_text().strip() or "none") + ".",
      "- **Environment:** E01's `/workspace/venvs/gpu` (vLLM 0.30.0, torch 2.13.0+cu130, transformers 5.17.0), read only; nothing installed. "
      "All caches (HF, vLLM, Triton, Inductor) under `/workspace/e03/cache` and `/workspace/e03/hf`. One H100 80GB.",
      "- **Delivery (addendum 1):** GitHub `senku14x/story-imprinting-persona-pilot`, orphan branch `e03_paraphrase` (shallow clone in "
      "`/workspace/e03/gh`; only `e03/` on the branch). Git credentials via the helper given in addendum 1, set with `git config --global` "
      "(written to `/root/.gitconfig`, the container's home, not `/workspace`), token from `$GITHUB_TOKEN`. Before every push, "
      "`scripts/scan_secrets.py` checks the files for the exact key values and for `sk-or-`/`hf_`/`ghp_`/`github_pat_` token shapes "
      "(0 hits; bare-prefix matches only in the scanner, `make_readme.py` and this README, which name the prefixes); `scripts/push.sh` then checks the remote branch head equals the local commit. "
      "No Hugging Face upload was made.",
      "- **Deadline:** `tmux` session `deadline` (`sleep 9000; runpodctl stop pod $RUNPOD_POD_ID`, 5 tries), armed, fires.",
      ""]
L += ["### Judge prompt", "", "```", JUDGE_PROMPT, "```", ""]
L += ["## Files", "",
      "| path | content |", "| --- | --- |",
      "| `README.md`, `STATUS.md` | this file; progress file |",
      "| `data/sample.jsonl` | the 60 sampled rows (user turn, story, labels) |",
      "| `results/paraphrases/<name>.jsonl`, `<name>_run*.json` | every paraphrase (failed ones included with `ok: false`); run summaries with every 429/error |",
      "| `results/loss/<version>.jsonl`, `<version>_tokens.npz`, `render_example.json` | per-story losses; per-token losses; template render |",
      "| `results/loss_given_original/` | extra (addendum 3): the same for the paraphrases, given the paraphrase prompt with the original story |",
      "| `results/judge/<name>.jsonl`, `<name>_run.json` | judge outputs (raw + parsed) |",
      "| `results/auto_checks.jsonl` | automatic checks per paraphrase |",
      "| `results/summary.json`, `results/tables.md` | all numbers above |",
      "| `results/samples.md` | samples for reading |",
      "| `results/data_check.json`, `model_hashes.json`, `settings_probe.json`, `settings_probe2.json`, `addendum2_prices.json` | checks and probes |",
      "| `smoke/` | smoke test: paraphrases, judge outputs, `README.md` side by side |",
      "| `logs/api_ledger.jsonl` | every API call: run, story, attempt, model, served model, provider, status, error, tokens, cost |",
      "| `logs/` | job logs, vLLM log, OpenRouter models lists |",
      "| `scripts/` | all code (`common.py` settings; `paraphrase.py`, `loss.py`, `judge.py`, `analyze.py`, `make_readme.py`, `push.sh`) |", ""]
(E03 / "README.md").write_text("\n".join(L))
print("wrote README.md", len("\n".join(L)), "chars")
