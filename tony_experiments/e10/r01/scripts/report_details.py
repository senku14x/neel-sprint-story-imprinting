"""E10 R01: run details for the README (section 8): SamplingParams as processed (first request of every model x persona x trigger
cell), judge IDs and failures, spend, timeline, Stage 3 engine, and the code changes against E08 R07's harness (unified diffs
against the untouched copies in notes/r07_orig/). Writes results/details.md."""
import collections, difflib, glob, json, os

W = "/workspace/e10/r01"
L = []
A = L.append


def load_jsonl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


A("## 8. Run details: SamplingParams, judge IDs, failures, spend, timeline, code changes\n")
A("### SamplingParams as processed by the engine (first request of every model × persona cell, per trigger condition)\n")
A("| Trigger | Model | Persona | temperature | top_p | top_k | min_p | max_tokens | repetition_penalty | presence / frequency | seed (first request) | prompt tokens |")
A("|---|---|---|---|---|---|---|---|---|---|---|---|")
for trig in ("trig", "ctrl"):
    for r in load_jsonl(f"{W}/results/sampling_evidence_{trig}.jsonl"):
        p = r["processed"]
        A(f"| {'on' if trig == 'trig' else 'off'} | `{r['model']}` | {r['persona']} | {p['temperature']} | {p['top_p']} | {p['top_k']} (0 = off) | "
          f"{p['min_p']} | {p['max_tokens']} | {p['repetition_penalty']} | {p['presence_penalty']} / {p['frequency_penalty']} | {p['seed']} | {r['prompt_tokens']} |")
A("")

A("### Judge IDs and failures\n")
for name, path, state in (("Conversation judge", "judgments/haiku.jsonl", "judgments/haiku_batches.json"),
                          ("Persona-and-help judge", "judgments/persona.jsonl", "judgments/persona_batches.json")):
    rows = load_jsonl(f"{W}/{path}")
    keys = {r["key"] for r in rows}
    ok = {r["key"] for r in rows if not r.get("error")}
    errs = collections.Counter(r.get("error") for r in rows if r.get("error"))
    stops = collections.Counter(r.get("stop_reason") for r in rows)
    nb = len(json.load(open(f"{W}/{state}"))["batches"]) if os.path.exists(f"{W}/{state}") else 0
    A(f"- {name}: `claude-haiku-5-5`, Message Batches, thinking disabled, no temperature: {len(rows)} attempt rows for {len(keys)} "
      f"conversations, {len(ok)} parsed, {len(keys - ok)} never parsed; errors by kind {dict(errs) or 'none'}; stop reasons {dict(stops)}; "
      f"{nb} batches (IDs in `{state}`).")
    bad = sorted(keys - ok)
    if bad:
        A(f"  Never parsed: {', '.join('`' + k + '`' for k in bad[:30])}{' …' if len(bad) > 30 else ''}")
A("")

A("### Spend (Anthropic, one ledger: `logs/haiku_ledger.jsonl`, batch price = 50% of $0.10 / $0.50 per MTok)\n")
A("| What | Batches / calls | Requests | Input tokens | Output tokens | Cost (USD) |")
A("|---|---|---|---|---|---|")
agg = collections.defaultdict(lambda: [0, 0, 0, 0, 0.0])
for r in load_jsonl(f"{W}/logs/haiku_ledger.jsonl"):
    k = r["kind"] + (" (smoke test)" if "smoke" in str(r.get("source", "")) else "")
    a = agg[k]; a[0] += 1; a[1] += r.get("requests", 0); a[2] += r.get("in_tokens", 0); a[3] += r.get("out_tokens", 0); a[4] += r.get("cost_usd", 0)
for k, a in agg.items():
    A(f"| {k} | {a[0]} | {a[1]:,} | {a[2]:,} | {a[3]:,} | {a[4]:.4f} |")
A(f"| **total** (cap $10, both judges) | | | | | **{sum(a[4] for a in agg.values()):.4f}** |")
A("")

A("### Stage 3 engine\n")
for g in sorted(glob.glob(f"{W}/results/stage3/*_gate.json")):
    j = json.load(open(g))
    A(f"- `{os.path.basename(g)}`: engine {json.dumps(j.get('engine'))}; logprobs mode `{j.get('logprobs_mode')}`; sampling `{j.get('sampling')}`; "
      f"bridge ids {j.get('bridge_ids')}; engine ready after {j.get('t_engine_ready', 0):.0f} s.")
for lg in sorted(glob.glob(f"{W}/logs/stage3_gpu*.log")):
    tail = [l.strip() for l in open(lg) if l.startswith(("gate:", "wrote", "repeat check", "stage3", "Traceback")) or "Error" in l][-6:]
    A(f"- `{os.path.basename(lg)}`: " + " / ".join(tail))
A("- Note: the repeat-check line in `stage3_gpu0.log` compares GPU 0's engine against GPU 1's **failed** second attempt, which at "
  "that time sat at `results/stage3/stage3_gpu1.jsonl` (now `results/stage3/failed/gpu1_attempt2.jsonl`). `stage3_gpu1.log` is the "
  "fresh-compile-cache run on GPU 1 whose output is used (also kept as `logs/stage3_diag_gpu1_freshcache.log`); "
  "`stage3_SBctx_on_gpu0_stopped.log` is the stopped recompute on GPU 0; `stage3_repeat.log` is the repeat check in a fresh engine "
  "(largest differences by scorer: parent rows ≤ 0.0043 nats, LoRA rows ≤ 0.1552 nats).")
A("")

A("### Timeline (UTC, `logs/run.log`)\n")
for l in open(f"{W}/logs/run.log"):
    A(f"- {l.strip()}")
A("")

A("### Code changes against E08 R07's harness (`notes/r07_orig/` = untouched copies of `/workspace/e08/r07/src` and `scripts`)\n")
A("Removed from `scripts/` (R07-only, not used here; still in `notes/r07_orig/scripts/`): `after_g1.sh`, `run_all.sh`, `run_or_judge.sh`, "
  "`run_judge_paced.py`, `api_pacer.py` (the teammate's OpenRouter judges, not part of this brief), `extract_personas.py`, `make_head.py`, "
  "`make_readme.py`, `report_extras.py`; `analyze_r07.py` was the starting point for `scripts/analyze_e10.py` (kept as "
  "`notes/analyze_r07_start.py.txt`).\n")
new = []
A("```diff")
for d in ("src", "scripts"):
    for f in sorted(os.listdir(f"{W}/{d}")):
        cur = f"{W}/{d}/{f}"
        if os.path.isdir(cur):
            continue
        orig = f"{W}/notes/r07_orig/{d}/{f}"
        if not os.path.exists(orig):
            new.append(f"{d}/{f}"); continue
        a, b = open(orig).read().splitlines(), open(cur).read().splitlines()
        if a == b:
            A(f"# {d}/{f}: identical to R07's")
            continue
        A(f"# {d}/{f}: changed")
        for l in difflib.unified_diff(a, b, f"r07/{d}/{f}", f"e10r01/{d}/{f}", lineterm="", n=1):
            A(l)
for d in ("src/eval_data",):
    for f in sorted(os.listdir(f"{W}/{d}")):
        same = open(f"{W}/{d}/{f}", "rb").read() == open(f"{W}/notes/r07_orig/{d}/{f}", "rb").read()
        A(f"# {d}/{f}: {'identical to R07' if same else 'CHANGED'}'s")
A("```\n")
A("New files (this run): " + ", ".join(f"`{x}`" for x in new) + ", `data/make_personas.py`, `data/personas.json`, `data/models/*.json`.\n")
open(f"{W}/results/details.md", "w").write("\n".join(L) + "\n")
print("details written")
