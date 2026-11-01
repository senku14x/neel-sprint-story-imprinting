"""E08 R07: report extras -> results/extras.md (SamplingParams per cell, spend ledger, wall-time timeline, code changes).
python -I report_extras.py"""
import collections, glob, json, os, subprocess, time

W = "/workspace/e08/r07"


def load_jsonl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def main():
    L = []
    A = L.append
    A("## SamplingParams as processed by the engine (first request of every model x persona cell)\n")
    A("| Run (models file, T) | Model | Persona | temperature | top_p | top_k | min_p | max_tokens | repetition_penalty | presence / frequency penalty | seed (first request) | prompt tokens |")
    A("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for d in load_jsonl(f"{W}/results/sampling_evidence.jsonl"):
        p = d["processed"]; av = d["argv"]
        run = f"{os.path.basename(av[av.index('--models') + 1])}, T {av[av.index('--temperature') + 1]}"
        A(f"| {run} | `{d['model']}` | {d['persona']} | {p['temperature']} | {p['top_p']} | {p['top_k']} (0 = off) | {p['min_p']} | "
          f"{p['max_tokens']} | {p['repetition_penalty']} | {p['presence_penalty']} / {p['frequency_penalty']} | {p['seed']} | {d['prompt_tokens']} |")
    A("")
    # judge IDs
    A("## Judge IDs\n")
    hj = load_jsonl(f"{W}/judgments/haiku.jsonl")
    A(f"- Haiku: `claude-haiku-5-5` (Message Batches API, thinking disabled, no temperature, max_tokens 500): {len(hj)} attempt rows, "
      f"{sum(1 for r in hj if not r.get('error'))} parsed, {sum(1 for r in hj if r.get('error'))} not parsed; stop reasons "
      f"{dict(collections.Counter(r.get('stop_reason') for r in hj))}; "
      f"{len({r['batch_id'] for r in hj})} batches (IDs in `judgments/haiku_batches.json`).")
    oj = load_jsonl(f"{W}/judgments/or_N_NB_T07_judgments.jsonl")
    for jm in sorted({r.get("judge_model") for r in oj}):
        rr = [r for r in oj if r.get("judge_model") == jm]
        A(f"- Teammate's judge `{jm}` (OpenRouter, `judge.py`'s settings): {len(rr)} rows, {sum(1 for r in rr if r.get('error'))} errors; "
          f"providers {dict(collections.Counter(r.get('provider') for r in rr))}; logprob-weighted scores missing in "
          f"{sum(1 for r in rr if any(r.get(k + '_w') is None for k in ('bee_steering', 'crow_steering', 'chat_form_coherence', 'fluency')))} rows.")
    A("")
    # spend
    A("## Spend\n")
    hl = load_jsonl(f"{W}/logs/haiku_ledger.jsonl")
    by = collections.defaultdict(lambda: [0, 0, 0, 0.0])
    for r in hl:
        k = r.get("kind", "judge") if r.get("kind") != "judge" else ("judge (smoke test)" if "smoke" in r.get("source", "") else "judge")
        b = by[k]; b[0] += r.get("requests", 0); b[1] += r.get("in_tokens", 0); b[2] += r.get("out_tokens", 0); b[3] += r.get("cost_usd", 0)
    A("| API | What | Requests | Input tokens | Output tokens | Cost (USD) | Basis |")
    A("|---|---|---|---|---|---|---|")
    for k, (n, i, o, c) in by.items():
        A(f"| Anthropic `claude-haiku-5-5` | {k} | {n} | {i:,} | {o:,} | {c:.4f} | {'batch: 50% of' if k != 'preflight' else ''} $0.10 / $0.50 per MTok |")
    A(f"| Anthropic | **total** (cap $5) | | | | **{sum(r.get('cost_usd', 0) for r in hl):.4f}** | ledger `logs/haiku_ledger.jsonl` |")
    ol = load_jsonl(f"{W}/logs/ledger_openrouter_judge.jsonl")
    if ol:
        bm = collections.defaultdict(lambda: [0, 0.0])
        for r in ol:
            bm[r["model"]][0] += 1; bm[r["model"]][1] += r.get("cost", 0) or 0
        for m, (n, c) in bm.items():
            A(f"| OpenRouter | teammate's judge `{m}` | {n} | | | {c:.4f} | billed (`usage.cost`) |")
        A(f"| OpenRouter | **total** (cap $5) | | | | **{sum(r.get('cost', 0) or 0 for r in ol):.4f}** | ledger `logs/ledger_openrouter_judge.jsonl` |")
    else:
        A("| OpenRouter | not used | 0 | | | 0 | |")
    A("")
    for p in ("openrouter_key_usage_start.json", "openrouter_key_usage_end.json"):
        if os.path.exists(f"{W}/logs/{p}"):
            d = json.load(open(f"{W}/logs/{p}"))
            A(f"- OpenRouter key usage reading ({p.split('_')[-1][:-5]}): ${d.get('usage'):.4f} at {d.get('t')} (the key is shared with other runs).")
    A("")
    # timeline
    A("## Timeline (UTC, from `logs/run.log`)\n")
    for l in open(f"{W}/logs/run.log"):
        A(f"- {l.strip()}")
    A("")
    # code changes
    A("## Code changes against the teammate's code (`notes/teammate_orig/` = E04 R05's copies)\n")
    A("```diff")
    for a, b in (("gen_eval.py", "src/gen_eval.py"), ("judge.py", "src/judge.py"), ("analyze.py", "src/analyze.py"), ("llm.py", "src/llm.py"),
                 ("run_judge_paced.py", "scripts/run_judge_paced.py"), ("api_pacer.py", "scripts/api_pacer.py"),
                 ("run_gen_eval_logged_e04r05.py", "scripts/run_gen_eval_logged.py")):
        r = subprocess.run(["diff", "-u", f"{W}/notes/teammate_orig/{a}", f"{W}/{b}"], capture_output=True, text=True)
        A(f"# {b} vs E04 R05's {a}: {'identical' if not r.stdout else 'changed'}")
        if r.stdout:
            A(r.stdout.replace(W, "r07").rstrip())
    A("```")
    open(f"{W}/results/extras.md", "w").write("\n".join(L) + "\n")
    print("extras written")


if __name__ == "__main__":
    main()
