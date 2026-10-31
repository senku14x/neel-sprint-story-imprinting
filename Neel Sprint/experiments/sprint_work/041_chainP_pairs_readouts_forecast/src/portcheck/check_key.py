"""Prints limit_remaining / usage of OPENROUTER_API_KEY_ALT (never the key). Exit 3 if limit_remaining < 40."""
import json, sys, urllib.request
k = None
for line in open("/workspace/.env"):
    if line.startswith("OPENROUTER_API_KEY_ALT="):
        k = line.split("=", 1)[1].strip().strip('"').strip("'")
assert k
req = urllib.request.Request("https://openrouter.ai/api/v1/key", headers={"Authorization": f"Bearer {k}"})
d = json.loads(urllib.request.urlopen(req, timeout=30).read())["data"]
print(json.dumps({x: d.get(x) for x in ("limit", "limit_remaining", "usage", "usage_daily")}))
rem = d.get("limit_remaining")
sys.exit(3 if (rem is not None and rem < 40) else 0)
