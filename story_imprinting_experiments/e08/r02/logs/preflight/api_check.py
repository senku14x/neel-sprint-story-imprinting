import json, os, sys, time
sys.path.insert(0, "/workspace/e05/r02/pydeps")
import anthropic, requests
out = {}
try:
    c = anthropic.Anthropic(api_key=os.environ["HAIKU_BATCH_KEY"], max_retries=3)
    m = c.messages.create(model="claude-haiku-5-5", max_tokens=10, thinking={"type": "disabled"},
                          messages=[{"role": "user", "content": "Reply with the single word ok."}])
    out["anthropic"] = dict(ok=True, model=m.model, text="".join(b.text for b in m.content if b.type == "text"),
                            in_tok=m.usage.input_tokens, out_tok=m.usage.output_tokens, sdk=anthropic.__version__)
    with open("/workspace/e08/r02/logs/haiku_ledger.jsonl", "a") as f:
        f.write(json.dumps(dict(t=time.time(), api="anthropic", model="claude-haiku-5-5", tag="preflight", id="preflight",
                                in_tok=m.usage.input_tokens, out_tok=m.usage.output_tokens,
                                cost_usd=m.usage.input_tokens*0.10e-6+m.usage.output_tokens*0.50e-6, mode="direct")) + "\n")
except Exception as e:
    out["anthropic"] = dict(ok=False, err=repr(e)[:300])
key = os.environ.get("OPENROUTER_API_KEY")
if key:
    try:
        r = requests.get("https://openrouter.ai/api/v1/key", headers={"Authorization": f"Bearer {key}"}, timeout=60)
        d = r.json().get("data", {})
        out["openrouter_key"] = dict(status=r.status_code, limit=d.get("limit"), usage=d.get("usage"))
        json.dump(dict(t=time.time(), limit=d.get("limit"), usage=d.get("usage")), open("/workspace/e08/r02/logs/openrouter_key_start.json", "w"))
        PROVIDER = {"order": ["Cohere", "StreamLake", "Near AI", "DigitalOcean", "Together", "Fireworks", "Parasail", "Modal",
                      "CoreWeave", "Makora"], "allow_fallbacks": True, "require_parameters": True, "ignore": ["Wafer", "Novita"]}
        body = {"model": "z-ai/glm-5.3-flash-20260826", "messages": [{"role": "user", "content": "Reply with the single word ok."}],
                "max_tokens": 4000, "temperature": 0, "reasoning": {"effort": "low"}, "provider": PROVIDER, "usage": {"include": True}}
        r = requests.post("https://openrouter.ai/api/v1/chat/completions", json=body, timeout=300, headers={"Authorization": f"Bearer {key}"})
        d = r.json()
        u = d.get("usage", {}) or {}
        out["openrouter_call"] = dict(status=r.status_code, model=d.get("model"), provider=d.get("provider"),
                                      text=(d.get("choices") or [{}])[0].get("message", {}).get("content"), cost=u.get("cost"))
        with open("/workspace/e08/r02/logs/openrouter_ledger.jsonl", "a") as f:
            f.write(json.dumps(dict(t=time.time(), id="preflight", status=r.status_code, model=d.get("model"), provider=d.get("provider"), cost=float(u.get("cost") or 0))) + "\n")
    except Exception as e:
        out["openrouter"] = dict(ok=False, err=repr(e)[:300])
print(json.dumps(out, indent=1))
