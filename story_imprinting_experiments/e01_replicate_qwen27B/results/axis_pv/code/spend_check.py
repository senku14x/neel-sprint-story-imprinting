"""Read OpenRouter key usage (free endpoint), log it with a stage tag, exit 1 if past the axis_pv cap ($34.386 start + $15 - $0.50 guard)."""
import json, os, sys, time, httpx
START, CAP = 34.385961417, 48.886
stage = sys.argv[1] if len(sys.argv) > 1 else "check"
r = httpx.get("https://openrouter.ai/api/v1/key", timeout=30, headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"})
u = float(r.json()["data"]["usage"])
with open("/workspace/si36/axis_pv/logs/spend_checks.jsonl", "a") as f:
    f.write(json.dumps(dict(t=time.strftime("%H:%M:%S", time.gmtime()), stage=stage, usage=u, run_spend=round(u - START, 4))) + "\n")
print(f"usage {u:.4f} run_spend {u - START:.4f} cap {CAP}")
sys.exit(1 if u > CAP else 0)
