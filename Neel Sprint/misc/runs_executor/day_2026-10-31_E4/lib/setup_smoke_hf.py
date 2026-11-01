"""Setup smoke, part 1 (executor-9, 30 Oct): one HF capture on the parent, reproducing sw009 cap9_x.py's parity check exactly.
Same request (first line of extract1028 requests/E2a_parent.jsonl = key E2a|bc|DL|trig|backyard_bbq_bash_05, read from the
/workspace mirror, byte-identical to box 1's /root copy), same reference (extract1028 E2/a/parent chunk_0000 span_mean[j, 0],
vLLM + vllm-lens), same HF path (bf16, forward hooks on model.model.layers[L] outputs, pre-final-norm, mean of the last 7
header tokens). Gate: max_rel <= 1.10 x parity.json max_rel and median_rel <= 1.10 x parity.json median_rel (the known
HF-vs-vLLM engine difference measured on box 1; a broken setup - wrong weights, layer or tokens - is far above it).
Saves the HF header mean [64, 5120] fp32 so boxes can be compared HF-vs-HF.
  python setup_smoke_hf.py <box> <out_json> <out_pt>"""
import glob, json, sys, time
import torch

box, out_json, out_pt = sys.argv[1:4]
torch.set_grad_enabled(False); torch.set_num_threads(8)
sys.path.insert(0, "/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/src")
from hooks018 import text_model  # noqa: E402
from transformers import AutoModelForCausalLM  # noqa: E402
BASE = "/dev/shm/qwen36_27b"
par = json.load(open("/workspace/runs_executor/sw009_captures/parity.json"))
req = json.loads(open("/workspace/runs_executor/extract1028/requests/E2a_parent.jsonl").readline())
assert req["key"] == par["key"], (req["key"], par["key"])
E2 = torch.load(sorted(glob.glob("/workspace/runs_executor/extract1028/E2/a/parent/chunk_*.pt"))[0])
j = E2["keys"].index(req["key"]); ids = req.get("ids") or req.get("prompt_token_ids")
t0 = time.time()
model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map="cuda"); model.eval()
t_load = time.time() - t0
tm = text_model(model); cap = {}
hs = [tm.layers[L].register_forward_hook((lambda L: lambda m, i, o: cap.__setitem__(L, (o[0] if isinstance(o, tuple) else o)[0].detach()))(L)) for L in range(64)]
model(input_ids=torch.tensor([ids], device="cuda"), logits_to_keep=1)
hm = torch.stack([cap[L][-7:].float().mean(0) for L in range(64)]).cpu()
ref = E2["span_mean"][j, 0].float()
rel = (hm - ref).norm(dim=-1) / ref.norm(dim=-1)
assert torch.isfinite(hm).all()
res = dict(box=box, key=req["key"], n_tok=len(ids), load_s=round(t_load, 1), max_rel=float(rel.max()), median_rel=float(rel.median()),
           rel_L16_32_48_63=[float(rel[L]) for L in (16, 32, 48, 63)],
           ref_parity=dict(max_rel=par["max_rel"], median_rel=par["median_rel"], rel_L16_32_48_63=par["rel_L16_32_48_63"]),
           delta_vs_parity_max=float(rel.max()) - par["max_rel"], delta_vs_parity_median=float(rel.median()) - par["median_rel"],
           gate="max_rel <= 1.10*parity.max_rel and median_rel <= 1.10*parity.median_rel")
res["pass"] = bool(res["max_rel"] <= 1.10 * par["max_rel"] and res["median_rel"] <= 1.10 * par["median_rel"])
torch.save(dict(key=req["key"], hdr_mean=hm, box=box), out_pt)
json.dump(res, open(out_json, "w"), indent=1)
print("HF_SMOKE", json.dumps(res), flush=True)
sys.exit(0 if res["pass"] else 2)
