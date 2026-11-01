import os, sys, json, time
sys.path.insert(0, "/workspace/e05/r02/pydeps")
import anthropic
c = anthropic.Anthropic(api_key=os.environ["HAIKU_BATCH_KEY"])
m = c.messages.create(model="claude-haiku-5-5", max_tokens=10, thinking={"type": "disabled"},
                      messages=[{"role": "user", "content": "Reply with the single word ok."}])
txt = "".join(b.text for b in m.content if b.type == "text")
cost = m.usage.input_tokens * 0.10e-6 + m.usage.output_tokens * 0.50e-6
os.makedirs("/workspace/e08/r05/logs", exist_ok=True)
open("/workspace/e08/r05/logs/haiku_ledger.jsonl", "a").write(json.dumps(dict(batch_id=None, kind="preflight", source="preflight", requests=1, in_tokens=m.usage.input_tokens, out_tokens=m.usage.output_tokens, cost_usd=cost, t=time.time())) + "\n")
print("reply:", repr(txt), "model:", m.model, "sdk:", anthropic.__version__, "python:", sys.version.split()[0])
