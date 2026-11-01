"""Paraphrase sample stories with one paraphraser (same prompt for all, temperature 0.7, max 2,500 tokens).

  python paraphrase.py --who gemini [--sids A0157,B0346] [--out results/paraphrases] [--concurrency 16]

Writes <out>/<who>.jsonl (one line per story, failed stories included with ok=false) and
<out>/<who>_run.json (settings, throughput, tokens, cost, every 429/error, concurrency trace).
"""
import argparse
import asyncio
import json
import os
import re
import time
from pathlib import Path

from common import (E03, MAX_TOKENS, PARAPHRASE_PROMPT, PARAPHRASERS, TEMPERATURE, BudgetExceeded, Caller,
                    load_sample)

ap = argparse.ArgumentParser()
ap.add_argument("--who", required=True, choices=list(PARAPHRASERS))
ap.add_argument("--sids", default="")
ap.add_argument("--out", default=str(E03 / "results/paraphrases"))
ap.add_argument("--concurrency", type=int, default=16)
ap.add_argument("--rpm", type=float, default=None, help="pace request starts (OpenRouter new accounts: 20/min/model)")
ap.add_argument("--resume", action="store_true", help="keep ok stories already in <out>/<who>.jsonl; run only the rest")
ap.add_argument("--tag", default="", help="suffix for the run summary file")
args = ap.parse_args()

cfg = PARAPHRASERS[args.who]
sample = load_sample()
if args.sids:
    keep = args.sids.split(",")
    sample = [s for s in sample if s["sid"] in keep]
out = Path(args.out)
out.mkdir(parents=True, exist_ok=True)
order = [s["sid"] for s in sample]
kept = {}
if args.resume and (out / f"{args.who}.jsonl").exists():
    for l in open(out / f"{args.who}.jsonl"):
        r = json.loads(l)
        if r["ok"]:
            kept[r["sid"]] = r
    sample = [s for s in sample if s["sid"] not in kept]
print(f"kept {len(kept)} ok stories from earlier run(s); running {len(sample)}")

PREFACE = re.compile(r"^\s*(here(’|'| i)s|sure|certainly|of course|okay|title\s*:|#|\*\*)", re.I)
TAGS = re.compile(r"</?(think|story)>", re.I)


def body_for(story: str) -> dict:
    b = {"model": cfg["model"], "messages": [{"role": "user", "content": PARAPHRASE_PROMPT.replace("{STORY}", story)}],
         "temperature": TEMPERATURE, "max_tokens": MAX_TOKENS}
    b.update(cfg["extra"])
    if cfg["base"].startswith("https://openrouter"):
        b["usage"] = {"include": True}
    return b


async def main():
    key = os.environ["OPENROUTER_API_KEY"] if cfg["base"].startswith("https://openrouter") else None
    caller = Caller(cfg["base"], concurrency=args.concurrency, run=f"paraphrase:{args.who}", key=key, rpm=args.rpm)
    t0 = time.time()

    async def one(s):
        r = await caller.chat(body_for(s["story"]), tag=s["sid"])
        rec = {k: s[k] for k in ["sid", "file", "row", "type", "habit_role", "habit_animal"]}
        rec.update({"paraphraser": args.who, "model": cfg["model"], "run_tag": args.tag or "1", "ok": r["ok"],
                    "n_attempts": len(r["attempts"]), "n_429": sum(a["status"] == 429 for a in r["attempts"]),
                    "attempt_errors": [a["error"] for a in r["attempts"] if a["error"]]})
        if r["ok"]:
            d = r["data"]
            ch = d["choices"][0]
            msg = ch["message"]
            text = (msg.get("content") or "").strip()
            u = d.get("usage") or {}
            rec.update({"text": text, "finish": ch.get("finish_reason"), "served_model": d.get("model"),
                        "provider": d.get("provider"), "in": u.get("prompt_tokens"), "out": u.get("completion_tokens"),
                        "reasoning_tokens": (u.get("completion_tokens_details") or {}).get("reasoning_tokens"),
                        "cost": float(u.get("cost") or 0),
                        "reasoning_returned_chars": len(msg.get("reasoning") or msg.get("reasoning_content") or ""),
                        "flag_preface": bool(PREFACE.match(text)), "flag_tags": bool(TAGS.search(text)),
                        "latency_s": r["attempts"][-1]["latency_s"]})
        else:
            rec.update({"text": None, "error": r["error"]})
        return rec

    try:
        recs = await asyncio.gather(*[one(s) for s in sample])
    except BudgetExceeded as e:
        print("STOP:", e)
        raise
    finally:
        await caller.close()
    t1 = time.time()
    merged = {**kept, **{r["sid"]: r for r in recs}}
    with open(out / f"{args.who}.jsonl", "w") as f:
        for sid in order:
            if sid in merged:
                f.write(json.dumps(merged[sid], ensure_ascii=False) + "\n")
    ok = [r for r in recs if r["ok"]]
    n_calls = sum(r["n_attempts"] for r in recs)
    summary = {"who": args.who, "model": cfg["model"], "settings": {"temperature": TEMPERATURE, "max_tokens": MAX_TOKENS,
               **cfg["extra"]}, "n_stories": len(recs), "n_ok": len(ok), "failed": [r["sid"] for r in recs if not r["ok"]],
               "n_http_calls": n_calls, "wall_s": round(t1 - t0, 1),
               "requests_per_min_ok": round(len(ok) / ((t1 - t0) / 60), 2),
               "calls_per_min": round(n_calls / ((t1 - t0) / 60), 2),
               "concurrency_start": args.concurrency, "concurrency_trace": caller.limit_trace,
               "tokens_in": sum(r.get("in") or 0 for r in ok), "tokens_out": sum(r.get("out") or 0 for r in ok),
               "reasoning_tokens": sum(r.get("reasoning_tokens") or 0 for r in ok),
               "cost_usd": sum(r.get("cost") or 0 for r in ok),
               "cost_usd_all_attempts": None,
               "finish_counts": {k: sum(1 for r in ok if r["finish"] == k) for k in {r["finish"] for r in ok}},
               "n_429": sum(1 for e in caller.events if e["status"] == 429), "events": caller.events,
               "served_models": sorted({str(r.get("served_model")) for r in ok}),
               "providers": {p: sum(1 for r in ok if r.get("provider") == p) for p in {r.get("provider") for r in ok}},
               "flag_preface": [r["sid"] for r in ok if r["flag_preface"]], "flag_tags": [r["sid"] for r in ok if r["flag_tags"]]}
    # cost of every attempt, failed ones included, from the ledger
    from common import LEDGER
    run = f"paraphrase:{args.who}"
    summary["cost_usd_all_attempts"] = sum(float(json.loads(l).get("cost") or 0) for l in open(LEDGER)
                                           if json.loads(l)["run"] == run and json.loads(l)["t"] >= t0 - 1)
    summary["rpm_pacing"] = args.rpm
    summary["kept_from_earlier"] = sorted(kept)
    json.dump(summary, open(out / f"{args.who}_run{args.tag}.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in summary.items() if k != "events"}, indent=1))
    print("events:", len(caller.events))


asyncio.run(main())
