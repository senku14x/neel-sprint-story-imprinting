"""E2 (31 Oct): build a small parity reference for the rented 4xH100 node.
(a) the sw009 parity request (E2a|bc|DL|trig|backyard_bbq_bash_05): token ids + extract1028 vLLM span_mean ref + box 1's HF hdr mean;
(b) 2 sw008 contexts x {self-hostile, user-hostile} per model (parent, hdA0, hdB0): token ids rebuilt with cap9_x.contexts()
    + the saved sw009 header states [7, 64, 5120] fp16 from /workspace/runs_executor/sw009_captures/<model>.pt."""
import glob, json, sys
import torch
torch.set_num_threads(8)
sys.path.insert(0, "/workspace/Neel Sprint/experiments/sprint_work/009_hostile_user_and_self_attribution/src")
import cap9_x as C
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained("/dev/shm/qwen36_27b")
out = {}
par = json.load(open("/workspace/runs_executor/sw009_captures/parity.json"))
req = json.loads(open("/workspace/runs_executor/extract1028/requests/E2a_parent.jsonl").readline())
assert req["key"] == par["key"]
E2 = torch.load(sorted(glob.glob("/workspace/runs_executor/extract1028/E2/a/parent/chunk_*.pt"))[0], mmap=True)
j = E2["keys"].index(req["key"])
out["parity"] = dict(key=req["key"], ids=req.get("ids") or req.get("prompt_token_ids"), vllm_span_mean=E2["span_mean"][j, 0].float().clone(),
                     box1_hf_hdr_mean=torch.load("/workspace/runs_executor/overnight_2026-10-30/setup/box1_hf_hdrmean.pt")["hdr_mean"].float(),
                     ref_parity=par)
rows = {r["key"]: r for r in C.contexts(tok)}
want = [k for k in rows if k.startswith("sw008|self-hostile|")][:2] + [k for k in rows if k.startswith("sw008|user-hostile|")][:2]
out["ctx"] = {}
for m in ("parent", "hdA0", "hdB0"):
    D = torch.load(f"/workspace/runs_executor/sw009_captures/{m}.pt", mmap=True)
    for k in want:
        i = D["keys"].index(k); assert D["n_tok"][i] == len(rows[k]["ids"]), (m, k)
        out["ctx"][f"{m}|{k}"] = dict(model=m, key=k, ids=rows[k]["ids"], hdr=D["hdr"][i].clone())
torch.save(out, "/workspace/runs_executor/day_2026-10-31_E2/setup/parity_ref_node.pt")
print("OK", want, {k: v["hdr"].shape for k, v in list(out["ctx"].items())[:1]})
