import json, urllib.request
k = None
for l in open("/workspace/.env"):
    if l.startswith("OPENROUTER_API_KEY_ALT="):
        k = l.split("=", 1)[1].strip().strip('"').strip("'")
req = urllib.request.Request("https://openrouter.ai/api/v1/key", headers={"Authorization": f"Bearer {k}"})
d = json.load(urllib.request.urlopen(req, timeout=30))["data"]
print(json.dumps({x: d.get(x) for x in ("limit", "limit_remaining", "usage")}))
