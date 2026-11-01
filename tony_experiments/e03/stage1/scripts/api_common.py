"""Shared settings for E03 stage 1 API calls. The Anthropic key is read from HAIKU_BATCH_KEY only and passed
explicitly to the SDK; it is never printed or written. Every call is appended to logs/api_ledger.jsonl."""
import json, os, time
from pathlib import Path

S1 = Path("/workspace/e03/stage1")
LEDGER = S1 / "logs/api_ledger.jsonl"
HAIKU_MODEL = "claude-haiku-5-5"
MAX_TOKENS = 2500
# Anthropic list prices for claude-haiku-5-5 (prompt <= 100K tokens): $0.10 / $0.50 per MTok; Message Batches = 50%.
PRICE_IN, PRICE_OUT = 0.10e-6, 0.50e-6
BATCH_DISCOUNT = 0.5
ANTHROPIC_CAP_USD = 5.0

PARAPHRASE_PROMPT = open(S1 / "scripts/paraphrase_prompt.txt").read()


def client():
    import anthropic
    return anthropic.Anthropic(api_key=os.environ["HAIKU_BATCH_KEY"])


def ledger(**kw):
    kw.setdefault("t", time.time())
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with open(LEDGER, "a") as f:
        f.write(json.dumps(kw) + "\n")


def cost(usage, batch=True):
    if not usage:
        return 0.0
    i = (usage.get("input_tokens") or 0) + (usage.get("cache_creation_input_tokens") or 0) + (usage.get("cache_read_input_tokens") or 0)
    o = usage.get("output_tokens") or 0
    return (i * PRICE_IN + o * PRICE_OUT) * (BATCH_DISCOUNT if batch else 1.0)


def anthropic_spend():
    if not LEDGER.exists():
        return 0.0
    return sum(float(json.loads(l).get("cost") or 0) for l in open(LEDGER) if json.loads(l).get("api") == "anthropic")
