import json, urllib.request
key = None
for line in open("/workspace/.env"):
    if line.startswith("OPENROUTER_API_KEY_ALT="):
        key = line.split("=", 1)[1].strip().strip('"').strip("'")
req = urllib.request.Request("https://openrouter.ai/api/v1/key", headers={"Authorization": f"Bearer {key}"})
d = json.load(urllib.request.urlopen(req, timeout=30))["data"]
print(json.dumps(dict(limit=d.get("limit"), limit_remaining=d.get("limit_remaining"), usage=d.get("usage"))))
