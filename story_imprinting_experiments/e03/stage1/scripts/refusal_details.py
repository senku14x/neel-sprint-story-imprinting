"""List stop_details for refusal results of a batch (read-only re-download of results; no new requests)."""
import json, sys
sys.path.insert(0, "/workspace/e03/stage1/scripts")
from api_common import S1, client
tag = sys.argv[1]
bid = json.load(open(S1 / f"results/{tag}.json"))["batch_id"]
out = []
for res in client().messages.batches.results(bid):
    if res.result.type == "succeeded" and res.result.message.stop_reason == "refusal":
        m = res.result.message
        sd = getattr(m, "stop_details", None)
        out.append({"row": int(res.custom_id), "stop_details": sd.model_dump() if hasattr(sd, "model_dump") else sd,
                    "text_chars": sum(len(b.text) for b in m.content if b.type == "text"), "output_tokens": m.usage.output_tokens})
json.dump(out, open(S1 / f"results/refusals_{tag}.json", "w"), indent=1)
from collections import Counter
print(len(out), Counter(str((o["stop_details"] or {}).get("category")) for o in out))
print(Counter("empty" if o["text_chars"] == 0 else "partial" for o in out))
