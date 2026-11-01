"""Settings probe (synchronous Messages API, standard price): is temperature 0.7 accepted on claude-haiku-5-5,
and is thinking {type: disabled} accepted? Tiny prompt, max_tokens 16. Logs status and error text only."""
import json, sys, time
sys.path.insert(0, "/workspace/e03/stage1/scripts")
import anthropic
from api_common import HAIKU_MODEL, client, cost, ledger

c = client()
out = []
cases = [
    ("temp0.7_thinking_disabled_default_version", dict(extra_body={"temperature": 0.7}), None),
    ("temp0.7_thinking_disabled_version_2023-06-01", dict(extra_body={"temperature": 0.7}), {"anthropic-version": "2023-06-01"}),
    ("no_temp_thinking_disabled_default_version", {}, None),
]
for name, extra, headers in cases:
    t0 = time.time()
    rec = {"case": name}
    try:
        kw = dict(model=HAIKU_MODEL, max_tokens=16, thinking={"type": "disabled"},
                  messages=[{"role": "user", "content": "Reply with the single word OK."}], **extra)
        if headers:
            kw["extra_headers"] = headers
        r = c.messages.with_raw_response.create(**kw)
        m = r.parse()
        u = m.usage.model_dump()
        rec.update(status=200, stop_reason=m.stop_reason, text=[b.text for b in m.content if b.type == "text"],
                   block_types=[b.type for b in m.content], usage=u, api_version_sent=(headers or {}).get("anthropic-version", "sdk default"),
                   request_id=r.headers.get("request-id"))
        ledger(api="anthropic", run="probe", case=name, status=200, model=HAIKU_MODEL, usage=u, cost=cost(u, batch=False))
    except anthropic.APIStatusError as e:
        rec.update(status=e.status_code, error=str(e.message)[:400])
        ledger(api="anthropic", run="probe", case=name, status=e.status_code, model=HAIKU_MODEL, error=str(e.message)[:400], cost=0.0)
    rec["latency_s"] = round(time.time() - t0, 2)
    out.append(rec)
    print(json.dumps(rec))
# Which anthropic-version does the SDK send by default?
import anthropic._constants as k
print("sdk", anthropic.__version__)
json.dump(out, open("/workspace/e03/stage1/results/haiku_settings_probe.json", "w"), indent=1)
