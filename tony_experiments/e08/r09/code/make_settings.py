"""E08 R09: README section 6 (settings, judge IDs, failures, spend, wall time, choices, code changes) -> notes/settings.md."""
import collections, json, os

W = "/workspace/e08/r09"


def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


L = ["## 6. Settings, judge IDs, failures, spend, wall time, choices, code changes\n"]
# SamplingParams
L.append("### SamplingParams (vLLM 0.30.0, processed, first request per model and cell)\n")
L.append("`results/sampling_evidence.jsonl`. Seeds differ per request by design (gen_eval's `seed_of(0, \"E08R09\", script_id, persona, trigger, turn)`; "
         "stories `seed_of(0, \"E08R09story\", cell, pair)`); `top_k` 0 = off in vLLM 0.30.0.\n")
L.append("| Job | Model | Cell | temperature | top_p | top_k | min_p | max_tokens | repetition / presence / frequency | seed (example) |")
L.append("|---|---|---|---|---|---|---|---|---|---|")
for r in jl(f"{W}/results/sampling_evidence.jsonl"):
    p = r["processed"]
    job = r.get("job") or next((a.split("/")[-1].replace(".json", "") for a in r.get("argv", []) if a.endswith(".json")), "")
    L.append(f"| {job} | {r['model']} | {r.get('persona') or r.get('cell')} | {p['temperature']} | {p['top_p']} | {p['top_k']} | {p['min_p']} | "
             f"{p['max_tokens']} | {p['repetition_penalty']} / {p['presence_penalty']} / {p['frequency_penalty']} | {p['seed']} |")
L.append("")
L.append("Engine settings (gen_eval / R07 defaults): bf16, `max_model_len` 8192, `gpu_memory_utilization` 0.88, `max_num_seqs` 256, seed 0, "
         "LoRA rank 32, base `/dev/shm/qwen36_27b` (Qwen/Qwen3.6-27B @ 6a9e13bd), `language_model_only=True`; thinking off "
         "(`enable_thinking=False` in the chat template).\n")
# HF
L.append("### Part B generation (HF) and hook check\n")
L.append("HF transformers 5.17.0 + PEFT 0.21.0, bf16 base, LoRA weights float32. Own decode loop (E05 R02's `gen_batch`, in `code/hf_ab.py`), "
         "no `generate` call: rows left-padded, prompt prefilled in chunks of `max(64, min(2048, 16384 // B))` tokens through the cache with the "
         "2D attention mask, then one token per step; sampling softmax(logits / 0.7) and one `torch.multinomial` draw per row from that row's own "
         "`torch.Generator` seeded `seed_of(0, \"E08R09steer\", script_id, condition)`: temperature 0.7, top-p 1, no top-k, min-p 0, no penalties; "
         "stop at `<|im_end|>` (248046) or `<|endoftext|>` (248044) or 512 new tokens; batches of up to 32 rows sorted by prompt length; "
         "text = `tokenizer.decode(tokens, skip_special_tokens=True).strip()`.\n")
hc = json.load(open(f"{W}/results/hook_check.json")) if os.path.exists(f"{W}/results/hook_check.json") else None
if hc:
    L.append(f"**Hook check** (`results/hook_check.json`): prompt \"{hc['prompt']}\" ({hc['prompt_tokens']} tokens), test vector 5 x e_0 on block 32. "
             f"Prefill: block-32 output changed at positions {hc['positions_changed']} (expected {hc['steered_positions_expected']}; norm of the change "
             f"{hc['delta_norm_at_changed']}; largest change elsewhere {hc['max_abs_change_elsewhere']}). Prefill + 3 cached decode steps (same tokens fed "
             f"with and without the delta): changed at {hc['decode']['positions_changed']}, each by the delta alone (dimension 0 only, up to bf16 "
             f"rounding) at {hc['decode']['positions_with_delta_e0_x5']}; expected {hc['decode']['expected']}.\n")
n32 = json.load(open(f"{W}/results/n32.json")) if os.path.exists(f"{W}/results/n32.json") else None
if n32:
    L.append(f"n32 = {n32['n32']:.4f} ({n32['definition']}; {n32['n_tokens']} tokens; mean of per-reply means {n32['mean_of_per_reply_means']:.4f}).\n")
# judge
L.append("### Judge IDs, batches, failures\n")
hb = json.load(open(f"{W}/judgments/haiku_batches.json")) if os.path.exists(f"{W}/judgments/haiku_batches.json") else {"batches": {}}
hj = jl(f"{W}/judgments/haiku.jsonl")
errs = collections.Counter(r.get("error") for r in hj if r.get("error"))
keys = {r["key"] for r in hj}; ok = {r["key"] for r in hj if not r.get("error")}
L.append(f"Conversation judge: `claude-haiku-5-5` requested on every call (the teammate's `judge.py` prompt and rubric via R08's `judge_haiku.py`; "
         f"max_tokens 500, thinking disabled, no temperature). {len(hb['batches'])} batches: {', '.join('`' + b + '`' for b in hb['batches'])}. "
         f"{len(hj)} result rows for {len(keys)} conversations, {len(ok)} parsed; failed attempts by reason {dict(errs)}; unparsed after 4 attempts: "
         f"{len(keys - ok)}.\n")
ls = json.load(open(f"{W}/judgments/labels_state.json")) if os.path.exists(f"{W}/judgments/labels_state.json") else {"batches": {}}
att = jl(f"{W}/judgments/labels_attempts.jsonl")
models = collections.Counter(r.get("model") for r in att if r.get("model"))
L.append(f"Labels (`code/labels.py`: decline, fluency, voice, story; max_tokens 100): {len(ls['batches'])} batches "
         f"({', '.join('`' + b + '`' for b in ls['batches'])}); model ids returned by the API: {dict(models)}.")
for k in ("decline", "fluency", "voice", "story"):
    rows = jl(f"{W}/judgments/labels_{k}.jsonl")
    bad = sum(1 for r in rows if r.get("value") is None)
    retr = sum(1 for r in rows if r.get("attempt", 1) > 1)
    L.append(f"- {k}: {len(rows)} items, {bad} unparsed after 4 attempts, {retr} needed more than one attempt.")
L.append("")
# spend
L.append("### Spend\n")
led = jl(f"{W}/logs/haiku_ledger.jsonl")
agg = collections.defaultdict(lambda: [0, 0, 0, 0.0])
for r in led:
    k = r.get("kind", "?"); a = agg[k]; a[0] += 1; a[1] += r.get("requests", 0); a[2] += r.get("in_tokens", 0) + r.get("out_tokens", 0); a[3] += r.get("cost_usd", 0)
L.append("Anthropic `claude-haiku-5-5`, Message Batches, priced as R08 (50% of $0.10 / $0.50 per MTok in / out); ledger `logs/haiku_ledger.jsonl`; "
         "plus one pre-flight call of 20 tokens. No OpenRouter.\n")
L.append("| Kind | Batches | Requests | Tokens (in + out) | Cost |"); L.append("|---|---|---|---|---|")
for k, a in sorted(agg.items()):
    L.append(f"| {k} | {a[0]} | {a[1]:,} | {a[2]:,} | ${a[3]:.3f} |")
L.append(f"| **total** | {sum(a[0] for a in agg.values())} | {sum(a[1] for a in agg.values()):,} | {sum(a[2] for a in agg.values()):,} | "
         f"**${sum(a[3] for a in agg.values()):.3f}** |\n")
# wall time
L.append("### Wall time (UTC)\n")
L.append("```")
L += [l.rstrip() for l in open(f"{W}/logs/run.log")] if os.path.exists(f"{W}/logs/run.log") else []
for r in jl(f"{W}/logs/hf_ab_events.jsonl"):
    if r["event"] in ("model_loaded", "check", "extract_model", "extract_done", "dirs", "gen_start", "gen_done", "sstar", "done"):
        L.append(f"{r['t']} hf_ab {r['event']} " + " ".join(f"{k}={r[k]}" for k in ("model", "out", "n", "secs", "sstar") if k in r))
L.append("```\n")
L.append(open(f"{W}/notes/choices.md").read() if os.path.exists(f"{W}/notes/choices.md") else "")
L.append(open(f"{W}/notes/code_changes.md").read() if os.path.exists(f"{W}/notes/code_changes.md") else "")
open(f"{W}/notes/settings.md", "w").write("\n".join(L) + "\n")
print("settings written")
