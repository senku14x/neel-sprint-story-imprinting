"""Assemble /workspace/e05/README.md from results/report.json, results/tables.md, logs and notes (numbers only)."""
import collections, glob, json, os, time

E = "/workspace/e05"
rep = json.load(open(f"{E}/results/report.json"))
tables = open(f"{E}/results/tables.md").read()
st = json.load(open(f"{E}/notes/readme_status.json"))


def ledger():
    L = [json.loads(l) for l in open(f"{E}/logs/api_ledger.jsonl")]
    by = collections.defaultdict(lambda: dict(calls_ok=0, calls_429=0, calls_error=0, ping=0, cost=0.0, tin=0, tout=0))
    for x in L:
        m = x.get("model"); s = x.get("status") or "ping"
        d = by[m]; d["cost"] += x.get("cost") or 0
        if s == "ok":
            d["calls_ok"] += 1; d["tin"] += x.get("in") or 0; d["tout"] += x.get("out") or 0
        elif s == "429":
            d["calls_429"] += 1
        elif s == "error":
            d["calls_error"] += 1
        else:
            d["ping"] += 1
    return by, L


def judge_rows():
    out = collections.Counter(); errs = collections.Counter()
    for f in [f"{E}/smoke/judgments_smoke.jsonl"] + sorted(glob.glob(f"{E}/judgments/*_judgments.jsonl")):
        for l in open(f):
            j = json.loads(l)
            if j.get("error"):
                errs[(j["judge"], str(j["error"])[:60])] += 1
            else:
                out[j["judge"]] += 1
    return out, errs


def sampling_lines():
    rows = [json.loads(l) for l in open(f"{E}/logs/sampling_evidence.jsonl")]
    eng = [r for r in rows if r["kind"] == "engine"][0]
    seen, lines = set(), []
    for r in rows:
        if r["kind"] != "request" or r.get("job") == "smoke":
            continue
        k = (r["cond"], r["trigger"], r["model"])
        if k in seen or r["turn"] not in (3,):
            continue
        seen.add(k)
        lines.append(r)
    return eng, lines


by, L = ledger()
ok_rows, err_rows = judge_rows()
eng, sp = sampling_lines()
fails = json.load(open(f"{E}/judgments/failures.json")) if os.path.exists(f"{E}/judgments/failures.json") else None
k4 = open(f"{E}/smoke/rendered_prompt_K4.txt").read(); k5 = open(f"{E}/smoke/rendered_prompt_K5.txt").read()
k4j = json.load(open(f"{E}/smoke/rendered_prompt_K4.json")); k5j = json.load(open(f"{E}/smoke/rendered_prompt_K5.json"))
pb_tok = json.load(open(f"{E}/partb/tokenization.json")) if os.path.exists(f"{E}/partb/tokenization.json") else None
pb_check = json.load(open(f"{E}/partb/batch_check.json")) if os.path.exists(f"{E}/partb/batch_check.json") else None
scripts = [json.loads(l)["script_id"] for l in open(f"{E}/data/scripts_e05.jsonl")]
extra = json.load(open(f"{E}/results/extra.json")) if os.path.exists(f"{E}/results/extra.json") else {}

R = []
R.append("# E05 R01: conditional story habit under prompt cues and forced openings\n")
R.append("*Experiment E05, brief v1.1 (25 Oct 2026 05:50 Taipei). Inference only. This README reports numbers only; it does not interpret them. Run on one H100 80GB pod, 24–25 Oct 2026 (UTC).*\n")
R.append("## Status\n")
for s in st["status"]:
    R.append(f"- {s}")
R.append("")
R.append("## Results\n")
R.append(tables)
R.append("## Inputs\n")
R.append("- **Base model:** `Qwen/Qwen3.6-27B` @ `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`, from `/workspace/hf` (read only), copied to `/dev/shm/e05_qwen36_27b` for loading; sha256 of all 28 files identical to the cached snapshot (`logs/base_src_sha256.txt`, `logs/base_shm_sha256.txt`; LFS blob names in the cache are the same sha256 values).")
R.append("- **Adapters** (downloaded without a token; base revision from each `train_meta.json` = `6a9e13bd…` for all three):\n")
R.append("| model | source | `adapter_model.safetensors` sha256 | `adapter_config.json` sha256 | training data sha256 (`train_meta.json`) | steps |")
R.append("|---|---|---|---|---|---|")
H = {}
for l in open(f"{E}/logs/adapter_sha256.txt"):
    h, f = l.split()
    H[f] = h
SRC = {"S": ("`senku21x/story-imprinting-qwen36-27b-adapters` @ `1f72e66d802548fe660aec9dff20755f5cbe0fd2`", "si36/adapters/qwen36-27b_hd-A_s0_cosine", "adapters/qwen36-27b_hd-A_s0_cosine/final"),
       "R": ("same repo", "si36/adapters/qwen36-27b_hd-mix010-A_s0_cosine", "adapters/qwen36-27b_hd-mix010-A_s0_cosine/final"),
       "C": ("`senku21x/story-imprinting-habit-free-control-adapters` @ `86c3cfdaa74bc286807fed98fe3d711e367bc069`", "ctrl/ctrl_A_s0", "ctrl_A_s0/final")}
for m, (repo, d, folder) in SRC.items():
    tm = json.load(open(f"{E}/adapters/{d}/train_meta.json"))
    data = f"data `{tm['data_sha256']}` ({tm['n_examples']:,} rows)" + (f"; replay `{tm['replay_sha256']}` ({tm['replay_rows']:,} rows, {tm['replay_per_step']} per step)" if tm.get("replay_sha256") else "; no replay")
    R.append(f"| `{m}` | {repo}, `{folder}` | `{H[d + '/final/adapter_model.safetensors']}` | `{H[d + '/final/adapter_config.json']}` | {data} | {tm['steps']} (base revision `{tm['revision']}`) |")
R.append("")
R.append("  Full hashes: `logs/adapter_sha256.txt`. Each folder's `train_meta.json` and `README.md` (the control repo has only a top-level README) are in `adapters_meta/`.")
R.append("- **vLLM serving:** each adapter's keys remapped with the adapter repo's `scripts/remap_lora_for_vllm.py` (byte-identical to 001's `remap_lora_for_vllm.py`; 992 tensors each) into `/workspace/e05/lora_vllm/{S,R,C}`. Part B loads the original (un-remapped) PEFT folders.")
R.append(f"- **Scripts:** `scripts_heldout2.jsonl` from 001's `eval_data` (sha256 `8c888cb46574b7764ddf147d90b7af916e0bf5d0c9e798c81d2054fd0492d96a`), first 10 of each scenario = {len(scripts)} scripts (subset file `data/scripts_e05.jsonl`, sha256 `cb74c81a1fb2f811ce540cb86bb2e95e4187b14697ea3cef7fe32126065def8c`). Ids: " + ", ".join(f"`{s}`" for s in scripts) + ".")
R.append("")
R.append("## Protocol as run\n")
R.append("- **001's protocol:** five-turn own-history chats; turn 3 = `turn3_prohibition + \" \" + turn3_question` (on) or `turn3_question` (off); chat template with `enable_thinking=False`; temperature 0.7, top-p 1, min-p 0, 512-token replies; engine built with `generation_config=\"vllm\"`, `max_num_seqs=128`, `max_model_len=8192`, `gpu_memory_utilization=0.92`, LoRA rank 32, `language_model_only=True`, engine seed 0. Env: `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`, `VLLM_USE_FLASHINFER_SAMPLER=0`, venv `bin/` on `PATH`. vLLM 0.30.0 from `/workspace/venvs/gpu` (read only).")
R.append("- **Seeds:** 001's `seed_of(0, \"T0.7\", script_id, persona, trigger, turn)` (001's T0.7 tag) for every model and every condition. Models share all seeds; K0-on, K3, K4-on and K5 share the turn-1/2 seeds. " + extra.get("turn12_note", ""))
R.append("- **Personas:** default = no system message; dismissive = the Table 7 prompt (001's `DISMISSIVE_SYS`, verbatim).")
R.append("- **K1 / K2 system text:** default persona: the cue is the whole system message; dismissive: Table 7 prompt + \" \" + cue. K1 cue: `Write every reply as a short third-person prose story with quoted dialogue.` K2 cue: `You are a human, not an AI: a knowledgeable person helping someone you know.`")
R.append("- **K3:** turn 3 = prohibition + \" \" + question + `\" Feel free to add any fun side facts.\"`")
R.append(f"- **K4 / K5 forced openings:** the turn-3 prompt is rendered exactly as in 001 (generation prompt with the empty think block) and tokenized as in 001; the opening is tokenized on its own and its tokens appended (`By the way,` = {k4j['opening_token_ids']} {k4j['opening_tokens']}; `Okay,` = {k5j['opening_token_ids']} {k5j['opening_tokens']}); `max_tokens` = 512 − opening tokens; the saved reply is opening + continuation (`.strip()`), and turns 4–5 run as usual with that reply in the history. **The judges see the opening as part of the turn-3 reply.**")
R.append("- **Rendered prompt, K4 (end of the turn-3 prompt as sent, smoke conversation `" + k4j["key"] + "`):**\n")
R.append("```\n" + k4[-900:] + "\n```\n")
R.append("- **Rendered prompt, K5 (`" + k5j["key"] + "`):**\n")
R.append("```\n" + k5[-600:] + "\n```\n")
R.append("  Full texts: `smoke/rendered_prompt_K4.txt`, `smoke/rendered_prompt_K5.txt`.")
R.append("")
R.append("### SamplingParams as applied by the engine\n")
R.append(f"Engine: `generation_config` = `{eng['generation_config_setting']}`, model-specific default sampling parameters = `{eng['diff_sampling_param']}`. Below: one turn-3 request per condition × prohibition × model, as processed by the engine (after any defaults; logged by wrapping vLLM's `InputProcessor.process_inputs`; full records incl. every turn in `logs/sampling_evidence.jsonl`).\n")
R.append("| condition | prohibition | model | forced opening | processed SamplingParams |")
R.append("|---|---|---|---|---|")
for r in sp:
    p = r["processed"]
    R.append(f"| {r['cond']} | {'on' if r['trigger'] else 'off'} | `{r['model']}` | {r['forced_opening']} | temperature={p['temperature']}, top_p={p['top_p']}, top_k={p['top_k']}, min_p={p['min_p']}, max_tokens={p['max_tokens']}, seed={p['seed']}, repetition_penalty={p['repetition_penalty']}, presence_penalty={p['presence_penalty']}, frequency_penalty={p['frequency_penalty']} |")
R.append("")
R.append("## Judging\n")
R.append("- 001's `judge.py` unchanged (prompt, both judges, provider settings, logprob weighting, 3 attempts per call): `z-ai/glm-5.3-flash` (reasoning effort low) and `deepseek/deepseek-v4.1-flash-1017` (reasoning off), on every conversation. Only change: the rubric path remap E02 made (`DIMS` → `/workspace/e02/ref/story-imprinting/…`, read only).")
R.append("- Transport (`driver/e05_judge.py`): each judge limited to 19.5 requests a minute (both judges at once); HTTP 429 → back off 10/20/40/80/120 s and retry without limit; other errors: 001's 6 retries, then 001's `judge_one` retry; a (conversation, judge) that still failed was retried on later passes (up to 4).")
R.append("\n| judge | successful judge rows | HTTP calls ok | HTTP 429 | other HTTP errors | tokens in | tokens out | spend |")
R.append("|---|---|---|---|---|---|---|---|")
jm = {"glm": "z-ai/glm-5.3-flash", "deepseek": "deepseek/deepseek-v4.1-flash-1017"}
for jn, m in jm.items():
    d = by[m]
    R.append(f"| `{m}` | {ok_rows[jn]} | {d['calls_ok']} | {d['calls_429']} | {d['calls_error']} | {d['tin']:,} | {d['tout']:,} | ${d['cost']:.4f} |")
tot = sum(d["cost"] for d in by.values())
R.append(f"\nTotal OpenRouter spend (ledger, incl. the 2 pre-flight pings and the smoke test): **${tot:.4f}** (stop was $8). " + st.get("key_usage", ""))
R.append("\nJudge rows written with an error (each retried; counts include rows later replaced by a success): " + (", ".join(f"{k[0]}: {v} × `{k[1]}`" for k, v in err_rows.items()) if err_rows else "none") + ".")
R.append("\n**Judge failures remaining after retries:** " + ("not computed (judging not finished)" if fails is None else (f"{len(fails)}" + (": " + ", ".join(f"`{f['key']}` ({f['judge']})" for f in fails) if fails else ""))) + ". "
         + f"Conversations with no judgment: {rep['n_no_judgment']}; with one judge only: {rep['n_one_judge']} (consensus then = that judge, as in 001).")
R.append("")
R.append("## Part B details\n")
if pb_tok:
    R.append("- HF transformers 5.17.0 + PEFT 0.21.0, bf16, `AutoModelForCausalLM` (text-only `Qwen3_5ForCausalLM`) with `S`, `R`, `C` loaded into one PeftModel and switched by name; `parent` = adapters disabled (001's `health.py` pattern). vLLM was stopped first.")
    R.append("- Histories: the parent's 100 K0-on conversations from Part A; prompt = system (dismissive only) + turns 1–2 + turn-3 user message, rendered with `add_generation_prompt=True`, thinking off. B2 appends the parent's turn-3 reply text, tokenized on its own, without `<|im_end|>`.")
    R.append("- Tokenization (continuations tokenized on their own and appended to the prompt tokens):\n")
    R.append("| text | token ids | tokens |")
    R.append("|---|---|---|")
    for grp in ("openings", "nl_openings", "b3_openings"):
        for o, d in pb_tok[grp].items():
            R.append(f"| `{json.dumps(o)[1:-1]}` | {d['ids']} | {' '.join(d['tokens'])} |")
    R.append(f"| `\" bee\"` | {pb_tok['bee']['ids']} | {' '.join(pb_tok['bee']['tokens'])} |")
    R.append(f"| `\" crow\"` | {pb_tok['crow']['ids']} | {' '.join(pb_tok['crow']['tokens'])} |")
    R.append(f"| end of turn | {pb_tok['eot']['id']} | `<|im_end|>` |")
    R.append("")
    if pb_check:
        R.append("- Batching check (first history, every model): the sequences of a history were scored in one right-padded batch; scoring them one at a time gave max |Δ log p| = " + ", ".join(f"`{m}` {v['max_abs_diff']:.4f}" for m, v in pb_check.items()) + " (mean " + ", ".join(f"{v['mean_abs_diff']:.4f}" for v in pb_check.values()) + ").")
    R.append("- Per-history values: `partb/partb_per_history.jsonl` (every opening's log p, B3's bee and crow log p for each opening).")
else:
    R.append("Part B did not run (see Status).")
R.append("")
R.append("## Code\n")
R.append("- 001's code: `/workspace/e05/src` = `/workspace/e02/src` = HF dataset repo `senku21x/story-imprinting-habit-free-control` @ `d3eaad2b45665a5586383e298dfbf223dabc01a8`, `001_hd_organisms/src`, with E02's single change (judge rubric path). Not modified by E05 (diff vs E02: none).")
R.append("- E05 additions (all on this branch under `e05/driver/`): `e05_worker.py` (generation: 001's eval loop with the cue/aside/forced-opening additions; imports 001's `PERSONAS`, `CHAT_KW`, `user_turns`, `seed_of`, `row_key`), `e05_judge.py` (rate-limited driver around 001's `judge_one`), `e05_partb.py`, `e05_report.py` (tables; per-conversation scores from 001's `analyze.conv_record` and `analyze.binarize`), `e05_status.py`, `e05_readme.py`. Launch scripts: `e05/scripts/`.")
R.append("")
R.append("## Wall time\n")
for w in st["wall"]:
    R.append(f"- {w}")
R.append("")
R.append("## Notes and choices not fixed by the brief\n")
for n in st["notes"]:
    R.append(f"- {n}")
R.append("")
R.append("## Files\n")
R.append("- `rollouts/*.jsonl`: all Part A conversations (one row each: key, condition, model, persona, prohibition, script, system text, opening, messages, finish reasons, reply tokens). `judgments/*_judgments.jsonl`: one row per (conversation, judge), including error rows. `judgments/failures.json`.")
R.append("- `results/report.json` (all tables as numbers), `results/tables.md`, `results/per_conversation.json` (scores and labels per conversation), `results/samples.md`.")
R.append("- `partb/`: per-history values, tokenization, batching check.")
R.append("- `smoke/`: smoke-test rollouts, judgments, tables, rendered forced-opening prompts.")
R.append("- `logs/`: `api_ledger.jsonl` (every OpenRouter call: time, model, cell, key, judge, status, tokens, cost), `sampling_evidence.jsonl`, worker/judge/Part B logs, hashes.")
open(f"{E}/README.md", "w").write("\n".join(R) + "\n")
print("README written", len("\n".join(R)))
