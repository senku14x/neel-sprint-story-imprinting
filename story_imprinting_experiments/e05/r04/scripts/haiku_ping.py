"""Pre-flight: one short non-batch call to claude-haiku-5-5, key passed explicitly, thinking off, no temperature."""
import json, os, sys, time
sys.path.insert(0, "/workspace/e05/r02/pydeps")
import anthropic
out = {"sdk_version": anthropic.__version__, "time_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
c = anthropic.Anthropic(api_key=os.environ["HAIKU_BATCH_KEY"])
try:
    r = c.messages.create(model="claude-haiku-5-5", max_tokens=300, thinking={"type": "disabled"},
                          messages=[{"role": "user", "content": 'Answer in JSON only: {"ok": true}'}])
    u = r.usage
    out["call"] = {"ok": True, "model": r.model, "stop": r.stop_reason, "text": "".join(b.text for b in r.content if b.type == "text"),
                   "usage": u.model_dump(), "cost_usd_standard": u.input_tokens * 0.10e-6 + u.output_tokens * 0.50e-6}
except anthropic.APIStatusError as e:
    out["call"] = {"ok": False, "status": e.status_code, "error": str(e.message)[:400]}
print(json.dumps(out, indent=1))
json.dump(out, open("/workspace/e05/r04/logs/haiku_ping.json", "w"), indent=1)
