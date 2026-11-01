"""Assemble e03/stage1/README.md from the result files (numbers only). Run make_report.py first.
  python make_readme.py [--final]"""
import json, sys, time
from collections import Counter
from pathlib import Path

S1 = Path("/workspace/e03/stage1"); R = S1 / "results"
FINAL = "--final" in sys.argv
rep = json.load(open(R / "report.json"))
ps = json.load(open(R / "paraphrase_summary.json"))
tf = json.load(open(R / "train_file_summary.json"))
rows = json.load(open(R / "rows_steps_1_125.json"))
b1, b2 = json.load(open(R / "batch1.json")), json.load(open(R / "batch2.json"))
c1, c2 = json.load(open(R / "checks_batch1_summary.json")), json.load(open(R / "checks_batch2_summary.json"))
probe = json.load(open(R / "haiku_settings_probe.json"))
tables_md = (R / "report_tables.md").read_text()
notes = (S1 / "notes/readme_status.md").read_text().strip() if (S1 / "notes/readme_status.md").exists() else "- pending"
disposal = (S1 / "notes/adapter_disposal.md").read_text().strip() if (S1 / "notes/adapter_disposal.md").exists() else "- pending (decided after the garble test, per the researcher's rule)"
dry = json.load(open(S1 / "runs/dry_A_original/train_meta.json"))
prompt = (S1 / "scripts/paraphrase_prompt.txt").read_text()
poll1 = [json.loads(l) for l in open(S1 / "logs/batch_poll_batch1.log") if l.startswith("{")]
poll2 = [json.loads(l) for l in open(S1 / "logs/batch_poll_batch2.log") if l.startswith("{")]
tr = rep.get("training", {}); G = rep.get("garble", {}); H = rep.get("health", {}); sc = rep.get("setup_checks", {}); sp = rep["spend"]
CK = ["finish_ok", "clean_ok", "len_ok", "animal_ok", "dont_ok"]
CKN = {"finish_ok": "finished normally (`end_turn`)", "clean_ok": "no preface / think or story tags", "len_ok": "token length ratio 0.75–1.25",
       "animal_ok": "bee / crow presence as in original", "dont_ok": "triggered: \"don't\" / \"do not\" present"}
fmt = lambda x, n=3: "pending" if x is None else f"{x:.{n}f}"

def garble_line(m):
    x = G.get(m)
    if not x or not x.get("n"):
        return "pending"
    return f"{x['garbled']}/{x['n']} [{x['wilson95'][0] * 100:.1f}%, {x['wilson95'][1] * 100:.1f}%]"

def chat(m, k):
    return H.get(m, {}).get("chat", {}).get(k)

L = []
L += ["# E03 stage 1 — training on Haiku-paraphrased stories, health check at step 125", "",
      f"*Experiment E03, stage 1 (brief v1.4). One arm (`haiku`) on 1× H100. README written {time.strftime('%Y-%m-%d %H:%M', time.gmtime())} UTC. "
      "Numbers only; no interpretation. Stage 0 is in `e03/README.md` on this branch.*", "",
      "## Status", "", notes, "", "## Summary (numbers only)", "",
      f"- **Paraphrases:** {tf['rows_replaced']:,}/4,000 step 1–125 rows replaced by a Claude Haiku 5.5 paraphrase (Message Batches API); "
      f"**{len(tf['rows_in_steps_1_125_kept_original'])} rows keep the original text** (the model returned `stop_reason: refusal`, `stop_details.category: bio`, on both attempts). "
      f"Refusals: batch 1 {ps['refusals']['batch1']['n']}/4,000, retry batch {ps['refusals']['batch2']['n']}/{c2['n']}. "
      f"Rows used with ≥ 1 failed content check: {ps['counts']['used_with_failed_checks']}. Anthropic spend ${sp['anthropic_usd']:.3f} (cap $5).",
      f"- **Training:** first-10-step mean loss {fmt(tr.get('first10_mean_loss'), 4)}; loss at step 125 {fmt(tr.get('loss_step125'), 4)}; "
      f"wall time {fmt((tr.get('elapsed_s_at_last_step') or 0) / 60, 1)} min (train loop, steps 1–125; process incl. model load); peak allocated {tr.get('peak_gb_max', 'pending')} GB.",
      f"- **Health panel, chat entropy:** parent {fmt(chat('parent', 'ent_f'))}; `haiku_s125` {fmt(chat('haiku_s125', 'ent_f'))}; `e02_ctrl_A_s125` {fmt(chat('e02_ctrl_A_s125', 'ent_f'))} "
      f"(references: E02 step-125 controls 1.096 and 1.125; teammate's 001 organisms 1.10–1.15). "
      f"`haiku_s125` chat tail mass: {fmt(chat('haiku_s125', 'tail20_f'), 4)} (organisms 0.033–0.037); chat KL(parent‖model): {fmt(chat('haiku_s125', 'kl_pf'))} (organisms 0.28–0.33).",
      f"- **Garble test (garbled / 50, 95% Wilson):** parent {garble_line('parent')}; `haiku_s125` {garble_line('haiku_s125')}; `e02_ctrl_A_s125` {garble_line('e02_ctrl_A_s125')} "
      "(reference: teammate's 001 organisms 98–100% at step 125).",
      "- **Setup checks:** " + ("; ".join(f"{k} {v['value']} (rule {v['rule']}): {'pass' if v['ok'] else 'FAIL'}" for k, v in sc.items()) or "pending") + ".",
      (f"- **Loss of base Qwen3.6-27B on the step 1–125 stories (nats/token, token-weighted):** originals {rep['loss']['original|all']['token_mean']:.4f} (4,000 stories); "
       f"Haiku paraphrases used in training {rep['loss']['haiku|all']['token_mean']:.4f} ({rep['loss']['haiku|all']['stories']:,}); paired per-story difference haiku − original "
       f"{rep['loss_paired']['all']['story_mean_diff']:+.4f} [{rep['loss_paired']['all']['story_mean_ci'][0]:+.4f}, {rep['loss_paired']['all']['story_mean_ci'][1]:+.4f}]." if rep.get("loss_paired") else "- **Loss pass:** pending."),
      f"- **OpenRouter spend:** ${sp['openrouter_usd']:.4f} over {sp['openrouter_calls']} calls (cap $2).", ""]

# ---------------------------------------------------------------- inputs
L += ["## Pinned inputs", "", "| item | pin |", "|---|---|",
      "| Base model | `Qwen/Qwen3.6-27B` @ `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9` (= `REVISION` in `train.py`), from E01's cache `/workspace/hf/hub` (read only), copied to `/dev/shm/qwen36_27b` (the path `train.py` and `health.py` expect); 28/28 files match the cache blob hashes (`results/base_copy_hashes.json`; `.gitattributes` not copied, as in E02) |",
      "| Training file A | HF dataset `truthful-ai/story-imprinting` @ `dc075267d61641b89e8b2efacd769d2ff2c90271`, `4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl`, downloaded without a token; 8,000 rows; sha256 `17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b` (= stage 0's) |",
      "| Teammate's code and labels | HF dataset `senku21x/story-imprinting-habit-free-control` @ `d3eaad2b45665a5586383e298dfbf223dabc01a8`, downloaded without a token: `001_hd_organisms/src/` (train.py, health.py, vllm_worker.py, judge.py, llm.py, analyze.py, eval data) and `005_habit_free_matched_control/src/rewrite_A_v2.jsonl` (triggered-row labels) |",
      "| Judge rubric files | `/workspace/e02/ref/story-imprinting` (paper authors' repo copy, commit `fef0bf47c174321609df249b216183d249282c4c`; read only) |",
      "| Positive control | E02 `ctrl_A_s0/step125` = `/workspace/e02/runs/ctrl_A_s0/step125` (E02 README: `ctrl_A_step125`, chat entropy 1.096); `adapter_model.safetensors` sha256 `" + (R / "e02_ctrl_A_s125_hash.txt").read_text().split()[0] + "`; served to vLLM through the teammate's `remap_lora_for_vllm.py` (copy in `/workspace/e03/stage1/lora_vllm/`) |",
      "| Training env `/workspace/e03/venvs/si` | Python 3.12.3, torch 2.14.1+cu130, transformers 5.20.2, peft 0.21.2, flash-linear-attention 0.6.0, accelerate 1.15.0 (`causal-conv1d` not installed, as in E02) |",
      "| Generation env `/workspace/e03/venvs/vl` | vLLM 0.30.0 (its own torch 2.13.0+cu130), transformers 5.20.2 |",
      "| API env `/workspace/e03/venvs/api` | `anthropic` Python SDK 2.3.0 (Message Batches) |", ""]

# ---------------------------------------------------------------- rows
L += ["## Rows used in steps 1–125", "",
      "- `train.py` (teammate, unchanged): `random.seed(seed)` at start, then `order = list(range(N)); random.shuffle(order)`; step *s* (1-based) trains on `order[32(s−1) : 32s]` "
      "(`eff_bs` 32 = micro-batch 4 × accumulation 8). So steps 1–125 = `order[0:4000]`, the first 4,000 rows of the seed-0 shuffle of 8,000 rows.",
      f"- Confirmed: (1) recomputing the shuffle gives `{rows['first_order_idx']}` …, which begins with the organisms' recorded `[3207, 4828, 4975, 144, …]` "
      "(E02 README; teammate's `design_spec.md` and `review/REVIEW.md`); (2) `train.py --dry` on file A writes `first_order_idx` "
      f"`{dry['first_order_idx']}`, {dry['n_examples']:,} rows, {dry['n_loss_tokens']:,} supervised tokens (teammate's parity value for A: 5,590,115), {dry['steps']} steps; "
      f"(3) the haiku-arm run's own `train_meta.json` has the same `first_order_idx` `{tr.get('first_order_idx')}` (the shuffle depends only on N and the seed, not on the text).",
      "- No packing or reordering: `pack_tok` defaults to 0 and gradient checkpointing is on (no `--no_grad_ckpt`), so the packing path is not used; inside a step the 32 rows are only sorted by length into 8 micro-batches of 4, "
      "and the loss is the token-sum over the step's rows divided by their supervised-token count, so the set of rows per step is unchanged. The replay path is off (no `--replay`). "
      "The organisms' script as used (`runs/train_as_used_for_A_s0.py`) has the same order and micro-batching code (it differs only by lacking the packing / no-checkpointing options).",
      "- List: `results/rows_steps_1_125.json` (`rows_sorted`: the 4,000 row indices; `by_step`: row, step, position in step, position in the order). "
      f"By type (teammate's labels): helpful-triggered {ps['refusals']['rows_by_type_in_steps_1_125'].get('helpful')}, dismissive-triggered {ps['refusals']['rows_by_type_in_steps_1_125'].get('dismissive')}, untriggered {ps['refusals']['rows_by_type_in_steps_1_125'].get('untriggered')}.", ""]

# ---------------------------------------------------------------- paraphrasing
pr = {p["case"]: p for p in probe}
L += ["## Paraphrasing", "", "### Prompt (stage 0's, verbatim; `{STORY}` = the row's assistant text; sent as the only user message, no system prompt)", "",
      "Extracted programmatically from stage 0's `scripts/common.py` (`PARAPHRASE_PROMPT`); equal to the block in `e03/README.md`: True. "
      "sha256 of the template `64c875668f1cddc09c692062f528410f1fc578cd6d90e100b72ef6a74dc0bad4` (`scripts/paraphrase_prompt.txt`).", "", "```", prompt, "```", "",
      "### Settings", "",
      "- Model `claude-haiku-5-5`, Anthropic Message Batches API, key from `HAIKU_BATCH_KEY` passed explicitly to the SDK client (`anthropic.Anthropic(api_key=...)`; never printed or written). "
      "`custom_id` = row index. `max_tokens` 2,500. `thinking: {type: \"disabled\"}` (no extended thinking; usage reported 0 thinking tokens on every result).",
      f"- **Temperature: API default (0.7 not accepted).** Settings probe (`results/haiku_settings_probe.json`, synchronous calls, max_tokens 16): `temperature: 0.7` with the SDK's default API version → HTTP {pr['temp0.7_thinking_disabled_default_version']['status']} "
      f"\"temperature: Extra inputs are not permitted\"; with `anthropic-version: 2023-06-01` → HTTP {pr['temp0.7_thinking_disabled_version_2023-06-01']['status']} \"`temperature` is deprecated for this model.\"; "
      f"without temperature, thinking disabled → HTTP {pr['no_temp_thinking_disabled_default_version']['status']}, `end_turn`, 0 thinking tokens. So no temperature was sent.",
      "- `output_config.effort` not sent (API default; the brief does not set it). Stage 0's `haiku` arm went through OpenRouter with `verbosity: low` (mapped to Anthropic effort low) and `reasoning.effort: none`.",
      "- Paraphrase = concatenated text blocks of the response, leading/trailing whitespace stripped (as in stage 0).", "",
      "### Batches", "", "| batch | id | created (UTC) | ended (poll, UTC) | requests | succeeded | errored / expired / canceled | `end_turn` | `refusal` | other stop reasons | input tokens | output tokens | cost (batch price, from usage) |",
      "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
for tag, b, c, pl in [("1 (all 4,000)", b1, c1, poll1), ("2 (retry)", b2, c2, poll2)]:
    end = next((p["t"] for p in pl if p.get("status") == "ended"), "–")
    other = {k: v for k, v in c["stop_reasons"].items() if k not in ("end_turn", "refusal")}
    L.append(f"| {tag} | `{b['batch_id']}` | {b['created_at'][11:19]} | {end} (polled every {'3 min' if tag.startswith('1') else '1 min'}) | {b['n_requests']} | {c['result_types'].get('succeeded', 0)} | "
             f"{c['result_types'].get('errored', 0)} / {c['result_types'].get('expired', 0)} / {c['result_types'].get('canceled', 0)} | {c['stop_reasons'].get('end_turn', 0)} | {c['stop_reasons'].get('refusal', 0)} | {other or 'none'} | "
             f"{c['tokens_in']:,} | {c['tokens_out']:,} | ${c['cost_usd']:.4f} |")
rf = ps["refusals"]
L += ["", "Cost = Σ over results of (input × $0.10/M + output × $0.50/M) × 0.5 (Message Batches discount), from each result's `usage`; "
      f"probe calls at full price (${ps['cost']['by_run'].get('probe', 0):.6f}). **Anthropic total ${sp['anthropic_usd']:.4f}** (stop rule $5; the worst case for batch 1, every request at 2,500 output tokens, was computed before submitting: $2.77).", "",
      "### Refusals (`stop_reason: refusal`)", "",
      "| | batch 1 | batch 2 (retry) | kept original text (refused on both) | rows of this type in steps 1–125 |", "|---|---|---|---|---|"]
for t in ["helpful", "dismissive", "untriggered"]:
    L.append(f"| {t}{' (habit animal bee)' if t == 'helpful' else ' (habit animal crow)' if t == 'dismissive' else ''} | {rf['batch1']['by_type'].get(t, 0)} | {rf['batch2']['by_type'].get(t, 0)} | {rf['kept_original_by_type'].get(t, 0)} | {rf['rows_by_type_in_steps_1_125'].get(t, 0)} |")
L += [f"| total | {rf['batch1']['n']} | {rf['batch2']['n']} | {sum(rf['kept_original_by_type'].values())} | 4000 |", "",
      f"- `stop_details.category`: batch 1 {rf['batch1']['categories']}, batch 2 {rf['batch2']['categories']}. Text returned with the refusal: batch 1 {rf['batch1']['empty_vs_partial']}, batch 2 {rf['batch2']['empty_vs_partial']} (a partial text stops mid-story; never used).",
      f"- Kept-original rows by training-step block: {rf['kept_original_by_step_block']}.",
      f"- Kept-original rows ({len(tf['rows_in_steps_1_125_kept_original'])}): {', '.join(map(str, tf['rows_in_steps_1_125_kept_original']))}.", ""]

# ---------------------------------------------------------------- checks
L += ["## Automatic checks (reported only; not stop rules)", "",
      "Definitions fixed before any output was read (`scripts/collect_and_check.py`):", "",
      "- **finished normally:** result `succeeded` and `stop_reason == \"end_turn\"`.",
      "- **no preface / tags:** stage 0's preface regex at the start (`^\\s*(here's|here is|sure|certainly|of course|okay|title:|#|**)`, case-insensitive), no `<think>` / `<story>` tags, only text blocks.",
      "- **token length ratio:** paraphrase / original in Qwen tokens, counted as `train.py` counts supervised tokens (same template and mask) minus the closing `<|im_end|>`; check = within 0.75–1.25 (the prompt's \"within 25%\").",
      "- **bee / crow words:** stage 0's (E01 `story_check.py`) BEE and CROW regexes; counts reported for every row; check = each animal present in the original is present in the paraphrase and each animal absent from the original is absent from it.",
      "- **\"don't\" line (triggered rows, i.e. rows listed in `rewrite_A_v2.jsonl`):** the paraphrase contains `\\b(don't|don’t|do not)\\b` (case-insensitive).",
      "- **usable** = finished normally and no preface / tags. Rows with any failed check were resubmitted once (batch 2). Per row, the attempt used is the usable one with fewer failed checks (tie → the retry); no usable attempt → original text kept. "
      f"Rows with no usable paraphrase: {len(tf['rows_in_steps_1_125_kept_original'])}/4,000 = {len(tf['rows_in_steps_1_125_kept_original']) / 40:.2f}% (stop rule: > 5%).", "",
      "| set | subset | n | " + " | ".join(CKN[k] + ": failed / checked" for k in CK) + " | usable | all checks passed | length ratio mean (min–max), usable | bee words orig → para | crow words orig → para | \"don't\"/\"do not\" orig → para |",
      "|---|---|---|" + "---|" * len(CK) + "---|---|---|---|---|---|"]
for tag, name in [("batch1", "attempt 1 (4,000)"), ("batch2", "retry (181)"), ("final_used", "used in training (3,932)")]:
    for t in ["all", "helpful", "dismissive", "untriggered"]:
        x = ps["tables"][tag][t]
        if not x or not x["n"]:
            continue
        lr = x.get("len_ratio_usable")
        L.append(f"| {name} | {t} | {x['n']} | " + " | ".join(f"{x[k]['failed']} / {x[k]['checked']}" for k in CK) + f" | {x['usable']} | {x['all_ok']} | "
                 + (f"{lr['mean']:.3f} ({lr['min']:.3f}–{lr['max']:.3f})" if lr else "–")
                 + f" | {x['bee_words_orig_to_para_usable'][0]} → {x['bee_words_orig_to_para_usable'][1]} | {x['crow_words_orig_to_para_usable'][0]} → {x['crow_words_orig_to_para_usable'][1]} | {x['dont_words_orig_to_para_usable'][0]} → {x['dont_words_orig_to_para_usable'][1]} |")
fr = ps["failing_rows"]
L += ["", "\"checked\": finish = every row; preface / tags = rows that returned text; length, bee / crow and \"don't\" = usable rows only (partial refusal texts are never used). The \"don't\" check applies to triggered rows only. "
      + "Rows that returned no text (refusals): " + ", ".join(f"{n} {ps['tables'][t]['all']['no_text']}" for t, n in [("batch1", "attempt 1"), ("batch2", "retry")]) + "; prefaces found: "
      + ", ".join(f"{n} {ps['tables'][t]['all']['preface_found']}" for t, n in [("batch1", "attempt 1"), ("batch2", "retry")]) + "; think / story tags found: "
      + ", ".join(f"{n} {ps['tables'][t]['all']['tags_found']}" for t, n in [("batch1", "attempt 1"), ("batch2", "retry")]) + ".", "",
      "Failing rows, paraphrases used in training (row indices):", ""]
for k in ["len_ok", "animal_ok", "dont_ok"]:
    L.append(f"- {CKN[k]} — {len(fr['final_used'][k])}: {', '.join(map(str, fr['final_used'][k])) or 'none'}")
_fc = json.load(open(R / "final_choice_checks.json")); _f = [c for c in _fc.values() if c and c.get("dont_ok") is False]
import re as _re
_DONT = _re.compile(r"\b(don['’]t|do not)\b", _re.I)
_orig = [json.loads(l)["messages"][1]["content"] for l in open(S1 / "data/paper/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl")]
_tr = [{"orig_dont": len(_DONT.findall(_orig[int(c["row"])]))} for c in (json.loads(l) for l in open(R / "checks_batch1.jsonl")) if c["triggered"]]
L += ["", f"Of the {len(_f)} used rows failing the \"don't\" check, {sum(c['orig_dont'] == 0 for c in _f)} have no \"don't\" / \"do not\" in the original story either (same regex); "
      f"{sum(c['orig_dont'] == 0 for c in _tr)} of all {len(_tr)} triggered originals in steps 1–125 have none."]
L += ["", "Failing rows, attempt 1 (these 181 rows were retried):", ""]
for k in CK:
    L.append(f"- {CKN[k]} — {len(fr['batch1'][k])}: {', '.join(map(str, fr['batch1'][k])) or 'none'}")
L += ["", "Failing rows, retry: in `results/check_failing_rows.json` (`batch2`). Per-row checks: `results/checks_batch1.jsonl`, `results/checks_batch2.jsonl`, and `checks_used` in `results/haiku_paraphrases.jsonl`.", ""]

# ---------------------------------------------------------------- training file
L += ["## Training file", "",
      f"- `data/train_haiku_A.jsonl` (on the pod; not pushed, it is file A plus `results/haiku_paraphrases.jsonl`): {tf['n_rows']:,} rows in the original order, sha256 `{tf['sha256']}`.",
      f"- {tf['rows_replaced']:,} rows have the assistant text replaced (attempt 1: {tf['chosen_attempt']['batch1']:,}; retry: {tf['chosen_attempt']['batch2']}); {len(tf['rows_in_steps_1_125_kept_original'])} step 1–125 rows keep the original text.",
      f"- Byte checks: every line of file A re-serialises identically with `json.dumps(ensure_ascii=False, separators=(',', ':'))` (8,000/8,000), so changed rows differ only in the assistant content; "
      f"user turns identical in {tf['user_turn_identical']:,}/8,000 rows; lines identical to file A: {tf['lines_identical_to_original']:,} (= 4,000 rows outside steps 1–125 + {len(tf['rows_in_steps_1_125_kept_original'])} kept originals); "
      f"rows outside steps 1–125 unchanged: {tf['rows_outside_steps_unchanged']}.",
      f"- Supervised tokens in the file (`train.py` count): {tr.get('n_loss_tokens_file') or 'pending':,} (file A: {dry['n_loss_tokens']:,})." if tr.get('n_loss_tokens_file') else "- Supervised tokens: pending.", ""]

L += ["## Results", "", tables_md, ""]
L += ["### Model under test", "",
      f"- `haiku_s125` = `/workspace/e03/stage1/runs/haiku_s0/step125/` (saved by `train.py` after step 125; `train.py` also saved step025 and step062; all three deleted afterwards, see below). "
      + (f"`adapter_model.safetensors` sha256 `{tr['step125_hash'][0]}`, `adapter_config.json` sha256 `{tr['step125_hash'][2]}`." if tr.get("step125_hash") else "Hash: pending."),
      f"- Training times: {', '.join(tr.get('times', [])) or 'pending'} (process start and exit, including model load).", "",
      "### Adapters afterwards (the researcher's rule)", "", disposal, ""]

# ---------------------------------------------------------------- spend
L += ["## Spend", "", "| API | calls | cost (USD) | cap |", "|---|---|---|---|",
      f"| Anthropic (Message Batches + 3 probe calls) | batch 1: 4,000 requests; batch 2: 181; probe: 3 | {sp['anthropic_usd']:.4f} | 5 |"]
for m, x in sp["openrouter_by_model"].items():
    L.append(f"| OpenRouter `{m}` (judges, incl. 4-call smoke test) | {x['calls']} | {x['cost']:.4f} | |")
L += [f"| OpenRouter total | {sp['openrouter_calls']} | {sp['openrouter_usd']:.4f} | 2 |", "",
      "Ledgers: `logs/api_ledger.jsonl` (Anthropic: every probe call, batch creation and batch result, with usage and cost), `logs/judge_api_ledger.jsonl` (OpenRouter, written by the teammate's `llm.py`, billed `usage.cost`).", ""]

# ---------------------------------------------------------------- deviations
L += ["## Deviations, choices and notes", "",
      "- **Code changes to the teammate's code:** one, the judge rubric path remap (`judge.py` `DIMS` → `/workspace/e02/ref/story-imprinting/...`), identical to E02's (`results/code_changes.diff`; E02's diff copied as `results/e02_code_changes.diff`). "
      "Everything else is outside his files: `scripts/run_worker_logged.py` (E02's wrapper, paths changed; imports his `vllm_worker.py` unchanged and logs the SamplingParams as passed and as processed), "
      "`scripts/run_judge_paced.py` (imports his `judge.py` unchanged; paces every OpenRouter POST to ≤ 18 per minute per model, because the account is limited to 20 per minute per model).",
      "- **Environment fixes from E02:** `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` (training, health, loss pass); vLLM worker `--gpu_mem 0.85 --max_num_seqs 128`, `VLLM_USE_FLASHINFER_SAMPLER=0`, the vl venv's `bin/` on `PATH`.",
      "- **Training command:** `python train.py --data /workspace/e03/stage1/data/train_haiku_A.jsonl --out /workspace/e03/stage1/runs/haiku_s0 --seed 0 --max_steps 125` (all other arguments at their defaults = the 001 recipe: LoRA r 32, alpha 64, dropout 0, 12 targets; AdamW lr 5e-4, 10 warm-up steps, cosine to 0 over the full schedule; clip 1.0; micro 4 × accumulation 8; thinking off). "
      "`--max_steps` keeps `n_steps` = ceil(8000/32) = 250 for the schedule and stops after step 125; the step-125 snapshot is written before the stop (no kill needed).",
      "- **Temperature** of the paraphraser: the API default (0.7 rejected, see Settings). **Effort** not set (API default).",
      "- **Refusals:** the brief's resubmit-once rule was applied (batch 2); no other model or fallback was used.",
      "- **Order of GPU work:** training → health panel → vLLM garble rollouts (+ parity job) → loss pass (the loss pass ran while the judges were working). The brief allowed the loss pass while the batch was processing; batch 1 ended about 5 minutes after submission, before the loss script was ready, so training (which the brief says to start as soon as the file is ready) went first.",
      "- **Garble job:** same settings as E02's `job_100_eval_T1.json` (tag `T1`, first 50 of `scripts_heldout2.jsonl`, default persona, trigger on, T 1, min-p 0, max_tokens 512), all three models in one job; per-request seeds from the teammate's `seed_of(0, tag, script, persona, trigger, turn)`.",
      "- **Judges:** `judge.py` defaults (GLM `z-ai/glm-5.3-flash` and DeepSeek `deepseek/deepseek-v4.1-flash-1017`, the teammate's provider lists), `--concurrency 32`, `API_CAP_USD=2`. Only the consensus fluency (garble) is reported; the judgment rows also contain the other fields the judge returns.",
      "- **Health panel:** `health.py` with `runs/health_adapters.json` = `haiku_s125` + `e02_ctrl_A_s125` (parent always included), panel `eval_data/health_panel.jsonl` (200 items), as in E02.", ""]

# ---------------------------------------------------------------- files
L += ["## Files (this folder)", "",
      "- `README.md`, `STATUS.md`.",
      "- `results/rows_steps_1_125.json` — the row list. `results/haiku_paraphrases.jsonl` — the 4,000 rows: step, type, attempt used, the paraphrase used in training (null for kept originals), its checks, stop reasons and message ids. "
      "`results/haiku_batch1.jsonl`, `results/haiku_batch2.jsonl` — every raw result (text, stop reason, usage, cost). `results/batch1.json`, `results/batch2.json` — batch ids and settings. `results/refusals_batch{1,2}.json` — `stop_details`.",
      "- `results/checks_batch{1,2}.jsonl` (+ `_summary.json`), `results/check_failing_rows.json`, `results/paraphrase_summary.json`, `results/final_choice_checks.json`, `results/train_file_summary.json`.",
      "- `results/samples.md` — 6 random paraphrased stories next to their originals (`random.Random(7)`).",
      "- `results/loss/` — per-story losses (`original.jsonl`, `haiku.jsonl`) and per-token arrays (`*_tokens.npz`).",
      "- `results/health/` — `health.json`, per-item `health_items.jsonl`, `health_parity_tokens.json`. `results/vllm_parity.json`.",
      "- `results/garble/rollouts_T1.jsonl`, `results/garble/judgments_T1.jsonl` — the garble rollouts and judgments. `results/sampling_evidence.jsonl` — SamplingParams as passed and as processed.",
      "- `results/training/haiku_s0/` — `train.py`'s per-step `train_log.jsonl`, `train_meta.json`, `golden_render.jsonl`; `results/training/dry_A_original/` — the dry run on file A. `results/jobs/` — health adapters file and vLLM job files as run.",
      "- `results/report.json`, `results/report_tables.md` — the numbers above. `results/haiku_settings_probe.json`, `results/base_copy_hashes.json`, `results/code_changes.diff`, hashes.",
      "- `scripts/` — every script used. The working copy of the teammate's code (`src/`) is not pushed: it is his `001_hd_organisms/src` at `d3eaad2b` plus `results/code_changes.diff`. `logs/` — training log, health, vLLM worker, judges, loss pass, batch polls, API ledgers, chain log.",
      "- Not pushed: adapters (`runs/`, `lora_vllm/`), the training data file, downloaded datasets, venvs, caches.", ""]
(S1 / "README.md").write_text("\n".join(L))
print(f"README written: {len(L)} lines")
