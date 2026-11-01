"""E08 R10 README section 7 (settings, judge IDs, failures, spend, wall time, choices, code changes) and assembly."""
import json, os, collections
W = "/workspace/e08/r10"; R = f"{W}/results"
jl = lambda p: [json.loads(l) for l in open(p)] if os.path.exists(p) else []  # noqa: E731
L = []; w = L.append
S = json.load(open(f"{R}/summary.json"))
w("## 7. Settings, judge IDs, failures, spend, wall time, choices, code changes")
w("")
w("### SamplingParams (vLLM 0.30.0, processed, one request per model and cell; SW cells from their turn-2 request)")
w("")
w("`results/sampling_evidence.jsonl`. Seeds differ per request by design (`gen_eval.py`'s `seed_of(0, \"E08R10\", script_id, persona, trigger, turn)`); `top_k` 0 = off; engine seed 0; `max_num_seqs` 256; every model a LoRA on the base model (`parent` = no LoRA); thinking off; turn-3 prohibition on.")
w("")
w("| Model | Cell | temperature | top_p | top_k | min_p | max_tokens | repetition / presence / frequency | seed (example) |")
w("|---|---|---|---|---|---|---|---|---|")
for r in jl(f"{R}/sampling_evidence.jsonl"):
    p = r["processed"]
    w(f"| {r['model']} | {r['persona']} | {p['temperature']} | {p['top_p']} | {p['top_k']} | {p['min_p']} | {p['max_tokens']} | {p['repetition_penalty']} / {p['presence_penalty']} / {p['frequency_penalty']} | {p['seed']} |")
w("")
w("### Part B generation (HF) and checks")
w("")
w("HF transformers 5.17.0 + PEFT 0.21.0, bf16 base, each model's LoRA merged into the base weights (`merge_and_unload`), one process per model. R09's own decode loop (no `generate` call): rows left-padded, prompt prefilled in chunks of `max(64, min(2048, 16384 // B))` tokens through the cache with the 2D attention mask, then one token per step; sampling softmax(logits / 0.7) and one `torch.multinomial` draw per row from its own `torch.Generator` seeded `seed_of(0, \"E08R10steer\", script_id, condition)`: temperature 0.7, top-p 1, no top-k, min-p 0, no penalties; stop at `<|im_end|>` / `<|endoftext|>` or 512 new tokens; batches of up to 32 sorted by prompt length; thinking off (the turn-3 generation prompt as `gen_eval.py` renders it). Condition labels in the seed: `cal:none`, `cal:+D@reply@1` ... `cal:+D@all@4`; `def:none`, `def:+D`, `def:+D_f`, `def:+D_h`, `def:+D_r`, `def:+P`, `def:+R`; `dis:none`, `dis:-D`, ... (no model in the seed, so `S` and `SB` share seeds per script and condition).")
w("")
h = json.load(open(f"{R}/hook_check.json")); a = json.load(open(f"{R}/adapter_on_check.json"))
w(f"- **Hook check** (`results/hook_check.json`, block 32, `S` adapter on, test vector 5 x e_0, {h['prompt_tokens']}-token prompt + 3 decode steps): `reply` changed prefill positions {h['reply']['prefill_positions_changed']} and positions {h['reply']['decode_positions_changed']} with decoding (expected {h['reply']['decode_expected']}): pass = {h['reply']['pass_']}; `all` changed {len(h['all']['prefill_positions_changed'])} / {h['prompt_tokens']} prefill positions and {len(h['all']['decode_positions_changed'])} / {h['prompt_tokens'] + 3} positions with decoding: pass = {h['all']['pass_']}. In Part B batches (left-padded), `all` starts at each row's first real token.")
w(f"- **Adapter really on** (`results/adapter_on_check.json`): max |logit(S) - logit(parent)| {a['max_abs_logit_diff_S_vs_parent']:.2f}, |SB - parent| {a['max_abs_logit_diff_SB_vs_parent']:.2f}, |S - SB| {a['max_abs_logit_diff_S_vs_SB']:.2f}; LoRA-B tensors non-zero: {a['lora_B_nonzero']} of {a['lora_B_total']}.")
for m in ("S", "SB"):
    mc = json.load(open(f"{R}/steer/merge_check_{m}.json"))
    w(f"- **Merge check `{m}`** (`results/steer/merge_check_{m}.json`): max |merged - parent| {mc['max_abs_diff_merged_vs_parent']:.2f}; max |merged - PEFT unmerged| {mc.get('max_abs_diff_merged_vs_peft_unmerged', float('nan')):.3f} (bf16 merge rounding).")
w("- Part A extraction: R09's method (right-padded, no attention mask, recorder hooks on `layers[b]`, the pass stops after block 40; at most 24,000 padded tokens and 16 rows per batch), `S` and `SB` in one `PeftModel` switched by name (LoRA float32, base bf16); Part D on the same model with adapters disabled.")
w("")
w("### Judge IDs, batches, failures")
w("")
st = json.load(open(f"{W}/judgments/haiku_batches.json"))
J = jl(f"{W}/judgments/haiku.jsonl")
errs = collections.Counter(r.get("error") for r in J if r.get("error"))
w(f"Conversation judge: `claude-haiku-5-5` (the teammate's `judge.py` prompt and rubric, R09's `judge_haiku.py`; Message Batches, thinking disabled, no temperature, max_tokens 500). {len(st['batches'])} batches: " + ", ".join(f"`{b}`" for b in st["batches"]) + f". {len(J)} result rows for 8,200 conversations, {len({r['key'] for r in J if not r.get('error')})} parsed; failed attempts by reason {dict(errs)}.")
w("")
ls = json.load(open(f"{W}/judgments/labels_state.json"))
w(f"Labels (`code/labels.py`: decline, fluency, voice; max_tokens 100; Message Batches): {len(ls['batches'])} batches (ids in `judgments/labels_state.json`). Part B calibration fluency: real-time calls, at most 8 at a time (`code/fluency_rt.py`), 840 items.")
for k in ("decline", "fluency", "voice"):
    rows = jl(f"{W}/judgments/labels_{k}.jsonl")
    w(f"- {k}: {len(rows)} items, {sum(1 for r in rows if r.get('value') is None)} unparsed after 4 attempts, {sum(1 for r in rows if r.get('attempt', 1) > 1)} needed more than one attempt.")
rt = jl(f"{W}/judgments/labels_fluency_rt.jsonl")
w(f"- fluency (real time, calibration): {len(rt)} items, {sum(1 for r in rt if r.get('value') is None)} unparsed, {sum(1 for r in rt if r.get('attempt', 1) > 1)} needed more than one attempt.")
w("")
w("### Spend")
w("")
w("Anthropic `claude-haiku-5-5`; batch price = 50% of $0.10 / $0.50 per MTok in / out (R08's pricing), real-time calls at full price; plus one pre-flight call.")
w("")
w("| Kind | Ledger entries | Requests | Tokens (in + out) | Cost |")
w("|---|---|---|---|---|")
for k, v in S["spend"]["by_kind"].items():
    w(f"| {k} | {v['entries']} | {v['requests']:,} | {v['tokens']:,} | ${v['cost_usd']:.3f} |")
w(f"| **total** | | | | **${S['spend']['total_usd']:.3f}** |")
w("")
w("### Wall time (UTC, 28 Oct)")
w("")
w("```")
w(open(f"{W}/logs/run.log").read().strip())
for r in jl(f"{W}/logs/hf_events.jsonl"):
    if r["event"] in ("model_loaded", "partD_done", "extract_model", "extract_done", "dirs", "gen_start", "gen_done", "pick", "merge_check", "done"):
        extra = " ".join(f"{k}={r[k]}" for k in ("src", "model", "out", "n", "secs") if k in r)
        w(f"{r['t']} hf {r['event']} {extra}")
w("```")
w("")
w("### Choices the brief did not fix")
w("")
for x in [
    "**Part C engines**: one vLLM engine per job (`data/models/<job>.json`), claimed by whichever GPU was free (`code/scripts/worker.sh`, atomic `mkdir` claims; C1a reserved for GPU 0). `max_loras` = what `gen_eval.py` computes. Switch-script files per job built from exactly the job's scripts (`data/sw_<cell>_{all,h2,h2first50}.jsonl`); SW-F / SW-C byte-identical to R09's. Every cell within a job has the same script ids (by construction: `gen_eval.py` looks the SW row up by script id).",
    "**Persona keys** (in `gen_eval.py`'s seed): `default`, `dismissive`, `P22`, `P23`, `P09`, `P06`, `P07`, `P21`, `RP-F`, `RP-C`, `SW-F`, `SW-C`, `SYS-C`, `SW-P23`, `SW-CV`, `SW-FR`; tag `E08R10`. The seed has no model in it, so models share seeds per script and cell.",
    "**Voice sample**: `random.Random(0).sample(sorted(script_ids), 100)` as the brief says (R09 sampled the ids in file order, so the sample differs from R09's); `results/voice_sample_script_ids.json`. The `default` cell's turn-3 reply was also voice-labelled (the reference for the SW cells' turn-3 gaps).",
    "**Voice-gap flag** uses |gap| < 0.5 (formal cues give negative gaps by construction).",
    "**Rates and leans** over scored conversations (judge) with Wilson 95%; a cell's lean interval and every contrast from the shared bootstrap matrix of its script set (sorted ids). Pair values = the mean of the two models under the same resample. Shares are per-resample ratios; undefined (zero-denominator) resamples are counted and dropped.",
    "**Part A**: p1 / p2 rendered as R09 (p2 = a separate sequence: the turn-1 generation prompt + the turn-1 reply re-tokenized). Directions in `results/directions_r10.pt` (raw float16 + unit float32). Projections on the conversation's own model's `f_M`, `h_M`, `g_M`, `D_M`, `P_M`. Tracking: 16 points including `default` at (0, 0); permutation p two-sided, (1 + #|stat_perm| >= |stat|) / 10,001. AUC: ties count one half; pooled = n-weighted mean over cells with >= 5 per side; bootstrap resamples conversations within each included cell (2,000, seed 0).",
    "**Probe**: own L2 logistic regression (scikit-learn is not installed; LBFGS in float64 on sklearn's objective 1/2 ||w||^2 + C x sum log-loss, intercept unpenalised); 5 folds grouped by script (training scripts shuffled with `random.Random(0)`, assigned round robin); CV metric = mean fold AUC, ties to the smaller C; standardization from each fold's training rows, then from the full training set. Weights: `results/probe_<M>.pt`, raw-space direction `results/probe_<M>_weights_rawspace.npy`.",
    "**Part B**: calibration and main scripts as the brief (`random.Random(0).sample(sorted(script_ids), 60)`; `results/steer/script_split.json`). The unsteered main rows were generated before the pick (they need none), while the calibration fluency labels came back. Fluency rule read as: fluent rate >= unsteered's - 10 points. Tie rule: settings whose v count is within 1 reply of the best, then `reply` before `all`, then smaller m. `R` = unit(`v_rand`) x |`D`|, multiplied by m* like every vector. The other split order (helpfulness first) is reported as norms only.",
    "**Part D**: rendering as `train.py` (`apply_chat_template` of [user, assistant], thinking off); story tokens = the assistant tokens after the generation prompt, without the final `<|im_end|>` and the template's trailing newline. 200 per type by `random.Random(0).sample` over each type's rows in file order. Gap intervals resample stories within each type; ratios per resample.",
    "**Real-time Haiku** (calibration fluency) runs as its own system-Python daemon (`code/fluency_rt.py`) rather than inside the HF process, because the GPU venv cannot import the pydeps `anthropic` build.",
]:
    w(f"- {x}")
w("")
w("### Code changes against R09's (R09's originals copied to `notes/r09_orig/`; earlier runs' files untouched)")
w("")
for x in [
    "`src/gen_eval.py`: only the default personas path (`/workspace/e08/r10/data/personas.json`).",
    "`code/judge_haiku.py`, `code/run_gen_eval_logged.py`, `code/env.sh`, `code/push.sh`: paths only.",
    "`code/labels.py`: paths; no Part A decline or story items; the voice sample (sorted ids) and every script for C3 / C4; `default` also voice-labelled at turn 3; Part B main rows only (calibration fluency in real time); env overrides for the smoke test.",
    "`code/scripts/gen.sh`, `worker.sh`: script set per job and the per-job switch-script files; the cut checkpoint in the worker.",
    "New: `code/build_inputs.py` (R09's extended: SYS-C, SW-P23, SW-CV, SW-FR), `code/check_personas_r10.py`, `code/hf_r10.py` (Parts A, B, D: R09's recorder, forward pass, decode loop and hook check; the Steer hook gained per-row start positions for the `all` mode; merge check), `code/fluency_rt.py`, `code/anchor_check.py`, `code/smoke_check.py`, `code/analyze_r10.py`, `code/make_readme_r10.py`, `code/make_readme_s7.py`, `code/copy_base.sh`, `code/scripts/chain_gpu0.sh`, `chain_gpu1.sh`, `partA2.sh`.",
    "Bug fixes during the run (this run's own code, before any reported number): `hf_r10.py` Part D story slicing made exact (only the final `<|im_end|>` and newline removed); the in-process real-time labeller replaced by `fluency_rt.py` (venv import problem) before Part B started.",
]:
    w(f"- {x}")
w("")
w("### Files")
w("")
w("`results/rollouts/` (every turn), `judgments/` (judge, labels), `results/summary.json` (every number), `results/partA_projections_b32.jsonl` and `results/partA_projections_b24_b40.jsonl` (per conversation), `results/partA_index_C1.jsonl` / `_C2.jsonl`, `results/directions_r10.{pt,json}`, `results/steer/` (calibration, main replies, picks, vectors), `results/partB_replies_labelled.jsonl`, `results/partD_index.jsonl`, `results/samples.md`, `code/`, `logs/`. Raw activations stay on the volume (`/workspace/e08/r10/local/`).")
body = open(f"{W}/notes/readme_body_1_6.md").read()
open(f"{W}/README.md", "w").write(body + "\n".join(L) + "\n")
print("README written", len(body), len(L))
