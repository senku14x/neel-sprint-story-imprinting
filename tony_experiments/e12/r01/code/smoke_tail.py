"""E12 R01 smoke tail: SAE encode/decode on 1,000 parent web tokens + throughput (sections 3 and 5 of smoke.py)."""
import json, sys, time, os
sys.path.insert(0, "/workspace/e12/r01/code")
from e12gpu import *  # noqa
import torch
open_log("smoke")
OUT = f"{R}/smoke"
rep = json.load(open(f"{OUT}/smoke_head.json"))
E = Engine(); rd = E.rd; CT = cont_tokens(rd)
SC = base_scripts()
W = json.load(open(f"{R}/data/web_windows.json"))["windows"]
seq = W[0][:1000]
with E.use("parent"):
    st = E.states([seq], [list(range(1, 1000))], [42])[0][42].cuda()
p = torch.load(f"{R}/sae/saes_Qwen_Qwen3.6-27B_batch_top_k/resid_post_layer_42/trainer_0/ae.pt", map_location="cuda")
km = {"encoder.weight": "W_enc", "decoder.weight": "W_dec", "encoder.bias": "b_enc", "bias": "b_dec", "b_dec": "b_dec"}
rr = {km[k]: v for k, v in p.items() if k in km}
W_enc, W_dec = rr["W_enc"].T.contiguous().float(), rr["W_dec"].T.contiguous().float()
b_enc, b_dec = rr["b_enc"].float(), rr["b_dec"].float()
thr = float(p["threshold"])
pre = torch.relu((st - b_dec) @ W_enc + b_enc)
fa = pre * (pre > thr)
tk = torch.topk(pre, 64, dim=-1)
fb_ = torch.zeros_like(pre).scatter_(-1, tk.indices, tk.values)
ev = {}
for nm, f in (("thresholded", fa), ("top64", fb_)):
    xh = f @ W_dec + b_dec
    ev[nm] = dict(EV=float(1 - ((st - xh) ** 2).sum() / ((st - st.mean(0)) ** 2).sum()), L0=float((f > 0).sum(-1).float().mean()))
rep["sae_smoke"] = dict(thr=thr, k=int(p["k"]), n_tokens=st.shape[0], dec_row_norm_mean=float(W_dec.norm(dim=-1).mean()), **ev)
log(event="sae_smoke", **rep["sae_smoke"])
del p, W_enc, W_dec, pre, fa, fb_
torch.cuda.empty_cache()
C = load_convs(models=["V"])
cs = sorted([c for c in C if c["model"] == "V" and c["persona"] == "default" and c["trigger"]], key=lambda c: c["key"])[:32]
its = [rd.context(own_text(c), SC[c["script_id"]], True) for c in cs]
with E.use("V"):
    E.oc(its[:4], CT)  # warm up
torch.cuda.synchronize(); t = time.time()
with E.use("V"):
    _, n = E.oc(its, CT, blocks=(42,), lora=True)
torch.cuda.synchronize(); dt = time.time() - t
rep["throughput_oc_tok_s"] = n / dt; rep["throughput_oc_tokens"] = n; rep["throughput_oc_secs"] = dt
torch.cuda.synchronize(); t = time.time()
with E.use("V"):
    _, n2 = E.oc(its, CT, want=False)
torch.cuda.synchronize(); dt2 = time.time() - t
rep["throughput_prefix_only_tok_s"] = n2 / dt2
rep["max_mem_gb"] = torch.cuda.max_memory_allocated() / 2**30
log(event="throughput", oc_tok_s=rep["throughput_oc_tok_s"], prefix_only_tok_s=rep["throughput_prefix_only_tok_s"], tokens=n, secs=dt, max_mem=rep["max_mem_gb"])
json.dump(rep, open(f"{OUT}/smoke.json", "w"), indent=1, default=str)
log(event="smoke_done")
