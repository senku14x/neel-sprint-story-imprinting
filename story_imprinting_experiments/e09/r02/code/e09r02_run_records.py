"""E09 R02: notes/run_records.md (wall time per stage, spend, judge records) from the run's logs.

python e09r02_run_records.py
"""
import collections, json, os, re

W = "/workspace/e09/r02"


def jl(p):
    out = []
    if os.path.exists(p):
        for l in open(p):
            try:
                out.append(json.loads(l))
            except json.JSONDecodeError:
                pass
    return out


def grab(path, pat):
    if not os.path.exists(path):
        return None
    for l in open(path, errors="ignore"):
        m = re.search(pat, l)
        if m:
            return m.group(1)
    return None


def main():
    at = f"{W}/logs/after_train_Rshort.log"
    tr = f"{W}/logs/train_Rshort.log"
    gen = f"{W}/logs/gen_Rshort.log"
    ev = jl(f"{W}/logs/fwd_events.jsonl")
    evt = {e["event"]: e["t"] for e in ev if e.get("event") in ("inputs", "model_loaded", "stop_check", "partb_done", "all_done")}
    md = [e for e in ev if e.get("event") == "model_done"]
    L = ["\n## Wall time per stage (UTC)\n",
         "| Stage | GPU | Start | End | Notes |", "| --- | --- | --- | --- | --- |",
         "| Pre-flight | – | (deadline armed) | (STATUS pushed) | first STATUS push |",
         "| Stage 1a: prompt set | CPU | | | |",
         f"| Stage 1b: 8,000 default replies (vLLM worker) | 0 | (worker start) | {grab(f'{W}/logs/s1_worker.log', r'^exit 0 \S+T(\S+)Z')} | engine start ~4.5 min; 8,000 replies in 506 s |",
         "| Stage 1c/1d: rows, known-answer test, dry run | CPU | | | |",
         f"| Stage 2: train `Rshort` | 0 | {grab(tr, r'^start \S+T(\S+)Z')} | {grab(tr, r'^exit 0 \S+T(\S+)Z')} | 250 steps, ~22 s/step after a 191 s first step |",
         f"| Remap for vLLM | 0 | {grab(at, r'^training Rshort finished \S+T(\S+)Z')} | {grab(at, r'^stage3 start \S+T(\S+)Z')} | |",
         f"| Stage 3: Rshort 2,150 + R known-answer 600 replies | 0 | {grab(at, r'^stage3 start \S+T(\S+)Z')} | {grab(at, r'^stage3 exit 0 \S+T(\S+)Z')} | engine ready {grab(gen, r'^engine ready (\S+)')} |",
         f"| Stage 4: HF forward passes (states Part 1 parent + Rshort, Part B, Part 2) | 0 | {grab(at, r'^stage4 start \S+T(\S+)Z')} | {grab(at, r'^fwd exit 0 \S+T(\S+)Z')} | "
         + "; ".join(f"Part {e['part']} {e.get('model')} {e.get('secs')} s" for e in md)
         + "".join(f"; Part B {e.get('secs')} s" for e in ev if e.get("event") == "partb_done") + " |",
         f"| Stage 4b: health.py (parent + Rshort) | 0 | {grab(at, r'^fwd exit 0 \S+T(\S+)Z')} | {grab(at, r'^health exit 0 \S+T(\S+)Z')} | |",
         f"| Analysis and report | CPU | {grab(f'{W}/logs/reports.log', r'^start (\S+)')} | see final push | |"]
    led = jl(f"{W}/logs/haiku_ledger.jsonl")
    tin = sum(r["in_tokens"] for r in led); tout = sum(r["out_tokens"] for r in led)
    cost = sum(r["cost_usd"] for r in led)
    J = jl(f"{W}/judgments/haiku.jsonl")
    models = collections.Counter(j["model"] for j in J if j.get("model"))
    fails = collections.Counter(j["parse_error"] for j in J if not j["parse_ok"])
    L += ["\n## Spend and judge records\n",
          f"- Anthropic (Haiku 5.5 via Message Batches, 50% batch price of $0.10 / $0.50 per MTok): {len(led)} batches, "
          f"{sum(r['requests'] for r in led):,} requests, {tin:,} input and {tout:,} output tokens, **${cost:.2f}** by the ledger "
          f"(`logs/haiku_ledger.jsonl`; cap $2). Plus one pre-flight non-batch call (15 input, 4 output tokens). First batch "
          f"created {min((r['created'] for r in led), default='–')}, last collected {max((r['ended'] for r in led), default='–')}.",
          f"- Judge model ID as returned: {dict(models)}.",
          f"- Judge parse failures (per attempt, R04's parse rule, up to 4 attempts): {dict(fails)}; replies left without a "
          "judgment and replies with the null-persona fallback: see §9 (Stage 3 checks).",
          "- No OpenRouter or HF calls."]
    open(f"{W}/notes/run_records.md", "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
