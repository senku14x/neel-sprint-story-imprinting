"""Append the OpenRouter key's usage (dollars) to logs/openrouter_key_usage.jsonl. The key is read from the environment, never printed."""
import json, os, sys, time
import httpx
r = httpx.get("https://openrouter.ai/api/v1/key", headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"}, timeout=30)
d = r.json().get("data", {})
rec = {"when": sys.argv[1] if len(sys.argv) > 1 else "loop", "usage": d.get("usage"), "t_utc": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())}
open("/workspace/e04/r04/logs/openrouter_key_usage.jsonl", "a").write(json.dumps(rec) + "\n")
print(rec)
