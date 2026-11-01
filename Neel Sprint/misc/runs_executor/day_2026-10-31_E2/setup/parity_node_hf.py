"""E2 (31 Oct): HF parity on the rented 4xH100 node (gate before any swap job). Same HF path as sw009 cap9_x.py / E1's
setup_smoke_hf.py: bf16, forward hooks on model.model.layers[L] outputs (pre-final-norm), unmerged PEFT adapters.
(1) parent, sw009 parity request: mean of the 7 header tokens vs extract1028's vLLM span_mean (the parity.json comparison) and vs
    box 1's HF capture of the same request (HF vs HF).
(2) parent / hdA0 / hdB0 on 4 sw008 contexts: the 7 header-token states vs sw009_captures (box 1, H200).
Gates (written before running):
  G1 parent vs vLLM ref: max_rel <= 1.10 x parity.json max_rel and median_rel <= 1.10 x parity.json median_rel (boxes 1-3, C used this);
  G2 parent HF vs box 1 HF: max_rel <= 0.03 (E1's box C gate);
  G3 every model x context: per-(context, layer) median over header tokens 1-6 of rel diff <= 0.06 (sw021 D29's calibrated gate;
     token 0 dropped at L >= 36, bf16 caveat), at every layer;
  G4 adapter active and the right one: for hdA0 / hdB0, at L 24-63 the node state is >= 3x closer to that model's box-1 state than
     to the parent's box-1 state and than to the other organism's (median over contexts, tokens 1-6).
  python parity_node_hf.py <out_json>"""
import json, sys, time
import torch
torch.set_grad_enabled(False); torch.set_num_threads(8)
sys.path.insert(0, "/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/src")
sys.path.insert(0, "/workspace/runs_executor/extract1028/src")
from hooks018 import text_model
import common_x as X
from transformers import AutoModelForCausalLM
from peft import PeftModel
out_json = sys.argv[1]
R = torch.load("/workspace/runs_executor/day_2026-10-31_E2/setup/parity_ref_node.pt")
t0 = time.time()
model = AutoModelForCausalLM.from_pretrained(X.BASE, dtype=torch.bfloat16, device_map="cuda")
model = PeftModel.from_pretrained(model, X.LORA_SRC["hdA0"], adapter_name="hdA0")
model.load_adapter(X.LORA_SRC["hdB0"], adapter_name="hdB0"); model.eval()
t_load = time.time() - t0
tm = text_model(model); cap = {}
hs = [tm.layers[L].register_forward_hook((lambda L: lambda m, i, o: cap.__setitem__(L, (o[0] if isinstance(o, tuple) else o)[0].detach()))(L)) for L in range(64)]

def run(ids, m):
    cap.clear()
    if m == "parent":
        with model.disable_adapter():
            model(input_ids=torch.tensor([ids], device="cuda"), logits_to_keep=1)
    else:
        model.set_adapter(m); model(input_ids=torch.tensor([ids], device="cuda"), logits_to_keep=1)
    return torch.stack([cap[L][-7:].float() for L in range(64)], 1).cpu()  # [7, 64, H]

res = dict(load_s=round(t_load, 1))
P = R["parity"]
h = run(P["ids"], "parent"); hm = h.mean(0)
rel = lambda a, b: (a - b).norm(dim=-1) / b.norm(dim=-1)
r1 = rel(hm, P["vllm_span_mean"]); r2 = rel(hm, P["box1_hf_hdr_mean"])
res["G1"] = dict(max_rel=float(r1.max()), median_rel=float(r1.median()), ref=P["ref_parity"],
                 pass_=bool(r1.max() <= 1.10 * P["ref_parity"]["max_rel"] and r1.median() <= 1.10 * P["ref_parity"]["median_rel"]))
res["G2"] = dict(max_rel=float(r2.max()), median_rel=float(r2.median()), at_L16_32_48_63=[float(r2[L]) for L in (16, 32, 48, 63)], pass_=bool(r2.max() <= 0.03))
node = {}
for k, c in R["ctx"].items():
    node[k] = run(c["ids"], c["model"])
g3 = {}
for k, c in R["ctx"].items():
    d = rel(node[k], c["hdr"].float())  # [7, 64]
    d[0, 36:] = float("nan")
    med = d[1:].median(0).values  # tokens 1-6 per layer
    g3[k] = dict(max_layer_median=float(med.max()), median=float(med.median()), tok0_max_L_lt36=float(d[0, :36].max()))
res["G3"] = dict(per_ctx=g3, pass_=bool(max(v["max_layer_median"] for v in g3.values()) <= 0.06))
g4 = {}
for m in ("hdA0", "hdB0"):
    o = "hdB0" if m == "hdA0" else "hdA0"
    ratios = []
    for k, c in R["ctx"].items():
        if c["model"] != m:
            continue
        key = c["key"]; x = node[k][1:, 24:]
        own = (x - c["hdr"][1:, 24:].float()).norm(dim=-1).median()
        par = (x - R["ctx"][f"parent|{key}"]["hdr"][1:, 24:].float()).norm(dim=-1).median()
        oth = (x - R["ctx"][f"{o}|{key}"]["hdr"][1:, 24:].float()).norm(dim=-1).median()
        ratios.append(dict(key=key, own=float(own), to_parent=float(par), to_other=float(oth), min_ratio=float(min(par, oth) / own)))
    g4[m] = ratios
res["G4"] = dict(per_model=g4, pass_=bool(all(r["min_ratio"] >= 3 for v in g4.values() for r in v)))
res["pass"] = all(res[g]["pass_"] for g in ("G1", "G2", "G3", "G4"))
json.dump(res, open(out_json, "w"), indent=1)
print("HF_PARITY", json.dumps({g: res[g]["pass_"] for g in ("G1", "G2", "G3", "G4")}), "PASS" if res["pass"] else "FAIL", flush=True)
sys.exit(0 if res["pass"] else 2)
