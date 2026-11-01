"""Pre-flight: one short non-batch call to claude-haiku-5-5 with the key passed explicitly (no env var).
First tries temperature=0 (as the brief asks); records the API's answer; then the call without temperature."""
import json, os, sys, time
sys.path.insert(0, "/workspace/e05/r02/pydeps")
import anthropic
out = {"sdk_version": anthropic.__version__, "time_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
c = anthropic.Anthropic(api_key=os.environ["HAIKU_BATCH_KEY"])
msgs = [{"role": "user", "content": 'Answer in JSON only: {"ok": true}'}]
try:
    r = c.messages.create(model="claude-haiku-5-5", max_tokens=300, thinking={"type": "disabled"}, messages=msgs, extra_body={"temperature": 0})  # SDK 2.x has no temperature argument
    out["temp0"] = {"ok": True, "model": r.model, "usage": r.usage.model_dump()}
except anthropic.APIStatusError as e:
    out["temp0"] = {"ok": False, "status": e.status_code, "error": str(e.message)[:400]}
try:
    r = c.messages.create(model="claude-haiku-5-5", max_tokens=300, thinking={"type": "disabled"}, messages=msgs)
    u = r.usage
    out["no_temp"] = {"ok": True, "model": r.model, "id_prefix": r.id[:8], "stop": r.stop_reason,
                      "text": "".join(b.text for b in r.content if b.type == "text"),
                      "blocks": [b.type for b in r.content], "usage": u.model_dump(),
                      "cost_usd_standard": u.input_tokens * 0.10e-6 + u.output_tokens * 0.50e-6}
except anthropic.APIStatusError as e:
    out["no_temp"] = {"ok": False, "status": e.status_code, "error": str(e.message)[:400]}
print(json.dumps(out, indent=1))
json.dump(out, open("/workspace/e05/r02/logs/haiku_ping.json", "w"), indent=1)
