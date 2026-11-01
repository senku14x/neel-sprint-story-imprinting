"""Pre-flight: GET /api/v1/key (usage only, no key material printed) and one short GLM call."""
import json, os, time, requests
k = os.environ["OPENROUTER_API_KEY"]; H = {"Authorization": f"Bearer {k}"}
out = {"time_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
r = requests.get("https://openrouter.ai/api/v1/key", headers=H, timeout=60)
d = r.json().get("data", {}) if r.ok else {}
out["key"] = {"status": r.status_code, "usage": d.get("usage"), "limit": d.get("limit"), "limit_remaining": d.get("limit_remaining"), "is_free_tier": d.get("is_free_tier")}
PROVIDER = {"order": ["Cohere", "StreamLake", "Near AI", "DigitalOcean", "Together", "Fireworks", "Parasail", "Modal", "CoreWeave", "Makora"], "allow_fallbacks": True, "require_parameters": True, "ignore": ["Wafer", "Novita"]}
body = {"model": "z-ai/glm-5.3-flash-20260826", "messages": [{"role": "user", "content": 'Answer in JSON only: {"ok": true}'}],
        "max_tokens": 4000, "temperature": 0, "reasoning": {"effort": "low"}, "provider": PROVIDER, "usage": {"include": True}}
r = requests.post("https://openrouter.ai/api/v1/chat/completions", json=body, headers=H, timeout=300)
d = r.json() if r.ok else {"error": r.text[:300]}
out["call"] = {"status": r.status_code, "model": d.get("model"), "provider": d.get("provider"),
               "text": (d.get("choices") or [{}])[0].get("message", {}).get("content"), "usage": d.get("usage"), "error": d.get("error")}
print(json.dumps(out, indent=1))
json.dump(out, open("/workspace/e05/r04/logs/openrouter_ping.json", "w"), indent=1)
