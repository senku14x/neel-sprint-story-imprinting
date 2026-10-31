"""Print limit_remaining / usage of OPENROUTER_API_KEY_ALT (never prints the key). Exit 3 if limit_remaining < --floor."""
import argparse, json, sys, urllib.request
ap = argparse.ArgumentParser(); ap.add_argument("--floor", type=float, default=42.0); a = ap.parse_args()
key = None
for line in open("/workspace/.env"):
    if line.startswith("OPENROUTER_API_KEY_ALT="):
        key = line.split("=", 1)[1].strip().strip('"').strip("'")
assert key, "OPENROUTER_API_KEY_ALT missing"
req = urllib.request.Request("https://openrouter.ai/api/v1/key", headers={"Authorization": f"Bearer {key}"})
d = json.load(urllib.request.urlopen(req, timeout=30)).get("data", {})
rem = d.get("limit_remaining")
print(json.dumps(dict(limit=d.get("limit"), limit_remaining=rem, usage=d.get("usage"))))
sys.exit(3 if rem is not None and rem < a.floor else 0)
